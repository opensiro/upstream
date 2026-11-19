"""Deterministic, network-free checks for Index-first roadmap selection."""
import base64
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from aggregate import APIError
from roadmap_select import hypotheses, load_index, shortlist, rank, live_screen, markdown

SHA = "b" * 40
ORIGINAL = "sample/orchestra"
FORK = "opensiro-contributions/orchestra"
WHEN = datetime(2026, 11, 18, tzinfo=timezone.utc)
RANKINGS = """# Index accepted rows
| Rank | Harness | Period | Agent-owned | Metasystem A | C | P | ? | Vector |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | <a id="orchestra"></a>[Orchestra](assessments/or/orchestra.md) ([source](https://github.com/sample/orchestra)) | 2026-Q4 | 1/6 | 0/5 | 1 | 0 | 0 | `A C — — — —` |
| 4 | <a id="reviewer"></a>[Reviewer](assessments/re/reviewer.md) ([source](https://github.com/sample/reviewer)) | 2026-Q4 | 3/6 | 2/5 | 0 | 1 | 0 | `A A A — — P` |
"""
CATALOG = """catalog_position|harness_id|project_name|repository|repository_created_at|source_membership|review_ref|pinned_at
1|orchestra|Orchestra|https://github.com/sample/orchestra|2026-10-01T00:00:00Z|adapted-source|aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa|2026-11-18
2|reviewer|Reviewer|https://github.com/sample/reviewer|2026-10-01T00:00:00Z|adapted-source|cccccccccccccccccccccccccccccccccccccccc|2026-11-16
"""
STARS = {"schema_version": 1, "records": [
    {"harness_id": "orchestra", "stars": 100, "fetch_status": "ok"},
    {"harness_id": "reviewer", "stars": 10000, "fetch_status": "ok"}]}


