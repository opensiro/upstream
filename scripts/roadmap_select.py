#!/usr/bin/env python3
"""Rank source-backed *leads* for new OpenSiro roadmaps, not proven upgrades.

Index RANKINGS+catalog pin is authoritative for admission and historical VSM context.
A bounded second pass checks original GitHub activity, SPDX license, issue titles
and the exact matching fork. Selection never creates issues, forks, or records. Its source/issue-title leads
must trigger parallel current-work versus independent on-top research, not an
automatic NO_GO from original overlap or a C construction proposal from grades.
"""
import argparse
import base64
from datetime import date, datetime, timezone
from http.client import IncompleteRead, HTTPException
import csv
import io
import json
import os
import re
from pathlib import Path
from urllib.parse import quote

from aggregate import APIError, GitHub, api
from roadmap_view import read_text

INDEX = "opensiro/vsm-harness-index"
FORK_ORG = "opensiro-contributions"
SHA = re.compile(r"^[0-9a-f]{40}$")
LINK = re.compile(r"^\| [0-9]+ \| <a id=\"([^\"]+)\"></a>\[(.*?)\]\((assessments/[^)]+)\) \(\[source\]\((https://github.com/([^/)]+/[^/)]+))\)\) \| ")
PERMISSIVE = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "Unlicense", "CC0-1.0"}
COPYLEFT = {"GPL-2.0", "GPL-3.0", "LGPL-2.1", "LGPL-3.0", "AGPL-3.0", "MPL-2.0", "EPL-2.0"}
TOPICS = {
    "s2": re.compile(r"(?i)\b(?:coordina\w*|shared (?:queue|task|state)|agent (?:collision|conflict|interference)|race condition|reservation|deadlock|oscillat\w*|distributed lock)"),
    "s3": re.compile(r"(?i)\b(?:multi[- ]?agent|subagents?|swarm|shared (?:resource|browser|queue)|work(?:er|load|force)|schedul\w*|priorit\w*|capacity|resource (?:allocation|limit|control|conflict)|ownership|lease|deadlock|concurren\w*|task (?:assign|distribut|priorit)|rate.limit)"),
    "s3star": re.compile(r"(?i)\b(?:independent review|reviewer|auditor?|auditing|verification|verifier|quality gate|output validation|cross.check|review loop|evaluation feedback|corrective review)"),
    "s4": re.compile(r"(?i)\b(?:model (?:release|upgrade|change|version)|future (?:capability|model)|adaptive|adaptation|long.term learning|self.improv|capability evolution|new provider|environment change|upgrade strateg)"),
    "s5": re.compile(r"(?i)\b(?:governance|policy ownership|mandate|authority transfer|delegat\w* decision|ultimate policy|identity management|human oversight)"),
}


def index_text(client, index_sha, path, local_dir=None):
    if local_dir:
        return (Path(local_dir) / path).read_text(encoding="utf-8")
    data = client.get(api(INDEX, "contents/" + path) + "?ref=" + index_sha)
    if data.get("encoding") != "base64" or data.get("type") != "file":
        raise ValueError("Index file unavailable or not a raw GitHub file: " + path)
    return base64.b64decode(data["content"]).decode("utf-8")


