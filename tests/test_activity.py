"""Offline tests for the read-only GitHub-style PR activity projection."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from activity import linked_prs, collect, svg, markdown, review_approval
from aggregate import APIError

TIME = "2026-11-16T12:00:00Z"
BASE = "https://github.com/example/agent/pull/"


def snapshot(urls):
    return {"generated_at": TIME,
        "coverage": {"scan_complete": True, "errors": 0, "filtered_by_attention": 0},
        "forks": [{"working_fork": "opensiro-contributions/agent",
                   "original_repository": "example/agent",
                   "contributions": [{"id": "feature-a", "external_prs": [{"url": u} for u in urls]},
                                     {"id": "feature-b", "external_prs": [{"url": urls[0]}]}]}]}


class FakeGitHub:
    def __init__(self):
        self.routes = {}
        self.seen = []

    def get(self, path):
        self.seen.append(path)
        if path not in self.routes:
            raise APIError(404, "not found")
        return self.routes[path]

    def add(self, number, *, state="open", merged=None, closed=None,
            created="2026-10-24T12:00:00Z", reviews=None):
        self.routes[f"/repos/example/agent/pulls/{number}"] = {
            "html_url": BASE + str(number), "created_at": created, "state": state,
            "merged_at": merged, "closed_at": closed,
        }
        if state == "closed" and merged is None:
            self.routes[f"/repos/example/agent/pulls/{number}/reviews?per_page=100&page=1"] = reviews or []
        return self


class ActivityTests(unittest.TestCase):
    def test_one_unique_url_even_if_linked_twice(self):
        self.assertEqual(len(linked_prs(snapshot([BASE+"1", BASE+"2"]))), 2)
        self.assertEqual(len(linked_prs(snapshot([BASE+"1"]))), 1)

    def test_published_merge_closed_approved_subset_and_open(self):
        client = (FakeGitHub()
                  .add(1, state="closed", merged="2026-10-25T01:00:00Z",
                       closed="2026-10-25T01:00:00Z")
                  .add(2, state="closed", closed="2026-10-28T01:00:00Z", reviews=[
                      {"user": {"login": "maintainer"}, "state": "APPROVED",
                       "submitted_at": "2026-10-27T01:00:00Z"}])
                  .add(3))
        report = collect(client, snapshot([BASE+"1", BASE+"2", BASE+"3"]), observed_at=TIME)
        self.assertTrue(report["complete"])
        self.assertEqual(report["summary"], {"published": 3, "merged": 1, "open": 1,
            "closed_unmerged": 1, "closed_with_approval_review": 1, "unknown": 0})
        self.assertEqual(len(report["events"]), 5)
        output = svg(report, weeks=8)
        self.assertIn("2026-10-24: 3 events", output)
        self.assertIn("Closed w/ APPROVED review", output)
        self.assertIn("**3**", markdown(report))
        self.assertTrue(all(path.startswith("/repos/") for path in client.seen))

    def test_closed_without_review_not_approved(self):
        client = FakeGitHub().add(1, state="closed", closed="2026-10-26T01:00:00Z")
        report = collect(client, snapshot([BASE+"1"]), observed_at=TIME)
        self.assertEqual(report["summary"]["closed_with_approval_review"], 0)
        self.assertEqual(report["summary"]["closed_unmerged"], 1)

    def test_changes_requested_supersedes_earlier_approval(self):
        client = FakeGitHub().add(1, state="closed", closed="2026-10-26T01:00:00Z", reviews=[
            {"user": {"login": "maintainer"}, "state": "APPROVED",
             "submitted_at": "2026-10-24T15:00:00Z"},
            {"user": {"login": "maintainer"}, "state": "CHANGES_REQUESTED",
             "submitted_at": "2026-10-25T15:00:00Z"}])
        self.assertFalse(review_approval(client, "example/agent", "1",
            __import__("datetime").datetime.fromisoformat("2026-10-26T01:00:00+00:00")))

    def test_unknown_is_not_misrepresented_as_zero(self):
        client = FakeGitHub().add(1)
        report = collect(client, snapshot([BASE+"1", BASE+"2"]), observed_at=TIME)
        self.assertFalse(report["complete"])
        self.assertEqual(report["summary"]["unknown"], 1)
        with self.assertRaises(ValueError):
            svg(report)
        with self.assertRaises(ValueError):
            markdown(report)

    def test_bad_parent_or_incomplete_snapshot_fails_closed(self):
        snap = snapshot([BASE+"1"])
        snap["forks"][0]["original_repository"] = "different/agent"
        with self.assertRaises(ValueError):
            linked_prs(snap)
        snap = snapshot([BASE+"1"])
        snap["coverage"]["scan_complete"] = False
        with self.assertRaises(ValueError):
            linked_prs(snap)
        snap = snapshot([BASE+"1"])
        snap["coverage"]["filtered_by_attention"] = 1
        with self.assertRaises(ValueError):
            linked_prs(snap)

    def test_replacement_prs_count_separately_but_improvements_not(self):
        client = (FakeGitHub()
                  .add(1, state="closed", closed="2026-10-26T01:00:00Z")
                  .add(2, state="closed", merged="2026-10-27T01:00:00Z",
                       closed="2026-10-27T01:00:00Z"))
        report = collect(client, snapshot([BASE+"1", BASE+"2"]), observed_at=TIME)
        self.assertEqual(report["independent_contributions"], 2)
        self.assertEqual(report["summary"]["published"], 2)
        self.assertEqual(report["summary"]["closed_unmerged"], 1)
        self.assertEqual(report["summary"]["merged"], 1)


if __name__ == "__main__":
    unittest.main()
