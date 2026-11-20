"""Source-neutral guardrails for Human Issue + AI contract + external proposal.

These tests verify decision/source boundaries, not real VSM function or cost proof.
The historical Paperclip pilot is a stress case, not a mandatory template layout.
"""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HUMAN = ROOT / "templates" / "FORK_CAPABILITY_ROADMAP_ISSUE.md"
AI = ROOT / "templates" / "ROADMAP_AI_CONSTRUCTOR_CONTRACT.md"
EXTERNAL = ROOT / "templates" / "EXTERNAL_ARCHITECTURE_ISSUE.md"
PROTOCOL = ROOT / "PROTOCOL.md"
GUIDE = ROOT / "docs" / "CAPABILITY_ROADMAP.md"


class RoadmapHumanAIContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.human = HUMAN.read_text(encoding="utf-8")
        cls.ai = AI.read_text(encoding="utf-8")
        cls.external = EXTERNAL.read_text(encoding="utf-8")
        cls.protocol = PROTOCOL.read_text(encoding="utf-8")
        cls.guide = GUIDE.read_text(encoding="utf-8")

    def test_human_is_one_compact_decision_surface_not_two_six_row_tables(self):
        h = self.human
        self.assertTrue(h.startswith("# [HARNESS]"))
        self.assertIn("Opensiro", h)
        self.assertNotIn("OpenSiro", h)
        self.assertIn("Why Opensiro", h)
        self.assertIn("ACCEPTED HISTORICAL INDEX", h)
        self.assertIn("One combined historical-and-current six-function table", h)
        self.assertEqual(len(re.findall(r"(?m)^[|] [*][*]S1 · Operations", h)), 1)
        for fn in ("S1", "S2", "S3", "S3*", "S4", "S5"):
            self.assertEqual(len(re.findall(r"(?m)^[|] [*][*]" + re.escape(fn) + r" · ", h)), 1)
            self.assertIn(fn + "=[accepted]", h)
        self.assertLess(h.index("### Central starting point"), h.index("## 2. Selected construction"))
        self.assertLess(h.index("Priority rationale"), h.index("## 2. Selected construction"))

    def test_human_preserves_all_six_function_constraints_and_optional_interest(self):
        h = self.human
        for marker in ("Repository-wide audit", "system-in-focus", "S3* ·",
                       "P0 / DEFER / NO_TARGET / UNKNOWN", "Deliberate exclusions",
                       "Methodology", "NOT_STATED", "owner_control", "PAUSE",
                       "No public fork Issue", "original external Issue"):
            self.assertIn(marker.lower(), h.lower())
        self.assertIn("do not trigger mandatory c work", h.lower())
        self.assertIn("not quality ranks", h.lower())

    def test_human_goal_is_selected_after_census_and_has_true_no_target(self):
        h = self.human
        self.assertIn("NO_QUALIFIED_C_TARGET", h)
        self.assertIn("Selected construction hypothesis", h)
        self.assertIn("Target transition:", h)
        self.assertIn("Best native operator alternative", h)
        self.assertIn("Track A", h)
        self.assertIn("Track B", h)
        self.assertIn("matching Issue veto", h)
        self.assertIn("Proposed C-sufficiency verdict", h)
        self.assertIn("separate Index review", h)
        self.assertIn("NOT_MEASURED", h)
        self.assertIn("GO + NEEDS_EVIDENCE", h)
        self.assertNotIn("S3=A(P) · S4=—", h)

    def test_human_and_ai_share_receipt_derivation_without_duplicate_vector(self):
        for doc in (self.human, self.ai):
            self.assertIn("[roadmap.md](roadmap.md)", doc)
            for marker in ("**Target transition:**", "**Proposal-stage decision:**",
                           "**Research disposition:**"):
                self.assertIn(marker, doc)
            self.assertIn("GO", doc)
            self.assertIn("NO_GO", doc)
            self.assertIn("BLOCKED", doc)
        self.assertIn("[constructor-sufficiency.md](constructor-sufficiency.md)", self.human)
        self.assertIn("[issue.md](issue.md)", self.ai)
        self.assertNotRegex(self.ai, r"(?m)^\\| \\*\\*S1 · ")
        self.assertIn("roadmap.md owns all historical Index grades", self.ai)
        self.assertIn("source of truth", self.human)
        self.assertIn("Canonical decision receipt", self.human)
        self.assertIn("Canonical decision receipt", self.ai)

    def test_ai_is_function_neutral_and_does_not_copy_paperclip_interfaces(self):
        ai = self.ai
        self.assertEqual([x for x in ai.splitlines() if x.startswith("## ")],
                         ["## 1. Function-specific construction boundary and methodology checks",
                          "## 2. Source-pinned baseline and parallel native Track A / on-top Track B",
                          "## 3. Minimal complete [selected function] first-party C construction",
                          "## 4. Priorities, optional alternative and stopping rules",
                          "## 5. Future source-native acceptance — derive tests, do not copy a matrix",
                          "## 6. Proposal verdict, falsification, evidence ownership and handoff"])
        for fn in ("S1", "S2", "S3", "S3*", "S4", "S5"):
            self.assertIn(fn, ai)
        self.assertIn("Physical interface count is NOT prescribed", ai)
        self.assertIn("five-port pattern", ai)
        self.assertIn("no mandatory feature novelty", ai)
        self.assertNotIn("ObservedReturnReceipt", ai)
        self.assertNotIn("AC-01 Positive closure", ai)
        self.assertNotIn("AC-OPTIONAL-01", ai)

    def test_ai_acceptance_cases_source_native_not_prescriptive(self):
        ai = self.ai
        self.assertIn("Native test commands and entry points", ai)
        self.assertIn("Positive functional closure", ai)
        self.assertIn("Negative authority and compatibility", ai)
        self.assertIn("Matched native alternative", ai)
        self.assertIn("Case derived from selected function, NOT_RUN", ai)
        self.assertIn("test count are deliberately not supplied", ai)
        self.assertIn("NONE / NOT_RUN", ai)
        self.assertIn("source-applicable cases", ai)
        self.assertIn("No original external Issue/comment/PR", ai)

    def test_go_and_research_uncertainty_are_separate(self):
        for doc in (self.ai, self.human, self.protocol, self.guide):
            self.assertIn("GO + NEEDS_EVIDENCE", doc)
        self.assertIn("Do not automatically turn NEEDS_EVIDENCE into NO_GO or BLOCKED", self.ai)
        self.assertIn("not an implementation authorization", self.ai)
        self.assertIn("NOT_MEASURED", self.ai)
        self.assertIn("NO_QUALIFIED_C_TARGET", self.ai)

    def test_p2_is_optional_not_paperclip_double_constructor(self):
        self.assertIn("P2:", self.human)
        self.assertIn("P2:", self.ai)
        self.assertIn("by default", self.ai)
        self.assertIn("do not embed a forced second five-port", self.ai)
        self.assertIn("no mandatory second function", self.human.lower()) if "no mandatory second function" in self.human.lower() else self.assertIn("not a mandated second function", self.human.lower())

    def test_canonical_stable_filenames_and_paperclip_is_historical(self):
        for name in ("issue.md", "constructor-sufficiency.md", "roadmap.md"):
            self.assertIn(name, self.human)
            self.assertIn(name, self.ai)
            self.assertIn(name, self.guide)
        self.assertNotIn("/constructor-sufficiency-v2.md", self.human)
        self.assertIn("Paperclip two-level pilot", self.protocol)
        self.assertIn("Paperclip is a historical stress case", self.guide)
        self.assertIn("not a mandatory format", self.guide)
        self.assertIn("case-level structural check", self.protocol)

    def test_external_issue_shows_complete_readable_vsm_without_product_ranking(self):
        external = self.external
        self.assertLess(external.index("## Proposal in the project's own terms"),
                        external.index("## How we reached this proposal"))
        for fn in ("S1", "S2", "S3", "S3*", "S4", "S5"):
            self.assertIn("| **" + fn + " · ", external)
        for state in ("`A`", "`C`", "`P`", "`A(P)`", "`C(P)`", "`—`", "`?`"):
            self.assertIn(state, external)
        for marker in ("Historical assessment:", "Index commit SHA",
                       "assessment blob SHA", "review_ref", "Current original HEAD:",
                       "Skills Methodology", "first-party",
                       "not VSM theory", "not ranks", "DRAFT — NOT PUBLISHED",
                       "current-conversation approval", "AI involvement"):
            self.assertIn(marker.lower(), external.lower())
        self.assertNotIn("OpenSiro", external)

    def test_template_conformity_is_required_at_case_write_not_only_publication(self):
        self.assertIn("## Mandatory Roadmap case-write Human/AI template gate",
                      self.protocol)
        self.assertIn("before writing its fork-local", self.protocol)
        self.assertIn("then validate the exact stored commit", self.protocol)
        self.assertIn("existing numbered template sections", self.protocol)
        for doc in (self.protocol, self.guide):
            self.assertIn("validate_capability_roadmap.py", doc)
            self.assertIn("validate_roadmap_publication.py", doc)
            self.assertIn("materially revised", doc)
        self.assertIn("before writing opensiro/meta", self.human)
        self.assertIn("again after committed SHA readback", self.ai)

    def test_original_maintainer_publication_is_separately_gated(self):
        for doc in (self.protocol, self.guide):
            self.assertIn("FORK_CAPABILITY_ROADMAP_ISSUE.md", doc)
            self.assertIn("EXTERNAL_ARCHITECTURE_ISSUE.md", doc)
            self.assertIn("separate", doc)
            self.assertIn("current-conversation", doc)
        self.assertIn("not an original-maintainer Issue", self.human)
        self.assertIn("This is a", self.ai)
        self.assertIn("DRAFT — NOT PUBLISHED", self.ai)


if __name__ == "__main__":
    unittest.main()
