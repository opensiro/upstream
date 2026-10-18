#!/usr/bin/env python3
"""Provider-agnostic, local-only batch proposal preview; never an approval or GitHub writer."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

DEST = "opensiro-contributions"
BATCH_ID = re.compile(r"^upstream-[0-9]{8}-[a-z0-9][a-z0-9-]{0,39}$")
ITEM_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")
LICENSE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.+-]{0,49}$")
SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$")
PROPOSAL_FIELDS = {"system_component", "problem", "planned_change",
                   "expected_improvement", "validation", "evidence_url"}


class BatchError(Exception):
    pass


def validate_slug(value):
    if not isinstance(value, str) or not SLUG.fullmatch(value) or value.endswith("."):
        raise BatchError("Invalid draft repository slug")
    return value


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
        with path.open("rb") as source:
            raw = source.read(16385)
        if len(raw) > 16384:
            raise BatchError("Draft batch too large")
        data = json.loads(raw, object_pairs_hook=no_duplicate_keys)
    except (OSError, ValueError, UnicodeDecodeError, RecursionError) as exc:
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
            owner, name = (validate_slug(x) for x in source.split("/"))
            validate_slug(target)
        except BatchError:
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
        if "create_public_fork" in stages and owner.casefold() == DEST.casefold():
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


def render_draft_text(report):
    """Plain-text operator view, deliberately without approval or execution commands."""
    if report.get("status") != "PROPOSAL_PREVIEW":
        raise BatchError("Text view is limited to read-only proposal previews")
    lines = [
        "BATCH " + report["batch_id"] + " / revision " + str(report["revision"]),
        "PROPOSAL ONLY — NOT APPROVED — NO GITHUB WRITES",
        "Proposal SHA-256: " + report["proposal_sha256"],
        "Selection SHA-256: " + report["selection_sha256"],
        "",
    ]
    for i, candidate in enumerate(report["candidates"], start=1):
        selected = "SELECTED FOR PREVIEW" if candidate["selected"] else "not selected"
        blocked = " / BLOCKED" if candidate["blockers"] else ""
        detail = candidate["proposal"]
        lines.extend([
            str(i) + ". " + candidate["id"] + " (" + selected + blocked + ")",
            "   Target: " + candidate["source"],
            "   Requested stages: " + " + ".join(candidate["stages"]),
            "   Destination fork name: " + candidate["fork_name"],
            "   Declared SPDX license (unverified): " + (candidate["expected_license"] or "not reviewed"),
            "   Problem: " + detail["problem"],
            "   Change: " + detail["planned_change"],
            "   Expected benefit: " + detail["expected_improvement"] + " (unverified)",
            "   Validation: " + detail["validation"],
            "   Claimed public evidence URL (unchecked): " + (detail["evidence_url"] or "MISSING"),
        ])
        for blocker in candidate["blockers"]:
            lines.append("   Blocker: " + blocker)
        lines.append("")
    if report["selection_has_blockers"]:
        lines.append("Selected entries include BLOCKED items; do not treat as eligible.")
    lines.append("This is selection preview only; no operator authorization was recorded.")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="No-write, no-approval contribution draft preview")
    parser.add_argument("--manifest", required=True, help="Local proposal-only JSON file")
    parser.add_argument("--draft", action="store_true", help="Required; this CLI never accepts approval")
    parser.add_argument("--select", default="", help="Comma-separated IDs; preview only")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args(argv)
    if not args.draft:
        print("DRAFT_ERROR: --draft is required; approvals and execution are unsupported", file=sys.stderr)
        return 1
    try:
        selection = [x.strip() for x in args.select.split(",")] if args.select else []
        report = preview_draft(args.manifest, selected_ids=selection)
        print(render_draft_text(report) if args.format == "text"
              else json.dumps(report, sort_keys=True, ensure_ascii=False))
        return 0
    except BatchError as exc:
        print("DRAFT_ERROR: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())