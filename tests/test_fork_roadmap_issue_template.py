"""Guardrails for Opensiro's v2 fork-local capability roadmap Issue template."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "FORK_CAPABILITY_ROADMAP_ISSUE.md"
AI_TEMPLATE = ROOT / "templates" / "ROADMAP_AI_CONSTRUCTOR_CONTRACT.md"
PROTOCOL = ROOT / "PROTOCOL.md"
ROADMAP = ROOT / "docs" / "CAPABILITY_ROADMAP.md"


class ForkCapabilityRoadmapIssueTemplateTests(unittest.TestCase):
    def test_template_is_generic_and_structurally_complete_v2(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# [PROJECT]"))
        self.assertIn("Opensiro", text)
        self.assertNotIn("OpenSiro", text)
        headings = [
            "## 1. Why Opensiro and central accepted VSM baseline",
            "## 2. Evidence baseline and scope",
            "## 3. Existing work vs user-visible gap",
            "## 4. VSM targets and human priority decision",
            "## 5. Acceptance, alternatives and stop conditions",
            "## 6. Independent development paths",
            "## 7. Value evaluation",
            "## 8. Decision and handoff",
        ]
        self.assertEqual([line for line in text.splitlines() if line.startswith("## ")], headings)
        self.assertNotIn("paperclipai/", text)
        self.assertNotIn("browser-use/", text)
        self.assertIn("existing original Issues/PRs", text)
        self.assertIn("Best original-native alternative", text)

    def test_target_and_priority_invariants(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        protocol = PROTOCOL.read_text(encoding="utf-8")
        roadmap = ROADMAP.read_text(encoding="utf-8")
        for doc in (text, protocol, roadmap):
            for requirement in ("P0", "P1", "P2", "A(P)", "C(P)", "NEEDS_EVIDENCE",
                                "NO_USEFUL_CHANGE"):
                self.assertIn(requirement, doc)
        for requirement in (
            "Target matrix (required)",
            "Already-confirmed `A`/`A(P)` functions",
            "not mandatory `C` targets",
            "An unresolved `?` must be investigated",
            "P0 — useful C sufficiency",
            "P1 — necessary enabling work",
            "P2 — optional improvements",
            "C sufficiency contract (required",
            "Sufficiency verdict",
            "Cost status: `NOT_MEASURED`",
        ):
            self.assertIn(requirement, text)
        self.assertIn("already at `A`/`A(P)` is **not required**", protocol)
        self.assertIn("already-`a`/`a(p)` functions **do not need c engineering work**", roadmap.lower())
        self.assertIn("why their combined behavior would be sufficient", roadmap)
        self.assertNotIn("a maturity ordering", text)

    def test_no_unearned_capability_or_cost_claims(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        for requirement in (
            "mandatory progression",
            "design",  # design and shipment remain distinct
            "not shipping",
            "separate Index review",
            "NOT_MEASURED",
            "Native alternative",
            "Positive operator scenario",
            "Negative/authority case",
            "No public fork Issue",
            "exact current-conversation owner approval",
        ):
            self.assertIn(requirement.lower(), text.lower())

    def test_case_storage_and_external_boundary(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn(".opensiro/issues/<case-id>/", text)
        self.assertIn("opensiro/meta", text)
        self.assertIn("fork-local discussion surface", text)
        self.assertIn("original maintainer request", text)
        self.assertIn("AI disclosure", text)
        self.assertIn("not an original maintainer request", text)

    def test_human_first_order_and_separate_ai_contract(self):
        human = TEMPLATE.read_text(encoding="utf-8")
        protocol = PROTOCOL.read_text(encoding="utf-8")
        guide = ROADMAP.read_text(encoding="utf-8")
        ai = AI_TEMPLATE.read_text(encoding="utf-8")

        mission = human.index("Opensiro tests whether")
        central = human.index("### Accepted Index — central starting point")
        matrix = human.index("| **S1 · Operations**")
        outcome = human.index("**User/operator counterfactual:**")
        self.assertLess(mission, central)
        self.assertLess(central, matrix)
        self.assertLess(matrix, outcome)
        for row in ("S1 · Operations", "S2 · Coordination", "S3 · Inside-and-now",
                    "S3* · Complementary audit", "S4 · Outside-and-then",
                    "S5 · Identity / policy"):
            self.assertIn(row, human)
        for phrase in ("Human → AI", "why Opensiro", "full central accepted six-function",
                       "AI/developer"):
            self.assertIn(phrase.lower(), protocol.lower())
        self.assertIn("Why Opensiro", guide)
        self.assertIn("Central accepted Index assessment", guide)
        self.assertIn("ROADMAP_AI_CONSTRUCTOR_CONTRACT.md", human)
        self.assertIn("ROADMAP_AI_CONSTRUCTOR_CONTRACT.md", protocol)
        self.assertIn("ROADMAP_AI_CONSTRUCTOR_CONTRACT.md", guide)
        self.assertIn("Level 1 / Human decision Issue", ai)
        self.assertIn("ACCEPTED HISTORICAL INDEX — NOT A TARGET", ai)
        for phrase in ("S1=[accepted]", "S2=[accepted]", "S3=[accepted]",
                       "S3*=[accepted]", "S4=[accepted]", "S5=[accepted]",
                       "shipped", "Positive outcome", "Unauthorized",
                       "S3↔S4", "NOT_MEASURED", "No original external"):
            self.assertIn(phrase.lower(), ai.lower())
        self.assertEqual(
            len([line for line in ai.splitlines() if line.startswith("## ")]), 8
        )

    def test_protocol_routes_to_internal_and_external_templates(self):
        for path in (PROTOCOL, ROADMAP):
            text = path.read_text(encoding="utf-8")
            self.assertIn("FORK_CAPABILITY_ROADMAP_ISSUE.md", text)
            self.assertIn("EXTERNAL_ARCHITECTURE_ISSUE.md", text)
        external = (ROOT / "templates" / "EXTERNAL_ARCHITECTURE_ISSUE.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Opensiro", external)
        self.assertNotIn("OpenSiro", external)


if __name__ == "__main__":
    unittest.main()
