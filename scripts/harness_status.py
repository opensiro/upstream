#!/usr/bin/env python3
"""Read-only, evidence-preserving Harness -> Intervention -> PR status view.

Existing batch, publication, casebook and registry records remain authoritative.
The generated Markdown and JSON are projections, never lifecycle write targets.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

from upstream_status import load_verified, registry_prs


ROOT = Path(__file__).resolve().parents[1]
BATCHES = ROOT / "data" / "assessment-candidate-batches"
CORRECTIVE = ROOT / "data" / "corrective-publication" / "2026-10-23-01.json"
IMPROVEMENT = ROOT / "data" / "improvement-publication" / "2026-10-24-01.json"
MONITOR = ROOT / "data" / "pr-maintenance" / "targets.json"
OUTPUT = ROOT / "HARNESS_STATUS.md"
REPO = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9_.-]+\Z")
PR = re.compile(r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/pull/[0-9]+\Z")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def repo_key(source):
    require(isinstance(source, str) and REPO.fullmatch(source), f"Invalid harness repository: {source!r}")
    return source.casefold()


def pr_repo(url):
    match = PR.fullmatch(url) if isinstance(url, str) else None
    require(match is not None, f"Invalid external PR URL: {url!r}")
    return repo_key(match.group(1))


def registry_sources():
    """Read only the existing narrow registry schema; fail closed on identity drift."""
    source = (ROOT / "registry.yaml").read_text(encoding="utf-8")
    entries = {}
    for part in re.split(r"(?m)^  - id: ", source)[1:]:
        ident = part.splitlines()[0].strip()
        matches = re.findall(r"(?m)^    upstream: https://github\.com/([^\s]+)\s*$", part)
        require(len(matches) == 1 and ident not in entries, f"Invalid registry upstream for {ident}")
        entries[ident] = matches[0]
    require(entries, "No registry projects found")
    return entries


def add_pr(prs, url, intervention_id, state, evidence_source, observed_at=None):
    key = pr_repo(url)
    record = prs.setdefault(url, {"url": url, "harness_id": key, "interventions": [], "observations": [], "monitored": False})
    require(record["harness_id"] == key, f"PR source identity changed: {url}")
    if intervention_id not in record["interventions"]:
        record["interventions"].append(intervention_id)
    receipt = {"state": state, "source": evidence_source, "observed_at": observed_at}
    if receipt not in record["observations"]:
        record["observations"].append(receipt)


def build_view():
    harnesses, interventions, prs, batches = {}, {}, {}, []

    def add_intervention(ident, source, kind, *, technical="NOT_TRACKED", external="NOT_TRACKED", **extras):
        key = repo_key(source)
        require(ident not in interventions, f"Intervention ID repeated: {ident}")
        harness = harnesses.setdefault(key, {"id": key, "repository": source, "interventions": []})
        harness["interventions"].append(ident)
        interventions[ident] = {"id": ident, "harness_id": key, "kind": kind,
                                "technical_status": technical, "external_status": external,
                                "pr_urls": [], **extras}
        return interventions[ident]

    manifests = sorted(BATCHES.glob("*.json"))
    require(manifests, "Assessment candidate manifests missing")
    for path in manifests:
        batch = read_json(path)
        require(batch.get("schema_version") in (1, 2) and isinstance(batch.get("candidates"), list), f"Invalid batch: {path}")
        batch_id = batch["batch_id"]
        ids = []
        for candidate in batch["candidates"]:
            ident = "assessment:" + candidate["id"]
            record = add_intervention(ident, candidate["source"], "assessment_batch",
                technical=candidate["stage"], external="NOT_SUBMITTED" if candidate["stage"] == "AWAITING_EXTERNAL" else "NONE",
                vsm_functions=[candidate["function"]], origin=candidate["origin"],
                assessment_path=candidate["assessment_path"], batch_ids=[batch_id],
                evidence=candidate.get("evidence", []), blocker=candidate.get("blocker"),
                handoff_url=candidate.get("handoff_url"),
                source_ref=f"data/assessment-candidate-batches/{path.name}")
            if candidate.get("external_action") == "NOT_EXECUTED":
                require(not record["pr_urls"], f"False external publication: {ident}")
            ids.append(ident)
        batches.append({"id": batch_id, "index_sha": batch["index_sha"],
                        "interventions": ids, "source_ref": f"data/assessment-candidate-batches/{path.name}"})

    for name, path in (("corrective", CORRECTIVE), ("improvement", IMPROVEMENT)):
        ledger = read_json(path)
        require(isinstance(ledger.get("cases"), list), f"Invalid {name} ledger")
        for case in ledger["cases"]:
            ident = "assessment:" + case["id"]
            require(ident in interventions, f"Publication record lacks historical assessment: {ident}")
            row = interventions[ident]
            if case.get("source"):
                require(row["harness_id"] == repo_key(case["source"]), f"Publication source differs: {ident}")
            state = case["publication"]
            if name == "corrective":
                require(state in ("SUBMITTED", "BLOCKED"), f"Unknown Corrective publication: {state}")
                row["external_status"] = "SUBMITTED_UNVERIFIED_LIVE" if state == "SUBMITTED" else "BLOCKED_PUBLICATION"
            else:
                require(state == "MERGED_UPSTREAM" and case.get("pr_merged") is True, f"Unverified Improvement merge: {ident}")
                row["external_status"] = "MERGED_UPSTREAM"
            row["publication_ref"] = f"data/{name}-publication/{path.name}"
            row["publication_observed_at"] = case.get("observed_at") or case.get("merged_readback_date")
            row["publication_blocker"] = case.get("reason")
            url = case.get("pr_url") or case.get("external_pr")
            if url:
                require(pr_repo(url) == row["harness_id"], f"PR repository differs: {ident}")
                row["pr_urls"].append(url)
                add_pr(prs, url, ident, "MERGED" if state == "MERGED_UPSTREAM" else "SUBMITTED",
                       row["publication_ref"], row["publication_observed_at"])
            else:
                require(state == "BLOCKED", f"Submitted case missing external PR: {ident}")

    snapshot, cases, observed = load_verified()
    lifecycle = {row["id"]: row for row in observed["records"]}
    require(len(lifecycle) == len(snapshot["interventions"]), "Casebook lifecycle record missing")
    for case in snapshot["interventions"]:
        ident = "portfolio:" + case["id"]
        live = lifecycle[case["id"]]
        require(case["id"] in cases, f"Casebook metadata missing: {ident}")
        row = add_intervention(ident, case["upstream_repository"], "casebook",
            external=live["lifecycle"].upper(), vsm_functions=[], fit=case["fit"],
            title=cases[case["id"]]["title"],
            source_ref=f"cases/{cases[case['id']]['case']}",
            publication_observed_at=observed["observed_at"])
        for ref in (live["original_pr"], live.get("landing_pr")):
            if ref and ref["url"] not in row["pr_urls"]:
                row["pr_urls"].append(ref["url"])
                add_pr(prs, ref["url"], ident, ref["lifecycle"].upper(),
                       "data/upstream-lifecycle.json", observed["observed_at"])

    upstreams = registry_sources()
    registry_live = {x["id"]: x["pr"] for x in observed["registry_records"]}
    for entry in registry_prs():
        require(entry["id"] in upstreams and entry["id"] in registry_live, f"Registry metadata missing: {entry['id']}")
        ident = "registry:" + entry["id"]
        url = entry["url"]
        require(pr_repo(url) == repo_key(upstreams[entry["id"]]), f"Registry PR source differs: {ident}")
        live = registry_live[entry["id"]]
        require(live["url"] == url, f"Registry PR readback mismatch: {ident}")
        row = add_intervention(ident, upstreams[entry["id"]], "registry",
            external=live["lifecycle"].upper(), vsm_functions=[], source_ref="registry.yaml",
            publication_observed_at=observed["registry_verified_at"])
        row["pr_urls"].append(url)
        add_pr(prs, url, ident, live["lifecycle"].upper(),
               "data/upstream-lifecycle.json", observed["registry_verified_at"])

    watcher = read_json(MONITOR)
    for target in watcher["targets"]:
        url = target["url"]
        key = pr_repo(url)
        require(key == repo_key(target["repository"]), f"Watchlist source mismatch: {url}")
        if url not in prs:
            ident = f"monitor:{key}#{target['number']}"
            row = add_intervention(ident, target["repository"], "monitor_only",
                external="WATCHLIST_ONLY", vsm_functions=[],
                source_ref="data/pr-maintenance/targets.json")
            row["pr_urls"].append(url)
            add_pr(prs, url, ident, "WATCHLIST_ONLY", row["source_ref"])
        prs[url]["monitored"] = True

    for value in prs.values():
        value["interventions"].sort()
        value["observations"].sort(key=lambda x: (x["source"], x["state"]))
    for value in harnesses.values():
        value["interventions"].sort()
    return {"schema_version": 1,
            "sources": {"batch_manifests": len(manifests), "casebook_observed_at": observed["observed_at"],
                        "registry_observed_at": observed["registry_verified_at"], "watchlist_targets": len(watcher["targets"])},
            "harnesses": [harnesses[k] for k in sorted(harnesses)],
            "interventions": [interventions[k] for k in sorted(interventions)],
            "prs": [prs[k] for k in sorted(prs)], "batches": batches}


def next_action(row):
    stage, external = row["technical_status"], row["external_status"]
    if external in ("MERGED_UPSTREAM", "MERGED"):
        return "Accepted externally; no new delivery claim"
    if external == "UNVERIFIABLE":
        return "Recheck exact external PR identity"
    if external in ("OPEN", "SUBMITTED_UNVERIFIED_LIVE"):
        return "Check current maintainer/CI outcome"
    if external == "BLOCKED_PUBLICATION":
        return "Resolve documented publication gate"
    if stage == "AWAITING_EXTERNAL":
        return "Refresh source; check external publication grant"
    if stage == "BLOCKED_EVIDENCE":
        return "Obtain missing native evidence"
    if stage == "CLOSED_NO_CHANGE":
        return "No code change justified"
    if external == "WATCHLIST_ONLY":
        return "Read PR maintenance inbox; no technical inference"
    if external == "CLOSED_UNMERGED":
        return "Recorded external no-merge outcome"
    return "Inspect owner evidence; no assumed next write"


def filter_view(view, selection):
    if selection == "all":
        return view
    def matches(row):
        technical, external = row["technical_status"], row["external_status"]
        if selection == "awaiting-external":
            return technical == "AWAITING_EXTERNAL" and external == "NOT_SUBMITTED"
        if selection == "blocked":
            return technical == "BLOCKED_EVIDENCE" or external == "BLOCKED_PUBLICATION"
        if selection == "merged":
            return external in ("MERGED", "MERGED_UPSTREAM")
        if selection == "actionable":
            return (matches_for_action(technical, external))
        raise ValueError(f"Unknown filter: {selection}")

    chosen = {row["id"] for row in view["interventions"] if matches(row)}
    result = dict(view)
    result["interventions"] = [row for row in view["interventions"] if row["id"] in chosen]
    result["harnesses"] = [{**h, "interventions": [i for i in h["interventions"] if i in chosen]}
                           for h in view["harnesses"] if any(i in chosen for i in h["interventions"])]
    result["prs"] = [{**p, "interventions": [i for i in p["interventions"] if i in chosen]}
                     for p in view["prs"] if any(i in chosen for i in p["interventions"])]
    result["batches"] = [{**b, "interventions": [i for i in b["interventions"] if i in chosen]}
                         for b in view["batches"] if any(i in chosen for i in b["interventions"])]
    result["filter"] = selection
    return result


def matches_for_action(technical, external):
    if external in ("MERGED", "MERGED_UPSTREAM", "CLOSED_UNMERGED"):
        return False
    return (technical in ("AWAITING_EXTERNAL", "ACTIVE", "SCREENING", "BLOCKED_EVIDENCE", "ESCALATED")
            or external in ("OPEN", "UNVERIFIABLE", "SUBMITTED_UNVERIFIED_LIVE", "BLOCKED_PUBLICATION", "WATCHLIST_ONLY"))


def render_markdown(view):
    interventions = {x["id"]: x for x in view["interventions"]}
    source = view["sources"]
    lines = ["# Upstream — harness intervention status", "",
        "> **Generated read-only view**, not a new ledger or a live GitHub verification.",
        f"> Source snapshots: casebook **{source['casebook_observed_at']}**, registry **{source['registry_observed_at']}**; batch manifests preserve their own frozen dates.",
        "", "A harness may have several independent interventions and PRs. A historical `AWAITING_EXTERNAL` batch state **remains historical** even when a separate publication ledger later confirms an upstream merge. All external submission/acceptance claims below come from the linked owning source; `SUBMITTED_UNVERIFIED_LIVE` means **no current PR-state claim**.", "",
        f"**Scope:** {len(view['harnesses'])} harnesses · {len(view['interventions'])} interventions · {len(view['prs'])} unique external PR URLs · {len(view['batches'])} assessment batches · {source['watchlist_targets']} monitored PR targets.",
        "", "## Harness overview", "",
        "| Harness | Interventions | Technical handoffs | External submissions (recorded) | Confirmed merges | Evidence blocks |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for harness in view["harnesses"]:
        rows = [interventions[k] for k in harness["interventions"]]
        handoffs = sum(r["technical_status"] == "AWAITING_EXTERNAL" for r in rows)
        submitted = sum(r["external_status"] in ("SUBMITTED_UNVERIFIED_LIVE", "OPEN", "MERGED", "MERGED_UPSTREAM") for r in rows)
        merged = sum(r["external_status"] in ("MERGED_UPSTREAM", "MERGED") for r in rows)
        blocked = sum(r["technical_status"] == "BLOCKED_EVIDENCE" or r["external_status"] == "BLOCKED_PUBLICATION" for r in rows)
        lines.append(f"| [{harness['repository']}](https://github.com/{harness['repository']}) | {len(rows)} | {handoffs} | {submitted} | {merged} | {blocked} |")
    lines += ["", "## Interventions (one row per independent change)", "",
        "| Harness | Intervention ID | VSM | Technical | External | PRs | Batch / owner | Next action |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for harness in view["harnesses"]:
        for ident in harness["interventions"]:
            row = interventions[ident]
            links = ", ".join(f"[#{url.rsplit('/', 1)[1]}]({url})" for url in row["pr_urls"]) or "—"
            src = row["source_ref"]
            owner = ", ".join(row.get("batch_ids", [])) or row["kind"]
            lines.append(f"| {harness['repository']} | [{ident}]({src}) | {', '.join(row['vsm_functions']) or '—'} | {row['technical_status']} | {row['external_status']} | {links} | {owner} | {next_action(row)} |")
    lines += ["", "## Provenance and usage", "",
        "- **Harness:** normalized GitHub `owner/repo`; grouping only, never an overall `FIXED` claim.",
        "- **Intervention:** stable ID; assessment cases keep their original ID and batch membership. Distinct portfolio, registry and monitor-only records are deliberately namespaced; no VSM function is inferred for them.",
        "- **PR:** one external GitHub URL can link several interventions, while each intervention can link multiple PRs (including an original and maintainer replacement). PR monitoring is not a new intervention if a matching source PR already exists.",
        "- **Batch:** a planning/evidence freeze; its historical stage never mutates to fake an external merge. Corrective/Improvement publication ledgers and the dated casebook/registry lifecycle snapshot are separate overlays.",
        "- **Live freshness:** the existing [PR maintenance watcher](docs/PR_MAINTENANCE.md) follows a bounded 18-target snapshot. This view does not expand that mandate, fetch new external state or grant publication/merge rights.",
        "", "Regenerate: `python3 scripts/harness_status.py --write`; verify: `python3 scripts/harness_status.py --check`; inspect machine-readable projection: `python3 scripts/harness_status.py --json`. Filter on demand with `--filter actionable|awaiting-external|blocked|merged` (never rewrites this full view).", ""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    option = parser.add_mutually_exclusive_group()
    option.add_argument("--write", action="store_true", help="Regenerate derived Markdown; never edit source ledgers")
    option.add_argument("--check", action="store_true", help="Fail if committed Markdown projection is stale")
    option.add_argument("--json", action="store_true", help="Print normalized read-only model")
    parser.add_argument("--filter", choices=("all", "actionable", "awaiting-external", "blocked", "merged"), default="all")
    args = parser.parse_args(argv)
    try:
        view = build_view()
        require(not (args.write or args.check) or args.filter == "all", "Cannot write/check a filtered projection")
        view = filter_view(view, args.filter)
        if args.json:
            print(json.dumps(view, indent=2, ensure_ascii=False, sort_keys=True))
        else:
            content = render_markdown(view)
            if args.write:
                OUTPUT.write_text(content, encoding="utf-8")
                print(f"Wrote {OUTPUT}")
            elif args.check:
                require(OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == content,
                        "HARNESS_STATUS.md differs from its owning inputs")
                print("HARNESS_STATUS_CURRENT")
            else:
                sys.stdout.write(content)
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        parser.exit(2, f"HARNESS_STATUS_BLOCKED: {exc}\n")


if __name__ == "__main__":
    main()
