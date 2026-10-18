#!/usr/bin/env python3
"""Read-only validator for proposed conversation-approved batches.

No execution authority or independently authenticated operator identity is established here.
"""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit
import create_fork

BATCH_ID = re.compile(r"^upstream-[0-9]{8}-[a-z0-9][a-z0-9-]{0,39}$")
ITEM_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")
LICENSE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.+-]{0,49}$")
APPROVAL_URL = re.compile(r"^https://github[.]com/opensiro/upstream/(issues|pull)/[0-9]+$")
BATCH_FIELDS = {"schema_version", "batch_id", "approved_by", "approval_medium",
                "approval_ref", "approved_at", "expires_at", "items"}
ITEM_FIELDS = {"id", "action", "source", "fork_name", "expected_license", "proposal"}
PROPOSAL_FIELDS = {"system_component", "problem", "planned_change",
                   "expected_improvement", "validation", "evidence_url"}

class BatchError(Exception):
    pass

def canonical_digest(value):
    """SHA-256 of stable JSON, so formatting changes do not alter a proposal."""
    canonical = json.dumps(value, sort_keys=True, ensure_ascii=False,
                           separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise BatchError("Duplicate JSON field")
        result[key] = value
    return result

def parse_time(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise BatchError("Expected UTC timestamp ending in Z")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise BatchError("Invalid timestamp") from None

def validate_proposal(proposal, *, allow_missing_evidence=False):
    """Validate the frozen descriptive intent; never treat it as an execution command."""
    if not isinstance(proposal, dict) or set(proposal) != PROPOSAL_FIELDS:
        raise BatchError("Contribution proposal must contain every required field")
    for field in PROPOSAL_FIELDS - {"evidence_url"}:
        value = proposal[field]
        if not isinstance(value, str) or not (12 <= len(value.strip()) <= 1000):
            raise BatchError("Contribution proposal field missing or too long: " + field)
        if any(ord(char) < 32 for char in value):
            raise BatchError("Invalid control character in proposal")
        if value.strip().casefold() in {"tbd", "todo", "n/a", "unknown"}:
            raise BatchError("Placeholder is not a contribution proposal")
    evidence = proposal["evidence_url"]
    if evidence is None and allow_missing_evidence:
        return
    if (not isinstance(evidence, str) or len(evidence) > 2048
            or any(ord(char) <= 32 for char in evidence)):
        raise BatchError("Missing or invalid proposal evidence URL")
    try:
        url = urlsplit(evidence)
        if (url.scheme != "https" or not url.hostname or url.username or url.password
                or url.path in ("", "/")):
            raise BatchError("Proposal evidence requires a specific HTTPS source URL")
    except ValueError:
        raise BatchError("Malformed proposal evidence URL") from None


DRAFT_FIELDS = {"schema_version", "batch_id", "revision", "status", "candidates"}
DRAFT_ITEM_FIELDS = {"id", "source", "fork_name", "stages",
                     "expected_license", "proposal", "blockers"}
DRAFT_STAGES = ("create_public_fork", "prepare_contribution", "submit_external_pr")


def load_draft(path):
    """Read a proposed batch with no approval assertions and no GitHub API calls."""
    path = Path(path)
    if not BATCH_ID.fullmatch(path.stem) or path.suffix != ".json":
        raise BatchError("Invalid draft batch filename")
    try:
        raw = path.read_bytes()
        if len(raw) > 16384:
            raise BatchError("Draft batch too large")
        data = json.loads(raw, object_pairs_hook=no_duplicate_keys)
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        raise BatchError("Cannot read proposed batch: " + type(exc).__name__) from None
    if not isinstance(data, dict) or set(data) != DRAFT_FIELDS:
        raise BatchError("Draft schema does not accept approval fields")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise BatchError("Unsupported draft schema version")
    if data["batch_id"] != path.stem or data["status"] != "proposal_only":
        raise BatchError("Draft ID or status mismatch")
    if type(data["revision"]) is not int or not (1 <= data["revision"] <= 1000):
        raise BatchError("Invalid draft revision")
    candidates = data["candidates"]
    if not isinstance(candidates, list) or not (1 <= len(candidates) <= 10):
        raise BatchError("Draft requires 1 to 10 candidate entries")
    seen_ids, seen_sources, seen_targets = set(), set(), set()
    for item in candidates:
        if not isinstance(item, dict) or set(item) != DRAFT_ITEM_FIELDS:
            raise BatchError("Unexpected draft candidate fields")
        cid, source, target = item["id"], item["source"], item["fork_name"]
        if not isinstance(cid, str) or not ITEM_ID.fullmatch(cid):
            raise BatchError("Invalid candidate ID")
        if not isinstance(source, str) or source.count("/") != 1 or not isinstance(target, str):
            raise BatchError("Invalid draft repository identity")
        try:
            owner, name = (create_fork.slug(x) for x in source.split("/"))
            create_fork.slug(target)
        except create_fork.ForkError:
            raise BatchError("Invalid draft repository slug") from None
        stages = item["stages"]
        if (not isinstance(stages, list) or not stages
                or len(stages) > len(DRAFT_STAGES)
                or any(not isinstance(x, str) or x not in DRAFT_STAGES for x in stages)
                or stages != [x for x in DRAFT_STAGES if x in stages]):
            raise BatchError("Invalid or repeated contribution stage")
        blockers = item["blockers"]
        if (not isinstance(blockers, list) or len(blockers) > 5
                or any(not isinstance(x, str) or not 5 <= len(x.strip()) <= 300
                       or any(ord(char) < 32 for char in x)
                       for x in blockers)):
            raise BatchError("Invalid blockers")
        license_id = item["expected_license"]
        if license_id is None:
            if not blockers:
                raise BatchError("Unreviewed license must block selection")
        elif (not isinstance(license_id, str) or not LICENSE.fullmatch(license_id)
              or license_id.upper() in ("UNKNOWN", "NOASSERTION")):
            raise BatchError("Invalid or unresolved draft SPDX license")
        if "create_public_fork" in stages and owner.casefold() == create_fork.DEST.casefold():
            raise BatchError("Cannot fork from destination organization")
        # Blocked proposals may have no public evidence yet, but never fabricate a URL.
        validate_proposal(item["proposal"], allow_missing_evidence=bool(blockers))
        if cid in seen_ids or (owner + "/" + name).casefold() in seen_sources:
            raise BatchError("Duplicate candidate ID or upstream source")
        if "create_public_fork" in stages and target.casefold() in seen_targets:
            raise BatchError("Duplicate destination fork name")
        seen_ids.add(cid)
        seen_sources.add((owner + "/" + name).casefold())
        if "create_public_fork" in stages:
            seen_targets.add(target.casefold())
    return data, canonical_digest(data)


def preview_draft(path, *, selected_ids=None):
    """Pure proposal preview. Selection is not a grant and has no side effects."""
    data, digest = load_draft(path)
    if selected_ids is None:
        selected_ids = []
    if not isinstance(selected_ids, (list, tuple)):
        raise BatchError("Selected IDs must be a list")
    if any(not isinstance(x, str) for x in selected_ids):
        raise BatchError("Invalid selected ID")
    if len(set(selected_ids)) != len(selected_ids):
        raise BatchError("Duplicate selected IDs")
    ids = {x["id"] for x in data["candidates"]}
    if set(selected_ids) - ids:
        raise BatchError("Selection includes unknown candidates")
    selected = set(selected_ids)
    entries = []
    for candidate in data["candidates"]:
        choice = candidate["id"] in selected
        entries.append({
            "id": candidate["id"],
            "source": candidate["source"],
            "fork_name": candidate["fork_name"],
            "expected_license": candidate["expected_license"],
            "stages": candidate["stages"],
            "proposal": candidate["proposal"],
            "selected": choice,
            "status": "BLOCKED" if candidate["blockers"] else "PROPOSED_ONLY",
            "blockers": candidate["blockers"]
        })
    return {
        "batch_id": data["batch_id"], "revision": data["revision"],
        "proposal_sha256": digest, "status": "PROPOSAL_PREVIEW",
        "selection_sha256": canonical_digest({
            "batch_id": data["batch_id"], "revision": data["revision"],
            "proposal_sha256": digest, "selected_ids": sorted(selected)
        }),
        "authorization_status": "NOT_APPROVED_NO_WRITES",
        "selected_ids": selected_ids,
        "selection_has_blockers": any(x["selected"] and x["blockers"] for x in entries),
        "candidates": entries
    }


def load_manifest(path, *, now=None):
    path = Path(path)
    if not BATCH_ID.fullmatch(path.stem) or path.suffix != ".json":
        raise BatchError("Invalid manifest filename")
    try:
        raw = path.read_bytes()
        if len(raw) > 16384:
            raise BatchError("Manifest too large")
        data = json.loads(raw, object_pairs_hook=no_duplicate_keys)
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        raise BatchError("Cannot read JSON manifest: " + type(exc).__name__) from None
    if not isinstance(data, dict) or set(data) != BATCH_FIELDS:
        raise BatchError("Unexpected batch fields")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise BatchError("Unsupported schema version")
    if data["batch_id"] != path.stem:
        raise BatchError("Batch ID does not match filename")
    if data["approved_by"] != "xLagerFeuer" or data["approval_medium"] != "agent_chat":
        raise BatchError("Declared operator/conversational approval context mismatch")
    if not isinstance(data["approval_ref"], str) or not APPROVAL_URL.fullmatch(data["approval_ref"]):
        raise BatchError("Approval reference must be an upstream issue or PR")
    approved, expires = parse_time(data["approved_at"]), parse_time(data["expires_at"])
    now = now or datetime.now(timezone.utc)
    if approved > now or expires <= now or expires <= approved:
        raise BatchError("Approval not valid at execution time")
    if expires - approved > timedelta(days=7):
        raise BatchError("Approval validity exceeds seven days")
    items = data["items"]
    if not isinstance(items, list) or not (1 <= len(items) <= 10):
        raise BatchError("Batch must contain 1 to 10 approved entries")
    ids, sources, targets = set(), set(), set()
    for item in items:
        if not isinstance(item, dict) or set(item) != ITEM_FIELDS:
            raise BatchError("Unexpected entry fields")
        if not isinstance(item["id"], str) or not ITEM_ID.fullmatch(item["id"]):
            raise BatchError("Invalid item ID")
        if item["action"] != "create_public_fork":
            raise BatchError("Unapproved action type")
        source, name = item["source"], item["fork_name"]
        if not isinstance(source, str) or source.count("/") != 1 or not isinstance(name, str):
            raise BatchError("Invalid repository identity")
        try:
            owner, repository = (create_fork.slug(p) for p in source.split("/"))
            create_fork.slug(name)
        except create_fork.ForkError:
            raise BatchError("Invalid repository identity") from None
        if owner.casefold() == create_fork.DEST.casefold():
            raise BatchError("Source cannot be within destination org")
        validate_proposal(item["proposal"])
        license_id = item["expected_license"]
        if (not isinstance(license_id, str) or not LICENSE.fullmatch(license_id)
                or license_id.upper() in {"UNKNOWN", "NOASSERTION"}):
            raise BatchError("Explicit reviewed SPDX license required")
        source_key = (owner + "/" + repository).casefold()
        if item["id"] in ids or source_key in sources or name.casefold() in targets:
            raise BatchError("Duplicate item/source/destination")
        ids.add(item["id"])
        sources.add(source_key)
        targets.add(name.casefold())
    return data, canonical_digest(data)

def run_batch(path, *, execute=False, now=None, create_fn=create_fork.run):
    if execute:
        raise BatchError("Batch execution inactive: verified authorization runner is not installed")
    data, digest = load_manifest(path, now=now)
    checks = []
    # No fork creation begins until every approved item passes preflight.
    for item in data["items"]:
        try:
            observed = create_fn(item["source"], item["fork_name"],
                                 expected_license=item["expected_license"])
        except create_fork.ForkError as exc:
            raise BatchError("Preflight " + item["id"] + ": " + str(exc)) from None
        if observed["status"] not in ("DRY_RUN", "EXISTS_VERIFIED"):
            raise BatchError("Unexpected preflight status")
        checks.append({"id": item["id"], "source": item["source"],
                       "proposal": item["proposal"],
                       "destination": create_fork.DEST + "/" + item["fork_name"],
                       "status": observed["status"]})
    report = {"batch_id": data["batch_id"], "sha256": digest,
              "approval_ref": data["approval_ref"],
              "approved_by_asserted": data["approved_by"], "preflight": checks}
    report["authorization_status"] = "UNVERIFIED_NOT_EXECUTABLE"
    return {**report, "status": "PREFLIGHT_PASS"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--draft", action="store_true", help="Preview proposal without approval or GitHub API access")
    parser.add_argument("--select", default="", help="Comma-separated candidate IDs, proposal preview only")
    args = parser.parse_args()
    if args.execute:
        print("BATCH_ERROR: executable batch workflow is not integrated or validated; refusing writes", file=sys.stderr)
        return 1
    try:
        if args.select and not args.draft:
            raise BatchError("--select is only valid with --draft")
        if args.draft:
            selection = [x.strip() for x in args.select.split(",")] if args.select else []
            report = preview_draft(args.manifest, selected_ids=selection)
        else:
            report = run_batch(args.manifest, execute=False)
        serialized = json.dumps(report, sort_keys=True)
        print(serialized)
        if os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
                f.write("Read-only batch preview (NOT an authorization): " + serialized + "\n")
        return 0 if report["status"] in ("PREFLIGHT_PASS", "PROPOSAL_PREVIEW") else 1
    except BatchError as exc:
        print("BATCH_ERROR: " + str(exc), file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
