#!/usr/bin/env python3
"""Reconstruct a one-harness Upgrade handoff from current fork-local facts.

This tool makes NO network calls and grants NO publication permission.
Callers MUST independently read back live fork parent, refs, PR and approval.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from contribution_classification import validate_new_contribution
from validate_upgrade_pr_links import NO_REVIEW_PREVIEW, field, validate_pr_links

SHA40 = re.compile(r"^[a-f0-9]{40}$")
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
BRANCH = re.compile(r"^[A-Za-z0-9._/-]+$")
ISSUE = re.compile(r"^https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/issues/[1-9]\d*$")


def _sha(label: str, value: str) -> str:
    if not SHA40.fullmatch(value):
        raise ValueError(f"{label}: expected exact 40-character commit SHA")
    return value


def _read(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected JSON object")
    return data


def render_handoff(*, contribution: dict, state: dict, fork: str,
                   product_branch: str, product_sha: str, meta_sha: str,
                   base_branch: str, review_pr_url: str | None = None,
                   stage: str = "preview") -> str:
    """Source-only, consistent links and a STOP-aware resumable checkpoint."""
    origin = validate_new_contribution(contribution)
    _sha("Product head", product_sha)
    _sha("Metadata head", meta_sha)
    if not REPO.fullmatch(fork) or not fork.startswith("opensiro-contributions/"):
        raise ValueError("Expected verified opensiro-contributions OWNER/REPO")
    if not BRANCH.fullmatch(product_branch) or product_branch not in contribution.get("work_branches", []):
        raise ValueError("Product branch missing or not listed in canonical contribution")
    if not BRANCH.fullmatch(base_branch):
        raise ValueError("Invalid product base branch")
    if state.get("working_fork") != fork or state.get("original_repository") != contribution.get("original_repository"):
        raise ValueError("State/contribution/fork original identity mismatch")
    if state.get("owner_control") != "ALLOW" or state.get("attention") != "ACTIVE":
        raise ValueError("Owner PAUSE/STOP/DORMANT forbids effectful handoff")
    source = contribution.get("original_repository", "")
    if not REPO.fullmatch(source):
        raise ValueError("Invalid selected original repository")
    selected_rev = contribution.get("source_revision", "")
    _sha("Pinned original source", selected_rev)
    evidence = contribution.get("classification_evidence", [])
    source_issues = [u for u in evidence if ISSUE.fullmatch(u) and ISSUE.fullmatch(u).group(1).lower() == source.lower()]
    if not source_issues:
        raise ValueError("Original issue URL missing from canonical classification evidence")
    if review_pr_url is not None:
        p = urlsplit(review_pr_url)
        prefix = f"/{fork}/pull/"
        if p.scheme != "https" or p.netloc != "github.com" or not p.path.startswith(prefix) or not p.path[len(prefix):].isdigit() or p.query or p.fragment:
            raise ValueError("Fork-local review PR URL mismatches the verified fork")
    if stage not in ("preview", "new"):
        raise ValueError("stage must be preview or new")
    if stage == "new" and not review_pr_url:
        raise ValueError("PR_BLOCKED_NO_WRITE: a new external PR requires actual fork-local review PR")
    if stage == "new" and contribution.get("handoff_publication_hold"):
        raise ValueError("PR_BLOCKED_NO_WRITE: explicit owner STOP blocks publication until new exact consent")
    base_url = f"https://github.com/{fork}"
    contribution_id = contribution.get("id", "")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", contribution_id):
        raise ValueError("Invalid stable contribution ID")
    record_url = f"{base_url}/blob/{meta_sha}/.opensiro/contributions/{contribution_id}.json"
    review_field = f"[Review PR]({review_pr_url})" if review_pr_url else NO_REVIEW_PREVIEW
    hold = ("HOLD — prior publication consent is not reusable; owner STOP requires a fresh exact decision."
            if contribution.get("handoff_publication_hold") else
            "NOT AUTHORIZED BY THIS HANDOFF — recheck exact per-action consent.")
    evidence_line = ", ".join(f"[{i+1}]({url})" for i, url in enumerate(contribution.get("native_evidence", [])))
    assessment = contribution.get("assessment_pin", {})
    assessment_url = assessment.get("url", "")
    assessment_current = (
        assessment_url.replace("/blob/" + assessment_url.split("/blob/", 1)[1][:40] + "/", "/blob/main/", 1)
        if "/blob/" in assessment_url else ""
    )
    assessment_links = (
        f"[Current]({assessment_current}) | [Pinned]({assessment_url})"
        f" | reviewed_at={assessment['reviewed_at']}"
        f" | review_ref={assessment['assessed_source_revision']}"
        if assessment_url else "No verified matching general VSM assessment"
    )
    event = contribution.get("last_event_id")
    event_url = (
        f"[Pinned event]({base_url}/blob/{meta_sha}/.opensiro/events/{event}.json)"
        if event else "NOT_RECORDED"
    )
    recorded_prs = contribution.get("external_prs", [])
    return "\n".join([
        "## Resumable Upgrade handoff — source-only, not publication approval",
        f"**Selected original:** [{source}](https://github.com/{source})",
        f"**Pinned original source:** [{selected_rev}](https://github.com/{source}/commit/{selected_rev})",
        f"**Original source request:** {source_issues[0]}",
        f"**Contribution ID:** `{contribution_id}`",
        f"**Improvement origin:** {origin} — {contribution['classification_rationale']}",
        f"**Working fork:** [{fork}]({base_url})",
        f"**Implementation branch:** [{product_branch}]({base_url}/tree/{product_branch})",
        f"**Implementation commit:** [`{product_sha}`]({base_url}/commit/{product_sha})",
        f"**Fork-local review PR:** {review_field}",
        f"**Fork-local metadata record:** [{contribution_id}]({record_url})",
        f"**Fork-local owner state:** [Pinned state]({base_url}/blob/{meta_sha}/.opensiro/state.json)",
        f"**Last attributable event:** {event_url}",
        f"**VSM assessment:** {assessment_links}",
        f"**Recorded external PR URLs (not live states):** {recorded_prs}",
        f"**Read-only code diff:** [base → implementation]({base_url}/compare/{base_branch}...{product_branch})",
        f"**Native evidence:** {evidence_line or 'NOT_RECORDED'}",
        f"**Known test gaps:** {contribution.get('validation_summary', {}).get('not_validated', 'UNKNOWN')}",
        f"**Next action:** {contribution.get('next_action', 'UNKNOWN')}",
        f"**Publication gate:** {hold}",
    ]) + "\n"



def validate_body_against_handoff(*, body: str, stage: str, fork: str,
                                  product_branch: str, product_sha: str,
                                  meta_sha: str, contribution_id: str,
                                  review_pr_url: str | None,
                                  contribution: dict) -> None:
    """Check the actual draft body, including exact refs, not only URL shapes."""
    errors = validate_pr_links(body, stage)
    repo_url = f"https://github.com/{fork}"
    for label, target in (
        ("Working fork", repo_url),
        ("Implementation branch", f"{repo_url}/tree/{product_branch}"),
        ("Implementation commit", f"{repo_url}/commit/{product_sha}"),
        ("Fork-local metadata record",
         f"{repo_url}/blob/{meta_sha}/.opensiro/contributions/{contribution_id}.json"),
    ):
        line_value = next((line for line in body.splitlines() if line.startswith(f"**{label}:**")), "")
        if f"]({target})" not in line_value:
            errors.append(f"{label}: body differs from independently verified handoff")
    line_value = next((line for line in body.splitlines() if line.startswith("**Fork-local review PR:**")), "")
    if review_pr_url and f"]({review_pr_url})" not in line_value:
        errors.append("Fork-local review PR: body differs from actual verified review URL")
    if not review_pr_url and NO_REVIEW_PREVIEW not in line_value:
        errors.append("Fork-local review PR: absent PR must be explicitly NOT_CREATED in preview")
    origin = contribution.get("contribution_type")
    if not str(field(body, "Improvement origin") or "").startswith(f"{origin} — "):
        errors.append("Improvement origin: does not match canonical contribution type")
    original = contribution["original_repository"]
    source_issue = next(
        (url for url in contribution.get("classification_evidence", [])
         if ISSUE.fullmatch(url) and ISSUE.fullmatch(url).group(1).lower() == original.lower()),
        None,
    )
    if source_issue and source_issue not in str(field(body, "Original source request") or ""):
        errors.append("Original source request: differs from pinned contribution evidence")
    pin = contribution.get("assessment_pin")
    if pin:
        if pin["url"] not in str(field(body, "VSM assessment (when verified)") or ""):
            errors.append("VSM assessment: wrong pinned Index evidence")
        if pin["reviewed_at"] not in str(field(body, "Assessment date") or ""):
            errors.append("Assessment date: mismatch with pinned Index review")
        if pin["assessed_source_revision"] not in str(field(body, "Assessed source revision") or ""):
            errors.append("Assessed source revision: mismatch with pinned Index review")
    if errors:
        raise ValueError("PR_BLOCKED_NO_WRITE: " + "; ".join(dict.fromkeys(errors)))

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--contribution", required=True, type=Path)
    p.add_argument("--state", required=True, type=Path)
    p.add_argument("--fork", required=True)
    p.add_argument("--branch", required=True)
    p.add_argument("--head", required=True)
    p.add_argument("--meta-sha", required=True)
    p.add_argument("--base", required=True)
    p.add_argument("--review-pr-url")
    p.add_argument("--body-file", type=Path, help="Exact proposed public PR body to check")
    p.add_argument("--stage", choices=("preview", "new"), default="preview")
    args = p.parse_args()
    try:
        contribution = _read(args.contribution)
        state = _read(args.state)
        packet = render_handoff(
            contribution=contribution, state=state, fork=args.fork,
            product_branch=args.branch, product_sha=args.head, meta_sha=args.meta_sha,
            base_branch=args.base, review_pr_url=args.review_pr_url, stage=args.stage,
        )
        if args.stage == "new" and not args.body_file:
            raise ValueError("new external publication requires --body-file for exact-body preflight")
        if args.body_file:
            validate_body_against_handoff(
                body=args.body_file.read_text(encoding="utf-8"), stage=args.stage,
                fork=args.fork, product_branch=args.branch, product_sha=args.head,
                meta_sha=args.meta_sha, contribution_id=contribution["id"],
                review_pr_url=args.review_pr_url, contribution=contribution,
            )
        print(packet, end="")
        print("BODY_PREFLIGHT_PASS_NOT_PUBLICATION_APPROVAL" if args.body_file
              else "BODY_PREFLIGHT_NOT_RUN — no PR publication action permitted")
    except (OSError, ValueError, TypeError, KeyError) as e:
        p.error(f"PR_BLOCKED_NO_WRITE: {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
