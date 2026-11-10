"""Offline tests of the real HarnessDesk pilot bundle loader. No network/writes."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import prepare_harnessdesk_local as runner
from connected_stage_adapter import StageBlocked


class PilotBundleTests(unittest.TestCase):
    def test_exact_v2_bundle_matches_reviewed_source_and_fork_sha(self):
        action = runner.action_from_pilot()
        self.assertEqual(action["source_sha"],
                         "81d5e34e0e8e3d7e0945bc680695940b41ab852f")
        self.assertEqual(action["fork_observed_sha"],
                         "4029e95189c61485f934f158c6725ef6eeb7ef35")
        self.assertEqual(action["new_branch"], "opensiro/fix-toolgateway-1772")
        self.assertEqual(len(action["changed_paths"]), 2)
        self.assertEqual(action["patch_sha256"],
                         "12b5c7e55a6f730fb9a2465ca30dd47321690c87c0d887e7b8c9d6990ec186e7")

    def test_tampered_bundle_rejected_before_any_provider(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wrong.patch"
            path.write_text("diff --git a/foo b/foo\n--- a/foo\n+++ b/foo\n")
            with patch.object(runner, "PATCH", path):
                with self.assertRaisesRegex(StageBlocked, "Invalid historical"):
                    runner.action_from_pilot()

    def test_historical_packet_not_treated_as_grant(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = json.loads(runner.PACKET.read_text())
            original["status"] = "PREPARED_VERIFIED"
            path = Path(tmp) / "packet.json"
            path.write_text(json.dumps(original))
            with patch.object(runner, "PACKET", path):
                with self.assertRaisesRegex(StageBlocked, "Invalid historical"):
                    runner.action_from_pilot()


if __name__ == "__main__":
    unittest.main()
