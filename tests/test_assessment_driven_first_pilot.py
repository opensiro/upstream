"""Contract checks on the bounded Index-origin S1 pilot receipt (not live proof)."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "2026-10-19-index-origin-s1-pilot.md"
INDEX_SHA = "d701ec67c96e39de5971271f6158997337c6e524"
ASSESSMENTS = (
    "assessments/ha/harness2.md",
    "assessments/na/nanocoder-haoyuzhang0214.md",
    "assessments/co/codeagent-harvil1.md",
    "assessments/ra/raincode.md",
    "assessments/mi/minagent.md",
)


class FirstIndexPilotReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = REPORT.read_text(encoding="utf-8")

    def test_exact_index_revision_and_five_assessments(self):
        self.assertIn(INDEX_SHA, self.text)
        for path in ASSESSMENTS:
            with self.subTest(path=path):
                self.assertIn(f"/blob/{INDEX_SHA}/{path}", self.text)
        self.assertIn("NOT_EVALUATED", self.text)
        self.assertIn("NOT_ADMITTED", self.text)

    def test_overlap_and_lack_of_demonstrated_native_benefit_block(self):
        for phrase in (
            "BLOCKED_OVERLAP",
            "BLOCKED_EVIDENCE",
            "NO_ELIGIBLE_ASSESSMENT_CANDIDATE_IN_SAMPLED_SET",
            "PASS/PASS/PASS/PASS",
            "PENDING/PENDING/PENDING/PENDING",
            "intentional behavior",
            "not a global absence statement",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), self.text.lower())
        self.assertRegex(self.text, r"\bS2=—\b|\bS2=—;")

    def test_no_write_claim_or_vsm_grade_promotion(self):
        for stage in (
            "create_public_fork",
            "prepare_contribution",
            "submit_external_pr",
        ):
            with self.subTest(stage=stage):
                self.assertRegex(
                    self.text,
                    rf"(?m)^\| `{re.escape(stage)}` \| `NOT_EXECUTED`",
                )
        for phrase in (
            "no new external submission",
            "NOT_ASSESSED",
            "PARTIAL",
            "no existing fork substituted",
            "no exact current-session operator authorization",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), self.text.lower())


if __name__ == "__main__":
    unittest.main()
