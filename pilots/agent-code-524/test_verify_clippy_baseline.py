#!/usr/bin/env python3
"""Synthetic tests for the upstream baseline lint verifier (not live lint results)."""
import json
import unittest

from verify_clippy_baseline import EXPECTED, errors_from_jsonl, validate


def make_jsonl():
    lines = []
    for (code, path, line), n in EXPECTED.items():
        for _ in range(n):
            lines.append(json.dumps({
                "reason": "compiler-message",
                "message": {
                    "level": "error", "code": {"code": code},
                    "spans": [{"file_name": path, "line_start": line, "is_primary": True}]
                }
            }))
    lines.append(json.dumps({"reason": "build-finished", "success": False}))
    return "\n".join(lines)


class ClippyBaselineValidatorTests(unittest.TestCase):
    def test_expected_baseline_is_only_an_attestation(self):
        result = validate(make_jsonl(), 101)
        self.assertEqual(result["unique_existing_diagnostics"], 6)
        self.assertEqual(result["diagnostic_instances"], 6)
        self.assertTrue(result["does_not_prove_unqualified_strict_clippy_pass"])

    def test_patched_repeated_lib_diagnostics_are_reported_not_silenced(self):
        lines = make_jsonl().splitlines()
        repeated = "\n".join(lines[:-1] + lines[:-1] + [lines[-1]])
        result = validate(repeated, 101, side="patched")
        self.assertEqual(result["unique_existing_diagnostics"], 6)
        self.assertEqual(result["diagnostic_instances"], 12)
        self.assertEqual(result["result"], "NO_NEW_DIAGNOSTIC_LOCATIONS")
        with self.assertRaisesRegex(ValueError, "baseline Clippy diagnostics changed"):
            validate(repeated, 101, side="baseline")

    def test_patched_third_duplicate_is_rejected(self):
        lines = make_jsonl().splitlines()
        repeated = "\n".join(lines[:-1] * 3)
        with self.assertRaisesRegex(ValueError, "diagnostic locations changed"):
            validate(repeated, 101, side="patched")

    def test_reject_additional_errors(self):
        extra = json.dumps({"reason": "compiler-message", "message": {
            "level": "error", "code": {"code": "E0382"},
            "spans": [{"file_name": "src/new.rs", "line_start": 10, "is_primary": True}]
        }})
        with self.assertRaisesRegex(ValueError, "diagnostics changed"):
            validate(make_jsonl() + "\n" + extra, 101)

    def test_reject_missing_errors(self):
        lines = make_jsonl().splitlines()
        with self.assertRaisesRegex(ValueError, "diagnostics changed"):
            validate("\n".join(lines[1:]), 101)

    def test_reject_successful_baseline(self):
        with self.assertRaisesRegex(ValueError, "succeeded"):
            validate(make_jsonl(), 0)

    def test_reject_malformed_json(self):
        with self.assertRaisesRegex(ValueError, "malformed"):
            validate(make_jsonl() + "\n{bad json", 101)

    def test_ignore_nonerrors(self):
        text = make_jsonl() + "\n" + json.dumps({
            "reason": "compiler-message",
            "message": {"level": "warning", "code": {"code": "clippy::example"}, "spans": []}
        })
        self.assertEqual(len(errors_from_jsonl(text)[0]), 6)


if __name__ == "__main__":
    unittest.main()
