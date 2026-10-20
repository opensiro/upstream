"""Offline integrity tests for the exact, non-authorizing HarnessDesk V2 handoff."""
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "pilots" / "harnessdesk-1772"


class V2HandoffContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.intent = json.loads((PILOT / "prepare-v2-handoff.json").read_text())
        cls.manifest = json.loads((PILOT / "upstream-20261019-harnessdesk-1772.json").read_text())
        cls.patch = (PILOT / "tool-gateway-ownership-fix-v2.patch").read_bytes()

    def test_patch_bytes_sha_match_exact_handoff(self):
        self.assertEqual(hashlib.sha256(self.patch).hexdigest(),
                         self.intent["patch_sha256"])
        self.assertRegex(self.intent["patch_sha256"], r"^[0-9a-f]{64}$")

    def test_source_stage_cannot_be_silently_promoted(self):
        self.assertEqual(self.intent["kind"], "UPSTREAM_MULTIFILE_PREPARE_HANDOFF")
        self.assertEqual(self.intent["status"], "ACTION_PREPARED_NOT_AUTHORIZED")
        self.assertEqual(self.intent["authorization"], "NO_VERIFIABLE_STAGE_GRANT")
        self.assertIs(self.intent["execution_available"], False)
        self.assertEqual(self.intent["stage"], "prepare_contribution")
        self.assertEqual(self.manifest["status"], "proposal_only")
        self.assertEqual(self.manifest["candidates"][0]["stages"],
                         ["prepare_contribution"])
        self.assertTrue(self.manifest["candidates"][0]["blockers"])

    def test_diff_paths_are_bound_to_production_plus_regression(self):
        paths = re.findall(rb"^diff --git a/(.+?) b/\1$", self.patch, re.M)
        self.assertEqual(sorted(p.decode() for p in paths),
                         sorted(self.intent["changed_paths"]))
        self.assertEqual(sorted(self.intent["changed_paths"]), sorted([
            "packages/server/src/tool-gateway.ts",
            "packages/server/test/tool-gateway-ownership.test.ts",
        ]))
        self.assertIn(b"linkSync(", self.patch)
        self.assertIn(b"socketIdentity(", self.patch)
        self.assertIn(b"SIGKILL", self.patch)

    def test_source_is_current_but_fork_is_behind(self):
        self.assertEqual(self.intent["upstream_source"], "HarnessDesk/HarnessDesk")
        self.assertEqual(self.intent["working_fork"], "opensiro-contributions/HarnessDesk")
        self.assertEqual(self.intent["fork_parent_verified"], self.intent["upstream_source"])
        self.assertNotEqual(self.intent["observed_source_base_sha"],
                            self.intent["observed_fork_development_sha"])
        self.assertRegex(self.intent["observed_source_base_sha"], r"^[0-9a-f]{40}$")
        self.assertEqual(self.intent["proposed_contribution_branch"],
                         "opensiro/fix-toolgateway-1772")
        self.assertEqual(self.intent["contribution_branch_observation"],
                         "NOT_FOUND_BY_AUTHENTICATED_GET")

    def test_no_writes_or_human_publication_implicitly_authorized(self):
        self.assertEqual(self.intent["verified_tests"]["gateway_tests_pass"], 17)
        self.assertIn("push patch to organization fork",
                      self.intent["prohibited_without_grant"])
        self.assertIn("publish external upstream PR",
                      self.intent["prohibited_without_grant"])
        self.assertTrue(any("single new test file" in s for s in
                            self.intent["blockers"]))
        self.assertFalse(any("token" in key.lower() or "password" in key.lower()
                             for key in self.intent))


if __name__ == "__main__":
    unittest.main()
