"""Offline batch host boundary tests. Fake actors/permissions grant no live rights."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
from batch_fork_executor import execute_one_verified_fork_batch, StageBlocked
from test_connected_fork_adapter import FakeProvider, draft, NotFound


class FakeGrant:
    pass


class FakeHost:
    def __init__(self):
        self.allowed = True
        self.verify_calls = []
        self.stage_calls = []
        self.on_batch = lambda: None
        self.on_stage = lambda: None

    def verify_exact_batch(self, intent):
        self.verify_calls.append(intent)
        self.on_batch()
        return FakeGrant() if self.allowed else None

    def authorize_exact_stage(self, grant, batch_intent, stage_intent):
        self.stage_calls.append((grant, batch_intent, stage_intent))
        self.on_stage()
        return self.allowed


class MultiForkProvider(FakeProvider):
    def __init__(self):
        super().__init__()
        self.created_names = set()
        self.parents = {}

    def repo(self, name):
        if name == "outside/second":
            return {**super().repo("outside/example"), "full_name": name}
        if name.startswith("opensiro-contributions/"):
            if name not in self.created_names:
                raise NotFound()
            return {"full_name": name, "private": self.private_fork,
                    "archived": False, "fork": True,
                    "parent": {"full_name": self.parents.get(name, self.parent)},
                    "permissions": {"push": self.push},
                    "html_url": "https://github.com/" + name}
        return super().repo(name)

    def branch(self, repository, name):
        if repository.startswith("opensiro-contributions/"):
            if repository not in self.created_names or self.fork_branch_missing:
                raise NotFound()
            return {"sha": self.fork_branch_sha or self.source_branch_sha}
        if repository == "outside/second":
            return super().branch("outside/example", name)
        return super().branch(repository, name)

    def create_public_fork(self, source, owner, name, *, default_branch_only):
        self.calls.append(("create_public_fork", source, owner, name, default_branch_only))
        if self.fail_write:
            raise RuntimeError("simulated failure")
        self.created_names.add(owner + "/" + name)
        self.parents[owner + "/" + name] = source
        return {"accepted": self.accepted}


class BatchTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "upstream-20261020-batch-fork.json"
        self.data = draft()
        self.data["batch_id"] = "upstream-20261020-batch-fork"
        self.save()
        self.provider = MultiForkProvider()
        self.host = FakeHost()
        self.actions = {"example": {"destination_owner": "opensiro-contributions",
                                    "fork_name": "example",
                                    "working_branch": "main",
                                    "working_branch_sha": "a" * 40,
                                    "default_branch_only": True}}
        self.ids = ["example"]
        self.scopes = {"example": ["create_public_fork"]}

    def save(self):
        self.path.write_text(json.dumps(self.data), encoding="utf-8")

    def run_batch(self, **kw):
        x = {"manifest": self.path, "selected_ids": self.ids,
             "stage_scopes": self.scopes, "actions": self.actions,
             "github": self.provider, "host": self.host}
        x.update(kw)
        return execute_one_verified_fork_batch(**x)

    def test_one_stage_verified_and_batch_bound(self):
        result = self.run_batch()
        self.assertEqual(result["status"], "BATCH_VERIFIED")
        self.assertEqual(result["processed_count"], 1)
        self.assertEqual(result["receipts"][0]["status"], "CREATED_VERIFIED")
        self.assertEqual(len(self.host.verify_calls), 1)
        self.assertEqual(len(self.host.stage_calls), 1)
        self.assertEqual(self.host.verify_calls[0]["selected_stages"][0]["destination"],
                         "opensiro-contributions/example")
        self.assertEqual(len(self.provider.writes()), 1)

    def test_no_host_or_provider_methods_prevents_any_write(self):
        for kw in ({"host": None}, {"github": None}):
            with self.subTest(kw=kw), self.assertRaises(StageBlocked):
                self.run_batch(**kw)
        self.provider.create_public_fork = None
        with self.assertRaises(StageBlocked):
            self.run_batch()
        self.assertEqual(self.provider.writes(), [])

    def test_no_authentication_or_denial_blocks(self):
        self.host.allowed = False
        with self.assertRaises(StageBlocked):
            self.run_batch()
        self.assertEqual(self.provider.writes(), [])

    def test_stage_denied_without_provider_write(self):
        self.host.authorize_exact_stage = lambda *args: False
        result = self.run_batch()
        self.assertEqual(result["status"], "BATCH_STOPPED")
        self.assertEqual(result["receipts"][0]["status"], "BLOCKED")
        self.assertEqual(self.provider.writes(), [])

    def test_blocked_harnessdesk_shape_cannot_run(self):
        self.data["candidates"][0]["blockers"] = ["unverified fork"]
        self.save()
        with self.assertRaises(StageBlocked):
            self.run_batch()
        self.assertEqual(self.host.verify_calls, [])
        self.assertEqual(self.provider.writes(), [])

    def test_cannot_stage_prepare_or_submit(self):
        self.scopes["example"] = ["create_public_fork", "prepare_contribution"]
        with self.assertRaises(StageBlocked):
            self.run_batch()
        self.assertEqual(self.provider.writes(), [])

    def test_manifest_change_after_batch_approval_prevents_write(self):
        def change():
            self.data["revision"] += 1
            self.save()
        self.host.on_batch = change
        with self.assertRaises(StageBlocked):
            self.run_batch()
        self.assertEqual(self.provider.writes(), [])

    def test_action_change_after_batch_approval_prevents_write(self):
        self.host.on_batch = lambda: self.actions["example"].__setitem__(
            "default_branch_only", False)
        with self.assertRaises(StageBlocked):
            self.run_batch()
        self.assertEqual(self.provider.writes(), [])

    def test_stage_scope_change_after_batch_approval_prevents_write(self):
        self.host.on_batch = lambda: self.scopes["example"].append("prepare_contribution")
        with self.assertRaises(StageBlocked):
            self.run_batch()
        self.assertEqual(self.provider.writes(), [])

    def test_source_branch_drift_after_stage_authorization_prevents_write(self):
        self.host.on_stage = lambda: setattr(self.provider, "source_branch_sha", "b" * 40)
        r = self.run_batch()
        self.assertEqual(r["status"], "BATCH_STOPPED")
        self.assertEqual(r["receipts"][0]["status"], "BLOCKED")
        self.assertEqual(self.provider.writes(), [])

    def test_nondefault_without_full_copy_is_blocked(self):
        self.actions["example"]["working_branch"] = "development"
        with self.assertRaises(StageBlocked):
            self.run_batch()
        self.assertEqual(self.provider.writes(), [])

    def test_nondefault_all_branches_can_be_verified_by_fake(self):
        self.actions["example"]["working_branch"] = "development"
        self.actions["example"]["default_branch_only"] = False
        r = self.run_batch()
        self.assertEqual(r["receipts"][0]["status"], "CREATED_VERIFIED")
        self.assertFalse(self.provider.writes()[0][-1])

    def test_write_failure_stops_batch_without_retry(self):
        self.provider.fail_write = True
        r = self.run_batch()
        self.assertEqual(r["status"], "BATCH_STOPPED")
        self.assertEqual(r["receipts"][0]["status"], "FAILED")
        self.assertEqual(len(self.provider.writes()), 1)

    def test_pending_readback_stops_batch(self):
        self.provider.fork_branch_missing = True
        r = self.run_batch()
        self.assertEqual(r["status"], "BATCH_STOPPED")
        self.assertEqual(r["receipts"][0]["status"], "PENDING_VERIFICATION")
        self.assertEqual(len(self.provider.writes()), 1)

    def test_duplicate_fork_destination_denied_before_auth(self):
        self.data["candidates"].append({
            **self.data["candidates"][0], "id": "second",
            "source": "outside/example",
        })
        self.save()
        self.ids.append("second")
        self.scopes["second"] = ["create_public_fork"]
        self.actions["second"] = dict(self.actions["example"])
        with self.assertRaises(StageBlocked):
            self.run_batch()
        self.assertEqual(self.host.verify_calls, [])
        self.assertEqual(self.provider.writes(), [])

    def test_two_items_one_batch_grant(self):
        self.data["candidates"].append({
            **self.data["candidates"][0], "id": "second",
            "fork_name": "second", "source": "outside/second",
        })
        self.save()
        self.ids.append("second")
        self.scopes["second"] = ["create_public_fork"]
        self.actions["second"] = {**self.actions["example"], "fork_name": "second"}
        r = self.run_batch()
        self.assertEqual(r["status"], "BATCH_VERIFIED")
        self.assertEqual(len(self.host.verify_calls), 1)
        self.assertEqual(len(self.host.stage_calls), 2)
        self.assertEqual(len(self.provider.writes()), 2)

    def test_batch_grant_not_synthetic_boolean(self):
        self.host.verify_exact_batch = lambda _: True
        with self.assertRaises(StageBlocked):
            self.run_batch()
        self.assertEqual(self.provider.writes(), [])


if __name__ == "__main__":
    unittest.main()
