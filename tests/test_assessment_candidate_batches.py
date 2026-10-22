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
NEXT_PATH = ROOT / "data/assessment-candidate-batches/2026-10-22-02.json"
THIRD_PATH = ROOT / "data/assessment-candidate-batches/2026-10-22-03.json"
FOURTH_PATH = ROOT / "data/assessment-candidate-batches/2026-10-22-04.json"
FIFTH_PATH = ROOT / "data/assessment-candidate-batches/2026-10-22-05.json"
SIXTH_PATH = ROOT / "data/assessment-candidate-batches/2026-10-22-06.json"
SEVENTH_PATH = ROOT / "data/assessment-candidate-batches/2026-10-22-07.json"
EIGHTH_PATH = ROOT / "data/assessment-candidate-batches/2026-10-23-08.json"
SCRIPT = ROOT / "scripts/assessment_candidate_batches.py"
SPEC = importlib.util.spec_from_file_location("assessment_candidate_batches", SCRIPT)
queue = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(queue)


class BatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(PATH.read_text(encoding="utf-8"))
        cls.following = json.loads(NEXT_PATH.read_text(encoding="utf-8"))
        cls.third = json.loads(THIRD_PATH.read_text(encoding="utf-8"))
        cls.fourth = json.loads(FOURTH_PATH.read_text(encoding="utf-8"))
        cls.fifth = json.loads(FIFTH_PATH.read_text(encoding="utf-8"))
        cls.sixth = json.loads(SIXTH_PATH.read_text(encoding="utf-8"))
        cls.seventh = json.loads(SEVENTH_PATH.read_text(encoding="utf-8"))
        cls.eighth = json.loads(EIGHTH_PATH.read_text(encoding="utf-8"))

    def test_real_frozen_batch_structure(self):
        board = queue.summarize(self.original)
        self.assertEqual(board["total"], 5)
        self.assertIsNone(board["next_candidate"])
        self.assertEqual(board["next_stage"], "NO_ACTIONABLE_CANDIDATE")
        self.assertEqual(board["stage_counts"]["BLOCKED_EVIDENCE"], 1)
        self.assertEqual(board["stage_counts"]["AWAITING_EXTERNAL"], 2)
        self.assertEqual(board["stage_counts"]["CLOSED_NO_CHANGE"], 2)
        self.assertFalse(board["external_writes_authorized"])
        self.assertFalse(board["remote_canonical_attested"])
        self.assertEqual(board["test_mode"], "NATIVE_SCRIPT_ONLY_NO_LLM_AGENTS")

    def test_blocked_external_case_does_not_stop_next(self):
        data = copy.deepcopy(self.original)
        data["candidates"][3]["stage"] = "SCREENING"
        first = data["candidates"][0]
        first.update(stage="AWAITING_EXTERNAL", origin="ASSESSMENT_INFORMED",
                     handoff_url="https://github.com/opensiro/upstream/pull/77",
                     external_action="NOT_EXECUTED", evidence=["https://github.com/opensiro/upstream/pull/77"])
        first["fit"] = dict.fromkeys(("need", "mechanism", "counterfactual", "scope"), "PASS")
        board = queue.summarize(data)
        self.assertEqual(board["next_candidate"], "raven-stale-edit-ledger")
        self.assertEqual(board["stage_counts"]["AWAITING_EXTERNAL"], 2)

    def test_full_new_cohort_rolls_to_first_unreviewed_row(self):
        first = queue.summarize(self.following)
        self.assertEqual(first["total"], 5)
        self.assertIsNone(first["next_candidate"])
        self.assertEqual(first["next_stage"], "NO_ACTIONABLE_CANDIDATE")
        self.assertEqual(first["stage_counts"]["BLOCKED_EVIDENCE"], 3)
        self.assertEqual(first["stage_counts"]["CLOSED_NO_CHANGE"], 2)
        self.assertEqual(first["test_mode"], "NATIVE_SCRIPT_ONLY_NO_LLM_AGENTS")
        self.assertEqual({r["source"] for r in self.original["candidates"]} & {r["source"] for r in self.following["candidates"]}, set())
        third = queue.summarize(self.third)
        self.assertEqual(third["total"], 5)
        self.assertIsNone(third["next_candidate"])
        self.assertEqual(third["next_stage"], "NO_ACTIONABLE_CANDIDATE")
        self.assertEqual(third["stage_counts"]["CLOSED_NO_CHANGE"], 3)
        self.assertEqual(third["stage_counts"]["BLOCKED_EVIDENCE"], 2)
        earlier = {r["source"] for r in self.original["candidates"] + self.following["candidates"]}
        self.assertFalse(earlier.intersection({r["source"] for r in self.third["candidates"]}))
        fourth = queue.summarize(self.fourth)
        self.assertIsNone(fourth["next_candidate"])
        self.assertEqual(fourth["next_stage"], "NO_ACTIONABLE_CANDIDATE")
        self.assertEqual(fourth["total"], 5)
        self.assertEqual(fourth["stage_counts"]["AWAITING_EXTERNAL"], 3)
        self.assertEqual(fourth["stage_counts"]["BLOCKED_EVIDENCE"], 2)
        all_previous = earlier | {r["source"] for r in self.third["candidates"]}
        self.assertFalse(all_previous.intersection({r["source"] for r in self.fourth["candidates"]}))
        fifth = queue.summarize(self.fifth)
        self.assertEqual(fifth["total"], 5)
        self.assertIsNone(fifth["next_candidate"])
        self.assertEqual(fifth["next_stage"], "NO_ACTIONABLE_CANDIDATE")
        self.assertEqual(fifth["stage_counts"]["AWAITING_EXTERNAL"], 5)
        self.assertEqual(fifth["test_mode"], "NATIVE_SCRIPT_ONLY_NO_LLM_AGENTS")
        all_previous.update(r["source"] for r in self.fourth["candidates"])
        self.assertFalse(all_previous.intersection({r["source"] for r in self.fifth["candidates"]}))
        sixth = queue.summarize(self.sixth)
        self.assertEqual(sixth["total"], 5)
        self.assertIsNone(sixth["next_candidate"])
        self.assertEqual(sixth["next_stage"], "NO_ACTIONABLE_CANDIDATE")
        self.assertEqual(sixth["stage_counts"]["AWAITING_EXTERNAL"], 5)
        self.assertEqual(sixth["test_mode"], "NATIVE_SCRIPT_ONLY_NO_LLM_AGENTS")
        all_previous.update(r["source"] for r in self.fifth["candidates"])
        self.assertFalse(all_previous.intersection({r["source"] for r in self.sixth["candidates"]}))
        all_previous.update(r["source"] for r in self.sixth["candidates"])
        seventh = queue.summarize(self.seventh)
        self.assertEqual(seventh["total"], 5)
        self.assertIsNone(seventh["next_candidate"])
        self.assertEqual(seventh["next_stage"], "NO_ACTIONABLE_CANDIDATE")
        self.assertEqual(seventh["stage_counts"]["AWAITING_EXTERNAL"], 5)
        self.assertEqual(seventh["test_mode"], "NATIVE_SCRIPT_ONLY_NO_LLM_AGENTS")
        self.assertFalse(all_previous.intersection({r["source"] for r in self.seventh["candidates"]}))
        all_previous.update(r["source"] for r in self.seventh["candidates"])
        eighth = queue.summarize(self.eighth)
        self.assertEqual(eighth["total"], 5)
        self.assertEqual(eighth["next_candidate"], "oniroute-validation-boundary")
        self.assertEqual(eighth["stage_counts"]["SCREENING"], 3)
        self.assertEqual(eighth["stage_counts"]["AWAITING_EXTERNAL"], 2)
        self.assertEqual(eighth["test_mode"], "NATIVE_SCRIPT_ONLY_NO_LLM_AGENTS")
        self.assertFalse(all_previous.intersection({r["source"] for r in self.eighth["candidates"]}))

    def test_no_actionable_after_full_review(self):
        data = copy.deepcopy(self.original)
        for row in data["candidates"]:
            row.update(stage="CLOSED_NO_CHANGE", evidence=["https://github.com/opensiro/upstream/issues/56"])
        board = queue.summarize(data)
        self.assertIsNone(board["next_candidate"])
        self.assertEqual(board["next_stage"], "NO_ACTIONABLE_CANDIDATE")

    def test_canonical_shard_with_hyphen_is_accepted_but_traversal_is_not(self):
        data = copy.deepcopy(self.third)
        self.assertEqual(data["candidates"][4]["assessment_path"], "assessments/g-/g-rump.md")
        queue.validate(data)
        data["candidates"][4]["assessment_path"] = "assessments/../g-rump.md"
        with self.assertRaisesRegex(queue.BatchError, "Invalid Index path"):
            queue.validate(data)

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
