#!/usr/bin/env python3
"""Deterministic source-to-working-fork outbox for the Upstream batch pipeline.

This script never creates forks, pushes code, or opens external PRs. It keeps
the 100-source priority snapshot and *all* historically screened batches in
one regenerable registry, including negative screens and blocked cases.
Actual fork and patch operations require a separate trusted executor under
Upstream #6/#28; external PR publication always requires a human decision.
"""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
POOL = Path("data/fork-priorities/2026-11-08.json")
BATCH_DIR = Path("data/assessment-candidate-batches")
REGISTRY = Path("data/contribution-workspaces/registry.json")
PILOTS = Path("data/contribution-workspaces/pilot-sources.json")
PR_HISTORY = Path("data/upstream-lifecycle.json")
FORK_READBACK_DIR = Path("data/contribution-workspaces/fork-readbacks")
SOURCE = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
COMMIT_SHA = re.compile(r"[0-9a-f]{40}\Z")
LOCAL_HANDOFF = re.compile(
    r"https://github\.com/opensiro/upstream/blob/(?:main|[0-9a-f]{40})/"
    r"(pilots/[A-Za-z0-9_.-]+/CONTRIBUTION_HANDOFF\.md)\Z"
)
POOL_GROUPS = (
    ("existing_forks", "EXISTING_FORK"),
    ("prepared_packets_missing_forks", "PREPARED_PACKET"),
    ("new_index_hypothesis_screens", "INDEX_HYPOTHESIS"),
)
STAGES = {"SCREENING", "ACTIVE", "AWAITING_EXTERNAL", "CLOSED_CHANGE",
          "CLOSED_NO_CHANGE", "BLOCKED_EVIDENCE", "ESCALATED"}


class WorkspaceError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise WorkspaceError(message)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def key(source):
    require(type(source) is str and SOURCE.fullmatch(source),
            f"Invalid source identity: {source!r}")
    return source.casefold()


def _safe_pilot_file(root, path):
    if type(path) is not str:
        return None
    relative = Path(path)
    if (relative.is_absolute() or len(relative.parts) < 3
            or relative.parts[0] != "pilots"
            or any(part in ("..", ".") for part in relative.parts)):
        return None
    candidate = root / relative
    if candidate.is_symlink() or any(p.is_symlink() for p in candidate.parents
                                     if p != root and root in p.parents):
        raise WorkspaceError(f"Symlink in pilot artifact path: {path}")
    return candidate if candidate.is_file() else None


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _pilot_snapshot(root, local_path):
    """Hash existing local pilot evidence, without promoting it to a tested patch."""
    directory = (root / local_path).parent
    if not directory.is_dir() or directory.is_symlink():
        return None
    digest = hashlib.sha256()
    patches = []
    paths = sorted(directory.rglob("*"), key=lambda p: p.relative_to(root).as_posix())
    if any(p.is_symlink() for p in paths):
        raise WorkspaceError(f"Symlink inside pilot packet: {directory}")
    files = [p for p in paths if p.is_file()]
    for path in files:
        rel = path.relative_to(root).as_posix()
        sha = _sha(path)
        digest.update((rel + "\0" + sha + "\n").encode("utf-8"))
        if path.suffix.lower() == ".patch":
            patches.append({"path": rel, "sha256": sha})
    return {"directory": directory.relative_to(root).as_posix(),
            "files": len(files), "content_sha256": digest.hexdigest(),
            "patch_candidates": patches}


