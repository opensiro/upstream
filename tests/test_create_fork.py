"""Offline unit tests: no GitHub writes and no token exposure."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "create_fork", Path(__file__).resolve().parents[1] / "scripts" / "create_fork.py")
fork = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fork)

SOURCE = {"full_name": "owner/project", "private": False, "archived": False,
          "disabled": False, "license": {"spdx_id": "MIT"}}
DEST = {"fork": True, "private": False, "parent": {"full_name": "owner/project"},
        "html_url": "https://github.com/opensiro-contributions/project"}

class ForkTests(unittest.TestCase):
    def test_preview_never_writes(self):
        calls = []
        def request(method, path, **kwargs):
            calls.append(method)
            return (200, SOURCE) if path == "/repos/owner/project" else (404, {})
        result = fork.run("owner/project", request=request)
        self.assertEqual(result["status"], "DRY_RUN")
        self.assertEqual(calls, ["GET", "GET"])
        self.assertEqual(result["license_observed"], "MIT")

    def test_existing_fork_requires_exact_parent(self):
        def request(method, path, **kwargs):
            return (200, SOURCE) if path == "/repos/owner/project" else (200, DEST)
        self.assertEqual(fork.run("owner/project", request=request)["status"], "EXISTS_VERIFIED")
        for invalid, message in [
            ({**DEST, "fork": False}, "non-fork"),
            ({**DEST, "parent": {"full_name": "other/project"}}, "different parent"),
            ({**DEST, "private": True}, "not public"),
        ]:
            with self.subTest(message=message):
                with self.assertRaisesRegex(fork.ForkError, message):
                    fork.verify(invalid, "owner/project")

    def test_reject_invalid_slugs(self):
        for source in ["a/../b", "a/b/c", "opensiro-contributions/self", "a/b;curl"]:
            with self.subTest(source=source), self.assertRaises(fork.ForkError):
                fork.run(source, request=lambda *a, **k: self.fail("API called"))

    def test_reject_nonpublic_sources(self):
        for field in ("private", "archived", "disabled"):
            def request(method, path, **kwargs):
                return 200, {**SOURCE, field: True}
            with self.subTest(field=field), self.assertRaisesRegex(fork.ForkError, "public"):
                fork.run("owner/project", request=request)

    @patch.dict("os.environ", {"UPSTREAM_FORK_TOKEN": "dummy"})
    def test_execute_verifies_parent(self):
        seen = []
        count = [0]
        def request(method, path, **kwargs):
            seen.append((method, path, kwargs))
            if path == "/repos/owner/project":
                return 200, SOURCE
            if method == "POST":
                return 202, {"owner": {"login": "opensiro-contributions"}, "name": "project"}
            count[0] += 1
            return (404, {}) if count[0] < 3 else (200, DEST)
        result = fork.run("owner/project", execute=True, request=request, sleep=lambda _: None)
        self.assertEqual(result["status"], "CREATED_VERIFIED")
        posts = [x for x in seen if x[0] == "POST"]
        self.assertEqual(len(posts), 1)
        self.assertTrue(posts[0][2]["body"]["default_branch_only"])
        self.assertEqual(posts[0][2]["body"]["organization"], "opensiro-contributions")

    @patch.dict("os.environ", {"UPSTREAM_FORK_TOKEN": "dummy"})
    def test_pending_never_claims_verified(self):
        def request(method, path, **kwargs):
            if path == "/repos/owner/project":
                return 200, SOURCE
            if method == "POST":
                return 202, {"owner": {"login": "opensiro-contributions"}, "name": "project"}
            return 404, {}
        with patch.object(fork, "ATTEMPTS", 2):
            result = fork.run("owner/project", execute=True, request=request, sleep=lambda _: None)
        self.assertEqual(result["status"], "PENDING_VERIFICATION")

    def test_execute_requires_separate_token(self):
        def request(method, path, **kwargs):
            return (200, SOURCE) if path == "/repos/owner/project" else (404, {})
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(fork.ForkError, "missing"):
                fork.run("owner/project", execute=True, request=request)

if __name__ == "__main__":
    unittest.main()
