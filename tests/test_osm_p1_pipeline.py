"""End-to-end mock-only preview: proposal → P1 grant scope → repo preflight."""
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
import tempfile
import unittest
from copy import deepcopy

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from connected_stage_adapter import NotFound
from osm_p1_scope import digest
from osm_p1_pipeline import PipelineBlocked, preview_p1_pipeline


BASE_SHA = "a" * 40


def manifest():
    return {
        "schema_version": 1, "batch_id": "upstream-20261019-example",
        "revision": 1, "status": "proposal_only",
        "candidates": [{
            "id": "edge-regression", "source": "target/source", "fork_name": "source",
            "stages": ["create_public_fork", "prepare_contribution", "submit_external_pr"],
            "expected_license": "MIT",
            "proposal": {
                "system_component": "Graph adapter regression contract",
                "problem": "One edge check returns a Boolean instead of identity",
                "planned_change": "Add deterministic triple identity regression test",
                "expected_improvement": "Early failure for the wrong result structure",
                "validation": "Run the appropriate isolated test suite",
                "evidence_url": "https://github.com/target/source/issues/19",
            }, "blockers": [],
        }],
    }


def action():
    return {
        "working_repo": "worker/source", "base_branch": "main",
        "base_sha": BASE_SHA, "new_branch": "opensiro/edge-contract",
        "file_path": "tests/test_edge_contract.py", "content": "assert True\n",
    }


def grant():
    return {
        "schema_version": 1, "kind": "UPSTREAM_LOCAL_P1", "status": "ISSUED",
        "grant_id": "sample-upstream-grant", "issuer": "worker/source",
        "recipient_execution_id": "agent-runtime-001",
        "working_repositories": ["worker/source"], "branch_prefix": "opensiro/",
        "path_prefixes": ["tests/"], "allowed_stage": "prepare_contribution",
        "valid_from": "2026-10-19T10:00:00Z",
        "valid_until": "2026-10-20T10:00:00Z",
    }


class FakeHost:
    def __init__(self, g):
        self.g = deepcopy(g)
        self.actor = g["recipient_execution_id"]
        self.revoked = False
        self.valid_digest = digest(g)

    def actor_identity(self):
        return self.actor

    def utcnow(self):
        return datetime(2026, 10, 19, 12, tzinfo=timezone.utc)

    def verify_owner_grant(self, ignored_digest):
        return {
            "grant_digest": self.valid_digest,
            "issuer": self.g["issuer"], "recipient": self.actor,
            "active": True, "revoked": self.revoked,
        }


class FakeGitHub:
    def __init__(self):
        self.calls = []
        self.base_sha = BASE_SHA
        self.license = "MIT"
        self.push = True
        self.parent = "target/source"
        self.existing_branch = False
        self.existing_file = False

    def repo(self, name):
        self.calls.append(("repo", name))
        if name == "target/source":
            return {"full_name": name, "private": False, "archived": False,
                    "license": {"spdx_id": self.license}}
        return {"full_name": name, "private": False, "archived": False,
                "fork": True, "parent": {"full_name": self.parent},
                "permissions": {"push": self.push}}

    def branch(self, repo, name):
        self.calls.append(("branch", repo, name))
        if name == "main":
            return {"sha": self.base_sha}
        if self.existing_branch:
            return {"sha": BASE_SHA}
        raise NotFound()

    def file(self, repo, path, branch):
        self.calls.append(("file", repo, path, branch))
        if self.existing_file:
            return {"content": "already committed"}
        raise NotFound()

    def create_branch(self, *args):
        raise AssertionError("NO WRITE PATH ALLOWED")

    def create_file(self, *args):
        raise AssertionError("NO WRITE PATH ALLOWED")


