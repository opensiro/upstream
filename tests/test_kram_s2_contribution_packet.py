import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PILOT = ROOT / "pilots" / "kram-s2"


class KramContributionPacketTest(unittest.TestCase):
    def test_exact_pinned_patch_and_non_authorizing_status(self):
        packet = json.loads((PILOT / "contribution-handoff-2026-10-22.json").read_text())
        self.assertEqual(packet["state"], "ACTION_PREPARED_NOT_AUTHORIZED")
        self.assertEqual(packet["external_actions_executed"], [])
        self.assertIsNone(packet["effective_stage_authorization"])
        self.assertIsNone(packet["owner_decision_url"])
        self.assertFalse(packet["proposed_destination"]["fork_exists_verified"])
        self.assertFalse(packet["proposed_destination"]["branch_absence_verified"])
        self.assertEqual(packet["source"]["repository"], "codexmark/kram")
        self.assertEqual(packet["source"]["branch"], "master")
        self.assertEqual(packet["source"]["sha"], "5f18406709f432dbdb2d6b09da6f140385516366")
        patch_bytes = (ROOT / packet["patch"]["path"]).read_bytes()
        self.assertEqual(hashlib.sha256(patch_bytes).hexdigest(), packet["patch"]["sha256"])
        self.assertEqual(packet["verification"]["method"], "DETERMINISTIC_NATIVE_SCRIPT_ONLY")
        self.assertEqual(len(packet["patch"]["changed_paths"]), 3)

    def test_pr_body_and_policy_bounded(self):
        handoff = (PILOT / "CONTRIBUTION_HANDOFF.md").read_text()
        self.assertIn("ACTION_PREPARED_NOT_AUTHORIZED", handoff)
        self.assertIn("No deployed-user frequency", handoff)
        self.assertIn("no LLM-agent/Browser/model-provider testing", handoff)
        self.assertIn("final third-party PR creation remains human-owned", handoff)
        self.assertIn("scripts/verify.sh", handoff)


if __name__ == "__main__":
    unittest.main()
