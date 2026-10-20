"""Offline verified boundary tests: two-file contributor stage has no live writer."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from connected_multifile_stage import prepare_exact_two_file_patch, StageBlocked

SOURCE = "HarnessDesk/HarnessDesk"
FORK = "opensiro-contributions/HarnessDesk"
BASE = "a" * 40
FINAL = "b" * 40
SRC = "packages/server/src/tool-gateway.ts"
TEST = "packages/server/test/tool-gateway-ownership.test.ts"
OLD = "export const old = 1\n"
NEW = "export const old = 2\n"
ADDED = "assert(true)\n"


def digest(s):
    return hashlib.sha256(s.encode()).hexdigest()


PATCH = (
    f"diff --git a/{SRC} b/{SRC}\n"
    f"--- a/{SRC}\n+++ b/{SRC}\n@@ -1 +1 @@\n"
    "-export const old = 1\n+export const old = 2\n"
    f"diff --git a/{TEST} b/{TEST}\n"
    "new file mode 100644\n"
    f"--- /dev/null\n+++ b/{TEST}\n@@ -0,0 +1 @@\n+assert(true)\n"
)


def manifest_data():
    return {"schema_version": 1, "batch_id": "upstream-20261020-gateway",
            "revision": 1, "status": "proposal_only", "candidates": [{
                "id": "harnessdesk-1772", "source": SOURCE, "fork_name": "HarnessDesk",
                "stages": ["prepare_contribution"], "expected_license": "MIT",
                "proposal": {
                    "system_component": "ToolGateway Unix socket ownership",
                    "problem": "Duplicate homes could unlink live socket owners",
                    "planned_change": "Implement ownership-safe gateway startup and stop",
                    "expected_improvement": "Protect original live tool connections",
                    "validation": "Node tests on pinned source and two operating systems",
                    "evidence_url": "https://github.com/HarnessDesk/HarnessDesk/issues/1772"},
                "blockers": []}]}


def action():
    return {
        "working_repo": FORK, "source_branch": "development", "source_sha": BASE,
        "base_branch": "development", "base_sha": BASE,
        "new_branch": "opensiro/fix-toolgateway-1772",
        "patch_text": PATCH, "patch_sha256": digest(PATCH),
        "changed_paths": [SRC, TEST],
        "preimage_sha256": {SRC: digest(OLD)},
        "postimage_sha256": {SRC: digest(NEW), TEST: digest(ADDED)},
    }


class Grant:
    pass


class FakeHost:
    def __init__(self):
        self.allow = True
        self.batches = []
        self.stages = []
        self.on_batch = lambda: None
        self.on_stage = lambda: None

    def verify_exact_prepare(self, intent):
        self.batches.append(intent)
        self.on_batch()
        return Grant() if self.allow else None

    def authorize_exact_stage(self, grant, intent):
        self.stages.append((grant, intent))
        self.on_stage()
        return self.allow


class FakePort:
    def __init__(self):
        self.calls = []
        self.actor = "xLagerFeuer"
        self.source_sha = BASE
        self.work_sha = BASE
        self.new_branch = False
        self.bad_parent = False
        self.bad_license = False
        self.bad_push = False
        self.bad_preimage = False
        self.test_exists = False
        self.rights = True
        self.post_exception = False
        self.commit_parents = [BASE]
        self.commit_paths = [SRC, TEST]
        self.bad_postimage = False
        self.bad_receipt = False
        self.readback_sha = FINAL

    def repo(self, name):
        self.calls.append(("repo", name))
        if name == SOURCE:
            return {"full_name": SOURCE, "private": False, "archived": False,
                    "license": {"spdx_id": "Apache-2.0" if self.bad_license else "MIT"}}
        if name == FORK:
            return {"full_name": FORK, "private": False, "archived": False,
                    "fork": True, "parent": {
                        "full_name": "other/source" if self.bad_parent else SOURCE},
                    "permissions": {"push": not self.bad_push}}
        raise RuntimeError("Unexpected repo")

    def branch(self, repo, name):
        self.calls.append(("branch", repo, name))
        if name == "development":
            return {"sha": self.source_sha if repo == SOURCE else self.work_sha}
        if name == "opensiro/fix-toolgateway-1772" and self.new_branch:
            return {"sha": self.readback_sha}
        from connected_multifile_stage import NotFound
        raise NotFound()

    def file(self, repo, path, branch):
        self.calls.append(("file", repo, path, branch))
        if branch == "development" and path == SRC:
            return {"content": "wrong\n" if self.bad_preimage else OLD}
        if branch == "development" and path == TEST and self.test_exists:
            return {"content": "present\n"}
        if branch == "opensiro/fix-toolgateway-1772" and self.new_branch:
            if path == SRC:
                return {"content": OLD if self.bad_postimage else NEW}
            if path == TEST:
                return {"content": ADDED}
        from connected_multifile_stage import NotFound
        raise NotFound()

    def patch_capability(self, owner):
        self.calls.append(("patch_capability", owner))
        return {"owner": owner, "actor": self.actor, "available": self.rights,
                "authorized": self.rights}

    def publish_patch_commit(self, repo, base_sha, branch, patch_text, paths, sha_map):
        self.calls.append(("publish_patch_commit", repo, base_sha, branch,
                           digest(patch_text), paths, sha_map))
        if self.post_exception:
            raise RuntimeError("ambiguous")
        self.new_branch = True
        return {"commit_sha": "wrong" if self.bad_receipt else FINAL}

    def commit(self, repo, sha):
        self.calls.append(("commit", repo, sha))
        return {"parents": self.commit_parents, "changed_paths": self.commit_paths}

    def writes(self):
        return [c for c in self.calls if c[0] == "publish_patch_commit"]


class TestTwoFileStage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "upstream-20261020-gateway.json"
        self.data = manifest_data()
        self.save()
        self.port = FakePort()
        self.host = FakeHost()
        self.intent = action()

    def save(self):
        self.path.write_text(json.dumps(self.data))

    def run_stage(self, **kwargs):
        params = dict(manifest=self.path, selected_ids=["harnessdesk-1772"],
                      stage_scopes={"harnessdesk-1772": ["prepare_contribution"]},
                      candidate_id="harnessdesk-1772", action=self.intent,
                      github=self.port, host=self.host)
        params.update(kwargs)
        return prepare_exact_two_file_patch(**params)

    def test_verified_single_atomic_patch_write(self):
        r = self.run_stage()
        self.assertEqual(r["status"], "PREPARED_VERIFIED")
        self.assertEqual(len(self.port.writes()), 1)
        self.assertEqual(r["commit_sha"], FINAL)
        self.assertFalse(r["auto_retry"])
        self.assertEqual(self.host.batches[0]["patch_sha256"], digest(PATCH))
        self.assertEqual(self.host.stages[0][1]["changed_paths"], [SRC, TEST])
        self.assertNotIn("patch_text", self.host.batches[0])

    def test_no_provider_or_host_no_write(self):
        for what in ({"host": None}, {"github": None}):
            with self.subTest(what=what), self.assertRaises(StageBlocked):
                self.run_stage(**what)
        self.assertEqual(self.port.writes(), [])

    def test_missing_host_method_fails(self):
        with self.assertRaises(StageBlocked):
            self.run_stage(host=object())
        self.assertEqual(self.port.writes(), [])

    def test_grant_must_be_opaque_and_not_manifest(self):
        self.host.verify_exact_prepare = lambda intent: {"approved": True}
        with self.assertRaisesRegex(StageBlocked, "opaque"):
            self.run_stage()
        self.assertEqual(self.port.writes(), [])

    def test_denied_host_batch(self):
        self.host.allow = False
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.port.writes(), [])

    def test_host_stage_denial(self):
        self.host.authorize_exact_stage = lambda grant, intent: False
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.port.writes(), [])

    def test_source_license_drift(self):
        self.port.bad_license = True
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.port.writes(), [])

    def test_source_sha_drift(self):
        self.port.source_sha = FINAL
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.port.writes(), [])

    def test_fork_behind_upstream_no_write(self):
        self.intent["base_sha"] = "c" * 40
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.port.writes(), [])

    def test_realistic_stale_fork_read_prevents_write(self):
        self.port.work_sha = "c" * 40
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.port.writes(), [])

    def test_existing_branch_collision(self):
        self.port.new_branch = True
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.port.writes(), [])

    def test_existing_test_collision(self):
        self.port.test_exists = True
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.port.writes(), [])

    def test_wrong_fork_parent(self):
        self.port.bad_parent = True
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.port.writes(), [])

    def test_no_push_permission(self):
        self.port.bad_push = True
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.port.writes(), [])

    def test_no_provider_capability(self):
        self.port.rights = False
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.port.writes(), [])

    def test_preimage_mismatch(self):
        self.port.bad_preimage = True
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.port.writes(), [])

    def test_patch_checksum_mismatch_before_any_get(self):
        self.intent["patch_sha256"] = "d" * 64
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.port.calls, [])

    def test_patch_unapproved_extra_path(self):
        self.intent["patch_text"] += ("diff --git a/README.md b/README.md\n"
                                      "--- a/README.md\n+++ b/README.md\n")
        self.intent["patch_sha256"] = digest(self.intent["patch_text"])
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.port.calls, [])

    def test_path_traversal_or_non_source_not_allowed(self):
        for value in ("packages/server/src/../test/file.ts",
                      "README.md", "packages/server/src/evil.sh",
                      "packages/server/src/.lock", "packages/server/foo/file.ts"):
            self.intent = action()
            self.intent["changed_paths"][0] = value
            with self.subTest(value=value), self.assertRaises(StageBlocked):
                self.run_stage()
        self.assertEqual(self.port.calls, [])

    def test_missing_new_file_header_rejected(self):
        self.intent["patch_text"] = self.intent["patch_text"].replace(
            "new file mode 100644\n", "")
        self.intent["patch_sha256"] = digest(self.intent["patch_text"])
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.port.calls, [])

    def test_unexpected_existing_source_preimage_bound(self):
        self.intent["preimage_sha256"][SRC] = "d" * 64
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.port.writes(), [])

    def test_stage_not_selected_fails(self):
        with self.assertRaises(StageBlocked):
            self.run_stage(stage_scopes={"harnessdesk-1772": ["submit_external_pr"]})
        self.assertEqual(self.port.writes(), [])

    def test_existing_blockers_halt_before_permission(self):
        self.data["candidates"][0]["blockers"] = ["External contributor branch not approved"]
        self.save()
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.port.writes(), [])

    def test_proposal_mutates_at_batch_approval(self):
        def mutate():
            self.data["candidates"][0]["proposal"]["problem"] = (
                "Something else that was edited while approval was pending")
            self.save()
        self.host.on_batch = mutate
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.port.writes(), [])

    def test_provider_base_drift_after_grant(self):
        self.host.on_stage = lambda: setattr(self.port, "work_sha", FINAL)
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.port.writes(), [])

    def test_action_mutates_at_grant(self):
        self.host.on_batch = lambda: self.intent.update({"base_sha": "c" * 40})
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.port.writes(), [])

    def test_writer_throws_unknown_and_never_retries(self):
        self.port.post_exception = True
        r = self.run_stage()
        self.assertEqual(r["status"], "UNKNOWN_AFTER_WRITE")
        self.assertEqual(len(self.port.writes()), 1)
        self.assertFalse(r["auto_retry"])

    def test_bad_commit_receipt_no_auto_retry(self):
        self.port.bad_receipt = True
        r = self.run_stage()
        self.assertEqual(r["status"], "PENDING_VERIFICATION")
        self.assertEqual(len(self.port.writes()), 1)

    def test_remote_parent_wrong_blocks_verified(self):
        self.port.commit_parents = ["c" * 40]
        self.assertEqual(self.run_stage()["status"], "PENDING_VERIFICATION")

    def test_remote_file_bytes_wrong_blocks_verified(self):
        self.port.bad_postimage = True
        self.assertEqual(self.run_stage()["status"], "PENDING_VERIFICATION")

    def test_remote_changed_paths_wrong_blocks_verified(self):
        self.port.commit_paths = [SRC, "README.md"]
        self.assertEqual(self.run_stage()["status"], "PENDING_VERIFICATION")

    def test_remote_branch_sha_mismatch_blocks_verified(self):
        self.port.readback_sha = "c" * 40
        self.assertEqual(self.run_stage()["status"], "PENDING_VERIFICATION")

    def test_actual_v2_patch_diff_parser_and_pinned_sha(self):
        file = ROOT / "pilots/harnessdesk-1772/tool-gateway-ownership-fix-v2.patch"
        text = file.read_text(encoding="utf-8")
        actual = self.intent
        actual["patch_text"] = text
        actual["patch_sha256"] = digest(text)
        self.assertEqual(actual["patch_sha256"],
                         "12b5c7e55a6f730fb9a2465ca30dd47321690c87c0d887e7b8c9d6990ec186e7")
        from connected_multifile_stage import _validate
        _validate(actual)
        self.assertEqual(self.port.writes(), [])

    def test_no_external_pr_capability_is_ever_needed(self):
        self.run_stage()
        self.assertTrue(all(c[0] != "create_pull_request" for c in self.port.calls))


if __name__ == "__main__":
    unittest.main()