class P1PipelineTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.path = Path(t.name) / "upstream-20261019-example.json"
        self.draft = manifest()
        self.save()
        self.action = action()
        self.grant = grant()
        self.host = FakeHost(self.grant)
        self.github = FakeGitHub()

    def save(self):
        self.path.write_text(json.dumps(self.draft), encoding="utf-8")

    def preview(self, **overrides):
        values = dict(manifest=self.path, candidate_id="edge-regression",
                      action=self.action, grant=self.grant,
                      trusted_host=self.host, github=self.github)
        values.update(overrides)
        return preview_p1_pipeline(**values)

    def blocked(self, **overrides):
        with self.assertRaises(PipelineBlocked):
            self.preview(**overrides)

    def test_mock_happy_path_is_explicitly_non_executable(self):
        result = self.preview()
        self.assertEqual(result["status"], "PIPELINE_PREVIEW_ONLY_NO_GITHUB_WRITES")
        self.assertFalse(result["can_execute"])
        self.assertEqual(result["p1_scope_precheck"],
                         "SCOPE_PRECHECK_ONLY_NOT_A_WRITE_AUTHORIZATION")
        self.assertEqual(result["working_repo"], "worker/source")
        self.assertEqual(result["base_sha"], BASE_SHA)
        self.assertIn("content_sha256", result)
        self.assertNotIn("content", result)
        self.assertTrue(self.github.calls)
        self.assertEqual({x[0] for x in self.github.calls}, {"repo", "branch", "file"})

    def test_missing_host_stops_without_provider_reads(self):
        self.blocked(trusted_host=None)
        self.assertEqual(self.github.calls, [])

    def test_missing_github_stops(self):
        self.blocked(github=None)

    def test_unissued_grant_stops_without_provider_reads(self):
        g = deepcopy(self.grant)
        g["status"] = "PROPOSED_NOT_GRANTED"
        self.blocked(grant=g)
        self.assertEqual(self.github.calls, [])

    def test_revocation_stops_without_provider_reads(self):
        self.host.revoked = True
        self.blocked()
        self.assertEqual(self.github.calls, [])

    def test_wrong_execution_actor_stops(self):
        self.host.actor = "someone-else"
        self.blocked()
        self.assertEqual(self.github.calls, [])

    def test_unauthorized_fork_stops(self):
        a = deepcopy(self.action)
        a["working_repo"] = "other/source"
        self.blocked(action=a)
        self.assertEqual(self.github.calls, [])

    def test_upstream_source_mismatch_stops(self):
        self.github.parent = "unrelated/upstream"
        self.blocked()

    def test_source_license_changed_stops(self):
        self.github.license = "Apache-2.0"
        self.blocked()

    def test_not_writable_fork_stops(self):
        self.github.push = False
        self.blocked()

    def test_base_drift_stops(self):
        self.github.base_sha = "f" * 40
        self.blocked()

    def test_branch_collision_stops(self):
        self.github.existing_branch = True
        self.blocked()

    def test_file_collision_stops(self):
        self.github.existing_file = True
        self.blocked()

    def test_unreviewed_candidate_stops(self):
        self.draft["candidates"][0]["blockers"] = ["Needs contributor review"]
        self.save()
        self.blocked()
        self.assertEqual(self.github.calls, [])

    def test_submission_stage_not_delegated(self):
        self.grant["allowed_stage"] = "submit_external_pr"
        self.blocked()

    def test_source_file_outside_local_allowlist_stops(self):
        a = deepcopy(self.action)
        a["file_path"] = "src/graph.py"
        self.blocked(action=a)
        self.assertEqual(self.github.calls, [])

    def test_proposal_still_read_only_when_selected(self):
        result = self.preview()
        self.assertEqual(result["stage"], "prepare_contribution")
        self.assertFalse(result["can_execute"])
        self.assertFalse(hasattr(self.github, "created_branch"))

    def test_untrusted_approval_field_in_manifest_stops(self):
        self.draft["approved_by"] = "fake"
        self.save()
        self.blocked()
        self.assertEqual(self.github.calls, [])


if __name__ == "__main__":
    unittest.main()
