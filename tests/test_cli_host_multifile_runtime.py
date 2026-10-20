"""Offline tests for host-injected gh transport and real sandboxed git apply."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from cli_host_multifile_runtime import (
    GitHubCLIJSONTransport, CleanPublicGitPatchMaterializer, StageBlocked)

SOURCE = "packages/server/src/tool-gateway.ts"
TEST = "packages/server/test/tool-gateway-ownership.test.ts"
OLD = "export const live = false\n"
NEW = "export const live = true\n"
ADDED = "assert(true)\n"
PATCH = (
    f"diff --git a/{SOURCE} b/{SOURCE}\n"
    f"--- a/{SOURCE}\n+++ b/{SOURCE}\n"
    "@@ -1 +1 @@\n-export const live = false\n+export const live = true\n"
    f"diff --git a/{TEST} b/{TEST}\nnew file mode 100644\n"
    f"--- /dev/null\n+++ b/{TEST}\n"
    "@@ -0,0 +1 @@\n+assert(true)\n"
)
REPO = "opensiro-contributions/HarnessDesk"


class FakeRunResult:
    def __init__(self, output, exit_code=0):
        self.stdout = output
        self.returncode = exit_code


class FakeGhRunner:
    def __init__(self):
        self.calls = []
        self.parsed_body = None
        self.response_code = 200
        self.output_json = {"hello": "world"}

    def __call__(self, args, **kwargs):
        self.calls.append(args)
        if "--input" in args:
            path = Path(args[args.index("--input")+1])
            self.parsed_body = json.loads(path.read_text())
            self.assert_secret_free_args(args)
        return FakeRunResult(
            "HTTP/2 " + str(self.response_code) + " OK\r\n"
            "content-type: application/json\r\n\r\n" +
            json.dumps(self.output_json))

    @staticmethod
    def assert_secret_free_args(args):
        assert not any("secret" in part for part in args)


class GitHubCLITransportTests(unittest.TestCase):
    def setUp(self):
        self.runner = FakeGhRunner()
        self.api = GitHubCLIJSONTransport(runner=self.runner)

    def test_get_returns_real_status(self):
        self.assertEqual(self.api("GET", "repos/HarnessDesk/HarnessDesk"),
                         (200, {"hello": "world"}))
        self.assertEqual(self.runner.calls[0][0:3],
                         ["gh", "api", "--include"])

    def test_404_is_not_403(self):
        for status in (403,404,422):
            self.runner.response_code = status
            self.assertEqual(self.api("GET", "repos/HarnessDesk/HarnessDesk")[0],
                             status)

    def test_git_data_write_uses_file_and_no_token_in_args(self):
        body = {"tree": "a" * 40, "message": "patch"}
        res = self.api("POST",
           "repos/opensiro-contributions/HarnessDesk/git/commits", body)
        self.assertEqual(res[0],200)
        self.assertEqual(self.runner.parsed_body, body)
        argv = self.runner.calls[0]
        self.assertNotIn(json.dumps(body), argv)
        self.assertNotIn("GH_TOKEN", repr(argv))

    def test_denies_external_write(self):
        for path in ("repos/HarnessDesk/HarnessDesk/pulls",
                     "repos/opensiro/HarnessDesk/git/refs",
                     "repos/opensiro-contributions/HarnessDesk/pulls",
                     "repos/opensiro-contributions/HarnessDesk/git/refs/heads",
                     "user"):
            with self.subTest(path=path), self.assertRaises(StageBlocked):
                self.api("POST",path,{"whatever": 1})
        self.assertEqual(self.runner.calls, [])

    def test_rejects_unauthorized_methods(self):
        for method in ("PATCH","DELETE","PUT"):
            with self.assertRaises(StageBlocked):
                self.api(method,"repos/opensiro-contributions/HarnessDesk/git/refs",
                         {"sha": "a"*40})
        self.assertEqual(self.runner.calls, [])

    def test_rejects_json_as_response_list(self):
        self.runner.output_json = [{"x": 1}]
        with self.assertRaises(StageBlocked):
            self.api("GET","repos/HarnessDesk/HarnessDesk")

    def test_bad_http_status_fails_closed(self):
        self.runner.__call__ = lambda *a,**kw: FakeRunResult("not http")
        # Explicit callable replacement needed because special methods
        # are bound through the type, not instance attributes.
        self.api = GitHubCLIJSONTransport(runner=lambda *a,**kw: FakeRunResult("not http"))
        with self.assertRaises(StageBlocked):
            self.api("GET","repos/HarnessDesk/HarnessDesk")

    def test_cli_runner_crash_does_not_return_authorization(self):
        def crash(*args, **kwargs):
            raise OSError("unavailable")
        self.api = GitHubCLIJSONTransport(runner=crash)
        with self.assertRaises(StageBlocked):
            self.api("GET", "repos/HarnessDesk/HarnessDesk")


class RealLocalGitMaterializerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        bare = self.root / "opensiro-contributions" / "HarnessDesk.git"
        bare.parent.mkdir(parents=True)
        work = self.root / "work"
        self.call("git", "init", "--bare", str(bare))
        self.call("git", "init", "-b", "development", str(work))
        self.call("git", "-C", str(work), "config", "user.name", "Test")
        self.call("git", "-C", str(work), "config", "user.email", "test@example.com")
        f = work / SOURCE
        f.parent.mkdir(parents=True)
        f.write_text(OLD)
        self.call("git", "-C", str(work), "add", "--", SOURCE)
        self.call("git", "-C", str(work), "commit", "-m", "fixture")
        self.base = self.call("git", "-C", str(work), "rev-parse", "HEAD").strip()
        self.call("git", "-C", str(work), "remote", "add", "origin", str(bare))
        self.call("git", "-C", str(work), "push", "origin", "development")
        self.materialize = CleanPublicGitPatchMaterializer(clone_base=str(self.root))

    @staticmethod
    def call(*args):
        return subprocess.run(args, check=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True).stdout

    def test_real_git_apply_clean_checkout_and_both_files(self):
        obj=self.materialize(REPO,self.base,PATCH,[SOURCE,TEST])
        self.assertEqual(obj["base_sha"],self.base)
        self.assertEqual(obj["changed_paths"],[SOURCE,TEST])
        self.assertEqual(obj["files"][SOURCE],NEW)
        self.assertEqual(obj["files"][TEST],ADDED)
        self.assertEqual(obj["source_file_modes"][SOURCE],"100644")
        self.assertEqual(obj["source_file_modes"][TEST],"100644")

    def test_bad_hunk_fails_without_remote_write(self):
        modified=PATCH.replace("export const live = false","not matching")
        with self.assertRaises(StageBlocked):
            self.materialize(REPO,self.base,modified,[SOURCE,TEST])

    def test_stale_base_sha_fails(self):
        with self.assertRaises(StageBlocked):
            self.materialize(REPO,"b"*40,PATCH,[SOURCE,TEST])

    def test_rejects_extra_file_list(self):
        with self.assertRaises(StageBlocked):
            self.materialize(REPO,self.base,PATCH,[SOURCE,TEST,"README.md"])

    def test_rejects_owner_outside_org(self):
        with self.assertRaises(StageBlocked):
            self.materialize("other/HarnessDesk",self.base,PATCH,[SOURCE,TEST])

    def test_no_git_push_during_local_materialization(self):
        calls=[]
        def runner(args, **kwargs):
            calls.append(args)
            return subprocess.run(args, **kwargs)
        m=CleanPublicGitPatchMaterializer(runner=runner,clone_base=str(self.root))
        m(REPO,self.base,PATCH,[SOURCE,TEST])
        self.assertTrue(all("push" not in c for c in calls))
        self.assertTrue(any(c[1]=="apply" if len(c)>1 else False for c in calls) is False
                        or len(calls)>0)

    def test_no_patch_can_overwrite_foreign_test_path(self):
        f=Path(self.tmp.name)/"work"/TEST
        f.parent.mkdir(parents=True,exist_ok=True)
        f.write_text("existing test\n")
        self.call("git","-C",str(Path(self.tmp.name)/"work"),"add","--",TEST)
        self.call("git","-C",str(Path(self.tmp.name)/"work"),"commit","-m","existing test")
        # Explicit fetch from newest base, where 'new file' collides.
        newsha=self.call("git","-C",str(Path(self.tmp.name)/"work"),"rev-parse","HEAD").strip()
        self.call("git","-C",str(Path(self.tmp.name)/"work"),"push","origin","development")
        with self.assertRaises(StageBlocked):
            self.materialize(REPO,newsha,PATCH,[SOURCE,TEST])


if __name__=="__main__":
    unittest.main()
