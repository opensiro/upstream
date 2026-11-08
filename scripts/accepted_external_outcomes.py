#!/usr/bin/env python3
"""Fail-closed owner-decision outcomes ledger; never infer acceptance from merge.

An empty ledger intentionally means no Organization-claimable value. A nonempty
ledger must be checked against a fresh, complete observer report and an exact,
attributable Upstream owner decision before entries are eligible for export.
Independent S3* review is not part of this ordinary S1 acceptance loop.
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
DECISION_PR_URL = re.compile(r"https://github\.com/opensiro/upstream/pull/([1-9][0-9]*)\Z")
SHA = re.compile(r"[0-9a-f]{40}\Z")
# Current Upstream-local decision owner, not a new Organization S5 delegation.
# Changes to this list require an attributable source-owned authority decision.
DECISION_OWNERS = frozenset({"xLagerFeuer"})
ENTRY_KEYS = frozenset({"intervention_id", "source_pr_urls", "effective_pr_url",
                        "merge_commit_sha", "merged_at", "native_receipt",
                        "decision_actor", "decision_pr_url", "decision", "benefit_claim"})


def load_ledger(path=LEDGER):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if (not isinstance(data, dict) or set(data) != {"schema_version", "scope", "accepted"}
            or type(data["schema_version"]) is not int or data["schema_version"] != 1
            or data["scope"] != "opensiro/upstream"
            or not isinstance(data["accepted"], list)):
        raise ValueError("Unknown accepted outcome ledger schema/scope")
    cohort, _ = observer.cohort()
    source = {item["id"]: item for item in cohort}
    ids, urls, decisions = set(), set(), set()
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
        actor = row["decision_actor"]
        if not isinstance(actor, str) or actor not in DECISION_OWNERS:
            raise ValueError("No authorized Upstream decision owner")
        decision_url = row["decision_pr_url"]
        if (not isinstance(decision_url, str) or not DECISION_PR_URL.fullmatch(decision_url)
                or decision_url in decisions):
            raise ValueError("Missing, duplicate or non-native Upstream decision PR")
        decisions.add(decision_url)
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
    """Only exact machine-verified rows with owner-attributed decisions are eligible.

    Semantic overrides (Corrective/casebook/registry PENDING_REVIEW) intentionally
    require a separately scoped source-owned extension, not an S3* review.
    """
    candidates = validate_observation(report)
    if ledger["accepted"] and api is None:
        raise ValueError("Live GitHub owner-decision revalidation required for accepted records")
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
        # Owner action is an S1 decision, not an S3* audit. A merged Upstream PR
        # by the named owner, with exact evidence markers, is the attributable
        # decision record; an APPROVED review by a second person is optional.
        number = DECISION_PR_URL.fullmatch(row["decision_pr_url"]).group(1)
        decided_pr = api.get(f"/repos/opensiro/upstream/pulls/{number}")
        markers = {
            f"Outcome-Acceptance: {row['intervention_id']}",
            f"Outcome-Merge: {row['merge_commit_sha']}",
            f"Outcome-Native-Receipt: {row['native_receipt']}",
        }
        if (decided_pr.get("html_url") != row["decision_pr_url"]
                or decided_pr.get("state") != "closed" or not decided_pr.get("merged_at")
                or (decided_pr.get("user") or {}).get("login") != row["decision_actor"]
                or (decided_pr.get("merged_by") or {}).get("login") != row["decision_actor"]
                or decided_pr.get("base", {}).get("repo", {}).get("full_name") != "opensiro/upstream"
                or not isinstance(decided_pr.get("body"), str)
                or not markers.issubset(set(decided_pr["body"].splitlines()))):
            raise ValueError("Owner decision PR does not attest this exact accepted intervention")
        result.append({"intervention_id": row["intervention_id"],
                       "external_pr_url": row["effective_pr_url"],
                       "merge_commit_sha": row["merge_commit_sha"],
                       "native_receipt": row["native_receipt"],
                       "owner_decision": row["decision_pr_url"],
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
