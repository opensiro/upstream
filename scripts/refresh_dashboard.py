#!/usr/bin/env python3
"""Refresh the derived activity dashboard only when source-backed facts change.

This is a one-shot publisher input, not a second mutable event ledger. A failed
GitHub read or partial aggregate never changes tracked dashboard files.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys

from activity import GitHub, check_complete, collect, markdown, svg

SHA = re.compile(r"[a-f0-9]{40}\Z")


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def fingerprint(snapshot, report):
    # Timestamp, attention changes, and Git SHA churn alone do not cause a new
    # dashboard PR. Actual contribution identities/PR links and first-party PR
    # lifecycle facts do.
    links = []
    for fork in snapshot["forks"]:
        for record in fork["contributions"]:
            links.append({"original": fork["original_repository"],
                          "fork": fork["working_fork"], "id": record["id"],
                          "external_prs": sorted(p["url"] for p in record["external_prs"])})
    material = {"links": sorted(links, key=lambda x: (x["fork"], x["id"])),
                "prs": sorted(report["prs"], key=lambda x: x["url"].lower()),
                "forks": sorted(x["working_fork"] for x in snapshot["forks"])}
    return hashlib.sha256(canonical_bytes(material)).hexdigest()


def validate_snapshot(snapshot):
    if snapshot.get("scope") != "public_organization_repositories":
        raise ValueError("refusing to publish a subset as the full Upstream portfolio")
    coverage = snapshot.get("coverage") or {}
    if (not coverage.get("scan_complete") or coverage.get("errors")
            or coverage.get("filtered_by_attention")
            or coverage.get("pr_readback") not in ("NOT_REQUESTED", "COMPLETE")
            or not snapshot.get("forks")):
        raise ValueError("incomplete or filtered fork metadata scan")
    for fork in snapshot["forks"]:
        if not SHA.fullmatch(fork.get("meta_head_sha", "")):
            raise ValueError("missing pinned fork meta SHA")
        if not SHA.fullmatch(fork.get("state_blob_sha", "")):
            raise ValueError("missing pinned state blob SHA")
        for record in fork["contributions"]:
            if not SHA.fullmatch(record.get("record_sha", "")):
                raise ValueError("missing pinned improvement record SHA")


def provenance(snapshot, report, revision, signature, svg_text, md_text):
    if not SHA.fullmatch(revision):
        raise ValueError("invalid upstream checkout SHA")
    sources = []
    for fork in sorted(snapshot["forks"], key=lambda x: x["working_fork"]):
        sources.append({"working_fork": fork["working_fork"],
                        "original_repository": fork["original_repository"],
                        "meta_head_sha": fork["meta_head_sha"],
                        "state_blob_sha": fork["state_blob_sha"],
                        "contribution_records": [
                            {"id": rec["id"], "record_sha": rec["record_sha"]}
                            for rec in sorted(fork["contributions"], key=lambda x: x["id"])]})
    return {"schema_version": 1, "source": "opensiro/upstream read-only portfolio projection",
            "upstream_revision": revision, "aggregate_observed_at": snapshot["generated_at"],
            "external_pr_observed_at": report["observed_at"],
            "semantic_fingerprint": signature,
            "coverage": snapshot["coverage"], "summary": report["summary"],
            "fork_sources": sources,
            "external_pr_readbacks": report["prs"],
            "artifact_sha256": {"docs/activity.svg": hashlib.sha256(svg_text.encode()).hexdigest(),
                                "docs/ACTIVITY.md": hashlib.sha256(md_text.encode()).hexdigest()},
            "interpretation": "Metadata-linked PR activity, not historical completeness or verified deployed benefit"}


def refresh(snapshot, *, svg_path, markdown_path, sources_path, upstream_revision,
            client, observed_at=None, audit_path=None):
    validate_snapshot(snapshot)
    report = collect(client, snapshot, observed_at=observed_at)
    check_complete(report)
    generated_svg, generated_markdown = svg(report), markdown(report)
    signature = fingerprint(snapshot, report)
    receipt = provenance(snapshot, report, upstream_revision, signature,
                         generated_svg, generated_markdown)
    svg_path, markdown_path, sources_path = map(Path, (svg_path, markdown_path, sources_path))
    if audit_path is not None:
        Path(audit_path).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    if sources_path.exists():
        previous = json.loads(sources_path.read_text(encoding="utf-8"))
        if previous.get("semantic_fingerprint") == signature:
            actual = {"docs/activity.svg": svg_path, "docs/ACTIVITY.md": markdown_path}
            for key, path in actual.items():
                if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != previous.get("artifact_sha256", {}).get(key):
                    raise ValueError("existing dashboard artifact differs from its pinned provenance: " + key)
            return False
    # All validation and live GitHub reads must finish before touching the
    # tracked files. The workflow will push nothing on a failed refresh.
    svg_path.write_text(generated_svg, encoding="utf-8")
    markdown_path.write_text(generated_markdown, encoding="utf-8")
    sources_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--svg", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--upstream-revision", required=True)
    parser.add_argument("--audit-output", type=Path)
    args = parser.parse_args(argv)
    snapshot = json.loads(args.input.read_text(encoding="utf-8"))
    try:
        changed = refresh(snapshot, svg_path=args.svg, markdown_path=args.markdown,
                          sources_path=args.sources, upstream_revision=args.upstream_revision,
                          client=GitHub(os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")),
                          audit_path=args.audit_output)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print("Dashboard source facts changed; review PR update needed" if changed
          else "Dashboard facts unchanged; no snapshot-only commit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
