#!/usr/bin/env python3
"""Attest the exact *pre-existing* unqualified Clippy failures on clean agent-code.

Input: cargo clippy --all-targets --locked --message-format=json -- -D warnings
against the IMMUTABLE, UNPATCHED upstream commit. This does NOT waive any
warnings in a patched contribution and does NOT certify its strict Clippy.
"""
import argparse
import collections
import json
import pathlib

EXPECTED = collections.Counter({
    ("clippy::unnecessary_cast", "crates/lib/src/amr/selectors.rs", 202): 1,
    ("clippy::unnecessary_cast", "crates/lib/src/tools/bash_parse.rs", 84): 1,
    ("clippy::unnecessary_cast", "crates/lib/src/tools/bash_parse.rs", 119): 1,
    ("clippy::unnecessary_cast", "crates/lib/src/tools/bash_parse.rs", 129): 1,
    ("clippy::unnecessary_cast", "crates/lib/src/tools/bash_parse.rs", 148): 1,
    ("clippy::unnecessary_cast", "crates/lib/src/tools/bash_parse.rs", 165): 1,
})


def errors_from_jsonl(text):
    found = collections.Counter()
    malformed = 0
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            continue
        if entry.get("reason") != "compiler-message":
            continue
        m = entry.get("message", {})
        if m.get("level") != "error":
            continue
        code = (m.get("code") or {}).get("code") or "<none>"
        primary = [span for span in m.get("spans", []) if span.get("is_primary")]
        if not primary:
            found[(code, "<no-primary-span>", 0)] += 1
        else:
            for span in primary:
                found[(code, str(span.get("file_name")), span.get("line_start"))] += 1
    return found, malformed


def validate(text, exit_code):
    found, malformed = errors_from_jsonl(text)
    if exit_code == 0:
        raise ValueError("baseline strict Clippy succeeded; expected warnings no longer hold")
    if malformed:
        raise ValueError(f"{malformed} malformed compiler JSONL lines")
    if found != EXPECTED:
        raise ValueError(f"baseline Clippy diagnostics changed: expected={dict(EXPECTED)} observed={dict(found)}")
    return {
        "classification": "EXISTING_UNTOUCHED_UPSTREAM_BASELINE",
        "scope": "unmodified avala-ai/agent-code; strict all-targets Clippy",
        "expected_clippy_errors": sum(found.values()),
        "unexpected_errors": 0,
        "result": "BASELINE_WARNING_SET_CONFIRMED",
        "does_not_prove_patched_clippy_pass": True,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--jsonl", required=True, type=pathlib.Path)
    p.add_argument("--clippy-exit", required=True, type=int)
    args = p.parse_args()
    try:
        print(json.dumps(validate(args.jsonl.read_text(encoding="utf-8"), args.clippy_exit), indent=2))
    except ValueError as exc:
        p.exit(1, f"BASELINE_VERIFICATION_FAILED: {exc}\n")


if __name__ == "__main__":
    main()
