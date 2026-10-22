#!/usr/bin/env python3
"""Read-only upstream PR verification and deterministic portfolio presentation.

The Organization owns experimental fit; external GitHub PRs own lifecycle.
Nothing here changes fit decisions, GitHub issues/PRs, or Control Plane mandates.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import html
import json
import os
from pathlib import Path
import sys
from urllib.parse import urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data/upstream-fit-snapshot.json"
CASES = ROOT / "data/dashboard-cases.json"
LIVE = ROOT / "data/upstream-lifecycle.json"
MARKDOWN = ROOT / "DASHBOARD.md"
HTML = ROOT / "docs/index.html"
CASEBOOK = ROOT / "cases/README.md"
LABELS = {"merged": "Merged", "open": "Open", "closed_unmerged": "Closed unmerged"}
FIT_LABELS = {"pass": "Pass", "pending": "Pending", "fail": "Fail"}


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def snapshot_digest() -> str:
    return hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest()


def sources():
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    ids = [case["id"] for case in snapshot["interventions"]]
    if len(ids) != len(set(ids)) or set(ids) != set(cases):
        raise ValueError("Case metadata must match exactly the pinned intervention IDs")
    if Counter(x["fit"] for x in snapshot["interventions"]) != snapshot["fit_counts"]:
        raise ValueError("Pinned fit counts do not match interventions")
    return snapshot, cases


def pr_api_url(url: str) -> str:
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")
    if (parsed.scheme != "https" or parsed.netloc.lower() != "github.com" or
            len(parts) != 4 or parts[2] != "pull" or not parts[3].isdigit()):
        raise ValueError(f"Not an exact public GitHub PR URL: {url}")
    return f"https://api.github.com/repos/{parts[0]}/{parts[1]}/pulls/{parts[3]}"


def public_pr(url: str):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "opensiro-upstream-status/1"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(pr_api_url(url), headers=headers), timeout=20) as response:
        data = json.load(response)
    if data.get("merged_at"):
        lifecycle = "merged"
    elif data.get("state") == "open":
        lifecycle = "open"
    elif data.get("state") == "closed":
        lifecycle = "closed_unmerged"
    else:
        raise ValueError(f"Unknown GitHub PR state for {url}: {data.get('state')!r}")
    return {"url": url, "lifecycle": lifecycle, "merged_at": data.get("merged_at"),
            "updated_at": data.get("updated_at")}


def collect(fetch=public_pr, *, now=None):
    snapshot, _ = sources()
    records = []
    for intervention in snapshot["interventions"]:
        original_url = intervention["pull_request"]
        landing_url = intervention.get("landing_pull_request")
        original = fetch(original_url)
        landing = fetch(landing_url) if landing_url and landing_url != original_url else None
        # A replacement has its own GitHub outcome but does not create a ninth intervention.
        effective = landing if landing else original
        if landing and original["lifecycle"] == "merged" and landing["lifecycle"] != "merged":
            raise ValueError(f"Contradictory replacement chain for {intervention['id']}")
        records.append({"id": intervention["id"], "lifecycle": effective["lifecycle"],
                        "original_pr": original, "landing_pr": landing})
    return {"schema_version": 1, "observed_at": (now or datetime.now(timezone.utc)).isoformat(timespec="seconds"),
            "fit_snapshot_sha256": snapshot_digest(), "records": records}


def load_verified():
    snapshot, cases = sources()
    observed = json.loads(LIVE.read_text(encoding="utf-8"))
    if observed["fit_snapshot_sha256"] != snapshot_digest():
        raise ValueError("Pinned fit snapshot changed: reverify lifecycle before rendering")
    ids = [x["id"] for x in snapshot["interventions"]]
    if [x["id"] for x in observed["records"]] != ids:
        raise ValueError("Live-status intervention IDs differ from the pinned cohort")
    for record in observed["records"]:
        if record["lifecycle"] not in LABELS:
            raise ValueError(f"Unknown lifecycle: {record['lifecycle']}")
    return snapshot, cases, observed


def stats(snapshot, observed):
    outcomes = Counter(x["lifecycle"] for x in observed["records"])
    fits = Counter(x["fit"] for x in snapshot["interventions"])
    return outcomes, fits


def github_rows(snapshot, cases, observed):
    for intervention, status in zip(snapshot["interventions"], observed["records"]):
        yield intervention, cases[intervention["id"]], status


def render_markdown(snapshot, cases, observed):
    outcomes, fits = stats(snapshot, observed)
    count = len(observed["records"])
    repos = len({x["upstream_repository"] for x in snapshot["interventions"]})
    rate = snapshot["primary_metric"]
    date = observed["observed_at"]
    lines = ["# Upstream contributions — Dashboard", "",
             f"> **External PR states verified:** {date} · **Experimental fit snapshot:** {snapshot['as_of']}.",
             "> Lifecycle is a dated public GitHub observation; fit and attribution belong to the Organization experiment.", "",
             "### Upstream intervention outcomes (observed)", "",
             "| Interventions | Projects | Merged | Open | Closed unmerged |",
             "| :---: | :---: | :---: | :---: | :---: |",
             f"| **{count}** | **{repos}** | **{outcomes['merged']}** | **{outcomes['open']}** | **{outcomes['closed_unmerged']}** |", "",
             "### Product-native fit (separate historical experiment)", "",
             "| Fit rate of completed reviews | Pass | Pending | Fail |",
             "| :---: | :---: | :---: | :---: |",
             f"| **{rate['value']:.0%} ({rate['numerator_pass']}/{rate['denominator_completed_reviews']})** | **{fits['pass']}** | **{fits['pending']}** | **{fits['fail']}** |", "",
             "Four product-native fit gates are assessed in the [Organization-owned experiment](https://github.com/opensiro/vsm-oss-organization/tree/main/experiments/upstream-intervention-fit). This is **not** a PR acceptance rate, VSM grade, or automatically reassessed on a merge.", "",
             "### Evidence-linked interventions", "",
             "| Intervention / case | Original upstream PR | Current outcome | Experimental fit |",
             "| --- | --- | --- | --- |"]
    for item, meta, status in github_rows(snapshot, cases, observed):
        case_link = f"cases/{meta['case']}"
        original = f"[Original PR]({item['pull_request']})"
        if item.get("landing_pull_request"):
            original += f" → [replacement]({item['landing_pull_request']})"
        lines.append(f"| [{meta['project']} — {meta['title']}]({case_link}) | {original} | {LABELS[status['lifecycle']]} | **{FIT_LABELS[item['fit']]}** |")
    lines += ["", "**Attribution:** Henterprise original #1 and merged replacement #3 count as **one intervention**. StarNet maintainer's independent implementation is **not** counted as a contributor PR merge. GitHub PR lifecycle alone does not prove a functional VSM S2 improvement.", "",
              "### Provenance and refresh", "",
              f"- Historical fit snapshot: [Organization ledger](https://github.com/opensiro/vsm-oss-organization/blob/main/experiments/upstream-intervention-fit/snapshot.json), pinned here as [`data/upstream-fit-snapshot.json`](data/upstream-fit-snapshot.json) (`as_of` {snapshot['as_of']}).",
              f"- PR observations: [`data/upstream-lifecycle.json`](data/upstream-lifecycle.json), last verified {date}. They do **not** imply that GitHub statuses are live at viewing time.",
              "- [Public casebook](cases/README.md) provides contextual evidence; [Cognee](projects/cognee/README.md) and [`registry.yaml`](registry.yaml) are tracked separately, outside this eight-intervention cohort.",
              "- Refresh: `python3 scripts/upstream_status.py --refresh` then `--render`; test with `--check-generated` and `--check-live`. External PR checks are read-only; publication is a reviewed PR.", "",
              "_External maintainers retain decision authority; no upstream endorsement is implied._", ""]
    return "\n".join(lines)


def replace_region(text: str, start: str, end: str, payload: str):
    first = text.find(start)
    last = text.find(end, first + len(start))
    if first == -1 or last == -1 or text.find(start, first + 1) != -1:
        raise ValueError(f"HTML generation anchor missing or duplicated: {start}")
    return text[:first + len(start)] + "\n" + payload + "\n" + text[last:]


def html_regions(snapshot, cases, observed):
    outcomes, fits = stats(snapshot, observed)
    total = len(observed["records"])
    rate = snapshot["primary_metric"]
    meta = (f'<span>PR states verified · {html.escape(observed["observed_at"])}</span>'
            f'<span>Fit snapshot · {html.escape(snapshot["as_of"])}</span><span>Dated, not live telemetry</span>')
    metrics = (f'<div class="metric"><div class="kpi-name">Total interventions</div><div class="number">{total}</div><div class="kpi-foot">Distinct contributions, not PR count</div></div>\n'
               f'<div class="metric"><div class="kpi-name">Upstream projects</div><div class="number">{len(set(x["upstream_repository"] for x in snapshot["interventions"]))}</div><div class="kpi-foot">External OSS repositories</div></div>\n'
               f'<div class="metric"><div class="kpi-name">Merged interventions</div><div class="number">{outcomes["merged"]}</div><div class="kpi-foot">Includes credited replacement PR</div></div>\n'
               f'<div class="metric"><div class="kpi-name">Product-native fit</div><div class="number highlight">{rate["value"]:.0%}</div><div class="kpi-foot">{rate["numerator_pass"]} of {rate["denominator_completed_reviews"]} completed reviews</div></div>')
    fit = (f'<div class="ring" style="background:conic-gradient(#3271e9 0deg {360 * rate["value"]:.1f}deg,#e9eff7 {360 * rate["value"]:.1f}deg 360deg)" role="img" aria-label="Fit: {rate["value"]:.0%} of completed reviews"><div class="ring-inner"><strong>{rate["value"]:.0%}</strong><span>fit rate</span></div></div>\n'
           f'<div class="legend"><div class="legend-line"><span class="dot good"></span>Pass<strong>{fits["pass"]}</strong></div><div class="legend-line"><span class="dot warn"></span>Pending<strong>{fits["pending"]}</strong></div><div class="legend-line"><span class="dot bad"></span>Fail<strong>{fits["fail"]}</strong></div><div class="legend-line"><span class="dot"></span>Reviewed<strong>{rate["denominator_completed_reviews"]} / {total}</strong></div></div>')
    outcome_bars = "\n".join(
        f'<div><div class="barlabel"><span>{label}</span><strong>{outcomes[kind]}</strong></div><div class="track"><div class="fill {cls}" style="width:{100 * outcomes[kind] / total:.1f}%"></div></div></div>'
        for kind, label, cls in (("merged", "Merged", "merged"), ("open", "Open", "open"), ("closed_unmerged", "Closed without merge", "closed")))
    rows = []
    for item, case, record in github_rows(snapshot, cases, observed):
        esc = html.escape
        pr = f'<a href="{esc(item["pull_request"], quote=True)}">Original PR ↗</a>'
        if item.get("landing_pull_request"):
            pr += f'<div class="secondary"><a href="{esc(item["landing_pull_request"], quote=True)}">Landing replacement ↗</a></div>'
        status = record["lifecycle"]
        label = LABELS[status]
        css = "closed" if status == "closed_unmerged" else status
        fit = item["fit"]
        search = esc(" ".join((case["project"], case["title"], case["note"])).lower(), quote=True)
        rows.append(f'<tr class="item" data-outcome="{status}" data-fit="{fit}" data-search="{search}"><td><a class="project" href="https://github.com/opensiro/upstream/blob/main/cases/{esc(case["case"], quote=True)}">{esc(case["project"])}</a><div class="intervention">{esc(case["title"])}</div></td><td>{pr}</td><td><span class="pill {css}">{label}</span></td><td><span class="pill fit-{fit}">{FIT_LABELS[fit]}</span></td><td class="note">{esc(case["note"])}</td></tr>')
    source = (f'<p>External PR lifecycle last verified <strong style="display:inline">{esc(observed["observed_at"])}</strong>: <a href="https://github.com/opensiro/upstream/blob/main/data/upstream-lifecycle.json">read-only PR receipts</a>. This is a dated observation, not real-time GitHub telemetry.</p>\n'
              f'<p>Fit is a separate historical <a href="https://github.com/opensiro/vsm-oss-organization/blob/main/experiments/upstream-intervention-fit/snapshot.json">Organization-owned experiment</a> (`as_of` {esc(snapshot["as_of"])}). PR merges cannot update product-native fit automatically. The <a href="https://github.com/opensiro/upstream/blob/main/cases/README.md">casebook</a> holds contextual evidence.</p>')
    return {"meta": meta, "metrics": metrics, "fit": fit, "outcomes": outcome_bars, "rows": "\n".join(rows), "source": source}


def render_html(source: str, snapshot, cases, observed):
    for name, content in html_regions(snapshot, cases, observed).items():
        source = replace_region(source, f"<!-- BEGIN GENERATED:{name} -->", f"<!-- END GENERATED:{name} -->", content)
    return source


def render_casebook(source: str, snapshot, cases, observed):
    lines = []
    for item, meta, record in github_rows(snapshot, cases, observed):
        original = f"[Original PR]({item['pull_request']})"
        if item.get("landing_pull_request"):
            original += f" → [replacement]({item['landing_pull_request']})"
        lines.append(f"| [{meta['project']} — {meta['title']}]({meta['case']}) | {original} | {LABELS[record['lifecycle']]} | **{item['fit']}** |")
    return replace_region(source, "<!-- BEGIN GENERATED:casebook -->", "<!-- END GENERATED:casebook -->", "\n".join(lines))


def expected_outputs():
    snapshot, cases, observed = load_verified()
    return {MARKDOWN: render_markdown(snapshot, cases, observed),
            HTML: render_html(HTML.read_text(encoding="utf-8"), snapshot, cases, observed),
            CASEBOOK: render_casebook(CASEBOOK.read_text(encoding="utf-8"), snapshot, cases, observed)}


def check_live(fetch=public_pr):
    _, _, old = load_verified()
    new = collect(fetch=fetch)
    diff = [(a["id"], a["lifecycle"], b["lifecycle"])
            for a, b in zip(old["records"], new["records"])
            if a["id"] != b["id"] or a["lifecycle"] != b["lifecycle"] or
            a["original_pr"]["lifecycle"] != b["original_pr"]["lifecycle"] or
            (a["landing_pr"] or {}).get("lifecycle") != (b["landing_pr"] or {}).get("lifecycle")]
    if old["fit_snapshot_sha256"] != new["fit_snapshot_sha256"]:
        raise ValueError("Pinned Organization fit snapshot changed: refresh required")
    if diff:
        raise ValueError(f"External PR lifecycle drift (stored, current): {diff}. Run --refresh then --render; open a reviewed PR.")
    return len(new["records"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    for flag in ("refresh", "render", "check-generated", "check-live"):
        group.add_argument(f"--{flag}", action="store_true")
    args = parser.parse_args()
    try:
        if args.refresh:
            # Fetch/validate *all* PRs before changing any saved state.
            result = collect()
            LIVE.write_text(json_text(result), encoding="utf-8")
            print(f"Saved {len(result['records'])} verified interventions to {LIVE.relative_to(ROOT)}")
        elif args.check_live:
            print(f"No external PR lifecycle drift across {check_live()} interventions")
        else:
            outputs = expected_outputs()
            if args.check_generated:
                drift = [str(path.relative_to(ROOT)) for path, content in outputs.items() if path.read_text(encoding="utf-8") != content]
                if drift:
                    raise ValueError(f"Stale generated presentation: {drift}; run --render")
                print("Dashboard, HTML and casebook match pinned PR receipts and fit")
            else:
                for path, content in outputs.items():
                    path.write_text(content, encoding="utf-8")
                print("Refreshed Dashboard, HTML and casebook from pinned inputs")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"upstream-status: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
