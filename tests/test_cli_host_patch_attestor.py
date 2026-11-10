"""Read-only actor/rights attestor and credential-free git subprocess tests."""
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from cli_host_patch_attestor import GitHubCLIProviderAttestor, StageBlocked
from cli_host_multifile_runtime import GitHubCLIJSONTransport
from test_cli_host_multifile_runtime import (
    RealLocalGitMaterializerTests, SOURCE, TEST, PATCH, REPO,
)


SOURCE_REPO = "HarnessDesk/HarnessDesk"
OWNER = "opensiro-contributions"
PRINCIPAL = "xLagerFeuer"


class FakeAuthorizedRead:
    def __init__(self):
        self.calls = []
        self.actor = PRINCIPAL
        self.role = "admin"
        self.state = "active"
        self.fork = {
            "full_name": REPO, "private": False, "archived": False,
            "fork": True, "parent": {"full_name": SOURCE_REPO},
            "permissions": {"push": True},
        }
        self.fail_path = None
        self.fail_status = 403

    def __call__(self, method, path, body=None):
        self.calls.append((method, path))
        if method != "GET" or body is not None:
            raise AssertionError("attestor must never write")
        if path == self.fail_path:
            return self.fail_status, {"message": "denied"}
        if path == "user":
            return 200, {"login": self.actor}
        if path == "user/memberships/orgs/" + OWNER:
            return 200, {"role": self.role, "state": self.state}
        if path == "repos/" + REPO:
            return 200, self.fork
        raise AssertionError(path)


class ActorAttestorTests(unittest.TestCase):
    def setUp(self):
        self.fake = FakeAuthorizedRead()
        self.attestor = GitHubCLIProviderAttestor(
            transport=self.fake, expected_fork=REPO,
            expected_source=SOURCE_REPO, expected_actor=PRINCIPAL)

    def test_good_provider_evidence_is_not_a_host_stage_permit(self):
        x = self.attestor(OWNER)
        self.assertEqual(x, {"owner": OWNER, "actor": PRINCIPAL,
                             "available": True, "authorized": True})
        self.assertEqual(self.fake.calls, [
            ("GET", "user"), ("GET", "user/memberships/orgs/" + OWNER),
            ("GET", "repos/" + REPO)])
        self.assertNotIn("grant", x)

    def test_different_authenticated_actor_fails(self):
        self.fake.actor = "otherPerson"
        with self.assertRaises(StageBlocked):
            self.attestor(OWNER)

    def test_inactive_org_membership_fails(self):
        self.fake.state = "pending"
        with self.assertRaises(StageBlocked):
            self.attestor(OWNER)

    def test_org_membership_403_is_not_absence(self):
        self.fake.fail_path = "user/memberships/orgs/" + OWNER
        with self.assertRaises(StageBlocked):
            self.attestor(OWNER)

    def test_private_or_wrong_parent_fork_fails(self):
        for k, v in (("private", True), ("parent", {"full_name":"stranger/repo"}),
                     ("fork", False), ("permissions", {"push": False}),
                     ("archived", True)):
            self.fake.fork[k] = v
            with self.subTest(key=k), self.assertRaises(StageBlocked):
                self.attestor(OWNER)
            self.fake.fork = FakeAuthorizedRead().fork

    def test_disabled_push_permission_is_not_authorized(self):
        self.fake.fork["permissions"] = {"pull": True}
        with self.assertRaises(StageBlocked):
            self.attestor(OWNER)

    def test_wrong_requested_owner_blocks_before_read(self):
        with self.assertRaises(StageBlocked):
            self.attestor("opensiro")
        self.assertEqual(self.fake.calls, [])

    def test_wrong_repo_configuration_blocks_at_constructor(self):
        with self.assertRaises(StageBlocked):
            GitHubCLIProviderAttestor(transport=self.fake,
                expected_fork="personal/HarnessDesk", expected_source=SOURCE_REPO)

    def test_user_read_403_fails_closed(self):
        self.fake.fail_path = "user"
        with self.assertRaises(StageBlocked):
            self.attestor(OWNER)

    def test_transport_allows_only_bounded_identity_gets(self):
        class Runner:
            def __init__(self):
                self.calls = []
            def __call__(self,args,**kw):
                self.calls.append(args)
                return type("Result",(),{"stdout":"HTTP/2.0 200 OK\r\n\r\n{}",
                                         "returncode":0})()
        runner = Runner()
        api = GitHubCLIJSONTransport(runner=runner)
        self.assertEqual(api("GET","user")[0],200)
        self.assertEqual(api("GET","user/memberships/orgs/"+OWNER)[0],200)
        for path in ("user/emails", "user/memberships/orgs/other",
                     "orgs/opensiro/members", "user/gists"):
            with self.subTest(path=path), self.assertRaises(StageBlocked):
                api("GET",path)
        self.assertEqual(len(runner.calls),2)

    def test_gh_nonzero_success_status_is_not_accepted(self):
        runner=lambda *a,**kw:type("Result",(),{
            "stdout":"HTTP/2.0 200 OK\r\n\r\n{}","returncode":1})()
        with self.assertRaises(StageBlocked):
            GitHubCLIJSONTransport(runner=runner)("GET","user")


class MaterializerCredentialsTests(RealLocalGitMaterializerTests):
    """Reuse actual bare-repo fixture, capture every real Git child env."""

    def test_git_never_inherits_parent_pat_or_custom_filter(self):
        calls = []
        def guarded_run(args, **kwargs):
            calls.append(kwargs.get("env"))
            return subprocess.run(args, **kwargs)
        from cli_host_multifile_runtime import CleanPublicGitPatchMaterializer
        mat = CleanPublicGitPatchMaterializer(
            runner=guarded_run, clone_base=str(self.root))
        with patch.dict(os.environ, {
            "GH_TOKEN": "dummy-private-value",
            "GITHUB_TOKEN": "dummy-other-value",
            "SSH_AUTH_SOCK": "/private/socket",
            "GIT_ASKPASS": "/private/askpass",
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "filter.exec.smudge",
            "GIT_CONFIG_VALUE_0": "malicious-smudge-command",
            "GIT_SSH_COMMAND": "malicious-ssh",
        }):
            out = mat(REPO, self.base, PATCH, [SOURCE, TEST])
        self.assertEqual(out["files"][TEST],"assert(true)\n")
        self.assertGreater(len(calls),5)
        for env in calls:
            self.assertIsInstance(env,dict)
            for banned in ("GH_TOKEN", "GITHUB_TOKEN", "SSH_AUTH_SOCK",
                           "GIT_ASKPASS", "GIT_CONFIG_COUNT",
                           "GIT_CONFIG_VALUE_0","GIT_SSH_COMMAND"):
                self.assertNotIn(banned,env)
            self.assertEqual(env["GIT_CONFIG_NOSYSTEM"],"1")
            self.assertEqual(env["GIT_TERMINAL_PROMPT"],"0")
            self.assertEqual(env["GIT_CONFIG_GLOBAL"], os.devnull)
            self.assertNotEqual(env["HOME"],os.path.expanduser("~"))

if __name__=="__main__":
    unittest.main()
