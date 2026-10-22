#!/usr/bin/env python3
"""Read-only assessment-first Upstream candidate-batch ledger and NEXT selection."""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HEX40 = re.compile(r"[0-9a-f]{40}\Z")
SOURCE = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
ASSESSMENT = re.compile(r"assessments/[a-z0-9-]{2}/[a-z0-9-]+\.md\Z")
FIT_KEYS = {"need", "mechanism", "counterfactual", "scope"}
FIT_STATES = {"PENDING", "PASS", "FAIL"}
ORIGINS = {"ASSESSMENT_DERIVED", "ASSESSMENT_INFORMED", "GENERAL_UPSTREAM", "INSUFFICIENT"}
STAGES = {"SCREENING", "ACTIVE", "AWAITING_EXTERNAL", "CLOSED_CHANGE", "CLOSED_NO_CHANGE", "BLOCKED_EVIDENCE", "ESCALATED"}
SKIP = {"AWAITING_EXTERNAL", "CLOSED_CHANGE", "CLOSED_NO_CHANGE", "BLOCKED_EVIDENCE", "ESCALATED"}


class BatchError(ValueError):
    pass


def _require(condition, message):
    if not condition:
        raise BatchError(message)


def _frontmatter(contents):
    _require(contents.startswith("---\n"), "Index assessment must have YAML frontmatter")
    fields = {}
    for line in contents.split("---\n", 2)[1].splitlines():
        if ": " in line:
            key, value = line.split(": ", 1)
            fields[key] = value.strip().strip('"\'')
    return fields


def _git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True, check=False)
    _require(result.returncode == 0, f"Index git object unavailable: {result.stderr.strip()}")
    return result.stdout.strip()


