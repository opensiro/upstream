#!/usr/bin/env python3
"""Fail-closed check for the exact title/body presented and submitted as a public Roadmap Issue."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from validate_capability_roadmap import value
from aggregate import GitHub
from roadmap_proposal_gate import (BLOCKED, VERIFIED, GATE_ERRORS, digest,
    review_evidence_sha256, verify_persisted_case)
from preflight_publication_destination import (markdown_feature_template_requirements,
                                            markdown_feature_payload_errors)
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


def accepted_index_commit(receipt):
    """Use a direct Index commit pin or derive it from an immutable Index assessment URL.

    The two representations must agree when both are provided. Never
    resolve a branch URL, a mutable ref or a conflicting SHA by guessing.
    """
    explicit = value(receipt, "Accepted Index commit")
    index_url = value(receipt, "Accepted Index assessment")
    pin = None
    if index_url:
        match = re.fullmatch(
            r"https://github\.com/opensiro/vsm-harness-index/blob/"
            r"([0-9a-f]{40})/assessments/[A-Za-z0-9_./-]+\.md",
            index_url.strip())
        if not match:
            return None
        pin = match.group(1)
    if explicit and not re.fullmatch(r"[0-9a-f]{40}", explicit):
        return None
    if explicit and pin and explicit != pin:
        return None
    return explicit or pin


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


def original_section_layout_errors(body, native_markdown_template=None):
    """Keep seven OpenSiro evidence sections even when the provider has 5 ## fields.

    No template: existing seven-## contract. Native Markdown template: provider
    headings are the exactly checked ## sections; all seven OpenSiro evidence
    sections appear as ### beneath provider 'Additional Context'. This is not
    an exemption from provider requirements or a permit to publish.
    """
    if native_markdown_template is None:
        return ([] if re.findall(r"(?m)^## (.+?)\s*$", body) == ORIGINAL_SECTIONS
                else ["external template seven section mismatch"])
    try:
        spec = markdown_feature_template_requirements(native_markdown_template)
    except ValueError as exc:
        return ["native Markdown feature template not verified: " + str(exc)]
    errors = []
    if re.findall(r"(?m)^## (.+?)\s*$", body) != spec["required_sections"]:
        errors.append("native Markdown top-level feature sections mismatch")
    errors.extend(markdown_feature_payload_errors(spec, body))
    if re.findall(r"(?m)^### (.+?)\s*$", body) != ORIGINAL_SECTIONS:
        errors.append("nested original template seven section mismatch")
    tail = body.split("## Additional Context\n", 1)
    if len(tail) != 2 or ("### " + ORIGINAL_SECTIONS[0]) not in tail[1]:
        errors.append("nested original sections must be under native Additional Context")
    return list(dict.fromkeys(errors))


def check_payload(kind, case, repo, ref, title, body, source_head="", native_markdown_template=None):
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
        errors.extend(original_section_layout_errors(body, native_markdown_template))
        for field in ORIGINAL_FIELDS:
            if not re.search(r"(?m)^\*\*" + re.escape(field) + r":\*\*\s*\S", body):
                errors.append("external missing populated field: " + field)
        receipt = (case / "roadmap.md").read_text(encoding="utf-8")
        errors += original_case_lineage_errors(receipt, repo, body)
        vector = dict(part.split("=", 1) for part in value(receipt, "Accepted VSM vector").split(" · "))
        for fn in FUNCTIONS:
            rows = re.findall(r"(?m)^\|\s*\*\*" + re.escape(fn)
                              + r"\s*·[^|]*\*\*\s*\|[^|]*\|\s*([^|]*?)\s*\|", body)
            if len(rows) != 1 or rows[0].strip() != vector.get(fn):
                errors.append("external accepted vector row mismatch: " + fn)
        index_commit = accepted_index_commit(receipt)
        if not index_commit or index_commit not in body:
            errors.append("external missing or conflicting historical pin: Accepted Index commit")
        for key in ("Accepted assessment blob SHA", "Accepted review ref", "Accepted reviewed at"):
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


def original_case_lineage_errors(receipt, original_repo, original_body):
    """Check the external text has the SAME original and Sx target as its case.

    This is a deterministic identity/target guard, not a semantic review or
    permission to publish. Other gates check historical grades and provenance.
    """
    errors = []
    canonical_original = value(receipt, "Original repository")
    if not canonical_original or canonical_original.casefold() != original_repo.casefold():
        errors.append("external original destination differs from canonical case")
    transition = value(receipt, "Target transition")
    if not transition:
        errors.append("canonical case target transition is missing")
    elif (transition not in original_body and
          transition.replace(" -> ", " → ") not in original_body):
        errors.append("external proposal target differs from canonical case")
    return errors


def verify_issue_approval_case(client, report, kind, case, repo, ref, title, body, source_head):
    """Bind a live remote readback to the exact previously checked history/payload."""
    proof = report.get("roadmap_gate", {})
    context = report.get("review_context", {})
    pre = report.get("preflight", {})
    action = kind + "_issue"
    if (proof.get("status") != VERIFIED
            or report.get("recheck", {}).get("status") == "CHANGED_OR_UNVERIFIED"
            or pre.get("candidate_kind") != action
            or pre.get("candidate_title") != title
            or pre.get("case_id") != case.name
            or proof.get("case_ref") != ref
            or proof.get("source_head") != source_head
            or context.get("source_head") != source_head
            or context.get("destination") != "https://github.com/" + repo
            or not report.get("coverage", {}).get("scan_complete")
            or pre.get("search_errors")
            or pre.get("status") in {"ALREADY_PUBLISHED", "REUSE_EXISTING"}
            or (kind == "original" and pre.get("status") == "HISTORY_UNVERIFIED")):
        raise ValueError("current exact persisted case/history approval report required")
    history_sha = review_evidence_sha256(report, source_head, context["destination"],
                                         context.get("target"))
    if history_sha != report.get("review_evidence_sha256"):
        raise ValueError("bounded reconciliation digest does not match history report")
    snapshot = report.get("candidate_snapshot") or {}
    if (snapshot.get("original_head") != source_head
            or snapshot.get("title_sha256") != digest(title.encode("utf-8"))
            or snapshot.get("body_sha256") != digest(body)):
        raise ValueError("exact approval-time source/title/body snapshot mismatch")
    fork = proof.get("working_fork")
    original = repo if kind == "original" else proof.get("original")
    if kind == "fork" and fork != repo:
        raise ValueError("fork approval destination mismatch")
    if pre.get("original") != original:
        raise ValueError("history original identity mismatch")
    actual = verify_persisted_case(client, fork, case.name, ref, original, source_head,
                                   action, context["destination"], title, body,
                                   history_sha, local_case=case)
    if actual != proof:
        raise ValueError("persisted case proof changed; re-read and re-review")
    return actual


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--kind", choices=("fork", "original"), required=True)
    p.add_argument("--case-dir", type=Path, required=True)
    p.add_argument("--repo", required=True)
    p.add_argument("--case-ref", required=True)
    p.add_argument("--title-file", type=Path, required=True)
    p.add_argument("--body-file", type=Path, required=True)
    p.add_argument("--source-head", default="")
    p.add_argument("--native-markdown-template-file", type=Path,
                   help="verified first-party Markdown Feature Request template for original; used with live route preflight")
    p.add_argument("--render-fork", action="store_true")
    p.add_argument("--draft-only", action="store_true",
                   help="local structural preparation only; never an approval preview")
    p.add_argument("--history-report", type=Path,
                   help="fresh publication_history.py report for the exact committed candidate")
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
        body_bytes = a.body_file.read_bytes()
        body = body_bytes.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print("PUBLICATION_BLOCKED_TEMPLATE_MISMATCH: " + str(exc))
        return 1
    native_markdown_template = None
    if a.native_markdown_template_file:
        if a.kind != "original":
            p.error("--native-markdown-template-file is only for original Issues")
        try:
            native_markdown_template = a.native_markdown_template_file.read_text(encoding="utf-8")
        except OSError as exc:
            print("PUBLICATION_BLOCKED_TEMPLATE_MISMATCH: native Markdown template unreadable: " + str(exc))
            return 1
    errors = check_payload(a.kind, a.case_dir, a.repo, a.case_ref, title, body,
                           a.source_head, native_markdown_template)
    if errors:
        for error in errors:
            print("PUBLICATION_BLOCKED_TEMPLATE_MISMATCH: " + error)
        return 1
    if a.draft_only:
        print("LOCAL_DRAFT_PAYLOAD_PASS_NOT_APPROVAL_READY "
              + "title_sha256=" + checksum(title) + " body_sha256=" + digest(body_bytes))
        return 0
    try:
        if not a.history_report:
            raise ValueError("--history-report required; use --draft-only for local preparation")
        report = json.loads(a.history_report.read_text(encoding="utf-8"))
        proof = verify_issue_approval_case(
            GitHub(os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")), report,
            a.kind, a.case_dir, a.repo, a.case_ref, title, body_bytes, a.source_head)
    except GATE_ERRORS as exc:
        print(BLOCKED + ": " + str(exc))
        return 1
    print(VERIFIED + " case_ref=" + proof["case_ref"] + " roadmap=" + proof["roadmap_url"])
    print("PUBLIC_ISSUE_PAYLOAD_PREFLIGHT_PASS_NOT_PUBLICATION_APPROVAL "
          + "title_sha256=" + checksum(title) + " body_sha256=" + digest(body_bytes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