def _technical_packet(root, item):
    """Read-only bridge from frozen batch handoff to mutable local artifact bytes.

    A discovered .patch is not a selected, source-tested or executable patch.
    """
    result = {"state": "NO_LOCAL_PATCH_SELECTED", "pilot": None,
              "explicit_patch": None, "explicit_test_patch": None}
    url = item.get("handoff_url")
    match = LOCAL_HANDOFF.fullmatch(url) if type(url) is str else None
    if match:
        pilot_path = match.group(1)
        if _safe_pilot_file(root, pilot_path) is None:
            result["state"] = "LINKED_PILOT_MISSING"
        else:
            result["pilot"] = _pilot_snapshot(root, pilot_path)
    for field, dest in (("patch_path", "explicit_patch"),
                        ("test_patch_path", "explicit_test_patch")):
        value = item.get(field)
        if value is None:
            continue
        path = _safe_pilot_file(root, value)
        result[dest] = {"path": value,
                        "sha256": _sha(path) if path is not None else None}
        if path is None:
            result["state"] = "EXPLICIT_PATCH_MISSING_OR_UNSAFE"

    if result["state"] == "EXPLICIT_PATCH_MISSING_OR_UNSAFE":
        return result
    if result["explicit_patch"]:
        expected = item.get("patch_sha256")
        observed = result["explicit_patch"]["sha256"]
        if expected is not None and observed != expected:
            result["state"] = "EXPLICIT_PATCH_DIGEST_MISMATCH"
        else:
            result["state"] = ("EXPLICIT_PATCH_HASH_MATCHED"
                               if expected is not None else "EXPLICIT_PATCH_UNPINNED")
        return result
    if result["pilot"] is None:
        if result["state"] != "LINKED_PILOT_MISSING":
            result["state"] = "NO_LOCAL_PACKET_OR_PR_ONLY_HANDOFF"
        return result
    candidates = result["pilot"]["patch_candidates"]
    result["state"] = (
        "LOCAL_SINGLE_PATCH_UNREVIEWED" if len(candidates) == 1
        else "LOCAL_MULTI_PATCH_SELECTION_REQUIRED" if candidates
        else "LOCAL_PACKET_WITHOUT_PATCH"
    )
    return result


def _dated_fork_readbacks(root):
    """Validate dated, reviewable GitHub readbacks; never attest live write rights."""
    latest = {}
    fork_owners = {}
    for path in sorted((root / FORK_READBACK_DIR).glob("*.json")):
        report = read(path)
        require(report.get("schema_version") == 1
                and report.get("observed_on") == path.stem
                and report.get("source") == "CONNECTED_GITHUB_REST_READ_ONLY"
                and isinstance(report.get("entries"), list),
                f"Malformed dated fork observation {path}")
        unique = set()
        for item in report["entries"]:
            source = item["source"]
            source_key = key(source)
            fork = item["fork"]
            require(key(fork).startswith("opensiro-contributions/")
                    and source_key not in unique,
                    f"Invalid or duplicate fork readback: {source}")
            unique.add(source_key)
            known_owner = fork_owners.setdefault(key(fork), source_key)
            require(known_owner == source_key,
                    f"One read-back fork is associated with multiple sources: {fork}")
            if source_key in latest:
                require(latest[source_key]["fork"].casefold() == fork.casefold(),
                        f"Fork mapping changed between dated receipts: {source}")
            require(item.get("parent_verified") is True
                    and item.get("public_fork_verified") is True
                    and type(item.get("branch")) is str and item["branch"]
                    and type(item.get("fork_sha")) is str
                    and COMMIT_SHA.fullmatch(item["fork_sha"])
                    and type(item.get("source_same_named_branch_sha")) is str
                    and COMMIT_SHA.fullmatch(item["source_same_named_branch_sha"])
                    and item.get("ref_relation") == (
                        "MATCH" if item["fork_sha"]
                        == item["source_same_named_branch_sha"] else "DIFFERENT_SHAS"),
                    f"Invalid dated fork observation fields: {source}")
            require(item.get("repo_evidence") == f"https://api.github.com/repos/{fork}"
                    and item.get("fork_branch_evidence") ==
                        f"https://api.github.com/repos/{fork}/branches/{item['branch']}"
                    and item.get("source_branch_evidence") ==
                        f"https://api.github.com/repos/{source}/branches/{item['branch']}",
                    f"Missing or mismatched GitHub readback provenance: {source}")
            latest[source_key] = {
                "observed_on": report["observed_on"],
                "receipt": path.relative_to(root).as_posix(),
                "fork": fork,
                "branch": item["branch"],
                "fork_sha": item["fork_sha"],
                "source_same_named_branch_sha": item["source_same_named_branch_sha"],
                "ref_relation": item["ref_relation"],
                "recheck_before_any_write": True,
            }
    return latest


