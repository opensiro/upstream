#!/usr/bin/env python3
"""Bounded Upstream task arbitration and opt-in Git CAS reservations.

The input is an agent-assembled, source-pinned *proposal* from existing Upstream
owner lanes, not authority to execute a task. A live first-party preflight is
required before writing a claim. The actual work stays with its owning lane.
No external repository mutation, background daemon, or VSM grade is implied.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

from assessment_batch_conflict_preflight import GithubReader
from assessment_candidate_batches import BatchError
from assessment_source_reservations import fetch_ledger as fetch_batch_ledger, replay as replay_batch


class AutoError(ValueError):
    """Fail-closed, operator-readable auto coordination error."""


LEDGER_REF = "refs/heads/upstream-auto-task-reservations"
LANE_OWNER = {"maintenance": 125, "outcomes": 159, "portfolio": 150,
              "batch": 56}
LANE_WIP_CAP = {"maintenance": 2, "outcomes": 2, "portfolio": 1,
                "batch": 1}
LANE_BONUS = {"maintenance": 8, "outcomes": 7, "batch": 5,
              "portfolio": 4}
PRIORITY_BASE = {"P0": 100, "P1": 70, "P2": 40, "P3": 10}
TASK_KEY = re.compile(r"[a-z0-9][a-z0-9._:#/-]{2,159}\Z")
RESOURCE_KEY = re.compile(
    r"(?:source:[a-z0-9_.-]+/[a-z0-9_.-]+|"
    r"pr:[a-z0-9_.-]+/[a-z0-9_.-]+#[1-9][0-9]*|"
    r"intervention:[a-z0-9][a-z0-9._-]{1,79}|"
    r"batch:assessment-upstream-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2})\Z")
SHA = re.compile(r"[0-9a-f]{40}\Z")
ACTOR = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{1,79}\Z")
TASK_FIELDS = {"task_id", "lane", "owner_issue", "resources",
               "evidence_url", "queued_at", "observed_at", "status",
               "priority", "operation", "head_sha"}
EVENT_FIELDS = {"action", "claim_id", "task_id", "actor", "resources",
                "owner_issue", "evidence_url", "timestamp"}


def _timestamp(value):
    if not isinstance(value, str) or not re.fullmatch(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value):
        raise AutoError("Invalid UTC timestamp; use YYYY-MM-DDTHH:MM:SSZ")
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise AutoError("Invalid UTC date") from exc


def _issue_url(value):
    if not isinstance(value, str):
        raise AutoError("Missing first-party evidence URL")
    parsed = urlparse(value)
    if (parsed.scheme != "https" or parsed.netloc != "github.com"
            or parsed.username or parsed.password or parsed.query
            or not re.fullmatch(r"/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/(?:issues|pull)/[1-9][0-9]*", parsed.path)):
        raise AutoError("Evidence must be an exact public GitHub issue/PR URL")
    return value


def _resources(values):
    if not isinstance(values, list) or not 1 <= len(values) <= 10:
        raise AutoError("Resource list must contain 1–10 exact keys")
    normalized = [v.casefold() if isinstance(v, str) else "" for v in values]
    if any(not RESOURCE_KEY.fullmatch(v) for v in normalized) or len(normalized) != len(set(normalized)):
        raise AutoError("Malformed or duplicate resource key")
    return sorted(normalized)


def validate_manifest(data, *, now=None):
    """Validate untrusted task proposals, preserving their non-authoritative status."""
    now = now or datetime.now(timezone.utc)
    if not isinstance(data, dict) or set(data) != {"schema_version", "upstream_main_sha", "observed_at", "tasks"}:
        raise AutoError("Invalid worklist schema")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise AutoError("Unsupported worklist version")
    if not isinstance(data["upstream_main_sha"], str) or not SHA.fullmatch(data["upstream_main_sha"]):
        raise AutoError("Missing exact Upstream main source cut")
    snapshot = _timestamp(data["observed_at"])
    if snapshot > now + timedelta(minutes=1) or now - snapshot > timedelta(minutes=60):
        raise AutoError("BLOCKED_STALE_EVIDENCE: refresh Upstream source cut")
    if not isinstance(data["tasks"], list) or len(data["tasks"]) > 100:
        raise AutoError("Invalid bounded task list")
    seen = set()
    tasks = []
    for raw in data["tasks"]:
        if not isinstance(raw, dict) or set(raw) != TASK_FIELDS:
            raise AutoError("Invalid task fields")
        task_id = raw["task_id"]
        if (not isinstance(task_id, str) or not TASK_KEY.fullmatch(task_id)
                or task_id in seen):
            raise AutoError("Duplicate or malformed task ID")
        seen.add(task_id)
        lane = raw["lane"]
        if lane not in LANE_OWNER or type(raw["owner_issue"]) is not int or raw["owner_issue"] != LANE_OWNER[lane]:
            raise AutoError("Task lane must point to its admitted Upstream owner issue")
        if raw["status"] not in {"ACTIONABLE", "BLOCKED_EVIDENCE", "AWAITING_EXTERNAL", "NON_ADMITTED"}:
            raise AutoError("Unknown task admission status")
        if raw["priority"] not in PRIORITY_BASE:
            raise AutoError("Unknown task priority")
        if raw["operation"] not in {"READ_ONLY_REVIEW", "INTERNAL_PREPARE"}:
            raise AutoError("External writes are not an Upstream Auto task operation")
        queue_time, observed = _timestamp(raw["queued_at"]), _timestamp(raw["observed_at"])
        if queue_time > observed or observed > snapshot or now - observed > timedelta(minutes=60):
            raise AutoError("BLOCKED_STALE_EVIDENCE: task readback is missing or stale")
        keys = _resources(raw["resources"])
        head_sha = raw["head_sha"]
        if head_sha is not None and (not isinstance(head_sha, str) or not SHA.fullmatch(head_sha)):
            raise AutoError("Invalid PR head SHA")
        if any(k.startswith("pr:") for k in keys) and head_sha is None:
            raise AutoError("A PR work item needs its exact reviewed head SHA")
        if not any(k.startswith("pr:") for k in keys) and head_sha is not None:
            raise AutoError("PR head SHA without a matching PR resource")
        if lane == "batch":
            if (len([k for k in keys if k.startswith("batch:")]) != 1
                    or len([k for k in keys if k.startswith("source:")]) != 5):
                raise AutoError("Batch task must name one frozen batch identity and five sources")
        evidence_url = _issue_url(raw["evidence_url"])
        pr_refs = [k[3:] for k in keys if k.startswith("pr:")]
        evidence = urlparse(evidence_url).path.casefold()
        if any("source:" + name.split("#", 1)[0] not in keys for name in pr_refs):
            raise AutoError("PR task needs its normalized source resource lock")
        if pr_refs and not any(evidence == "/" + name.replace("#", "/pull/") for name in pr_refs):
            raise AutoError("PR work evidence must link to its exact target PR")
        task = dict(raw, resources=keys)
        tasks.append(task)
    return tasks


def replay(ledger):
    """Validate append-only claim/release semantics and active resource exclusivity."""
    if (not isinstance(ledger, dict) or set(ledger) != {"schema_version", "events"}
            or type(ledger["schema_version"]) is not int or ledger["schema_version"] != 1):
        raise AutoError("Invalid task reservation ledger")
    if not isinstance(ledger["events"], list):
        raise AutoError("Invalid reservation event list")
    active, resources, seen = {}, {}, set()
    for event in ledger["events"]:
        if not isinstance(event, dict) or not EVENT_FIELDS <= set(event):
            raise AutoError("Invalid task reservation event")
        action, claim_id = event["action"], event["claim_id"]
        if (action not in {"CLAIM", "RELEASE"}
                or not isinstance(claim_id, str) or not re.fullmatch(r"[0-9a-f]{32}", claim_id)
                or not isinstance(event["task_id"], str) or not TASK_KEY.fullmatch(event["task_id"])
                or not isinstance(event["actor"], str) or not ACTOR.fullmatch(event["actor"])
                or type(event["owner_issue"]) is not int or event["owner_issue"] not in LANE_OWNER.values()):
            raise AutoError("Malformed claim identity")
        _issue_url(event["evidence_url"])
        _timestamp(event["timestamp"])
        keys = _resources(event["resources"])
        if action == "CLAIM":
            if set(event) != EVENT_FIELDS or claim_id in seen or event["task_id"] in {x["task_id"] for x in active.values()}:
                raise AutoError("Duplicate task claim")
            collision = [k for k in keys if k in resources]
            if collision:
                raise AutoError("BLOCKED_CONCURRENT_RESERVATION: " + ", ".join(collision))
            active[claim_id] = event
            resources.update({k: claim_id for k in keys})
            seen.add(claim_id)
        else:
            prior = active.get(claim_id)
            if (set(event) != EVENT_FIELDS | {"reason"}
                    or prior is None or not isinstance(event["reason"], str)
                    or len(event["reason"].strip()) < 15
                    or _timestamp(event["timestamp"]) < _timestamp(prior["timestamp"])
                    or any(event[k] != prior[k] for k in ("task_id", "actor", "resources", "owner_issue"))):
                raise AutoError("Release requires active original claim, actor and auditable reason")
            for key in keys:
                del resources[key]
            del active[claim_id]
    return active


def plan(manifest, ledger, *, now=None):
    """Deterministic provisional priority; no claim, mandate or final S1 verdict."""
    now = now or datetime.now(timezone.utc)
    tasks = validate_manifest(manifest, now=now)
    active = replay(ledger)
    busy = {key for event in active.values() for key in event["resources"]}
    lane_active = {lane: 0 for lane in LANE_OWNER}
    for event in active.values():
        lane = next((t["lane"] for t in tasks if t["task_id"] == event["task_id"]), None)
        if lane is not None:
            lane_active[lane] += 1
    # Existing claims not present in the input must still count against WIP.
    # Their lane is derivable from stable owner issue, not current manifest.
    for event in active.values():
        if not any(t["task_id"] == event["task_id"] for t in tasks):
            lane = next((k for k, v in LANE_OWNER.items() if v == event["owner_issue"]), None)
            if lane is not None:
                lane_active[lane] += 1
    eligible, blocked = [], []
    for task in tasks:
        if task["status"] != "ACTIONABLE":
            blocked.append({"task_id": task["task_id"], "reason": task["status"]})
            continue
        if set(task["resources"]) & busy:
            blocked.append({"task_id": task["task_id"], "reason": "CLAIMED_RESOURCE"})
            continue
        if lane_active[task["lane"]] >= LANE_WIP_CAP[task["lane"]]:
            blocked.append({"task_id": task["task_id"], "reason": "LANE_WIP_CAP"})
            continue
        age_hours = max(0, (now - _timestamp(task["queued_at"])).total_seconds() // 3600)
        score = PRIORITY_BASE[task["priority"]] + min(60, age_hours * 2) + LANE_BONUS[task["lane"]]
        eligible.append({"task_id": task["task_id"], "lane": task["lane"],
                         "owner_issue": task["owner_issue"], "score": int(score),
                         "resources": task["resources"], "evidence_url": task["evidence_url"]})
    eligible.sort(key=lambda x: (-x["score"], x["task_id"]))
    return {"status": "PREVIEW_ONLY" if eligible else "NO_VERIFIED_ELIGIBLE_WORK",
            "selected": eligible[0] if eligible else None,
            "eligible": eligible, "blocked": blocked, "active_claims": len(active),
            "upstream_main_sha": manifest["upstream_main_sha"],
            "warning": "Manifest actionability is an agent proposal, not live attestation or permission to execute"}


def _git(root, *args, input_text=None, allow_failure=False):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    result = subprocess.run(["git", "-C", str(root), *args], input=input_text,
                            text=True, capture_output=True, check=False, env=env)
    if result.returncode and not allow_failure:
        raise AutoError("Git task reservation operation failed; inspect local Git credentials/configuration")
    return result


def fetch_ledger(root, remote):
    fetched = _git(root, "fetch", "--no-tags", remote, LEDGER_REF, allow_failure=True)
    if fetched.returncode:
        raise AutoError("BLOCKED_RESERVATION_VISIBILITY: task ledger ref unavailable")
    parent = _git(root, "rev-parse", "FETCH_HEAD").stdout.strip()
    paths = _git(root, "ls-tree", "-r", "--name-only", parent).stdout.splitlines()
    if paths != ["reservations.json"]:
        raise AutoError("BLOCKED_RESERVATION_VISIBILITY: unexpected ledger branch tree")
    raw = _git(root, "show", f"{parent}:reservations.json", allow_failure=True)
    if raw.returncode:
        raise AutoError("BLOCKED_RESERVATION_VISIBILITY: missing ledger blob")
    try:
        ledger = json.loads(raw.stdout)
    except ValueError as exc:
        raise AutoError("BLOCKED_RESERVATION_VISIBILITY: malformed ledger JSON") from exc
    replay(ledger)
    return parent, ledger


def live_preflight(manifest, task, reader):
    """Live source identity/PR state gate; semantic actionability remains agent-owned."""
    if reader is None:
        raise AutoError("BLOCKED_GITHUB_VISIBILITY: live reader required before claim")
    try:
        branch = reader.get("/repos/opensiro/upstream/branches/main")
        if branch.get("commit", {}).get("sha") != manifest["upstream_main_sha"]:
            raise AutoError("BLOCKED_STALE_SOURCE_CUT: Upstream main moved")
        issue = reader.get(f"/repos/opensiro/upstream/issues/{task['owner_issue']}")
        if issue.get("state") != "open":
            raise AutoError("BLOCKED_OWNER_ISSUE: owning task issue not open")
        for key in task["resources"]:
            if not key.startswith("pr:"):
                continue
            identifier = key[3:]
            repo, number = identifier.rsplit("#", 1)
            pr = reader.get(f"/repos/{repo}/pulls/{number}")
            if pr.get("head", {}).get("sha") != task["head_sha"]:
                raise AutoError("BLOCKED_PR_HEAD_CHANGED: re-read before dispatch")
            if task["lane"] in {"maintenance", "portfolio"} and pr.get("state") != "open":
                raise AutoError("BLOCKED_PR_LIFECYCLE: review target no longer open")
    except AutoError:
        raise
    except (BatchError, KeyError, TypeError, ValueError, OSError) as exc:
        raise AutoError("BLOCKED_GITHUB_VISIBILITY: incomplete first-party readback") from exc
    return {"owner_issue": task["owner_issue"], "main_sha": manifest["upstream_main_sha"],
            "head_sha": task["head_sha"], "status": "LIVE_PREFLIGHT_PASS"}


def _append(root, remote, parent, ledger, event, *, write):
    updated = {"schema_version": 1, "events": ledger["events"] + [event]}
    replay(updated)
    if not write:
        return {"status": "PREVIEW_ONLY", "parent_sha": parent}
    payload = json.dumps(updated, indent=2, sort_keys=True) + "\n"
    blob = _git(root, "hash-object", "-w", "--stdin", input_text=payload).stdout.strip()
    tree = _git(root, "mktree", input_text=f"100644 blob {blob}\treservations.json\n").stdout.strip()
    commit = _git(root, "commit-tree", tree, "-p", parent,
                  input_text=f"Upstream Auto {event['action'].lower()} {event['task_id']}\n").stdout.strip()
    pushed = _git(root, "push", remote, f"{commit}:{LEDGER_REF}", allow_failure=True)
    if pushed.returncode:
        error = pushed.stderr.casefold()
        if any(label in error for label in ("non-fast-forward", "fetch first", "stale info")):
            raise AutoError("BLOCKED_CONCURRENT_RESERVATION: Git CAS lost; re-fetch and re-plan")
        raise AutoError("RESERVATION_PUSH_BLOCKED: Git remote rejected the task reservation write")
    return {"status": "WRITTEN_CAS", "claim_commit": commit, "parent_sha": parent}


def claim(root, remote, manifest, actor, *, task_id=None, write=False, reader=None, now=None):
    now = now or datetime.now(timezone.utc)
    if not isinstance(actor, str) or not ACTOR.fullmatch(actor):
        raise AutoError("Invalid attributable actor")
    parent, ledger = fetch_ledger(root, remote)
    selection = plan(manifest, ledger, now=now)
    task_ref = task_id or (selection["selected"] or {}).get("task_id")
    if not task_ref:
        raise AutoError("NO_VERIFIED_ELIGIBLE_WORK: nothing admitted for selection")
    selected = next((t for t in selection["eligible"] if t["task_id"] == task_ref), None)
    if selected is None:
        raise AutoError("BLOCKED_TASK_NOT_AVAILABLE: occupied, unadmitted or WIP cap")
    task = next(t for t in manifest["tasks"] if t["task_id"] == task_ref)
    if write and task["lane"] == "batch":
        # This separate source-CAS is mandatory; the task lease cannot replace it.
        try:
            _, source_ledger = fetch_batch_ledger(root, remote)
            source_owners = replay_batch(source_ledger)
        except BatchError as exc:
            raise AutoError("BLOCKED_BATCH_SOURCE_CAS: source reservation unavailable") from exc
        batch = next(k[len("batch:"):] for k in selected["resources"] if k.startswith("batch:"))
        sources = [k[len("source:"):] for k in selected["resources"] if k.startswith("source:")]
        if any(source_owners.get(source) != batch for source in sources):
            raise AutoError("BLOCKED_BATCH_SOURCE_CAS: five sources not reserved to frozen batch")
    # Validate even when planning only, but never imply unverified external authority.
    preflight = live_preflight(manifest, task, reader) if write else None
    event = {"action": "CLAIM", "claim_id": uuid.uuid4().hex,
             "task_id": task_ref, "actor": actor, "resources": selected["resources"],
             "owner_issue": selected["owner_issue"],
             "evidence_url": selected["evidence_url"],
             "timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ")}
    receipt = _append(root, remote, parent, ledger, event, write=write)
    receipt.update({"claim_id": event["claim_id"], "task_id": task_ref,
                    "actor": actor, "owner_issue": selected["owner_issue"],
                    "resources": selected["resources"], "live_preflight": preflight,
                    "external_writes_authorized": False,
                    "work_executed": False,
                    "next": "Re-read selected owner lane, stage grants and current source before one bounded agent action"})
    if not write:
        receipt["provisional_claim_id"] = receipt.pop("claim_id")
    return receipt


def resume(root, remote, actor, *, now=None):
    now = now or datetime.now(timezone.utc)
    _, ledger = fetch_ledger(root, remote)
    records = [event for event in replay(ledger).values() if event["actor"] == actor]
    result = []
    for event in records:
        age = now - _timestamp(event["timestamp"])
        result.append({"claim_id": event["claim_id"], "task_id": event["task_id"],
                       "owner_issue": event["owner_issue"], "resources": event["resources"],
                       "status": "STALE_CLAIM_UNRESOLVED" if age > timedelta(hours=24) else "CLAIMED_NEEDS_REVALIDATION"})
    return {"status": "RESUME_INSPECTION_ONLY", "claims": result}


def release(root, remote, claim_id, actor, reason, evidence_url, *, write=False, now=None):
    now = now or datetime.now(timezone.utc)
    if not isinstance(actor, str) or not ACTOR.fullmatch(actor):
        raise AutoError("Invalid attributable actor")
    if not isinstance(reason, str) or len(reason.strip()) < 15:
        raise AutoError("Auditable release reason is required")
    _issue_url(evidence_url)
    parent, ledger = fetch_ledger(root, remote)
    event = replay(ledger).get(claim_id)
    if event is None or event["actor"] != actor:
        raise AutoError("BLOCKED_CLAIM_OWNER: only original actor can release")
    released = {**event, "action": "RELEASE", "timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "evidence_url": evidence_url, "reason": reason}
    result = _append(root, remote, parent, ledger, released, write=write)
    result.update({"claim_id": claim_id, "task_id": event["task_id"],
                   "actor": actor, "work_executed": False,
                   "warning": "Release changes reservation only; owner evidence must separately prove task outcome"})
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("status", "claim", "resume", "release"))
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--git-root", type=Path, default=Path.cwd())
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--actor")
    parser.add_argument("--task-id")
    parser.add_argument("--claim-id")
    parser.add_argument("--reason")
    parser.add_argument("--evidence-url")
    parser.add_argument("--write-claim", action="store_true")
    parser.add_argument("--write-release", action="store_true")
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8")) if args.manifest else None
        if args.command in {"status", "claim"} and manifest is None:
            raise AutoError("A fresh agent-reviewed --manifest is required")
        if args.command in {"claim", "resume", "release"} and not args.actor:
            raise AutoError("An attributable --actor is required")
        if args.command == "status":
            _, ledger = fetch_ledger(args.git_root, args.remote)
            result = plan(manifest, ledger)
        elif args.command == "claim":
            result = claim(args.git_root, args.remote, manifest, args.actor,
                           task_id=args.task_id, write=args.write_claim,
                           reader=GithubReader(os.environ.get("GITHUB_TOKEN")) if args.write_claim else None)
        elif args.command == "resume":
            result = resume(args.git_root, args.remote, args.actor)
        else:
            if not args.claim_id or not args.reason or not args.evidence_url:
                raise AutoError("Release needs --claim-id, --reason and --evidence-url")
            result = release(args.git_root, args.remote, args.claim_id, args.actor,
                             args.reason, args.evidence_url, write=args.write_release)
    except (AutoError, OSError, json.JSONDecodeError) as exc:
        parser.exit(2, f"UPSTREAM_AUTO_BLOCKED: {exc}\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
