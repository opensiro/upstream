#!/usr/bin/env python3
"""Deterministic tests for score.py; all examples are MOCK, never product outcomes."""
import copy
import unittest
from score import score


def fixture():
    cases = {"schema_version": 1, "cases": [
        {"id": "bug", "source_sha": "a" * 40, "input_sha256": "b" * 64,
         "truth_ids": ["bug-1", "bug-2"]},
        {"id": "clean", "source_sha": "a" * 40, "input_sha256": "c" * 64,
         "truth_ids": []}
    ]}
    runs = {"schema_version": 1, "runs": []}
    judgements = {"schema_version": 1, "blinded_adjudication": True,
                  "adjudications": {}}
    for case in cases["cases"]:
        for arm in ("baseline", "isolated"):
            rid = case["id"] + "-" + arm
            finds = (
                [{"title": "one", "file": "src/x.rs", "line_start": 1, "line_end": 1},
                 {"title": "dup", "file": "src/x.rs", "line_start": 1, "line_end": 1}]
                if arm == "isolated" and case["id"] == "bug" else
                [{"title": "noise", "file": "src/x.rs", "line_start": 2, "line_end": 2}]
                if arm == "baseline" else []
            )
            matches = (["bug-1", "bug-1"] if arm == "isolated" and case["id"] == "bug"
                       else [None] if arm == "baseline" else [])
            runs["runs"].append({
                "id": rid, "case_id": case["id"], "arm": arm, "repeat": 1,
                "source_type": "mock_provider", "source_sha": case["source_sha"],
                "input_sha256": case["input_sha256"], "model": "fake-model",
                "context_condition": "author_exposed",
                "prompt_sha256": ("d" if arm == "baseline" else "e") * 64,
                "duration_ms": 100 if arm == "baseline" else 120,
                "total_tokens": 50 if arm == "baseline" else 70,
                "findings": finds
            })
            judgements["adjudications"][rid] = matches
    return cases, runs, judgements


class TestScorer(unittest.TestCase):
    def test_mock_never_counts_as_proven_benefit(self):
        data = score(*fixture())
        self.assertEqual(data["evidence_class"], "NON_LIVE_NOT_PRODUCT_BENEFIT")
        self.assertEqual(data["benefit_verdict"], "NOT_AUTO_ADJUDICATED")
        self.assertEqual(data["pairs"], 2)
        self.assertEqual(data["baseline"]["tp"], 0)
        self.assertEqual(data["baseline"]["fp"], 2)
        self.assertEqual(data["isolated"]["tp"], 1)
        self.assertEqual(data["isolated"]["fp"], 1)  # duplicate doesn't count twice
        self.assertEqual(data["isolated"]["fn"], 1)

    def test_unpaired_rejected(self):
        c, r, j = fixture()
        r["runs"].pop()
        j["adjudications"].pop("clean-isolated")
        with self.assertRaisesRegex(ValueError, "unpaired"):
            score(c, r, j)

    def test_unadjudicated_rejected(self):
        c, r, j = fixture()
        j["adjudications"].pop("bug-baseline")
        with self.assertRaisesRegex(ValueError, "adjudication"):
            score(c, r, j)

    def test_unknown_truth_rejected(self):
        c, r, j = fixture()
        j["adjudications"]["bug-isolated"][0] = "invented"
        with self.assertRaisesRegex(ValueError, "unknown truth"):
            score(c, r, j)

    def test_mismatched_models_rejected(self):
        c, r, j = fixture()
        r["runs"][0]["model"] = "other-model"
        with self.assertRaisesRegex(ValueError, "model/source"):
            score(c, r, j)

    def test_mismatched_scenario_rejected(self):
        c, r, j = fixture()
        r["runs"][0]["input_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "source/input mismatch"):
            score(c, r, j)

    def test_duplicate_arm_rejected(self):
        c, r, j = fixture()
        duplicate = copy.deepcopy(r["runs"][0])
        duplicate["id"] = "duplicate-baseline"
        r["runs"].append(duplicate)
        j["adjudications"]["duplicate-baseline"] = [None]
        with self.assertRaisesRegex(ValueError, "duplicate baseline"):
            score(c, r, j)

    def test_zero_observations_not_success(self):
        c, r, j = fixture()
        r["runs"] = []
        j["adjudications"] = {}
        with self.assertRaisesRegex(ValueError, "NOT_MEASURED"):
            score(c, r, j)

    def test_missing_blind_attestation_rejected(self):
        c, r, j = fixture()
        j["blinded_adjudication"] = False
        with self.assertRaisesRegex(ValueError, "blinded_adjudication"):
            score(c, r, j)


if __name__ == "__main__":
    unittest.main()
