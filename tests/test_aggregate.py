"""Offline tests for the read-only fork-local portfolio aggregation.

All API reads are fake. No GitHub access, writes, permanent jobs or credentials.
"""
import base64
import csv
import io
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from aggregate import APIError, aggregate, csv_output, markdown, pr_observation, transitions  # noqa: E402

TIME = "2026-11-16T00:00:00Z"


def file_blob(value, sha="a" * 40):
    return {"type": "file", "sha": sha, "encoding": "base64",
            "content": base64.b64encode(json.dumps(value).encode()).decode()}


class FakeGitHub:
    def __init__(self):
        self.routes = {}
        self.seen = []

    def get(self, path):
        self.seen.append(path)
        value = self.routes.get(path)
        if value is None:
            raise APIError(404, f"missing test route: {path}")
        if isinstance(value, Exception):
            raise value
        return value

    def add(self, fork="opensiro-contributions/Citadel", original="SethGammon/Citadel",
            attention="DORMANT", control="PAUSE", identifiers=("citadel-claims",),
            prs=("https://github.com/SethGammon/Citadel/pull/366",),
            merged_at="2026-10-25T21:26:14Z", pr_state="closed"):
        root = f"/repos/{fork}"
        self.routes[root] = {"fork": True, "parent": {"full_name": original}}
        self.routes[root + "/git/ref/heads/opensiro/meta"] = {"object": {"sha": "b" * 40}}
        self.routes[root + "/contents/.opensiro/state.json?ref=opensiro%2Fmeta"] = file_blob(
            {"schema_version": 1, "original_repository": original,
             "working_fork": fork, "attention": attention, "owner_control": control,
             "last_event_id": None})
        entries = []
        for identifier in identifiers:
            path = f".opensiro/contributions/{identifier}.json"
            entries.append({"type": "file", "name": identifier + ".json", "path": path})
            self.routes[root + "/contents/" + path + "?ref=opensiro%2Fmeta"] = file_blob(
                {"schema_version": 1, "id": identifier, "original_repository": original,
                 "work_state": "DELIVERED", "external_prs": list(prs), "title": "Fix"})
        self.routes[root + "/contents/.opensiro/contributions?ref=opensiro%2Fmeta"] = entries
        for pr in prs:
            match = pr.split("/")
            self.routes[f"/repos/{match[3]}/{match[4]}/pulls/{match[6]}"] = {
                "state": pr_state, "merged_at": merged_at, "draft": False,
                "updated_at": "2026-11-15T12:00:00Z"}
        return self


