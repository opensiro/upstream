"""Offline tests: organization-owned fork PR previews never POST or publish."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from io import StringIO

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from upstream_pr_handoff import prepare_pr_handoff, PRBlocked, main

SOURCE = "HarnessDesk/HarnessDesk"
FORK = "opensiro-contributions/HarnessDesk"
HEAD = "opensiro/fix-toolgateway-1772"
B_SHA = "b" * 40
H_SHA = "c" * 40


class Response:
    def __init__(self, value, error=False):
        self.returncode = 1 if error else 0
        self.stdout = json.dumps(value)


class FakeRunner:
    def __init__(self):
        self.calls = []
        self.identity = "xLagerFeuer"
        self.source = {"full_name": SOURCE, "private": False,
                       "archived": False, "disabled": False}
        self.fork = {"full_name": FORK, "private": False, "archived": False,
                     "fork": True, "permissions": {"push": True},
                     "parent": {"full_name": SOURCE}}
        self.base_sha = B_SHA
        self.head_sha = H_SHA
        self.cmp = {"status": "ahead", "ahead_by": 1,
                    "files": [{"filename": "packages/server/test/socket.test.ts"}]}
        self.open_prs = []
        self.fail_suffix = None

    def __call__(self, args, **kwargs):
        self.calls.append(args)
        if args[:4] != ["gh", "api", "--method", "GET"] or len(args) != 5:
            raise AssertionError("Only gh api GET is allowed: " + repr(args))
        endpoint = args[-1]
        if self.fail_suffix is not None and endpoint.endswith(self.fail_suffix):
            return Response({}, error=True)
        if endpoint == "user":
            return Response({"login": self.identity})
        if endpoint == "repos/" + SOURCE:
            return Response(self.source)
        if endpoint == "repos/" + FORK:
            return Response(self.fork)
        if endpoint == "repos/" + SOURCE + "/branches/development":
            return Response({"commit": {"sha": self.base_sha}})
        if endpoint == "repos/" + FORK + "/branches/opensiro%2Ffix-toolgateway-1772":
            return Response({"commit": {"sha": self.head_sha}})
        if "/compare/" in endpoint:
            return Response(self.cmp)
        if "/pulls?" in endpoint:
            return Response(self.open_prs)
        raise AssertionError("Unexpected endpoint: " + endpoint)


class UpstreamPRHandoffTests(unittest.TestCase):
    def setUp(self):
        self.fake = FakeRunner()
        self.data = dict(upstream=SOURCE, fork=FORK, head_branch=HEAD,
                         head_sha=H_SHA, base_branch="development",
                         base_sha=B_SHA,
                         title="fix: prevent duplicate ToolGateway socket takeover",
                         body="Regression test and ownership fix for #1772.")

    def preview(self, **changes):
        return prepare_pr_handoff(**(self.data | changes),
                                  runner=self.fake)

    def test_success_is_only_draft_rest_handoff(self):
        r = self.preview()
        self.assertEqual(r["status"], "PR_READY_FOR_MANUAL_REVIEW_NOT_PUBLISHED")
        self.assertEqual(r["draft_request_body"]["head"],
                         "opensiro-contributions:" + HEAD)
        self.assertEqual(r["draft_request_body"]["base"], "development")
        self.assertTrue(r["draft_request_body"]["draft"])
        self.assertEqual(r["api_path_if_separately_approved"],
                         "repos/HarnessDesk/HarnessDesk/pulls")
        self.assertEqual(len(r["intent_sha256"]), 64)
        self.assertNotIn("token", json.dumps(r).lower())
        self.assertTrue(all(c[3] == "GET" for c in self.fake.calls))

    def test_user_identity_is_pinned_and_sane(self):
        self.fake.identity = "invalid:actor"
        with self.assertRaisesRegex(PRBlocked, "user"):
            self.preview()

    def test_source_and_fork_identity_or_parent_mismatch_blocks(self):
        self.fake.fork["parent"]["full_name"] = "other/source"
        with self.assertRaisesRegex(PRBlocked, "parent"):
            self.preview()
        self.fake.fork["parent"]["full_name"] = SOURCE
        self.fake.source["full_name"] = "wrong/wrong"
        with self.assertRaisesRegex(PRBlocked, "upstream"):
            self.preview()

    def test_fork_push_or_public_permission_required(self):
        self.fake.fork["permissions"]["push"] = False
        with self.assertRaisesRegex(PRBlocked, "push"):
            self.preview()
        self.fake.fork["permissions"]["push"] = True
        self.fake.fork["private"] = True
        with self.assertRaisesRegex(PRBlocked, "public"):
            self.preview()

    def test_head_sha_drift_rejected(self):
        self.fake.head_sha = "e" * 40
        with self.assertRaisesRegex(PRBlocked, "head branch"):
            self.preview()

    def test_base_sha_drift_rejected(self):
        self.fake.base_sha = "d" * 40
        with self.assertRaisesRegex(PRBlocked, "base branch"):
            self.preview()

    def test_zero_commit_diff_fails(self):
        self.fake.cmp = {"status": "identical", "ahead_by": 0, "files": []}
        with self.assertRaisesRegex(PRBlocked, "diff"):
            self.preview()

    def test_compare_with_no_files_or_truncated_fails(self):
        self.fake.cmp["files"] = []
        with self.assertRaisesRegex(PRBlocked, "diff"):
            self.preview()
        self.fake.cmp["files"] = [{"filename": str(i)} for i in range(300)]
        with self.assertRaisesRegex(PRBlocked, "truncated"):
            self.preview()

    def test_duplicate_open_pr_fails(self):
        self.fake.open_prs = [{"number": 123}]
        with self.assertRaisesRegex(PRBlocked, "already"):
            self.preview()

    def test_pr_inventory_truncation_fails(self):
        self.fake.open_prs = [{}] * 100
        with self.assertRaisesRegex(PRBlocked, "truncated"):
            self.preview()

    def test_read_api_failure_is_fail_closed(self):
        self.fake.fail_suffix = "/branches/development"
        with self.assertRaisesRegex(PRBlocked, "GET unavailable"):
            self.preview()

    def test_missing_working_branch_is_explicitly_blocked_no_post(self):
        self.fake.fail_suffix = "/branches/opensiro%2Ffix-toolgateway-1772"
        with self.assertRaisesRegex(PRBlocked, "fork contribution head branch"):
            self.preview()
        self.assertTrue(all(call[3] == "GET" for call in self.fake.calls))

    def test_namespaced_branch_only(self):
        for invalid in ("main", "fix/issue", "../bad", "opensiro/a..b",
                        "opensiro/a.lock", "opensiro/a//b"):
            with self.subTest(invalid=invalid), self.assertRaises(PRBlocked):
                self.preview(head_branch=invalid)
        self.assertEqual(self.fake.calls, [])

    def test_exact_organizations_only(self):
        for bad in ("personal/HarnessDesk", "a/b/extra", SOURCE):
            with self.subTest(bad=bad), self.assertRaises(PRBlocked):
                self.preview(fork=bad)
        self.assertEqual(self.fake.calls, [])

    def test_rejects_unpinned_sha_before_network(self):
        with self.assertRaises(PRBlocked):
            self.preview(head_sha="HEAD")
        self.assertEqual(self.fake.calls, [])

    def test_same_owner_repo_uses_head_repo_parameter(self):
        self.data["upstream"] = "opensiro/upstream"
        self.data["fork"] = "opensiro/upstream-fork"
        self.fake.source["full_name"] = "opensiro/upstream"
        self.fake.fork["full_name"] = "opensiro/upstream-fork"
        self.fake.fork["parent"]["full_name"] = "opensiro/upstream"
        # Adapt exact paths to an owner-agnostic fake.
        old = self.fake
        class SameOwner(FakeRunner):
            def __call__(self, args, **kwargs):
                mapped = list(args)
                mapped[-1] = (mapped[-1].replace("repos/opensiro/upstream-fork",
                                                 "repos/" + FORK)
                             .replace("repos/opensiro/upstream",
                                      "repos/" + SOURCE))
                old.calls.append(args)
                if mapped[-1] == "repos/" + SOURCE:
                    return Response(old.source)
                if mapped[-1] == "repos/" + FORK:
                    return Response(old.fork)
                if mapped[-1].startswith("repos/" + FORK + "/branches/"):
                    return Response({"commit": {"sha": H_SHA}})
                if mapped[-1].startswith("repos/" + SOURCE + "/branches/"):
                    return Response({"commit": {"sha": B_SHA}})
                if "/compare/" in mapped[-1]:
                    return Response(old.cmp)
                if "/pulls?" in mapped[-1]:
                    return Response([])
                if mapped[-1] == "user":
                    return Response({"login": old.identity})
                raise AssertionError(mapped[-1])
        out = prepare_pr_handoff(**self.data, runner=SameOwner())
        self.assertEqual(out["draft_request_body"]["head_repo"], "upstream-fork")

    def test_preview_is_deterministic(self):
        first = self.preview()
        second = self.preview()
        self.assertEqual(first["intent_sha256"], second["intent_sha256"])
        modified = self.preview(body=self.data["body"] + " Updated test.")
        self.assertNotEqual(first["intent_sha256"], modified["intent_sha256"])

    def test_cli_prints_handoff_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            body_file = Path(tmp) / "body.md"
            body_file.write_text(self.data["body"], encoding="utf-8")
            argv = ["--upstream", SOURCE, "--fork", FORK,
                    "--head-branch", HEAD, "--head-sha", H_SHA,
                    "--base-branch", "development", "--base-sha", B_SHA,
                    "--title", self.data["title"], "--body-file", str(body_file)]
            with patch("sys.stdout", new_callable=StringIO) as capture:
                rc = main(argv, runner=self.fake)
            self.assertEqual(rc, 0)
            self.assertEqual(json.loads(capture.getvalue())["authorization"],
                             "EXTERNAL_PR_HUMAN_OWNED_NO_WRITE")

    def test_cli_has_no_publish_or_post_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            body_file = Path(tmp) / "body.md"
            body_file.write_text(self.data["body"], encoding="utf-8")
            args = [sys.executable, str(ROOT / "scripts/upstream_pr_handoff.py"),
                    "--upstream", SOURCE, "--fork", FORK,
                    "--head-branch", HEAD, "--head-sha", H_SHA,
                    "--base-branch", "development", "--base-sha", B_SHA,
                    "--title", self.data["title"], "--body-file", str(body_file),
                    "--publish"]
            p = subprocess.run(args, text=True, capture_output=True)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("unrecognized arguments", p.stderr)
            self.assertEqual(self.fake.calls, [])


if __name__ == "__main__":
    unittest.main()
