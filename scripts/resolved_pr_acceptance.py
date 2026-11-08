#!/usr/bin/env python3
"""Report resolved external PR acceptance for the reviewed Upstream watchlist.

This is an Upstream-owned lifecycle observation, not the Organization-owned
product-native fit experiment or a claim about VSM autonomy/user benefit.
External GitHub sources are read-only. The optional write is restricted to one
bot-owned summary comment in opensiro/upstream issue #125.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from urllib.error import HTTPError

from pr_maintenance_watch import Github, TARGETS, validate_targets


INBOX_REPO = "opensiro/upstream"
INBOX_NUMBER = 125
MARKER = "<!-- opensiro-resolved-pr-acceptance-v1 -->"
BOT = "github-actions[bot]"
LABELS = ("merged", "closed_unmerged", "open", "unverifiable")


def classify(payload, target):
    """Classify one verified GitHub PR; a closure is not a technical refutation."""
    if payload.get("html_url") != target["url"] or payload.get("number") != target["number"]:
        raise ValueError("External PR identity mismatch")
    state = payload.get("state")
    merged_at = payload.get("merged_at")
    if state not in {"open", "closed"} or (merged_at is not None and
                                             (not isinstance(merged_at, str) or not merged_at)):
        raise ValueError("Unknown external PR lifecycle")
    if merged_at and state != "closed":
        raise ValueError("Contradictory merged/open external PR state")
    if merged_at:
        return "merged"
    return "open" if state == "open" else "closed_unmerged"


def observe(api, targets_path=TARGETS, *, observed_at=None):
    targets = validate_targets(targets_path)["targets"]
    records = []
    for target in targets:
        try:
            source = api.get(f"/repos/{target['repository']}/pulls/{target['number']}")
        except HTTPError as exc:
            # A 404 proves neither rejection nor continuing openness. Preserve
            # the reviewed identity, but keep the outcome out of the denominator.
            if exc.code != 404:
                raise
            records.append({"url": target["url"], "outcome": "unverifiable", "reason": "HTTP_404"})
            continue
        records.append({"url": target["url"], "outcome": classify(source, target)})
    return {"schema_version": 1,
            "cohort": "data/pr-maintenance/targets.json",
            "observed_at": observed_at or datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "records": records}


def summarize(report):
    records = report["records"]
    if report.get("schema_version") != 1 or not isinstance(records, list):
        raise ValueError("Unexpected acceptance report schema")
    urls = [r["url"] for r in records]
    if not urls or len(urls) != len(set(urls)):
        raise ValueError("Missing or duplicate acceptance report identities")
    counts = Counter(r["outcome"] for r in records)
    if set(counts) - set(LABELS):
        raise ValueError("Unknown acceptance report outcome")
    resolved = counts["merged"] + counts["closed_unmerged"]
    return {"merged": counts["merged"], "closed_unmerged": counts["closed_unmerged"],
            "open": counts["open"], "unverifiable": counts["unverifiable"],
            "resolved": resolved, "total": len(records),
            "rate": counts["merged"] / resolved if resolved else None}


def render(report):
    stats = summarize(report)
    rate = "N/A (no resolved PRs)" if stats["rate"] is None else (
        f"{stats['rate']:.1%} ({stats['merged']}/{stats['resolved']})")
    lines = [f"### Resolved Upstream PR Acceptance — {report['observed_at']}", "",
             f"**Acceptance among resolved PRs: {rate}.**", "",
             f"Tracked **{stats['total']}** · merged **{stats['merged']}** · closed without merge "
             f"**{stats['closed_unmerged']}** · still open **{stats['open']}** · "
             f"unverifiable **{stats['unverifiable']}**.", "",
             "Only `MERGED / (MERGED + CLOSED_UNMERGED)` enters the rate. "
             "Open and unavailable PRs are excluded, not counted as failures. "
             "Closed unmerged means *not accepted as this PR*, not necessarily that the idea was refuted.", "",
             "| Outcome | External PRs |", "| --- | --- |"]
    for key, title in (("merged", "Merged"), ("closed_unmerged", "Closed without merge"),
                       ("open", "Pending"), ("unverifiable", "Unverifiable")):
        subset = [f"[#{r['url'].rsplit('/', 1)[1]}]({r['url']})" for r in report["records"]
                  if r["outcome"] == key]
        lines.append(f"| {title} ({len(subset)}) | {', '.join(subset) if subset else '—'} |")
    lines += ["", "Source: [reviewed Upstream watchlist](https://github.com/opensiro/upstream/blob/main/data/pr-maintenance/targets.json). "
              "This is a dated PR-lifecycle snapshot, not a final-cohort success rate, "
              "product-native fit, maintainer endorsement, or a VSM assessment. "
              "For intervention fit see the separately owned "
              "[Organization experiment](https://github.com/opensiro/vsm-oss-organization/tree/main/experiments/upstream-intervention-fit)."]
    return "\n".join(lines)


def fingerprint(report):
    return hashlib.sha256(json.dumps([(r["url"], r["outcome"]) for r in report["records"]],
                                    separators=(",", ":")).encode()).hexdigest()


def update_inbox(api, report):
    """Maintain one bot-owned summary in #125, at most once daily if unchanged."""
    issue = api.get(f"/repos/{INBOX_REPO}/issues/{INBOX_NUMBER}")
    if issue.get("state") != "open":
        raise ValueError("PR-maintenance inbox is not open")
    comments = api.pages(f"/repos/{INBOX_REPO}/issues/{INBOX_NUMBER}/comments?per_page=100")
    matches = [c for c in comments if MARKER in c.get("body", "")
               and c.get("user", {}).get("login") == BOT]
    if len(matches) > 1:
        raise ValueError("Multiple acceptance report comments; manual reconciliation required")
    day = report["observed_at"][:10]
    signature = fingerprint(report)
    metadata = f"<!-- acceptance-state:{signature} observed-day:{day} -->"
    body = f"{MARKER}\n{metadata}\n\n{render(report)}"
    if matches:
        current = matches[0]["body"]
        if f"acceptance-state:{signature} observed-day:{day}" in current:
            return False
        api.request(f"/repos/{INBOX_REPO}/issues/comments/{matches[0]['id']}",
                    method="PATCH", payload={"body": body})
    else:
        api.request(f"/repos/{INBOX_REPO}/issues/{INBOX_NUMBER}/comments",
                    method="POST", payload={"body": body})
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--validate-only", action="store_true")
    group.add_argument("--report", action="store_true", help="Live read-only report")
    group.add_argument("--update-inbox", action="store_true", help="Update only the bot summary in Upstream #125")
    args = parser.parse_args()
    if args.validate_only:
        print(f"Validated {len(validate_targets()['targets'])} acceptance targets")
        return
    api = Github(os.environ.get("GITHUB_TOKEN", ""))
    report = observe(api)
    print(render(report))
    if args.update_inbox:
        print("Upstream #125 acceptance comment updated" if update_inbox(api, report)
              else "Upstream #125 acceptance comment already current")


if __name__ == "__main__":
    main()
