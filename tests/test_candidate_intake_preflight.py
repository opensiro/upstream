"""Deterministic negative and positive checks for GET-only candidate intake."""
import base64
from io import StringIO
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "scripts"))
from candidate_intake_preflight import IntakeError, inspect_candidate, main
from rest_fork_port import StageBlocked

SOURCE = "outside/example"
PREFIX = "/repos/" + SOURCE
SHA = "c" * 40


def content(text):
    data = text.encode("utf-8")
    return {"type": "file", "encoding": "base64",
            "content": base64.b64encode(data).decode(), "size": len(data)}


class FakeGet:
    def __init__(self):
        self.calls = []
        self.responses = {
            PREFIX: (200, {"full_name": SOURCE, "private": False, "archived": False,
                           "disabled": False, "default_branch": "main", "license": None}),
            PREFIX + "/branches/main": (200, {"commit": {"sha": SHA}}),
            PREFIX + "/contents?ref=" + SHA: (200, [
                {"name": "LICENSE", "type": "file"},
                {"name": "CONTRIBUTING.md", "type": "file"},
            ]),
            PREFIX + "/contents/LICENSE?ref=" + SHA: (200, content("MIT License\nPermission is hereby granted")),
            PREFIX + "/contents/CONTRIBUTING.md?ref=" + SHA: (
                200, content("DCO Signed-off-by; file an issue before a PR. "
                             "Use a branch, run CI checks before merging; "
                             "before submitting a draft PR read the guidelines.")),
            PREFIX + "/issues?state=all&per_page=100&page=1": (200, []),
            PREFIX + "/pulls?state=all&per_page=100&page=1": (200, []),
        }

    def __call__(self, path):
        self.calls.append(path)
        if not path.startswith(PREFIX):
            raise AssertionError("Unexpected nonrepository GET path")
        return self.responses.get(path, (404, {}))


