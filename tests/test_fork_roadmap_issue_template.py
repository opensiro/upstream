"""Guardrails for the reusable Opensiro fork-local roadmap Issue template."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "FORK_CAPABILITY_ROADMAP_ISSUE.md"


class ForkCapabilityRoadmapIssueTemplateTests(unittest.TestCase):
    def test_template_is_generic_and_source_driven(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# [PROJECT]"))
        self.assertIn("Opensiro", text)
        self.assertNotIn("OpenSiro", text)
        for part in (
            "## Why this Issue exists",
            "## Source and evidence",
            "## What already exists?",
            "## Proposed priorities",
            "## How would we know it helps?",
            "## Independent next steps",
            "## Decision / handoff",
        ):
            self.assertIn(part, text)
        self.assertIn("Current implementation", text)
        self.assertIn("Remaining gap", text)
        self.assertIn("Simplest original-native alternative", text)
        self.assertNotIn("paperclipai/", text)
        self.assertNotIn("browser-use/", text)

    def test_no_unearned_capability_or_cost_claims(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        for required in (
            "NOT_MEASURED",
            "No automatic implementation",
            "not a delivered",
            "No mandatory grade progression",
            "No-change condition",
            "Positive case",
            "Negative case",
        ):
            self.assertIn(required, text)

    def test_case_location_and_publication_boundaries(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn(".opensiro/issues/<case-id>/", text)
        self.assertIn("opensiro/meta", text)
        self.assertIn("separate exact approval", text)
        self.assertIn("not a cross-owner transfer", text)
        self.assertIn("fork-local discussion", text)
        self.assertIn("AI disclosure", text)
        self.assertIn("This is NOT the external maintainer issue template", text)

    def test_protocol_routes_to_correct_templates(self):
        p = (ROOT / "PROTOCOL.md").read_text(encoding="utf-8")
        g = (ROOT / "docs/CAPABILITY_ROADMAP.md").read_text(encoding="utf-8")
        for s in (p, g):
            self.assertIn("FORK_CAPABILITY_ROADMAP_ISSUE.md", s)
            self.assertIn("EXTERNAL_ARCHITECTURE_ISSUE.md", s)
        self.assertTrue((ROOT / "templates/EXTERNAL_ARCHITECTURE_ISSUE.md").exists())
        external = (ROOT / "templates/EXTERNAL_ARCHITECTURE_ISSUE.md").read_text(encoding="utf-8")
        self.assertIn("Opensiro", external)
        self.assertNotIn("OpenSiro", external)


if __name__ == "__main__":
    unittest.main()
