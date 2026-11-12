"""Mandatory offline merged-batch disjointness gate; uses no GitHub."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import assessment_batch_disjointness as guard
from assessment_candidate_batches import BatchError


class CohortUniquenessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.first = json.loads((ROOT / "data/assessment-candidate-batches/2026-11-12-30.json").read_text())
        self.second = json.loads((ROOT / "data/assessment-candidate-batches/2026-11-12-31.json").read_text())
        self.write(self.first)
        self.write(self.second)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, batch):
        name = batch["batch_id"].removeprefix("assessment-upstream-") + ".json"
        (self.root / name).write_text(json.dumps(batch))

    def test_actual_repository_has_no_duplicate_assessed_source(self):
        result = guard.check_cohorts(ROOT / "data/assessment-candidate-batches")
        self.assertEqual(result["status"], "MERGED_COHORTS_DISTINCT")
        self.assertGreaterEqual(result["manifest_count"], 31)
        self.assertGreaterEqual(result["source_count"], 175)
        self.assertEqual(len(result["cohort_sha256"]), 64)
        self.assertFalse(result["admission_attested"])
        self.assertFalse(result["remote_open_prs_checked"])
        self.assertFalse(result["external_writes_authorized"])

    def test_two_distinct_cohorts_are_accepted(self):
        result = guard.check_cohorts(self.root)
        self.assertEqual(result["manifest_count"], 2)
        self.assertEqual(result["source_count"], 10)

    def test_duplicate_source_or_case_alias_is_rejected(self):
        for alt in (lambda x: x, str.upper, str.swapcase):
            with self.subTest(alt=alt):
                batch = copy.deepcopy(self.second)
                batch["candidates"][0]["source"] = alt(self.first["candidates"][0]["source"])
                self.write(batch)
                with self.assertRaisesRegex(BatchError, "BLOCKED_DUPLICATE_SOURCE"):
                    guard.check_cohorts(self.root)

    def test_wrong_filename_and_missing_manifest_fail_closed(self):
        (self.root / "2026-11-12-31.json").rename(self.root / "2026-11-12-32.json")
        with self.assertRaisesRegex(BatchError, "BLOCKED_COHORT_IDENTITY"):
            guard.check_cohorts(self.root)
        for p in self.root.glob("*.json"):
            p.unlink()
        with self.assertRaisesRegex(BatchError, "BLOCKED_COHORT_VISIBILITY"):
            guard.check_cohorts(self.root)

    def test_malformed_record_and_symlink_fail_closed(self):
        (self.root / "2026-11-12-31.json").write_text("{")
        with self.assertRaisesRegex(BatchError, "BLOCKED_COHORT_VISIBILITY"):
            guard.check_cohorts(self.root)
        (self.root / "2026-11-12-31.json").unlink()
        (self.root / "2026-11-12-31.json").symlink_to(self.root / "2026-11-12-30.json")
        with self.assertRaisesRegex(BatchError, "BLOCKED_COHORT_VISIBILITY"):
            guard.check_cohorts(self.root)

    def test_cli_returns_machine_readable_receipt(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts/assessment_batch_disjointness.py"),
             "--batch-dir", str(self.root)], text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["source_count"], 10)


if __name__ == "__main__":
    unittest.main()