class CandidateIntakeTests(unittest.TestCase):
    def setUp(self):
        self.get = FakeGet()

    def inspect(self, **kwargs):
        return inspect_candidate(source=SOURCE, get=self.get, **kwargs)

    def test_actual_license_text_required_even_when_spdx_metadata_missing(self):
        result = self.inspect()
        self.assertEqual(result["status"], "LICENSE_REVIEW_REQUIRED")
        self.assertEqual(result["license"]["verdict"], "LICENSE_TEXT_PRESENT_REVIEW_REQUIRED")
        self.assertEqual(result["license"]["spdx_metadata"], None)
        self.assertEqual(len(result["license"]["sha256"]), 64)
        self.assertEqual(result["source_sha"], SHA)
        self.assertEqual(result["authorization"], "READ_ONLY_NO_WRITES")
        self.assertIn("MERGE_GATE_MENTIONED", result["contributor_policy"]["hints"])
        self.assertIn("DRAFT_PR_GATE_MENTIONED", result["contributor_policy"]["hints"])
        self.assertIn("DCO_SIGNOFF_MENTIONED", result["contributor_policy"]["hints"])
        self.assertFalse(any("POST" in path for path in self.get.calls))

    def test_named_dual_license_files_are_both_read_at_pinned_source(self):
        self.get.responses[PREFIX + "/contents?ref=" + SHA] = (200, [
            {"name": "LICENSE-APACHE", "type": "file"},
            {"name": "LICENSE-MIT", "type": "file"},
        ])
        self.get.responses[PREFIX + "/contents/LICENSE-APACHE?ref=" + SHA] = (
            200, content("Apache License Version 2.0"))
        self.get.responses[PREFIX + "/contents/LICENSE-MIT?ref=" + SHA] = (
            200, content("MIT License permission is hereby granted"))
        result = self.inspect()
        self.assertEqual(result["status"], "LICENSE_REVIEW_REQUIRED")
        self.assertEqual([file["path"] for file in result["license"]["files"]],
                         ["LICENSE-APACHE", "LICENSE-MIT"])
        self.assertEqual(result["license"]["path"], "LICENSE-APACHE")
        self.assertTrue(all(len(file["sha256"]) == 64 for file in result["license"]["files"]))
        self.assertIn("LICENSE-MIT", result["license"]["other_root_license_candidates"])
        self.assertIn(PREFIX + "/contents/LICENSE-APACHE?ref=" + SHA, self.get.calls)
        self.assertIn(PREFIX + "/contents/LICENSE-MIT?ref=" + SHA, self.get.calls)

    def test_missing_second_license_text_fails_closed(self):
        self.get.responses[PREFIX + "/contents?ref=" + SHA] = (200, [
            {"name": "LICENSE-APACHE", "type": "file"},
            {"name": "LICENSE-MIT", "type": "file"},
        ])
        self.get.responses[PREFIX + "/contents/LICENSE-APACHE?ref=" + SHA] = (
            200, content("Apache License"))
        with self.assertRaises(IntakeError):
            self.inspect()

    def test_no_root_license_blocks_before_policy_and_overlap(self):
        self.get.responses[PREFIX + "/contents?ref=" + SHA] = (
            200, [{"name": "CONTRIBUTING.md", "type": "file"}])
        result = self.inspect(topic="stale edit ledger")
        self.assertEqual(result["status"], "LICENSE_BLOCKED")
        self.assertEqual(result["license"]["verdict"], "LICENSE_NOT_FOUND_AT_ROOT")
        self.assertEqual(result["overlap"]["status"], "NOT_SEARCHED")
        self.assertNotIn(PREFIX + "/contents/CONTRIBUTING.md?ref=" + SHA, self.get.calls)
        self.assertNotIn(PREFIX + "/issues?state=all&per_page=100&page=1", self.get.calls)

    def test_license_spdx_metadata_is_not_a_license_text_substitute(self):
        self.get.responses[PREFIX][1]["license"] = {"spdx_id": "MIT"}
        self.get.responses[PREFIX + "/contents?ref=" + SHA] = (200, [])
        self.assertEqual(self.inspect()["status"], "LICENSE_BLOCKED")

    def test_denial_rate_limit_and_missing_license_content_are_unverified(self):
        path = PREFIX + "/contents/LICENSE?ref=" + SHA
        for status in (403, 429, 404, 500):
            with self.subTest(status=status):
                self.get.responses[path] = (status, {})
                with self.assertRaises(IntakeError):
                    self.inspect()

    def test_invalid_base64_size_and_utf8_fail_closed(self):
        path = PREFIX + "/contents/LICENSE?ref=" + SHA
        bad = [
            {"type": "file", "encoding": "base64", "content": "!!!", "size": 3},
            {"type": "file", "encoding": "base64", "content": "YQ==", "size": 2},
            {"type": "file", "encoding": "base64", "content": "/w==", "size": 1},
            {"type": "file", "encoding": "base64", "content": "YQ==", "size": 300_000},
        ]
        for item in bad:
            with self.subTest(content=item):
                self.get.responses[path] = (200, item)
                with self.assertRaises(IntakeError):
                    self.inspect()

    def test_malformed_api_shape_sha_and_identity_fail_closed(self):
        self.get.responses[PREFIX + "/contents?ref=" + SHA] = (200, {})
        with self.assertRaises(IntakeError):
            self.inspect()
        self.get = FakeGet()
        self.get.responses[PREFIX + "/branches/main"] = (
            200, {"commit": {"sha": "unknown"}})
        with self.assertRaises(IntakeError):
            self.inspect()
        self.get = FakeGet()
        self.get.responses[PREFIX][1]["full_name"] = "outside/elsewhere"
        with self.assertRaises(IntakeError):
            self.inspect()

    def test_topic_overlap_is_hint_and_prs_are_not_issues(self):
        self.get.responses[PREFIX + "/issues?state=all&per_page=100&page=1"] = (200, [
            {"number": 7, "title": "Fix stale edit ledger", "html_url": "https://example/7"},
            {"number": 8, "title": "Stale edit ledger", "pull_request": {},
             "html_url": "https://example/8"},
        ])
        self.get.responses[PREFIX + "/pulls?state=all&per_page=100&page=1"] = (200, [
            {"number": 8, "title": "Repair stale edit ledger", "html_url": "https://example/8"},
        ])
        result = self.inspect(topic="stale edit ledger")
        self.assertEqual(result["overlap"]["status"],
                         "TITLE_BODY_HEURISTIC_ONLY_NOT_PROOF_OF_ABSENCE")
        self.assertEqual([i["number"] for i in result["overlap"]["issues"]], [7])
        self.assertEqual([i["number"] for i in result["overlap"]["pull_requests"]], [8])

    def test_full_first_page_traverses_pagination_and_never_clears_overlap(self):
        self.get.responses[PREFIX + "/pulls?state=all&per_page=100&page=1"] = (
            200, [{"number": i, "title": "Another unrelated task"} for i in range(100)])
        self.get.responses[PREFIX + "/pulls?state=all&per_page=100&page=2"] = (200, [])
        result = self.inspect(topic="stale edit ledger")
        self.assertEqual(result["overlap"]["status"],
                         "TITLE_BODY_HEURISTIC_ONLY_NOT_PROOF_OF_ABSENCE")
        self.assertEqual(result["overlap"]["pull_requests_pages"], 2)
        self.assertIn(PREFIX + "/pulls?state=all&per_page=100&page=2", self.get.calls)

    def test_nested_github_policy_file_and_line_evidence(self):
        self.get.responses[PREFIX + "/contents?ref=" + SHA][1].append(
            {"name": ".github", "type": "dir"})
        self.get.responses[PREFIX + "/contents/.github?ref=" + SHA] = (200, [
            {"name": "CONTRIBUTING.md", "type": "file"},
            {"name": "PULL_REQUEST_TEMPLATE", "type": "dir"},
        ])
        self.get.responses[PREFIX + "/contents/.github/CONTRIBUTING.md?ref=" + SHA] = (
            200, content("Review contributor guidelines\nAssign an issue before opening a pull request\n"
                         "Use a signed-off commit before submitting a draft PR"))
        self.get.responses[PREFIX + "/contents/.github/PULL_REQUEST_TEMPLATE?ref=" + SHA] = (
            200, [{"name": "bugfix.md", "type": "file"}])
        self.get.responses[PREFIX + "/contents/.github/PULL_REQUEST_TEMPLATE/bugfix.md?ref=" + SHA] = (
            200, content("Before merging, run CI tests"))
        result = self.inspect()
        paths = [x["path"] for x in result["contributor_policy"]["paths"]]
        self.assertIn(".github/CONTRIBUTING.md", paths)
        self.assertIn(".github/PULL_REQUEST_TEMPLATE/bugfix.md", paths)
        self.assertIn({"path": ".github/CONTRIBUTING.md", "line": 2,
                       "stage": "BEFORE_IMPLEMENTATION", "code": "ISSUE_WORKFLOW_MENTIONED",
                       "excerpt": "Assign an issue before opening a pull request"},
                      result["contributor_policy"]["evidence"])
        self.assertEqual(result["gates"]["BEFORE_DRAFT"]["status"], "NOT_CLEARED")
        self.assertIn("UPSTREAM_MAINTAINER_MERGE_RESERVED",
                      result["gates"]["BEFORE_MERGE"]["reasons"])

    def test_closed_issue_and_pr_overlap_across_pages_including_body(self):
        first_page = [{"number": i, "title": "Unrelated", "body": None,
                       "state": "closed"} for i in range(100)]
        self.get.responses[PREFIX + "/issues?state=all&per_page=100&page=1"] = (
            200, first_page)
        self.get.responses[PREFIX + "/issues?state=all&per_page=100&page=2"] = (
            200, [{"number": 101, "title": "Something else",
                   "body": "Stale edit ledger causes lost updates", "state": "closed"}])
        self.get.responses[PREFIX + "/pulls?state=all&per_page=100&page=1"] = (
            200, [{"number": 102, "title": "Fix stale edit ledger", "state": "closed"}])
        result = self.inspect(topic="stale edit ledger")
        self.assertEqual(result["overlap"]["status"],
                         "TITLE_BODY_HEURISTIC_ONLY_NOT_PROOF_OF_ABSENCE")
        self.assertEqual(result["overlap"]["issues"][0]["state"], "closed")
        self.assertEqual(result["overlap"]["issues"][0]["matched_in"], "body")
        self.assertEqual(result["overlap"]["pull_requests"][0]["state"], "closed")
        self.assertIn("POTENTIAL_DUPLICATE_REVIEW_REQUIRED",
                      result["gates"]["BEFORE_IMPLEMENTATION"]["reasons"])

    def test_potential_duplicate_token_separator_and_partial_topic(self):
        self.get.responses[PREFIX + "/pulls?state=all&per_page=100&page=1"] = (
            200, [{"number": 1, "title": "preflight batch_edit before changing files",
                   "body": "Avoid partial file writes", "state": "open"}])
        result = self.inspect(topic="batch edit partial mutation")
        self.assertEqual(result["overlap"]["pull_requests"][0]["number"], 1)
        self.assertIn("POTENTIAL_DUPLICATE_REVIEW_REQUIRED",
                      result["gates"]["BEFORE_IMPLEMENTATION"]["reasons"])

    def test_page_budget_discloses_incomplete_inventory(self):
        for page in range(1, 31):
            self.get.responses[PREFIX + f"/issues?state=all&per_page=100&page={page}"] = (
                200, [{"number": (page - 1) * 100 + i, "title": "other"}
                      for i in range(100)])
        result = self.inspect(topic="stale edit ledger")
        self.assertEqual(result["overlap"]["status"], "INVENTORY_INCOMPLETE")
        self.assertEqual(result["overlap"]["issue_count_examined"], 3000)
        self.assertIn("DUPLICATE_INVENTORY_INCOMPLETE",
                      result["gates"]["BEFORE_IMPLEMENTATION"]["reasons"])

    def test_pagination_denial_never_reports_complete(self):
        self.get.responses[PREFIX + "/pulls?state=all&per_page=100&page=1"] = (
            200, [{"title": "other"} for _ in range(100)])
        self.get.responses[PREFIX + "/pulls?state=all&per_page=100&page=2"] = (403, {})
        with self.assertRaises(IntakeError):
            self.inspect(topic="stale edit ledger")

    def test_sha_pins_all_content_reads(self):
        self.inspect()
        content_reads = [path for path in self.get.calls if "/contents" in path]
        self.assertTrue(content_reads)
        self.assertTrue(all(path.endswith("?ref=" + SHA) for path in content_reads))

    def test_malformed_nested_directory_is_insufficient(self):
        self.get.responses[PREFIX + "/contents?ref=" + SHA][1].append(
            {"name": ".github", "type": "dir"})
        self.get.responses[PREFIX + "/contents/.github?ref=" + SHA] = (
            200, [{"name": "CONTRIBUTING.md", "type": "symlink"}])
        with self.assertRaises(IntakeError):
            self.inspect()

    def test_invalid_inputs_rejected_before_network(self):
        for data in ({"source": "outside/../../secret"},
                     {"source": "outside/example", "branch": "../main"},
                     {"source": "outside/example", "topic": "?test&state=open"}):
            with self.subTest(data=data), self.assertRaises((IntakeError, StageBlocked, ValueError)):
                inspect_candidate(get=self.get, **data)
        self.assertEqual(self.get.calls, [])

    def test_cli_json_status_and_nonzero_for_blocked_or_failed(self):
        with patch("sys.stdout", new_callable=StringIO) as output:
            self.assertEqual(main(["--source", SOURCE], get=self.get), 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "LICENSE_REVIEW_REQUIRED")
        self.get.responses[PREFIX + "/contents?ref=" + SHA] = (200, [])
        with patch("sys.stdout", new_callable=StringIO) as output:
            self.assertEqual(main(["--source", SOURCE], get=self.get), 2)
        self.assertEqual(json.loads(output.getvalue())["status"], "LICENSE_BLOCKED")
        self.get.responses[PREFIX] = (403, {})
        with patch("sys.stdout", new_callable=StringIO) as output:
            self.assertEqual(main(["--source", SOURCE], get=self.get), 2)
        self.assertEqual(json.loads(output.getvalue())["status"], "INSUFFICIENT_EVIDENCE")

    def test_cli_has_no_write_mode(self):
        process = subprocess.run(
            [sys.executable, str(BASE / "scripts" / "candidate_intake_preflight.py"),
             "--source", SOURCE, "--execute"], capture_output=True,
            text=True, check=False)
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("unrecognized arguments", process.stderr)


if __name__ == "__main__":
    unittest.main()