def build(root=ROOT):
    root = Path(root)
    fork_readbacks = _dated_fork_readbacks(root)
    pool = read(root / POOL)
    require(pool.get("schema_version") == 1, "Unsupported priority pool")
    sources = {}
    for field, kind in POOL_GROUPS:
        for item in pool[field]:
            source = item["source"]
            identity = key(source)
            require(identity not in sources, f"Duplicate priority source: {source}")
            sources[identity] = {
                "source": source,
                "priority_group": kind,
                "batches": [],
                "latest_stage": None,
                "handoffs": [],
                "pilot_links": [],
                "historical_prs": [],
                "fork": item.get("fork") if kind == "EXISTING_FORK" else None,
            }

    require(len(sources) == pool["counts"]["total"] == 100,
            "Priority cohort must retain its exact 100 sources")
    deferred = {key(item["source"]) for item in
                pool["deferred_prepared_packet_license_review"]}
    batch_files = sorted((root / BATCH_DIR).glob("*.json"))
    seen_batches = set()
    for path in batch_files:
        manifest = read(path)
        batch_id = manifest.get("batch_id")
        require(manifest.get("schema_version") == 1
                and manifest.get("state") == "FROZEN_SCREENING"
                and isinstance(batch_id, str) and batch_id not in seen_batches,
                f"Invalid or duplicate batch: {path.name}")
        seen_batches.add(batch_id)
        seen_in_batch = set()
        for item in manifest["candidates"]:
            source = item["source"]
            identity = key(source)
            require(identity not in seen_in_batch,
                    f"Duplicate source in {batch_id}: {source}")
            seen_in_batch.add(identity)
            require(item["stage"] in STAGES,
                    f"Unexpected {batch_id} stage: {item['stage']}")
            if identity not in sources:
                sources[identity] = {
                    "source": source,
                    "priority_group": "HISTORICAL_EXTRA",
                    "batches": [],
                    "latest_stage": None,
                    "handoffs": [],
                    "pilot_links": [],
                    "historical_prs": [],
                    "fork": None,
                }
            record = sources[identity]
            require(record["source"].casefold() == source.casefold(),
                    "Source identity drift")
            record["batches"].append(path.relative_to(root).as_posix())
            record["latest_stage"] = item["stage"]
            if item["stage"] in {"AWAITING_EXTERNAL", "CLOSED_CHANGE"}:
                # Local artifact references only: an external fork commit is
                # never inferred from a handoff or a passing native test.
                record["handoffs"].append({
                    "candidate_id": item["id"],
                    "stage": item["stage"],
                    "origin": item["origin"],
                    "handoff_url": item.get("handoff_url"),
                    "patch_path": item.get("patch_path"),
                    "patch_sha256": item.get("patch_sha256"),
                    "test_patch_path": item.get("test_patch_path"),
                    "technical_packet": _technical_packet(root, item),
                })

    # Earlier product-native pilots were outside the five-source assessment
    # batches, but are equally important worked-source inventory. The explicit
    # mappings are backed by first-party receipts or internal reviewable PRs.
    pilots = read(root / PILOTS)
    require(pilots.get("schema_version") == 1, "Unsupported pilot source ledger")
    pilot_sources = set()
    for item in pilots["cases"]:
        source = item["source"]
        identity = key(source)
        require(identity not in pilot_sources, f"Duplicate pilot source {source}")
        pilot_sources.add(identity)
        evidence = item["evidence"]
        require(type(evidence) is str and
                (evidence.startswith("https://github.com/opensiro/upstream/pull/")
                 or ((root / evidence).is_file() and not Path(evidence).is_absolute())),
                f"Unverifiable pilot receipt for {source}")
        if identity not in sources:
            sources[identity] = {
                "source": source, "priority_group": "PILOT_EXTRA",
                "batches": [], "latest_stage": None, "handoffs": [],
                "pilot_links": [], "historical_prs": [], "fork": None,
            }
        sources[identity]["pilot_links"].append({
            "case_id": item["case_id"], "evidence": evidence,
            "patch_path": item.get("patch_path"),
            "local_evidence": (
                _pilot_snapshot(root, evidence)
                if evidence.startswith("pilots/") else None
            ),
            "local_patch_sha256": (
                _sha(path) if (path := _safe_pilot_file(root, item.get("patch_path")))
                is not None else None
            ),
        })

    # Historical casebook/registry PRs are source identity evidence, not
    # future publication work or a verified opensiro-contributions fork.
    history = read(root / PR_HISTORY)
    require(history.get("schema_version") == 2, "Unsupported historical PR record")
    historical = list(history["records"]) + list(history["registry_records"])
    for item in historical:
        pr = item.get("original_pr", item.get("pr"))
        require(isinstance(pr, dict), f"Missing PR identity for {item.get('id')}")
        url = pr["url"]
        parsed = urlparse(url)
        parts = parsed.path.strip("/").split("/")
        require(parsed.scheme == "https" and parsed.netloc == "github.com"
                and len(parts) == 4 and parts[2] == "pull"
                and parts[3].isdigit() and not parsed.query and not parsed.fragment,
                f"Invalid historical PR identity {url}")
        source = "/".join(parts[:2])
        identity = key(source)
        if identity not in sources:
            sources[identity] = {
                "source": source, "priority_group": "PORTFOLIO_EXTRA",
                "batches": [], "latest_stage": None, "handoffs": [],
                "pilot_links": [], "historical_prs": [], "fork": None,
            }
        sources[identity]["historical_prs"].append(url)

    # Destination basenames are *not* sufficient proof of a fork's parent.
    # A collision may be resolved only after a verified exact fork readback.
    names = defaultdict(list)
    for identity, record in sources.items():
        names[record["source"].split("/", 1)[1].casefold()].append(identity)
    collisions = {n for n, identities in names.items() if len(identities) > 1}
    mapped = set()
    for identity, record in sources.items():
        source = record["source"]
        name = source.split("/", 1)[1]
        actual = record["fork"]
        observed = fork_readbacks.get(identity)
        if observed is not None:
            require(actual is None or actual.casefold() == observed["fork"].casefold(),
                    f"Dated fork readback conflicts with reviewed working-fork mapping: {source}")
        record["dated_fork_readback"] = observed
        if actual is not None:
            require(type(actual) is str and SOURCE.fullmatch(actual)
                    and actual.split("/", 1)[0].casefold() == "opensiro-contributions",
                    f"Invalid recorded working fork for {source}")
            require(actual.casefold() not in mapped,
                    f"Conflicting recorded forks: {actual}")
            mapped.add(actual.casefold())
            record["fork_state"] = "HISTORICAL_MAPPING_REQUIRES_LIVE_READBACK"
            record["proposed_fork"] = actual
        elif observed is not None:
            # The frozen 100-source snapshot is NOT an updatable list of all
            # future forks. A dated provider readback may bind an extra source
            # without rewriting that historical priority cohort.
            require(observed["fork"].casefold() not in mapped,
                    f"Read-back destination collides with another fork: {observed['fork']}")
            mapped.add(observed["fork"].casefold())
            record["fork_state"] = "DATED_MAPPING_REQUIRES_LIVE_READBACK"
            record["proposed_fork"] = observed["fork"]
        elif name.casefold() in collisions:
            record["fork_state"] = "NAME_COLLISION_REQUIRES_EXACT_DECISION"
            record["proposed_fork"] = None
        else:
            record["fork_state"] = "UNVERIFIED_NOT_PROVISIONED"
            record["proposed_fork"] = "opensiro-contributions/" + name

        record["license_review"] = identity in deferred
        stage = record["latest_stage"]
        if record["license_review"]:
            record["next_step"] = "BLOCKED_LICENSE_REVIEW"
        elif record["fork_state"] == "NAME_COLLISION_REQUIRES_EXACT_DECISION":
            record["next_step"] = "RESOLVE_FORK_PARENT_AND_NAME"
        elif stage in {"AWAITING_EXTERNAL", "CLOSED_CHANGE"}:
            record["next_step"] = "VERIFY_FORK_AND_PREPARE_PATCH_WITH_STAGE_GRANT"
        elif stage == "CLOSED_NO_CHANGE":
            record["next_step"] = "TRACK_ONLY_NO_CHANGE"
        elif stage == "BLOCKED_EVIDENCE":
            record["next_step"] = "TRACK_ONLY_REEVALUATE_EVIDENCE"
        elif record["pilot_links"]:
            record["next_step"] = "RECONCILE_NATIVE_PILOT_BEFORE_FORK_STAGE"
        elif record["historical_prs"]:
            record["next_step"] = "HISTORICAL_PR_TRACK_ONLY_NO_NEW_PUBLICATION"
        else:
            record["next_step"] = "SCREEN_BEFORE_FORK_WRITE"

    require(set(fork_readbacks).issubset(sources),
            "Dated fork readback references an unknown source")
    ordered = sorted(sources.values(), key=lambda r: r["source"].casefold())
    return {
        "schema_version": 1,
        "priority_snapshot": POOL.as_posix(),
        "batch_sources": BATCH_DIR.as_posix() + "/*.json",
        "counts": {
            "priority_sources": 100,
            "historical_extras": sum(r["priority_group"] in {
                "HISTORICAL_EXTRA", "PILOT_EXTRA", "PORTFOLIO_EXTRA"} for r in ordered),
            "batch_only_extras": sum(r["priority_group"] == "HISTORICAL_EXTRA" for r in ordered),
            "pilot_only_extras": sum(r["priority_group"] == "PILOT_EXTRA" for r in ordered),
            "portfolio_only_extras": sum(r["priority_group"] == "PORTFOLIO_EXTRA" for r in ordered),
            "unique_sources": len(ordered),
            "batch_manifests": len(batch_files),
            "batch_cases": sum(len(r["batches"]) for r in ordered),
            "historical_fork_mappings": sum(r["fork"] is not None for r in ordered),
            "name_collision_sources": sum(r["fork_state"] == "NAME_COLLISION_REQUIRES_EXACT_DECISION" for r in ordered),
            "technical_handoffs": sum(len(r["handoffs"]) for r in ordered),
            "dated_fork_readbacks": sum(r["dated_fork_readback"] is not None
                                        for r in ordered),
            "same_named_ref_matches_at_readback": sum(
                r["dated_fork_readback"] is not None and
                r["dated_fork_readback"]["ref_relation"] == "MATCH"
                for r in ordered),
            "technical_packet_states": dict(sorted(Counter(
                h["technical_packet"]["state"] for r in ordered
                for h in r["handoffs"]).items())),
        },
        "execution": {
            "fork_and_patch_writes": "SEPARATE_TRUSTED_HOST_STAGE_GRANT_REQUIRED",
            "continuous_link": "REGENERATE_WITH_EVERY_BATCH_OR_PATCH_RECORD_CHANGE",
            # Source-linked intent only: current-main policy and native gates
            # must be independently checked by the actual publisher.
            "external_pr": "CHECK_EFFECTIVE_STANDING_MANDATE_AND_NATIVE_GATES",
            "external_pr_policy_source": "policies/standing-external-publication-p1.json",
            # No unattended end-to-end executor is attested by this registry.
            "auto_external_pr": False,
            "live_forks_verified_by_this_script": False,
            "dated_fork_readback_is_live_authority": False,
        },
        "sources": ordered,
    }


def encoded(report):
    return json.dumps(report, ensure_ascii=False, indent=2) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("status", "list", "sync", "check"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--source", help="Exact owner/repository filter for list")
    args = parser.parse_args(argv)
    try:
        report = build(args.root)
        output = args.root / REGISTRY
        if args.command == "sync":
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(encoded(report), encoding="utf-8")
        elif args.command == "check":
            require(output.exists() and output.read_text(encoding="utf-8") == encoded(report),
                    f"Stale {REGISTRY}; run scripts/contribution_workspaces.py sync")
        elif args.command == "list":
            if args.source:
                identity = key(args.source)
                matches = [r for r in report["sources"]
                           if r["source"].casefold() == identity]
                require(matches, f"Unknown source {args.source}")
            else:
                matches = report["sources"]
            print(json.dumps(matches, indent=2, ensure_ascii=False))
        else:
            print(json.dumps({"counts": report["counts"],
                              "execution": report["execution"],
                              "next_steps": dict(sorted(Counter(
                                  r["next_step"] for r in report["sources"]).items()))},
                             indent=2))
    except (OSError, KeyError, TypeError, ValueError, WorkspaceError) as exc:
        parser.exit(2, f"WORKSPACE_INVALID: {exc}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
