#!/usr/bin/env python3
"""Source-only syntactic preflight for required Upgrade PR provenance links.

Does not query GitHub, grant publication permission or verify native tests.
Use first-party ref/PR readback and exact owner consent as separate gates.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
from urllib.parse import urlsplit

LABELS = (
    "Working fork",
    "Implementation branch",
    "Implementation commit",
    "Fork-local review PR",
    "Fork-local metadata record",
)
REQUIRED_DISCLOSURE_FIELDS = (
    "AI involvement",
    "Original source request",
    "Improvement origin",
    "VSM assessment (when verified)",
    "Native validation",
    "Human/publication status",
    "Authority",
)
SHA40 = re.compile(r"^[0-9a-f]{40}$")
FORK_NAME = re.compile(r"^[A-Za-z0-9._-]+$")
STABLE_ID = re.compile(r"^[A-Za-z0-9._-]+$")
NO_REVIEW_PREVIEW = "NOT_CREATED — awaiting exact fork-local PR consent"
NO_REVIEW_HISTORICAL = "NOT_CREATED — historical PR; no prior fork-local review PR"


def field(body: str, label: str) -> str | None:
    match = re.search(r"^\*\*" + re.escape(label) + r":\*\*\s*(.+)$", body, re.M)
    return match.group(1).strip() if match else None


def linked_url(body: str, label: str, errors: list[str]) -> str | None:
    value = field(body, label)
    if value is None:
        errors.append(f"{label}: required field missing")
        return None
    match = re.search(r"\[[^\]]+\]\((https://github\.com/[^)\s]+)\)", value)
    if not match:
        errors.append(f"{label}: required clickable GitHub link missing")
        return None
    url = match.group(1)
    u = urlsplit(url)
    if (u.scheme != "https" or u.netloc != "github.com" or u.query or u.fragment
            or not u.path.startswith("/opensiro-contributions/")):
        errors.append(f"{label}: URL must be a clean opensiro-contributions GitHub URL")
        return None
    return url


def validate_pr_links(body: str, stage: str = "new") -> list[str]:
    """Return structural defects in a prospective PR body.

    stage=new: new third-party publication; actual fork review PR required.
    stage=preview: unpublished fork PR proposal; review link may be pending.
    stage=historical: already-published PR correction; missing review may be
    disclosed, never backfilled as an invented historical event.
    """
    if stage not in ("new", "preview", "historical"):
        raise ValueError("stage must be new, preview or historical")

    errors: list[str] = []
    if "<!-- opensiro-ai-assessment-disclosure:review-gated -->" not in body:
        errors.append("AI disclosure marker missing")
    for label in REQUIRED_DISCLOSURE_FIELDS:
        if field(body, label) is None:
            errors.append(f"{label}: required disclosure field missing")

    fork_url = linked_url(body, "Working fork", errors)
    fork = None
    if fork_url:
        bits = urlsplit(fork_url).path.strip("/").split("/")
        if len(bits) != 2 or not FORK_NAME.fullmatch(bits[1]) or "<" in fork_url:
            errors.append("Working fork: expected exact organization/fork repository URL")
        else:
            fork = bits[1]

    for label in LABELS[1:]:
        value = field(body, label)
        if label == "Fork-local review PR" and value and value.startswith("NOT_CREATED"):
            valid = (stage == "preview" and value == NO_REVIEW_PREVIEW) or (
                stage == "historical" and value == NO_REVIEW_HISTORICAL)
            if not valid:
                errors.append("Fork-local review PR: missing real review PR blocks a new PR or has invalid status")
            continue
        url = linked_url(body, label, errors)
        if not url:
            continue
        parts = urlsplit(url).path.strip("/").split("/")
        if len(parts) < 3:
            errors.append(f"{label}: URL missing artifact path")
            continue
        if fork and parts[1] != fork:
            errors.append(f"{label}: working fork identity mismatch")
        remainder = parts[2:]
        if label == "Implementation branch":
            if len(remainder) < 2 or remainder[0] != "tree" or any(
                not p or "<" in p or ">" in p for p in remainder[1:]
            ):
                errors.append("Implementation branch: expected /tree/<actual-branch>")
        elif label == "Implementation commit":
            if len(remainder) != 2 or remainder[0] != "commit" or not SHA40.fullmatch(remainder[1]):
                errors.append("Implementation commit: expected exact 40-character SHA")
        elif label == "Fork-local review PR":
            if len(remainder) != 2 or remainder[0] != "pull" or not remainder[1].isdigit() or int(remainder[1]) < 1:
                errors.append("Fork-local review PR: expected existing /pull/<number>")
        elif label == "Fork-local metadata record":
            if (len(remainder) != 5 or remainder[0] != "blob"
                    or not SHA40.fullmatch(remainder[1])
                    or remainder[2:4] != [".opensiro", "contributions"]
                    or not remainder[4].endswith(".json")
                    or not STABLE_ID.fullmatch(remainder[4][:-5])):
                errors.append("Fork-local metadata record: expected pinned meta SHA and .opensiro/contributions/<id>.json")

    assessment = field(body, "VSM assessment (when verified)")
    if assessment is not None and "No verified matching general VSM assessment" not in assessment:
        current = re.search(
            r"https://github\.com/opensiro/vsm-harness-index/blob/main/assessments/[A-Za-z0-9._/-]+\.md",
            assessment,
        )
        pinned = re.search(
            r"https://github\.com/opensiro/vsm-harness-index/blob/([0-9a-f]{40})/assessments/[A-Za-z0-9._/-]+\.md",
            assessment,
        )
        if not current or not pinned:
            errors.append("VSM assessment: expected current and 40-character pinned Index links")
        else:
            current_path = current.group(0).split("/main/", 1)[1]
            pinned_path = pinned.group(0).split("/" + pinned.group(1) + "/", 1)[1]
            if current_path != pinned_path:
                errors.append("VSM assessment: current/pinned paths mismatch")
        date = field(body, "Assessment date")
        if not date or not re.search(r"\b\d{4}-\d{2}-\d{2}\b", date):
            errors.append("Assessment date: missing reviewed_at date")
        source = field(body, "Assessed source revision")
        if not source or not re.search(r"\b[0-9a-f]{40}\b", source):
            errors.append("Assessed source revision: missing 40-character review_ref")
    if "without a separate human approval of this PR" in body:
        errors.append("Historical standing-mandate disclosure is not permitted in new review-gated text")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("body_file", type=Path)
    parser.add_argument("--stage", choices=("new", "preview", "historical"), default="new")
    args = parser.parse_args()
    errors = validate_pr_links(args.body_file.read_text(encoding="utf-8"), args.stage)
    for error in errors:
        print(f"PR_BLOCKED_NO_WRITE: {error}")
    if errors:
        return 1
    print("STRUCTURAL_LINK_PREFLIGHT_PASS_NOT_PUBLICATION_APPROVAL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
