#!/usr/bin/env python3
"""Read-only OpenSiro Control Plane handoff for one proposed test-file change.

A handoff is a proposal identity and confirmation checklist, never operator
approval. Only the host can verify a live user decision and connected rights.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from batch_proposals import BatchError, preview_draft
from connected_stage_adapter import STAGE, StageBlocked, _validate_action


class HandoffError(Exception):
    pass


def handoff(*, manifest, candidate_id, action):
    """Render exactly one prepare_contribution action without network or writes."""
    try:
        _validate_action(action)
        selection = preview_draft(
            manifest, selected_ids=[candidate_id],
            stage_scopes={candidate_id: [STAGE]},
        )
    except (BatchError, StageBlocked) as exc:
        raise HandoffError(str(exc)) from None
    items = [item for item in selection["candidates"]
             if item["id"] == candidate_id and item["selected"]]
    if len(items) != 1:
        raise HandoffError("Candidate absent from proposal")
    item = items[0]
    if item["blockers"] or not item["expected_license"] or not item["proposal"]["evidence_url"]:
        raise HandoffError("Candidate has blockers, unresolved license or missing evidence")
    if action["working_repo"].split("/")[1].casefold() != item["fork_name"].casefold():
        raise HandoffError("Working repo name does not match proposed fork")
    content = action["content"].encode("utf-8")
    return {
        "schema_version": 1,
        "kind": "UPSTREAM_PREPARATION_HANDOFF",
        "status": "ACTION_PREPARED_NOT_AUTHORIZED",
        "authorization_status": "NOT_APPROVED_NO_WRITES",
        "batch_id": selection["batch_id"],
        "revision": selection["revision"],
        "candidate_id": candidate_id,
        "stage": STAGE,
        "upstream_source": item["source"],
        "claimed_evidence_url": item["proposal"]["evidence_url"],
        "expected_license_unverified": item["expected_license"],
        "proposal_sha256": selection["proposal_sha256"],
        "selection_scope_sha256": selection["selection_scope_sha256"],
        "action": {**{k: action[k] for k in (
            "working_repo", "base_branch", "base_sha", "new_branch", "file_path"
        )}, "content_sha256": hashlib.sha256(content).hexdigest(),
            "content_size_bytes": len(content)},
        "required_human_decision": "Approve or decline this exact candidate, stage, repository, pinned base SHA, branch, path and content SHA-256 in the current authenticated conversation. A generic confirmation is not permission for other stages.",
        "runtime_preflight": [
            "fresh upstream issue, contribution policy and license compatibility",
            "connected user has push permission to existing matching public fork",
            "base SHA still matches and proposed branch/file do not exist",
            "trusted current-session approval callback and supported GitHub operations",
        ],
        "execution_available": False,
        "reason": "Planning output only: no connected provider, no authenticated approval and no write operation."
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate an exact read-only Control Plane prepare-stage handoff")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--working-repo", required=True)
    parser.add_argument("--base-branch", required=True)
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--new-branch", required=True)
    parser.add_argument("--file-path", required=True)
    parser.add_argument("--content-file", required=True)
    args = parser.parse_args(argv)
    try:
        source = Path(args.content_file)
        if not source.is_file():
            raise HandoffError("Content file must exist")
        with source.open("rb") as f:
            raw = f.read(49153)
        if len(raw) > 49152:
            raise HandoffError("Content exceeds 48 KiB")
        content = raw.decode("utf-8")
        data = handoff(
            manifest=args.manifest, candidate_id=args.candidate,
            action={"working_repo": args.working_repo, "base_branch": args.base_branch,
                    "base_sha": args.base_sha, "new_branch": args.new_branch,
                    "file_path": args.file_path, "content": content},
        )
    except (HandoffError, UnicodeDecodeError, OSError, ValueError) as exc:
        print("HANDOFF_BLOCKED: " + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
