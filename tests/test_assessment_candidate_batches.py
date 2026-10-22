"""Offline native-script-only validations of frozen upstream screening batches."""

import copy
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data/assessment-candidate-batches/2026-10-22-01.json"
SCRIPT = ROOT / "scripts/assessment_candidate_batches.py"
SPEC = importlib.util.spec_from_file_location("assessment_candidate_batches", SCRIPT)
queue = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(queue)


class BatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(PATH.read_text(encoding="utf-8"))

    def test_real_frozen_batch_structure(self):
        board = queue.summarize(self.original)
        self.assertEqual(board["total"], 5)
        self.assertEqual(board["next_candidate"], "raven-stale-edit-ledger")
        self.assertEqual(board["stage_counts"]["BLOCKED_EVIDENCE"], 1)
        self.assertEqual(board["stage_counts"]["AWAITING_EXTERNAL"], 1)
        self.assertFalse(board["external_writes_authorized"])
        self.assertFalse(board["remote_canonical_attested"])
        self.assertEqual(board["test_mode"], "NATIVE_SCRIPT_ONLY_NO_LLM_AGENTS")

    def test_blocked_external_case_does_not_stop_next(self):
        data = copy.deepcopy(self.original)
        first = data["candidates"][0]
        first.update(stage="AWAITING_EXTERNAL", origin="ASSESSMENT_INFORMED",
                     handoff_url="https://github.com/opensiro/upstream/pull/77",
                     external_action="NOT_EXECUTED", evidence=["https://github.com/opensiro/upstream/pull/77"])
        first["fit"] = dict.fromkeys(("need", "mechanism", "counterfactual", "scope"), "PASS")
        board = queue.summarize(data)
        self.assertEqual(board["next_candidate"], "raven-stale-edit-ledger")
        self.assertEqual(board["stage_counts"]["AWAITING_EXTERNAL"], 2)

    def test_no_actionable_after_full_review(self):
        data = copy.deepcopy(self.original)
        for row in data["candidates"]:
            row.update(stage="CLOSED_NO_CHANGE", evidence=["https://github.com/opensiro/upstream/issues/56"])
        board = queue.summarize(data)
        self.assertIsNone(board["next_candidate"])
        self.assertEqual(board["next_stage"], "NO_ACTIONABLE_CANDIDATE")

    def test_reject_partial_duplicate_or_reordered_batch(self):
        for transform in (
            lambda d: d["candidates"].pop(),
            lambda d: d["candidates"][1].update(source=d["candidates"][0]["source"]),
            lambda d: d["candidates"].reverse(),
            lambda d: d.update(index_sha="0" * 39),
            lambda d: d["candidates"][2].update(stage="ACTIVE"),
            lambda d: d["candidates"][2].update(stage="AWAITING_EXTERNAL"),
        ):
            with self.subTest(transform=transform):
                data = copy.deepcopy(self.original)
                transform(data)
                with self.assertRaises(queue.BatchError):
                    queue.validate(data)

    def test_local_index_exact_object_crosscheck(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            subprocess.run(["git", "init", "-q", str(folder)], check=True)
            subprocess.run(["git", "-C", str(folder), "config", "user.email", "test@example.com"], check=True)
            subprocess.run(["git", "-C", str(folder), "config", "user.name", "Test"], check=True)
            data = copy.deepcopy(self.original)
            for row in data["candidates"]:
                file = folder / row["assessment_path"]
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text("---\n" + "\n".join((
                    f"harness_id: {file.stem}",
                    f"repository: https://github.com/{row['source']}",
                    f"review_ref: {row['review_ref']}",
                    f"reviewed_at: {row['reviewed_at']}",
                    "status: included", "autonomy_s1: A"
                )) + "\n---\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(folder), "add", "assessments"], check=True)
            subprocess.run(["git", "-C", str(folder), "commit", "-qm", "fixture"], check=True)
            sha = subprocess.check_output(["git", "-C", str(folder), "rev-parse", "HEAD"], text=True).strip()
            data["index_sha"] = sha
            queue.validate(data, folder)
            data["candidates"][0]["review_ref"] = "0" * 40
            with self.assertRaisesRegex(queue.BatchError, "identity or reviewed ref changed"):
                queue.validate(data, folder)


if __name__ == "__main__":
    unittest.main()