def load_index(client, local_dir=None, index_sha=None):
    if not index_sha:
        if local_dir:
            raise ValueError("local --index-dir requires --index-sha (an exact pinned commit)")
        latest = client.get(api(INDEX, "commits/main"))
        index_sha = latest.get("sha")
    if not isinstance(index_sha, str) or not SHA.fullmatch(index_sha):
        raise ValueError("invalid accepted Index commit pin")
    catalog = {}
    for item in csv.DictReader(io.StringIO(index_text(client, index_sha, "data/catalog.psv", local_dir)),
                               delimiter="|"):
        key = item.get("harness_id")
        if not key or key in catalog:
            raise ValueError("duplicate/invalid Index catalog id")
        catalog[key] = item
    rows, keys = [], set()
    for line in index_text(client, index_sha, "RANKINGS.md", local_dir).splitlines():
        if not line.startswith("| ") or " | <a id=" not in line:
            continue
        match = LINK.match(line)
        if match is None:
            raise ValueError("Index RANKINGS included-row format changed")
        ident, title, path, source, original = match.groups()
        pieces = line[match.end():].split(" | ")
        if len(pieces) < 7:
            raise ValueError("invalid Index autonomy vector row")
        vector_match = re.fullmatch(r"`([^`]+)` \|\s*", pieces[-1])
        if not vector_match:
            raise ValueError("invalid Index autonomy vector field")
        vector = vector_match.group(1).split()
        if len(vector) != 6 or any(x not in {"A", "A(P)", "C", "C(P)", "P", "—", "?"} for x in vector):
            raise ValueError("invalid Index autonomy vector")
        if ident in keys or ident not in catalog or catalog[ident]["repository"].lower() != source.lower():
            raise ValueError("Index RANKINGS and catalog identity mismatch: " + ident)
        if not SHA.fullmatch(catalog[ident]["review_ref"]):
            raise ValueError("invalid historical review_ref")
        keys.add(ident)
        rows.append({"id": ident, "project": title, "original": original,
                     "source_url": source, "assessment_path": path, "vector": vector,
                     "review_ref": catalog[ident]["review_ref"],
                     "catalog_pin_date": catalog[ident]["pinned_at"]})
    if not rows:
        raise ValueError("no accepted Index RANKINGS rows found")
    # Historical popularity is a sampling aid only; do not treat it as
    # current GitHub traffic, usefulness or an Index quality rating.
    stars_file = json.loads(index_text(client, index_sha, "data/github-stars.json", local_dir))
    stars_by_id = {r["harness_id"]: r["stars"] for r in stars_file.get("records", [])
                   if isinstance(r.get("stars"), int) and r.get("fetch_status") == "ok"}
    for row in rows:
        row["historic_stars"] = stars_by_id.get(row["id"])
    return index_sha, rows


def hypotheses(vector):
    s1, s2, s3, audit, s4, s5 = vector
    if s1 not in ("A", "A(P)", "C", "C(P)"):
        return {}
    result = {}
    # S1=A alone already owns operations: no forced A->C upgrade by default.
    # S2 needs multiple actual S1 units/interference, which vector alone cannot
    # establish; a score of 1 is only a lead for whole-repository investigation.
    if s2 in ("—", "?", "P"):
        result["s2"] = 1
    if s2 in ("A", "A(P)", "C", "C(P)") and s3 in ("—", "?", "P"):
        result["s3"] = 4 if s3 == "—" else 3
    if s3 in ("A", "A(P)", "C", "C(P)", "P") and audit in ("—", "?", "P"):
        result["s3star"] = 4 if s3 not in ("P",) else 3
    if s3 in ("A", "A(P)", "C", "C(P)", "P") and s4 in ("—", "?", "P"):
        result["s4"] = 4 if s3 not in ("P",) else 3
    if s5 in ("—", "?", "P") and s3 in ("A", "A(P)", "C", "C(P)", "P"):
        result["s5"] = 2
    # These are heuristics for a source-native investigation, not claims of lack.
    return result


def shortlist(rows, focus, pool):
    out = []
    for row in rows:
        possibilities = hypotheses(row["vector"])
        # "all" must not suppress S5 or privilege S3 as a mandatory P0.
        # These are Index-only research leads; a full six-function census is
        # required *after* selecting the original and before choosing its P0.
        possible = {k: v for k, v in possibilities.items()
                    if focus == "all" or focus == k}
        if focus == "s1" and row["vector"][0] in ("A", "A(P)"):
            # Explicit opt-in exploratory A->C investigation is not the same
            # as claiming S1 lacks operations or requires a constructor.
            possible["s1"] = 1
        if not possible:
            continue
        candidate = dict(row)
        candidate["hypotheses"] = possible
        candidate["index_fit"] = max(possible.values())
        candidate["primary_focus"] = sorted(possible, key=lambda k: (-possible[k], k))[0]
        candidate["primary_focus_is_hint_only"] = True
        candidate["required_repository_wide_screen"] = ["S1", "S2", "S3", "S3*", "S4", "S5"]
        candidate["p0_selected"] = False
        out.append(candidate)
    # Two independent, bounded intake streams prevent alphabetical sorting or
    # old popularity snapshots from hiding newly admitted Index harnesses.
    # Popularity affects only which repos are screened, never the final score.
    prominent = sorted(out, key=lambda x: (-x["index_fit"],
                        -(x["historic_stars"] or 0), x["original"].lower()))
    fresh = sorted(out, key=lambda x: (-x["index_fit"],
                   -int((x["catalog_pin_date"] or "1900-01-01").replace("-", "")),
                   x["original"].lower()))
    result, seen = [], set()
    for i in range(max(len(prominent), len(fresh))):
        for feed in (prominent, fresh):
            if i < len(feed):
                row = feed[i]
                if row["original"].lower() not in seen:
                    result.append(row)
                    seen.add(row["original"].lower())
                    if len(result) == pool:
                        return result
    return result