class FakeGitHub:
    def __init__(self):
        self.routes = {}
        self.reads = []

    def get(self, path):
        self.reads.append(path)
        if path not in self.routes:
            raise APIError(404, "missing route " + path)
        value = self.routes[path]
        if isinstance(value, Exception):
            raise value
        return value

    def add_original(self, original=ORIGINAL, license_id="MIT"):
        self.routes["/repos/" + original] = {
            "full_name": original, "license": {"spdx_id": license_id},
            "pushed_at": "2026-11-18T12:00:00Z", "archived": False,
            "disabled": False, "has_issues": True, "stargazers_count": 150}
        self.routes["/repos/" + original +
                    "/issues?state=open&per_page=100&sort=updated&direction=desc"] = [
            {"title": "Shared browser agents race over resource leases",
             "html_url": "https://github.com/" + original + "/issues/8",
             "updated_at": "2026-11-16T00:00:00Z"},
            {"title": "Feature request unrelated to S3",
             "html_url": "https://github.com/" + original + "/issues/7"},
            {"title": "PR in issue sample", "pull_request": {"url": "..."},
             "html_url": "https://github.com/" + original + "/pull/9"}]
        return self


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        d = Path(self.temp.name)
        (d / "data").mkdir()
        (d / "RANKINGS.md").write_text(RANKINGS)
        (d / "data" / "catalog.psv").write_text(CATALOG)
        (d / "data" / "github-stars.json").write_text(json.dumps(STARS))
        self.path = d

    def tearDown(self):
        self.temp.cleanup()

    def load(self):
        return load_index(FakeGitHub(), self.path, SHA)[1]

    def test_only_included_index_rankings_and_exact_pin(self):
        records = self.load()
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["vector"], ["A", "C", "—", "—", "—", "—"])
        self.assertEqual(records[0]["review_ref"], "a" * 40)
        with self.assertRaises(ValueError):
            load_index(FakeGitHub(), self.path)
        with self.assertRaises(ValueError):
            load_index(FakeGitHub(), self.path, "main")

    def test_index_catalog_mismatch_is_fatal(self):
        p = self.path / "data/catalog.psv"
        p.write_text(p.read_text().replace("sample/orchestra", "another/orchestra"))
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            self.load()

    def test_hypothesis_not_from_missing_grade_alone(self):
        self.assertEqual(hypotheses(["A", "—", "—", "—", "—", "—"]), {"s2": 1})
        self.assertIn("s3", hypotheses(["A", "C", "—", "—", "—", "—"]))
        self.assertNotIn("s3", hypotheses(["A", "C", "C", "—", "—", "—"]))
        self.assertIn("s3star", hypotheses(["A", "C", "C", "—", "—", "—"]))
        self.assertIn("s4", hypotheses(["A", "A", "A", "—", "—", "P"]))

    def test_source_shortlist_covers_s5_and_supports_s1_s2_explicit_focus(self):
        records = self.load()
        picked = shortlist(records, "all", 10)
        self.assertEqual(len(picked), 2)
        self.assertIn("s5", next(x for x in picked if x["id"] == "reviewer")["hypotheses"])
        self.assertTrue(all(x["primary_focus_is_hint_only"] and not x["p0_selected"]
                            for x in picked))
        self.assertTrue(all(x["required_repository_wide_screen"] ==
                            ["S1", "S2", "S3", "S3*", "S4", "S5"] for x in picked))
        self.assertIn("s2", shortlist([dict(picked[0], vector=["A", "—", "—", "—", "—", "—"])], "s2", 10)[0]["hypotheses"])
        self.assertEqual(shortlist(records, "s1", 10)[0]["hypotheses"]["s1"], 1)
        self.assertEqual(len(shortlist(records, "s3", 10)), 1)

    def test_explicit_focus_does_not_make_missing_function_automatic_p0(self):
        records = self.load()
        s1 = shortlist(records, "s1", 5)
        self.assertEqual(len(s1), 2)
        for row in s1:
            self.assertEqual(row["hypotheses"], {"s1": 1})
            self.assertFalse(row["p0_selected"])
        s2 = shortlist(records, "s2", 5)
        self.assertEqual(len(s2), 0)  # historical S2=C/A in fixture; no gap hypothesis
        self.assertEqual(hypotheses(["A", "C", "C", "C", "C", "C"]), {})

    def test_live_issue_title_is_lead_not_closure(self):
        client = FakeGitHub().add_original()
        row = shortlist(self.load(), "s3", 5)[0]
        live = live_screen(client, row, WHEN)
        self.assertEqual(live["license"], "MIT")
        self.assertEqual(live["license_gate"], "PERMISSIVE_REVIEW_FORMALITIES")
        self.assertEqual(live["issue_evidence"][0]["url"], "https://github.com/sample/orchestra/issues/8")
        self.assertEqual(live["owner_control"], "UNKNOWN")
        self.assertIsNone(live["matched_fork"])
        self.assertEqual(live["existing_roadmap_cases"], None)
        self.assertNotIn("C_PROVED", live["disposition"])

    def test_pause_fork_not_promoted(self):
        client = FakeGitHub().add_original()
        client.routes["/repos/" + FORK] = {
            "fork": True, "parent": {"full_name": ORIGINAL}}
        client.routes["/repos/" + FORK + "/git/ref/heads/opensiro/meta"] = {
            "object": {"sha": SHA}}
        state = {"schema_version": 1, "original_repository": ORIGINAL,
                 "working_fork": FORK, "owner_control": "PAUSE",
                 "attention": "DORMANT"}
        client.routes["/repos/" + FORK + "/contents/.opensiro/state.json?ref=" + SHA] = {
            "type": "file", "encoding": "base64",
            "content": base64.b64encode(json.dumps(state).encode()).decode()}
        client.routes["/repos/" + FORK + "/contents/.opensiro/issues?ref=" + SHA] = [
            {"type": "dir", "name": "historic-case"}]
        row = shortlist(self.load(), "s3", 5)[0]
        live = live_screen(client, row, WHEN)
        self.assertEqual(live["disposition"], "OWNER_PAUSED")
        self.assertEqual(live["existing_roadmap_cases"], 1)

    def test_license_and_archival_gates(self):
        row = shortlist(self.load(), "s3", 5)[0]
        for license_id, expected in (
            ("NOASSERTION", "RIGHTS_UNVERIFIED"),
            ("MIT", "ELIGIBLE_FOR_RESEARCH")):
            client = FakeGitHub().add_original(license_id=license_id)
            self.assertEqual(live_screen(client, row, WHEN)["disposition"], expected)
        client = FakeGitHub().add_original()
        client.routes["/repos/" + ORIGINAL]["archived"] = True
        self.assertEqual(live_screen(client, row, WHEN)["disposition"], "EXCLUDE_INACTIVE")

    def test_offline_rank_and_markdown_are_explicitly_unverified(self):
        report = rank(FakeGitHub(), no_live=True, index_dir=self.path,
                      index_sha=SHA, observed_at=WHEN)
        self.assertEqual(report["accepted_included_rows"], 2)
        self.assertTrue(all(x["disposition"] == "INDEX_ONLY_NOT_SOURCE_VERIFIED"
                            for x in report["candidates"]))
        self.assertIn("research leads", markdown(report).lower())

    def test_live_network_failure_not_a_candidate(self):
        client = FakeGitHub()
        report = rank(client, no_live=False, focus="s3", probe=1, limit=1,
                      index_dir=self.path, index_sha=SHA, observed_at=WHEN)
        self.assertFalse(report["scan_complete"])
        self.assertTrue(report["unknowns"])
        self.assertEqual(report["candidates"], [])


if __name__ == "__main__":
    unittest.main()
