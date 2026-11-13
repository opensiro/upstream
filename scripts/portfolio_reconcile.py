#!/usr/bin/env python3
"""Read-only reconciliation across existing, separately owned external PR cohorts.

Inputs are the reviewed PR watcher, frozen casebook, fork registry, and
source-verified publication receipts. Never changes the watchlist, Organization
fit, source receipts, issues, PRs or external repositories.
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

import harness_status
from urllib.error import HTTPError

import pr_maintenance_watch
import resolved_pr_acceptance
import upstream_status


LABELS = ("merged", "closed_unmerged", "open", "unverifiable")
GROUPS = ("watchlist", "casebook", "registry", "published")
KNOWN_404 = pr_maintenance_watch.KNOWN_404_SOURCE
EXACT_PR = re.compile(r"https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/pull/([1-9][0-9]*)\Z")
ROOT = Path(__file__).resolve().parents[1]
PUBLICATION_READBACKS = ROOT / "data" / "external-pr-publication-readbacks"
SHA = re.compile(r"[0-9a-f]{40}\Z")


def identity(url):
    match = EXACT_PR.fullmatch(url)
    if not match:
        raise ValueError(f"Not an exact GitHub PR URL: {url!r}")
    owner, repo, number = match.groups()
    return f"{owner}/{repo}", int(number)


def newly_published_urls():
    """Discover actual publications from existing owner receipts, no new roster.

    Frozen technical batch manifests alone never establish an external PR.
    Publication receipts must have an exact GitHub PR identity, validated
    source repository and authenticated source/fork readback.  The existing
    Harness Status model validates the two legacy publication ledgers; the
    dated publication-readback files cover later standing-mandate waves.
    """
    view = harness_status.build_view()
    urls = set()
    for row in view["interventions"]:
        if row["kind"] != "assessment_batch" or not row.get("publication_ref"):
            continue
        for url in row["pr_urls"]:
            identity(url)
            urls.add(url)

    for path in sorted(PUBLICATION_READBACKS.glob("????-??-??.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        cases = record.get("cases")
        if (record.get("schema_version") != 1 or record.get("observed_at") != path.stem
                or record.get("authenticated_actor") != "xLagerFeuer"
                or not isinstance(cases, list) or not cases):
            raise ValueError(f"Invalid published PR readback: {path.name}")
        for case in cases:
            url, repo, fork = (case.get("pr_url"), case.get("repository"),
                               case.get("public_fork"))
            if (not isinstance(url, str) or not isinstance(repo, str)
                    or not isinstance(fork, str)
                    or not fork.startswith("opensiro-contributions/")
                    or not SHA.fullmatch(case.get("head_sha") or "")
                    or type(case.get("pr_commits")) is not int
                    or case["pr_commits"] < 1):
                raise ValueError(f"Invalid published PR identity: {path.name}")
            source_repo, _ = identity(url)
            if source_repo.casefold() != repo.casefold():
                raise ValueError(f"Published PR repository mismatch: {url}")
            urls.add(url)
    return urls


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

    # The static 34-target review/alert watchlist is *not* the universe of
    # published contributions.  Admit later exact, source-backed publications
    # to daily read-only portfolio observation without silently widening the
    # hourly alert checkpoint or rewriting its historically stable cohort.
    for url in sorted(newly_published_urls()):
        if url not in urls:
            add(url, "published")

    if not urls or len({target["url"] for target in targets}) != len(targets):
        raise ValueError("Empty or duplicate operational watchlist")
    return [{"url": url, "groups": sorted(groups)} for url, groups in sorted(urls.items())]


def cohort_fingerprint(records):
    """Hash exact PR URL/group membership; outcomes must not affect this key."""
    identities = sorted(({"url": row["url"], "groups": sorted(row["groups"])}
                         for row in records), key=lambda row: row["url"])
    canonical = json.dumps(identities, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


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
        timezone.utc).isoformat(timespec="seconds"),
        "cohort_sha256": cohort_fingerprint(records), "records": records}


def summarize(report, *, group=None):
    if report.get("schema_version") != 1 or not isinstance(report.get("records"), list):
        raise ValueError("Unknown portfolio observation schema")
    records = report["records"]
    if not records or len({r["url"] for r in records}) != len(records):
        raise ValueError("Empty or duplicate portfolio records")
    if "cohort_sha256" in report and report["cohort_sha256"] != cohort_fingerprint(records):
        raise ValueError("Portfolio cohort fingerprint mismatch")
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


def joined_view(report, accepted=None):
    """Present one PR-level projection of verified owner records and live APIs.

    Never convert PR lifecycle state, a published patch, or local regression
    evidence into an accepted outcome.  Only an independently revalidated live
    accepted-source export may populate the accepted outcome column.
    """
    summarize(report)
    expected = cohort()
    if ({row["url"] for row in report["records"]} != {row["url"] for row in expected}
            or report.get("cohort_sha256") != cohort_fingerprint(expected)):
        raise ValueError("Joined portfolio does not match current source cohort")

    # Delayed import avoids a cycle: the verified-outcome source owner itself
    # cross-checks every published intervention with this portfolio cohort.
    import verified_external_outcomes as verified
    candidates, _ = verified.cohort()
    owner_by_pr = {}
    for item in candidates:
        for url in item["pr_urls"]:
            if url in owner_by_pr:
                raise ValueError(f"Duplicate PR-to-intervention provenance: {url}")
            owner_by_pr[url] = item
    if set(owner_by_pr) != {row["url"] for row in expected}:
        raise ValueError("Publication source and PR portfolio coverage differs")

    checked = accepted is not None
    accepted_prs = {}
    if checked:
        if (not isinstance(accepted, dict) or accepted.get("schema_version") != 1
                or accepted.get("source") != "opensiro/upstream"
                or accepted.get("source_sha256") != verified.digest_sources()
                or accepted.get("portfolio_cohort_sha256") != report["cohort_sha256"]
                or accepted.get("organization_metric_claimed") is not False
                or accepted.get("metric_status") not in (
                    "UPSTREAM_ACCEPTED_SOURCE_ONLY", "UNCLAIMED_SEMANTIC_EVIDENCE")
                or not isinstance(accepted.get("accepted"), list)
                or accepted.get("accepted_count") != len(accepted["accepted"])):
            raise ValueError("Joined view needs the current verified Upstream source export")
        # Prevent stale accepted-source artifacts from appearing to be part of
        # the same live run as the PR observation.
        try:
            t_pr = datetime.fromisoformat(report["observed_at"].replace("Z", "+00:00"))
            t_acc = datetime.fromisoformat(accepted["observed_at"].replace("Z", "+00:00"))
            if (t_pr.utcoffset() is None or t_acc.utcoffset() is None
                    or abs((t_pr - t_acc).total_seconds()) > 3600):
                raise ValueError("Accepted export and PR observation are not contemporaneous")
        except (TypeError, KeyError, AttributeError) as exc:
            raise ValueError("Missing accepted-source observation time") from exc
        if bool(accepted["accepted"]) != (accepted["metric_status"] == "UPSTREAM_ACCEPTED_SOURCE_ONLY"):
            raise ValueError("Inconsistent accepted-source metric status")
        for row in accepted["accepted"]:
            if not isinstance(row, dict):
                raise ValueError("Malformed accepted-source row")
            url = row.get("external_pr_url")
            item = owner_by_pr.get(url)
            if (item is None or row.get("intervention_id") != item["id"]
                    or url != item["pr_urls"][-1]
                    or row.get("decision") != "ACCEPTED_MERGED_CHANGE_ONLY"
                    or row.get("acceptance_basis") != "DETERMINISTIC_VERIFIED_MERGE"
                    or row.get("benefit_claim") != "NOT_MEASURED"
                    or not SHA.fullmatch(row.get("merge_commit_sha") or "")
                    or not verified.immutable_native_receipt(row.get("native_receipt"))
                    or url in accepted_prs):
                raise ValueError("Accepted source lacks exact independent intervention evidence")
            accepted_prs[url] = row

    # Link native before/after claims only through an *exact PR URL already
    # present in the owner-controlled functional-effects receipts*. A project
    # name or VSM grade resemblance is insufficient for attribution.
    native_effects = json.loads((ROOT / "data/functional-effects.json").read_text(encoding="utf-8"))
    if native_effects.get("schema_version") != 1 or not isinstance(native_effects.get("cases"), list):
        raise ValueError("Invalid source-owned functional effect ledger")
    effects_by_pr = {}
    for case in native_effects["cases"]:
        receipts = case.get("receipts")
        if (not isinstance(receipts, list) or not all(isinstance(r, str) for r in receipts)
                or not isinstance(case.get("id"), str)
                or case.get("product_benefit") != "NOT_MEASURED"):
            raise ValueError("Invalid source-owned functional effect case")
        for url in receipts:
            if EXACT_PR.fullmatch(url) and url in owner_by_pr:
                effects_by_pr.setdefault(url, []).append({
                    "id": case["id"], "origin": case["origin"],
                    "measurement_level": case["measurement_level"],
                    "product_benefit": case["product_benefit"],
                    "evidence": "data/functional-effects.json"})

    technical = harness_status.build_view()
    linked = {row["url"]: row for row in technical["prs"]}
    interventions = {row["id"]: row for row in technical["interventions"]}
    rows = []
    for row in report["records"]:
        url = row["url"]
        item = owner_by_pr[url]
        receipt = item["source"]
        linked_ints = linked.get(url, {}).get("interventions", [])
        assessments = [interventions[k] for k in linked_ints
                       if k.startswith("assessment:") and k in interventions]
        origins = sorted({case.get("origin") for case in assessments if case.get("origin")})
        effects = effects_by_pr.get(url, [])
        origins = sorted(set(origins) | {effect["origin"] for effect in effects})
        stages = sorted({case["technical_status"] for case in assessments})
        native = (receipt.get("github_native_evidence") if item["kind"] == "improvement"
                  else receipt.get("native_test_receipt") if item["kind"] == "corrective"
                  else None)
        if native is not None and not isinstance(native, str):
            raise ValueError("Unrecognized technical receipt")
        chosen = accepted_prs.get(url)
        if chosen and row["outcome"] != "merged":
            raise ValueError("Accepted merged change contradicts current external PR state")
        rows.append({"url": url, "state": row["outcome"], "groups": row["groups"],
                     "intervention_id": item["id"], "source_kind": item["kind"],
                     "assessment_origin": origins or ["NOT_LINKED"],
                     "technical_stage": stages or ["NOT_LINKED"],
                     "functional_effects": effects,
                     "native_receipt": native,
                     "verified_outcome": ("ACCEPTED_MERGED_CHANGE_ONLY" if chosen
                                          else "NOT_ACCEPTED" if checked else "NOT_LIVE_CHECKED"),
                     "outcome_native_receipt": chosen["native_receipt"] if chosen else None,
                     "product_benefit": "NOT_MEASURED" if chosen else "UNCLAIMED"})
    return {"schema_version": 1, "kind": "derived_upstream_pr_view",
            "observed_at": report["observed_at"], "cohort_sha256": report["cohort_sha256"],
            "accepted_source_observed_at": accepted["observed_at"] if checked else None,
            "accepted_source_status": (accepted["metric_status"] if checked else "NOT_LIVE_CHECKED"),
            "summary": {"unique_prs": len(rows),
                        "watched_prs": sum("watchlist" in r["groups"] for r in rows),
                        "accepted_changes": len(accepted_prs) if checked else None,
                        **{key: sum(r["state"] == key for r in rows) for key in LABELS}},
            "records": rows}


def render_joined(view):
    summary = view["summary"]
    accepted = (str(summary["accepted_changes"]) if summary["accepted_changes"] is not None
                else "not live-checked")
    lines = [f"# Unified Upstream PR view — {view['observed_at']}", "",
        "**Derived read-only projection**, not another source ledger. Each external PR URL appears once;",
        "the assessment, historical source, watchlist and accepted outcome remain different dimensions.",
        "A merged PR is **not** automatically an accepted, measured product benefit.", "",
        f"**Known PRs:** {summary['unique_prs']} · **Hourly watched:** {summary['watched_prs']} · "
        f"**Merged:** {summary['merged']} · **Open:** {summary['open']} · "
        f"**Closed unmerged:** {summary['closed_unmerged']} · **Unavailable:** {summary['unverifiable']} · "
        f"**Accepted source-verified changes:** {accepted} (benefit not measured).", "",
        "| External PR | Live state | Source intervention | Assessment origin | Native evidence | Accepted outcome |",
        "| --- | --- | --- | --- | --- | --- |"]
    for row in view["records"]:
        def safe(value):
            return str(value).replace("|", "\\|").replace("\n", " ")
        origin = ", ".join(row["assessment_origin"])
        evidence = f"[receipt]({row['native_receipt']})" if row["native_receipt"] else "—"
        if row["functional_effects"]:
            effect_link = "https://github.com/opensiro/upstream/blob/main/docs/FUNCTIONAL_EFFECTS.md"
            evidence += f" · [before/after]({effect_link})"
        lines.append(f"| [PR]({row['url']}) | {row['state']} | "
                     f"{safe(row['intervention_id'])} | {safe(origin)} | {evidence} | "
                     f"{row['verified_outcome']} |")
    lines += ["", "**Interpretation:** `NOT_LINKED` means no exact source-owned assessment/technical",
              "link was established; it is not a negative assessment. `NOT_ACCEPTED` means no",
              "accepted-source evidence for this intervention, not a rejected or ineffective fix.",
              "`NOT_LIVE_CHECKED` means no independently revalidated source export was supplied.",
              "The hourly watcher remains a separate explicitly reviewed target set; newly published",
              "source-backed PRs are automatically included in the **daily portfolio observation**",
              "but not automatically admitted to the hourly alert inbox. GitHub PRs and source receipts",
              "remain authoritative; no new grants, score, or product-benefit assertions are made."]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--validate-only", action="store_true", help="Offline input/identity validation")
    mode.add_argument("--report", action="store_true", help="Read-only live exact-PR reconciliation")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output-json", type=Path, help="Write the original PR-lifecycle artifact")
    parser.add_argument("--joined", action="store_true", help="Show a unified, read-only per-PR view")
    parser.add_argument("--accepted-json", type=Path, help="Live accepted-source export from the owning verified-outcome workflow")
    parser.add_argument("--joined-json", type=Path, help="Write the joined view as a noncanonical artifact")
    args = parser.parse_args()
    if (args.joined or args.accepted_json or args.joined_json) and not args.report:
        parser.error("--joined/--accepted-json/--joined-json require --report")
    if (args.accepted_json or args.joined_json) and not args.joined:
        parser.error("--accepted-json/--joined-json require --joined")
    if args.validate_only:
        if args.output_json:
            parser.error("--output-json requires --report")
        targets = cohort()
        print(f"Validated {len(targets)} exact unique PR identities across existing source-backed cohorts")
        return
    # Refuse to probe anonymously for scheduled observations: a real token is
    # necessary for bounded, reliable GitHub API reads; no write route used.
    api = pr_maintenance_watch.Github(os.environ.get("GITHUB_TOKEN", ""))
    report = observe(api)
    # All API reads, identity checks and schema checks must finish before a
    # historical artifact can be emitted; no partial observation is saved.
    summarize(report)
    view = joined_view(report, json.loads(args.accepted_json.read_text(encoding="utf-8"))
                       if args.accepted_json else None) if args.joined else None
    if args.output_json:
        args.output_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                    encoding="utf-8")
    if args.joined_json:
        args.joined_json.write_text(json.dumps(view, indent=2, ensure_ascii=False) + "\n",
                                    encoding="utf-8")
    output = view if args.joined else report
    print(json.dumps(output, indent=2, ensure_ascii=False) if args.format == "json" else
          render_joined(view) if args.joined else render(report))


if __name__ == "__main__":
    main()
