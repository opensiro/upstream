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
            "no candidates qualify", 
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
            "itself a bug", 
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
        self.assertIn("not a separate bot", self.handoff)

    def test_admitted_domain_does_not_activate_execution_or_external_rights(self):
        for phrase in (
            "read-only",
            "admitted Upstream S1 domain",
            "does **not** activate an independent executor",
            "widen publication rights",
            "authorize GitHub writes",
            "existing fork",
            "does **not** prove new fork creation",
            "trusted current-session",
            "P1",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), self.spec.lower())

    def test_strict_derived_cases_require_prospective_hypothesis_and_ci_receipt(self):
        protocol = (
            ROOT / "docs" / "ASSESSMENT_TO_IMPROVEMENT.md"
        ).read_text(encoding="utf-8")
        batches = (
            ROOT / "docs" / "ASSESSMENT_CANDIDATE_BATCHES.md"
        ).read_text(encoding="utf-8")
        for document in (self.spec, protocol, batches):
            with self.subTest(document=document[:75]):
                self.assertRegex(document.lower(), r"before (?:fresh|inspecting)|\*\*before\*\* investigating")
                self.assertIn("BLOCKED_INDEPENDENT_EXECUTION", document)
                self.assertIn("runner", document.lower())
        self.assertIn("not directly run them as their validator", self.spec)
        self.assertIn("merely increasing confidence", protocol)
        self.assertIn("C → A", protocol)


    def test_two_upstream_batch_modes_search_vsm_hypotheses_without_new_queue(self):
        batches = (
            ROOT / "docs" / "ASSESSMENT_CANDIDATE_BATCHES.md"
        ).read_text(encoding="utf-8")
        for phrase in (
            "Control Plane command: `batch upstream`",
            "Control Plane command: `upstream upgrade batch`",
            "Both batch commands search",
            "five",
            "not five pre-approved patches",
            "ASSESSMENT_INFORMED",
            "ASSESSMENT_DERIVED",
            "before** fresh upstream code/issue inspection",
            "distinct deterministic CI/runner",
            "BLOCKED_INDEPENDENT_EXECUTION",
            "not** create a new scheduler",
            "no separate active `batch upgrade` command",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, batches)


if __name__ == "__main__":
    unittest.main()
