#!/usr/bin/env python3
"""Compose a verified local Index-object origin with an unapproved Upstream handoff.

No GitHub API, no external write, no live fit/consent attestation.
"""
import argparse
import json
from pathlib import Path
import sys

from assessment_origin_preflight import OriginBlocked, preflight
from control_plane_handoff import HandoffError, handoff


class AssessmentHandoffBlocked(Exception):
    """Cannot produce even a read-only, origin-linked preparation preview."""


def preview_assessment_handoff(*, index_root, index_sha, assessment_path,
                               manifest, candidate_id, action):
    try:
        origin = preflight(
            index_root=index_root, index_sha=index_sha,
            assessment_path=assessment_path, manifest=manifest,
            candidate_id=candidate_id,
        )
        plan = handoff(manifest=manifest, candidate_id=candidate_id, action=action)
    except (OriginBlocked, HandoffError) as exc:
        raise AssessmentHandoffBlocked(str(exc)) from None
    if (origin["proposal_sha256"] != plan["proposal_sha256"]
            or origin["candidate_id"] != plan["candidate_id"]
            or origin["assessed_upstream"].casefold() != plan["upstream_source"].casefold()):
        raise AssessmentHandoffBlocked("Index origin and proposed handoff diverged")
    return {
        "kind": "ASSESSMENT_DRIVEN_UPSTREAM_HANDOFF",
        "status": "ASSESSMENT_DRIVEN_HANDOFF_PREVIEW_ONLY",
        "authorization_status": "NOT_APPROVED_NO_GITHUB_WRITES",
        "execution_available": False,
        "origin": origin,
        "prepare_stage": plan,
        "unresolved_gates": [
            "Verify Index checkout SHA/path against live canonical public GitHub",
            "Independently verify current upstream native need, mechanism, value and scope",
            "Check live upstream issues/PR overlap, policy, license and exact source ref",
            "Obtain an authenticated, exact-stage current-session operator decision",
            "Verify connected actor, repo/fork ancestry, branch, content and write rights",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index-root", type=Path, required=True)
    parser.add_argument("--index-sha", required=True)
    parser.add_argument("--assessment-path", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--working-repo", required=True)
    parser.add_argument("--base-branch", required=True)
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--new-branch", required=True)
    parser.add_argument("--file-path", required=True)
    parser.add_argument("--content-file", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        with args.content_file.open("rb") as src:
            raw = src.read(49153)
        if len(raw) > 49152:
            raise AssessmentHandoffBlocked("Test file exceeds 48 KiB")
        proposed = preview_assessment_handoff(
            index_root=args.index_root, index_sha=args.index_sha,
            assessment_path=args.assessment_path, manifest=args.manifest,
            candidate_id=args.candidate,
            action={
                "working_repo": args.working_repo,
                "base_branch": args.base_branch,
                "base_sha": args.base_sha,
                "new_branch": args.new_branch,
                "file_path": args.file_path,
                "content": raw.decode("utf-8"),
            },
        )
    except (AssessmentHandoffBlocked, UnicodeDecodeError, OSError) as exc:
        print("ASSESSMENT_HANDOFF_BLOCKED: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(proposed, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
