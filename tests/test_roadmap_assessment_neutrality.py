"""Roadmap assessment neutrality vs maintainer product decisions."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class NeutralityContractTest(unittest.TestCase):
    def check(self, name, *phrases):
        content = (ROOT / name).read_text()
        for phrase in phrases:
            with self.subTest(name=name, phrase=phrase):
                self.assertIn(phrase, content)

    def test_protocol(self):
        self.check("PROTOCOL.md", "Assessment neutrality and maintainer authority",
                   "Constructibility precedes product desirability",
                   "VSM function, decisive decision owner and closure path")
    def test_guide(self):
        self.check("docs/CAPABILITY_ROADMAP.md",
                   "Assessment-neutral construction; maintainer-owned product decisions",
                   "functional equivalence must be shown",
                   "Maintainers alone decide adoption")
    def test_templates(self):
        self.check("templates/ROADMAP_AI_CONSTRUCTOR_CONTRACT.md",
                   "maintainer's product preference is not a constructibility verdict")
        self.check("templates/FORK_CAPABILITY_ROADMAP_ISSUE.md",
                   "not whether maintainers should adopt")
        self.check("templates/EXTERNAL_ARCHITECTURE_ISSUE.md",
                   "The maintainers alone decide product fit")
        self.check("docs/ROADMAP_INDEPENDENT_RERUN.md",
                   "Assess architectural C sufficiency")
    def test_release(self):
        self.check("VERSION", "0.18.1")
        self.check("CHANGELOG.md", "Assessment neutrality / maintainer-owned adoption")
        self.check("changes/v0.18.0.md", "Assessment-neutral constructibility")

if __name__ == "__main__":
    unittest.main()
