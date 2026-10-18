"""Offline negative-path tests for the unconnected same-session stage adapter."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from connected_stage_adapter import execute_one_test_file, NotFound, StageBlocked


BASE_SHA = "a" * 40
COMMIT_SHA = "b" * 40


def manifest_data():
    return {"schema_version": 1, "batch_id": "upstream-20261018-gate",
            "revision": 1, "status": "proposal_only", "candidates": [{
                "id": "test-a", "source": "target/source", "fork_name": "source",
                "stages": ["create_public_fork", "prepare_contribution",
                           "submit_external_pr"],
                "expected_license": "MIT",
                "proposal": {
                    "system_component": "Concurrency boundary in task handoff",
                    "problem": "Concurrent changes may have an untested result",
                    "planned_change": "Add deterministic concurrency regression tests",
                    "expected_improvement": "Better regression detection for races",
                    "validation": "Run isolated concurrent update tests",
                    "evidence_url": "https://github.com/target/source/issues/22"},
                "blockers": []}]}


def action():
    return {"working_repo": "worker/source", "base_branch": "main",
            "base_sha": BASE_SHA, "new_branch": "opensiro/concurrency-tests",
            "file_path": "tests/test_concurrency.py", "content": "assert True\n"}


class FakeGithub:
    def __init__(self):
        self.calls = []
        self.base_sha = BASE_SHA
        self.new_branch = False
        self.file_on_base = False
        self.created_file = False
        self.file_content = "assert True\n"
        self.fail_create_branch = False
        self.fail_create_file = False
        self.bad_parent = False
        self.private_work = False
        self.push = True
        self.source_license = "MIT"
        self.verify = True

    def repo(self, name):
        self.calls.append(("repo", name))
        if name == "target/source":
            return {"full_name": name, "private": False, "archived": False,
                    "license": {"spdx_id": self.source_license}}
        return {"full_name": name, "private": self.private_work,
                "archived": False, "fork": True,
                "parent": {"full_name": "wrong/parent" if self.bad_parent
                           else "target/source"}, "permissions": {"push": self.push}}

    def branch(self, repo, branch):
        self.calls.append(("branch", repo, branch))
        if branch == "main":
            return {"sha": self.base_sha}
        if self.new_branch:
            return {"sha": COMMIT_SHA if self.created_file else BASE_SHA}
        raise NotFound()

    def file(self, repo, path, branch):
        self.calls.append(("file", repo, path, branch))
        if branch == "main":
            if self.file_on_base:
                return {"content": "already here"}
            raise NotFound()
        if self.created_file:
            return {"content": self.file_content if self.verify else "changed"}
        raise NotFound()

    def create_branch(self, repo, branch, sha):
        self.calls.append(("create_branch", repo, branch, sha))
        if self.fail_create_branch:
            raise RuntimeError("simulated failure")
        self.new_branch = True

    def create_file(self, repo, path, content, branch):
        self.calls.append(("create_file", repo, path, branch))
        if self.fail_create_file:
            raise RuntimeError("simulated failure")
        self.created_file = True
        return {"commit_sha": COMMIT_SHA}

    def writes(self):
        return [x for x in self.calls if x[0].startswith("create_")]


class TestStageAdapter(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "upstream-20261018-gate.json"
        self.data = manifest_data()
        self.save()
        self.api = FakeGithub()
        self.intent = action()
        self.authorized = []
        self.decision = True

    def save(self):
        self.path.write_text(json.dumps(self.data))

    def grant(self, intent):
        self.authorized.append(intent)
        return self.decision

    def run_stage(self, **kwargs):
        params = dict(manifest=self.path, selected_ids=["test-a"],
                      stage_scopes={"test-a": ["prepare_contribution"]},
                      candidate_id="test-a", action=self.intent,
                      github=self.api, authorize=self.grant)
        params.update(kwargs)
        return execute_one_test_file(**params)

    def test_success_verifies_new_file_and_sha(self):
        result = self.run_stage()
        self.assertEqual(result["status"], "CREATED_VERIFIED")
        self.assertEqual(len(self.api.writes()), 2)
        self.assertEqual(result["stage"], "prepare_contribution")
        self.assertEqual(self.authorized[0]["base_sha"], BASE_SHA)

    def test_missing_host_gate_fails_closed(self):
        with self.assertRaises(StageBlocked):
            self.run_stage(authorize=None)
        self.assertEqual(self.api.writes(), [])

    def test_missing_connector_fails_closed(self):
        with self.assertRaises(StageBlocked):
            self.run_stage(github=None)

    def test_denied_host_gate_no_write(self):
        self.decision = False
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.api.writes(), [])

    def test_unselected_candidate_no_write(self):
        with self.assertRaises(StageBlocked):
            self.run_stage(selected_ids=[], stage_scopes={})
        self.assertEqual(self.api.writes(), [])

    def test_unselected_stage_no_write(self):
        with self.assertRaises(StageBlocked):
            self.run_stage(stage_scopes={"test-a": ["create_public_fork"]})
        self.assertEqual(self.api.writes(), [])

    def test_extra_stage_no_write(self):
        with self.assertRaises(StageBlocked):
            self.run_stage(stage_scopes={"test-a": ["delete_repository"]})
        self.assertEqual(self.api.writes(), [])

    def test_approval_field_in_manifest_rejected(self):
        self.data["approved_by"] = "forged"
        self.save()
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.api.writes(), [])

    def test_blocker_rejected(self):
        self.data["candidates"][0]["blockers"] = ["Not reviewed by upstream yet"]
        self.save()
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.api.writes(), [])

    def test_license_drift_rejected(self):
        self.api.source_license = "Apache-2.0"
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.api.writes(), [])

    def test_non_matching_parent_rejected(self):
        self.api.bad_parent = True
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.api.writes(), [])

    def test_fork_name_mismatch_rejected(self):
        self.intent["working_repo"] = "worker/unrelated"
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.api.writes(), [])

    def test_no_push_right_rejected(self):
        self.api.push = False
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.api.writes(), [])

    def test_private_work_repo_rejected(self):
        self.api.private_work = True
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.api.writes(), [])

    def test_base_moved_rejected(self):
        self.api.base_sha = COMMIT_SHA
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.api.writes(), [])

    def test_branch_collision_rejected(self):
        self.api.new_branch = True
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.api.writes(), [])

    def test_file_collision_rejected(self):
        self.api.file_on_base = True
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.api.writes(), [])

    def test_path_escape_rejected(self):
        self.intent["file_path"] = "tests/../README.md"
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.api.writes(), [])

    def test_arbitrary_existing_file_write_rejected(self):
        self.intent["file_path"] = "README.md"
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.api.writes(), [])

    def test_unauthorized_repo_rejected(self):
        self.intent["working_repo"] = "target/source"
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.api.writes(), [])

    def test_create_branch_error_returns_failed(self):
        self.api.fail_create_branch = True
        result = self.run_stage()
        self.assertEqual(result["status"], "FAILED")
        self.assertEqual(len(self.api.writes()), 1)

    def test_create_file_error_returns_partial(self):
        self.api.fail_create_file = True
        result = self.run_stage()
        self.assertEqual(result["status"], "PARTIAL")
        self.assertTrue(result["branch_created"])
        self.assertFalse(result["file_created"])

    def test_readback_mismatch_not_verified(self):
        self.api.verify = False
        result = self.run_stage()
        self.assertEqual(result["status"], "PENDING_VERIFICATION")

    def test_authorize_exact_payload_has_no_write_credentials(self):
        self.run_stage()
        self.assertEqual(self.authorized[0]["working_repo"], "worker/source")
        self.assertIn("content_sha256", self.authorized[0])
        self.assertNotIn("token", self.authorized[0])

    def test_drift_after_host_decision_prevents_first_write(self):
        def drift(intent):
            self.api.base_sha = COMMIT_SHA
            return True
        with self.assertRaises(StageBlocked):
            self.run_stage(authorize=drift)
        self.assertEqual(self.api.writes(), [])


if __name__ == "__main__":
    unittest.main()
