"""Offline integration of signed host with the exact two-file stage core.

All keys are temporary test fixtures and provider writes are a FakePort.
No actual signed operator decision, SSH credentials or external ref mutation.
"""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from batch_proposals import preview_draft
from connected_multifile_stage import prepare_exact_two_file_patch, StageBlocked
from test_connected_multifile_stage import (
    FakePort, manifest_data, action,
)
from test_signed_one_use_prepare_host import SignedPrepareGrantTests


class SignedHostEndToEndTests(unittest.TestCase):
    def setUp(self):
        self.fixture = SignedPrepareGrantTests(
            "test_real_signature_consumed_once_and_restart_replay_rejected")
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.manifest = self.fixture.path / "upstream-20261020-gateway.json"
        self.manifest.write_text(json.dumps(manifest_data()))
        self.a = action()
        self.a["fork_observed_sha"] = "c" * 40
        self.port = FakePort()
        self.port.work_sha = "c" * 40
        self.selected = ["harnessdesk-1772"]
        self.scopes = {"harnessdesk-1772": ["prepare_contribution"]}
        preview = preview_draft(self.manifest, selected_ids=self.selected,
                                stage_scopes=self.scopes)
        item = preview["candidates"][0]
        self.fixture.intent = {
            "stage": "prepare_contribution",
            "candidate_id": item["id"],
            "source": item["source"],
            "proposal_sha256": preview["proposal_sha256"],
            "selection_scope_sha256": preview["selection_scope_sha256"],
            "actor": "xLagerFeuer",
            "working_repo": self.a["working_repo"],
            "source_branch": self.a["source_branch"],
            "source_sha": self.a["source_sha"],
            "base_branch": self.a["base_branch"],
            "base_sha": self.a["base_sha"],
            "new_branch": self.a["new_branch"],
            "fork_observed_sha": self.a["fork_observed_sha"],
            "patch_sha256": self.a["patch_sha256"],
            "changed_paths": self.a["changed_paths"],
            "preimage_sha256": self.a["preimage_sha256"],
            "postimage_sha256": self.a["postimage_sha256"],
        }

    def run_stage(self, host=None):
        return prepare_exact_two_file_patch(
            manifest=self.manifest, selected_ids=self.selected,
            stage_scopes=self.scopes, candidate_id="harnessdesk-1772",
            action=self.a, github=self.port,
            host=host if host is not None else self.fixture.make_host())

    def test_signed_exact_grant_reaches_one_fake_atomic_write(self):
        self.fixture.signed_payload()
        result = self.run_stage()
        self.assertEqual(result["status"], "PREPARED_VERIFIED")
        self.assertEqual(len(self.port.writes()), 1)
        self.assertEqual(self.port.work_sha, "c" * 40)
        self.assertTrue(self.fixture.ledger.exists())
        with self.assertRaises(StageBlocked):
            self.fixture.make_host().verify_exact_prepare(self.fixture.intent)

    def test_missing_operator_signature_rejects_before_writer(self):
        with self.assertRaisesRegex(StageBlocked, "missing or revoked"):
            self.run_stage()
        self.assertEqual(self.port.writes(), [])
        self.assertFalse(self.fixture.ledger.exists())

    def test_valid_signature_for_old_base_rejects_changed_stage(self):
        self.fixture.signed_payload()
        self.a["source_sha"] = "d" * 40
        self.a["base_sha"] = "d" * 40
        self.port.source_sha = "d" * 40
        self.port.shared_tree = "e" * 40
        self.port.commit_parents = ["d" * 40]
        with self.assertRaisesRegex(StageBlocked, "exact intent mismatch"):
            self.run_stage()
        self.assertEqual(self.port.writes(), [])

    def test_signature_for_wrong_scope_rejects_without_write(self):
        self.fixture.signed_payload()
        self.scopes = {"harnessdesk-1772": []}
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.port.writes(), [])

    def test_valid_signature_invalidated_by_proposal_change(self):
        self.fixture.signed_payload()
        data = json.loads(self.manifest.read_text())
        data["revision"] = 2
        self.manifest.write_text(json.dumps(data))
        with self.assertRaisesRegex(StageBlocked, "exact intent mismatch"):
            self.run_stage()
        self.assertEqual(self.port.writes(), [])


if __name__ == "__main__":
    unittest.main()