class AggregatorTests(unittest.TestCase):
    def test_real_metadata_shape_and_verified_external_merge(self):
        client = FakeGitHub().add()
        result = aggregate(client, requested=["opensiro-contributions/Citadel"], observed_at=TIME)
        self.assertEqual(result["summary"]["forks_with_metadata"], 1)
        self.assertEqual(result["summary"]["independent_contributions"], 1)
        self.assertEqual(result["summary"]["pr_statuses"]["MERGED"], 1)
        self.assertEqual(result["forks"][0]["meta_head_sha"], "b" * 40)
        self.assertEqual(result["forks"][0]["attention"], "DORMANT")
        self.assertFalse(result["historical_inventory_complete"])
        self.assertFalse(result["coverage"]["portfolio_complete"])
        self.assertEqual(result["coverage"]["errors"], 0)
        self.assertTrue(all(not path.startswith(("/write", "/post")) for path in client.seen))
        self.assertIn("MERGED", markdown(result))
        rows = list(csv.reader(io.StringIO(csv_output(result))))
        self.assertEqual(rows[1][8], "MERGED")

    def test_closed_unmerged_and_open_are_distinct(self):
        client = FakeGitHub().add(merged_at=None)
        report = aggregate(client, requested=["opensiro-contributions/Citadel"], observed_at=TIME)
        self.assertEqual(report["summary"]["pr_statuses"]["CLOSED_UNMERGED"], 1)
        client.add(merged_at=None, pr_state="open")
        report = aggregate(client, requested=["opensiro-contributions/Citadel"], observed_at=TIME)
        self.assertEqual(report["summary"]["pr_statuses"]["OPEN"], 1)

    def test_unknown_pr_on_http_error_does_not_become_closed(self):
        client = FakeGitHub().add()
        client.routes["/repos/SethGammon/Citadel/pulls/366"] = APIError(403, "rate limit")
        report = aggregate(client, requested=["opensiro-contributions/Citadel"], observed_at=TIME)
        self.assertEqual(report["summary"]["pr_statuses"]["UNKNOWN"], 1)
        pr = report["forks"][0]["contributions"][0]["external_prs"][0]
        self.assertEqual(pr["reason"], "GITHUB_HTTP_403")
        self.assertEqual(pr["status"], "UNKNOWN")

    def test_wrong_original_pr_is_unknown_and_not_fetched(self):
        client = FakeGitHub().add(prs=("https://github.com/other/repo/pull/77",))
        report = aggregate(client, requested=["opensiro-contributions/Citadel"], observed_at=TIME)
        pr = report["forks"][0]["contributions"][0]["external_prs"][0]
        self.assertEqual(pr["reason"], "NOT_ORIGINAL_SOURCE_REPOSITORY")
        self.assertNotIn("/repos/other/repo/pulls/77", client.seen)

    def test_multiple_improvements_one_fork_multiple_prs(self):
        client = FakeGitHub().add(identifiers=("claim-lock", "lock-release"),
                                  prs=("https://github.com/SethGammon/Citadel/pull/366",
                                       "https://github.com/SethGammon/Citadel/pull/367"))
        report = aggregate(client, requested=["opensiro-contributions/Citadel"], observed_at=TIME)
        self.assertEqual(report["summary"]["independent_contributions"], 2)
        self.assertEqual(report["summary"]["linked_unique_external_prs"], 2)
        self.assertEqual(client.seen.count("/repos/SethGammon/Citadel/pulls/366"), 1)

    def test_no_meta_is_missing_not_migrated(self):
        client = FakeGitHub()
        client.routes["/repos/opensiro-contributions/NoMeta"] = {
            "fork": True, "parent": {"full_name": "original/NoMeta"}}
        report = aggregate(client, requested=["opensiro-contributions/NoMeta"], observed_at=TIME)
        self.assertEqual(report["coverage"]["missing_meta"], 1)
        self.assertEqual(report["summary"]["forks_with_metadata"], 0)
        self.assertFalse(report["coverage"]["portfolio_complete"])

    def test_mismatched_parent_does_not_contribute(self):
        client = FakeGitHub().add()
        client.routes["/repos/opensiro-contributions/Citadel"]["parent"]["full_name"] = "other/Citadel"
        report = aggregate(client, requested=["opensiro-contributions/Citadel"], observed_at=TIME)
        self.assertEqual(report["coverage"]["errors"], 1)
        self.assertFalse(report["coverage"]["scan_complete"])
        self.assertEqual(report["summary"]["forks_with_metadata"], 0)

    def test_unexpected_record_failure_is_not_silent(self):
        client = FakeGitHub().add()
        entry = client.routes["/repos/opensiro-contributions/Citadel/contents/.opensiro/contributions/citadel-claims.json?ref=opensiro%2Fmeta"]
        item = json.loads(base64.b64decode(entry["content"]))
        item["work_state"] = "AUTOMATICALLY_ADOPTED"
        client.routes["/repos/opensiro-contributions/Citadel/contents/.opensiro/contributions/citadel-claims.json?ref=opensiro%2Fmeta"] = file_blob(item)
        report = aggregate(client, requested=["opensiro-contributions/Citadel"], observed_at=TIME)
        self.assertEqual(report["coverage"]["errors"], 1)
        self.assertEqual(report["summary"]["forks_with_metadata"], 0)

    def test_only_active_filters_dormant_before_pr_reads(self):
        client = FakeGitHub().add()
        report = aggregate(client, requested=["opensiro-contributions/Citadel"],
                           only_active=True, observed_at=TIME)
        self.assertEqual(report["coverage"]["filtered_by_attention"], 1)
        self.assertEqual(report["summary"]["linked_unique_external_prs"], 0)
        self.assertNotIn("/repos/SethGammon/Citadel/pulls/366", client.seen)

    def test_no_pr_readback_produces_unknown(self):
        client = FakeGitHub().add()
        report = aggregate(client, requested=["opensiro-contributions/Citadel"],
                           live_prs=False, observed_at=TIME)
        self.assertEqual(report["summary"]["pr_statuses"]["UNKNOWN"], 1)
        self.assertNotIn("/repos/SethGammon/Citadel/pulls/366", client.seen)

    def test_compare_reports_lifecycle_transition_only_when_known(self):
        client = FakeGitHub().add()
        report = aggregate(client, requested=["opensiro-contributions/Citadel"], observed_at=TIME)
        old = json.loads(json.dumps(report))
        old["forks"][0]["contributions"][0]["external_prs"][0]["status"] = "OPEN"
        changes = transitions(report, old)
        self.assertEqual(changes, [{
            "url": "https://github.com/SethGammon/Citadel/pull/366",
            "from": "OPEN", "to": "MERGED"}])
        old["forks"][0]["contributions"][0]["external_prs"][0]["status"] = "UNKNOWN"
        self.assertEqual(transitions(report, old), [])

    def test_reject_repo_outside_org(self):
        with self.assertRaises(ValueError):
            aggregate(FakeGitHub(), requested=["thirdparty/repo"])

    def test_discovery_uses_org_pages_and_warns_about_missing_meta(self):
        client = FakeGitHub().add()
        client.routes["/orgs/opensiro-contributions/repos?per_page=100&page=1&type=all"] = [
            {"full_name": "opensiro-contributions/Citadel"}]
        report = aggregate(client, observed_at=TIME)
        self.assertEqual(report["scope"], "public_organization_repositories")
        self.assertEqual(report["coverage"]["repositories_discovered"], 1)
        self.assertFalse(report["historical_inventory_complete"])


if __name__ == "__main__":
    unittest.main()
