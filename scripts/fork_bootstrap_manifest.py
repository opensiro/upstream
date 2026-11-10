#!/usr/bin/env python3
"""Generate a reviewable, non-executable one-time org-fork bootstrap proposal.

Nothing in this module issues a GitHub write or a dev-alpha-2 permit. The
proposal's hashes bind a selection for *future* human/host preflight; they are
neither authenticated consent nor source/actor/permission attestations.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

import contribution_workspaces as workspaces


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path("data/contribution-workspaces/fork-bootstrap-proposal.json")
DESTINATION = "opensiro-contributions"
BATCH_SIZE = 10
NAME = re.compile(r"[A-Za-z0-9_.-]{1,100}\Z")
EXTRA_HOLDS = {
    "TRACK_ONLY_NO_CHANGE",
    "TRACK_ONLY_REEVALUATE_EVIDENCE",
    "HISTORICAL_PR_TRACK_ONLY_NO_NEW_PUBLICATION",
}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def _order(inventory, root):
    """Keep the frozen 100 in their original priority order, then all extras."""
    pool = workspaces.read(root / workspaces.POOL)
    first = [item["source"].casefold() for field, _ in workspaces.POOL_GROUPS
             for item in pool[field]]
    records = {r["source"].casefold(): r for r in inventory["sources"]}
    workspaces.require(len(first) == len(set(first)) == 100,
                       "Duplicate or incomplete frozen priority pool")
    workspaces.require(set(first).issubset(records),
                       "Priority identity missing from source registry")
    ordered = [records[k] for k in first]
    ordered += [v for k, v in sorted(records.items()) if k not in set(first)]
    return ordered


def _propose_name(row):
    source = row["source"]
    owner, basename = source.split("/", 1)
    mapped = row.get("proposed_fork")
    if mapped is not None:
        workspaces.require(mapped.casefold().startswith(DESTINATION + "/"),
                           f"Unexpected destination for {source}")
        name = mapped.split("/", 1)[1]
        was_renamed = False
    else:
        workspaces.require(row["fork_state"] ==
                           "NAME_COLLISION_REQUIRES_EXACT_DECISION",
                           f"Unexplained missing proposed fork for {source}")
        # A *proposed* unambiguous alternative, never an actual reserved name.
        name = owner + "--" + basename
        was_renamed = True
    workspaces.require(bool(NAME.fullmatch(name)),
                       f"Fork name requires human resolution: {source}: {name}")
    return name, was_renamed


def build(root=ROOT, inventory=None):
    root = Path(root)
    if inventory is None:
        inventory = workspaces.build(root)
    workspaces.require(inventory.get("schema_version") == 1
                       and inventory["counts"]["unique_sources"] ==
                           len(inventory["sources"]),
                       "Invalid source/fork registry")
    raw_registry = workspaces.encoded(inventory)
    rows = _order(inventory, root)
    seen_sources = set()
    seen_names = {}
    sources = []
    candidates = []
    for row in rows:
        source = row["source"]
        key = workspaces.key(source)
        workspaces.require(key not in seen_sources,
                           f"Duplicate source identity: {source}")
        seen_sources.add(key)
        name, renamed = _propose_name(row)
        destination = f"{DESTINATION}/{name}"
        old = seen_names.setdefault(destination.casefold(), source)
        workspaces.require(old == source,
                           f"Proposed destination collision: {destination}, {old}, {source}")
        existing = row["fork_state"] in {
            "HISTORICAL_MAPPING_REQUIRES_LIVE_READBACK",
            "DATED_MAPPING_REQUIRES_LIVE_READBACK",
        }
        if existing:
            state = "RECHECK_MAPPED_FORK"
        elif row["license_review"]:
            state = "HOLD_LICENSE_REVIEW"
        elif (row["next_step"] in EXTRA_HOLDS
              or row["latest_stage"] in {"CLOSED_NO_CHANGE", "BLOCKED_EVIDENCE"}):
            state = "HOLD_HISTORICAL_OR_NEGATIVE_CASE"
        else:
            state = "PROPOSE_CREATE_REQUIRES_LIVE_PREFLIGHT"
        item = {
            "source": source,
            "priority_group": row["priority_group"],
            "next_step": row["next_step"],
            "candidate_fork": destination,
            "candidate_name": name,
            "collision_name_proposal": renamed,
            "state": state,
            "current_fork_mapping": row.get("fork"),
            "requires_fresh_source_license_policy_and_destination_checks": True,
        }
        sources.append(item)
        if state == "PROPOSE_CREATE_REQUIRES_LIVE_PREFLIGHT":
            candidates.append(item)

    batches = []
    for offset in range(0, len(candidates), BATCH_SIZE):
        group = candidates[offset:offset + BATCH_SIZE]
        selected = [{"source": item["source"],
                     "candidate_fork": item["candidate_fork"]}
                    for item in group]
        envelope = {"stage": "create_public_fork", "destination_org": DESTINATION,
                    "selection": selected, "registry_sha256":
                        hashlib.sha256(raw_registry.encode("utf-8")).hexdigest()}
        batches.append({
            "id": f"bootstrap-{len(batches) + 1:03d}",
            "state": "UNAPPROVED_REQUIRES_TRUSTED_PREFLIGHT",
            "selection_sha256": digest(envelope),
            "source_count": len(group),
            "has_collision_name_proposals": any(item["collision_name_proposal"]
                                                for item in group),
            "selection": selected,
        })
    counts = dict(sorted(Counter(row["state"] for row in sources).items()))
    workspaces.require(len(sources) == inventory["counts"]["unique_sources"]
                       and sum(counts.values()) == len(sources),
                       "Lost source identities in bootstrap proposal")
    return {
        "schema_version": 1,
        "state": "READ_ONLY_PROPOSAL_NOT_APPROVED",
        "destination_org": DESTINATION,
        "source_registry": workspaces.REGISTRY.as_posix(),
        "source_registry_sha256": hashlib.sha256(
            raw_registry.encode("utf-8")).hexdigest(),
        "priority_snapshot": workspaces.POOL.as_posix(),
        "batch_size_max": BATCH_SIZE,
        "counts": {"sources": len(sources), "priority_sources": 100,
                   "additive_extras": len(sources) - 100,
                   "collision_name_proposals": sum(x["collision_name_proposal"]
                                                   for x in sources),
                   "creation_batches": len(batches),
                   "by_state": counts},
        "authority": {
            "bootstrap_stage": "create_public_fork_only",
            "proposal_digest_is_an_approval": False,
            "authenticated_actor_and_org_rights": "REVERIFY_IN_TRUSTED_HOST",
            "one_use_revocable_batch_grant": "NOT_ISSUED",
            "source_license_and_fork_policy": "REVERIFY_BEFORE_EACH_WRITE",
            "destination_absence_or_correct_parent": "REVERIFY_BEFORE_EACH_WRITE",
            "failure": "STOP_AND_RECORD_NO_BLIND_RETRY",
            "working_branch_write_stage": "SEPARATE_PREPARE_CONTRIBUTION_GRANT",
            "external_pr": "HUMAN_APPROVAL_PER_EXACT_PR",
            "auto_external_pr": False,
        },
        "batches": batches,
        "sources": sources,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("status", "sync", "check"))
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        report = build(args.root)
        target = args.root / OUTPUT
        expected = workspaces.encoded(report)
        if args.command == "sync":
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(expected, encoding="utf-8")
        elif args.command == "check":
            workspaces.require(target.is_file()
                               and target.read_text(encoding="utf-8") == expected,
                               f"Stale {OUTPUT}; run scripts/fork_bootstrap_manifest.py sync")
        else:
            print(json.dumps({"state": report["state"],
                              "counts": report["counts"],
                              "batch_ids": [b["id"] for b in report["batches"]]},
                             indent=2))
    except (OSError, TypeError, KeyError, ValueError) as exc:
        parser.exit(2, f"FORK_BOOTSTRAP_INVALID: {exc}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
