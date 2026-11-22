"""Roadmap publication uses one existing case and two audience-specific views."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RoadmapSingleCaseLineageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = (ROOT / "PROTOCOL.md").read_text()
        cls.guide = (ROOT / "docs/CAPABILITY_ROADMAP.md").read_text()
        cls.human = (ROOT / "templates/FORK_CAPABILITY_ROADMAP_ISSUE.md").read_text()
        cls.external = (ROOT / "templates/EXTERNAL_ARCHITECTURE_ISSUE.md").read_text()

    def test_same_existing_case_across_two_audiences(self):
        for document in (self.protocol, self.guide, self.human, self.external):
            for filename in ("roadmap.md", "issue.md", "original-issue-draft.md"):
                self.assertIn(filename, document)
        self.assertIn("not a new independent proposal", self.protocol)
        self.assertIn("Reuse and update the *existing* case", self.protocol)
        self.assertIn("not a second independent OpenSiro proposal", self.guide)

    def test_fork_public_issue_is_optional(self):
        self.assertIn("has_issues=false", self.protocol)
        self.assertIn("FORK_ISSUES_DISABLED / NOT_PUBLISHED", self.protocol)
        self.assertIn("not a prerequisite", self.protocol)
        self.assertIn("has_issues=false", self.guide)
        self.assertIn("optional", self.human)
        self.assertIn("optional", self.external)

    def test_original_is_a_separate_public_action_not_new_case(self):
        self.assertIn("distinct **public GitHub object/action**", self.protocol)
        self.assertIn("exact current-conversation approval", self.protocol)
        self.assertIn("native Issue Form", self.protocol)
        self.assertIn("original project's native channel/template", self.guide)
        self.assertIn("separate exact", self.external)


if __name__ == "__main__":
    unittest.main()
