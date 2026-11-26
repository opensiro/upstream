#!/usr/bin/env python3
"""Fail-closed local template/file preflight for Roadmap case writes and external PRs.

This checks *local syntax and document completeness* only. Accepted Index/source,
fork identity, tests, original Issue/PR states and current owner consent require
separate independent live readback. PASS does not authorize publication.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from validate_capability_roadmap import validate_case_dir, value

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates"
REQUIRED_FILES = ("README.md", "roadmap.md", "issue.md", "constructor-sufficiency.md")
NUMBERED = re.compile(r"(?m)^## (\d+)\. (.+?)\s*$")
LEVEL_TWO = re.compile(r"(?m)^## (.+?)\s*$")
ROW = re.compile(r"(?m)^\|\s*\*\*(S1|S2|S3\*|S3|S4|S5)\s*·")
FUNCTIONS = ("S1", "S2", "S3", "S3*", "S4", "S5")

HUMAN_LABELS = (
    "One-sentence proposal",
    "Canonical decision receipt",
    "Technical companion",
    "Working fork",
    "Case",
    "Repository-wide audit",
    "Priority rationale",
    "Deliberate exclusions / methodology challenge",
    "Target transition",
    "Function-specific disturbance",
    "Proposed C capability (P0)",
    "Best native operator alternative",
    "Expected user benefit",
    "Architectural sufficiency argument",
    "Track A — native coverage",
    "Track B — independent on-top C construction",
    "Distinctness and falsifier",
    "Proposed C-sufficiency verdict",
    "Future positive test",
    "Future negative test",
    "Proposed falsifier",
    "Validation state",
    "Original-native contribution",
    "Profile / Skills",
    "Domain fork",
    "Proposal-stage decision",
    "Research disposition",
    "Decision reason / next permitted step",
    "Agent/developer handoff",
    "Rights and publication",
    "AI disclosure",
)
AI_LABELS = (
    "Source and mode boundary",
    "Target transition",
    "Six-function dependencies (S1/S2/S3/S3*/S4/S5)",
    "Function witness",
    "Counterfactual owner test",
    "Possible methodological negative control",
    "Contributor / maintainer priorities",
    "Original native workflow",
    "Closest existing solution",
    "Relevant original Issues/PRs",
    "On-top distinctness",
    "Source ambiguity / rights blockers",
    "Required property",
    "Architectural C-sufficiency argument",
    "Explicit non-goals",
    "Implementation dependency graph",
    "P0 and P1",
    "P2",
    "Alternative path",
    "Stop",
    "Native test commands and entry points",
    "Positive functional closure",
    "Independent alternative (where applicable)",
    "Negative authority and compatibility (where applicable)",
    "Matched native alternative",
    "Proposal-stage decision",
    "Research disposition",
    "Primary falsifier",
    "Validation state",
    "Ownership of truth",
    "Cost status",
    "Next permitted action",
    "Human backlink",
    "case receipt",
    "AI disclosure",
)

PLACEHOLDER = re.compile(r"\[(?![^\]\n]*\]\()([^\]\n]{2,180})\]")
UNFILLED_WORDS = (
    "HARNESS", "selected", "accepted", "actual", "pinned", "Full current",
    "Current shipped", "source link", "Exact ", "Original ", "Source-backed",
    "Developer's new", "Minimum ", "Real source", "Independently", "Function-specific",
)


def headings_match(actual: str, template_path: Path, file_name: str) -> list[str]:
    template = template_path.read_text(encoding="utf-8")
    required = NUMBERED.findall(template)
    found = NUMBERED.findall(actual)
    actual_level_two = LEVEL_TWO.findall(actual)
    errors: list[str] = []
    # Prevent appended versioned Human/AI refinements from bypassing the
    # numbered template checks; nested ### evidence sections remain permitted.
    if len(actual_level_two) != len(found):
        errors.append(f"{file_name}: unexpected top-level section outside numbered template")
    if len(found) != len(required):
        errors.append(f"{file_name}: template requires {len(required)} numbered sections, found {len(found)}")
    for i, (number, title) in enumerate(required):
        if i >= len(found):
            errors.append(f"{file_name}: missing template section {number}. {title}")
            continue
        observed_number, observed_title = found[i]
        # Only the template's explicit [selected function] heading placeholder varies.
        escaped = re.escape(title).replace(re.escape("[selected function]"), r".+")
        if observed_number != number or not re.fullmatch(escaped, observed_title):
            errors.append(f"{file_name}: section {number} template mismatch; expected '{title}'")
    return errors


def required_labels(body: str, labels: tuple[str, ...], file_name: str) -> list[str]:
    errors = []
    for label in labels:
        # Named template labels may be followed by another bold label on one line.
        pat = r"\*\*" + re.escape(label) + r":\*\*\s*([^\n]+)"
        match = re.search(pat, body)
        filled = match.group(1).split("**", 1)[0].strip() if match else ""
        if not filled:
            errors.append(f"{file_name}: missing or empty template field: {label}")
    return errors


def unfilled_placeholders(body: str, filename: str) -> list[str]:
    errors = []
    # Reject template scaffolding, not Markdown links or legitimate architecture notation.
    for match in PLACEHOLDER.finditer(body):
        token = match.group(1)
        if token.startswith(UNFILLED_WORDS) or token in ("GO / NO_GO / BLOCKED", "DECISION_READY / NEEDS_EVIDENCE / NO_USEFUL_CHANGE"):
            errors.append(f"{filename}: unfilled template placeholder: [{token[:48]}]")
    return errors


def check_case_structure(case_dir: Path, *, experimental_target: str | None = None, reference_realization: bool = False) -> list[str]:
    """Shared Human/AI structure. Experimental use is draft-only, never publication readiness."""
    errors = [f"missing required roadmap case file: {n}" for n in REQUIRED_FILES
              if not (case_dir / n).is_file()]
    if errors:
        return errors
    errors.extend(validate_case_dir(case_dir, experimental_target=experimental_target, reference_realization=reference_realization))
    human = (case_dir / "issue.md").read_text(encoding="utf-8")
    ai = (case_dir / "constructor-sufficiency.md").read_text(encoding="utf-8")
    readme = (case_dir / "README.md").read_text(encoding="utf-8")
    receipt = (case_dir / "roadmap.md").read_text(encoding="utf-8")
    for name, body in (("issue.md", human), ("constructor-sufficiency.md", ai), ("README.md", readme)):
        if not body.lstrip().startswith("# "):
            errors.append(f"{name}: document title missing")
        errors.extend(unfilled_placeholders(body, name))
    if experimental_target:
        human_template = "EXPERIMENTAL_ROADMAP_HUMAN.md"
        ai_template = "EXPERIMENTAL_ROADMAP_AI.md"
        human_labels = tuple({
            "Proposed C capability (P0)": "Proposed target capability (P0)",
            "Track B — independent on-top C construction": "Track B — independent on-top target construction",
            "Proposed C-sufficiency verdict": "Proposed target-sufficiency verdict",
        }.get(label, label) for label in HUMAN_LABELS)
        ai_labels = tuple("Architectural target-sufficiency argument" if label == "Architectural C-sufficiency argument" else label for label in AI_LABELS)
        for name, body in (("issue.md", human), ("constructor-sufficiency.md", ai), ("README.md", readme)):
            if "EXPERIMENTAL — DRAFT ONLY" not in body:
                errors.append(name + ": missing experimental draft-only marker")
    else:
        if any("EXPERIMENTAL — DRAFT ONLY" in body for body in (human, ai, readme)):
            errors.append("experimental draft cannot enter the production C gate")
        human_template = "FORK_CAPABILITY_ROADMAP_ISSUE.md"
        ai_template = "ROADMAP_AI_CONSTRUCTOR_CONTRACT.md"
        human_labels, ai_labels = HUMAN_LABELS, AI_LABELS
    errors.extend(headings_match(human, TEMPLATE / human_template, "issue.md"))
    errors.extend(headings_match(ai, TEMPLATE / ai_template, "constructor-sufficiency.md"))
    errors.extend(required_labels(human, human_labels, "issue.md"))
    errors.extend(required_labels(ai, ai_labels, "constructor-sufficiency.md"))
    for p in ("**P0:**", "**P1:**", "**P2:**"):
        if not re.search(r"(?m)^\s*-\s*" + re.escape(p) + r"\s*\S", human):
            errors.append(f"issue.md: missing populated priority {p}")
    if "**PLAN_ONLY" not in human or "DRAFT — NOT PUBLISHED" not in human:
        errors.append("issue.md: missing explicit PLAN_ONLY / DRAFT — NOT PUBLISHED status")
    if "**DRAFT — NOT PUBLISHED**" not in ai:
        errors.append("constructor-sufficiency.md: missing explicit draft status")
    if "Why Opensiro" not in human:
        errors.append("issue.md: missing Why Opensiro motivation")
    for fn in FUNCTIONS:
        if len([x for x in ROW.findall(human) if x == fn]) != 1:
            errors.append(f"issue.md: expected exactly one central six-function row for {fn}")
    historical = value(receipt, "Local VSM vector" if reference_realization else "Accepted VSM vector")
    if historical and historical not in human:
        errors.append("issue.md: central historical accepted Index vector missing or mismatched")
    for phrase in ("LOCAL REFERENCE ASSESSMENT" if reference_realization else "ACCEPTED HISTORICAL INDEX", "ownership categories", "not quality ranks"):
        if phrase.lower() not in human.lower():
            errors.append(f"issue.md: missing template interpretation: {phrase}")
    if "NOT_MEASURED" not in human or "NOT_MEASURED" not in ai:
        errors.append("issue.md/constructor-sufficiency.md: cost hypothesis must be NOT_MEASURED")
    if "[roadmap.md](roadmap.md)" not in readme or "[issue.md](issue.md)" not in readme or "[constructor-sufficiency.md](constructor-sufficiency.md)" not in readme:
        errors.append("README.md: missing canonical Human/AI/receipt links")
    if reference_realization and "accepted historical index" in human.lower():
        errors.append("local reference Human draft must not claim accepted Index provenance")
    # Do not let a populated template masquerade as external communication permission.
    return list(dict.fromkeys(errors))


def check_publication_ready(case_dir: Path) -> list[str]:
    """Production C gate; experimental A/P cases always fail closed."""
    return check_case_structure(case_dir)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("case_dir", type=Path, help="Complete four-file Roadmap case directory (pre-write draft or verified committed fork copy)")
    args = p.parse_args(argv)
    errors = check_publication_ready(args.case_dir)
    if errors:
        for error in errors:
            print("PR_BLOCKED_NO_WRITE: " + error)
        return 1
    print("ROADMAP_TEMPLATE_PREFLIGHT_PASS_NOT_PUBLICATION_APPROVAL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
