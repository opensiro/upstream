"""Offline tests of proposed bounded standing mandate; no real permission.

ACTIVE policies in tests are synthetic fixtures. The checked-in policy remains
PROPOSED_NOT_ACTIVE, so real preparation must fail closed.
"""
import base64
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import test_connected_multifile_stage as core_fixture
from batch_proposals import preview_draft
from connected_multifile_stage import prepare_exact_two_file_patch
from connected_stage_adapter import StageBlocked
from bounded_local_prepare_host import (
    BoundedLocalPrepareHost, CurrentMainMandateReader,
    POLICY_PATH, POLICY_REPO, BRANCH, PATHS, digest
)

class BoundedHostTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.manifest = Path(self.temp.name) / "upstream-20261020-gateway.json"
        self.manifest.write_text(json.dumps(core_fixture.manifest_data()))
        self.action = core_fixture.action()
        self.action["fork_observed_sha"] = "c" * 40
        self.github = core_fixture.FakePort()
        self.github.work_sha = "c" * 40
        self.selection = ["harnessdesk-1772"]
        self.scopes = {"harnessdesk-1772": ["prepare_contribution"]}
        preview = preview_draft(self.manifest, selected_ids=self.selection,
                                stage_scopes=self.scopes)
        self.intent = {
            "stage": "prepare_contribution",
            "candidate_id": "harnessdesk-1772",
            "source": "HarnessDesk/HarnessDesk",
            "proposal_sha256": preview["proposal_sha256"],
            "selection_scope_sha256": preview["selection_scope_sha256"],
            "actor": "xLagerFeuer",
            "working_repo": self.action["working_repo"],
            "source_branch": self.action["source_branch"],
            "source_sha": self.action["source_sha"],
            "base_branch": self.action["base_branch"],
            "base_sha": self.action["base_sha"],
            "new_branch": self.action["new_branch"],
            "fork_observed_sha": self.action["fork_observed_sha"],
            "patch_sha256": self.action["patch_sha256"],
            "changed_paths": self.action["changed_paths"],
            "preimage_sha256": self.action["preimage_sha256"],
            "postimage_sha256": self.action["postimage_sha256"],
        }
        self.policy = json.loads(
            (ROOT / "policies" / "harnessdesk-1772-local-prepare.json").read_text())
        self.assertEqual(self.policy["status"], "PROPOSED_NOT_ACTIVE")
        self.now = self.policy["valid_from"] + 400

    def active_fixture(self):
        # Tests only: an active fixture is not an adopted operator policy.
        self.policy["status"] = "ACTIVE"
        self.policy["owner_decision_url"] = (
            "https://github.com/opensiro/upstream/issues/6#issuecomment-123")

    def host(self):
        return BoundedLocalPrepareHost(
            mandate_reader=lambda: copy.deepcopy(self.policy),
            clock=lambda: self.now)

    def run_stage(self):
        return prepare_exact_two_file_patch(
            manifest=self.manifest, selected_ids=self.selection,
            stage_scopes=self.scopes, candidate_id="harnessdesk-1772",
            action=self.action, github=self.github, host=self.host())

    def test_checked_in_proposal_is_not_authority(self):
        with self.assertRaisesRegex(StageBlocked, "No effective"):
            self.run_stage()
        self.assertEqual(self.github.writes(), [])

    def test_no_owner_decision_even_if_active(self):
        self.policy["status"] = "ACTIVE"
        with self.assertRaisesRegex(StageBlocked, "No effective"):
            self.run_stage()
        self.assertEqual(self.github.writes(), [])

    def test_fixture_active_permits_one_fake_atomic_branch_commit(self):
        self.active_fixture()
        result = self.run_stage()
        self.assertEqual(result["status"], "PREPARED_VERIFIED")
        self.assertEqual(len(self.github.writes()), 1)
        self.assertTrue(self.github.new_branch)
        self.assertEqual(self.github.work_sha, "c" * 40)

    def test_reused_host_grant_rejected(self):
        self.active_fixture()
        host = self.host()
        grant = host.verify_exact_prepare(self.intent)
        self.assertTrue(host.authorize_exact_stage(grant, self.intent))
        with self.assertRaisesRegex(StageBlocked, "Wrong, reused"):
            host.authorize_exact_stage(grant, self.intent)

    def test_revocation_between_checks(self):
        self.active_fixture()
        host = self.host()
        grant = host.verify_exact_prepare(self.intent)
        self.policy["status"] = "REVOKED"
        with self.assertRaisesRegex(StageBlocked, "No effective"):
            host.authorize_exact_stage(grant, self.intent)
        self.assertEqual(self.github.writes(), [])

    def test_changed_mandate_between_checks(self):
        self.active_fixture()
        host = self.host()
        grant = host.verify_exact_prepare(self.intent)
        self.policy["valid_until"] -= 60
        with self.assertRaisesRegex(StageBlocked, "mandate changed"):
            host.authorize_exact_stage(grant, self.intent)

    def test_scope_fork_path_branch_actor_and_publication_rejected(self):
        self.active_fixture()
        for field, replacement in [
            ("working_repo", "xLagerFeuer/HarnessDesk"),
            ("changed_paths", [PATHS[0], "packages/server/test/other.test.ts"]),
            ("new_branch", "main"),
            ("actor", "other-user"),
            ("stage", "submit_external_pr"),
            ("candidate_id", "another-issue"),
        ]:
            with self.subTest(field=field), self.assertRaises(StageBlocked):
                self.host().verify_exact_prepare({**self.intent, field: replacement})

    def test_temporal_scope(self):
        self.active_fixture()
        for clock in (self.policy["valid_from"] - 1, self.policy["valid_until"]):
            with self.subTest(clock=clock):
                self.now = clock
                with self.assertRaisesRegex(StageBlocked, "expired"):
                    self.host().verify_exact_prepare(self.intent)

    def test_proposal_or_patch_digest_changed_rejected(self):
        self.active_fixture()
        for name in ("proposal_sha256", "patch_sha256",
                     "selection_scope_sha256"):
            with self.subTest(name=name):
                obj = copy.deepcopy(self.intent)
                obj[name] = "not-a-sha256"
                with self.assertRaises(StageBlocked):
                    self.host().verify_exact_prepare(obj)

    def test_fork_source_sha_drift_blocked_at_provider(self):
        self.active_fixture()
        self.github.source_sha = "e" * 40
        with self.assertRaises(StageBlocked):
            self.run_stage()
        self.assertEqual(self.github.writes(), [])

    def test_reader_checks_pinned_current_main_sha(self):
        self.active_fixture()
        commit = "a" * 40
        observed = []
        def fake(method, path, body=None):
            observed.append((method, path))
            if path.endswith("branches/main"):
                return 200, {"commit": {"sha": commit}}
            if path == ("repos/" + POLICY_REPO + "/contents/" +
                        POLICY_PATH + "?ref=" + commit):
                return 200, {"type": "file", "encoding": "base64",
                             "content": base64.b64encode(
                                 json.dumps(self.policy).encode()).decode()}
            raise RuntimeError("Unexpected reader GET")
        reader = CurrentMainMandateReader(fake)
        self.assertEqual(reader()["status"], "ACTIVE")
        self.assertEqual(len(observed), 3)
        self.assertTrue(all(t[0] == "GET" for t in observed))

    def test_reader_stops_on_main_drift(self):
        count = [0]
        def fake(method, path, body=None):
            if path.endswith("branches/main"):
                count[0] += 1
                return 200, {"commit": {"sha": (str(count[0]) * 40)}}
            return 200, {"type": "file", "encoding": "base64",
                         "content": base64.b64encode(
                             json.dumps(self.policy).encode()).decode()}
        with self.assertRaisesRegex(StageBlocked, "drifted"):
            CurrentMainMandateReader(fake)()

    def test_reader_denies_missing_or_non_json_policy(self):
        def missing(method, path, body=None):
            return 404, {}
        with self.assertRaisesRegex(StageBlocked, "fetch unavailable"):
            CurrentMainMandateReader(missing)()

if __name__ == "__main__":
    unittest.main()
