"""Contract checks: capability-first upgrade vs bug-fix fallback, protocol v0.9.0."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CapabilityFirstUpgradeTests(unittest.TestCase):
    def test_release_is_versioned_and_linked_from_operator_surfaces(self):
        version = (ROOT / "VERSION").read_text().strip()
        if tuple(map(int, version.split("."))) < (0, 9, 0):
            self.skipTest("pre-v0.9.0")
        package = (ROOT / "changes/v0.9.0.md").read_text()
        self.assertTrue(package.startswith("# v0.9.0"))
        self.assertIn("**Historical checkpoint:**", package)
        self.assertIn("MINOR", package)
        self.assertIn("## Protocol changes", package)
        self.assertIn("## Boundary and compatibility", package)
        self.assertIn("## [0.9.0](changes/v0.9.0.md)", (ROOT / "CHANGELOG.md").read_text())
        for rel in ("README.md", "UPSTREAMING.md"):
            with self.subTest(rel=rel):
                self.assertIn("SemVer `0.9.0`", (ROOT / rel).read_text())
        for rel in ("AGENTS.md", "README.md", "UPSTREAMING.md",
                    "docs/ASSESSMENT_CANDIDATE_BATCHES.md",
                    "docs/ASSESSMENT_TO_IMPROVEMENT.md",
                    "docs/ASSESSMENT_DRIVEN_S1_TEST.md"):
            with self.subTest(link=rel):
                self.assertIn("CAPABILITY_FIRST_RESEARCH.md", (ROOT / rel).read_text())

    def test_native_capability_is_not_a_repair_or_synthetic_bug(self):
        text = (ROOT / "docs/CAPABILITY_FIRST_RESEARCH.md").read_text()
        for phrase in ("new", "operator", "current", "value", "negative",
                       "MINOR_FEATURE", "MAJOR_FEATURE", "BUG_FIX",
                       "SDK", "reliability", "not automatically",
                       "before", "original"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), text.lower())
        self.assertIn("OPPORTUNITY_RESEARCH_PENDING", text)
        self.assertIn("CLOSED_NO_CHANGE", text)

    def test_no_evidence_origin_or_permission_shortcut(self):
        text = (ROOT / "docs/CAPABILITY_FIRST_RESEARCH.md").read_text()
        for phrase in ("ASSESSMENT_DERIVED", "ASSESSMENT_INFORMED",
                       "GENERAL_UPSTREAM", "need/mechanism/counterfactual/scope = PASS",
                       "separate deterministic runner", "six-function", "license",
                       "no new batch", "do not mutate frozen batches"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), text.lower())
        self.assertIn("do not require or initiate live llm/model/browser/user trials", text.lower())

    def test_examples_do_not_claim_admitted_source_first_features(self):
        text = (ROOT / "docs/CAPABILITY_FIRST_RESEARCH.md").read_text()
        for phrase in ("Akmatori", "srchd", "HelixHarness", "issues/67",
                       "issues/204", "issues/11", "pull/203", "pull/299",
                       "source-first", "not admitted"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), text.lower())

    def test_prior_protocol_details_are_not_rewritten(self):
        report = (ROOT / "docs/ASSESSMENT_CANDIDATE_BATCHES.md").read_text()
        for phrase in ("contribution protocol v0.8.0",
                       "contribution protocol v0.9.0",
                       "six-function", "all four", "SOURCE_FIRST",
                       "no retroactive", "strict", "BLOCKED_EVIDENCE"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), report.lower())


if __name__ == "__main__":
    unittest.main()
