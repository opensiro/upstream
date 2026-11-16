"""Read-only Git regression of the existing-dashboard-PR update decision."""
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/refresh-activity.yml"
FILES = ("docs/activity.svg", "docs/ACTIVITY.md", "docs/activity-sources.json")


def git(where, *args, check=True):
    return subprocess.run(["git", "-C", str(where), *args], capture_output=True, text=True, check=check)


class DashboardWorkflowTests(unittest.TestCase):
    def test_dashboard_is_only_source_verified_files_nonforce_commit(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("contents: write", text)
        self.assertNotIn("pull-requests: write", text)
        self.assertIn("git add -- docs/ACTIVITY.md docs/activity.svg docs/activity-sources.json", text)
        self.assertIn("git diff --cached --quiet", text)
        self.assertIn("git push origin HEAD:refs/heads/main", text)
        self.assertIn("git ls-remote origin refs/heads/main", text)
        self.assertNotIn("create-pull-request", text)
        self.assertNotIn("git push --force", text)
        self.assertNotIn("git add -A", text)

    def test_git_diff_detects_real_change_not_restored_review_branch(self):
        with tempfile.TemporaryDirectory() as name:
            repo = Path(name)
            git(repo, "init", "-b", "main")
            git(repo, "config", "user.name", "Test")
            git(repo, "config", "user.email", "test@example.com")
            (repo / "docs").mkdir()
            for f in FILES[:2]:
                (repo / f).write_text("old snapshot\n", encoding="utf-8")
            git(repo, "add", "--", *FILES[:2])
            git(repo, "commit", "-m", "base")
            git(repo, "switch", "-c", "automation/activity-dashboard-refresh")
            for f in FILES:
                (repo / f).write_text("observed snapshot\n", encoding="utf-8")
            git(repo, "add", "--", *FILES)
            git(repo, "commit", "-m", "first observation")
            git(repo, "switch", "main")
            git(repo, "restore", "--source=automation/activity-dashboard-refresh",
                "--staged", "--worktree", "--", *FILES)
            # Git difference against already-reviewed branch must be empty.
            self.assertEqual(
                git(repo, "diff", "--quiet", "automation/activity-dashboard-refresh", "--", *FILES,
                    check=False).returncode, 0)
            (repo / "docs/ACTIVITY.md").write_text("new source state\n", encoding="utf-8")
            self.assertEqual(
                git(repo, "diff", "--quiet", "automation/activity-dashboard-refresh", "--", *FILES,
                    check=False).returncode, 1)


if __name__ == "__main__":
    unittest.main()
