"""End-to-end offline origin → proposed exact prepare-stage handoff."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "scripts"))
from test_assessment_origin_preflight import (
    ASSESSMENT_PATH, source, manifest, git,
)
from assessment_driven_handoff import (
    AssessmentHandoffBlocked, preview_assessment_handoff,
)


class AssessmentDrivenHandoffTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)
        self.root = self.base / "index"
        self.root.mkdir()
        git(self.root, "init", "-q")
        path = self.root / ASSESSMENT_PATH
        path.parent.mkdir(parents=True)
        path.write_text(source(), encoding="utf-8")
        git(self.root, "add", "--all")
        git(self.root, "-c", "user.name=Fixture", "-c",
            "user.email=fixture@example.invalid", "commit", "-qm", "source")
        self.index_sha = git(self.root, "rev-parse", "HEAD")
        self.manifest = self.base / "upstream-20261019-origin-fixture.json"
        self.draft = manifest()
        self.persist()
        self.action = {
            "working_repo": "contributor/fixture-harness", "base_branch": "main",
            "base_sha": "b" * 40, "new_branch": "opensiro/fixture-gap",
            "file_path": "tests/test_fixture.py", "content": "assert True\n",
        }

    def persist(self):
        self.manifest.write_text(json.dumps(self.draft), encoding="utf-8")

    def run_preview(self, **changes):
        args = {
            "index_root": self.root, "index_sha": self.index_sha,
            "assessment_path": ASSESSMENT_PATH, "manifest": self.manifest,
            "candidate_id": "fixture-gap", "action": self.action,
        }
        args.update(changes)
        return preview_assessment_handoff(**args)

    def test_composition_is_bound_to_same_proposal_without_any_writes(self):
        with patch("urllib.request.urlopen", side_effect=AssertionError("network")):
            packet = self.run_preview()
        self.assertEqual(packet["status"], "ASSESSMENT_DRIVEN_HANDOFF_PREVIEW_ONLY")
        self.assertEqual(packet["authorization_status"], "NOT_APPROVED_NO_GITHUB_WRITES")
        self.assertFalse(packet["execution_available"])
        self.assertFalse(packet["origin"]["execution_available"])
        self.assertFalse(packet["prepare_stage"]["execution_available"])
        self.assertEqual(packet["origin"]["proposal_sha256"],
                         packet["prepare_stage"]["proposal_sha256"])
        self.assertEqual(packet["origin"]["assessed_upstream"],
                         packet["prepare_stage"]["upstream_source"])
        self.assertEqual(packet["prepare_stage"]["stage"], "prepare_contribution")
        self.assertIn("content_sha256", packet["prepare_stage"]["action"])
        self.assertNotIn("content", packet["prepare_stage"]["action"])
        self.assertEqual(len(packet["unresolved_gates"]), 5)

    def test_changed_test_file_content_changes_digest_not_authority(self):
        first = self.run_preview()
        change = dict(self.action, content="assert False\n")
        second = self.run_preview(action=change)
        self.assertNotEqual(first["prepare_stage"]["action"]["content_sha256"],
                            second["prepare_stage"]["action"]["content_sha256"])
        self.assertEqual(first["origin"]["proposal_sha256"],
                         second["origin"]["proposal_sha256"])
        self.assertFalse(second["execution_available"])

    def test_invalid_index_revision_fails_closed(self):
        with self.assertRaises(AssessmentHandoffBlocked):
            self.run_preview(index_sha="a" * 40)

    def test_candidate_source_substitution_fails_closed(self):
        self.draft["candidates"][0]["source"] = "unrelated/fixture-harness"
        self.persist()
        with self.assertRaises(AssessmentHandoffBlocked):
            self.run_preview()

    def test_blocked_candidate_stops_before_packet(self):
        self.draft["candidates"][0]["blockers"] = ["Need independent fit review"]
        self.persist()
        with self.assertRaises(AssessmentHandoffBlocked):
            self.run_preview()

    def test_working_fork_and_unsafe_path_checked_by_original_adapter(self):
        for action in (
            dict(self.action, working_repo="contributor/wrong"),
            dict(self.action, file_path="../secrets.txt"),
            dict(self.action, new_branch="main"),
        ):
            with self.subTest(action=action), self.assertRaises(AssessmentHandoffBlocked):
                self.run_preview(action=action)

    def test_cli_exposes_no_execute_flag(self):
        file = self.base / "test.py"
        file.write_text("assert True\n", encoding="utf-8")
        cmd = [
            sys.executable, str(ROOT / "scripts" / "assessment_driven_handoff.py"),
            "--index-root", str(self.root),
            "--index-sha", self.index_sha,
            "--assessment-path", ASSESSMENT_PATH,
            "--manifest", str(self.manifest), "--candidate", "fixture-gap",
            "--working-repo", "contributor/fixture-harness",
            "--base-branch", "main", "--base-sha", "b" * 40,
            "--new-branch", "opensiro/fixture-gap",
            "--file-path", "tests/test_fixture.py",
            "--content-file", str(file),
        ]
        ok = subprocess.run(cmd, text=True, capture_output=True, check=False)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertEqual(json.loads(ok.stdout)["status"],
                         "ASSESSMENT_DRIVEN_HANDOFF_PREVIEW_ONLY")
        blocked = subprocess.run([*cmd, "--execute"], text=True,
                                 capture_output=True, check=False)
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn("unrecognized arguments", blocked.stderr)


if __name__ == "__main__":
    unittest.main()
