"""Regression contract for the terminal Roadmap publication handoff."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RoadmapOwnerPublicationHandoff(unittest.TestCase):
    def test_every_terminal_handoff_names_concrete_outreach(self):
        for name in ("PROTOCOL.md", "AGENTS.md", "README.md", "docs/CAPABILITY_ROADMAP.md"):
            with self.subTest(name=name):
                text = (ROOT / name).read_text()
                self.assertIn("Proposed public Issue / outreach", text)
                self.assertIn("readiness", text)
                self.assertIn("no outreach", text)
                self.assertIn("native template/channel", text)

    def test_candidate_is_not_approval_or_a_case_link(self):
        text = (ROOT / "PROTOCOL.md").read_text()
        block = text.split("**Mandatory owner-facing publication candidate in every Roadmap handoff.**", 1)[1].split("\n\n", 1)[0]
        for phrase in ("complete candidate public body", "unapproved local draft", "conditional unlock", "PAUSE/STOP", "exact consent", "only a fully gated persisted-case preview may request approval", "GO + NEEDS_EVIDENCE alone is not a reason to suppress a candidate", "public fork Issue from original outreach", "not a substitute"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, block)


if __name__ == "__main__":
    unittest.main()
