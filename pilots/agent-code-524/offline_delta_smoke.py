#!/usr/bin/env python3
"""No-provider before/after CLI contract comparison on immutable agent-code.

Runs *real* original and patched executables with --dump-system-prompt and an
unreachable loopback model URL. Does not invoke model inference, TUI, OS
sandbox escape testing, or review-quality measurement.
"""
import argparse
import hashlib
import pathlib
import tempfile

from offline_cli_smoke import invoke


def _assert_process(label, result, *, success):
    if (result.returncode == 0) != success:
        raise AssertionError(
            f"{label}: unexpected exit {result.returncode}; "
            f"stderr_tail={result.stderr[-450:]!r}"
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-binary", required=True, type=pathlib.Path)
    parser.add_argument("--patched-binary", required=True, type=pathlib.Path)
    args = parser.parse_args()
    baseline = args.baseline_binary.resolve(strict=True)
    patched = args.patched_binary.resolve(strict=True)
    if baseline == patched:
        raise SystemExit("BASELINE_AND_PATCHED_BINARY_SAME_PATH")
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    if sha(baseline) == sha(patched):
        raise SystemExit("BASELINE_AND_PATCHED_BINARY_SAME_BYTES")

    with tempfile.TemporaryDirectory(prefix="ac524-delta-") as directory:
        root = pathlib.Path(directory)
        (root / "home").mkdir()
        overlay = root / "readonly.toml"
        overlay.write_text(
            '[permissions]\ndefault_mode = "plan"\n'
            'allowed_tools = ["FileRead", "Grep", "Glob", "Bash"]\n'
        )
        main_before = invoke(baseline, root, reviewer=False)
        main_after = invoke(patched, root, reviewer=False)
        for name, process in (("baseline main", main_before), ("patched main", main_after)):
            _assert_process(name, process, success=True)
            assert "You are an AI coding agent." in process.stdout, name

        review_before = invoke(baseline, root, reviewer=True, overlay=overlay)
        review_after = invoke(patched, root, reviewer=True, overlay=overlay)
        _assert_process("baseline reviewer", review_before, success=True)
        _assert_process("patched reviewer", review_after, success=True)

        assert "You are an AI coding agent." in review_before.stdout
        assert "You are an independent, read-only code reviewer." not in review_before.stdout
        assert "You are an independent, read-only code reviewer." in review_after.stdout
        assert "You are an AI coding agent." not in review_after.stdout
        assert "no prior conversation history" in review_after.stdout.lower()

        missing_before = invoke(baseline, root, reviewer=True)
        missing_after = invoke(patched, root, reviewer=True)
        _assert_process("baseline missing mandatory overlay", missing_before, success=True)
        _assert_process("patched missing mandatory overlay", missing_after, success=False)
        assert "missing required --permissions-overlay" in missing_after.stderr

        malformed = root / "malformed.toml"
        malformed.write_text("not valid toml = [")
        bad_before = invoke(baseline, root, reviewer=True, overlay=malformed)
        bad_after = invoke(patched, root, reviewer=True, overlay=malformed)
        _assert_process("baseline malformed overlay", bad_before, success=True)
        _assert_process("patched malformed overlay", bad_after, success=False)
        assert "--permissions-overlay" in bad_after.stderr

        print("BASELINE_CODE_ASSISTANT_REUSED_IN_CHILD=YES")
        print("PATCH_REPLACES_CHILD_WITH_DEDICATED_REVIEWER=YES")
        print("BASELINE_MISSING_CHILD_OVERLAY=ALLOWED")
        print("PATCH_MISSING_CHILD_OVERLAY=REJECTED")
        print("BASELINE_MALFORMED_CHILD_OVERLAY=ALLOWED_WITH_WARNING")
        print("PATCH_MALFORMED_CHILD_OVERLAY=REJECTED")
        print("MAIN_ROLE_COMPATIBILITY_BOTH=PASS")
        print("COMPARISON=DETERMINISTIC_OFFLINE_PROCESS_DELTA")
        print("MODEL_INFERENCE=NOT_EXERCISED")
        print("OS_CONFINEMENT=NOT_PROVEN")
        print("REVIEW_QUALITY=NOT_MEASURED")


if __name__ == "__main__":
    main()
