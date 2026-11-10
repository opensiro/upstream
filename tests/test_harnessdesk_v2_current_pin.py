"""Pinned 2026-10-20 current-source V2 proof is NOT an execution grant."""
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "pilots/harnessdesk-1772"
FROZEN = "24aa8d7fdeee47f03f787cc77f40978948bf8141"


class CurrentSourceV2EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads((P / "prepare-v2-20261020-24aa8d7.json").read_text())
        cls.old = json.loads((P / "prepare-v2-handoff.json").read_text())
        cls.patch = (P / "tool-gateway-ownership-fix-v2.patch").read_bytes()
        cls.ci = (ROOT / ".github/workflows/harnessdesk-v2-macos.yml").read_text()

    def test_exact_patch_bytes_remain_pinned(self):
        self.assertEqual(hashlib.sha256(self.patch).hexdigest(),
                         self.packet["patch_sha256"])
        self.assertEqual(self.packet["patch_sha256"],
                         self.old["patch_sha256"])

    def test_new_pin_in_mac_build_matches_packet(self):
        self.assertEqual(self.packet["source_sha"], FROZEN)
        self.assertEqual(self.ci.count(FROZEN), 2)
        self.assertIn("ref: " + FROZEN, self.ci)
        self.assertIn("EXPECTED_SOURCE='" + FROZEN + "'", self.ci)
        self.assertIn("contents: read", self.ci)
        self.assertNotIn("gh api --method POST", self.ci)

    def test_two_file_pre_and_postimages_are_pinned(self):
        target = "packages/server/src/tool-gateway.ts"
        newtest = "packages/server/test/tool-gateway-ownership.test.ts"
        self.assertEqual(self.packet["changed_paths"], [target, newtest])
        self.assertEqual(list(self.packet["preimage_sha256"]), [target])
        self.assertEqual(set(self.packet["postimage_sha256"]), {target, newtest})
        for v in list(self.packet["preimage_sha256"].values()) + list(self.packet["postimage_sha256"].values()):
            self.assertRegex(v, r"^[0-9a-f]{64}$")

    def test_later_evidence_does_not_rewrite_historical_snapshot(self):
        self.assertNotEqual(self.old["observed_source_base_sha"], FROZEN)
        self.assertEqual(self.packet["fork_base_sha"],
                         self.old["observed_fork_development_sha"])

    def test_no_grant_or_false_fork_sync(self):
        x = self.packet
        self.assertEqual(x["status"], "ACTION_PREPARED_NOT_AUTHORIZED")
        self.assertEqual(x["authorization"], "NO_VERIFIABLE_STAGE_GRANT")
        self.assertIs(x["execution_available"], False)
        self.assertIs(x["source_and_fork_base_match"], False)
        self.assertEqual(x["validation"]["gateway_tests_total"], 17)
        self.assertEqual(x["validation"]["gateway_tests_failed"], 0)
        self.assertEqual(x["validation"]["macos_current_pin"], "PENDING_NEW_CI")
        self.assertIn("post third-party upstream PR", x["prohibited_actions_without_grant"])


if __name__ == "__main__":
    unittest.main()
