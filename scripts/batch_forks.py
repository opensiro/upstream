#!/usr/bin/env python3
"""Execute precisely an approved batch; approval attribution is not a signed identity."""
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

def validate_proposal(proposal):
    """Validate the frozen descriptive intent; never treat it as an execution command."""
    if not isinstance(proposal, dict) or set(proposal) != PROPOSAL_FIELDS:
        raise BatchError("Contribution proposal must contain every required field")
    for field in PROPOSAL_FIELDS - {"evidence_url"}:
        value = proposal[field]
        if not isinstance(value, str) or not (12 <= len(value.strip()) <= 1000):
            raise BatchError("Contribution proposal field missing or too long: " + field)
        if any(ord(char) < 32 and char not in "\\n\\t" for char in value):
            raise BatchError("Invalid control character in proposal")
        if value.strip().casefold() in {"tbd", "todo", "n/a", "unknown"}:
            raise BatchError("Placeholder is not a contribution proposal")
    evidence = proposal["evidence_url"]
    if not isinstance(evidence, str) or len(evidence) > 2048:
        raise BatchError("Missing or invalid proposal evidence URL")
    try:
        url = urlsplit(evidence)
        if url.scheme != "https" or not url.hostname or url.username or url.password:
            raise BatchError("Proposal evidence must be a public HTTPS URL")
    except ValueError:
        raise BatchError("Malformed proposal evidence URL") from None


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
        if not isinstance(license_id, str) or not LICENSE.fullmatch(license_id) or license_id == "UNKNOWN":
            raise BatchError("Explicit reviewed SPDX license required")
        source_key = (owner + "/" + repository).casefold()
        if item["id"] in ids or source_key in sources or name.casefold() in targets:
            raise BatchError("Duplicate item/source/destination")
        ids.add(item["id"])
        sources.add(source_key)
        targets.add(name.casefold())
    return data, hashlib.sha256(raw).hexdigest()

def run_batch(path, *, execute=False, now=None, create_fn=create_fork.run):
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
    if not execute:
        return {**report, "status": "PREFLIGHT_PASS"}
    if not os.environ.get("UPSTREAM_FORK_TOKEN"):
        raise BatchError("Fork creation token unavailable")
    receipts = []
    for item in data["items"]:
        try:
            result = create_fn(item["source"], item["fork_name"], execute=True,
                               expected_license=item["expected_license"])
            receipts.append({"id": item["id"], **result})
        except create_fork.ForkError as exc:
            receipts.append({"id": item["id"], "status": "BLOCKED", "reason": str(exc)})
    success = all(x["status"] in {"CREATED_VERIFIED", "EXISTS_VERIFIED"} for x in receipts)
    return {**report, "status": "COMPLETED" if success else "INCOMPLETE", "results": receipts}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.execute:
        print("BATCH_ERROR: executable batch workflow is not integrated or validated; refusing writes", file=sys.stderr)
        return 1
    try:
        report = run_batch(args.manifest, execute=False)
        serialized = json.dumps(report, sort_keys=True)
        print(serialized)
        if os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
                f.write("Approved batch: " + serialized + "\n")
        return 0 if report["status"] in ("PREFLIGHT_PASS", "COMPLETED") else 1
    except BatchError as exc:
        print("BATCH_ERROR: " + str(exc), file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
