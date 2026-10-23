#!/usr/bin/env python3
"""Read-only finite owner-mandated Corrective PR publication queue."""

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data/corrective-publication/2026-10-23-01.json"
SOURCE_BATCHES = (
    *[f"data/assessment-candidate-batches/2026-10-22-{n:02d}.json" for n in range(1, 8)],
    *[f"data/assessment-candidate-batches/2026-10-23-{n:02d}.json" for n in range(8, 11)],
)
# Pinned blob objects from `git ls-tree -r 3dde0736...` on the owning main.
# The checkout may be shallow on CI; comparing the checked-out bytes to these
# exact frozen Git blob IDs validates the same manifest content offline.
FROZEN_SNAPSHOT_SHA = "3dde07363359607476af7b8d6a55026b6b4d6e11"
SOURCE_BLOBS = (
    "25ddad96a7c887ac0de970885f50c7bfdab51fe0",
    "53133d3f9d0bdb48d6375170ae940c9671fd65a0",
    "d24981b64defbae9c85c7918d99082134b842ed7",
    "59ad9ddc636bf465658a36740c44b0e4b81d1a70",
    "a5956e7e6e35e050418ac80a331cd7e9ebfd9c1b",
    "5000422c8bd75c1de546c0884b9ef5003248976c",
    "1df1c4e57da327d920a9deb20713e8be7428c65c",
    "03d22f101e5702f4a1528fd2626f2d09bb816e2b",
    "698deaf8b27338824525ae7df2f8d2ad39b873ca",
    "450da815c13dd225ae7038d9ab24c28677f1f2fd",
)
TERMINAL = {"SUBMITTED", "BLOCKED", "CLOSED_NO_CHANGE", "CLOSED_UPSTREAM", "MERGED"}
STATES = TERMINAL | {"QUEUED"}
HEX40 = re.compile(r"[0-9a-f]{40}\Z")


class QueueError(ValueError):
    pass


def _git_show(commit, path):
    if commit != FROZEN_SNAPSHOT_SHA or path not in SOURCE_BATCHES:
        raise QueueError("Source identity outside frozen 34-case snapshot")
    try:
        data = (ROOT / path).read_bytes()
    except OSError as exc:
        raise QueueError(f"Frozen source manifest missing: {path}") from exc
    actual_blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    expected_blob = SOURCE_BLOBS[SOURCE_BATCHES.index(path)]
    if actual_blob != expected_blob:
        raise QueueError(f"Frozen source manifest changed: {path}")
    try:
        return json.loads(data)
    except ValueError as exc:
        raise QueueError(f"Invalid pinned JSON: {path}") from exc


def validate(ledger):
    if not isinstance(ledger, dict) or ledger.get("schema_version") != 1:
        raise QueueError("Unsupported publication ledger")
    if ledger.get("mandate_id") != "CORRECTIVE-PUBLISH-2026-10-23-01":
        raise QueueError("Unknown bounded mandate")
    if ledger.get("owner_issue") != "https://github.com/opensiro/upstream/issues/56":
        raise QueueError("Wrong publication owner")
    snapshot = ledger.get("candidate_snapshot_sha", "")
    if snapshot != FROZEN_SNAPSHOT_SHA:
        raise QueueError("Exact frozen source snapshot required")
    allowed = []
    for path in SOURCE_BATCHES:
        source = _git_show(snapshot, path)
        for row in source["candidates"]:
            if row["stage"] == "AWAITING_EXTERNAL":
                if (row.get("origin") != "ASSESSMENT_INFORMED"
                    or set(row.get("fit", {}).values()) != {"PASS"}
                    or row.get("external_action") != "NOT_EXECUTED"
                    or not row.get("handoff_url", "").startswith("https://")):
                    raise QueueError(f"Unqualified source row: {row.get('id')}")
                allowed.append(row)
    cases = ledger.get("cases")
    if not isinstance(cases, list) or len(cases) != ledger.get("authorized_count") or len(allowed) != 34:
        raise QueueError("Finite 34-case scope mismatch")
    if [x.get("id") for x in cases] != [x["id"] for x in allowed]:
        raise QueueError("Publication queue changed the pinned candidate order or allowed scope")
    for case, source in zip(cases, allowed):
        status = case.get("publication")
        if status not in STATES:
            raise QueueError(f"Invalid publication state: {case['id']}")
        if status == "QUEUED":
            if case.get("pr_url"):
                raise QueueError(f"Queued case cannot claim a PR: {case['id']}")
        if status in {"BLOCKED", "CLOSED_NO_CHANGE", "CLOSED_UPSTREAM"}:
            if not isinstance(case.get("reason"), str) or len(case["reason"]) < 15:
                raise QueueError(f"Missing closure/blocker evidence: {case['id']}")
        if status in {"SUBMITTED", "MERGED"}:
            url = f"https://github.com/{source['source']}/pull/"
            if not isinstance(case.get("pr_url"), str) or not case["pr_url"].casefold().startswith(url.casefold()):
                raise QueueError(f"Missing exact target upstream PR: {case['id']}")
            if not isinstance(case.get("actor"), str) or not case["actor"]:
                raise QueueError(f"Missing authenticated actor: {case['id']}")
            for key in ("base_sha", "head_sha"):
                value = case.get(key)
                if not isinstance(value, str) or not HEX40.fullmatch(value):
                    raise QueueError(f"Missing observed {key}: {case['id']}")
            if not case.get("native_test_receipt"):
                raise QueueError(f"Missing first-party test receipt: {case['id']}")
            if status == "MERGED" and not HEX40.fullmatch(str(case.get("merge_sha", ""))):
                raise QueueError(f"Unverified upstream merge: {case['id']}")
    return ledger


def report(ledger):
    validate(ledger)
    counts = Counter(x["publication"] for x in ledger["cases"])
    item = next((x["id"] for x in ledger["cases"] if x["publication"] == "QUEUED"), None)
    return {
        "mandate_id": ledger["mandate_id"],
        "authorized_count": len(ledger["cases"]),
        "counts": dict(sorted(counts.items())),
        "next_candidate": item,
        "no_external_writes_performed_by_this_command": True,
        "test_mode": "NATIVE_SCRIPT_ONLY_NO_LLM_AGENTS",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "status", "next"))
    parser.add_argument("--ledger", type=Path, default=LEDGER)
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.ledger.read_text(encoding="utf-8"))
        result = report(data)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, f"PUBLICATION_QUEUE_INVALID: {exc}\n")
    if args.command == "validate":
        result = {"valid": True, "mandate_id": result["mandate_id"]}
    elif args.command == "next":
        result = {"next_candidate": result["next_candidate"], "mandate_id": result["mandate_id"]}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
