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
DISCLOSURE = (ROOT / "templates/EXTERNAL_PR_DISCLOSURE.md").read_text(encoding="utf-8").strip()
for marker, value in {
    "ASSESSMENT_PATH": "assessments/ha/harnessdesk.md",
    "ASSESSMENT_INDEX_SHA": "a" * 40,
    "ASSESSMENT_DATE": "2026-11-02",
    "ASSESSMENT_REVIEW_REF": "f" * 40,
}.items():
    DISCLOSURE = DISCLOSURE.replace("{{" + marker + "}}", value)


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
                         body="Regression test and ownership fix for #1772.\n\n" + DISCLOSURE)

    def preview(self, **changes):
        return prepare_pr_handoff(**(self.data | changes),
                                  runner=self.fake)

    def test_success_is_only_ready_for_review_rest_handoff(self):
        r = self.preview()
        self.assertEqual(r["status"], "PR_READY_FOR_MANUAL_REVIEW_NOT_PUBLISHED")
        self.assertEqual(r["draft_request_body"]["head"],
                         "opensiro-contributions:" + HEAD)
        self.assertEqual(r["draft_request_body"]["base"], "development")
        self.assertFalse(r["draft_request_body"]["draft"])
        self.assertEqual(r["api_path_if_separately_approved"],
                         "repos/HarnessDesk/HarnessDesk/pulls")
        self.assertEqual(len(r["intent_sha256"]), 64)
        self.assertNotIn("token", json.dumps(r).lower())
        self.assertEqual(r["evidence"]["assessment"]["reviewed_at"], "2026-11-02")
        self.assertEqual(r["evidence"]["assessment"]["path"],
                         "assessments/ha/harnessdesk.md")
        self.assertTrue(all(c[3] == "GET" for c in self.fake.calls))

    def test_missing_or_altered_ai_disclosure_fails_before_github_read(self):
        with self.assertRaisesRegex(PRBlocked, "AI-assisted disclosure"):
            self.preview(body="Regression test and ownership fix for #1772.")
        self.assertEqual(self.fake.calls, [])
        with self.assertRaisesRegex(PRBlocked, "AI-assisted disclosure"):
            self.preview(body=self.data["body"].replace(
                "a human approves publication", "no human approves publication"))
        self.assertEqual(self.fake.calls, [])
        with self.assertRaisesRegex(PRBlocked, "AI-assisted disclosure"):
            self.preview(body=self.data["body"] + "\n" + DISCLOSURE)
        self.assertEqual(self.fake.calls, [])

    def test_assessment_link_date_and_source_are_required_before_github_read(self):
        cases = (
            self.data["body"].replace("blob/main/assessments/ha/harnessdesk.md",
                                      "blob/main/assessments/xx/other.md"),
            self.data["body"].replace("2026-11-02", "2026-99-40"),
            self.data["body"].replace("`" + "f" * 40 + "`", "`unknown`"),
            self.data["body"].replace("blob/" + "a" * 40,
                                      "blob/main"),
            self.data["body"].replace("disclosure:v2", "disclosure:v1"),
            self.data["body"] + "\nExtra text after disclosure",
        )
        for body in cases:
            with self.subTest(body=body[-100:]), self.assertRaisesRegex(
                    PRBlocked, "AI-assisted disclosure"):
                self.preview(body=body)
        self.assertEqual(self.fake.calls, [])

    def test_explicit_draft_requires_documented_reason(self):
        with self.assertRaisesRegex(PRBlocked, "concrete documented reason"):
            self.preview(draft=True)
        self.assertEqual(self.fake.calls, [])
        out = self.preview(draft=True, draft_reason="Pending review of an optional test")
        self.assertTrue(out["draft_request_body"]["draft"])
        self.assertEqual(out["evidence"]["draft_reason"],
                         "Pending review of an optional test")
        self.assertTrue(all(c[3] == "GET" for c in self.fake.calls))

    def test_ready_for_review_rejects_spurious_draft_reason(self):
        with self.assertRaisesRegex(PRBlocked, "only valid"):
            self.preview(draft_reason="Unresolved test")
        self.assertEqual(self.fake.calls, [])

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
        modified = self.preview(body=self.data["body"].replace(
            "fix for #1772.", "fix for #1772. Updated test."))
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
            self.assertFalse(json.loads(capture.getvalue())["draft_request_body"]["draft"])

    def test_cli_explicit_draft_requires_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            body_file = Path(tmp) / "body.md"
            body_file.write_text(self.data["body"], encoding="utf-8")
            argv = ["--upstream", SOURCE, "--fork", FORK,
                    "--head-branch", HEAD, "--head-sha", H_SHA,
                    "--base-branch", "development", "--base-sha", B_SHA,
                    "--title", self.data["title"], "--body-file", str(body_file),
                    "--draft"]
            with patch("sys.stdout", new_callable=StringIO) as capture:
                rc = main(argv, runner=self.fake)
            self.assertEqual(rc, 2)
            self.assertIn("concrete documented reason", capture.getvalue())
            self.assertEqual(self.fake.calls, [])

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
