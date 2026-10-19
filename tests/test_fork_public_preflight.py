"""Public GitHub fork preflight tests: only GET, no credentials or forks."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "scripts"))
from fork_public_preflight import inspect_public_fork, ReadOnlyError, main
from rest_fork_port import StageBlocked

SHA = "f" * 40
SOURCE = {"full_name": "outside/example", "private": False, "archived": False,
          "disabled": False, "forking_allowed": True, "default_branch": "main",
          "license": {"spdx_id": "MIT"}}
BRANCH = {"commit": {"sha": SHA}}


class PublicGet:
    def __init__(self):
        self.calls = []
        self.source = dict(SOURCE)
        self.branch = dict(BRANCH)
        self.dest = (404, {})
        self.denied_path = None

    def __call__(self, path):
        self.calls.append(path)
        if self.denied_path and path == self.denied_path:
            return (403, {})
        if path == "/repos/outside/example":
            return (200, self.source)
        if path == "/repos/outside/example/branches/development":
            return (200, self.branch)
        if path == "/repos/outside/example/branches/main":
            return (200, self.branch)
        if path == "/repos/opensiro-contributions/example":
            return self.dest
        return (404, {})


class ReadOnlyForkPreflightTests(unittest.TestCase):
    def setUp(self):
        self.get = PublicGet()

    def run_check(self, **kw):
        args = dict(source="outside/example", fork_name="example",
                    working_branch="development", expected_sha=SHA,
                    expected_license="MIT", all_branches=True, get=self.get)
        args.update(kw)
        return inspect_public_fork(**args)

    def assert_read_only(self):
        self.assertTrue(all(x.startswith("/repos/") for x in self.get.calls))
        self.assertTrue(all(x.startswith("/") for x in self.get.calls))

    def test_all_branches_exact_sha_is_public_only_not_authorized(self):
        o = self.run_check()
        self.assertEqual(o["status"], "PUBLIC_PREFLIGHT_OK_NOT_AUTHORIZED")
        self.assertEqual(o["observed_source_sha"], SHA)
        self.assertEqual(o["observed_destination"], "NOT_PUBLICLY_VISIBLE")
        self.assertEqual(o["fork_create_permission"], "NOT_TESTED_NO_CREDENTIALS")
        self.assertEqual(o["authorization"], "NOT_APPROVED_NO_WRITES")
        self.assert_read_only()

    def test_default_only_cannot_copy_development(self):
        o = self.run_check(all_branches=False)
        self.assertEqual(o["status"], "BLOCKED_PUBLIC_PREFLIGHT")
        self.assertIn("nondefault", " ".join(o["reasons"]))

    def test_unpinned_sha_is_not_executable(self):
        o = self.run_check(expected_sha=None)
        self.assertEqual(o["status"], "BLOCKED_PUBLIC_PREFLIGHT")
        self.assertEqual(o["observed_source_sha"], SHA)
        self.assertIn("not approved/pinned", " ".join(o["reasons"]))

    def test_changed_sha_detected(self):
        o = self.run_check(expected_sha="a" * 40)
        self.assertEqual(o["status"], "BLOCKED_PUBLIC_PREFLIGHT")
        self.assertIn("SHA drift", " ".join(o["reasons"]))

    def test_missing_or_wrong_spdx_blocks(self):
        for value in (None, "Apache-2.0"):
            with self.subTest(license=value):
                self.assertEqual(self.run_check(expected_license=value)["status"],
                                 "BLOCKED_PUBLIC_PREFLIGHT")

    def test_invalid_sha_rejected_before_get(self):
        with self.assertRaises(ReadOnlyError):
            self.run_check(expected_sha="unverified")
        self.assertEqual(self.get.calls, [])

    def test_invalid_source_or_branch_rejected_before_get(self):
        for vals in ({"source": "a/b/other"}, {"working_branch": "../develop"},
                     {"fork_name": "../../evil"}, {"source": "opensiro-contributions/src"}):
            with self.subTest(vals=vals), self.assertRaises(
                    (ReadOnlyError, StageBlocked)):
                self.run_check(**vals)
        self.assertEqual(self.get.calls, [])

    def test_403_is_not_treated_as_absent_destination(self):
        self.get.denied_path = "/repos/opensiro-contributions/example"
        with self.assertRaisesRegex(ReadOnlyError, "not a 404"):
            self.run_check()

    def test_existing_destination_is_blocked_even_if_matching_parent(self):
        self.get.dest = 200, {
            "full_name": "opensiro-contributions/example",
            "fork": True, "parent": {"full_name": "outside/example"}}
        o = self.run_check()
        self.assertEqual(o["status"], "BLOCKED_PUBLIC_PREFLIGHT")
        self.assertIn("already publicly visible", " ".join(o["reasons"]))

    def test_missing_source_is_blocked_and_never_checks_creation(self):
        self.get.source = {}
        o = self.run_check()
        self.assertEqual(o["status"], "BLOCKED_SOURCE")
        self.assert_read_only()

    def test_unknown_branch_and_malformed_sha_block(self):
        self.get.branch = {"commit": {"sha": "short"}}
        self.assertEqual(self.run_check()["status"], "BLOCKED_PUBLIC_PREFLIGHT")

    def test_read_error_blocks(self):
        self.get.denied_path = "/repos/outside/example"
        with self.assertRaises(ReadOnlyError):
            self.run_check()

    def test_api_wrong_response_shape_is_rejected(self):
        with self.assertRaises(ReadOnlyError):
            self.run_check(get=lambda _: [200, {}])

    def test_cli_returns_json_with_no_approval(self):
        from io import StringIO
        import json
        with patch("sys.stdout", new_callable=StringIO) as capture:
            rc = main(["--source", "outside/example", "--fork-name", "example",
                       "--working-branch", "development",
                       "--expected-sha", SHA, "--expected-license", "MIT",
                       "--all-branches"], get=self.get)
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(capture.getvalue())["authorization"],
                         "NOT_APPROVED_NO_WRITES")

    def test_cli_rejects_execute_argument(self):
        result = subprocess.run([sys.executable, str(BASE / "scripts" /
            "fork_public_preflight.py"), "--source", "outside/example",
            "--fork-name", "example", "--working-branch", "development",
            "--execute"], capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unrecognized arguments", result.stderr)

    def test_deployed_workflow_read_only(self):
        workflow = (BASE / ".github/workflows/fork-lifecycle.yml").read_text()
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertIn("scripts/fork_public_preflight.py", workflow)
        self.assertNotIn("UPSTREAM_FORK_TOKEN", workflow)
        self.assertNotIn("--execute", workflow)
        self.assertNotIn("secrets.", workflow)
        self.assertNotIn("create_public_fork(", workflow)


if __name__ == "__main__":
    unittest.main()
