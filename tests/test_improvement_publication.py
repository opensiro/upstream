import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data/improvement-publication/2026-10-24-01.json"
CORRECTIVE = ROOT / "data/corrective-publication/2026-10-23-01.json"

class ImprovementPublicationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(LEDGER.read_text())
        cls.cases = cls.data["cases"]

    def test_bounded_mandate(self):
        self.assertEqual(self.data["mandate_id"], "IMPROVEMENT-PUBLISH-2026-10-24-01")
        self.assertEqual(self.data["authorized_count"], 2)
        self.assertEqual(len(self.cases), 2)
        self.assertEqual(self.data["allowed_public_fork_owner"], "opensiro-contributions")
        self.assertEqual(self.data["authenticated_actor"], "xLagerFeuer")
        self.assertEqual(self.data["mandate_record"], "https://github.com/opensiro/vsm-oss-organization/issues/287")
        self.assertIn("Ready for review", self.data["readiness_decision"])

    def test_expected_sources_only(self):
        self.assertEqual({c["source"] for c in self.cases}, {"SethGammon/Citadel", "chankov/agent-fleet"})
        self.assertEqual({c["external_pr"] for c in self.cases}, {
            "https://github.com/SethGammon/Citadel/pull/366",
            "https://github.com/chankov/agent-fleet/pull/43"
        })
        self.assertEqual(len({c["patch_sha256"] for c in self.cases}), 2)

    def test_external_write_scope(self):
        for c in self.cases:
            with self.subTest(c["source"]):
                self.assertEqual(c["publication"], "MERGED_UPSTREAM")
                self.assertEqual(c["initial_publication"], "SUBMITTED_DRAFT")
                self.assertFalse(c["pr_draft"])
                self.assertTrue(c["pr_merged"])
                self.assertTrue(c["public_fork"].startswith("opensiro-contributions/"))
                self.assertEqual(c["fork_parent"], c["source"])
                self.assertEqual(c["published_file_count"], 5)
                self.assertTrue(c["external_pr_head_branch"].startswith("opensiro/"))
                self.assertEqual(c["external_pr_base"], "main")
                self.assertEqual(c["source_baseline_sha"], c["external_pr_base_sha"])
                for key in ("patch_sha256", "source_baseline_sha", "external_pr_head_sha"):
                    self.assertEqual(len(c[key]), 64 if key=="patch_sha256" else 40)
                self.assertIn(c["maintainer_feedback"], {"MERGED_BY_MAINTAINER", "APPROVED_THEN_MERGED"})
                self.assertEqual(len(c["merge_commit_sha"]), 40)
                self.assertEqual(len(c["merged_pr_head_sha"]), 40)
                self.assertEqual(len(c["merged_pr_base_sha"]), 40)
                self.assertIn("T", c["merged_at"])
                self.assertEqual(c["merged_readback_date"], "2026-10-26")
                self.assertTrue(c["merged_by"])
                self.assertEqual(c["product_user_benefit"], "NOT_MEASURED")

    def test_original_corrective_queue_unchanged_scope(self):
        corrective = json.loads(CORRECTIVE.read_text())
        self.assertEqual(corrective["authorized_count"], 34)
        self.assertEqual(len(corrective["cases"]), 34)
        self.assertNotEqual(corrective["mandate_id"], self.data["mandate_id"])
        self.assertEqual(len({c["id"] for c in corrective["cases"]}), 34)
        self.assertTrue(all(c["publication"] in {
            "QUEUED", "SUBMITTED", "BLOCKED", "MERGED", "CLOSED_NO_CHANGE", "CLOSED_UPSTREAM"
        } for c in corrective["cases"]))

if __name__ == "__main__":
    unittest.main()
