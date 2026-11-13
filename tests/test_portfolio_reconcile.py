"""Offline contract tests for the deduplicated external PR portfolio observer."""

import copy
import importlib.util
import io
import json
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
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
    @staticmethod
    def full_portfolio_report():
        entries = portfolio.cohort()
        records = [dict(row, outcome="open") for row in entries]
        return {"schema_version": 1, "observed_at": "2026-11-13T17:00:00+00:00",
                "cohort_sha256": portfolio.cohort_fingerprint(records),
                "records": records}

    @staticmethod
    def accepted_export(report):
        import verified_external_outcomes as evidence
        ledger = json.loads((ROOT / "data/verified-external-outcomes/accepted-v1.json").read_text())
        rows = []
        for entry in ledger["accepted"]:
            url = entry["effective_pr_url"]
            next(row for row in report["records"] if row["url"] == url)["outcome"] = "merged"
            rows.append({"intervention_id": entry["intervention_id"],
                         "external_pr_url": url, "merge_commit_sha": entry["merge_commit_sha"],
                         "native_receipt": entry["native_receipt"],
                         "decision": "ACCEPTED_MERGED_CHANGE_ONLY",
                         "acceptance_basis": "DETERMINISTIC_VERIFIED_MERGE",
                         "benefit_claim": "NOT_MEASURED"})
        return {"schema_version": 1, "source": "opensiro/upstream",
                "metric_status": "UPSTREAM_ACCEPTED_SOURCE_ONLY",
                "observed_at": report["observed_at"],
                "source_sha256": evidence.digest_sources(),
                "portfolio_cohort_sha256": report["cohort_sha256"],
                "accepted_count": len(rows), "accepted": rows,
                "organization_metric_claimed": False}

    def test_joined_view_preserves_distinct_external_and_accepted_counts(self):
        report = self.full_portfolio_report()
        view = portfolio.joined_view(report)
        self.assertEqual(view["summary"]["unique_prs"], 43)
        self.assertEqual(view["summary"]["watched_prs"], 36)
        self.assertIsNone(view["summary"]["accepted_changes"])
        self.assertEqual({r["verified_outcome"] for r in view["records"]}, {"NOT_LIVE_CHECKED"})
        self.assertIn("not live-checked", portfolio.render_joined(view))
        friday = next(row for row in view["records"]
                      if row["url"] == "https://github.com/splashxmoon/friday/pull/23")
        self.assertEqual(friday["assessment_origin"], ["ASSESSMENT_DERIVED_HYPOTHESIS"])
        self.assertEqual(friday["functional_effects"][0]["measurement_level"],
                         "NATIVE_TOOL_BEHAVIOR")
        self.assertEqual(friday["functional_effects"][0]["product_benefit"], "NOT_MEASURED")
        for r in view["records"]:
            self.assertNotEqual(r["product_benefit"], "MEASURED")
        self.assertEqual(len({r["url"] for r in view["records"]}), 43)

        accepted = self.accepted_export(report)
        verified = portfolio.joined_view(report, accepted)
        self.assertEqual(verified["summary"]["accepted_changes"], 2)
        self.assertEqual(sum(r["verified_outcome"] == "ACCEPTED_MERGED_CHANGE_ONLY"
                             for r in verified["records"]), 2)
        self.assertIn("Accepted source-verified changes:** 2", portfolio.render_joined(verified))
        self.assertTrue(all(r["product_benefit"] == "NOT_MEASURED"
                            for r in verified["records"]
                            if r["verified_outcome"] == "ACCEPTED_MERGED_CHANGE_ONLY"))
        self.assertEqual(len({r["url"] for r in verified["records"]}), 43)

    def test_joined_view_rejects_stale_tampered_duplicate_or_unverified_acceptance(self):
        report = self.full_portfolio_report()
        accepted = self.accepted_export(report)
        for tamper in (lambda x: x.update(source_sha256="0" * 64),
                       lambda x: x.update(portfolio_cohort_sha256="0" * 64),
                       lambda x: x.update(observed_at="2020-01-01T00:00:00+00:00"),
                       lambda x: x.update(accepted_count=3),
                       lambda x: x["accepted"][0].update(benefit_claim="DEPLOYED"),
                       lambda x: x["accepted"].append(copy.deepcopy(x["accepted"][0])),
                       lambda x: x.update(organization_metric_claimed=True)):
            altered = copy.deepcopy(accepted)
            tamper(altered)
            with self.subTest(tamper=tamper):
                with self.assertRaises(ValueError):
                    portfolio.joined_view(report, altered)
        wrong_state = copy.deepcopy(report)
        next(r for r in wrong_state["records"]
             if r["url"] == accepted["accepted"][0]["external_pr_url"])["outcome"] = "open"
        with self.assertRaisesRegex(ValueError, "contradicts"):
            portfolio.joined_view(wrong_state, accepted)

    def test_new_reviewed_publication_receipt_is_discovered_without_watchlist_change(self):
        url = "https://github.com/example-co/new-harness/pull/7"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "2026-11-13.json"
            case = {"id": "new-harness-test", "repository": "example-co/new-harness",
                    "public_fork": "opensiro-contributions/new-harness",
                    "pr_url": url, "head_sha": "a" * 40, "pr_commits": 1}
            packet = {"schema_version": 1, "observed_at": "2026-11-13",
                      "authenticated_actor": "xLagerFeuer", "cases": [case]}
            path.write_text(json.dumps(packet))
            with patch.object(portfolio, "PUBLICATION_READBACKS", Path(directory)):
                cohort = portfolio.cohort()
                self.assertEqual(len(cohort), 44)
                self.assertEqual(next(r["groups"] for r in cohort if r["url"] == url),
                                 ["published"])
                self.assertEqual(sum("watchlist" in r["groups"] for r in cohort), 36)
                case["repository"] = "different/co"
                path.write_text(json.dumps(packet))
                with self.assertRaisesRegex(ValueError, "mismatch"):
                    portfolio.cohort()

    def test_frozen_source_union_exact_size_and_identity(self):
        entries = portfolio.cohort()
        self.assertEqual(len(entries), 43)
        self.assertEqual(sum("watchlist" in row["groups"] for row in entries), 36)
        self.assertEqual(len({row["url"] for row in entries}), 43)
        self.assertEqual([row["groups"] for row in entries if row["url"] ==
                         "https://github.com/witt3rd/oh-my-hermes/pull/28"],
                         [["watchlist"]])
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
        self.assertEqual(len(report["cohort_sha256"]), 64)
        flipped = [dict(row, outcome="merged") for row in report["records"]]
        self.assertEqual(report["cohort_sha256"], portfolio.cohort_fingerprint(flipped))
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

    def test_tampered_cohort_fingerprint_fails_closed(self):
        report = portfolio.observe(FakeAPI({1: payload(1)}), [entry(1)])
        report["records"][0]["groups"] = ["casebook"]
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            portfolio.summarize(report)

    def test_report_writes_one_identical_local_artifact_only_after_success(self):
        report = portfolio.observe(FakeAPI({1: payload(1)}), [entry(1)],
                                   observed_at="2026-11-07T12:00:00Z")
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "observation.json"
            argv = ["portfolio_reconcile.py", "--report", "--output-json", str(target)]
            with patch.object(sys, "argv", argv), patch.object(
                    portfolio.pr_maintenance_watch, "Github"), patch.object(
                    portfolio, "observe", return_value=report) as observer, patch(
                    "builtins.print"):
                portfolio.main()
            observer.assert_called_once()
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), report)

            target.unlink()
            with patch.object(sys, "argv", argv), patch.object(
                    portfolio.pr_maintenance_watch, "Github"), patch.object(
                    portfolio, "observe", side_effect=ValueError("source unavailable")):
                with self.assertRaisesRegex(ValueError, "source unavailable"):
                    portfolio.main()
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
