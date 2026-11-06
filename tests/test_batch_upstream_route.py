"""Keep the Upstream technical-batch route separate from external publication rights."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "ASSESSMENT_CANDIDATE_BATCHES.md"


class BatchUpstreamRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = CONTRACT.read_text(encoding="utf-8")
        cls.section = cls.document.split(
            "## Control Plane command: `batch upstream`", 1
        )[1].split("## Meaning of `continue`", 1)[0]

    def test_batch_command_is_distinct_from_other_lanes(self):
        for phrase in (
            "technical contribution batch",
            "start a batch assessment",
            "contribute to other harnesses",
            "autonomy-evaluation",
            "Upstream #56",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.section)

    def test_native_frozen_concurrency_and_evidence_guards(self):
        for phrase in (
            "unmerged draft cohorts",
            "five distinct",
            "Index commit",
            "NO_ELIGIBLE_ASSESSMENT_CANDIDATE",
            "serially",
            "need",
            "mechanism",
            "counterfactual",
            "scope",
            "native deterministic first-party regression tests",
            "BLOCKED_EVIDENCE",
            "NO_ACTIONABLE_CANDIDATE",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.section)

    def test_acceptance_and_external_grant_are_separate(self):
        self.assertNotIn("S1_WITNESS_PENDING", self.document)
        self.assertIn("construction witness", self.document)
        for phrase in (
            "separate effective external fork/branch/PR-stage grant",
            "AWAITING_EXTERNAL",
            "finite 34-case Corrective mandate",
            "internal reviewable OpenSiro patch/PR",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.section)


if __name__ == "__main__":
    unittest.main()