def live_screen(client, row, now):
    result = dict(row)
    result["disposition"] = "ELIGIBLE_FOR_RESEARCH"
    result["warnings"] = ["Original issue titles are research leads, not established VSM C needs.",
                          "All six VSM functions and the whole source repository must be inspected before P0.",
                          "Intentional non-construction and parent-governed functions may be valid; verify original intent.",
                          "Contributor/maintainer interest is optional and NOT_STATED unless evidenced.",
                          "CLA/DCO, issue bodies, open PR diff and real task gap need human/agent source review."]
    repo = row["original"]
    src = client.get(api(repo, ""))
    if src.get("full_name", "").lower() != repo.lower():
        raise ValueError("original repository identity mismatch")
    if src.get("archived") or src.get("disabled"):
        result["disposition"] = "EXCLUDE_INACTIVE"
    license_id = (src.get("license") or {}).get("spdx_id") or "UNKNOWN"
    result["license"] = license_id
    if license_id in PERMISSIVE:
        result["license_gate"] = "PERMISSIVE_REVIEW_FORMALITIES"
    elif license_id in COPYLEFT:
        result["license_gate"] = "REVIEW_COPYLEFT_AND_CONTRIBUTOR_FORMALITIES"
    else:
        result["license_gate"] = "REVIEW_LICENSE_BEFORE_SELECTION"
        if result["disposition"] == "ELIGIBLE_FOR_RESEARCH":
            result["disposition"] = "RIGHTS_UNVERIFIED"
    result["pushed_at"] = src.get("pushed_at")
    try:
        last = date.fromisoformat(result["pushed_at"][:10]) if result["pushed_at"] else None
        result["days_since_push"] = (now.date() - last).days if last else None
        if last and (now.date() - last).days > 180:
            result["disposition"] = "EXCLUDE_INACTIVE"
    except ValueError:
        result["days_since_push"] = None
        result["warnings"].append("Unknown original activity date.")
    result["stars"] = src.get("stargazers_count")
    result["issue_sample"] = []
    result["issue_evidence"] = []
    if src.get("has_issues"):
        try:
            issues = client.get(api(repo, "issues?state=open&per_page=100&sort=updated&direction=desc"))
            if not isinstance(issues, list):
                raise ValueError("original issue sample malformed")
            for it in issues:
                if it.get("pull_request"):
                    continue
                title = it.get("title")
                url = it.get("html_url")
                if not isinstance(title, str) or not isinstance(url, str):
                    continue
                match_topics = [k for k in row["hypotheses"]
                                if TOPICS[k].search(title)]
                if match_topics:
                    result["issue_evidence"].append({
                        "url": url, "title": title[:240], "matched_topics": match_topics,
                        "updated_at": it.get("updated_at")})
            result["issue_evidence"] = result["issue_evidence"][:6]
            result["issue_sample"] = ["most recent 100 open issues; titles only; may miss older issues"]
        except APIError as exc:
            result["warnings"].append("Original issue sample unavailable: HTTP " + str(exc.status))
            result["disposition"] = "ISSUE_EVIDENCE_UNAVAILABLE"
    else:
        result["warnings"].append("Original GitHub Issues are disabled.")
    # A local fork's presence/absence is NOT proven by repo slug if parent differs.
    fork = FORK_ORG + "/" + repo.rsplit("/", 1)[1]
    result["matched_fork"] = None
    result["owner_control"] = "UNKNOWN"
    result["existing_roadmap_cases"] = None
    try:
        fork_data = client.get(api(fork, ""))
        if fork_data.get("fork") and (fork_data.get("parent") or {}).get("full_name", "").lower() == repo.lower():
            result["matched_fork"] = fork
            try:
                ref = client.get(api(fork, "git/ref/heads/opensiro/meta"))
                sha = (ref.get("object") or {}).get("sha")
                if not isinstance(sha, str) or not SHA.fullmatch(sha):
                    raise ValueError("fork metadata ref malformed")
                state = json.loads(read_text(client, fork, ".opensiro/state.json", sha))
                if state.get("original_repository", "").lower() != repo.lower() or state.get("working_fork", "").lower() != fork.lower():
                    raise ValueError("fork state parent mismatch")
                result["owner_control"] = state.get("owner_control", "UNKNOWN")
                result["attention"] = state.get("attention", "UNKNOWN")
                if result["owner_control"] in ("PAUSE", "STOP"):
                    result["disposition"] = "OWNER_PAUSED"
                try:
                    directories = client.get(api(fork, "contents/.opensiro/issues") + "?ref=" + sha)
                    if not isinstance(directories, list):
                        raise ValueError("invalid fork case list")
                    result["existing_roadmap_cases"] = len([x for x in directories if x.get("type") == "dir"])
                except APIError as exc:
                    if exc.status == 404:
                        result["existing_roadmap_cases"] = 0
                    else:
                        raise
            except APIError as exc:
                if exc.status != 404:
                    raise
                result["warnings"].append("Matching fork lacks opensiro/meta; owner control not presumed ALLOW.")
        else:
            result["warnings"].append("Possible fork slug exists but parent does not match; require explicit fork discovery.")
    except APIError as exc:
        if exc.status != 404:
            raise
        result["warnings"].append("Matching fork slug unavailable; existing alternate-named fork not ruled out.")
    # An existing plan is a reason to seek a *new* candidate first, not a no-value verdict.
    if not result["issue_evidence"] and result["disposition"] == "ELIGIBLE_FOR_RESEARCH":
        result["disposition"] = "NATIVE_DEMAND_UNVERIFIED"
        result["warnings"].append("No topical open issue in latest 100 sampled; absence is not proof of no need.")
    if result["existing_roadmap_cases"]:
        result["warnings"].append("Matching fork already has a roadmap; prefer unstudied cases for new selection.")
    # This is a research obligation, not an invented candidate or live PR validation.
    result["parallel_research_required"] = True
    result["score"] = (10 * row["index_fit"]
                       + 6 * min(3, len(result["issue_evidence"]))
                       + (2 if result["license_gate"] == "PERMISSIVE_REVIEW_FORMALITIES" else 0)
                       + (1 if result["days_since_push"] is not None and result["days_since_push"] <= 30 else 0)
                       - (15 if result["existing_roadmap_cases"] else 0))
    return result


