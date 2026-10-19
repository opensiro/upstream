"""Mock-only P1 grant scope contract checks; no genuine issuer or executor."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from osm_p1_scope import MandateBlocked, digest, preview_p1_scope


def fixture_grant():
    return {
        "schema_version": 1,
        "kind": "UPSTREAM_LOCAL_P1",
        "status": "ISSUED",
        "grant_id": "local-example-p1",
        "issuer": "opensiro/upstream",
        "recipient_execution_id": "runtime-agent-123",
        "working_repositories": ["opensiro/fictional-fork"],
        "branch_prefix": "opensiro/",
        "path_prefixes": ["tests/", "packages/graph/tests/"],
        "allowed_stage": "prepare_contribution",
        "valid_from": "2026-10-19T10:00:00Z",
        "valid_until": "2026-10-20T10:00:00Z",
    }


def fixture_intent():
    return {
        "stage": "prepare_contribution",
        "working_repo": "opensiro/fictional-fork",
        "branch": "opensiro/regression-test",
        "file_paths": ["tests/test_regression.py"],
        "external_publication": False,
    }


class FakeHost:
    def __init__(self, grant):
        self.grant = grant
        self.actor = grant["recipient_execution_id"]
        self.time = datetime(2026, 10, 19, 12, tzinfo=timezone.utc)
        self.active = True
        self.revoked = False
        self.grant_digest = digest(grant)

    def actor_identity(self):
        return self.actor

    def utcnow(self):
        return self.time

    def verify_owner_grant(self, proposed_digest):
        return {"grant_digest": self.grant_digest, "issuer": self.grant["issuer"],
                "recipient": self.actor, "active": self.active,
                "revoked": self.revoked}


class P1ScopeTests(unittest.TestCase):
    def setUp(self):
        self.grant = fixture_grant()
        self.intent = fixture_intent()
        self.host = FakeHost(self.grant)

    def check(self, *, grant=None, intent=None, host=None):
        return preview_p1_scope(
            self.grant if grant is None else grant,
            self.intent if intent is None else intent,
            trusted_host=self.host if host is None else host)

    def blocked(self, *, grant=None, intent=None, host=None):
        with self.assertRaises(MandateBlocked):
            self.check(grant=grant, intent=intent, host=host)

    def test_mock_scope_pass_does_not_claim_permission(self):
        result = self.check()
        self.assertEqual(result["status"], "SCOPE_PRECHECK_ONLY_NOT_A_WRITE_AUTHORIZATION")
        self.assertEqual(result["grant_digest"], digest(self.grant))
        self.assertNotIn("approved", result)

    def test_no_host_cannot_operate(self):
        with self.assertRaises(MandateBlocked):
            preview_p1_scope(self.grant, self.intent)

    def test_proposed_design_does_not_become_grant(self):
        d = deepcopy(self.grant)
        d["status"] = "PROPOSED_NOT_GRANTED"
        self.blocked(grant=d)

    def test_extra_approval_field_is_not_authority(self):
        d = deepcopy(self.grant)
        d["approved_by"] = "fake-owner"
        self.blocked(grant=d)

    def test_missing_or_fake_recipient_blocks(self):
        d = deepcopy(self.grant)
        d["recipient_execution_id"] = "UNSET"
        self.blocked(grant=d)

    def test_wrong_actor_blocks(self):
        self.host.actor = "other-runtime"
        self.blocked()

    def test_revocation_blocks(self):
        self.host.revoked = True
        self.blocked()

    def test_inactive_attestation_blocks(self):
        self.host.active = False
        self.blocked()

    def test_forged_digest_blocks(self):
        self.host.grant_digest = "0" * 64
        self.blocked()

    def test_wrong_issuer_blocks(self):
        self.host.grant["issuer"] = "someone/else"
        self.blocked()

    def test_expired_or_not_yet_effective_blocks(self):
        self.host.time = datetime(2026, 10, 20, 12, tzinfo=timezone.utc)
        self.blocked()
        self.host.time = datetime(2026, 10, 19, 9, tzinfo=timezone.utc)
        self.blocked()

    def test_unbounded_or_malformed_grant_term_blocks(self):
        for until in ("2027-10-20T10:00:00Z", "not-a-time", "2026-10-19T09:00:00Z"):
            d = deepcopy(self.grant)
            d["valid_until"] = until
            self.blocked(grant=d)

    def test_external_pr_or_other_stage_blocks(self):
        for stage in ("submit_external_pr", "create_public_fork"):
            intent = deepcopy(self.intent)
            intent["stage"] = stage
            self.blocked(intent=intent)
        intent = deepcopy(self.intent)
        intent["external_publication"] = True
        self.blocked(intent=intent)

    def test_outside_repository_blocks(self):
        intent = deepcopy(self.intent)
        intent["working_repo"] = "someone/other-fork"
        self.blocked(intent=intent)

    def test_default_branch_or_branch_traversal_blocks(self):
        for branch in ("main", "master", "opensiro/../escape",
                       "opensiro/ok//wrong", "opensiro/name.lock"):
            intent = deepcopy(self.intent)
            intent["branch"] = branch
            self.blocked(intent=intent)

    def test_outside_or_dangerous_file_path_blocks(self):
        for file_path in ("src/agent.py", "../secrets.txt",
                          ".github/workflows/ci.yml",
                          "tests/../src/agent.py", "tests\\evil.py"):
            intent = deepcopy(self.intent)
            intent["file_paths"] = [file_path]
            self.blocked(intent=intent)

    def test_empty_and_duplicate_file_scope_blocks(self):
        for paths in ([], ["tests/a.py", "tests/a.py"]):
            intent = deepcopy(self.intent)
            intent["file_paths"] = paths
            self.blocked(intent=intent)

    def test_missing_host_method_blocks(self):
        self.blocked(host=object())

    def test_host_error_blocks(self):
        self.host.verify_owner_grant = lambda _: (_ for _ in ()).throw(
            PermissionError("revocation status unavailable"))
        self.blocked()

    def test_package_test_path_can_match_scope(self):
        intent = deepcopy(self.intent)
        intent["file_paths"] = ["packages/graph/tests/test_edge.py"]
        result = self.check(intent=intent)
        self.assertEqual(result["working_repo"], "opensiro/fictional-fork")


if __name__ == "__main__":
    unittest.main()
