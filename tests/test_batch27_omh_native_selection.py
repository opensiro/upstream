"""Pin the strict-derived Oh My Hermes native packet and negative batch outcomes."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Batch27NativeSelectionTest(unittest.TestCase):
    def test_exact_source_native_packet(self):
        batch = json.loads((ROOT / "data/assessment-candidate-batches/2026-11-12-27.json").read_text())
        selected = json.loads((ROOT / "data/contribution-workspaces/selected-packets.json").read_text())["selections"]
        row = next(v for v in batch["candidates"] if v["id"] == "oh-my-hermes-crossprocess-lock")
        packet = next(v for v in selected if v["candidate_id"] == row["id"])
        self.assertEqual(row["stage"], "AWAITING_EXTERNAL")
        self.assertEqual(row["origin"], "ASSESSMENT_DERIVED")
        self.assertEqual(set(row["fit"].values()), {"PASS"})
        self.assertEqual(packet["source"], row["source"])
        self.assertEqual(packet["source_sha"], row["review_ref"])
        self.assertEqual(hashlib.sha256((ROOT / packet["patch_path"]).read_bytes()).hexdigest(), packet["patch_sha256"])
        self.assertIn("9e2c1e9695a82fcb853d05244ba8198dcd61dc1b", row["evidence"][1])
        self.assertTrue((ROOT / packet["receipt"]).is_file())
        self.assertTrue((ROOT / row["test_patch_path"]).is_file())

    def test_five_distinct_source_rows_and_no_external_claims(self):
        rows = json.loads((ROOT / "data/assessment-candidate-batches/2026-11-12-27.json").read_text())["candidates"]
        self.assertEqual(len(rows), 5)
        self.assertEqual(len({r["source"].casefold() for r in rows}), 5)
        self.assertEqual([r["stage"] for r in rows].count("AWAITING_EXTERNAL"), 1)
        self.assertEqual([r["stage"] for r in rows].count("CLOSED_NO_CHANGE"), 1)
        self.assertEqual([r["stage"] for r in rows].count("BLOCKED_EVIDENCE"), 3)
        self.assertEqual({r["external_action"] for r in rows}, {"NOT_EXECUTED"})


if __name__ == "__main__":
    unittest.main()
