"""Offline contract tests for the deliberately non-executable proposal preview."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "batch_proposals.py"
SPEC = importlib.util.spec_from_file_location("batch_proposals", SCRIPT)
preview = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(preview)


def example():
    # Deliberately synthetic. The URL is syntax only, not evidence of a real issue.
    return {
        "schema_version": 1,
        "batch_id": "upstream-20261018-synthetic",
        "revision": 1,
        "status": "proposal_only",
        "candidates": [{
            "id": "project-a",
            "source": "example/project-a",
            "fork_name": "project-a",
            "stages": ["create_public_fork", "prepare_contribution", "submit_external_pr"],
            "expected_license": "MIT",
            "proposal": {
                "system_component": "Task handoff controller",
                "problem": "A hypothetical interruption leaves ownership uncertain",
                "planned_change": "Add test coverage for interrupted handoffs",
                "expected_improvement": "More clearly attributed task ownership after recovery",
                "validation": "Run interrupted-transfer regression suite",
                "evidence_url": "https://github.com/example/project-a/issues/1"
            },
            "blockers": ["Example data is synthetic and not executable"]
        }]
    }


class DraftPreviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "upstream-20261018-synthetic.json"
        self.data = example()
        self.save()

    def save(self):
        self.path.write_text(json.dumps(self.data), encoding="utf-8")

    def report(self, ids=("project-a",), stages=None):
        scope = {"project-a": stages} if stages is not None else None
        return preview.preview_draft(self.path, selected_ids=list(ids), stage_scopes=scope)

    def test_blocked_selection_never_approves(self):
        report = self.report()
        self.assertEqual(report["status"], "PROPOSAL_PREVIEW")
        self.assertEqual(report["authorization_status"], "NOT_APPROVED_NO_WRITES")
        self.assertTrue(report["selection_has_blockers"])
        self.assertEqual(report["candidates"][0]["status"], "BLOCKED")
        self.assertIn("NO GITHUB WRITES", preview.render_draft_text(report))

    def test_scope_reduction_changes_only_scoped_digest(self):
        full = self.report()
        reduced = self.report(stages=["create_public_fork"])
        self.assertEqual(full["selection_sha256"], reduced["selection_sha256"])
        self.assertNotEqual(full["selection_scope_sha256"], reduced["selection_scope_sha256"])
        self.assertEqual(reduced["candidates"][0]["selected_stages"], ["create_public_fork"])

    def test_scope_cannot_expand_permissions(self):
        with self.assertRaises(preview.BatchError):
            self.report(stages=["delete_repository"])

    def test_scope_cannot_reverse_stages(self):
        with self.assertRaises(preview.BatchError):
            self.report(stages=["submit_external_pr", "create_public_fork"])

    def test_scope_cannot_repeat_stages(self):
        with self.assertRaises(preview.BatchError):
            self.report(stages=["create_public_fork", "create_public_fork"])

    def test_scope_cannot_select_unselected_candidate(self):
        with self.assertRaises(preview.BatchError):
            preview.preview_draft(self.path, selected_ids=[],
                                  stage_scopes={"project-a": ["create_public_fork"]})

    def test_unknown_and_duplicate_ids_rejected(self):
        for ids in (["nonexistent"], ["project-a", "project-a"]):
            with self.subTest(ids=ids), self.assertRaises(preview.BatchError):
                preview.preview_draft(self.path, selected_ids=ids)

    def test_canonical_digest_ignores_json_key_order(self):
        reordered = dict(reversed(list(self.data.items())))
        self.assertEqual(preview.canonical_digest(self.data),
                         preview.canonical_digest(reordered))

    def test_plan_change_invalidates_digest(self):
        changed = copy.deepcopy(self.data)
        changed["candidates"][0]["proposal"]["planned_change"] += " and recovery"
        self.assertNotEqual(preview.canonical_digest(self.data),
                            preview.canonical_digest(changed))

    def test_asserted_chat_approval_rejected(self):
        self.data["approved_by"] = "someone"
        self.save()
        with self.assertRaises(preview.BatchError):
            preview.load_draft(self.path)

    def test_unresolved_license_rejected(self):
        self.data["candidates"][0]["expected_license"] = "UNKNOWN"
        self.save()
        with self.assertRaises(preview.BatchError):
            preview.load_draft(self.path)

    def test_invalid_evidence_url_rejected(self):
        self.data["candidates"][0]["proposal"]["evidence_url"] = "http://example.com/issue"
        self.save()
        with self.assertRaises(preview.BatchError):
            preview.load_draft(self.path)

    def test_duplicate_json_fields_rejected(self):
        with self.assertRaises(preview.BatchError):
            preview.no_duplicate_keys([("status", "first"), ("status", "second")])

    def test_execute_flag_rejected_by_cli(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--manifest", str(self.path),
             "--draft", "--execute"], capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unrecognized arguments", result.stderr)

    def test_preview_requires_draft_flag(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--manifest", str(self.path)],
            capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--draft is required", result.stderr)

    def test_preview_never_uses_github_network(self):
        with patch("urllib.request.urlopen", side_effect=AssertionError("network attempted")):
            self.report()


if __name__ == "__main__":
    unittest.main()
