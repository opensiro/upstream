"""Source-only handoff invariants; never an execution grant."""
from pathlib import Path
import hashlib
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from batch_proposals import preview_draft
from connected_multifile_stage import DIFF

PILOT = ROOT / "pilots" / "harnessdesk-1772"


class SharedCommitHandoffTests(unittest.TestCase):
    def setUp(self):
        self.packet = json.loads((PILOT / "prepare-v2-20261020-81d5e34-shared.json").read_text())
        self.proposal = PILOT / "upstream-20261020-harnessdesk-1772.json"

    def test_exact_selected_scope_has_no_historical_proposal_blockers(self):
        preview = preview_draft(self.proposal, selected_ids=["harnessdesk-1772"],
                                stage_scopes={"harnessdesk-1772": ["prepare_contribution"]})
        selected = [c for c in preview["candidates"] if c["selected"]]
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["selected_stages"], ["prepare_contribution"])
        self.assertEqual(selected[0]["blockers"], [])
        self.assertEqual(selected[0]["source"], "HarnessDesk/HarnessDesk")

    def test_packet_is_explicitly_non_authorizing(self):
        p = self.packet
        self.assertEqual(p["status"], "ACTION_PREPARED_NOT_AUTHORIZED")
        self.assertEqual(p["authorization"], "NO_VERIFIABLE_STAGE_GRANT")
        self.assertFalse(p["execution_available"])
        self.assertIn("prepare_contribution", p["selection_scope"])
        self.assertEqual(p["source_sha"], "81d5e34e0e8e3d7e0945bc680695940b41ab852f")
        self.assertEqual(p["fork_observed_sha"], "4029e95189c61485f934f158c6725ef6eeb7ef35")
        self.assertEqual(p["fork_ancestry"]["behind_by"], 0)
        self.assertTrue(p["shared_source_commit_in_fork"])
        self.assertIn("create or update contributor branch", p["prohibited_actions_without_grant"])

    def test_exact_reviewed_v2_patch_and_paths(self):
        p = self.packet
        patch = (ROOT / p["patch_path"]).read_bytes()
        self.assertEqual(hashlib.sha256(patch).hexdigest(), p["patch_sha256"])
        paths = [src for src, dst in DIFF.findall(patch.decode("utf-8")) if src == dst]
        self.assertEqual(sorted(paths), sorted(p["changed_paths"]))
        self.assertEqual(p["preimage_sha256"]["packages/server/src/tool-gateway.ts"], "727b8a13c8bcbbd4786c2ab9f048c8ab931f28a45d02aa1701a2c4d1131096ee")

    def test_preserves_historical_source_pins(self):
        p = self.packet
        older = json.loads((PILOT / "prepare-v2-20261020-24aa8d7.json").read_text())
        self.assertEqual(older["source_sha"], "24aa8d7fdeee47f03f787cc77f40978948bf8141")
        self.assertNotEqual(p["source_sha"], older["source_sha"])
        self.assertEqual(p["patch_sha256"], older["patch_sha256"])


if __name__ == "__main__":
    unittest.main()
