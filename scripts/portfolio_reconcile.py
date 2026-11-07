#!/usr/bin/env python3
"""Read-only reconciliation across existing, separately owned external PR cohorts.

Inputs are the explicitly reviewed 18-PR watcher, the pinned casebook experiment,
and the OpenSiro-owned fork registry. Never changes the watchlist, Organization
fit, source receipts, issues, PRs or external repositories.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
import re
from urllib.error import HTTPError

import pr_maintenance_watch
import resolved_pr_acceptance
import upstream_status


LABELS = ("merged", "closed_unmerged", "open", "unverifiable")
GROUPS = ("watchlist", "casebook", "registry")
KNOWN_404 = pr_maintenance_watch.KNOWN_404_SOURCE
EXACT_PR = re.compile(r"https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/pull/([1-9][0-9]*)\Z")


def identity(url):
    match = EXACT_PR.fullmatch(url)
    if not match:
        raise ValueError(f"Not an exact GitHub PR URL: {url!r}")
    owner, repo, number = match.groups()
    return f"{owner}/{repo}", int(number)


def cohort():
    """Deduplicate exact PR URLs without merging their semantic cohort owners."""
    urls = {}

    def add(url, group):
        identity(url)
        urls.setdefault(url, set()).add(group)

    targets = pr_maintenance_watch.validate_targets()["targets"]
    for target in targets:
        add(target["url"], "watchlist")

    snapshot, _ = upstream_status.sources()
    intervention_ids = set()
    for case in snapshot["interventions"]:
        case_id = case["id"]
        if case_id in intervention_ids:
            raise ValueError("Duplicate casebook intervention identity")
        intervention_ids.add(case_id)
        add(case["pull_request"], "casebook")
        replacement = case.get("landing_pull_request")
        if replacement:
            if replacement == case["pull_request"]:
                raise ValueError("Casebook replacement is original PR")
            add(replacement, "casebook")

    projects = upstream_status.registry_prs()
    for project in projects:
        add(project["url"], "registry")

    if not urls or len({target["url"] for target in targets}) != len(targets):
        raise ValueError("Empty or duplicate operational watchlist")
    return [{"url": url, "groups": sorted(groups)} for url, groups in sorted(urls.items())]


def final_closed_event(api, repository, number):
    events = api.pages(f"/repos/{repository}/issues/{number}/events?per_page=100")
    if not isinstance(events, list):
        raise ValueError("Unexpected GitHub issue events")
    terminal = [e for e in events if e.get("event") == "closed"]
    if not terminal:
        # The state is verified; closing *actor* is not. Never invent it.
        return {"actor": None, "closed_event_at": None, "evidence": "NO_CLOSED_EVENT"}
    if any(not isinstance(e.get("created_at"), str) or not e["created_at"] for e in terminal):
        raise ValueError("Malformed GitHub closure event timestamp")
    last = max(terminal, key=lambda e: e["created_at"])
    actor = last.get("actor") or {}
    login = actor.get("login")
    if login is not None and (not isinstance(login, str) or not login):
        raise ValueError("Malformed GitHub closure actor")
    return {"actor": login, "closed_event_at": last["created_at"],
            "evidence": "GITHUB_CLOSED_EVENT" if login else "ACTOR_UNAVAILABLE"}


def observe(api, targets=None, *, observed_at=None):
    records = []
    for target in targets if targets is not None else cohort():
        url = target["url"]
        repo, number = identity(url)
        try:
            source = api.get(f"/repos/{repo}/pulls/{number}")
        except HTTPError as exc:
            if exc.code != 404 or url != KNOWN_404:
                raise
            records.append({"url": url, "groups": target["groups"],
                            "outcome": "unverifiable", "reason": "VERIFIED_KNOWN_404"})
            continue
        outcome = resolved_pr_acceptance.classify(
            source, {"url": url, "number": number})
        row = {"url": url, "groups": target["groups"], "outcome": outcome}
        if outcome == "closed_unmerged":
            row["closure"] = final_closed_event(api, repo, number)
        records.append(row)
    return {"schema_version": 1, "observed_at": observed_at or datetime.now(
        timezone.utc).isoformat(timespec="seconds"), "records": records}


def summarize(report, *, group=None):
    if report.get("schema_version") != 1 or not isinstance(report.get("records"), list):
        raise ValueError("Unknown portfolio observation schema")
    records = report["records"]
    if not records or len({r["url"] for r in records}) != len(records):
        raise ValueError("Empty or duplicate portfolio records")
    selected = []
    for row in records:
        identity(row["url"])
        if (not isinstance(row.get("groups"), list) or not row["groups"]
                or len(row["groups"]) != len(set(row["groups"]))
                or set(row["groups"]) - set(GROUPS)):
            raise ValueError("Unknown portfolio group")
        if row.get("outcome") not in LABELS:
            raise ValueError("Unknown portfolio outcome")
        if group is None or group in row["groups"]:
            selected.append(row)
    counts = Counter(row["outcome"] for row in selected)
    resolved = counts["merged"] + counts["closed_unmerged"]
    return {**{label: counts[label] for label in LABELS}, "total": len(selected),
            "resolved": resolved, "rate": counts["merged"] / resolved if resolved else None}


def render(report):
    overall = summarize(report)
    watcher = summarize(report, group="watchlist")

    def rate(s):
        return f"{s['rate']:.1%} ({s['merged']}/{s['resolved']})" if s["rate"] is not None else "N/A"

    lines = [f"# External PR portfolio reconciliation — {report['observed_at']}", "",
             "Live read-only **GitHub PR URL** observation. The watchlist, historical casebook and "
             "OpenSiro-owned fork registry are distinct source cohorts; exact repeated PR URLs are deduplicated.", "",
             "| Cohort | Unique PR URLs | Merged | Closed without merge | Open | Unverifiable | Resolved-only PR merge rate |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
             f"| Reviewed watchlist | {watcher['total']} | {watcher['merged']} | "
             f"{watcher['closed_unmerged']} | {watcher['open']} | {watcher['unverifiable']} | {rate(watcher)} |",
             f"| Deduplicated broad union | {overall['total']} | {overall['merged']} | "
             f"{overall['closed_unmerged']} | {overall['open']} | {overall['unverifiable']} | {rate(overall)} |",
             "",
             "The operational acceptance cohort remains the explicit watchlist; the broader union is **not** "
             "its new denominator. Pending and unavailable PRs are excluded from both resolved-only rates.",
             "Closing actor is derived from the last applicable GitHub issue closure event; it is not "
             "evidence of **why** the PR closed, product-native benefit or an Organization fit decision.",
             "",
             "## Closed without merge — attribution", "",
             "| PR | Closing actor | Final event | Evidence |",
             "| --- | --- | --- | --- |"]
    closed = [r for r in report["records"] if r["outcome"] == "closed_unmerged"]
    for row in closed:
        event = row["closure"]
        lines.append(f"| [PR]({row['url']}) | {event['actor'] or 'Unknown'} | "
                     f"{event['closed_event_at'] or 'Unverified'} | {event['evidence']} |")
    if not closed:
        lines.append("| — | — | — | — |")
    lines += ["", "Source boundaries: [watchlist](https://github.com/opensiro/upstream/blob/main/data/pr-maintenance/targets.json), "
              "[casebook](https://github.com/opensiro/upstream/blob/main/data/upstream-fit-snapshot.json), "
              "[fork registry](https://github.com/opensiro/upstream/blob/main/registry.yaml). "
              "Henterprise original/replacement PRs are **two URLs for one intervention**; an "
              "independently implemented idea is **not** a contributor merge. "
              "For reviewed impact and closure interpretation see the dated casebook and Organization experiment.",
              "", "No third-party writes, fit changes, status-ledger changes, PR comments or archival actions were performed."]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--validate-only", action="store_true", help="Offline input/identity validation")
    mode.add_argument("--report", action="store_true", help="Read-only live exact-PR reconciliation")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args()
    if args.validate_only:
        targets = cohort()
        print(f"Validated {len(targets)} exact unique PR identities across three existing source cohorts")
        return
    # Refuse to probe anonymously for scheduled observations: a real token is
    # necessary for bounded, reliable GitHub API reads; no write route used.
    api = pr_maintenance_watch.Github(os.environ.get("GITHUB_TOKEN", ""))
    report = observe(api)
    print(json.dumps(report, indent=2, ensure_ascii=False) if args.format == "json" else render(report))


if __name__ == "__main__":
    main()
