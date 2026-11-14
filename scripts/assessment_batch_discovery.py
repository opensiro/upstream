#!/usr/bin/env python3
"""Read-only, Index-first discovery; never reserves or admits work.

Prospective upgrade intake defaults to VSM-wide schema v2. Historical v1
S1=A/S2=C selection is available only for backward-compatible reproduction.
Issue #144. Local Index must match its exact commit. Canonical Upstream main
manifests, visible open PR manifests and the main registry are read from GitHub
and checked for drift. Visibility errors fail closed.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote, urlsplit

from assessment_candidate_batches import BatchError, _frontmatter, _git
from assessment_batch_conflict_preflight import (
    REPO, INDEX_REPO, FILE_PATTERN, NAME_PATTERN, GithubReader,
    _attest_canonical_index, _branch_sha, _open_snapshot, _manifest_rows,
    decode_blob, normalize,
)

HEX40 = re.compile(r"[0-9a-f]{40}\Z")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
REGISTRY = "data/contribution-workspaces/registry.json"

# Optional human-curated first-party leads alter selection priority, not
# truth of the lead, native fit, or the candidate's assessment-derived origin.
LEAD_KINDS = {"ISSUE": "issues", "PR": "pull", "DISCUSSION": "discussions"}


def read_priority_evidence(path):
    """Validate a read-only lead list; never fetch or treat it as verified."""
    if path is None:
        return []
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise BatchError(f"BLOCKED_PRIORITY_EVIDENCE: unreadable JSON: {exc}") from exc
    if not isinstance(data, dict) or set(data) != {"schema_version", "leads"} or data["schema_version"] != 1:
        raise BatchError("BLOCKED_PRIORITY_EVIDENCE: expected schema_version 1 and leads")
    leads = data["leads"]
    if not isinstance(leads, list) or not leads or len(leads) > 100:
        raise BatchError("BLOCKED_PRIORITY_EVIDENCE: require 1–100 source-first leads")
    seen = set()
    for lead in leads:
        if not isinstance(lead, dict) or set(lead) != {"source", "kind", "url", "rationale"}:
            raise BatchError("BLOCKED_PRIORITY_EVIDENCE: each lead needs source/kind/url/rationale")
        source, kind, url, rationale = (lead[k] for k in ("source", "kind", "url", "rationale"))
        if not isinstance(source, str) or not NAME_PATTERN.fullmatch(source) or normalize(source) in seen:
            raise BatchError("BLOCKED_PRIORITY_EVIDENCE: invalid or duplicate source")
        seen.add(normalize(source))
        if kind not in LEAD_KINDS or not isinstance(url, str):
            raise BatchError("BLOCKED_PRIORITY_EVIDENCE: unsupported first-party lead")
        parsed = urlsplit(url)
        parts = parsed.path.strip("/").split("/")
        if (parsed.scheme != "https" or parsed.netloc != "github.com"
                or parsed.query or parsed.fragment or parsed.username or parsed.password
                or len(parts) != 4 or normalize("/".join(parts[:2])) != normalize(source)
                or parts[2] != LEAD_KINDS[kind] or not re.fullmatch(r"[0-9]{1,12}", parts[3])
                or int(parts[3]) < 1):
            raise BatchError("BLOCKED_PRIORITY_EVIDENCE: URL must be a source-owned GitHub issue/PR/discussion")
        if not isinstance(rationale, str) or len(rationale.strip()) < 20 or len(rationale) > 1000:
            raise BatchError("BLOCKED_PRIORITY_EVIDENCE: provide a specific short rationale")
    return leads


def remote_inventory(reader, index_sha):
    """One stable read window, not an atomic reservation or merge grant."""
    index_main = _attest_canonical_index(index_sha, reader)
    main = _branch_sha(reader, REPO)
    commit = reader.get(f"/repos/{REPO}/git/commits/{main}")
    tree_sha = commit.get("tree", {}).get("sha") if isinstance(commit, dict) else None
    if not isinstance(tree_sha, str) or not HEX40.fullmatch(tree_sha):
        raise BatchError("BLOCKED_GITHUB_VISIBILITY: no canonical Upstream tree")
    tree = reader.get(f"/repos/{REPO}/git/trees/{tree_sha}?recursive=1")
    if not isinstance(tree, dict) or tree.get("truncated") is not False or not isinstance(tree.get("tree"), list):
        raise BatchError("BLOCKED_GITHUB_VISIBILITY: truncated main tree")
    seen = set()
    merged = 0
    paths = set()
    for record in tree["tree"]:
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            raise BatchError("BLOCKED_GITHUB_VISIBILITY: malformed tree record")
        path = record["path"]
        if not FILE_PATTERN.fullmatch(path):
            continue
        sha = record.get("sha")
        if path in paths or record.get("type") != "blob" or not isinstance(sha, str) or not HEX40.fullmatch(sha):
            raise BatchError("BLOCKED_GITHUB_VISIBILITY: malformed/duplicated batch manifest entry")
        paths.add(path)
        payload = decode_blob(reader.get(f"/repos/{REPO}/git/blobs/{sha}"))
        seen.update(source for source, _, _ in _manifest_rows(payload, f"main@{main}:{path}"))
        merged += 1

    registry = decode_blob(reader.get(f"/repos/{REPO}/contents/{REGISTRY}?ref={main}"))
    sources = registry.get("sources") if isinstance(registry, dict) else None
    if not isinstance(sources, list):
        raise BatchError("BLOCKED_GITHUB_VISIBILITY: missing canonical source registry")
    for item in sources:
        if not isinstance(item, dict):
            raise BatchError("BLOCKED_GITHUB_VISIBILITY: malformed registry source")
        seen.add(normalize(item.get("source")))

    prs = _open_snapshot(reader)
    active_manifests = 0
    for number, pr in sorted(prs.items()):
        files = reader.pages(f"/repos/{REPO}/pulls/{number}/files")
        changed = set()
        for record in files:
            if not isinstance(record, dict) or not isinstance(record.get("filename"), str):
                raise BatchError("BLOCKED_GITHUB_VISIBILITY: incomplete open PR file list")
            path = record["filename"]
            if FILE_PATTERN.fullmatch(path) and record.get("status") != "removed":
                changed.add(path)
        if not changed:
            continue
        head = pr["head"]
        owner = head.get("repo", {}).get("full_name") if isinstance(head.get("repo"), dict) else None
        if not isinstance(owner, str) or not NAME_PATTERN.fullmatch(owner):
            raise BatchError("BLOCKED_GITHUB_VISIBILITY: inaccessible open PR head")
        for path in sorted(changed):
            payload = decode_blob(reader.get(
                f"/repos/{owner}/contents/{quote(path, safe='/')}?ref={head['sha']}"))
            seen.update(source for source, _, _ in _manifest_rows(payload, f"PR#{number}:{path}"))
            active_manifests += 1

    # Read again after all GitHub requests; still not a cross-ref atomic snapshot.
    final_prs = _open_snapshot(reader)
    if (_branch_sha(reader, REPO) != main
            or _branch_sha(reader, INDEX_REPO) != index_main
            or {number: pr["head"]["sha"] for number, pr in prs.items()} !=
               {number: pr["head"]["sha"] for number, pr in final_prs.items()}):
        raise BatchError("BLOCKED_GITHUB_VISIBILITY: repository changed during scan")
    return {"reserved": seen, "main_sha": main, "index_main_sha": index_main,
            "main_manifest_count": merged, "registry_source_count": len(sources),
            "open_pr_count": len(prs), "active_pr_manifest_count": active_manifests}


def index_candidates(index_root, index_sha, *, schema_version=2):
    if schema_version not in (1, 2):
        raise BatchError("Unsupported discovery schema version")
    root = Path(index_root)
    if not HEX40.fullmatch(index_sha) or _git(root, "rev-parse", "HEAD") != index_sha:
        raise BatchError("BLOCKED_INDEX_PROVENANCE: local Index HEAD does not match pinned SHA")
    dirty = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--", "assessments"],
                           capture_output=True, text=True, check=False)
    if dirty.returncode or dirty.stdout:
        raise BatchError("BLOCKED_INDEX_PROVENANCE: Index assessment checkout is dirty")
    files = subprocess.run(["git", "-C", str(root), "ls-tree", "-r", "--name-only",
                            index_sha, "assessments"], capture_output=True, text=True, check=False)
    if files.returncode:
        raise BatchError("BLOCKED_INDEX_PROVENANCE: cannot enumerate exact Index tree")
    rows = []
    identities = set()
    for path in files.stdout.splitlines():
        if not re.fullmatch(r"assessments/[a-z0-9-]+/[a-z0-9-]+\.md", path):
            continue
        contents = (root / path).read_text(encoding="utf-8")
        meta = _frontmatter(contents)
        if meta.get("status") != "included":
            continue
        # Historical v1 intake was restricted to A/C. Prospective v2 may
        # propose any included Index assessment, regardless of S1/S2 grade.
        if schema_version == 1 and (meta.get("autonomy_s1"), meta.get("autonomy_s2")) != ("A", "C"):
            continue
        url = meta.get("repository", "")
        if not url.startswith("https://github.com/"):
            raise BatchError("BLOCKED_INDEX_PROVENANCE: invalid included repository URL")
        source = url.removeprefix("https://github.com/").strip("/")
        if not NAME_PATTERN.fullmatch(source):
            raise BatchError("BLOCKED_INDEX_PROVENANCE: invalid included source identity")
        reviewed = meta.get("reviewed_at", "")
        ref = meta.get("review_ref", "")
        if not DATE.fullmatch(reviewed) or not HEX40.fullmatch(ref):
            raise BatchError("BLOCKED_INDEX_PROVENANCE: included assessment missing reviewed date/ref")
        if meta.get("harness_id") != Path(path).stem:
            raise BatchError("BLOCKED_INDEX_PROVENANCE: included assessment ID/path mismatch")
        identity = normalize(source)
        if identity in identities:
            raise BatchError("BLOCKED_INDEX_PROVENANCE: duplicate included source or case alias")
        identities.add(identity)
        row = {"source": source, "assessment_path": path,
               "review_ref": ref, "reviewed_at": reviewed}
        # Discovery does not prove a functional gap. The specific S1–S5
        # function must be chosen from the pinned assessment and preregistered
        # before inspecting target source. Never silently assign S2 in v2.
        if schema_version == 1:
            row["function"] = "S2"
        rows.append(row)
    rows.sort(key=lambda x: (-int(x["reviewed_at"].replace("-", "")),
                             x["source"].casefold(), x["assessment_path"]))
    return rows


def discover(index_root, index_sha, reader, count=5, *, schema_version=2, priority_evidence=None):
    if not 5 <= count <= 10:
        raise BatchError("Discovery requires a complete 5–10-row cohort")
    # Local Index check before remote scan; remote GitHub separately attests
    # Index ancestry and stable canonical main visibility.
    rows = index_candidates(index_root, index_sha, schema_version=schema_version)
    leads = read_priority_evidence(priority_evidence)
    if leads and schema_version != 2:
        raise BatchError("BLOCKED_PRIORITY_EVIDENCE: lead-first selection is v2 only")
    live = remote_inventory(reader, index_sha)
    eligible = [row for row in rows if normalize(row["source"]) not in live["reserved"]]
    candidates = {normalize(row["source"]): row for row in eligible}
    ranked = []
    for lead in leads:
        key = normalize(lead["source"])
        if key not in candidates:
            raise BatchError("BLOCKED_PRIORITY_EVIDENCE: lead absent from unreserved included Index")
        ranked.append({**candidates.pop(key),
                       "selection_origin_hint": "SOURCE_FIRST",
                       "lead_kind": lead["kind"], "lead_url": lead["url"],
                       "lead_rationale": lead["rationale"],
                       "strict_derived_origin_eligible": False,
                       "lead_verified": False})
    # The remaining Index-first candidates retain their historical recency
    # order, without fictional lead signals or a manufactured benefit score.
    ranked.extend(row for row in eligible if normalize(row["source"]) in candidates)
    selected = ranked[:count]
    status = "PROPOSED_ONLY" if len(selected) == count else "NO_ELIGIBLE_ASSESSMENT_CANDIDATE"
    return {"status": status, "schema_version": schema_version,
            "function_assignment_required": schema_version == 2,
            "selection_policy": ("first_party_leads_then_index_recency" if leads
                                 else "index_recency"),
            "unverified_priority_lead_count": len(leads),
            "index_sha": index_sha,
            "index_main_sha": live["index_main_sha"], "upstream_main_sha": live["main_sha"],
            "required_count": count, "selected": selected if len(selected) == count else [],
            "eligible_count": len(eligible), "included_filter_count": len(rows),
            "excluded_unique_source_count": len(live["reserved"]),
            "main_manifest_count": live["main_manifest_count"],
            "registry_source_count": live["registry_source_count"],
            "open_pr_count": live["open_pr_count"],
            "active_pr_manifest_count": live["active_pr_manifest_count"],
            "remote_visibility_checked": True, "admission_attested": False,
            "external_writes_authorized": False,
            "limitation": ("Read-only selection, not atomic; lead URLs/rationales have NOT "
                           "been independently verified. Source-first leads cannot count as "
                           "strict assessment-derived discoveries. Independently inspect "
                           "the source and native fit; v2 functions require pinned Index "
                           "justification; rerun admission gate before work/merge"
                           if schema_version == 2 else
                           "Read-only legacy v1 selection, not atomic; rerun admission "
                           "gate before work/merge")}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index-root", type=Path, required=True)
    parser.add_argument("--index-sha", required=True)
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--schema-version", type=int, choices=(1, 2), default=2,
                        help="2: VSM-wide prospective upgrade intake (default); "
                             "1: reproduce historical S1=A/S2=C selection")
    parser.add_argument("--priority-evidence", type=Path,
                        help="Optional JSON with source-owned issue/PR/discussion leads; "
                             "ordered source-first priority, NOT strict derived-origin proof")
    args = parser.parse_args(argv)
    try:
        report = discover(args.index_root, args.index_sha,
                          GithubReader(os.environ.get("GITHUB_TOKEN")), args.count,
                          schema_version=args.schema_version,
                          priority_evidence=args.priority_evidence)
    except (BatchError, OSError, UnicodeError, ValueError) as exc:
        parser.exit(2, f"DISCOVERY_BLOCKED: {exc}\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PROPOSED_ONLY" else 2


if __name__ == "__main__":
    sys.exit(main())
