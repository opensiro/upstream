"""Offline GitHub REST port test: never sends a real GitHub request."""
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from rest_fork_port import GitHubRESTForkPort, StageBlocked, NotFound


SHA = "a" * 40
SOURCE = {"full_name": "external/example", "private": False,
          "archived": False, "disabled": False, "forking_allowed": True,
          "default_branch": "main", "license": {"spdx_id": "MIT"}}
FORK = {"full_name": "opensiro-contributions/example", "fork": True,
        "private": False, "archived": False,
        "parent": {"full_name": "external/example"},
        "permissions": {"push": True},
        "html_url": "https://github.com/opensiro-contributions/example"}


class Transport:
    def __init__(self):
        self.calls = []
        self.source_branch_sha = SHA
        self.fork_branch_sha = SHA
        self.fork_exists = False
        self.read_403 = False
        self.create_status = 202
        self.bad_identity = False
        self.proof_allowed = True
        self.created_mode = None

    def capability(self, owner):
        return {"available": True, "authorized": self.proof_allowed,
                "owner": owner, "actor": "operator-account"}

    def api(self, method, route, *, body=None):
        self.calls.append((method, route, body))
        if self.read_403 and method == "GET":
            return 403, {}
        if method == "POST":
            self.created_mode = body["default_branch_only"]
            if self.create_status != 202:
                return self.create_status, {}
            self.fork_exists = True
            return 202, {"owner": {"login": "unrelated" if self.bad_identity
                                       else "opensiro-contributions"},
                         "name": body["name"]}
        if route == "/repos/external/example":
            return 200, dict(SOURCE)
        if route == "/repos/external/example/branches/development":
            return 200, {"commit": {"sha": self.source_branch_sha}}
        if route == "/repos/external/example/branches/main":
            return 200, {"commit": {"sha": self.source_branch_sha}}
        if route == "/repos/opensiro-contributions/example":
            return (200, dict(FORK)) if self.fork_exists else (404, {})
        if route == "/repos/opensiro-contributions/example/branches/development":
            return ((200, {"commit": {"sha": self.fork_branch_sha}})
                    if self.fork_exists and self.created_mode is False else (404, {}))
        if route == "/repos/opensiro-contributions/example/branches/main":
            return ((200, {"commit": {"sha": self.fork_branch_sha}})
                    if self.fork_exists else (404, {}))
        return 404, {}


class RESTPortTests(unittest.TestCase):
    def setUp(self):
        self.remote = Transport()
        self.port = GitHubRESTForkPort(api=self.remote.api,
                                       capability_attestor=self.remote.capability)

    def writes(self):
        return [x for x in self.remote.calls if x[0] == "POST"]

    def test_source_and_fork_404_are_distinct(self):
        self.assertEqual(self.port.repo("external/example")["default_branch"], "main")
        with self.assertRaises(NotFound):
            self.port.repo("opensiro-contributions/example")
        self.assertEqual(self.writes(), [])

    def test_existing_readback_contains_actual_parent(self):
        self.remote.fork_exists = True
        observed = self.port.repo("opensiro-contributions/example")
        self.assertEqual(observed["parent"]["full_name"], "external/example")

    def test_read_403_is_never_a_genuine_not_found(self):
        self.remote.read_403 = True
        with self.assertRaises(PermissionError):
            self.port.repo("opensiro-contributions/example")
        self.assertEqual(self.writes(), [])

    def test_source_branch_sha_is_normalized(self):
        self.assertEqual(self.port.branch("external/example", "development"), {"sha": SHA})
        self.assertIn("/branches/development", self.remote.calls[-1][1])

    def test_github_working_branch_invalid_sha_fails(self):
        self.remote.source_branch_sha = "truncated"
        with self.assertRaises(StageBlocked):
            self.port.branch("external/example", "development")

    def test_branch_ref_path_escape_fails(self):
        for name in ("../main", "a//b", "feature@{1}", "a.lock", "a b", ""):
            with self.subTest(name=name), self.assertRaises(StageBlocked):
                self.port.branch("external/example", name)
        self.assertEqual(self.remote.calls, [])

    def test_invalid_repository_name_fails_before_network(self):
        for value in ("../example", "outside/example/extra", "a/x?y", "a/."):
            with self.subTest(value=value), self.assertRaises(StageBlocked):
                self.port.repo(value)
        self.assertEqual(self.remote.calls, [])

    def test_owner_locked_and_capability_checked(self):
        with self.assertRaises(StageBlocked):
            self.port.fork_capability("personal")
        self.remote.proof_allowed = False
        with self.assertRaises(StageBlocked):
            self.port.fork_capability("opensiro-contributions")
        self.assertEqual(self.writes(), [])

    def test_unknown_host_methods_absent(self):
        with self.assertRaises(StageBlocked):
            GitHubRESTForkPort(api=None, capability_attestor=self.remote.capability)

    def test_fork_all_branches_uses_correct_rest_shape_once(self):
        response = self.port.create_public_fork(
            "external/example", "opensiro-contributions", "example",
            default_branch_only=False)
        self.assertEqual(response, {"accepted": True})
        self.assertEqual(len(self.writes()), 1)
        self.assertEqual(self.writes()[0], ("POST",
            "/repos/external/example/forks", {
                "organization": "opensiro-contributions", "name": "example",
                "default_branch_only": False}))
        self.assertEqual(self.port.branch(
            "opensiro-contributions/example", "development")["sha"], SHA)

    def test_default_only_does_not_materialize_development(self):
        self.port.create_public_fork("external/example",
            "opensiro-contributions", "example", default_branch_only=True)
        with self.assertRaises(NotFound):
            self.port.branch("opensiro-contributions/example", "development")

    def test_wrong_fork_namespace_does_not_call_provider(self):
        with self.assertRaises(StageBlocked):
            self.port.create_public_fork(
                "external/example", "personal", "example", default_branch_only=True)
        self.assertEqual(self.writes(), [])

    def test_wrong_response_identity_never_accepted(self):
        self.remote.bad_identity = True
        with self.assertRaises(StageBlocked):
            self.port.create_public_fork("external/example",
                "opensiro-contributions", "example", default_branch_only=True)
        self.assertEqual(len(self.writes()), 1)

    def test_http_permission_failure(self):
        self.remote.create_status = 403
        with self.assertRaises(PermissionError):
            self.port.create_public_fork("external/example",
                "opensiro-contributions", "example", default_branch_only=True)
        self.assertEqual(len(self.writes()), 1)

    def test_collision_or_validation_failure(self):
        for status in (409, 422):
            remote = Transport()
            remote.create_status = status
            port = GitHubRESTForkPort(
                api=remote.api, capability_attestor=remote.capability)
            with self.subTest(status=status), self.assertRaises(StageBlocked):
                port.create_public_fork("external/example",
                    "opensiro-contributions", "example", default_branch_only=True)
            self.assertEqual(len([x for x in remote.calls if x[0] == "POST"]), 1)

    def test_invalid_copy_mode_no_request(self):
        with self.assertRaises(StageBlocked):
            self.port.create_public_fork("external/example",
                "opensiro-contributions", "example", default_branch_only="false")
        self.assertEqual(self.writes(), [])

    def test_source_owner_cannot_be_destination(self):
        with self.assertRaises(StageBlocked):
            self.port.create_public_fork(
                "opensiro-contributions/example", "opensiro-contributions",
                "other", default_branch_only=True)
        self.assertEqual(self.writes(), [])


if __name__ == "__main__":
    unittest.main()
