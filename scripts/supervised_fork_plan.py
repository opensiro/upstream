#!/usr/bin/env python3
"""Show exact owner-supervised GitHub fork commands; never execute them.

This is a human-readable invocation plan for the existing dev-alpha-2 → SSH
host → GitHub CLI route. It is not a grant, executor, or source of live checks.
"""

import argparse
import json
from pathlib import Path
import shlex
import sys

import contribution_workspaces as workspaces
import fork_bootstrap_manifest as bootstrap


ROOT = Path(__file__).resolve().parents[1]


def current_proposal(root):
    expected = workspaces.encoded(bootstrap.build(root))
    path = root / bootstrap.OUTPUT
    workspaces.require(path.is_file() and path.read_text(encoding="utf-8") == expected,
                       "Stale bootstrap proposal; run fork_bootstrap_manifest.py sync")
    return json.loads(expected)


def plan(root, batch_id):
    report = current_proposal(Path(root))
    matches = [x for x in report["batches"] if x["id"] == batch_id]
    workspaces.require(len(matches) == 1, f"Unknown bootstrap batch {batch_id}")
    batch = matches[0]
    workspaces.require(batch["state"] == "UNAPPROVED_REQUIRES_TRUSTED_PREFLIGHT"
                       and report["state"] == "READ_ONLY_PROPOSAL_NOT_APPROVED",
                       "Unexpected executable bootstrap proposal")
    rows = []
    for item in batch["selection"]:
        source = item["source"]
        fork = item["candidate_fork"]
        workspaces.require(workspaces.SOURCE.fullmatch(source)
                           and fork.startswith("opensiro-contributions/")
                           and workspaces.SOURCE.fullmatch(fork),
                           "Invalid exact fork selection")
        name = fork.split("/", 1)[1]
        # All required source branches should be retained unless the exact
        # reviewed candidate specifies a different branch-aware strategy.
        argv = ("gh", "repo", "fork", source, "--org", "opensiro-contributions",
                "--fork-name", name, "--clone=false")
        rows.append({"source": source, "destination": fork,
                     "command_after_approval": shlex.join(argv)})
    workspaces.require(len(rows) == batch["source_count"]
                       and len(rows) <= report["batch_size_max"],
                       "Batch scope or size changed")
    return {"state": "DISPLAY_ONLY_NO_WRITE_AUTHORITY",
            "batch_id": batch_id,
            "selection_sha256": batch["selection_sha256"],
            "source_registry_sha256": report["source_registry_sha256"],
            "requires": [
                "Exact human owner selection/permission for this one-off batch",
                "Authenticated gh actor and destination-organization rights",
                "Fresh public source, license and fork-policy checks",
                "Absence or independently verified matching parent at destination",
                "Required branch/ref and collision-name checks",
                "One operation then independent provider readback; stop on uncertainty",
            ],
            "items": rows,
            "external_pr": "HUMAN_APPROVAL_PER_EXACT_PR"}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("status", "show"))
    p.add_argument("--batch", help="Exact bootstrap-NNN identifier for show")
    p.add_argument("--root", type=Path, default=ROOT)
    a = p.parse_args(argv)
    try:
        if a.command == "show":
            workspaces.require(bool(a.batch), "show requires --batch")
            result = plan(a.root, a.batch)
        else:
            workspaces.require(not a.batch, "status does not accept --batch")
            report = current_proposal(a.root)
            result = {"state": "DISPLAY_ONLY_NO_WRITE_AUTHORITY",
                      "counts": report["counts"],
                      "batches": [x["id"] for x in report["batches"]]}
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        p.exit(2, f"SUPERVISED_FORK_PLAN_INVALID: {exc}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
