#!/usr/bin/env python3
"""Read-only, local candidate-to-existing-proposal linkage preview.

This validates declared candidate identities against a local frozen Index
object and a separately authored batch_proposals.py draft. It does NOT verify
live canonical GitHub, native fit, a human decision, or any stage authorization.
It cannot create a proposal, fork, patch or external pull request.
"""
import argparse
import json
from pathlib import Path
import sys

from assessment_origin_preflight import OriginBlocked, preflight
from batch_proposals import BatchError, load_draft
from inspect_improvement_candidates import CandidateError, inspect


class LinkageBlocked(ValueError):
    """An improvement candidate cannot be linked even for source-only preview."""


def preview_linkage(*, candidate_root, candidate_id, index_root, manifest,
                    proposal_id):
    """Check exact local identities, never promote declared fit to approval."""
    try:
        inventory = inspect(candidate_root)
        hits = [x for x in inventory["candidates"]
                if x["candidate_id"] == candidate_id]
        if len(hits) != 1:
            raise LinkageBlocked("Unknown or duplicate improvement candidate")
        card = hits[0]
        if card["state"] not in {"QUALIFIED", "SELECTED"}:
            raise LinkageBlocked("Improvement candidate is not qualified for proposal linkage")
        if not card["declared_fit_complete"]:
            raise LinkageBlocked("Native fit declarations are incomplete")
        if card["origin_class"] not in {"ASSESSMENT_DERIVED", "ASSESSMENT_INFORMED"}:
            raise LinkageBlocked("This Index-linked route requires assessment-linked origin")
        draft, digest = load_draft(manifest)
        matches = [item for item in draft["candidates"]
                   if item["id"] == proposal_id]
        if len(matches) != 1:
            raise LinkageBlocked("Proposal item ID missing or ambiguous")
        proposal = matches[0]
        if proposal["blockers"]:
            raise LinkageBlocked("Proposal item still has blockers")
        if card["target_repo"].casefold() != proposal["source"].casefold():
            raise LinkageBlocked("Improvement target differs from proposed upstream")
        origin = preflight(
            index_root=index_root,
            index_sha=card["index_sha"],
            assessment_path=card["assessment_path"],
            manifest=manifest,
            candidate_id=proposal_id,
        )
        if origin["assessment_review_ref"] != card["review_ref"]:
            raise LinkageBlocked("Candidate assessed revision differs from the actual Index object")
        if origin["assessed_upstream"].casefold() != card["target_repo"].casefold():
            raise LinkageBlocked("Candidate target differs from the Index assessment")
        if origin["proposal_sha256"] != digest:
            raise LinkageBlocked("Proposal changed between identity preflight checks")
    except (CandidateError, BatchError, OriginBlocked) as exc:
        raise LinkageBlocked(str(exc)) from None

    return {
        "kind": "IMPROVEMENT_CANDIDATE_TO_PROPOSAL_LINKAGE",
        "status": "OFFLINE_LINKAGE_PREVIEW_ONLY",
        "authorization_status": "NOT_APPROVED_NO_GITHUB_WRITES",
        "candidate_selection_authenticated": False,
        "candidate_native_fit_verified": False,
        "live_index_verified": False,
        "upstream_source_freshness_verified": False,
        "proposal_created": False,
        "execution_available": False,
        "improvement_candidate_id": card["candidate_id"],
        "improvement_candidate_state": card["state"],
        "origin_class": card["origin_class"],
        "upstream_source": card["target_repo"],
        "current_target_source_pin_declared": card["source_sha"],
        "index_commit_sha": card["index_sha"],
        "assessment_path": card["assessment_path"],
        "assessment_sha256": origin["assessment_sha256"],
        "assessed_review_ref": origin["assessment_review_ref"],
        "proposal_id": proposal_id,
        "proposal_sha256": digest,
        "proposal_status": draft["status"],
        "unresolved_gates": [
            "Verify actual Index ref/path against live canonical public GitHub",
            "Verify assessment finding, discovery order and origin classification independently",
            "Independently verify all four native-fit claims and fresh target source/PR/policy",
            "Record real owner selection of the qualified candidate and intended proposal",
            "Separate exact-action stage grant and authenticated connected host verification",
            "Reserve external upstream issue/PR publication to its authorized owner",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-root", type=Path, default=Path("candidates"))
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--index-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--proposal-id", required=True)
    args = parser.parse_args(argv)
    try:
        result = preview_linkage(
            candidate_root=args.candidate_root,
            candidate_id=args.candidate_id,
            index_root=args.index_root,
            manifest=args.manifest,
            proposal_id=args.proposal_id,
        )
    except (LinkageBlocked, OSError, ValueError) as exc:
        print("IMPROVEMENT_LINKAGE_BLOCKED: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
