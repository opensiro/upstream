"""Offline tests: no real fork operation or authenticated host is provided."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from connected_fork_adapter import execute_one_public_fork, StageBlocked, NotFound


DEST = "opensiro-contributions/example"


def draft():
    return {"schema_version": 1, "batch_id": "upstream-20261019-real-fork-plan",
            "revision": 1, "status": "proposal_only", "candidates": [{
                "id": "example", "source": "outside/example", "fork_name": "example",
                "stages": ["create_public_fork", "prepare_contribution",
                           "submit_external_pr"],
                "expected_license": "MIT",
                "proposal": {
                    "system_component": "Issue reproduction in example service",
                    "problem": "A reported race is not covered by tests",
                    "planned_change": "Introduce a focused concurrency regression",
                    "expected_improvement": "Reduce undetected regression risk",
                    "validation": "Run upstream's concurrency test suite",
                    "evidence_url": "https://github.com/outside/example/issues/123"},
                "blockers": []}]}


class FakeProvider:
    def __init__(self):
        self.calls = []
        self.created = False
        self.existing = False
        self.license = "MIT"
        self.authority = True
        self.capable = True
        self.actor = "operator"
        self.source_private = False
        self.no_forking = False
        self.private_fork = False
        self.parent = "outside/example"
        self.push = True
        self.readback_missing = False
        self.fail_write = False
        self.accepted = True
        self.default_branch = "main"
        self.source_branch_sha = "a" * 40
        self.fork_branch_sha = None
        self.fork_branch_missing = False
        self.fork_branch_read_failure = False
        self.source_branch_missing = False
        self.fork_copy_default_only = True

    def fork_capability(self, owner):
        self.calls.append(("fork_capability", owner))
        return {"available": self.capable, "authorized": self.authority,
                "owner": owner, "actor": self.actor}

    def repo(self, name):
        self.calls.append(("repo", name))
        if name == "outside/example":
            return {"full_name": name, "private": self.source_private,
                    "archived": False, "forking_allowed": not self.no_forking,
                    "license": {"spdx_id": self.license},
                    "default_branch": self.default_branch}
        if not (self.created or self.existing) or self.readback_missing:
            raise NotFound()
        return {"full_name": name, "private": self.private_fork,
                "archived": False, "fork": True,
                "parent": {"full_name": self.parent},
                "permissions": {"push": self.push},
                "html_url": "https://github.com/" + name}

    def branch(self, repository, name):
        self.calls.append(("branch", repository, name))
        if repository == "outside/example":
            if self.source_branch_missing:
                raise NotFound()
            return {"sha": self.source_branch_sha}
        if self.fork_branch_read_failure:
            raise PermissionError("403")
        if not (self.created or self.existing) or self.fork_branch_missing:
            raise NotFound()
        # A default-only fork cannot magically materialize a nondefault branch.
        if self.fork_copy_default_only and name != self.default_branch:
            raise NotFound()
        return {"sha": self.fork_branch_sha or self.source_branch_sha}

    def create_public_fork(self, source, owner, name, *, default_branch_only):
        self.calls.append(("create_public_fork", source, owner, name, default_branch_only))
        if self.fail_write:
            raise RuntimeError("simulated GitHub failure")
        self.created = True
        self.fork_copy_default_only = default_branch_only
        return {"accepted": self.accepted}

    def writes(self):
        return [x for x in self.calls if x[0] == "create_public_fork"]


class ForkStageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.manifest = Path(self.temp.name) / "upstream-20261019-real-fork-plan.json"
        self.data = draft()
        self.save()
        self.provider = FakeProvider()
        self.action = {"destination_owner": "opensiro-contributions",
                       "fork_name": "example",
                       "working_branch": "main",
                       "working_branch_sha": "a" * 40,
                       "default_branch_only": True}
        self.approved = True
        self.intents = []
        self.on_approval = lambda: None

    def save(self):
        self.manifest.write_text(json.dumps(self.data), encoding="utf-8")

    def authorize(self, intent):
        self.intents.append(intent)
        self.on_approval()
        return self.approved

    def run_stage(self, **kwargs):
        opts = dict(manifest=self.manifest, selected_ids=["example"],
                    stage_scopes={"example": ["create_public_fork"]},
                    candidate_id="example", action=self.action,
                    github=self.provider, authorize=self.authorize)
        opts.update(kwargs)
        return execute_one_public_fork(**opts)

    def test_mock_success_after_readback(self):
        r = self.run_stage()
        self.assertEqual(r["status"], "CREATED_VERIFIED")
        self.assertEqual(r["fork_url"], "https://github.com/" + DEST)
        self.assertEqual(len(self.provider.writes()), 1)
        self.assertEqual(self.intents[0]["stage"], "create_public_fork")
        self.assertTrue(self.intents[0]["default_branch_only"])

    def test_no_host_authorization(self):
        with self.assertRaises(StageBlocked): self.run_stage(authorize=None)
        self.assertEqual(self.provider.writes(), [])

    def test_no_fork_endpoint(self):
        self.provider.create_public_fork = None
        with self.assertRaises(StageBlocked): self.run_stage()
        self.assertEqual(self.provider.writes(), [])

    def test_provider_lookup_failure(self):
        def unavailable(_):
            raise PermissionError("403")
        self.provider.repo = unavailable
        with self.assertRaises(StageBlocked): self.run_stage()
        self.assertEqual(self.provider.writes(), [])

    def test_no_connected_port(self):
        with self.assertRaises(StageBlocked): self.run_stage(github=None)

    def test_operator_declined(self):
        self.approved = False
        with self.assertRaises(StageBlocked): self.run_stage()
        self.assertEqual(self.provider.writes(), [])

    def test_provider_absent(self):
        self.provider.capable = False
        with self.assertRaises(StageBlocked): self.run_stage()
        self.assertEqual(self.provider.writes(), [])

    def test_org_authority_absent(self):
        self.provider.authority = False
        with self.assertRaises(StageBlocked): self.run_stage()
        self.assertEqual(self.provider.writes(), [])

    def test_unselected_candidate(self):
        with self.assertRaises(StageBlocked): self.run_stage(selected_ids=[], stage_scopes={})
        self.assertEqual(self.provider.writes(), [])

    def test_cannot_implicitly_approve_prepare_or_submit(self):
        with self.assertRaises(StageBlocked):
            self.run_stage(stage_scopes={"example": ["create_public_fork", "prepare_contribution"]})
        self.assertEqual(self.provider.writes(), [])

    def test_cannot_skip_fork_stage(self):
        with self.assertRaises(StageBlocked):
            self.run_stage(stage_scopes={"example": ["prepare_contribution"]})
        self.assertEqual(self.provider.writes(), [])

    def test_invalid_namespace(self):
        self.action["destination_owner"] = "personal-account"
        with self.assertRaises(StageBlocked): self.run_stage()

    def test_mismatched_fork_name(self):
        self.action["fork_name"] = "different"
        with self.assertRaises(StageBlocked): self.run_stage()

    def test_license_drift(self):
        self.provider.license = "Apache-2.0"
        with self.assertRaises(StageBlocked): self.run_stage()

    def test_source_private(self):
        self.provider.source_private = True
        with self.assertRaises(StageBlocked): self.run_stage()

    def test_source_prohibits_fork(self):
        self.provider.no_forking = True
        with self.assertRaises(StageBlocked): self.run_stage()

    def test_existing_correct_fork_cannot_pass_as_new(self):
        self.provider.existing = True
        with self.assertRaises(StageBlocked): self.run_stage()
        self.assertEqual(self.provider.writes(), [])

    def test_existing_wrong_parent_cannot_pass_as_new(self):
        self.provider.existing = True
        self.provider.parent = "someone/else"
        with self.assertRaises(StageBlocked): self.run_stage()
        self.assertEqual(self.provider.writes(), [])

    def test_fake_approval_field_invalid(self):
        self.data["approved_by"] = "someone"
        self.save()
        with self.assertRaises(StageBlocked): self.run_stage()
        self.assertEqual(self.provider.writes(), [])

    def test_blocked_proposal(self):
        self.data["candidates"][0]["blockers"] = ["Policy unresolved"]
        self.save()
        with self.assertRaises(StageBlocked): self.run_stage()
        self.assertEqual(self.provider.writes(), [])

    def test_operator_decision_after_drift(self):
        self.on_approval = lambda: setattr(self.provider, "existing", True)
        with self.assertRaises(StageBlocked): self.run_stage()
        self.assertEqual(self.provider.writes(), [])

    def test_operator_identity_drifts(self):
        self.on_approval = lambda: setattr(self.provider, "actor", "another-user")
        with self.assertRaises(StageBlocked): self.run_stage()
        self.assertEqual(self.provider.writes(), [])

    def test_write_failure_is_not_retried(self):
        self.provider.fail_write = True
        self.assertEqual(self.run_stage()["status"], "FAILED")
        self.assertEqual(len(self.provider.writes()), 1)

    def test_async_fork_remains_pending(self):
        self.provider.readback_missing = True
        self.assertEqual(self.run_stage()["status"], "PENDING_VERIFICATION")
        self.assertEqual(len(self.provider.writes()), 1)

    def test_unaccepted_provider_reply_not_success(self):
        self.provider.accepted = False
        self.assertEqual(self.run_stage()["status"], "PENDING_VERIFICATION")

    def test_wrong_parent_after_write(self):
        self.provider.parent = "unrelated/else"
        self.assertEqual(self.run_stage()["status"], "VERIFICATION_FAILED")

    def test_private_fork_not_verified(self):
        self.provider.private_fork = True
        self.assertEqual(self.run_stage()["status"], "VERIFICATION_FAILED")

    def test_no_push_permission_not_verified(self):
        self.provider.push = False
        self.assertEqual(self.run_stage()["status"], "VERIFICATION_FAILED")

    def test_default_branch_only_is_enforced(self):
        self.assertTrue(self.run_stage()["default_branch_only"])
        self.assertEqual(self.provider.writes()[0][-1], True)


    def test_harnessdesk_development_requires_all_branches(self):
        self.action["working_branch"] = "development"
        self.action["default_branch_only"] = False
        receipt = self.run_stage()
        self.assertEqual(receipt["status"], "CREATED_VERIFIED")
        self.assertEqual(receipt["working_branch"], "development")
        self.assertFalse(receipt["default_branch_only"])
        self.assertEqual(self.provider.writes()[0][-1], False)

    def test_default_only_cannot_silently_use_development(self):
        self.action["working_branch"] = "development"
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.provider.writes(), [])

    def test_missing_pinned_working_sha_rejected(self):
        self.action["working_branch_sha"] = "development"
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.provider.writes(), [])

    def test_source_branch_sha_mismatch_rejected(self):
        self.provider.source_branch_sha = "b" * 40
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.provider.writes(), [])

    def test_source_ref_drift_after_authorization_rejected(self):
        self.on_approval = lambda: setattr(self.provider, "source_branch_sha", "b" * 40)
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.provider.writes(), [])

    def test_missing_branch_provider_method_rejected(self):
        self.provider.branch = None
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.provider.writes(), [])

    def test_missing_source_branch_rejected(self):
        self.provider.source_branch_missing = True
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.provider.writes(), [])

    def test_fork_branch_missing_returns_pending_not_success(self):
        self.provider.fork_branch_missing = True
        r = self.run_stage()
        self.assertEqual(r["status"], "PENDING_VERIFICATION")
        self.assertEqual(len(self.provider.writes()), 1)

    def test_fork_wrong_branch_sha_is_not_verified(self):
        self.provider.fork_branch_sha = "c" * 40
        r = self.run_stage()
        self.assertEqual(r["status"], "VERIFICATION_FAILED")
        self.assertIsNone(r["fork_url"])

    def test_fork_branch_read_403_is_not_404(self):
        self.provider.fork_branch_read_failure = True
        r = self.run_stage()
        self.assertEqual(r["status"], "PENDING_VERIFICATION")
        self.assertEqual(len(self.provider.writes()), 1)

    def test_copy_strategy_and_ref_are_in_authorization_intent(self):
        self.action["working_branch"] = "development"
        self.action["default_branch_only"] = False
        self.run_stage()
        self.assertEqual(self.intents[0]["working_branch_sha"], "a" * 40)
        self.assertEqual(self.intents[0]["working_branch"], "development")
        self.assertIs(self.intents[0]["default_branch_only"], False)

    def test_invalid_boolean_and_branch_path_rejected(self):
        for key, value in (
            ("default_branch_only", "false"),
            ("working_branch", "../secret"),
            ("working_branch", "feature/@{bad}"),
            ("working_branch", "development.lock"),
            ("working_branch", "a//b"),
            ("working_branch", "a b"),
        ):
            with self.subTest(key=key, value=value):
                self.action[key] = value
                with self.assertRaises(StageBlocked):
                    self.run_stage()
                self.assertEqual(self.provider.writes(), [])
                self.action = {"destination_owner": "opensiro-contributions",
                               "fork_name": "example",
                               "working_branch": "main",
                               "working_branch_sha": "a" * 40,
                               "default_branch_only": True}


if __name__ == "__main__":
    unittest.main()