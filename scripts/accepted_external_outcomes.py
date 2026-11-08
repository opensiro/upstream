#!/usr/bin/env python3
"""Fail-closed owner-reviewed outcomes ledger; never infer acceptance from merge.

An empty ledger intentionally means no Organization-claimable value. A nonempty
ledger must be checked against a fresh, complete observer report and an exact
GitHub APPROVED review before its entries are eligible for owner-side export.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import json
import os
from pathlib import Path
import re

import portfolio_reconcile
import pr_maintenance_watch
import verified_external_outcomes as observer


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data/verified-external-outcomes/accepted-v1.json"
REVIEW_URL = re.compile(
    r"https://github\.com/opensiro/upstream/pull/([1-9][0-9]*)"
    r"#pullrequestreview-([1-9][0-9]*)\Z"
)
SHA = re.compile(r"[0-9a-f]{40}\Z")
LOGIN = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?\Z")
ENTRY_KEYS = frozenset({"intervention_id", "source_pr_urls", "effective_pr_url",
                        "merge_commit_sha", "merged_at", "native_receipt",
                        "reviewer_login", "review_url", "decision", "benefit_claim"})


def load_ledger(path=LEDGER):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if (not isinstance(data, dict) or set(data) != {"schema_version", "scope", "accepted"}
            or type(data["schema_version"]) is not int or data["schema_version"] != 1
            or data["scope"] != "opensiro/upstream"
            or not isinstance(data["accepted"], list)):
        raise ValueError("Unknown accepted outcome ledger schema/scope")
    cohort, _ = observer.cohort()
    source = {item["id"]: item for item in cohort}
    ids, urls, reviews = set(), set(), set()
    for row in data["accepted"]:
        if not isinstance(row, dict) or set(row) != ENTRY_KEYS:
            raise ValueError("Incomplete or unknown accepted outcome entry")
        identity = row["intervention_id"]
        if not isinstance(identity, str) or identity not in source or identity in ids:
            raise ValueError("Unknown or duplicate accepted intervention ID")
        ids.add(identity)
        expected = source[identity]["pr_urls"]
        if row["source_pr_urls"] != expected or row["effective_pr_url"] != expected[-1]:
            raise ValueError("Accepted PR identity/replacement chain mismatch")
        if row["effective_pr_url"] in urls:
            raise ValueError("Duplicate effective external PR")
        urls.add(row["effective_pr_url"])
        if not isinstance(row["merge_commit_sha"], str) or not SHA.fullmatch(row["merge_commit_sha"]):
            raise ValueError("Unpinned merge commit")
        if not isinstance(row["merged_at"], str) or not re.fullmatch(
                r"20[0-9]{2}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z",
                row["merged_at"]):
            raise ValueError("Unpinned merge timestamp")
        if not isinstance(row["native_receipt"], str) or not observer.immutable_native_receipt(
                row["native_receipt"]):
            raise ValueError("Native evidence must use immutable first-party receipt")
        if row["decision"] != "ACCEPTED_MERGED_CHANGE_ONLY" or row["benefit_claim"] != "NOT_MEASURED":
            raise ValueError("Unreviewed decision or deployed-benefit claim")
        login = row["reviewer_login"]
        if not isinstance(login, str) or not LOGIN.fullmatch(login):
            raise ValueError("Missing identifiable reviewer")
        review = row["review_url"]
        if not isinstance(review, str) or not REVIEW_URL.fullmatch(review) or review in reviews:
            raise ValueError("Missing, duplicate or non-native Upstream approval reference")
        reviews.add(review)
        # A reviewer approval is required; the contributor's own approval is
        # insufficient evidence of a separately controlled acceptance decision.
        actor = source[identity].get("actor") or source[identity]["source"].get("actor")
        if actor and login.lower() == actor.lower():
            raise ValueError("Contributor cannot self-accept an external outcome")
    return data


def validate_observation(report):
    """Do not trust partial, stale, duplicate or edited candidate artifacts."""
    cohort, excluded = observer.cohort()
    if (not isinstance(report, dict) or report.get("schema_version") != 1
            or report.get("metric_status") != "CANDIDATE_ONLY_NOT_ORGANIZATION_CLAIMED"
            or report.get("source_sha256") != observer.digest_sources()
            or report.get("portfolio_cohort_sha256") != portfolio_reconcile.cohort_fingerprint(
                portfolio_reconcile.cohort())
            or report.get("source_exclusions") != {"corrective_not_published": excluded}
            or not isinstance(report.get("records"), list)
            or len(report["records"]) != len(cohort)):
        raise ValueError("Incomplete, stale or incompatible candidate observation")
    if not isinstance(report.get("observed_at"), str):
        raise ValueError("Missing first-party observation time")
    try:
        if datetime.fromisoformat(report["observed_at"]).utcoffset() is None:
            raise ValueError("Observation time must be timezone-aware")
    except (ValueError, TypeError) as exc:
        raise ValueError("Invalid observation timestamp") from exc
    expected = {item["id"]: item for item in cohort}
    seen = set()
    counts = Counter()
    for row in report["records"]:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            raise ValueError("Malformed candidate record")
        identity = row["id"]
        if identity in seen or identity not in expected:
            raise ValueError("Duplicate or unknown candidate record")
        seen.add(identity)
        if (row.get("pr_urls") != expected[identity]["pr_urls"]
                or row.get("kind") != expected[identity]["kind"]
                or row.get("status") not in observer.STATES
                or not isinstance(row.get("reason_codes"), list)):
            raise ValueError("Candidate identity, status or reason mismatch")
        counts[row["status"]] += 1
    if report.get("counts") != {key: counts[key] for key in observer.STATES}:
        raise ValueError("Candidate status totals mismatch")
    return {row["id"]: row for row in report["records"]}


def verify_accepted(ledger, report, api):
    """Only exact machine-verified rows with genuine GitHub review are eligible.

    Semantic overrides (Corrective/casebook/registry PENDING_REVIEW) intentionally
    require a separately reviewed extension; v1 must not silently promote them.
    """
    candidates = validate_observation(report)
    if ledger["accepted"] and api is None:
        raise ValueError("Live GitHub approval revalidation required for accepted records")
    result = []
    source = {item["id"]: item for item in observer.cohort()[0]}
    for row in ledger["accepted"]:
        entry = candidates[row["intervention_id"]]
        if (entry["status"] != "VERIFIED" or entry["reason_codes"]
                or entry.get("pr_states", [])[-1:] != ["merged"]
                or entry.get("merged_at") != row["merged_at"]
                or entry.get("merge_commit_sha") != row["merge_commit_sha"]
                or entry.get("native_receipt") != row["native_receipt"]):
            raise ValueError("Accepted entry lacks exact machine-verified live evidence")
        # The observer artifact alone is not a proof: re-check first-party PR,
        # landed source delta and native CI against the current GitHub API.
        fresh = observer.evaluate(api, source[row["intervention_id"]])
        if (fresh["status"] != "VERIFIED" or fresh["reason_codes"]
                or any(fresh.get(key) != entry.get(key) for key in (
                    "pr_urls", "pr_states", "merged_at", "merge_commit_sha", "native_receipt"))):
            raise ValueError("Accepted entry differs from current first-party GitHub evidence")
        match = REVIEW_URL.fullmatch(row["review_url"])
        review = api.get(f"/repos/opensiro/upstream/pulls/{match.group(1)}/reviews/{match.group(2)}")
        if (review.get("html_url") != row["review_url"]
                or review.get("state") != "APPROVED"
                or (review.get("user") or {}).get("login", "").lower()
                != row["reviewer_login"].lower()
                or not review.get("submitted_at")
                or not SHA.fullmatch(review.get("commit_id") or "")):
            raise ValueError("GitHub first-party owner review not verified")
        # An APPROVED review of an unrelated PR cannot authorize this outcome.
        # The reviewed, merged Upstream PR must identify the exact intervention,
        # native receipt and merge SHA in the reviewed decision's PR body.
        number = match.group(1)
        reviewed_pr = api.get(f"/repos/opensiro/upstream/pulls/{number}")
        markers = {
            f"Outcome-Acceptance: {row['intervention_id']}",
            f"Outcome-Merge: {row['merge_commit_sha']}",
            f"Outcome-Native-Receipt: {row['native_receipt']}",
        }
        if (reviewed_pr.get("html_url") != f"https://github.com/opensiro/upstream/pull/{number}"
                or reviewed_pr.get("state") != "closed" or not reviewed_pr.get("merged_at")
                or reviewed_pr.get("head", {}).get("sha") != review["commit_id"]
                or reviewed_pr.get("base", {}).get("repo", {}).get("full_name") != "opensiro/upstream"
                or not isinstance(reviewed_pr.get("body"), str)
                or not markers.issubset(set(reviewed_pr["body"].splitlines()))):
            raise ValueError("Approval PR does not attest this exact accepted intervention")
        result.append({"intervention_id": row["intervention_id"],
                       "external_pr_url": row["effective_pr_url"],
                       "merge_commit_sha": row["merge_commit_sha"],
                       "native_receipt": row["native_receipt"],
                       "acceptance_review": row["review_url"],
                       "benefit_claim": "NOT_MEASURED"})
    return {"schema_version": 1, "source": "opensiro/upstream",
            "metric_status": "UPSTREAM_REVIEWED_SOURCE_ONLY" if result
                             else "UNCLAIMED_SEMANTIC_EVIDENCE",
            "observed_at": report["observed_at"],
            "source_sha256": report["source_sha256"],
            "portfolio_cohort_sha256": report["portfolio_cohort_sha256"],
            "accepted_count": len(result), "accepted": result,
            "organization_metric_claimed": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--validate-only", action="store_true")
    mode.add_argument("--observation-json", type=Path)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()
    ledger = load_ledger()
    if args.validate_only:
        if args.output_json:
            parser.error("--output-json requires --observation-json")
        print(f"Validated accepted-v1 schema and {len(ledger['accepted'])} proposed owner "
              "decisions; no KPI or live evidence inferred")
        return
    report = json.loads(args.observation_json.read_text(encoding="utf-8"))
    api = (pr_maintenance_watch.Github(os.environ.get("GITHUB_TOKEN", ""))
           if ledger["accepted"] else None)
    result = verify_accepted(ledger, report, api)
    if args.output_json:
        args.output_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
