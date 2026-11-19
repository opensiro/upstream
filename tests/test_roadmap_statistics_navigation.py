"""Contract regression: roadmap statistics must dispatch to the executable view first."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RoadmapStatisticsNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.readme = (ROOT / "README.md").read_text()
        cls.agents = (ROOT / "AGENTS.md").read_text()
        cls.protocol = (ROOT / "PROTOCOL.md").read_text()
        cls.view = (ROOT / "scripts/roadmap_view.py").read_text()
        cls.changelog = (ROOT / "CHANGELOG.md").read_text()
        cls.stats = cls.protocol.split(
            "## Roadmap portfolio statistics / case inventory (read-only; script-first)", 1
        )[1].split("\n## ", 1)[0]

    def test_stats_intent_is_script_first_in_all_entrypoints(self):
        for doc in (self.readme, self.agents, self.stats):
            for phrase in ("собери статистику по роадмапу", "scripts/roadmap_view.py --format json",
                           "roadmap_select.py", "aggregate.py"):
                self.assertIn(phrase, doc)
        self.assertLess(self.readme.index("## Command navigation"),
                        self.readme.index("## Index-first candidate selection"))
        self.assertLess(self.protocol.index("## Roadmap portfolio statistics"),
                        self.protocol.index("## Index-first `upstream roadmap` selection"))

    def test_failure_and_scope_are_explicit_not_fake_complete(self):
        for phrase in ("script not executed", "scan_complete", "historical_inventory_complete",
                       "PARTIAL", "NOT VERIFIED", "warnings", "scope"):
            self.assertIn(phrase.lower(), self.stats.lower())
        for phrase in ("without .opensiro/issues", "verified_forks"):
            # Verify key coverage is specified through either field or section text.
            self.assertTrue(phrase in self.stats or
                            (phrase == "without .opensiro/issues" and "no_issues_directory" in self.stats))
        self.assertIn("--live-original", self.stats)
        self.assertIn("--repo", self.stats)
        self.assertIn("no `--repo` or `--only-active`", self.agents)

    def test_script_exposes_documented_json_and_coverage(self):
        for phrase in ('parser.add_argument("--format"', '"json"', '"coverage"',
                       '"historical_inventory_complete"', '"scan_complete"',
                       'parser.add_argument("--live-original"'):
            self.assertIn(phrase, self.view)
        self.assertIn("Roadmap statistics script-first navigation", self.changelog)

    def test_research_disposition_is_not_terminal_decision(self):
        self.assertIn("research disposition", self.stats)
        self.assertIn("GO/NO_GO/BLOCKED", self.stats)
        self.assertIn("HISTORICAL_TEMPLATE_PILOT", self.stats)
        self.assertIn("NOT_CHECKED", self.stats)
        self.assertIn("UNKNOWN", self.stats)


if __name__ == "__main__":
    unittest.main()
