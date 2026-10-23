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
            PREFIX + "/contents?ref=main": (200, [
                {"name": "LICENSE", "type": "file"},
                {"name": "CONTRIBUTING.md", "type": "file"},
            ]),
            PREFIX + "/contents/LICENSE?ref=main": (200, content("MIT License\nPermission is hereby granted")),
            PREFIX + "/contents/CONTRIBUTING.md?ref=main": (
                200, content("DCO Signed-off-by; file an issue before a PR. "
                             "Use a branch, run CI checks before merging; "
                             "before submitting a draft PR read the guidelines.")),
            PREFIX + "/issues?state=all&per_page=100": (200, []),
            PREFIX + "/pulls?state=open&per_page=100": (200, []),
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

    def test_no_root_license_blocks_before_policy_and_overlap(self):
        self.get.responses[PREFIX + "/contents?ref=main"] = (
            200, [{"name": "CONTRIBUTING.md", "type": "file"}])
        result = self.inspect(topic="stale edit ledger")
        self.assertEqual(result["status"], "LICENSE_BLOCKED")
        self.assertEqual(result["license"]["verdict"], "LICENSE_NOT_FOUND_AT_ROOT")
        self.assertEqual(result["overlap"]["status"], "NOT_SEARCHED")
        self.assertNotIn(PREFIX + "/contents/CONTRIBUTING.md?ref=main", self.get.calls)
        self.assertNotIn(PREFIX + "/issues?state=all&per_page=100", self.get.calls)

    def test_license_spdx_metadata_is_not_a_license_text_substitute(self):
        self.get.responses[PREFIX][1]["license"] = {"spdx_id": "MIT"}
        self.get.responses[PREFIX + "/contents?ref=main"] = (200, [])
        self.assertEqual(self.inspect()["status"], "LICENSE_BLOCKED")

    def test_denial_rate_limit_and_missing_license_content_are_unverified(self):
        path = PREFIX + "/contents/LICENSE?ref=main"
        for status in (403, 429, 404, 500):
            with self.subTest(status=status):
                self.get.responses[path] = (status, {})
                with self.assertRaises(IntakeError):
                    self.inspect()

    def test_invalid_base64_size_and_utf8_fail_closed(self):
        path = PREFIX + "/contents/LICENSE?ref=main"
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
        self.get.responses[PREFIX + "/contents?ref=main"] = (200, {})
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
        self.get.responses[PREFIX + "/issues?state=all&per_page=100"] = (200, [
            {"number": 7, "title": "Fix stale edit ledger", "html_url": "https://example/7"},
            {"number": 8, "title": "Stale edit ledger", "pull_request": {},
             "html_url": "https://example/8"},
        ])
        self.get.responses[PREFIX + "/pulls?state=open&per_page=100"] = (200, [
            {"number": 8, "title": "Repair stale edit ledger", "html_url": "https://example/8"},
        ])
        result = self.inspect(topic="stale edit ledger")
        self.assertEqual(result["overlap"]["status"],
                         "TITLE_HEURISTIC_ONLY_NOT_PROOF_OF_ABSENCE")
        self.assertEqual([i["number"] for i in result["overlap"]["issues"]], [7])
        self.assertEqual([i["number"] for i in result["overlap"]["pull_requests"]], [8])

    def test_full_first_page_requires_pagination_and_never_clears_overlap(self):
        self.get.responses[PREFIX + "/pulls?state=open&per_page=100"] = (
            200, [{"number": i, "title": "Another unrelated task"} for i in range(100)])
        result = self.inspect(topic="stale edit ledger")
        self.assertEqual(result["overlap"]["status"], "PAGINATION_REQUIRED")

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
        self.get.responses[PREFIX + "/contents?ref=main"] = (200, [])
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
