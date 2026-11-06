#!/usr/bin/env python3
"""Experimental, opt-in Git fast-forward reservation ledger for assessment batches.

This is a reservation primitive, NOT a complete batch admission gate: callers must
independently validate canonical Index provenance and the merged/open PR inventory.
Never force-update the ledger branch or use its existence as publication authority.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path

from assessment_candidate_batches import BatchError, validate
from assessment_batch_conflict_preflight import GithubReader, preflight

LEDGER_REF = "refs/heads/batch-upstream-reservations"
SOURCE = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
EVENT_KEYS = {"action", "batch_id", "sources", "evidence", "event_id"}


def _git(root, *args, input_text=None, allow_failure=False):
    result = subprocess.run(
        ["git", "-C", str(root), *args], input=input_text, text=True,
        capture_output=True, check=False,
    )
    if result.returncode and not allow_failure:
        raise BatchError(f"Git reservation operation failed: {result.stderr.strip()}")
    return result


def _normalize(source):
    if not isinstance(source, str) or not SOURCE.fullmatch(source):
        raise BatchError("Invalid reservation source")
    return source.casefold()


def _sources(values):
    if not isinstance(values, list) or not values or len(values) > 10:
        raise BatchError("Reservation requires a bounded source list")
    normalized = [_normalize(value) for value in values]
    if len(normalized) != len(set(normalized)):
        raise BatchError("Duplicate reservation source, including case aliases")
    return normalized


def replay(ledger):
    """Validate append-only event semantics and return active source ownership."""
    if not isinstance(ledger, dict) or set(ledger) != {"schema_version", "events"}:
        raise BatchError("Invalid reservation ledger schema")
    if type(ledger["schema_version"]) is not int or ledger["schema_version"] != 1:
        raise BatchError("Unsupported reservation ledger version")
    if not isinstance(ledger["events"], list):
        raise BatchError("Invalid reservation events")
    active, live_batches, historical_batches, seen_event_ids = {}, {}, set(), set()
    for event in ledger["events"]:
        if not isinstance(event, dict) or not EVENT_KEYS <= set(event):
            raise BatchError("Invalid reservation event fields")
        action, batch = event["action"], event["batch_id"]
        if (action not in {"CLAIM", "RELEASE"}
                or not isinstance(event["event_id"], str)
                or not re.fullmatch(r"[0-9a-f]{32}", event["event_id"])
                or event["event_id"] in seen_event_ids
                or not isinstance(batch, str)
                or not re.fullmatch(r"assessment-upstream-\d{4}-\d{2}-\d{2}-\d{2}", batch)
                or not isinstance(event["evidence"], str)
                or not event["evidence"].startswith("https://github.com/opensiro/upstream/")):
            raise BatchError("Invalid reservation event identity/evidence")
        seen_event_ids.add(event["event_id"])
        sources = _sources(event["sources"])
        if action == "CLAIM":
            if set(event) != EVENT_KEYS or batch in historical_batches:
                raise BatchError("Duplicate or malformed reservation claim")
            conflict = sorted(set(sources) & set(active))
            if conflict:
                raise BatchError("BLOCKED_CONCURRENT_RESERVATION: " + ", ".join(conflict))
            historical_batches.add(batch)
            live_batches[batch] = sources
            active.update({source: batch for source in sources})
        else:
            if (set(event) != EVENT_KEYS | {"reason"}
                    or not isinstance(event["reason"], str)
                    or len(event["reason"].strip()) < 15
                    or batch not in live_batches or sources != live_batches[batch]):
                raise BatchError("Release requires original live batch and auditable reason")
            for source in sources:
                del active[source]
            del live_batches[batch]
    return active


def fetch_ledger(root, remote):
    """Require an existing GitHub-visible branch; missing visibility fails closed."""
    fetched = _git(root, "fetch", "--no-tags", remote, LEDGER_REF, allow_failure=True)
    if fetched.returncode:
        raise BatchError("BLOCKED_GITHUB_VISIBILITY: reservation branch unavailable")
    parent = _git(root, "rev-parse", "FETCH_HEAD").stdout.strip()
    paths = _git(root, "ls-tree", "-r", "--name-only", parent).stdout.splitlines()
    if paths != ["reservations.json"]:
        raise BatchError("BLOCKED_GITHUB_VISIBILITY: unexpected reservation branch tree")
    raw = _git(root, "show", f"{parent}:reservations.json", allow_failure=True)
    if raw.returncode:
        raise BatchError("BLOCKED_GITHUB_VISIBILITY: missing ledger at reservation ref")
    try:
        ledger = json.loads(raw.stdout)
    except ValueError as exc:
        raise BatchError("Malformed remote reservation ledger") from exc
    replay(ledger)
    return parent, ledger


def claim(root, remote, manifest_path, index_root, evidence, *, write=False,
          preflight_reader=None, own_pr=None):
    """Prepare an atomic cohort claim; non-force Git push is the sole CAS operation."""
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    validate(manifest, index_root)
    if len(manifest["candidates"]) != 5:
        raise BatchError("Claim requires exactly five assessed sources")
    sources = [candidate["source"] for candidate in manifest["candidates"]]
    visibility = None
    if write:
        if preflight_reader is None:
            raise BatchError("BLOCKED_GITHUB_VISIBILITY: live merged/open PR preflight required")
        visibility = preflight(manifest, index_root, preflight_reader, own_pr=own_pr)
        if visibility["status"] != "CLEAR_PREVIEW_ONLY":
            raise BatchError("BLOCKED_DUPLICATE_SOURCE: " + json.dumps(visibility["collisions"]))
    parent, ledger = fetch_ledger(root, remote)
    event = {"action": "CLAIM", "batch_id": manifest["batch_id"],
             "event_id": uuid.uuid4().hex,
             "sources": sources, "evidence": evidence}
    updated = {"schema_version": 1, "events": ledger["events"] + [event]}
    owners = replay(updated)
    receipt = {"batch_id": manifest["batch_id"], "sources": _sources(sources),
               "parent_sha": parent, "status": "PREVIEW_ONLY",
               "reservation_ref": LEDGER_REF, "external_writes_authorized": False,
               "admission_attested": False,
               "visibility": visibility,
               "warning": "Main and open PR refs can change after preflight; CI must revalidate at merge"}
    if not write:
        return receipt
    payload = json.dumps(updated, indent=2, sort_keys=True) + "\n"
    blob = _git(root, "hash-object", "-w", "--stdin", input_text=payload).stdout.strip()
    tree = _git(root, "mktree", input_text=f"100644 blob {blob}\treservations.json\n").stdout.strip()
    commit = _git(root, "commit-tree", tree, "-p", parent,
                  input_text=f"Reserve sources for {manifest['batch_id']}\n").stdout.strip()
    push = _git(root, "push", remote, f"{commit}:{LEDGER_REF}", allow_failure=True)
    if push.returncode:
        error = push.stderr.casefold()
        if "non-fast-forward" in error or "fetch first" in error or "stale info" in error:
            raise BatchError("BLOCKED_CONCURRENT_RESERVATION: non-fast-forward CAS rejected; re-fetch and reconcile")
        raise BatchError("RESERVATION_PUSH_BLOCKED: " + push.stderr.strip())
    receipt.update(status="CLAIMED_CAS", claim_commit=commit,
                   active_source_count=len(owners))
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--index-root", type=Path, required=True)
    parser.add_argument("--git-root", type=Path, default=Path.cwd())
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--evidence", required=True, help="Existing Upstream issue/PR URL")
    parser.add_argument("--own-pr", type=int, help="Proposal's own PR; identity checked against GitHub")
    parser.add_argument("--write-claim", action="store_true", help="Explicit opt-in Git ref write; no external PR")
    args = parser.parse_args(argv)
    try:
        result = claim(args.git_root, args.remote, args.manifest,
                       args.index_root, args.evidence, write=args.write_claim,
                       preflight_reader=GithubReader(os.environ.get("GITHUB_TOKEN")) if args.write_claim else None,
                       own_pr=args.own_pr)
    except (BatchError, ValueError, OSError) as exc:
        parser.exit(2, f"RESERVATION_BLOCKED: {exc}\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
