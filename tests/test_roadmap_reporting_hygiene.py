from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RoadmapReportingHygieneTests(unittest.TestCase):
    def test_one_supplementary_page_and_no_per_run_pr_guidance(self):
        protocol = (ROOT / "PROTOCOL.md").read_text(encoding="utf-8")
        report = (ROOT / "docs/ROADMAP_REPORT.md").read_text(encoding="utf-8")
        self.assertIn("Do not open an Upstream PR solely to record an individual Roadmap run", protocol)
        self.assertIn("Close obsolete internal status-only PRs without merging", protocol)
        self.assertIn("## Supplementary", report)
        self.assertIn("opensiro-contributions", report)

    def test_handoff_surface_links_same_report(self):
        for path in ["README.md", "AGENTS.md", "docs/ROADMAP_INDEPENDENT_RERUN.md"]:
            text = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn("ROADMAP_REPORT.md#supplementary", text)


if __name__ == "__main__":
    unittest.main()
