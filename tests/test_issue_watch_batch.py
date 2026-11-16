"""Tests for bounded discovery, preview dedup, and opt-in scheduled watch gates."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from issue_watch_batch import discover, run
from test_issue_watch import FakeGitHub, FORK, IDENT, source_comment


def portfolio():
    return {
        "scope": "public_organization_repositories",
        "coverage": {"scan_complete": True, "errors": 0, "filtered_by_attention": 0},
        "forks": [{"working_fork": FORK,
                   "contributions": [{"id": IDENT, "issue_watch": {
                       "issue_url": "https://github.com/openclaw/openclaw/issues/147509"}}]}],
    }


class BatchTests(unittest.TestCase):
    def test_fork_local_discovery_not_another_issue_ledger(self):
        self.assertEqual(discover(portfolio()), [(FORK, IDENT)])
        a = portfolio()
        a["forks"][0]["contributions"].append({"id": "other", "issue_watch": None})
        self.assertEqual(discover(a), [(FORK, IDENT)])

    def test_fails_closed_on_partial_overflow_and_duplicates(self):
        for key, value in (("scan_complete", False), ("errors", 1), ("filtered_by_attention", 1)):
            x=portfolio()
            x["coverage"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                discover(x)
        with self.assertRaises(ValueError):
            discover(portfolio(), max_targets=0)
        x=portfolio()
        x["forks"].append(x["forks"][0])
        with self.assertRaises(ValueError):
            discover(x)

    def test_preview_only_does_not_claim_alert_persisted(self):
        gh=FakeGitHub()
        gh.comments.append(source_comment(7000000000))
        data=run(lambda fork, apply: gh, [(FORK,IDENT)], apply=False)
        self.assertEqual(data["persisted_alerts"], 0)
        self.assertEqual(data["preview_changes"], 1)
        self.assertEqual(data["failures"], 0)
        self.assertEqual(gh.posts, [])

    def test_confirmed_change_only_alerts_once_with_durable_cursor(self):
        gh=FakeGitHub()
        gh.comments.append(source_comment(7000000000))
        factory=lambda fork, apply: gh
        first=run(factory, [(FORK,IDENT)], apply=True)
        self.assertEqual(first["persisted_alerts"], 1)
        self.assertEqual(first["failures"], 0)
        again=run(factory, [(FORK,IDENT)], apply=True)
        self.assertEqual(again["persisted_alerts"], 0)
        self.assertEqual(again["failures"], 0)

    def test_unknown_does_not_fake_zero_or_change_state(self):
        gh=FakeGitHub()
        gh.comments=[]
        result=run(lambda fork, apply: gh, [(FORK,IDENT)], apply=True)
        self.assertEqual(result["failures"],1)
        self.assertEqual(result["persisted_alerts"],0)
        self.assertEqual(gh.posts,[])

    def test_schedule_is_explicit_opt_in_with_no_pr_or_issue_write_access(self):
        import yaml
        w=yaml.safe_load((ROOT/".github/workflows/observe-issues.yml").read_text())
        self.assertEqual(w["permissions"], {"contents": "read"})
        raw=(ROOT/".github/workflows/observe-issues.yml").read_text()
        self.assertIn("UPSTREAM_ISSUE_WATCH_ENABLED", raw)
        self.assertIn("OPENSIRO_FORK_WATCH_TOKEN", raw)
        self.assertIn("workflow_dispatch",raw)
        self.assertIn("GH_TOKEN=", raw)
        self.assertNotIn("pull-requests: write", raw)
        self.assertNotIn("create-pull-request",raw)


if __name__=="__main__":
    unittest.main()
