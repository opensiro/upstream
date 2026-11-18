"""Fail-closed original-specific Upstream interactions require accepted general Index assessment."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class AcceptedAssessmentPrerequisiteTests(unittest.TestCase):
    def test_documents_gate_named_origins(self):
        for path in ("PROTOCOL.md", "docs/CAPABILITY_ROADMAP.md", "AGENTS.md", "README.md"):
            body = (ROOT / path).read_text()
            for token in ("ASSESSMENT_REQUIRED", "BLOCKED", "assessment", "included", "catalog", "review_ref", "proposed"):
                self.assertIn(token, body, f"{path} missing {token}")
        protocol = (ROOT / "PROTOCOL.md").read_text().split("## Mandatory accepted-assessment prerequisite", 1)[1].split("\n## ", 1)[0]
        for token in ("upstream roadmap", "upstream upgrade", "Index-owned", "Gas Town", "Gas City", "exact current-conversation"):
            self.assertIn(token, protocol)
        self.assertIn("NO_USEFUL_CHANGE", protocol)
        self.assertIn("canonical Index", protocol)
    def test_dedicated_roadmap_route_is_not_an_exception(self):
        route = (ROOT / "docs/CAPABILITY_ROADMAP.md").read_text()
        self.assertIn("A named original is **not exempt**", route)
        self.assertIn("re-run", route.lower())
