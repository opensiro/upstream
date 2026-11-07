#!/usr/bin/env python3
"""Read-only, evidence-gated candidates for verified external outcomes.

This is an Upstream-owned *observation*, not the Organization metric collector.
It never treats a merged PR as proof of deployed benefit, changes a publication
ledger, or resolves ambiguous replacement/independent-implementation cases.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
from urllib.error import HTTPError

import portfolio_reconcile
import pr_maintenance_watch
import upstream_status


ROOT = Path(__file__).resolve().parents[1]
CORRECTIVE = ROOT / "data/corrective-publication/2026-10-23-01.json"
IMPROVEMENT = ROOT / "data/improvement-publication/2026-10-24-01.json"
SOURCE_FILES = (CORRECTIVE, IMPROVEMENT, upstream_status.SNAPSHOT, upstream_status.REGISTRY)
STATES = ("VERIFIED", "PENDING_REVIEW", "INSUFFICIENT_EVIDENCE", "UNVERIFIABLE")
SHA = re.compile(r"[0-9a-f]{40}\Z")
RUN_URL = re.compile(r"https://github\.com/opensiro/upstream/actions/runs/([1-9][0-9]*)\Z")
PR_URL = re.compile(r"https://github\.com/opensiro/upstream/pull/([1-9][0-9]*)\Z")


def digest_sources():
    h = hashlib.sha256()
    for path in SOURCE_FILES:
        h.update(str(path.relative_to(ROOT)).encode("utf-8") + b"\0")
        h.update(path.read_bytes() + b"\0")
    return h.hexdigest()


def cohort():
    """One intervention per source record, including replacement chains once.

    Cross-check against the existing exact PR-URL portfolio so an omitted
    source, changed registry or duplicate semantic identity fails closed.
    """
    corrective = json.loads(CORRECTIVE.read_text(encoding="utf-8"))
    improvement = json.loads(IMPROVEMENT.read_text(encoding="utf-8"))
    if (corrective.get("schema_version") != 1 or improvement.get("schema_version") != 1
            or not isinstance(corrective.get("cases"), list)
            or not isinstance(improvement.get("cases"), list)):
        raise ValueError("Unknown publication ledger schema")
    items = []
    blocked = 0
    if len(corrective["cases"]) != corrective.get("authorized_count") or len(
            improvement["cases"]) != improvement.get("authorized_count"):
        raise ValueError("Publication cases no longer match authorized finite cohort")
    all_corrective_ids = [case.get("id") for case in corrective["cases"]]
    if not all(all_corrective_ids) or len(all_corrective_ids) != len(set(all_corrective_ids)):
        raise ValueError("Duplicate or absent Corrective case ID")
    for case in corrective["cases"]:
        status = case.get("publication")
        if status == "BLOCKED":
            if case.get("pr_url"):
                raise ValueError("Blocked corrective case has an external PR")
            blocked += 1
            continue
        if status != "SUBMITTED":
            raise ValueError(f"Unreviewed Corrective publication state: {status!r}")
        items.append({"id": f"corrective:{case['id']}", "kind": "corrective",
                      "pr_urls": [case["pr_url"]], "source": case})
    for case in improvement["cases"]:
        if case.get("publication") != "MERGED_UPSTREAM":
            raise ValueError("Unreviewed Improvement publication state")
        items.append({"id": f"improvement:{case['id']}", "kind": "improvement",
                      "pr_urls": [case["external_pr"]], "source": case,
                      "actor": improvement["authenticated_actor"]})
    historical, _ = upstream_status.sources()
    for case in historical["interventions"]:
        urls = [case["pull_request"]]
        if case.get("landing_pull_request"):
            urls.append(case["landing_pull_request"])
        items.append({"id": f"casebook:{case['id']}", "kind": "casebook",
                      "pr_urls": urls, "source": case})
    for case in upstream_status.registry_prs():
        items.append({"id": f"registry:{case['id']}", "kind": "registry",
                      "pr_urls": [case["url"]], "source": case})

    ids = [item["id"] for item in items]
    urls = [url for item in items for url in item["pr_urls"]]
    canonical_urls = [portfolio_reconcile.identity(url) for url in urls]
    if (len(ids) != len(set(ids)) or len(urls) != len(set(urls))
            or len({(repo.lower(), number) for repo, number in canonical_urls}) != len(urls)):
        raise ValueError("Duplicate intervention identity or PR URL across owner ledgers")
    for url in urls:
        portfolio_reconcile.identity(url)
    portfolio_urls = {item["url"] for item in portfolio_reconcile.cohort()}
    if set(urls) != portfolio_urls:
        raise ValueError("Outcome cohort differs from reviewed portfolio PR identities")
    return sorted(items, key=lambda item: item["id"]), blocked


def checked_pr(api, url):
    repo, number = portfolio_reconcile.identity(url)
    try:
        pr = api.get(f"/repos/{repo}/pulls/{number}")
    except HTTPError as exc:
        if exc.code == 404 and url == portfolio_reconcile.KNOWN_404:
            return None
        raise
    if pr.get("html_url") != url or pr.get("number") != number:
        raise ValueError(f"External PR identity mismatch: {url}")
    if (pr.get("base", {}).get("repo", {}).get("full_name", "").lower() != repo.lower()
            or pr.get("state") not in {"open", "closed"}):
        raise ValueError(f"Contradictory source PR identity/state: {url}")
    if pr.get("merged_at") and (pr["state"] != "closed" or not SHA.fullmatch(
            pr.get("merge_commit_sha") or "")):
        raise ValueError(f"Malformed external merge evidence: {url}")
    return pr


def public_state(pr):
    if pr is None:
        return "unverifiable"
    if pr.get("merged_at"):
        return "merged"
    return "open" if pr["state"] == "open" else "closed_unmerged"


def immutable_native_receipt(url):
    """Only a pinned commit path or an exact run is evidence-addressable."""
    return bool(RUN_URL.fullmatch(url or "") or re.fullmatch(
        r"https://github\.com/opensiro/upstream/blob/[0-9a-f]{40}/[^?#]+", url or ""))


def evaluate_improvement(api, item, pr):
    """Strong automatic case: reviewed local CI + exact externally merged diff."""
    data = item["source"]
    reasons = []
    actor = item["actor"]
    if pr.get("user", {}).get("login", "").lower() != actor.lower():
        reasons.append("CONTRIBUTOR_ACTOR_MISMATCH")
    if pr.get("head", {}).get("repo", {}).get("full_name", "").lower() != data["public_fork"].lower():
        reasons.append("FORK_IDENTITY_MISMATCH")
    if pr.get("head", {}).get("sha") != data["merged_pr_head_sha"]:
        reasons.append("MERGED_HEAD_DRIFT")
    published_head, landed_head = data["external_pr_head_sha"], data["merged_pr_head_sha"]
    if not SHA.fullmatch(published_head) or not SHA.fullmatch(landed_head):
        reasons.append("SOURCE_HEAD_NOT_PINNED")
    elif published_head != landed_head:
        # The tested patch might have changed between original publication
        # and landing. A complete first-party compare must prove only CI
        # plumbing changed; unreviewed product-code drift cannot inherit tests.
        fork = data["public_fork"]
        comparison = api.get(f"/repos/{fork}/compare/{published_head}...{landed_head}")
        files = comparison.get("files")
        if not (comparison.get("status") == "ahead"
                and comparison.get("base_commit", {}).get("sha") == published_head
                and comparison.get("merge_base_commit", {}).get("sha") == published_head
                and isinstance(files, list) and 0 < len(files) < 100
                and comparison.get("total_commits") == len(comparison.get("commits") or [])
                and all(f.get("status") == "modified"
                        and f.get("filename", "").startswith(".github/workflows/")
                        for f in files)):
            reasons.append("UNVERIFIED_POST_PUBLICATION_SOURCE_DELTA")
    if pr.get("merged_at") != data["merged_at"] or pr.get("merge_commit_sha") != data["merge_commit_sha"]:
        reasons.append("MERGE_RECEIPT_DRIFT")
    merger = (pr.get("merged_by") or {}).get("login")
    if not merger or merger.lower() == actor.lower() or merger != data["merged_by"]:
        reasons.append("FIRST_PARTY_DISPOSITION_NOT_ATTESTED")
    if data.get("pr_merged") is not True or data.get("product_user_benefit") != "NOT_MEASURED":
        reasons.append("IMPROVEMENT_LEDGER_SEMANTICS_CHANGED")

    run_match = RUN_URL.fullmatch(data.get("github_native_evidence", ""))
    draft_match = PR_URL.fullmatch(data.get("internal_draft", ""))
    if not run_match or not draft_match or not data.get("native_ci", "").startswith("SUCCESS"):
        reasons.append("NATIVE_EVIDENCE_NOT_PINNED")
    else:
        run = api.get(f"/repos/opensiro/upstream/actions/runs/{run_match.group(1)}")
        prs = run.get("pull_requests") or []
        if not (run.get("html_url") == data["github_native_evidence"]
                and run.get("repository", {}).get("full_name") == "opensiro/upstream"
                and run.get("status") == "completed" and run.get("conclusion") == "success"
                and SHA.fullmatch(run.get("head_sha") or "")
                and any(p.get("number") == int(draft_match.group(1))
                        and p.get("head", {}).get("sha") == run["head_sha"] for p in prs)):
            reasons.append("NATIVE_CI_RUN_NOT_LINKED_TO_INTERNAL_PR")
    return ("VERIFIED" if not reasons else "PENDING_REVIEW"), reasons


def evaluate(api, item):
    prs = [checked_pr(api, url) for url in item["pr_urls"]]
    states = [public_state(pr) for pr in prs]
    if len(prs) > 1 and states[0] == "merged" and states[-1] != "merged":
        raise ValueError("Contradictory original/replacement external disposition")
    effective = prs[-1]  # a replacement remains a single intervention
    state = states[-1]
    record = {"id": item["id"], "kind": item["kind"],
              "pr_urls": item["pr_urls"], "pr_states": states,
              "source_ledger": {"corrective": str(CORRECTIVE.relative_to(ROOT)),
                                "improvement": str(IMPROVEMENT.relative_to(ROOT)),
                                "casebook": str(upstream_status.SNAPSHOT.relative_to(ROOT)),
                                "registry": str(upstream_status.REGISTRY.relative_to(ROOT))}[item["kind"]],
              "merged_at": effective.get("merged_at") if effective else None,
              "merge_commit_sha": effective.get("merge_commit_sha") if effective else None}
    if "unverifiable" in states:
        # Even a separately merged replacement cannot establish the identity
        # of an inaccessible original without another reviewed provenance link.
        status, reasons = "UNVERIFIABLE", ["GITHUB_SOURCE_UNAVAILABLE"]
    elif item["kind"] == "improvement" and state == "merged":
        status, reasons = evaluate_improvement(api, item, effective)
    elif state == "merged":
        if item["kind"] == "corrective":
            src = item["source"]
            reasons = []
            if effective.get("user", {}).get("login", "").lower() != src["actor"].lower():
                reasons.append("CONTRIBUTOR_ACTOR_MISMATCH")
            if effective.get("head", {}).get("sha") != src["head_sha"]:
                reasons.append("MERGED_HEAD_NOT_PINNED")
            if not immutable_native_receipt(src.get("native_test_receipt")):
                reasons.append("MUTABLE_OR_MISSING_NATIVE_RECEIPT")
            # A submitted-only ledger cannot self-attest semantic completion.
            reasons.append("PUBLICATION_LEDGER_NOT_YET_REVIEWED_AS_COMPLETED")
        else:
            reasons = ["HISTORICAL_OR_REGISTRY_ATTRIBUTION_REQUIRES_REVIEW"]
        status = "PENDING_REVIEW"
    elif state == "closed_unmerged":
        status, reasons = "PENDING_REVIEW", ["CLOSED_UNMERGED_REQUIRES_SEMANTIC_ATTRIBUTION"]
    else:
        status, reasons = "INSUFFICIENT_EVIDENCE", ["EXTERNAL_PR_NOT_MERGED"]
    record.update({"status": status, "reason_codes": reasons})
    if item["kind"] == "improvement":
        record["native_receipt"] = item["source"]["github_native_evidence"]
        source = item["source"]
        if source["external_pr_head_sha"] != source["merged_pr_head_sha"]:
            record["source_delta_url"] = (f"https://github.com/{source['public_fork']}/compare/"
                                          f"{source['external_pr_head_sha']}...{source['merged_pr_head_sha']}")
    elif item["kind"] == "corrective":
        record["native_receipt"] = item["source"].get("native_test_receipt")
    return record


def observe(api, *, observed_at=None):
    items, blocked = cohort()
    records = [evaluate(api, item) for item in items]
    counts = Counter(item["status"] for item in records)
    return {"schema_version": 1,
            "observed_at": observed_at or datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "source_sha256": digest_sources(),
            "portfolio_cohort_sha256": portfolio_reconcile.cohort_fingerprint(
                portfolio_reconcile.cohort()),
            "source_exclusions": {"corrective_not_published": blocked},
            "counts": {state: counts[state] for state in STATES},
            "metric_status": "CANDIDATE_ONLY_NOT_ORGANIZATION_CLAIMED",
            "records": records}


def render(report):
    lines = [f"# Verified external outcome candidates — {report['observed_at']}", "",
             "**Read-only evidence screening; NOT the Organization's claimed metric.** "
             "A first-party merge plus attributable contribution and pinned native evidence "
             "may verify an external outcome, **not** deployed product benefit.", "",
             "| Verified evidence candidates | Pending semantic review | Insufficient evidence | Unverifiable |",
             "| ---: | ---: | ---: | ---: |",
             "| " + " | ".join(str(report["counts"][key]) for key in STATES) + " |", "",
             "| Intervention | GitHub PR | Status | Reason / pinned evidence |",
             "| --- | --- | --- | --- |"]
    for row in report["records"]:
        reasons = ", ".join(row["reason_codes"]) or "Source-linked merger and native CI validated"
        link = row["pr_urls"][-1]
        lines.append(f"| `{row['id']}` | [PR]({link}) | {row['status']} | {reasons} |")
    lines += ["", f"Not published Corrective cases excluded: {report['source_exclusions']['corrective_not_published']}.",
              "Original and replacement PR URLs are one intervention. No deployment, "
              "native benefit, acceptance motive, or Organization KPI is inferred; "
              "the source and cohort fingerprints accompany the JSON artifact."]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--validate-only", action="store_true")
    mode.add_argument("--report", action="store_true")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()
    if args.validate_only:
        if args.output_json:
            parser.error("--output-json requires --report")
        items, blocked = cohort()
        print(f"Validated {len(items)} interventions, {sum(len(x['pr_urls']) for x in items)} "
              f"PR URLs, {blocked} blocked Corrective cases excluded")
        return
    report = observe(pr_maintenance_watch.Github(os.environ.get("GITHUB_TOKEN", "")))
    if args.output_json:
        args.output_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                    encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False) if args.format == "json" else render(report))


if __name__ == "__main__":
    main()
