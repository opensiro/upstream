#!/usr/bin/env python3
"""Read-only persistence barrier for a Roadmap-derived outward proposal.

Checks committed GitHub bytes, current refs, canonical reconciliation fields and
exact proposal bytes. This is not semantic novelty, authority or approval.
Historical case inspection and local draft validation remain separate.
"""
import hashlib
import json
from pathlib import Path
import re
import tempfile
from urllib.parse import quote

from aggregate import APIError, api, check_state, read_file, REPOSITORY
from roadmap_view import CASE_ID, SHA, read_text
from validate_capability_roadmap import value
from validate_roadmap_publication import check_publication_ready, REQUIRED_FILES

BLOCKED = "ROADMAP_NOT_READY_FOR_EXTERNAL_PROPOSAL"
VERIFIED = "ROADMAP_PERSISTED_VERIFIED"
ACTIONS = {"original_issue", "fork_issue", "original_discussion", "original_issue_comment"}
DRAFT_FILES = {
    "original_issue": "original-issue-draft.md",
    "original_discussion": "original-discussion-draft.md",
    "original_issue_comment": "maintainer-comment-draft.md",
}
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def current_head(client, repo, branch):
    ref = client.get(api(repo, "git/ref/heads/" + quote(branch, safe="/")))
    head = (ref.get("object") or {}).get("sha")
    if not isinstance(head, str) or not SHA.fullmatch(head):
        raise ValueError("unverified branch HEAD: " + repo + "/" + branch)
    return head


def original_head(client, original):
    info = client.get(api(original, ""))
    if str(info.get("full_name", "")).casefold() != original.casefold():
        raise ValueError("original repository identity unverified")
    branch = info.get("default_branch")
    if not isinstance(branch, str) or not branch:
        raise ValueError("original default branch unverified")
    return current_head(client, original, branch)


def candidate_destination(original, fork, action, destination=None):
    """New objects target the repo; comments must name the exact existing Issue."""
    if action not in ACTIONS:
        raise ValueError("unsupported Roadmap proposal action")
    repo = fork if action == "fork_issue" else original
    base = "https://github.com/" + repo
    if action == "original_issue_comment":
        if not isinstance(destination, str) or not re.fullmatch(
                re.escape(base) + r"/issues/[1-9][0-9]*", destination, re.IGNORECASE):
            raise ValueError("exact original Issue comment destination required")
        return destination
    if destination is not None and destination != base:
        raise ValueError("proposal destination differs from the selected repository")
    return base


def comment_target(client, original, action, destination):
    """Read exact existing Issue state. Full feedback/semantic review is separate."""
    if action != "original_issue_comment":
        return None
    number = destination.rsplit("/", 1)[-1]
    data = client.get(api(original, "issues/" + number))
    if (data.get("pull_request") or data.get("html_url", "").casefold() != destination.casefold()
            or data.get("state") not in {"open", "closed"}
            or not isinstance(data.get("updated_at"), str)
            or not isinstance(data.get("body"), (str, type(None)))
            or not isinstance(data.get("title"), str) or not data["title"].strip()
            or type(data.get("comments")) is not int or data["comments"] < 0):
        raise ValueError("original Issue target unverified")
    return {"url": destination, "state": data["state"], "updated_at": data["updated_at"],
            "title": data.get("title"), "body_sha256": digest((data.get("body") or "").encode("utf-8")),
            "comments": data.get("comments")}


def review_evidence_sha256(report, source_head, destination, target=None):
    """Bind the bounded scan to a canonical reconciliation without self-reference.

    A metadata commit is required to record the reconciliation itself. Exclude
    metadata HEAD/provenance links and observation timestamps here, not from the
    later exact approval/recheck snapshot. Do retain provider state, feedback,
    scope, native search hits, action, title, and concrete user-visible delta.
    """
    def stable(obj):
        if isinstance(obj, dict):
            return {k: stable(v) for k, v in obj.items()
                    if k not in {"generated_at", "observed_at", "meta_head_sha",
                                 "metadata_head_sha", "provenance", "events_seen"}}
        if isinstance(obj, list):
            return [stable(v) for v in obj]
        return obj
    evidence = {"source_head": source_head, "destination": destination, "target": target,
                "scope": report.get("scope"), "coverage": report["coverage"],
                "cases": report["cases"], "publications": report["publications"],
                "candidate": report["preflight"], "warnings": report.get("warnings", [])}
    return digest(json.dumps(stable(evidence), sort_keys=True, ensure_ascii=False,
                             separators=(",", ":")).encode("utf-8"))


def review_field(receipt, name):
    matches = re.findall(r"(?m)^- " + re.escape(name) + r": ([^\r\n]+)$", receipt)
    if len(matches) != 1 or not matches[0].strip():
        raise ValueError("missing/ambiguous canonical " + name)
    return matches[0].strip()


