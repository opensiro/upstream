"""Guardrails for Paperclip-derived Human/AI roadmap template pair.

These tests verify generic template structure and safe handoff, not semantic
truth of any project's Index classification or feature implementation.
"""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "FORK_CAPABILITY_ROADMAP_ISSUE.md"
AI_TEMPLATE = ROOT / "templates" / "ROADMAP_AI_CONSTRUCTOR_CONTRACT.md"
PROTOCOL = ROOT / "PROTOCOL.md"
ROADMAP = ROOT / "docs" / "CAPABILITY_ROADMAP.md"


class ForkCapabilityRoadmapIssueTemplateTests(unittest.TestCase):
    def test_human_outline_matches_paperclip_pilot(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# [HARNESS]"))
        self.assertIn("Opensiro", text)
        self.assertNotIn("OpenSiro", text)
        self.assertEqual(
            [line for line in text.splitlines() if line.startswith("## ")],
            [
                "## 1. Why Opensiro and central accepted VSM assessment",
                "## 2. Proposed user capabilities and decision",
                "## 3. Existing native work vs missing capability",
                "## 4. Proposed priority and minimum sufficient result",
                "## 5. Acceptance / stop gates",
                "## 6. Independent paths",
                "## 7. Cost hypothesis",
                "## 8. Decision / handoff",
            ],
        )

    def test_mission_and_central_index_precede_technical_proposal(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        mission = text.index("Opensiro tests whether")
        central = text.index("### Central starting point — accepted Index, not the target")
        vector = text.index("S1=[accepted]")
        six_row_table = text.index("| S1 · Operations |")
        proposal = text.index("## 2. Proposed user capabilities and decision")
        self.assertLess(mission, central)
        self.assertLess(central, vector)
        self.assertLess(vector, six_row_table)
        self.assertLess(six_row_table, proposal)
        for row in (
            "S1 · Operations", "S2 · Coordination", "S3 · Current management",
            "S3* · Independent review", "S4 · Future adaptation", "S5 · Identity/policy",
        ):
            self.assertIn(row, text)
        for function in ("S1", "S2", "S3", "S3*", "S4", "S5"):
            self.assertIn(function + "=[accepted]", text)
        self.assertIn("historical", text.lower())
        self.assertIn("review_ref", text)
        self.assertIn("Profile / Skills", text)
        self.assertIn("not the target", text.lower())
        self.assertIn("not an automatic", text.lower())

    def test_human_scoped_goal_and_preflight(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        for requirement in (
            "P0", "P1", "P2", "A(P)", "C(P)", "NEEDS_EVIDENCE",
            "NO_USEFUL_CHANGE", "Already-confirmed", "no mandatory C",
            "Investigate `?`", "Sufficiency verdict", "not shipping",
            "separate Index review", "SHIPPED / OPEN_PR / ISSUE_ONLY",
            "Cost status: `NOT_MEASURED`", "No public fork Issue",
            "original maintainer request", "exact current-conversation owner approval",
            ".opensiro/issues/<case-id>/", "opensiro/meta", "AI disclosure",
            "Best native operator alternative",
        ):
            self.assertIn(requirement.lower(), text.lower())
        self.assertNotIn("paperclipai/", text)
        self.assertNotIn("browser-use/", text)
        self.assertNotIn("S3=A(P) · S4=—", text)
        self.assertIn("optional", text.lower())
        self.assertIn("do not", text.lower())

    def test_ai_outline_matches_paperclip_pilot_not_old_generic_outline(self):
        text = AI_TEMPLATE.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# [HARNESS]"))
        self.assertNotIn("OpenSiro", text)
        self.assertEqual(
            [line for line in text.splitlines() if line.startswith("## ")],
            [
                "## Functional scope: S2 vs S3 vs S4 vs S5",
                "## 1. Boundary, state, user and developer counterfactual",
                "## 2. Verified existing baseline versus still-proposed change",
                "## 3. Proposed minimum [PRIMARY FUNCTION] first-party construction ports",
                "## 4. Priority and dependency decisions",
                "## 5. Additional [OPTIONAL FUNCTION] constructor proposal — explicitly requested, or NONE",
                "## 6. [PRIMARY FUNCTION] example acceptance scenarios — adapt to repository (not executed)",
                "## 7. Falsification, exclusions and evidence ownership",
            ],
        )
        for phrase in (
            "Level 1 / Human decision Issue",
            "ACCEPTED HISTORICAL INDEX",
            "S1=[accepted]", "S2=[accepted]", "S3=[accepted]",
            "S3*=[accepted]", "S4=[accepted]", "S5=[accepted]",
            "S3↔S4", "SHIPPED", "source-native", "owner",
            "ObservedReturnReceipt", "AC-01 Positive closure",
            "AC-OPTIONAL-01", "NO_USEFUL_CHANGE", "NOT_MEASURED",
            "No original external Issue/comment/PR",
            "not shipped", "not another public Issue",
        ):
            self.assertIn(phrase.lower(), text.lower())

    def test_acceptance_rows_are_examples_not_prescribed_tests(self):
        ai = AI_TEMPLATE.read_text(encoding="utf-8")
        roadmap = ROADMAP.read_text(encoding="utf-8")
        section6 = ai.split("## 6. [PRIMARY FUNCTION] example acceptance scenarios")[1].split("## 7.")[0]
        optional = ai.split("### Example optional acceptance scenarios")[1].split("## 6.")[0]
        for text in (section6, optional):
            self.assertIn("NOT MANDATORY TEST CASES", text)
            self.assertIn("replace", text.lower())
            self.assertIn("repository", text.lower())
        for required in (
            "NOT prescribed tests",
            "MUST independently replace, remove, rename or add",
            "Required coverage (principles, not fixed IDs/count)",
            "No universal nine-case checklist exists",
            "NEEDS_EVIDENCE",
            "NONE / NOT RUN",
            "not acceptance requirements",
        ):
            self.assertIn(required, section6)
        self.assertIn("P2: NONE", optional)
        self.assertIn("delete this entire table", optional)
        self.assertIn("Acceptance example rule", roadmap)
        self.assertIn("illustrative placeholders, not mandatory tests", roadmap)
        self.assertNotIn("MANDATORY AC-01", ai)

    def test_optional_second_function_not_mandatory(self):
        human = TEMPLATE.read_text(encoding="utf-8")
        ai = AI_TEMPLATE.read_text(encoding="utf-8")
        for phrase in (
            "optional other function", "otherwise delete this paragraph",
            "separate developer-composability", "independent",
        ):
            self.assertIn(phrase.lower(), human.lower())
        for phrase in (
            "P2: NONE", "do not invent a second target",
            "only populate", "omit the port and scenario tables",
        ):
            self.assertIn(phrase.lower(), ai.lower())
        self.assertNotIn("paperclipai/", ai)
        self.assertNotIn("razzant/", ai)

    def test_linked_layers_keep_source_and_permissions(self):
        human = TEMPLATE.read_text(encoding="utf-8")
        ai = AI_TEMPLATE.read_text(encoding="utf-8")
        protocol = PROTOCOL.read_text(encoding="utf-8")
        roadmap = ROADMAP.read_text(encoding="utf-8")
        for required in ("ROADMAP_AI_CONSTRUCTOR_CONTRACT.md", "FORK_CAPABILITY_ROADMAP_ISSUE.md"):
            self.assertIn(required, protocol)
            self.assertIn(required, roadmap)
        self.assertIn("ROADMAP_AI_CONSTRUCTOR_CONTRACT.md", human)
        self.assertIn("human issue.md permalink", ai.lower())
        self.assertIn("same accepted six-system vector", human.lower())
        self.assertIn("MUST match the Human Issue", ai)
        self.assertIn("two layers", protocol.lower())
        self.assertIn("Paperclip", protocol)
        self.assertIn("Paperclip", roadmap)
        self.assertIn("two-level", roadmap.lower())
        self.assertIn("full central accepted six-function", protocol.lower())
        self.assertIn("No public fork Issue", human)
        self.assertIn("No original external", ai)
        self.assertIn("NOT_MEASURED", human)
        self.assertIn("NOT_MEASURED", ai)

    def test_canonical_unversioned_case_names(self):
        human = TEMPLATE.read_text(encoding='utf-8')
        ai = AI_TEMPLATE.read_text(encoding='utf-8')
        roadmap = ROADMAP.read_text(encoding='utf-8')
        self.assertIn('/constructor-sufficiency.md', human)
        self.assertIn('human issue.md permalink', ai)
        self.assertIn('Canonical case filenames', roadmap)
        self.assertNotIn('/constructor-sufficiency-v2.md', human)

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
