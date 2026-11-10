"""Source-only harness candidate: valid blocked preview, never external-write proof."""
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from batch_proposals import load_draft, preview_draft


BASE = ROOT / "pilots" / "harnessdesk-1772"
MANIFEST = BASE / "upstream-20261019-harnessdesk-1772.json"
REPORT = BASE / "README.md"
TEST_SOURCE = BASE / "tool-gateway-second-host.test.ts"
INDEX_SHA = "13dab0d4f2954614f7f99a9fa044ad5b9a154490"


class HarnessDeskPilotTests(unittest.TestCase):
    def test_candidate_schema_and_explicit_stage_blockers(self):
        draft, digest = load_draft(MANIFEST)
        self.assertEqual(draft["status"], "proposal_only")
        self.assertEqual(draft["batch_id"], MANIFEST.stem)
        self.assertEqual(len(digest), 64)
        self.assertEqual(len(draft["candidates"]), 1)
        one = draft["candidates"][0]
        self.assertEqual(one["source"], "HarnessDesk/HarnessDesk")
        self.assertEqual(one["fork_name"], "HarnessDesk")
        self.assertEqual(one["expected_license"], "MIT")
        self.assertEqual(one["stages"], ["prepare_contribution"])
        self.assertEqual(one["proposal"]["evidence_url"],
                         "https://github.com/HarnessDesk/HarnessDesk/issues/1772")
        self.assertTrue(one["blockers"])
        preview = preview_draft(MANIFEST, selected_ids=["harnessdesk-1772"],
                                stage_scopes={"harnessdesk-1772": ["prepare_contribution"]})
        self.assertTrue(preview["selection_has_blockers"])
        self.assertEqual(preview["authorization_status"], "NOT_APPROVED_NO_WRITES")
        self.assertEqual(preview["candidates"][0]["status"], "BLOCKED")

    def test_report_carries_frozen_assessment_and_active_development_source(self):
        report = REPORT.read_text(encoding="utf-8")
        for item in (
            INDEX_SHA,
            "assessments/ha/harnessdesk.md",
            "24add77185eebe321b0aa0b578933acf4a8e05d3",
            "aeb939a6709ae23c9f1ff5948fbd2151572aee58",
            "development",
            "packages/server/test/tool-gateway-second-host.test.ts",
            "BLOCKED",
            "No production patch",
            "not a VSM score repair",
        ):
            with self.subTest(item=item):
                self.assertIn(item.lower(), report.lower())

    def test_proposed_external_regression_is_unexecuted_source_only(self):
        source = TEST_SOURCE.read_text(encoding="utf-8")
        for phrase in (
            "SOURCE-ONLY / NOT RUN",
            "ToolGateway",
            "primary",
            "duplicate",
            "duplicate host on the same home must refuse startup",
            "failed host shutdown must not unlink owner socket",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, source)
        self.assertNotIn("https://api.github.com", source)


if __name__ == "__main__":
    unittest.main()
