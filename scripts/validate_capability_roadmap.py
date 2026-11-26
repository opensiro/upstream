#!/usr/bin/env python3
"""Structural check for a plan-only roadmap snapshot, NOT external/source validation."""

from __future__ import annotations

import hashlib
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
REFERENCE_REPO = "opensiro/vsm-oss-organization"
REFERENCE_FIELDS = ("Local assessment source", "Local assessment SHA-256",
                    "Local assessed ref", "Local assessed at", "Profile ref", "Methodology ref")
INDEX_FIELDS = ("Accepted Index assessment", "Accepted assessment blob SHA",
                "Accepted review ref", "Accepted reviewed at")
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


EXPERIMENTAL_CONTRACT = "experimental-proposal-gate"
EXPERIMENTAL_TARGETS = ("A", "P")
EXPERIMENTAL_FIELDS = (
    "Target family", "Current selected function state", "Mode preservation",
    "Prospective authority", "Cross-function authority compatibility",
)


def experimental_transition_errors(contents: str, target: str, *, reference_realization: bool = False) -> list[str]:
    """Check proposed ownership transition; never attest source truth or authority."""
    errors = []
    if value(contents, "Target family") != target:
        errors.append("experimental Target family must match explicit target")
    transition = value(contents, "Target transition")
    decision = value(contents, "Proposal-stage decision")
    current = value(contents, "Current selected function state")
    preservation = value(contents, "Mode preservation")
    if transition == f"NO_QUALIFIED_{target}_TARGET":
        if decision != "NO_GO" or current != "NONE" or preservation != "NOT_APPLICABLE":
            errors.append("experimental no-target requires NO_GO, NONE current, NOT_APPLICABLE mode preservation")
        return errors
    match = re.fullmatch(
        r"(S1|S2|S3\*|S3|S4|S5)=(—|\?|A|C|P|A\(P\)|C\(P\))\s*->\s*"
        r"(S1|S2|S3\*|S3|S4|S5)=(A|C|P|A\(P\)|C\(P\))",
        transition or "",
    )
    if not match or match[1] != match[3]:
        return errors + ["invalid experimental Target transition: same function required"]
    fn, before, _, after = match.groups()
    vector = parse_vector(value(contents, "Local VSM vector" if reference_realization else "Accepted VSM vector") or "")
    if vector and vector[fn] != before:
        errors.append("Target transition disagrees with accepted historical VSM vector")
    if (target == "A" and after not in ("A", "A(P)")) or (
        target == "P" and after not in ("P", "A(P)", "C(P)")
    ) or (target == "C" and (not reference_realization or fn == "S1" or after not in ("C", "C(P)"))):
        errors.append("transition does not match experimental Target family")
    parent_eligible = fn in ("S3", "S4", "S5")
    if not parent_eligible and (target == "P" or "P" in after or "P" in (current or "")):
        errors.append("parent mode is allowed only for S3, S4, S5")
    if current not in STATES:
        errors.append("invalid Current selected function state")
        return errors
    if current == "?":
        if decision != "BLOCKED" or preservation != "UNRESOLVED":
            errors.append("unresolved current state requires BLOCKED and UNRESOLVED mode preservation")
        return errors
    # Current source, not historical grades, determines whether a mode is added.
    # An already-established target may be a scoped NO_GO, not a new GO.
    existing_a = current in ("A", "A(P)")
    existing_p = current in ("P", "A(P)", "C(P)")
    if decision == "GO" and ((target == "A" and existing_a) or (target == "P" and existing_p) or (target == "C" and (existing_a or current in ("C", "C(P)")))):
        errors.append("GO cannot propose an already established target mode")
    if preservation not in ("PRESERVE", "REPLACE"):
        errors.append("resolved mode preservation must be PRESERVE or REPLACE")
    if preservation == "PRESERVE":
        expected = ("C(P)" if existing_p else "C") if target == "C" else ("A(P)" if existing_p else "A") if target == "A" else (
            "A(P)" if existing_a else "C(P)" if current in ("C", "C(P)") else "P"
        )
        if after != expected:
            errors.append("target transition conflicts with preserved current modes")
    if preservation == "REPLACE" and after != target:
        errors.append("REPLACE must target standalone selected family")
    if not value(contents, "Mode rationale"):
        errors.append("missing Mode rationale: source-grounded preservation or hypothetical replacement")
    return errors


