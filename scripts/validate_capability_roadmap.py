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


FUNCTIONS = ("S1", "S2", "S3", "S3*", "S4", "S5")
STATES = ("A", "A(P)", "C", "C(P)", "P", "—", "?")
REPORT_STATES = ("DECISION_READY", "NEEDS_EVIDENCE", "NO_USEFUL_CHANGE")


def parse_vector(vector: str) -> dict[str, str] | None:
    """Parse a single pinned Skills ownership vector, not six quality scores."""
    parts = [x.strip() for x in vector.split("·")] if "·" in vector else vector.split()
    if len(parts) != 6:
        return None
    out = {}
    for fn, part in zip(FUNCTIONS, parts):
        key, sep, state = part.partition("=")
        if not sep or key != fn or state not in STATES:
            return None
        if fn in ("S1", "S2", "S3*") and "P" in state:
            return None
        out[key] = state
    return out


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
            for key in ("Repository-wide source map", "Priority rationale",
                        "Accepted VSM vector", "Target transition", "P1 dependencies",
                        "P2 optional", "Proposed C construction", "C sufficiency falsifier",
                        "Scenario basis", "Proposal-stage decision", "Research disposition",
                        "Proposed validation", "Validation state", "Proposal falsifier"):
                if not value(contents, key):
                    errors.append("missing field: " + key)
            for fn in ("S1", "S2", "S3", "S3*", "S4", "S5"):
                if not value(contents, fn + " disposition"):
                    errors.append("missing field: " + fn + " disposition")
            historical = value(contents, "Accepted VSM vector")
            if historical and not parse_vector(historical):
                errors.append("invalid Accepted VSM vector: require six ordered Skills states")
            disposition = value(contents, "Research disposition")
            if disposition and disposition not in ("DECISION_READY", "NEEDS_EVIDENCE", "NO_USEFUL_CHANGE"):
                errors.append("invalid Research disposition")
            transition = value(contents, "Target transition")
            if transition == "NO_QUALIFIED_C_TARGET":
                if value(contents, "Proposal-stage decision") != "NO_GO":
                    errors.append("NO_QUALIFIED_C_TARGET requires NO_GO")
            elif transition:
                match = re.fullmatch(
                    r"S(1|2|3\*|3|4|5)=(—|\?|A|C|P|A\(P\)|C\(P\))\s*->\s*"
                    r"S(1|2|3\*|3|4|5)=C", transition
                )
                if not match or match.group(1) != match.group(3):
                    errors.append("invalid Target transition: same VSM function must target C")
                elif historical:
                    vector = parse_vector(historical)
                    if vector and vector.get("S" + match.group(1)) != match.group(2):
                        errors.append("Target transition disagrees with accepted historical VSM vector")
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


def display_value(text: str, label: str) -> str | None:
    """Read an explicit Human/AI receipt-derived field, not descriptive prose."""
    m = re.search(r"^\*\*" + re.escape(label) + r":\*\*\s*(.+?)\s*$", text, re.M)
    return m.group(1).strip().strip("`") if m else None


def validate_case_dir(directory: Path) -> list[str]:
    """Structural consistency: three public-source case files, no GitHub lookups."""
    needed = {name: directory / name
              for name in ("roadmap.md", "issue.md", "constructor-sufficiency.md")}
    errors = ["missing case file: " + name for name, path in needed.items()
              if not path.is_file()]
    if errors:
        return errors
    receipt = needed["roadmap.md"].read_text(encoding="utf-8")
    errors.extend(validate(receipt))
    if value(receipt, "Receipt contract") != "proposal-gate":
        return errors  # grandfather historical read-only receipts
    human = needed["issue.md"].read_text(encoding="utf-8")
    ai = needed["constructor-sufficiency.md"].read_text(encoding="utf-8")
    for name, body in (("issue.md", human), ("constructor-sufficiency.md", ai)):
        if "[roadmap.md](roadmap.md)" not in body:
            errors.append(name + " must link canonical roadmap.md")
        for label, key in (("Target transition", "Target transition"),
                           ("Proposal-stage decision", "Proposal-stage decision"),
                           ("Research disposition", "Research disposition")):
            observed = display_value(body, label)
            expected = value(receipt, key)
            if observed is None:
                errors.append(name + " missing receipt-derived field: " + label)
            elif observed != expected:
                errors.append(name + " " + label + " disagrees with roadmap.md")
    if "[constructor-sufficiency.md](constructor-sufficiency.md)" not in human:
        errors.append("issue.md must link constructor-sufficiency.md")
    if "[issue.md](issue.md)" not in ai:
        errors.append("constructor-sufficiency.md must link issue.md")
    vector = parse_vector(value(receipt, "Accepted VSM vector") or "")
    if vector:
        for fn in FUNCTIONS:
            pat = r"(?m)^\|\s*\*\*" + re.escape(fn) + r"\s*·[^|]*\|\s*([^|]+)\|"
            m = re.search(pat, human)
            if not m:
                errors.append("issue.md missing combined six-function row: " + fn)
            elif m.group(1).strip().strip("`* ") != vector[fn]:
                errors.append("issue.md historical state differs from roadmap.md: " + fn)
    if re.search(r"(?m)^\|\s*\*\*S1\s*·", ai):
        errors.append("AI contract must reference, not duplicate, Human six-function table")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_capability_roadmap.py <receipt.md|case-dir>",file=sys.stderr)
        return 2
    path=Path(argv[1])
    if not path.is_file() and not path.is_dir():
        print("roadmap receipt or case directory not found",file=sys.stderr)
        return 2
    errors=(validate_case_dir(path) if path.is_dir()
            else validate(path.read_text(encoding="utf-8")))
    if errors:
        print("\n".join(errors),file=sys.stderr)
        return 1
    print("Plan-only roadmap receipt/case structural contract: PASS (not semantic review)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