def verify_persisted_case(client, fork, case_id, case_ref, original, source_head,
                          action, destination, title, body, history_sha, local_case=None):
    """Verify the live case, then both existing structural checks on its exact bytes."""
    if (not isinstance(fork, str) or not REPOSITORY.fullmatch(fork)
            or fork.split("/")[0] != "opensiro-contributions"
            or not REPOSITORY.fullmatch(original) or not CASE_ID.fullmatch(case_id)
            or not SHA.fullmatch(case_ref or "") or not SHA.fullmatch(source_head or "")
            or not HEX64.fullmatch(history_sha or "")):
        raise ValueError("verified fork, case, metadata/source pins and history digest required")
    destination = candidate_destination(original, fork, action, destination)
    if not isinstance(title, str) or not title.strip() or "\n" in title or "\r" in title or not isinstance(body, bytes) or not body.strip():
        raise ValueError("exact candidate title/search subject and nonempty body required")
    info = client.get(api(fork, ""))
    if (info.get("fork") is not True or str(info.get("full_name", "")).casefold() != fork.casefold()
            or str((info.get("parent") or {}).get("full_name", "")).casefold() != original.casefold()):
        raise ValueError("working fork parent/identity unverified")
    if current_head(client, fork, "opensiro/meta") != case_ref:
        raise ValueError("claimed case-ref is not current opensiro/meta HEAD")
    if original_head(client, original) != source_head:
        raise ValueError("original HEAD changed; reconcile canonical roadmap first")
    state, _ = read_file(client, fork, ".opensiro/state.json", case_ref)
    check_state(state, fork, original)
    if state["owner_control"] != "ALLOW" or state["attention"] != "ACTIVE":
        raise ValueError("fork owner state is not ACTIVE/ALLOW")
    prefix = ".opensiro/issues/" + case_id + "/"
    files = {name: read_text(client, fork, prefix + name, case_ref).encode("utf-8")
             for name in REQUIRED_FILES}
    if local_case is not None:
        local_case = Path(local_case)
        if local_case.name != case_id:
            raise ValueError("local case directory identity mismatch")
        for name, content in files.items():
            if (local_case / name).read_bytes() != content:
                raise ValueError("local case differs from committed bytes: " + name)
    receipt = files["roadmap.md"].decode("utf-8")
    if (value(receipt, "Original repository") or "").casefold() != original.casefold():
        raise ValueError("canonical original differs from verified fork parent")
    required = {
        "Publication review source HEAD": source_head,
        "Publication review action": action,
        "Publication review destination": destination,
        "Publication review title SHA256": digest(title.encode("utf-8")),
        "Publication review history SHA256": history_sha,
        "Publication review resolution": ("REUSE_EXISTING" if action == "original_issue_comment"
                                          else "NEW_DISTINCT_OUTCOME"),
    }
    for name, expected in required.items():
        if review_field(receipt, name) != expected:
            raise ValueError("canonical reconciliation differs: " + name)
    rationale = review_field(receipt, "Publication review rationale")
    # Both existing validators (validate_case_dir is invoked by check_publication_ready)
    # run against a materialized copy of exactly the provider-returned commit bytes.
    with tempfile.TemporaryDirectory() as tmp:
        case = Path(tmp) / ".opensiro" / "issues" / case_id
        case.mkdir(parents=True)
        (case.parent.parent / "state.json").write_text(json.dumps(state), encoding="utf-8")
        for name, content in files.items():
            (case / name).write_bytes(content)
        errors = check_publication_ready(case)
        if errors:
            raise ValueError("committed canonical case: " + "; ".join(errors))
        if action == "fork_issue":
            from validate_public_issue_payload import render_fork
            expected_title, expected_body = render_fork(case, fork, case_ref)
            if title != expected_title or body != expected_body.encode("utf-8"):
                raise ValueError("exact fork payload differs from committed Human rendering")
        else:
            name = DRAFT_FILES[action]
            stored = read_text(client, fork, prefix + name, case_ref).encode("utf-8")
            if stored != body:
                raise ValueError("exact outbound body differs from committed " + name)
            files[name] = stored
    # Recheck both live refs after reading/validating, including PAUSE/STOP on new meta.
    if current_head(client, fork, "opensiro/meta") != case_ref or original_head(client, original) != source_head:
        raise ValueError("metadata or original HEAD changed during gate")
    return {"status": VERIFIED, "working_fork": fork, "case_id": case_id,
            "case_ref": case_ref, "original": original, "source_head": source_head,
            "action": action, "destination": destination,
            "roadmap_url": f"https://github.com/{fork}/blob/{case_ref}/{prefix}roadmap.md",
            "target_transition": value(receipt, "Target transition"),
            "proposal_decision": value(receipt, "Proposal-stage decision"),
            "research_disposition": value(receipt, "Research disposition"),
            "review_resolution": required["Publication review resolution"],
            "review_rationale": rationale,
            # A mechanical persistence PASS does not demand empirical benefit or
            # decide whether the owner should promote the architecture.
            "promotion_decision": "OWNER_RESERVED",
            "empirical_benefit_required_for_roadmap_proposal": False,
            "history_sha256": history_sha, "title_sha256": digest(title.encode("utf-8")),
            "body_sha256": digest(body),
            "case_files_sha256": {n: digest(b) for n, b in sorted(files.items())}}


GATE_ERRORS = (APIError, OSError, ValueError, KeyError, TypeError, AttributeError)
