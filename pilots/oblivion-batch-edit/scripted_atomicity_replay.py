#!/usr/bin/env python3
"""Native, model-free replay against a checked-out Oblivion tools/batch_edit.py."""

import argparse
import importlib.util
import json
import os
import tempfile
from pathlib import Path


def replay(root):
    source = Path(root) / "tools" / "batch_edit.py"
    if not source.is_file():
        raise ValueError(f"Missing first-party source: {source}")
    spec = importlib.util.spec_from_file_location("actual_oblivion_batch_edit", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix="oblivion-script-native-") as tmp:
        previous = os.environ.get("WORKSPACE_DIR")
        os.environ["WORKSPACE_DIR"] = tmp
        try:
            first = Path(tmp) / "first.txt"
            second = Path(tmp) / "second.txt"
            first.write_text("original first", encoding="utf-8")
            second.write_text("original second", encoding="utf-8")
            result = module.batch_edit([
                {"path": "first.txt", "old_text": "original first", "new_text": "changed first"},
                {"path": "second.txt", "old_text": "not present", "new_text": "changed second"},
            ])
            actual = (first.read_text(encoding="utf-8"), second.read_text(encoding="utf-8"))

            # Independent positive control: valid sequential same-path edits
            # must still apply both updates to the true first-party function.
            first.write_text("one", encoding="utf-8")
            success = module.batch_edit([
                {"path": "first.txt", "old_text": "one", "new_text": "two"},
                {"path": "first.txt", "old_text": "two", "new_text": "three"},
                {"path": "second.txt", "content": "independent"},
            ])
            control = (first.read_text(encoding="utf-8"), second.read_text(encoding="utf-8"))
        finally:
            if previous is None:
                os.environ.pop("WORKSPACE_DIR", None)
            else:
                os.environ["WORKSPACE_DIR"] = previous
    return {
        "native_source": str(source),
        "two_edit_batch_contains_one_invalid_old_text": True,
        "first_file_changed_despite_second_error": actual[0] != "original first",
        "second_file_unchanged": actual[1] == "original second",
        "partial_mutation": actual != ("original first", "original second"),
        "returned_error": "ERRORS" in result or "Error" in result,
        "positive_control_same_path_sequential": control[0] == "three",
        "positive_control_independent_file": control[1] == "independent",
        "positive_control_reported_success": "SUCCESS" in success,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-root", required=True, type=Path)
    parser.add_argument("--expect", choices=["before", "after"], required=True)
    args = parser.parse_args()
    report = replay(args.target_root)
    report["expected_mode"] = args.expect
    print(json.dumps(report, indent=2, sort_keys=True))
    assert report["returned_error"] and report["second_file_unchanged"], report
    assert (report["positive_control_same_path_sequential"] and
            report["positive_control_independent_file"] and
            report["positive_control_reported_success"]), report
    assert report["first_file_changed_despite_second_error"] == (args.expect == "before"), report


if __name__ == "__main__":
    main()
