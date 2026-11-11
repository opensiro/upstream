"""Source-only tests for the independent resolved-PR acceptance metric."""

import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from urllib.error import HTTPError


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("resolved_acceptance", ROOT / "scripts/resolved_pr_acceptance.py")
import sys
sys.path.insert(0, str(ROOT / "scripts"))
metric = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(metric)

BASE = "https://github.com/Example/repo/pull/"


def target(number):
    return {"repository": "Example/repo", "number": number, "url": BASE + str(number)}


def source(number, state="open", merged_at=None):
    return {"html_url": BASE + str(number), "number": number,
            "state": state, "merged_at": merged_at}


class FakeAPI:
    def __init__(self, prs):
        self.prs = prs
        self.comments = []
        self.writes = []

    def get(self, path):
        if path == "/repos/opensiro/upstream/issues/125":
            return {"state": "open"}
        number = int(path.rsplit("/", 1)[1])
        result = self.prs[number]
        if result == "404":
            raise HTTPError("https://api.github.com" + path, 404, "Not Found", {}, io.BytesIO())
        if isinstance(result, BaseException):
            raise result
        return result

    def pages(self, path):
        self.asserted_path = path
        return self.comments

    def request(self, path, method="GET", payload=None):
        if path != "/repos/opensiro/upstream/issues/125/comments" and not path.startswith(
                "/repos/opensiro/upstream/issues/comments/"):
            raise AssertionError("Unexpected GitHub write: " + path)
        self.writes.append((path, method, payload))
        if method == "POST":
            self.comments.append({"id": 11, "user": {"login": "github-actions[bot]"},
                                  "body": payload["body"]})
        elif method == "PATCH":
            self.comments[0]["body"] = payload["body"]
        else:
            raise AssertionError("Unapproved method")


def manifest(path, count=4):
    data = {"schema_version": 1, "inbox_issue": "https://github.com/opensiro/upstream/issues/125",
            "targets": [target(n) for n in range(1, count + 1)]}
    path.write_text(json.dumps(data), encoding="utf-8")


class AcceptanceTests(unittest.TestCase):
    def test_resolved_rate_excludes_open_and_404(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "targets.json"
            manifest(path)
            api = FakeAPI({1: source(1, "closed", "2026-10-30T00:00:00Z"),
                           2: source(2, "closed"), 3: source(3), 4: "404"})
            report = metric.observe(api, path, observed_at="2026-11-05T12:00:00Z")
            stats = metric.summarize(report)
            self.assertEqual((stats["merged"], stats["closed_unmerged"], stats["open"],
                              stats["unverifiable"], stats["resolved"]), (1, 1, 1, 1, 2))
            self.assertEqual(stats["rate"], 0.5)
            text = metric.render(report)
            self.assertIn("50.0% (1/2)", text)
            self.assertIn("not counted as failures", text)
            self.assertEqual(len(report["records"]), 4)

    def test_zero_resolved_is_not_100_percent(self):
        report = {"schema_version": 1, "records": [
            {"url": BASE + "1", "outcome": "open"},
            {"url": BASE + "2", "outcome": "unverifiable"}],
            "observed_at": "2026-11-05T12:00:00Z"}
        self.assertIsNone(metric.summarize(report)["rate"])
        self.assertIn("N/A (no resolved PRs)", metric.render(report))

    def test_unknown_or_false_source_rejected_not_as_negative_outcome(self):
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            metric.classify(source(2), target(1))
        with self.assertRaisesRegex(ValueError, "Contradictory"):
            metric.classify(source(1, "open", "2026-10-30T00:00:00Z"), target(1))
        with self.assertRaisesRegex(ValueError, "Unknown"):
            metric.classify(source(1, "queued"), target(1))
        with self.assertRaisesRegex(ValueError, "Unknown"):
            metric.classify(source(1, "closed", ""), target(1))
        with self.assertRaisesRegex(ValueError, "Unknown acceptance"):
            metric.summarize({"schema_version": 1, "records": [{"url": BASE + "1", "outcome": "rejected"}]})

    def test_non_404_error_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "targets.json"
            manifest(path, 1)
            api = FakeAPI({1: HTTPError(BASE + "1", 403, "Forbidden", {}, io.BytesIO())})
            with self.assertRaises(HTTPError):
                metric.observe(api, path)

    def test_report_is_owned_comment_idempotent_and_dated(self):
        api = FakeAPI({})
        report = {"schema_version": 1, "observed_at": "2026-11-05T12:00:00Z", "records": [
            {"url": BASE + "1", "outcome": "merged"}]}
        self.assertTrue(metric.update_inbox(api, report))
        self.assertEqual(len(api.writes), 1)
        self.assertEqual(api.writes[0][1], "POST")
        self.assertIn(metric.MARKER, api.comments[0]["body"])
        self.assertFalse(metric.update_inbox(api, report))
        self.assertEqual(len(api.writes), 1)
        newer = dict(report, observed_at="2026-11-06T10:00:00Z")
        self.assertTrue(metric.update_inbox(api, newer))
        self.assertEqual(api.writes[-1][1], "PATCH")
        self.assertEqual(len(api.comments), 1)

    def test_multiple_bot_report_comments_fail_before_write(self):
        api = FakeAPI({})
        api.comments = [{"id": x, "user": {"login": "github-actions[bot]"},
                         "body": metric.MARKER} for x in (1, 2)]
        with self.assertRaisesRegex(ValueError, "Multiple acceptance"):
            metric.update_inbox(api, {"schema_version": 1, "observed_at": "2026-11-05",
                                      "records": [{"url": BASE + "1", "outcome": "open"}]})
        self.assertFalse(api.writes)

    def test_only_reviewed_watchlist_and_no_unreviewed_expansion(self):
        self.assertEqual(len(metric.validate_targets()["targets"]), 29)
        self.assertEqual(metric.INBOX_REPO, "opensiro/upstream")
        self.assertEqual(metric.INBOX_NUMBER, 125)


if __name__ == "__main__":
    unittest.main()
