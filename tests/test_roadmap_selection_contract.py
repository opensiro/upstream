"""Contract tests: Index-first candidate discovery never overrides named-roadmap rights."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RoadmapSelectionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = (ROOT / "PROTOCOL.md").read_text()
        cls.readme = (ROOT / "README.md").read_text()
        cls.guide = (ROOT / "docs/CAPABILITY_ROADMAP.md").read_text()
        cls.agents = (ROOT / "AGENTS.md").read_text()

    def test_index_first_source_boundary(self):
        for s in ("Index-first", "accepted", "TLDR.md", "catalog",
                  "license", "PAUSE/STOP", "issues", "PR", "one"):
            self.assertIn(s.lower(), self.protocol.lower())
        self.assertIn("scripts/roadmap_select.py", self.protocol)
        self.assertIn("scripts/roadmap_select.py", self.agents)
        self.assertIn("scripts/roadmap_select.py", self.readme)

    def test_named_original_remains_full_cycle(self):
        for s in ("upstream roadmap OWNER/REPO", "Human", "AI", "fork-local",
                  "separate exact current-conversation owner-consent"):
            self.assertIn(s, self.protocol)
        self.assertIn("upstream roadmap select", self.protocol)
        self.assertIn("No effects from selection", self.protocol)

    def test_neither_missing_grade_nor_title_implies_useful_c(self):
        for s in ("issue titles", "not proof", "Index", "grade",
                  "original PR", "NO_USEFUL_CHANGE", "NEEDS_EVIDENCE"):
            self.assertIn(s.lower(), self.protocol.lower())
        self.assertIn("not an established useful", self.readme)
        self.assertIn("never automatically", self.guide.lower())

    def test_view_and_contribution_are_distinct(self):
        self.assertIn("scripts/roadmap_view.py", self.protocol)
        self.assertIn("scripts/aggregate.py", self.protocol)
        self.assertIn("not three authorities", self.protocol)
        self.assertIn("public fork", self.protocol)


if __name__ == "__main__":
    unittest.main()