def validate(manifest, index_root=None):
    """Check manifest and, if provided, exact local Index HEAD/object provenance."""
    _require(isinstance(manifest, dict) and manifest.get("schema_version") == 1, "Unsupported schema")
    _require(re.fullmatch(r"assessment-upstream-\d{4}-\d{2}-\d{2}-\d{2}", manifest.get("batch_id", "")) is not None, "Invalid batch ID")
    _require(manifest.get("owner_issue") == "https://github.com/opensiro/upstream/issues/56", "Invalid owner")
    sha = manifest.get("index_sha", "")
    _require(isinstance(sha, str) and HEX40.fullmatch(sha), "Exact Index SHA required")
    _require(manifest.get("state") == "FROZEN_SCREENING", "Cohort selection must remain frozen")
    items = manifest.get("candidates")
    _require(isinstance(items, list) and 5 <= len(items) <= 10, "Freeze a full cohort of 5–10 records")
    _require(isinstance(manifest.get("selection_note"), str) and len(manifest["selection_note"]) >= 30, "Selection policy needed")
    seen_ids, seen_sources, seen_paths = set(), set(), set()
    order = []
    if index_root is not None:
        root = Path(index_root)
        _require(_git(root, "rev-parse", "HEAD") == sha, "Index HEAD differs from frozen SHA")
    for row in items:
        _require(isinstance(row, dict), "Candidate must be an object")
        ident = row.get("id", "")
        source = row.get("source", "")
        path = row.get("assessment_path", "")
        ref = row.get("review_ref", "")
        _require(isinstance(ident, str) and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", ident), "Invalid candidate ID")
        _require(isinstance(source, str) and SOURCE.fullmatch(source), f"Invalid repository for {ident}")
        _require(isinstance(path, str) and ASSESSMENT.fullmatch(path), f"Invalid Index path for {ident}")
        _require(isinstance(ref, str) and HEX40.fullmatch(ref), f"Missing reviewed revision for {ident}")
        _require(ident not in seen_ids and source.casefold() not in seen_sources and path not in seen_paths, "Duplicate candidate or source")
        seen_ids.add(ident)
        seen_sources.add(source.casefold())
        seen_paths.add(path)
        _require(row.get("function") in {"S1", "S2", "S3", "S3*", "S4", "S5"}, f"Unknown function for {ident}")
        _require(isinstance(row.get("finding"), str) and len(row["finding"]) >= 40, f"Missing bounded question for {ident}")
        _require(row.get("origin") in ORIGINS, f"Invalid origin for {ident}")
        stage = row.get("stage")
        _require(stage in STAGES, f"Invalid stage for {ident}")
        fit = row.get("fit")
        _require(isinstance(fit, dict) and set(fit) == FIT_KEYS and set(fit.values()) <= FIT_STATES, f"Invalid four gates for {ident}")
        evidence = row.get("evidence")
        _require(isinstance(evidence, list) and all(isinstance(x, str) and x.startswith("https://") for x in evidence), f"Invalid primary-source URLs for {ident}")
        _require(stage not in {"ACTIVE", "AWAITING_EXTERNAL", "CLOSED_CHANGE"} or (set(fit.values()) == {"PASS"} and evidence and row["origin"] != "INSUFFICIENT"), f"Unqualified active/prepared case: {ident}")
        _require(stage not in {"AWAITING_EXTERNAL", "CLOSED_CHANGE", "CLOSED_NO_CHANGE", "BLOCKED_EVIDENCE", "ESCALATED"} or bool(evidence), f"Stage {stage} must have evidence: {ident}")
        _require(stage != "AWAITING_EXTERNAL" or (row.get("handoff_url", "").startswith("https://") and row.get("external_action") == "NOT_EXECUTED"), f"External stage cannot be silently inferred: {ident}")
        _require(stage != "BLOCKED_EVIDENCE" or isinstance(row.get("blocker"), str) and len(row["blocker"]) >= 10, f"Missing evidence blocker: {ident}")
        reviewed_at = row.get("reviewed_at", "")
        _require(isinstance(reviewed_at, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", reviewed_at), f"Missing assessment date: {ident}")
        order.append(reviewed_at)
        if index_root is not None:
            fields = _frontmatter(_git(root, "show", f"{sha}:{path}"))
            _require(fields.get("status") == "included", f"Non-included Index assessment: {ident}")
            _require(fields.get("review_ref") == ref and fields.get("repository", "").casefold() == ("https://github.com/" + source).casefold(), f"Index identity or reviewed ref changed: {ident}")
            _require(fields.get("reviewed_at") == reviewed_at and fields.get("harness_id") == path.rsplit("/", 1)[1][:-3], f"Index assessment metadata mismatch: {ident}")
            _require(fields.get("autonomy_s1") == "A", f"Included S1=A filter violated: {ident}")
    _require(order == sorted(order, reverse=True), "Frozen cohort must use reviewed_at descending")
    return manifest


def summarize(manifest, index_root=None):
    validate(manifest, index_root)
    counts = {stage: sum(x["stage"] == stage for x in manifest["candidates"]) for stage in STAGES}
    eligible = next((x for x in manifest["candidates"] if x["stage"] not in SKIP), None)
    return {
        "batch_id": manifest["batch_id"],
        "index_sha": manifest["index_sha"],
        "local_index_object_checked": index_root is not None,
        "remote_canonical_attested": False,
        "total": len(manifest["candidates"]),
        "stage_counts": counts,
        "next_candidate": eligible["id"] if eligible else None,
        "next_stage": eligible["stage"] if eligible else "NO_ACTIONABLE_CANDIDATE",
        "external_writes_authorized": False,
        "test_mode": "NATIVE_SCRIPT_ONLY_NO_LLM_AGENTS"
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "status", "next"))
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--index-root", type=Path, help="Exact local Index git HEAD; never attests canonical remote")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.manifest.read_text(encoding="utf-8"))
        report = summarize(payload, args.index_root)
    except (BatchError, ValueError, OSError) as exc:
        parser.exit(2, f"BATCH_INVALID: {exc}\n")
    if args.command == "next":
        report = {k: report[k] for k in ("batch_id", "next_candidate", "next_stage", "external_writes_authorized", "test_mode", "local_index_object_checked", "remote_canonical_attested")}
    elif args.command == "validate":
        report = {"valid": True, "batch_id": report["batch_id"], "local_index_object_checked": report["local_index_object_checked"], "remote_canonical_attested": False}
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
