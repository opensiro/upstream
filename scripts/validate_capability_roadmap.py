#!/usr/bin/env python3
"""Structural check for a plan-only roadmap snapshot, NOT external/source validation."""

from __future__ import annotations

import re
import sys
from pathlib import Path

SECTIONS = (
    "Identity and pins",
    "Rights and authority",
    "Existing work / overlap",
    "Function ownership",
    "Capability priority",
    "Implementation options",
    "Specification and domain alternatives",
    "Cost experiment",
    "Delivery and publication",
)
FIELDS = (
    "Original repository",
    "Original HEAD",
    "Observed at",
    "Accepted Index assessment",
    "Accepted assessment blob SHA",
    "Accepted review ref",
    "Accepted reviewed at",
    "System in focus",
)
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
URL = re.compile(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/(?:blob|commit|issues|pull)/[^\s)]+")
OUTCOMES = ("PLAN_ONLY", "NEEDS_EVIDENCE", "NO_USEFUL_CHANGE")


def value(contents: str, key: str) -> str | None:
    match = re.search(r"^- "+re.escape(key)+r":\s*(.+?)\s*$", contents, re.M)
    return match.group(1).strip() if match else None


def validate(contents: str) -> list[str]:
    errors = []
    for section in SECTIONS:
        if not re.search(r"^## "+re.escape(section)+r"\s*$", contents, re.M):
            errors.append("missing section: "+section)
    for field in FIELDS:
        if not value(contents,field):
            errors.append("missing field: "+field)

    for field,pattern in (
        ("Original repository",REPO),
        ("Original HEAD",HEX40),
        ("Accepted assessment blob SHA",HEX40),
        ("Accepted review ref",HEX40),
        ("Observed at",DATE),
        ("Accepted reviewed at",DATE),
    ):
        actual=value(contents,field)
        if actual and not pattern.fullmatch(actual):
            errors.append("invalid format: "+field)
    on_top = value(contents, "Receipt contract")
    if on_top in ("contribution-on-top", "proposal-gate"):
        if not re.search(r"^## Parallel contribution-on-top review\s*$", contents, re.M):
            errors.append("missing section: Parallel contribution-on-top review")
        for key in ("Evaluation object", "Existing-work overlap",
                    "Our on-top contribution", "Incremental benefit", "Decision scope"):
            if not value(contents, key):
                errors.append("missing field: " + key)
        if on_top == "proposal-gate":
            for key in ("Target transition", "Proposed C construction", "C sufficiency falsifier",
                        "Scenario basis", "Proposal-stage decision",
                        "Proposed validation", "Validation state", "Proposal falsifier"):
                if not value(contents, key):
                    errors.append("missing field: " + key)
            transition = value(contents, "Target transition")
            if transition:
                match = re.fullmatch(
                    r"S(1|2|3\*|3|4|5)=(—|\?|A|C|P|A\(P\)|C\(P\))\s*->\s*"
                    r"S(1|2|3\*|3|4|5)=C", transition
                )
                if not match or match.group(1) != match.group(3):
                    errors.append("invalid Target transition: same VSM function must target C")
            basis = value(contents, "Scenario basis")
            if basis and basis not in ("OBSERVED", "HYPOTHETICAL"):
                errors.append("invalid Scenario basis: expected OBSERVED or HYPOTHETICAL")
            decision = value(contents, "Proposal-stage decision")
            if decision and decision not in ("GO", "NO_GO", "BLOCKED"):
                errors.append("invalid Proposal-stage decision")
            validation = value(contents, "Validation state")
            if validation and validation not in ("NOT_RUN", "PARTIAL_WITH_PINNED_EVIDENCE"):
                errors.append("invalid Validation state: cannot claim proof at proposal stage")
    elif on_top is not None:
        errors.append("unknown Receipt contract: " + on_top)
    idx=value(contents,"Accepted Index assessment")
    if idx and not idx.startswith("https://github.com/opensiro/vsm-harness-index/blob/"):
        errors.append("Index assessment must be pinned to a GitHub blob URL")
    if idx and "/blob/main/" in idx:
        errors.append("Index assessment must use a frozen commit, not main")
    result=value(contents,"Result")
    if result not in OUTCOMES:
        errors.append("missing/invalid Result (narrative only)")
    if value(contents,"External issue") != "DRAFT — NOT PUBLISHED":
        errors.append("external issue must be explicitly DRAFT — NOT PUBLISHED")
    if value(contents,"Cost status") != "NOT_MEASURED":
        errors.append("cost status must remain NOT_MEASURED until independently measured")
    if not URL.search(contents):
        errors.append("no first-party GitHub source link")
    if "[placeholder]" in contents.lower() or "TODO" in contents:
        errors.append("unresolved placeholder")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_capability_roadmap.py <receipt.md>",file=sys.stderr)
        return 2
    path=Path(argv[1])
    if not path.is_file():
        print("roadmap receipt not found",file=sys.stderr)
        return 2
    errors=validate(path.read_text(encoding="utf-8"))
    if errors:
        print("\n".join(errors),file=sys.stderr)
        return 1
    print("Plan-only roadmap receipt structural contract: PASS (not semantic review)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
