"""Offline contract for standing delegated fork/patch decisions.

These fixtures are never evidence of real GitHub writes or a connected host.
"""
import base64
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from connected_stage_adapter import StageBlocked
import test_connected_multifile_stage as core_fixture
from connected_multifile_stage import prepare_exact_two_file_patch
from standing_preparation_mandate import (
    CurrentMainStandingPreparationReader, StandingPreparationHost,
    POLICY_PATH, REGISTRY_PATH,
)


class StandingPreparationTests(unittest.TestCase):
    def setUp(self):
        self.policy = json.loads((ROOT / POLICY_PATH).read_text())
        self.sources = [f"source{i}/repo{i}" for i in range(5)]
        self.forks = [f"opensiro-contributions/repo{i}" for i in range(5)]
        self.registry = {
            "schema_version": 1,
            "sources": [
                {
                    "source": source,
                    "proposed_fork": fork,
                    "license_review": False,
                    "latest_stage": "AWAITING_EXTERNAL",
                    "handoffs": [{
                        "stage": "AWAITING_EXTERNAL",
                        "technical_packet": {
                            "state": "EXPLICIT_PATCH_HASH_MATCHED"},
                    }],
                }
                for source, fork in zip(self.sources, self.forks)
            ],
        }
        self.head = "a" * 40
        self.now = self.policy["valid_from"] + 100
        self.intent = {
            "stage": "prepare_contribution",
            "source": self.sources[0],
            "actor": "xLagerFeuer",
            "working_repo": self.forks[0],
            "new_branch": "opensiro/fix-stale-lifecycle",
            "source_sha": "b" * 40,
            "patch_sha256": "c" * 64,
        }

    def snapshot(self):
        return {"head_sha": self.head, "policy": copy.deepcopy(self.policy),
                "registry": copy.deepcopy(self.registry)}

    def host(self, **kwargs):
        return StandingPreparationHost(
            reader=self.snapshot, wave_sources=self.sources,
            host_identity="dev-alpha-2", clock=lambda: self.now, **kwargs)

    def test_effective_standing_grant_does_not_request_human_per_action(self):
        host = self.host()
        first = host.verify_exact_prepare(self.intent)
        self.assertTrue(host.authorize_exact_stage(first, self.intent))
        second_intent = dict(self.intent, new_branch="opensiro/fix-second")
        second = host.verify_exact_prepare(second_intent)
        self.assertTrue(host.authorize_exact_stage(second, second_intent))
        self.assertEqual(self.policy["publication_owner"], "separate_standing_policy")

    def test_reused_exact_grant_rejected(self):
        host = self.host()
        grant = host.verify_exact_prepare(self.intent)
        host.authorize_exact_stage(grant, self.intent)
        with self.assertRaisesRegex(StageBlocked, "replayed"):
            host.authorize_exact_stage(grant, self.intent)

    def test_drift_or_revocation_fails_before_consumption(self):
        for change in ("REVOKED", "HEAD"):
            with self.subTest(change=change):
                host = self.host()
                grant = host.verify_exact_prepare(self.intent)
                if change == "REVOKED":
                    self.policy["status"] = "REVOKED"
                else:
                    self.head = "f" * 40
                with self.assertRaises(StageBlocked):
                    host.authorize_exact_stage(grant, self.intent)
                self.policy["status"] = "ACTIVE"
                self.head = "a" * 40

    def test_wave_must_have_five_unique_source_identities(self):
        for wave in ([self.sources[0]] * 5, self.sources[:4],
                     self.sources[:4] + ["other/repo"]):
            with self.subTest(wave=wave), self.assertRaises(StageBlocked):
                StandingPreparationHost(
                    reader=self.snapshot, wave_sources=wave,
                    host_identity="dev-alpha-2", clock=lambda: self.now
                ).verify_exact_prepare(self.intent)

    def test_unqualified_registry_blocks_all_stages(self):
        for field, replacement in [
            ("license_review", True),
            ("latest_stage", "CLOSED_NO_CHANGE"),
            ("proposed_fork", None),
            ("handoffs", []),
        ]:
            with self.subTest(field=field):
                original = self.registry["sources"][4][field]
                self.registry["sources"][4][field] = replacement
                with self.assertRaises(StageBlocked):
                    self.host().verify_exact_prepare(self.intent)
                self.registry["sources"][4][field] = original

    def test_denied_scope_actor_host_branch_destination_and_publication(self):
        for update in [
            {"stage": "submit_external_pr"},
            {"actor": "different-user"},
            {"source": "unknown/project"},
            {"working_repo": "opensiro/evil-repo"},
            {"working_repo": "opensiro-contributions/repo1"},
            {"new_branch": "main"},
            {"new_branch": "opensiro/../../main"},
        ]:
            with self.subTest(update=update), self.assertRaises(StageBlocked):
                self.host().verify_exact_prepare({**self.intent, **update})
        with self.assertRaisesRegex(StageBlocked, "Wrong execution host"):
            StandingPreparationHost(
                reader=self.snapshot, wave_sources=self.sources,
                host_identity="other-runner").verify_exact_prepare(self.intent)

    def test_expired_or_proposed_policy_rejected(self):
        for new_now in (self.policy["valid_from"] - 1,
                        self.policy["valid_until"]):
            with self.subTest(new_now=new_now), self.assertRaisesRegex(
                StageBlocked, "expired"
            ):
                self.now = new_now
                self.host().verify_exact_prepare(self.intent)
        self.now = self.policy["valid_from"] + 100
        self.policy["status"] = "PROPOSED_NOT_ACTIVE"
        with self.assertRaisesRegex(StageBlocked, "No effective"):
            self.host().verify_exact_prepare(self.intent)

    def test_fork_stages_are_automatic_but_no_external_pr(self):
        host = self.host()
        fork_intent = {
            "stage": "create_public_fork",
            "source": self.sources[1],
            "connected_actor": "xLagerFeuer",
            "destination": self.forks[1],
            "working_branch": "development",
            "working_branch_sha": "a" * 40,
            "default_branch_only": False,
        }
        self.assertTrue(host.authorize_fork(fork_intent))
        with self.assertRaisesRegex(StageBlocked, "already consumed"):
            host.authorize_fork(fork_intent)
        with self.assertRaises(StageBlocked):
            host.authorize_fork({**fork_intent, "stage": "submit_external_pr"})
        with self.assertRaises(StageBlocked):
            self.host().authorize_fork({
                **fork_intent, "default_branch_only": True})

    def test_standing_grant_runs_existing_exact_patch_adapter_offline(self):
        # Real patch port is still required for any external repository write.
        self.sources[0] = core_fixture.SOURCE
        self.forks[0] = core_fixture.FORK
        self.registry["sources"][0]["source"] = core_fixture.SOURCE
        self.registry["sources"][0]["proposed_fork"] = core_fixture.FORK
        port = core_fixture.FakePort()
        action = core_fixture.action()
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "upstream-20261020-gateway.json"
            manifest.write_text(json.dumps(core_fixture.manifest_data()))
            result = prepare_exact_two_file_patch(
                manifest=manifest,
                selected_ids=["harnessdesk-1772"],
                stage_scopes={"harnessdesk-1772": ["prepare_contribution"]},
                candidate_id="harnessdesk-1772", action=action,
                github=port, host=self.host())
        self.assertEqual(result["status"], "PREPARED_VERIFIED")
        self.assertEqual(len(port.writes()), 1)

    def test_get_only_pinned_reader_observes_source_drift(self):
        calls = []
        def transport(method, path):
            self.assertEqual(method, "GET")
            calls.append(path)
            if path.endswith("branches/main"):
                return 200, {"commit": {"sha": self.head}}
            value = (self.policy if POLICY_PATH in path else self.registry)
            return 200, {"type": "file", "encoding": "base64",
                         "content": base64.b64encode(
                             json.dumps(value).encode()).decode()}
        reader = CurrentMainStandingPreparationReader(transport)
        read = reader()
        self.assertEqual(read["head_sha"], self.head)
        self.assertEqual(len(calls), 4)
        self.assertEqual(read["policy"], self.policy)


if __name__ == "__main__":
    unittest.main()