def rank(client, *, focus="all", limit=10, pool=50, probe=20,
         index_dir=None, index_sha=None, no_live=False, observed_at=None):
    observed = observed_at or datetime.now(timezone.utc)
    sha, rows = load_index(client, index_dir, index_sha)
    pool_rows = shortlist(rows, focus, pool)
    if not 0 < probe <= pool or not 0 < limit <= pool:
        raise ValueError("invalid --probe/--limit/--pool bounds")
    result = {"observed_at": observed.isoformat(), "index_commit": sha,
              "index_source": "opensiro/vsm-harness-index/RANKINGS.md + data/catalog.psv",
              "accepted_included_rows": len(rows), "candidate_pool_count": len(pool_rows),
              "focus": focus, "live_screening": not no_live,
              "disclaimer": "Index-only research leads, NOT final P0 ranking: inspect the full original repository and all six S1/S2/S3/S3*/S4/S5 functions before choosing any C target. Document justified intentional omissions, parent/recursion boundaries and UNKNOWN; optional contributor or maintainer interest needs evidence. Compare native Track A vs independently proposed C links Track B; neither a grade nor overlap decides GO/NO_GO.",
              "candidates": [], "unknowns": []}
    if no_live:
        for row in pool_rows[:limit]:
            result["candidates"].append({**row, "disposition": "INDEX_ONLY_NOT_SOURCE_VERIFIED",
                                          "score": None})
        return result
    screened = []
    for row in pool_rows[:probe]:
        try:
            screened.append(live_screen(client, row, observed))
        except (APIError, ValueError, TypeError, KeyError, IncompleteRead, HTTPException) as exc:
            result["unknowns"].append(f"{row['original']}: {exc}")
    # UNKNOWN/PAUSE is never silently treated as ALLOW; only eligible research
    # can head the shortlist. Legal/CLA checks remain explicitly unverified.
    rank_order = {"ELIGIBLE_FOR_RESEARCH": 0, "RIGHTS_UNVERIFIED": 1,
                  "ISSUE_EVIDENCE_UNAVAILABLE": 2, "NATIVE_DEMAND_UNVERIFIED": 2,
                  "OWNER_PAUSED": 3, "EXCLUDE_INACTIVE": 4}
    screened.sort(key=lambda x: (rank_order.get(x["disposition"], 5),
                                  -x["score"], -len(x["issue_evidence"]),
                                  x["original"].lower()))
    result["candidates"] = screened[:limit]
    result["probed"] = len(screened)
    result["scan_complete"] = len(result["unknowns"]) == 0
    return result


