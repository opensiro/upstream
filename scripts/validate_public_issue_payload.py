#!/usr/bin/env python3
"""Fail-closed check for the exact title/body presented and submitted as a public Roadmap Issue."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from validate_capability_roadmap import value
from validate_roadmap_publication import (
    check_publication_ready, headings_match, required_labels, unfilled_placeholders,
    HUMAN_LABELS, TEMPLATE, ROW, FUNCTIONS,
)

DRAFT = "DRAFT — NOT PUBLISHED"
PUBLIC = "PUBLIC FORK ROADMAP PROPOSAL"
TITLE_MARKER = "**Public fork Issue title (draft only):**"
ORIGINAL_SECTIONS = [
    "Proposal in the project's own terms",
    "How we reached this proposal — Opensiro VSM assessment",
    "Why this particular construction?",
    "Proposed approach and validation",
    "Feedback requested",
    "Three independent ways to participate",
    "Research attribution and AI disclosure",
]
ORIGINAL_FIELDS = (
    "What exists today", "What may be missing", "Closest existing project-native solution",
    "Existing discussion", "Historical assessment", "Boundary", "Current original HEAD",
    "Whole-repository prioritization", "Construction hypothesis", "Native building blocks",
    "Minimal proposed addition", "Scope exclusions", "Hypothesized benefit", "How to falsify",
    "Cost status", "AI involvement",
)


def accepted_version(receipt, *aliases):
    """Read historical version without renaming legacy canonical receipt fields.

    Missing or inconsistent aliases must fail closed; this only normalizes
    provenance key spelling, never an Index grade or permission.
    """
    values = {v for key in aliases if (v := value(receipt, key))}
    return next(iter(values)) if len(values) == 1 else None


def accepted_profile_skills_versions(receipt):
    """Resolve historical Profile/Skills pins, including a legacy combined receipt.

    Never resolve a contradictory pair by preferring one spelling.
    """
    profiles = {v for key in ("Accepted Profile version", "Profile version")
                if (v := value(receipt, key))}
    skills = {v for key in ("Accepted Methodology version",
                           "Accepted Skills methodology version",
                           "Skills methodology version",
                           "Assessment procedure version")
              if (v := value(receipt, key))}
    combined = value(receipt, "Profile / Skills procedure")
    if combined:
        parsed = re.fullmatch(
            r"\s*(\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?)\s*/\s*"
            r"(\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?)\s*", combined)
        if not parsed:
            return None, None
        profiles.add(parsed.group(1))
        skills.add(parsed.group(2))
    if len(profiles) != 1 or len(skills) != 1:
        return None, None
    return next(iter(profiles)), next(iter(skills))


def checksum(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def render_fork(case, repo, ref):
    case = case.resolve()
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("invalid destination")
    if not re.fullmatch(r"[0-9a-f]{40}", ref):
        raise ValueError("immutable fork commit SHA required")
    if case.parent.name != "issues" or case.parent.parent.name != ".opensiro":
        raise ValueError("expected .opensiro/issues/<case-id>")
    state = json.loads((case.parent.parent / "state.json").read_text(encoding="utf-8"))
    if (state.get("working_fork") != repo or state.get("attention") != "ACTIVE"
            or state.get("owner_control") != "ALLOW"):
        raise ValueError("fork identity or owner state mismatch")
    human = (case / "issue.md").read_text(encoding="utf-8")
    title_match = re.search(r"(?m)^\*\*Public fork Issue title \(draft only\):\*\*\s*(.+?)\s*$", human)
    if not title_match or "**Public fork Issue body (draft only):**" not in human:
        raise ValueError("missing canonical fork publication draft markers")
    body = human.split("\n" + TITLE_MARKER, 1)[0].rstrip()
    if DRAFT not in body:
        raise ValueError("missing draft status")
    body = body.replace(DRAFT, PUBLIC)
    base = "https://github.com/" + repo + "/blob/" + ref + "/.opensiro/issues/" + case.name + "/"
    for filename in ("roadmap.md", "issue.md", "constructor-sufficiency.md"):
        body = body.replace("](" + filename + ")", "](" + base + filename + ")")
    return title_match.group(1).strip(), body + "\n"


def check_payload(kind, case, repo, ref, title, body, source_head=""):
    errors = ["canonical case: " + e for e in check_publication_ready(case)]
    if errors:
        return errors
    if not title.strip() or "\n" in title or len(title) > 256:
        errors.append("invalid title")
    if not body.startswith("# ") or not body.endswith("\n"):
        errors.append("full Markdown body with final newline required")
    if TITLE_MARKER in body or "**Public fork Issue body (draft only):**" in body:
        errors.append("draft-only publication instructions remain in body")
    errors += unfilled_placeholders(title + "\n" + body, "public payload")
    if source_head and (not re.fullmatch(r"[0-9a-f]{40}", source_head) or source_head not in body):
        errors.append("observed current original HEAD is not in published body")
    if kind == "fork":
        try:
            expected_title, expected_body = render_fork(case, repo, ref)
            if (title, body) != (expected_title, expected_body):
                errors.append("fork payload differs from deterministic canonical Human Issue rendering")
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            errors.append("fork render failed: " + str(exc))
        errors += headings_match(body, TEMPLATE / "FORK_CAPABILITY_ROADMAP_ISSUE.md", "public body")
        errors += required_labels(body, HUMAN_LABELS, "public body")
        for fn in FUNCTIONS:
            if sum(row == fn for row in ROW.findall(body)) != 1:
                errors.append("missing accepted six-function row: " + fn)
        if DRAFT in body:
            errors.append("draft status in public body")
    elif kind == "original":
        if not title.startswith("Proposal: ") or "Opensiro VSM architecture review" not in title:
            errors.append("external template title mismatch")
        if re.findall(r"(?m)^## (.+?)\s*$", body) != ORIGINAL_SECTIONS:
            errors.append("external template seven section mismatch")
        for field in ORIGINAL_FIELDS:
            if not re.search(r"(?m)^\*\*" + re.escape(field) + r":\*\*\s*\S", body):
                errors.append("external missing populated field: " + field)
        receipt = (case / "roadmap.md").read_text(encoding="utf-8")
        vector = dict(part.split("=", 1) for part in value(receipt, "Accepted VSM vector").split(" · "))
        for fn in FUNCTIONS:
            rows = re.findall(r"(?m)^\|\s*\*\*" + re.escape(fn)
                              + r"\s*·[^|]*\*\*\s*\|[^|]*\|\s*([^|]*?)\s*\|", body)
            if len(rows) != 1 or rows[0].strip() != vector.get(fn):
                errors.append("external accepted vector row mismatch: " + fn)
        for key in ("Accepted Index commit", "Accepted assessment blob SHA",
                    "Accepted review ref", "Accepted reviewed at"):
            v = value(receipt, key)
            if not v or v not in body:
                errors.append("external missing historical pin: " + key)
        profile_version, skills_version = accepted_profile_skills_versions(receipt)
        for key, observed in (("Accepted Profile version", profile_version),
                              ("Accepted Methodology version", skills_version)):
            if not observed or observed not in body:
                errors.append("external missing or conflicting historical pin: " + key)
        for grade in ("A", "C", "P", "A(P)", "C(P)", "—", "?"):
            if chr(96) + grade + chr(96) not in body:
                errors.append("external missing state definition: " + grade)
        if "NOT_MEASURED" not in body:
            errors.append("external cost must be NOT_MEASURED")
    return list(dict.fromkeys(errors))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--kind", choices=("fork", "original"), required=True)
    p.add_argument("--case-dir", type=Path, required=True)
    p.add_argument("--repo", required=True)
    p.add_argument("--case-ref", required=True)
    p.add_argument("--title-file", type=Path, required=True)
    p.add_argument("--body-file", type=Path, required=True)
    p.add_argument("--source-head", default="")
    p.add_argument("--render-fork", action="store_true")
    a = p.parse_args()
    if a.render_fork:
        if a.kind != "fork":
            p.error("--render-fork requires --kind fork")
        early = check_publication_ready(a.case_dir)
        if early:
            print("PUBLICATION_BLOCKED_TEMPLATE_MISMATCH: " + "; ".join(early))
            return 1
        try:
            title, body = render_fork(a.case_dir, a.repo, a.case_ref)
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            print("PUBLICATION_BLOCKED_TEMPLATE_MISMATCH: " + str(exc))
            return 1
        a.title_file.write_text(title + "\n", encoding="utf-8")
        a.body_file.write_text(body, encoding="utf-8")
    try:
        title = a.title_file.read_text(encoding="utf-8").rstrip("\n")
        body = a.body_file.read_text(encoding="utf-8")
    except OSError as exc:
        print("PUBLICATION_BLOCKED_TEMPLATE_MISMATCH: " + str(exc))
        return 1
    errors = check_payload(a.kind, a.case_dir, a.repo, a.case_ref, title, body, a.source_head)
    if errors:
        for error in errors:
            print("PUBLICATION_BLOCKED_TEMPLATE_MISMATCH: " + error)
        return 1
    print("PUBLIC_ISSUE_PAYLOAD_PREFLIGHT_PASS_NOT_PUBLICATION_APPROVAL "
          + "title_sha256=" + checksum(title) + " body_sha256=" + checksum(body))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
