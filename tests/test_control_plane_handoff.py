"""Read-only Control Plane handoff contract and failure tests."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from control_plane_handoff import handoff, HandoffError


SHA = "a" * 40


def fixture():
    return {
        "schema_version": 1, "batch_id": "upstream-20261019-control",
        "revision": 1, "status": "proposal_only", "candidates": [{
            "id": "race-regression", "source": "vendor/project", "fork_name": "project",
            "stages": ["create_public_fork", "prepare_contribution", "submit_external_pr"],
            "expected_license": "MIT",
            "proposal": {
                "system_component": "Concurrent task handoff",
                "problem": "An existing concurrency path lacks regression coverage",
                "planned_change": "Add a focused regression test in the fork",
                "expected_improvement": "Earlier detection of future race regressions",
                "validation": "Run one deterministic concurrency test",
                "evidence_url": "https://github.com/vendor/project/issues/12"},
            "blockers": []}]
    }


def action():
    return {"working_repo": "contributor/project", "base_branch": "main",
            "base_sha": SHA, "new_branch": "opensiro/race-regression",
            "file_path": "tests/test_race.py", "content": "assert True\n"}


class HandoffContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.manifest = Path(self.tmp.name) / "upstream-20261019-control.json"
        self.content_file = Path(self.tmp.name) / "test.py"
        self.content_file.write_text("assert True\n", encoding="utf-8")
        self.data = fixture()
        self.persist()

    def persist(self):
        self.manifest.write_text(json.dumps(self.data), encoding="utf-8")

    def invoke(self, candidate="race-regression", op=None):
        return handoff(manifest=self.manifest, candidate_id=candidate, action=op or action())

    def test_exact_one_stage_no_writes_and_no_approval(self):
        result = self.invoke()
        self.assertEqual(result["status"], "ACTION_PREPARED_NOT_AUTHORIZED")
        self.assertEqual(result["authorization_status"], "NOT_APPROVED_NO_WRITES")
        self.assertEqual(result["stage"], "prepare_contribution")
        self.assertFalse(result["execution_available"])
        self.assertIn("trusted current-session", result["runtime_preflight"][-1])
        self.assertNotIn("approved_by", result)
        self.assertNotIn("content", result["action"])
        self.assertIn("content_sha256", result["action"])

    def test_exact_same_packet_on_repeated_draft(self):
        self.assertEqual(self.invoke(), self.invoke())

    def test_changed_bytes_change_digest(self):
        item = action()
        item["content"] += "assert False\n"
        self.assertNotEqual(
            self.invoke()["action"]["content_sha256"],
            self.invoke(op=item)["action"]["content_sha256"])

    def test_revision_change_invalidates_proposal(self):
        current = self.invoke()
        self.data["revision"] = 2
        self.persist()
        self.assertNotEqual(current["proposal_sha256"], self.invoke()["proposal_sha256"])
        self.assertNotEqual(current["selection_scope_sha256"], self.invoke()["selection_scope_sha256"])

    def test_unknown_candidate_rejected(self):
        with self.assertRaises(HandoffError):
            self.invoke(candidate="absent")

    def test_no_prepare_stage_rejected(self):
        self.data["candidates"][0]["stages"] = ["create_public_fork"]
        self.persist()
        with self.assertRaises(HandoffError):
            self.invoke()

    def test_blocked_candidate_rejected(self):
        self.data["candidates"][0]["blockers"] = ["Source evidence not verified"]
        self.persist()
        with self.assertRaises(HandoffError):
            self.invoke()

    def test_unknown_license_rejected(self):
        self.data["candidates"][0]["expected_license"] = None
        self.data["candidates"][0]["blockers"] = ["License status is unverified"]
        self.persist()
        with self.assertRaises(HandoffError):
            self.invoke()

    def test_fake_approval_field_rejected(self):
        self.data["approved_by"] = "imposter"
        self.persist()
        with self.assertRaises(HandoffError):
            self.invoke()

    def test_different_fork_name_rejected(self):
        a = action()
        a["working_repo"] = "contributor/unrelated"
        with self.assertRaises(HandoffError):
            self.invoke(op=a)

    def test_package_local_test_path_is_included_in_packet(self):
        a = action()
        a["file_path"] = "packages/graph/arcadedb/tests/unit/test_has_edges.py"
        packet = self.invoke(op=a)
        self.assertEqual(packet["action"]["file_path"], a["file_path"])
        self.assertEqual(packet["status"], "ACTION_PREPARED_NOT_AUTHORIZED")

    def test_existing_file_path_rejected(self):
        a = action()
        a["file_path"] = "README.md"
        with self.assertRaises(HandoffError):
            self.invoke(op=a)

    def test_path_traversal_rejected(self):
        a = action()
        a["file_path"] = "tests/../README.md"
        with self.assertRaises(HandoffError):
            self.invoke(op=a)

    def test_bad_branch_rejected(self):
        a = action()
        a["new_branch"] = "main"
        with self.assertRaises(HandoffError):
            self.invoke(op=a)

    def test_non_sha_rejected(self):
        a = action()
        a["base_sha"] = "main"
        with self.assertRaises(HandoffError):
            self.invoke(op=a)

    def test_too_much_content_rejected(self):
        a = action()
        a["content"] = "x" * 49153
        with self.assertRaises(HandoffError):
            self.invoke(op=a)

    def test_no_network_even_when_previewed(self):
        with patch("urllib.request.urlopen", side_effect=AssertionError("Unexpected network")):
            self.invoke()

    def test_cli_outputs_same_unapproved_packet(self):
        cmd = [sys.executable, str(SCRIPTS / "control_plane_handoff.py"),
               "--manifest", str(self.manifest), "--candidate", "race-regression",
               "--working-repo", "contributor/project", "--base-branch", "main",
               "--base-sha", SHA, "--new-branch", "opensiro/race-regression",
               "--file-path", "tests/test_race.py", "--content-file", str(self.content_file)]
        result = subprocess.run(cmd, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), self.invoke())

    def test_cli_no_execute_flag(self):
        cmd = [sys.executable, str(SCRIPTS / "control_plane_handoff.py"),
               "--manifest", str(self.manifest), "--candidate", "race-regression",
               "--working-repo", "contributor/project", "--base-branch", "main",
               "--base-sha", SHA, "--new-branch", "opensiro/race-regression",
               "--file-path", "tests/test_race.py", "--content-file", str(self.content_file),
               "--execute"]
        r = subprocess.run(cmd, text=True, capture_output=True, check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("unrecognized arguments", r.stderr)

    def test_cli_binary_file_rejected(self):
        self.content_file.write_bytes(b"\xff")
        cmd = [sys.executable, str(SCRIPTS / "control_plane_handoff.py"),
               "--manifest", str(self.manifest), "--candidate", "race-regression",
               "--working-repo", "contributor/project", "--base-branch", "main",
               "--base-sha", SHA, "--new-branch", "opensiro/race-regression",
               "--file-path", "tests/test_race.py", "--content-file", str(self.content_file)]
        result = subprocess.run(cmd, text=True, capture_output=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("HANDOFF_BLOCKED", result.stderr)


if __name__ == "__main__":
    unittest.main()