def markdown(report):
    lines = ["# Index-first Upstream roadmap selection (read-only)", "",
             f"Index commit: `{report['index_commit']}` · included: {report['accepted_included_rows']}",
             f"Focus: `{report['focus']}` · live original source checks: {report['live_screening']}",
             "**Research leads only, not the P0 function priority.** An Index grade gap or issue title is not an established user need. "
             "Review the whole original repository, all six functions, intentional omissions, contributor/maintainer interests only when evidenced, "
             "current source/issue bodies/PR diffs and formalities before selecting one target.", "",
             "| Candidate | Potential function(s) | Original issues | License | Existing cases | Disposition |",
             "| --- | --- | --- | --- | --- | --- |"]
    for c in report["candidates"]:
        safe = lambda x: str(x).replace("|", chr(92)+"|").replace("\n", " ")
        issues = ", ".join(f"[#{i['url'].rsplit('/',1)[1]}]({i['url']})"
                           for i in c.get("issue_evidence", [])[:3]) or "unverified"
        cs = c.get("existing_roadmap_cases")
        rows = (f"[{safe(c['project'])}]({c['source_url']})",
                ", ".join(c["hypotheses"]), issues, c.get("license", "NOT_CHECKED"),
                str(cs) if cs is not None else "UNKNOWN", c["disposition"])
        lines.append("| " + " | ".join(map(safe, rows)) + " |")
    if report.get("unknowns"):
        lines.extend(["", "## Incomplete source readback", ""])
        lines.extend("- " + str(x) for x in report["unknowns"])
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--focus", choices=("all", "s1", "s2", "s3", "s3star", "s4", "s5"),
                        default="all")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--pool", type=int, default=50)
    parser.add_argument("--probe", type=int, default=20)
    parser.add_argument("--no-live", action="store_true",
                        help="only Index context; results are not source-verified recommendations")
    parser.add_argument("--index-dir", help="offline pinned Index checkout for local screening")
    parser.add_argument("--index-sha", help="pinned Index SHA (required with --index-dir)")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    o = parser.parse_args(argv)
    try:
        result = rank(GitHub(os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")),
                      focus=o.focus, limit=o.limit, pool=o.pool, probe=o.probe,
                      index_dir=o.index_dir, index_sha=o.index_sha, no_live=o.no_live)
    except (ValueError, APIError, OSError, IncompleteRead, HTTPException) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, ensure_ascii=False)
          if o.format == "json" else markdown(result), end="")
    return 0 if o.no_live or result.get("scan_complete") else 1


if __name__ == "__main__":
    raise SystemExit(main())