def validate(contents: str, *, experimental_target: str | None = None, reference_realization: bool = False) -> list[str]:
    errors = []
    for section in SECTIONS:
        if not re.search(r"^## "+re.escape(section)+r"\s*$", contents, re.M):
            errors.append("missing section: "+section)
    if reference_realization:
        if experimental_target not in ("C", "P", "A") or value(contents, "Original repository") != REFERENCE_REPO:
            return errors + ["reference route requires exact VSM OSS identity and explicit C/P/A target"]
        if any(value(contents, key) is not None for key in (*INDEX_FIELDS, "Accepted VSM vector")):
            errors.append("reference receipt must not assert accepted Index fields")
        local_source = value(contents, "Local assessment source") or ""
        if not re.fullmatch(r"https://github\.com/opensiro/vsm-oss-organization/(?:issues/[1-9][0-9]*|blob/[0-9a-f]{40}/[^\s]+)", local_source):
            errors.append("local assessment source must be an Organization issue or immutable blob")
        for key, pattern in (
            ("Local assessment SHA-256", re.compile(r"[0-9a-f]{64}")),
            ("Local assessed ref", HEX40), ("Local assessed at", DATE),
            ("Profile ref", re.compile(r"https://github\.com/opensiro/vsm-harness-profile/blob/[0-9a-f]{40}/[^\s]+")),
            ("Methodology ref", re.compile(r"https://github\.com/opensiro/vsm-harness-skills/blob/[0-9a-f]{40}/[^\s]+")),
        ):
            if not pattern.fullmatch(value(contents, key) or ""):
                errors.append("invalid or missing local provenance: " + key)
        fields = tuple(key for key in FIELDS if key not in INDEX_FIELDS) + REFERENCE_FIELDS
    else:
        if any(value(contents, key) is not None for key in (*REFERENCE_FIELDS[:4], "Local VSM vector")):
            errors.append("local reference receipt cannot enter ordinary Roadmap gates")
        fields = FIELDS
    vector_key = "Local VSM vector" if reference_realization else "Accepted VSM vector"
    for field in fields:
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
    if experimental_target is not None:
        if experimental_target not in (("C", "A", "P") if reference_realization else EXPERIMENTAL_TARGETS) or on_top != EXPERIMENTAL_CONTRACT:
            return errors + ["explicit experimental target requires experimental-proposal-gate"]
    elif on_top == EXPERIMENTAL_CONTRACT or value(contents, "Target family") in EXPERIMENTAL_TARGETS:
        return errors + ["experimental receipt is not a production C Roadmap"]
    if on_top in ("contribution-on-top", "proposal-gate", EXPERIMENTAL_CONTRACT):
        if not re.search(r"^## Parallel contribution-on-top review\s*$", contents, re.M):
            errors.append("missing section: Parallel contribution-on-top review")
        for key in ("Evaluation object", "Existing-work overlap",
                    "Our on-top contribution", "Incremental benefit", "Decision scope"):
            if not value(contents, key):
                errors.append("missing field: " + key)
        if on_top in ("proposal-gate", EXPERIMENTAL_CONTRACT):
            for key in ("Repository-wide source map", "Priority rationale",
                        vector_key, "Target transition", "P1 dependencies",
                        "P2 optional",
                        "Proposed target construction" if experimental_target else "Proposed C construction",
                        "Target sufficiency falsifier" if experimental_target else "C sufficiency falsifier",
                        "Scenario basis", "Proposal-stage decision", "Research disposition",
                        "Proposed validation", "Validation state", "Proposal falsifier"):
                if not value(contents, key):
                    errors.append("missing field: " + key)
            for fn in ("S1", "S2", "S3", "S3*", "S4", "S5"):
                if not value(contents, fn + " disposition"):
                    errors.append("missing field: " + fn + " disposition")
            historical = value(contents, vector_key)
            if historical and not parse_vector(historical):
                errors.append("invalid " + vector_key + ": require six ordered Skills states")
            disposition = value(contents, "Research disposition")
            if disposition and disposition not in ("DECISION_READY", "NEEDS_EVIDENCE", "NO_USEFUL_CHANGE"):
                errors.append("invalid Research disposition")
            transition = value(contents, "Target transition")
            if experimental_target:
                for key in EXPERIMENTAL_FIELDS:
                    if not value(contents, key):
                        errors.append("missing experimental field: " + key)
                errors.extend(experimental_transition_errors(contents, experimental_target, reference_realization=reference_realization))
            elif transition == "NO_QUALIFIED_C_TARGET":
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


def validate_case_dir(directory: Path, *, experimental_target: str | None = None, reference_realization: bool = False) -> list[str]:
    """Structural consistency: three public-source case files, no GitHub lookups."""
    needed = {name: directory / name
              for name in ("roadmap.md", "issue.md", "constructor-sufficiency.md")}
    errors = ["missing case file: " + name for name, path in needed.items()
              if not path.is_file()]
    if errors:
        return errors
    receipt = needed["roadmap.md"].read_text(encoding="utf-8")
    errors.extend(validate(receipt, experimental_target=experimental_target, reference_realization=reference_realization))
    if reference_realization:
        evidence = directory / "local-assessment-source.md"
        if not evidence.is_file():
            errors.append("missing local-assessment-source.md evidence attachment")
        elif hashlib.sha256(evidence.read_bytes()).hexdigest() != value(receipt, "Local assessment SHA-256"):
            errors.append("local assessment evidence digest mismatch")
    expected_contract = EXPERIMENTAL_CONTRACT if experimental_target else "proposal-gate"
    if value(receipt, "Receipt contract") != expected_contract:
        return errors  # grandfather historical read-only receipts
    human = needed["issue.md"].read_text(encoding="utf-8")
    ai = needed["constructor-sufficiency.md"].read_text(encoding="utf-8")
    for name, body in (("issue.md", human), ("constructor-sufficiency.md", ai)):
        if "[roadmap.md](roadmap.md)" not in body:
            errors.append(name + " must link canonical roadmap.md")
        keys = ("Target transition", "Proposal-stage decision", "Research disposition")
        if experimental_target:
            keys += EXPERIMENTAL_FIELDS
        for key in keys:
            label = key
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
    vector = parse_vector(value(receipt, "Local VSM vector" if reference_realization else "Accepted VSM vector") or "")
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
