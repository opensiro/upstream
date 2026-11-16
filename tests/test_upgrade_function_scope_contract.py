"""Regression contract for explicitly function-scoped conversational Upgrades.

These checks protect written operator invariants; they do not simulate an agent,
execute a third-party harness, or prove functional S5 closure.
"""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class FunctionScopedUpgradeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = (ROOT / "PROTOCOL.md").read_text(encoding="utf-8")
        cls.section = cls.protocol.split(
            "### Function-scoped Upgrade — evidence-first selection and closure", 1
        )[1].split("\n### ", 1)[0]

    def test_function_scope_is_gated_before_capability_implementation(self):
        self.assertLess(
            self.protocol.index("### Function-scoped Upgrade — evidence-first selection and closure"),
            self.protocol.index("### Material capability-delta gate before implementation"),
        )
        for phrase in (
            "bounded read-only function-first preselection",
            "license/contributor-formalities preflight",
            "before source lock",
            "credible material",
            "existing fork/green tests",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), self.section.lower())

    def test_exact_operator_phrase_and_canonical_origin(self):
        for phrase in (
            "upstream upgrade VSM derived & informed only S5",
            "ASSESSMENT_DERIVED",
            "ASSESSMENT_INFORMED",
            "S3*",
            "OWNER/REPO",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.section)
        self.assertIn("not itself proof", self.section)
        self.assertIn("not a new assessment", self.section)

    def test_one_harness_and_function_stay_locked_when_candidate_fails(self):
        for phrase in (
            "SELECTED_ORIGINAL_REPOSITORY",
            "FUNCTION_SCOPE",
            "inside the same selected harness AND requested function scope",
            "Do not switch to a different original",
            "widen to a different VSM function",
            "do not reinterpret",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), self.section.lower())
        single_source = self.protocol.split(
            "### End-to-end single-source Upgrade — finish at human PR approval", 1
        )[1].split("\n### ", 1)[0]
        self.assertIn("any explicitly requested function scope", single_source)

    def test_s5_requires_real_authority_and_closure_not_just_static_policy(self):
        for phrase in (
            "S5",
            "legitimate identity/ultimate-policy decisions",
            "returning to govern later operations",
            "policy.yaml",
            "generic human approval",
            "unauthorized actor",
            "subsequent behavior",
            "no genuine S5-level conflict",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), self.section.lower())

    def test_target_function_lock_does_not_block_native_cross_function_closure(self):
        section = self.section
        for phrase in (
            "claimed capability delta",
            "supporting implementation and verification",
            "only when causally necessary",
            "existing S3 constraints",
            "changed S1 task execution",
            "evidence of S5 closure",
            "not S3/S1 upgrades",
            "unauthorized S5 decisions",
            "supporting evidence, not an expanded improvement target",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), section.lower())
        review = (ROOT / "docs/UPGRADE_PR_REVIEW.md").read_text(encoding="utf-8")
        self.assertIn("without asserting an S3 or S1 feature", review)
        agent = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Lock the qualifying capability to the requested function", agent)
        self.assertIn("Function-scope verification boundary (unreleased)", (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))

    def test_unverified_ownership_and_native_runner_are_not_false_no_change(self):
        for phrase in (
            "NO_QUALIFIED_IMPROVEMENT",
            "EVIDENCE_INSUFFICIENT",
            "BLOCKED_WITH_HANDOFF",
            "First try a permitted source-native test setup",
            "tests actually run, including zero",
            "MATERIAL_DELTA_SUPPORTED",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), self.section.lower())

    def test_existing_overlap_supports_s5_and_scoped_continuation(self):
        overlap = self.protocol.split(
            "### Existing-work functional overlap and VSM-ownership gate", 1
        )[1].split("\n### ", 1)[0]
        self.assertIn("For S5 distinguish a legitimate identity/ultimate-policy decision", overlap)
        self.assertIn("same selected harness and any explicitly requested function scope", overlap)
        self.assertIn("MATERIAL_DELTA_SUPPORTED", self.protocol)
        self.assertIn("exact current-conversation consent", self.protocol)

    def test_agent_readme_review_and_changelog_all_route_to_gate(self):
        for path in ("AGENTS.md", "README.md", "docs/UPGRADE_PR_REVIEW.md"):
            with self.subTest(path=path):
                text = (ROOT / path).read_text(encoding="utf-8")
                self.assertIn("function-scoped-upgrade--evidence-first-selection-and-closure", text)
                self.assertIn("S5", text)
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("**Function-scoped evidence-first Upgrade (unreleased):**", changelog)
        self.assertIn("without new JSON enums", changelog)


if __name__ == "__main__":
    unittest.main()
