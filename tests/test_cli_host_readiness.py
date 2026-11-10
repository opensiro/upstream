"""Offline, secret-free CLI host readiness tests."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from cli_host_readiness import inspect_cli_host, StageBlocked, main


class FakeResult:
    def __init__(self, exit_code, output=""):
        self.returncode = exit_code
        self.stdout = output


class FakeRunner:
    def __init__(self):
        self.calls = []
        self.gh_auth = False
        self.git_helper = True
        self.identity = "xLagerFeuer"
        self.branch_sha = "a" * 40
        self.source_readable = True

    def __call__(self, args, **kwargs):
        self.calls.append(list(args))
        if args == ["git", "config", "--global", "--get", "credential.helper"]:
            return FakeResult(0 if self.git_helper else 1)
        if args == ["gh", "auth", "status", "--hostname", "github.com"]:
            return FakeResult(0 if self.gh_auth else 1, "sensitive-output-never-exposed")
        if args == ["gh", "api", "--method", "GET", "user", "--jq", ".login"]:
            return FakeResult(0, self.identity)
        if args[:4] == ["gh", "api", "--method", "GET"] and args[-2:] == [
                "--jq", ".commit.sha"]:
            return FakeResult(0 if self.source_readable else 1, self.branch_sha)
        raise AssertionError("Unexpected command " + repr(args))


class TestCLIHostReadiness(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.runner = FakeRunner()
        self.which = lambda name: "/usr/bin/" + name
        self.env = {}

    def check(self, **changes):
        kwargs = {"source": "HarnessDesk/HarnessDesk",
                  "working_branch": "development",
                  "runner": self.runner, "which": self.which,
                  "home": self.home, "environ": self.env}
        kwargs.update(changes)
        return inspect_cli_host(**kwargs)

    def test_credential_store_present_does_not_mean_gh_auth(self):
        (self.home / ".git-credentials").write_text("not-a-token")
        r = self.check()
        self.assertEqual(r["status"], "BLOCKED_GH_CLI_AUTH")
        self.assertTrue(r["git_credential_store_file_present"])
        self.assertTrue(r["git_credential_helper_configured"])
        self.assertFalse(r["gh_authenticated"])
        self.assertIsNone(r["github_login"])
        self.assertFalse(any(c[0:2] == ["git", "credential"]
                             for c in self.runner.calls))

    def test_login_and_source_read_is_not_creation_authority(self):
        self.runner.gh_auth = True
        r = self.check()
        self.assertEqual(r["status"], "CLI_READ_READY_NOT_AUTHORIZED")
        self.assertEqual(r["github_login"], "xLagerFeuer")
        self.assertEqual(r["source_branch_sha"], "a" * 40)
        self.assertEqual(r["authorization"], "NOT_APPROVED_NO_WRITES")
        self.assertEqual(r["fork_create_permission"], "NOT_TESTED_NO_WRITES")
        self.assertTrue(all("POST" not in c for c in self.runner.calls))

    def test_gh_unavailable_never_invokes_gh(self):
        r = self.check(which=lambda n: None if n == "gh" else "/usr/bin/git")
        self.assertEqual(r["status"], "BLOCKED_GH_CLI_UNAVAILABLE")
        self.assertTrue(all(c[0] != "gh" for c in self.runner.calls))

    def test_no_git_binary_does_not_block_gh(self):
        self.runner.gh_auth = True
        r = self.check(which=lambda n: None if n == "git" else "/usr/bin/gh")
        self.assertEqual(r["status"], "CLI_READ_READY_NOT_AUTHORIZED")
        self.assertFalse(r["git_credential_helper_configured"])

    def test_unverified_identity_rejected(self):
        self.runner.gh_auth = True
        self.runner.identity = "invalid token\nvalue"
        r = self.check()
        self.assertEqual(r["status"], "BLOCKED_GH_IDENTITY")
        self.assertIsNone(r["github_login"])

    def test_missing_branch_or_invalid_sha_is_blocked(self):
        self.runner.gh_auth = True
        for branch_sha in ("", "something", "A" * 40):
            self.runner.branch_sha = branch_sha
            with self.subTest(sha=branch_sha):
                self.assertEqual(self.check()["status"],
                                 "BLOCKED_GH_SOURCE_BRANCH_READ")

    def test_source_read_error_is_not_authority(self):
        self.runner.gh_auth = True
        self.runner.source_readable = False
        self.assertEqual(self.check()["status"], "BLOCKED_GH_SOURCE_BRANCH_READ")

    def test_environment_presence_does_not_prove_gh_auth(self):
        self.env["GH_TOKEN"] = "dummy-not-a-real-secret"
        r = self.check()
        self.assertEqual(r["status"], "BLOCKED_GH_CLI_AUTH")
        self.assertTrue(r["github_token_env_presence"])

    def test_invalid_branch_or_source_blocks_before_cli(self):
        for change in ({"source": "../outside"},
                       {"working_branch": "foo/../bar"},
                       {"working_branch": "a b"}):
            with self.subTest(change=change), self.assertRaises(StageBlocked):
                self.check(**change)
        self.assertEqual(self.runner.calls, [])

    def test_gh_only_performs_auth_and_explicit_get(self):
        self.runner.gh_auth = True
        r = self.check()
        self.assertEqual(r["status"], "CLI_READ_READY_NOT_AUTHORIZED")
        gh_calls = [c for c in self.runner.calls if c[0] == "gh"]
        self.assertEqual(gh_calls[0],
            ["gh", "auth", "status", "--hostname", "github.com"])
        for call in gh_calls[1:]:
            self.assertEqual(call[1:4], ["api", "--method", "GET"])
        self.assertTrue(all("auth" not in c[1:2] or c[1] == "auth"
                            for c in gh_calls))

    def test_suppress_credential_helper_data(self):
        self.runner.gh_auth = True
        r = self.check()
        serialized = json.dumps(r)
        self.assertNotIn("sensitive-output", serialized)
        self.assertNotIn("password", serialized)
        self.assertNotIn("secret", serialized)

    def test_cli_rejects_execute_parameter(self):
        proc = subprocess.run([sys.executable, str(ROOT / "scripts" /
            "cli_host_readiness.py"), "--source", "x/y",
            "--working-branch", "main", "--execute"],
            capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("unrecognized arguments", proc.stderr)


if __name__ == "__main__":
    unittest.main()
