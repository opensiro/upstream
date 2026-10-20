"""Offline tests: GitHub REST Git Data two-file atomic ref writer (no live PAT)."""
import base64
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from rest_multifile_patch_port import GitHubRESTMultifilePatchPort, StageBlocked, NotFound
from connected_multifile_stage import digest

REPO = "opensiro-contributions/HarnessDesk"
BASE = "a" * 40
TREE = "b" * 40
NEXT_TREE = "c" * 40
NEW = "d" * 40
BRANCH = "opensiro/fix-toolgateway-1772"
SRC = "packages/server/src/tool-gateway.ts"
TEST = "packages/server/test/tool-gateway-ownership.test.ts"
PATCH = "diff --git a/src b/src\nmock local patch\n"
FILES = {SRC: "const fixed = true\n", TEST: "assert(true)\n"}
POST = {k: digest(v) for k, v in FILES.items()}


class FakeAPI:
    def __init__(self):
        self.calls = []
        self.forced = {}
        self.target_exists = False
        self.ref_object = NEW
        self.changed = [SRC, TEST]
        self.parent = BASE
        self.target_files = dict(FILES)

    def __call__(self, method, path, body=None):
        self.calls.append((method, path, body))
        if (method, path) in self.forced:
            return self.forced[(method, path)]
        if method == "GET" and path == "repos/" + REPO:
            return (200, {"full_name": REPO, "private": False})
        if method == "GET" and path == "repos/" + REPO + "/branches/" + BRANCH.replace("/", "%2F"):
            return (200, {"commit": {"sha": NEW}}) if self.target_exists else (404, {"message":"Not Found"})
        if method == "GET" and path == "repos/" + REPO + "/branches/development":
            return (200, {"commit": {"sha": BASE}})
        if method == "GET" and "/contents/" in path:
            objpath = path.split("/contents/", 1)[1].split("?",1)[0]
            from urllib.parse import unquote
            objpath = unquote(objpath)
            if objpath not in self.target_files:
                return (404, {"message": "Not Found"})
            value = self.target_files[objpath]
            return (200, {"type":"file", "encoding":"base64",
                          "content": base64.b64encode(value.encode()).decode()})
        if method == "GET" and path == "repos/" + REPO + "/commits/" + NEW:
            return (200, {"parents": [{"sha": self.parent}],
                          "files": [{"filename": f} for f in self.changed]})
        if method == "GET" and path == "repos/" + REPO + "/git/commits/" + BASE:
            return (200, {"tree": {"sha": TREE}})
        if method == "POST" and path == "repos/" + REPO + "/git/trees":
            return (201, {"sha": NEXT_TREE})
        if method == "POST" and path == "repos/" + REPO + "/git/commits":
            return (201, {"sha": NEW})
        if method == "POST" and path == "repos/" + REPO + "/git/refs":
            self.target_exists = True
            return (201, {"ref": "refs/heads/" + BRANCH,
                          "object": {"sha": self.ref_object}})
        raise AssertionError("Unexpected API call: " + repr((method, path)))

    def writes(self):
        return [r for r in self.calls if r[0] == "POST"]


