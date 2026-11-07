"""Offline contract tests for the deduplicated external PR portfolio observer."""

import importlib.util
import io
import sys
from pathlib import Path
import unittest
from urllib.error import HTTPError


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("portfolio_reconcile", ROOT / "scripts/portfolio_reconcile.py")
portfolio = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(portfolio)

BASE = "https://github.com/Owner/repo/pull/"


def entry(n, *groups):
    return {"url": BASE + str(n), "groups": list(groups or ("watchlist",))}


def payload(n, state="open", merged_at=None):
    return {"html_url": BASE + str(n), "number": n, "state": state, "merged_at": merged_at}


class FakeAPI:
    def __init__(self, prs=None, events=None):
        self.prs = prs or {}
        self.events = events or {}
        self.calls = []

    def get(self, path):
        self.calls.append(("GET", path))
        number = int(path.rsplit("/", 1)[-1])
        result = self.prs[number]
        if result == "404":
            raise HTTPError("https://api.github.com" + path, 404, "Not Found", {}, io.BytesIO())
        return result

    def pages(self, path):
        self.calls.append(("PAGES", path))
        return self.events.get(int(path.split("/issues/")[1].split("/")[0]), [])


class PortfolioReconcileTests(unittest.TestCase):
    def test_frozen_source_union_exact_size_and_identity(self):
        entries = portfolio.cohort()
        self.assertEqual(len(entries), 25)
        self.assertEqual(sum("watchlist" in row["groups"] for row in entries), 18)
        self.assertEqual(len({row["url"] for row in entries}), 25)
        self.assertEqual(len([row for row in entries if "casebook" in row["groups"]]), 9)
        self.assertEqual(len([row for row in entries if "registry" in row["groups"]]), 1)
        self.assertEqual(
            [row["groups"] for row in entries if row["url"] ==
             "https://github.com/androoAGI/starnet/pull/56"], [["casebook", "watchlist"]])

    def test_live_classification_and_attribution_are_separate(self):
        api = FakeAPI(
            {1: payload(1, "closed", "2026-11-01T00:00:00Z"),
             2: payload(2, "closed"),
             3: payload(3)},
            {2: [{"event": "closed", "created_at": "2026-11-01T01:00:00Z",
                  "actor": {"login": "first"}},
                 {"event": "reopened", "created_at": "2026-11-01T02:00:00Z"},
                 {"event": "closed", "created_at": "2026-11-01T03:00:00Z",
                  "actor": {"login": "last"}}]})
        report = portfolio.observe(api, [entry(1, "watchlist", "casebook"),
                                         entry(2, "casebook"), entry(3, "watchlist")],
                                   observed_at="2026-11-07T12:00:00Z")
        broad = portfolio.summarize(report)
        watch = portfolio.summarize(report, group="watchlist")
        self.assertEqual((broad["merged"], broad["closed_unmerged"], broad["open"]), (1, 1, 1))
        self.assertEqual((watch["merged"], watch["closed_unmerged"], watch["open"]), (1, 0, 1))
        self.assertEqual(broad["rate"], 0.5)
        self.assertEqual(watch["rate"], 1.0)
        self.assertEqual(report["records"][1]["closure"]["actor"], "last")
        self.assertEqual(len([x for x in api.calls if x[0] == "PAGES"]), 1)
        output = portfolio.render(report)
        self.assertIn("50.0% (1/2)", output)
        self.assertIn("100.0% (1/1)", output)
        self.assertIn("not", output.lower())

    def test_closed_without_event_does_not_invent_actor(self):
        report = portfolio.observe(FakeAPI({2: payload(2, "closed")}), [entry(2)])
        self.assertIsNone(report["records"][0]["closure"]["actor"])
        self.assertIn("NO_CLOSED_EVENT", portfolio.render(report))

    def test_unknown_404_fails_closed(self):
        with self.assertRaises(HTTPError):
            portfolio.observe(FakeAPI({4: "404"}), [entry(4)])

    def test_known_404_requires_exact_identity(self):
        record = {"url": portfolio.KNOWN_404, "groups": ["watchlist"]}
        repo, number = portfolio.identity(portfolio.KNOWN_404)

        class MissingAPI:
            def get(self, path):
                self.asserted_path = path
                raise HTTPError("https://api.github.com" + path, 404, "Not Found", {}, io.BytesIO())

        api = MissingAPI()
        report = portfolio.observe(api, [record])
        self.assertEqual(api.asserted_path, f"/repos/{repo}/pulls/{number}")
        self.assertEqual(portfolio.summarize(report)["unverifiable"], 1)
        self.assertIsNone(portfolio.summarize(report)["rate"])

    def test_invalid_identity_and_malformed_report_fail_closed(self):
        for url in ("http://github.com/Owner/repo/pull/1",
                    "https://github.com/Owner/repo/issues/1",
                    "https://github.com/Owner/repo/pull/01"):
            with self.assertRaises(ValueError):
                portfolio.identity(url)
        report = {"schema_version": 1, "records": [
            {"url": BASE + "1", "groups": ["watchlist"], "outcome": "open"},
            {"url": BASE + "1", "groups": ["casebook"], "outcome": "merged"}]}
        with self.assertRaisesRegex(ValueError, "duplicate"):
            portfolio.summarize(report)


if __name__ == "__main__":
    unittest.main()
