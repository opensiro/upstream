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


def validate(text, exit_code, side="baseline"):
    if side not in ("baseline", "patched"):
        raise ValueError(f"unknown provenance side {side}")
    found, malformed = errors_from_jsonl(text)
    if exit_code == 0:
        raise ValueError("strict Clippy succeeded; a known-fail comparison cannot claim success")
    if malformed:
        raise ValueError(f"{malformed} malformed compiler JSONL lines")
    if side == "baseline":
        if found != EXPECTED:
            raise ValueError(f"baseline Clippy diagnostics changed: expected={dict(EXPECTED)} observed={dict(found)}")
    elif set(found) != set(EXPECTED) or any(n > 2 for n in found.values()):
        # Cargo --all-targets may emit the same lib diagnostic twice (lib and
        # test targets). Compare unique source locations and bound multiplicity.
        # Any new lint, file or line is rejected, not suppressed.
        raise ValueError(f"patched Clippy diagnostic locations changed: expected={list(EXPECTED)} observed={dict(found)}")
    return {
        "classification": ("UNMODIFIED_UPSTREAM_BASELINE" if side == "baseline"
                           else "PATCHED_UPSTREAM_BASELINE_PARITY"),
        "scope": side + " avala-ai/agent-code; unqualified strict all-targets Clippy",
        "unique_existing_diagnostics": len(found),
        "diagnostic_instances": sum(found.values()),
        "unexpected_diagnostic_locations": 0,
        "result": ("BASELINE_WARNING_SET_CONFIRMED" if side == "baseline"
                   else "NO_NEW_DIAGNOSTIC_LOCATIONS"),
        "does_not_prove_unqualified_strict_clippy_pass": True,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--jsonl", required=True, type=pathlib.Path)
    p.add_argument("--clippy-exit", required=True, type=int)
    p.add_argument("--side", required=True, choices=("baseline", "patched"))
    args = p.parse_args()
    try:
        print(json.dumps(validate(args.jsonl.read_text(encoding="utf-8"), args.clippy_exit, side=args.side), indent=2))
    except ValueError as exc:
        p.exit(1, f"BASELINE_VERIFICATION_FAILED: {exc}\n")


if __name__ == "__main__":
    main()