class TestGitHubRESTMultifilePatchPort(unittest.TestCase):
    def setUp(self):
        self.api = FakeAPI()
        self.material = []
        self.rights = True
        self.materialized = dict(FILES)
        self.attestation = {"base_sha": BASE, "changed_paths": [SRC, TEST],
                            "source_file_modes": {SRC: "100644", TEST: "100644"},
                            "files": self.materialized}
        def materialize(repo, sha, patch, paths):
            self.material.append((repo, sha, patch, paths))
            return self.attestation
        def attest(owner):
            return {"owner": owner, "actor": "xLagerFeuer",
                    "available": self.rights, "authorized": self.rights}
        self.port = GitHubRESTMultifilePatchPort(
            api=self.api, materializer=materialize, capability_attestor=attest)

    def publish(self):
        return self.port.publish_patch_commit(
            REPO, BASE, BRANCH, PATCH, [SRC, TEST], POST)

    def test_single_atomic_branch_reference_created_last(self):
        result = self.publish()
        self.assertEqual(result["commit_sha"], NEW)
        ops = [x[1].split("/")[-2:] for x in self.api.writes()]
        self.assertEqual(ops, [["git", "trees"], ["git", "commits"], ["git", "refs"]])
        self.assertEqual(self.api.writes()[-1][2],
                         {"ref": "refs/heads/" + BRANCH, "sha": NEW})
        self.assertEqual(len(self.material), 1)

    def test_commit_parent_pinned_and_exact_diff_tree(self):
        self.publish()
        writes = self.api.writes()
        self.assertEqual(writes[0][2]["base_tree"], TREE)
        self.assertEqual([x["path"] for x in writes[0][2]["tree"]], [SRC, TEST])
        self.assertTrue(all(x["mode"]=="100644" for x in writes[0][2]["tree"]))
        self.assertEqual(writes[1][2]["parents"], [BASE])
        self.assertEqual(writes[1][2]["tree"], NEXT_TREE)

    def test_invalid_credentials_surface_unavailable(self):
        self.rights = False
        with self.assertRaises(StageBlocked):
            self.port.patch_capability("opensiro-contributions")
        self.assertEqual(self.api.writes(), [])

    def test_permission_owner_locked(self):
        with self.assertRaises(StageBlocked):
            self.port.patch_capability("opensiro")
        self.assertEqual(self.api.calls, [])

    def test_attestor_actor_identity(self):
        p = self.port.patch_capability("opensiro-contributions")
        self.assertEqual(p["actor"], "xLagerFeuer")

    def test_absent_branch_is_only_404(self):
        with self.assertRaises(NotFound):
            self.port.branch(REPO, BRANCH)
        self.api.forced[("GET","repos/"+REPO+"/branches/"+BRANCH.replace("/","%2F"))] = (403, {"message":"Forbidden"})
        with self.assertRaises(StageBlocked):
            self.port.branch(REPO, BRANCH)

    def test_existing_branch_blocks_before_materialization(self):
        self.api.target_exists = True
        with self.assertRaises(StageBlocked):
            self.publish()
        self.assertEqual(self.material, [])
        self.assertEqual(self.api.writes(), [])

    def test_materializer_changed_paths_rejected_before_post(self):
        self.attestation["changed_paths"] = [SRC, "README.md"]
        with self.assertRaises(StageBlocked):
            self.publish()
        self.assertEqual(self.api.writes(), [])

    def test_materializer_mode_rejected_before_post(self):
        self.attestation["source_file_modes"][SRC] = "100755"
        with self.assertRaises(StageBlocked):
            self.publish()
        self.assertEqual(self.api.writes(), [])

    def test_materializer_content_mismatch_rejected(self):
        self.materialized[SRC] = "corrupted\n"
        with self.assertRaises(StageBlocked):
            self.publish()
        self.assertEqual(self.api.writes(), [])

    def test_materializer_missing_file_rejected(self):
        del self.materialized[TEST]
        with self.assertRaises(StageBlocked):
            self.publish()
        self.assertEqual(self.api.writes(), [])

    def test_wrong_repo_owner_rejected_before_read(self):
        with self.assertRaises(StageBlocked):
            self.port.publish_patch_commit("personal/HarnessDesk",BASE,BRANCH,PATCH,[SRC,TEST],POST)
        self.assertEqual(self.api.calls, [])

    def test_invalid_new_branch_rejected_before_read(self):
        with self.assertRaises(StageBlocked):
            self.port.publish_patch_commit(REPO,BASE,"features/bad",PATCH,[SRC,TEST],POST)
        self.assertEqual(self.api.calls, [])

    def test_tree_post_403_stops_before_commit_and_ref(self):
        self.api.forced[("POST","repos/"+REPO+"/git/trees")] = (403, {"message":"denied"})
        with self.assertRaises(StageBlocked):
            self.publish()
        self.assertEqual(len(self.api.writes()), 1)

    def test_commit_post_failure_no_branch_creation(self):
        self.api.forced[("POST","repos/"+REPO+"/git/commits")] = (422, {"message":"denied"})
        with self.assertRaises(StageBlocked):
            self.publish()
        self.assertEqual(len(self.api.writes()), 2)
        self.assertFalse(self.api.target_exists)

    def test_ref_collision_no_overwrite_or_retry(self):
        self.api.forced[("POST","repos/"+REPO+"/git/refs")] = (422, {"message":"exists"})
        with self.assertRaises(StageBlocked):
            self.publish()
        self.assertEqual(len(self.api.writes()), 3)
        self.assertFalse(self.api.target_exists)

    def test_ref_wrong_sha_rejected(self):
        self.api.ref_object = "e" * 40
        with self.assertRaises(StageBlocked):
            self.publish()
        self.assertEqual(len(self.api.writes()), 3)

    def test_base_commit_malformed_stops_before_post(self):
        self.api.forced[("GET","repos/"+REPO+"/git/commits/"+BASE)] = (200, {"tree":{"sha":"wrong"}})
        with self.assertRaises(StageBlocked):
            self.publish()
        self.assertEqual(self.api.writes(), [])

    def test_exact_external_commit_readback(self):
        actual = self.port.commit(REPO, NEW)
        self.assertEqual(actual["parents"], [BASE])
        self.assertEqual(actual["changed_paths"], [SRC, TEST])

    def test_commit_inventory_truncated_rejected(self):
        self.api.changed = [str(i) for i in range(300)]
        with self.assertRaises(StageBlocked):
            self.port.commit(REPO, NEW)

    def test_base64_file_readback_and_wrong_base64(self):
        self.assertEqual(self.port.file(REPO, SRC, BRANCH)["content"],FILES[SRC])
        key=("GET","repos/"+REPO+"/contents/"+SRC+"?ref="+BRANCH.replace("/", "%2F"))
        self.api.forced[key]=(200, {"type":"file","encoding":"base64","content":"?"})
        with self.assertRaises(StageBlocked):
            self.port.file(REPO,SRC,BRANCH)

    def test_transport_wrong_shape_fails_closed(self):
        self.api.forced[("GET","repos/"+REPO)]=(200, [])
        with self.assertRaises(StageBlocked):
            self.port.repo(REPO)

    def test_duplicate_file_paths_rejected(self):
        with self.assertRaises(StageBlocked):
            self.port.publish_patch_commit(REPO,BASE,BRANCH,PATCH,[SRC,SRC],POST)
        self.assertEqual(self.api.calls, [])

    def test_no_input_api_or_local_materializer_rejected(self):
        for args in (dict(api=self.api,materializer=None,capability_attestor=lambda o: {}),
                     dict(api=None,materializer=lambda *x: {},capability_attestor=lambda o: {})):
            with self.assertRaises(StageBlocked):
                GitHubRESTMultifilePatchPort(**args)


if __name__ == "__main__":
    unittest.main()
