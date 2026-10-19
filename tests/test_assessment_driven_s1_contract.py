"""Assessment-linked S1 construction testing stays distinct from generic OSS proposals."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class AssessmentDrivenS1ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = (ROOT / "docs" / "ASSESSMENT_DRIVEN_S1_TEST.md").read_text(
            encoding="utf-8"
        )
        cls.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        cls.preview = (ROOT / "docs" / "BATCH_PROPOSALS.md").read_text(encoding="utf-8")
        cls.handoff = (ROOT / "docs" / "CONTROL_PLANE_HANDOFF.md").read_text(
            encoding="utf-8"
        )

    def test_canonical_index_first_not_familiar_fork_first(self):
        for phrase in (
            "test S1 function: upstream contributions",
            "Index assessment",
            "immutable Index commit SHA",
            "assessed source repository/revision",
            "S1–S5 function/ownership",
            "Do not start from a favourite fork",
            "NO_ELIGIBLE_ASSESSMENT_CANDIDATE",
            "BLOCKED_EVIDENCE",
            "no suitable assessment-derived candidate",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), self.spec.lower())

    def test_upstream_native_value_and_provenance_are_separate(self):
        for phrase in (
            "need",
            "mechanism",
            "counterfactual value",
            "scope",
            "Index assessment @ SHA",
            "proposal.evidence_url",
            "not a bug",
            "PASS",
            "PENDING",
            "FAIL",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), self.spec.lower())
        self.assertIn("Index assessment", self.readme)
        self.assertIn("docs/ASSESSMENT_DRIVEN_S1_TEST.md", self.readme)
        self.assertIn("ASSESSMENT_DRIVEN_S1_TEST.md", self.preview)
        self.assertIn("ASSESSMENT_DRIVEN_S1_TEST.md", self.handoff)

    def test_generic_preview_retained_without_fake_approval(self):
        self.assertIn("ordinary GitHub-issue-driven", self.spec)
        self.assertIn("generic OSS", self.readme)
        self.assertIn("standalone OSS preview", self.preview)
        self.assertIn("does **not** enforce", self.preview)
        self.assertIn("ACTION_PREPARED_NOT_AUTHORIZED", self.handoff)
        self.assertIn("not a new", self.handoff)

    def test_current_s1_test_cannot_create_a_fork_or_submit_external_pr(self):
        for phrase in (
            "read-only",
            "not an activated automation",
            "existing fork",
            "does **not** prove new fork creation",
            "trusted current-session",
            "no new S1 domain",
            "not",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), self.spec.lower())
        self.assertIn("PROPOSED", self.spec)
        self.assertIn("not a permission to modify GitHub", self.spec)
        self.assertIn("P1", self.spec)


if __name__ == "__main__":
    unittest.main()
