#!/usr/bin/env python3
"""Read-only view of fork-local Upstream capability roadmaps, not a writable registry.

The verified fork's opensiro/meta is the source of each case; original GitHub
owns live Issue/PR state. No source code, metadata, issues or PRs are modified.
"""
import argparse
import base64
from datetime import datetime, timezone
import json
import os
import re
from urllib.parse import quote

from aggregate import APIError, GitHub, api, check_state, list_repositories, read_file, REPOSITORY

ORG = "opensiro-contributions"
CASE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,127}$")
SHA = re.compile(r"^[0-9a-f]{40}$")
RESULTS = {"PLAN_ONLY", "NEEDS_EVIDENCE", "DECISION_READY", "NO_USEFUL_CHANGE"}
MAX_TEXT_BYTES = 200_000


def read_text(client, repo, path, sha):
    response = client.get(api(repo, "contents/" + quote(path, safe="/"))
                          + "?ref=" + sha)
    if not isinstance(response, dict) or response.get("type") != "file":
        raise ValueError("not a GitHub file: " + path)
    if response.get("encoding") != "base64":
        raise ValueError("unsupported file encoding: " + path)
    text = base64.b64decode(response["content"]).decode("utf-8")
    if len(text.encode("utf-8")) > MAX_TEXT_BYTES:
        raise ValueError("case file too large: " + path)
    return text


def extract_status(documents):
    receipt = documents.get("roadmap.md", "")
    # Disposition is the research outcome; Result: PLAN_ONLY may only name the route.
    match = re.search(r"(?m)^- Disposition: (PLAN_ONLY|NEEDS_EVIDENCE|DECISION_READY|NO_USEFUL_CHANGE)\b", receipt)
    if not match:
        match = re.search(r"(?m)^- Result: (PLAN_ONLY|NEEDS_EVIDENCE|DECISION_READY|NO_USEFUL_CHANGE)\s*$", receipt)
    if match:
        return match.group(1), "roadmap.md Result"
    # Historical pilot folders need not have a canonical roadmap.md.
    for name in ("README.md", "issue.md"):
        first = documents.get(name, "")[:1500]
        match = re.search(r"(?im)^(?:\*\*)?status:(?:\*\*)?\s*([^\n]+)", first)
        if match:
            values = [v for v in ("NEEDS_EVIDENCE", "NO_USEFUL_CHANGE",
                                  "DECISION_READY", "PLAN_ONLY")
                      if re.search(r"\b" + v + r"\b", match.group(1))]
            if values:
                return values[0], name + " status (historical)"
        for line in first.splitlines()[:5]:
            if "PLAN_ONLY" in line and "NEEDS_EVIDENCE" in line:
                return "NEEDS_EVIDENCE", name + " heading (historical)"
    return "UNKNOWN", "not explicitly recorded"


def original_links(documents, original):
    pattern = re.compile(r"https://github\.com/" + re.escape(original)
                         + r"/(issues|pull)/([1-9][0-9]*)\b", re.IGNORECASE)
    return sorted({f"https://github.com/{original}/{kind}/{number}"
                   for contents in documents.values()
                   for kind, number in pattern.findall(contents)},
                  key=lambda x: ("/pull/" not in x, int(x.rsplit("/", 1)[1])))


def original_observation(client, url, observed_at):
    parts = url.split("/")
    repo, kind, number = "/".join(parts[3:5]), parts[5], parts[6]
    route = api(repo, ("pulls/" if kind == "pull" else "issues/") + number)
    result = {"url": url, "status": "UNKNOWN", "observed_at": observed_at}
    try:
        data = client.get(route)
        if kind == "pull":
            status = ("MERGED" if data.get("merged_at") else "OPEN"
                      if data.get("state") == "open" else "CLOSED_UNMERGED"
                      if data.get("state") == "closed" else "UNKNOWN")
        else:
            status = ("OPEN" if data.get("state") == "open" else "CLOSED"
                      if data.get("state") == "closed" else "UNKNOWN")
        result.update(status=status, updated_at=data.get("updated_at"))
    except APIError as exc:
        result["reason"] = f"GITHUB_HTTP_{exc.status}" if exc.status else "GITHUB_UNAVAILABLE"
    return result


def case_from_directory(client, repo, original, case_id, meta_sha,
                        listing, observed_at, live_original, live_cache):
    if not isinstance(listing, list) or len(listing) >= 1000:
        raise ValueError("invalid/truncated case directory")
    names = {}
    for entry in listing:
        name = entry.get("name")
        if not isinstance(name, str) or entry.get("type") != "file" or "/" in name:
            raise ValueError("unexpected nested case entry")
        if name in names:
            raise ValueError("duplicate case filename")
        names[name] = entry
    documents = {}
    for filename in ("README.md", "roadmap.md", "issue.md",
                     "constructor-sufficiency.md", "comparison.md",
                     "constructor-acceptance.md", "issue-v2.md",
                     "constructor-sufficiency-v2.md"):
        if filename in names:
            path = f".opensiro/issues/{case_id}/{filename}"
            if names[filename].get("path") != path:
                raise ValueError("case path mismatch")
            documents[filename] = read_text(client, repo, path, meta_sha)
    if not (documents.get("roadmap.md") or documents.get("README.md")):
        raise ValueError("case lacks roadmap.md and README.md")
    pilot = "pilot" in case_id and "comparison.md" in names
    canonical = all(x in names for x in
                    ("README.md", "issue.md", "constructor-sufficiency.md", "roadmap.md"))
    kind = "HISTORICAL_TEMPLATE_PILOT" if pilot else "ROADMAP"
    structure = "CANONICAL" if canonical else "HISTORICAL_PILOT" if pilot else "LEGACY_PARTIAL"
    status, status_source = extract_status(documents)
    title = ""
    for name in ("roadmap.md", "issue.md", "README.md"):
        match = re.search(r"(?m)^# (.+)$", documents.get(name, ""))
        if match:
            title = match.group(1).strip()
            break
    paths = {name: f"https://github.com/{repo}/blob/{meta_sha}/.opensiro/issues/{case_id}/{name}"
             for name in documents}
    refs = []
    for url in original_links(documents, original):
        if url not in live_cache:
            live_cache[url] = (original_observation(client, url, observed_at)
                               if live_original
                               else {"url": url, "status": "NOT_CHECKED",
                                     "observed_at": None})
        refs.append(live_cache[url])
    return {"id": case_id, "title": title, "kind": kind, "structure": structure,
            "status": status, "status_source": status_source,
            "files": paths, "original_links": refs,
            "original_link_statuses_live": live_original}


def roadmap_view(client, org=ORG, requested=None, only_active=False,
                 live_original=False, observed_at=None):
    now = observed_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    coverage = {"repositories_discovered": 0, "verified_forks": 0, "missing_meta": 0,
                "no_issues_directory": 0, "forks_with_cases": 0, "cases": 0,
                "filtered_by_attention": 0, "skipped_nonfork": 0,
                "errors": 0, "scan_complete": False}
    report = {"generated_at": now, "source": "GitHub verified fork opensiro/meta",
              "scope": "selected_repositories" if requested else "public_org_repositories",
              "historical_inventory_complete": False, "coverage": coverage,
              "cases": [], "warnings": []}
    if requested:
        repos = sorted(set(requested), key=str.lower)
        for repo in repos:
            if not REPOSITORY.fullmatch(repo) or repo.split("/")[0].lower() != org.lower():
                raise ValueError(f"--repo must belong to {org}: {repo}")
    else:
        try:
            repos = list_repositories(client, org)
        except (APIError, ValueError) as exc:
            report["warnings"].append(f"organization discovery unavailable: {exc}")
            coverage["errors"] += 1
            repos = []
    coverage["repositories_discovered"] = len(repos)
    live_cache = {}
    for repo in repos:
        try:
            info = client.get(api(repo, ""))
            parent = (info.get("parent") or {}).get("full_name")
            if not info.get("fork") or not isinstance(parent, str) or not REPOSITORY.fullmatch(parent):
                coverage["skipped_nonfork"] += 1
                continue
            coverage["verified_forks"] += 1
            try:
                meta = client.get(api(repo, "git/ref/heads/opensiro/meta"))
            except APIError as exc:
                if exc.status == 404:
                    coverage["missing_meta"] += 1
                    continue
                raise
            meta_sha = (meta.get("object") or {}).get("sha")
            if not isinstance(meta_sha, str) or not SHA.fullmatch(meta_sha):
                raise ValueError("invalid metadata head SHA")
            state, _ = read_file(client, repo, ".opensiro/state.json", meta_sha)
            check_state(state, repo, parent)
            if only_active and state["attention"] != "ACTIVE":
                coverage["filtered_by_attention"] += 1
                continue
            try:
                entries = client.get(api(repo, "contents/.opensiro/issues") + "?ref=" + meta_sha)
            except APIError as exc:
                if exc.status == 404:
                    coverage["no_issues_directory"] += 1
                    continue
                raise
            if not isinstance(entries, list) or len(entries) >= 1000:
                raise ValueError("invalid/truncated issues listing")
            dirs = {}
            for entry in entries:
                cid = entry.get("name")
                if (not isinstance(cid, str) or not CASE_ID.fullmatch(cid)
                        or entry.get("type") != "dir"
                        or entry.get("path") != ".opensiro/issues/" + cid):
                    raise ValueError("invalid issue-local directory entry")
                if cid in dirs:
                    raise ValueError("duplicate case id")
                dirs[cid] = True
            fork_cases = []
            for cid in sorted(dirs):
                listing = client.get(api(repo, f"contents/.opensiro/issues/{cid}")
                                     + "?ref=" + meta_sha)
                fork_cases.append(case_from_directory(
                    client, repo, parent, cid, meta_sha, listing,
                    now, live_original, live_cache))
            coverage["forks_with_cases"] += bool(fork_cases)
            coverage["cases"] += len(fork_cases)
            for case in fork_cases:
                case.update(working_fork=repo, original_repository=parent,
                            meta_head_sha=meta_sha, attention=state["attention"],
                            owner_control=state["owner_control"])
            report["cases"].extend(fork_cases)
        except (APIError, ValueError, KeyError, TypeError, UnicodeDecodeError) as exc:
            coverage["errors"] += 1
            report["warnings"].append(f"{repo}: {exc}")
    report["cases"].sort(key=lambda c: (c["working_fork"].lower(), c["id"]))
    unknown_live = sum(x["status"] == "UNKNOWN" for x in live_cache.values())
    coverage["unknown_live_original_links"] = unknown_live
    coverage["original_readback"] = ("NOT_REQUESTED" if not live_original else
                                     "PARTIAL" if unknown_live else "COMPLETE")
    coverage["scan_complete"] = coverage["errors"] == 0 and unknown_live == 0
    if unknown_live:
        report["warnings"].append(f"{unknown_live} original Issue/PR states could not be read live")
    return report


def markdown(report, show_links=False):
    c = report["coverage"]
    safe = lambda x: str(x).replace("|", "\\|").replace("\n", " ")
    lines = ["# Upstream capability roadmap view (read-only)", "",
             f"Observed: {report['generated_at']} · scope: {report['scope']}",
             f"Repositories scanned: **{c['repositories_discovered']}**; "
             f"forks with cases: **{c['forks_with_cases']}**; "
             f"case folders: **{c['cases']}**.",
             f"Missing opensiro/meta: {c['missing_meta']}; "
             f"without .opensiro/issues: {c['no_issues_directory']}; errors: {c['errors']}.",
             f"Scan completeness: **{'COMPLETE' if c['scan_complete'] else 'PARTIAL'}** "
             "(for this accessible GitHub scope; historical inventory remains UNKNOWN).",
             "**Original Issue/PR state:** live checked only with `--live-original`; "
             "otherwise links are NOT_CHECKED, never presumed open/merged.", "",
             "| Original | Fork / case | Type | Status (recorded) | Case structure | Attention / owner |",
             "| --- | --- | --- | --- | --- | --- |"]
    for item in report["cases"]:
        link = item["files"].get("README.md") or item["files"].get("roadmap.md")
        rows = [item["original_repository"],
                f"[{item['working_fork']}/{item['id']}]({link})",
                item["kind"], item["status"], item["structure"],
                item["attention"] + " / " + item["owner_control"]]
        lines.append("| " + " | ".join(map(safe, rows)) + " |")
    for case in report["cases"]:
        links = case["original_links"]
        if links and show_links:
            lines.append("")
            lines.append(f"**{safe(case['working_fork'] + '/' + case['id'])}** original references: " +
                         ", ".join(f"[{x['url'].rsplit('/',2)[-2]} #{x['url'].rsplit('/',1)[-1]}]"
                                   f"({x['url']}) {x['status']}" for x in links))
    if report["warnings"]:
        lines += ["", "## Warnings / unknowns", ""]
        lines += ["- " + safe(msg) for msg in report["warnings"]]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--org", default=ORG)
    parser.add_argument("--repo", action="append", help="repeat to restrict to verified forks")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--only-active", action="store_true")
    parser.add_argument("--live-original", action="store_true",
                        help="fetch live states for linked original Issues/PRs (uses API quota)")
    parser.add_argument("--show-links", action="store_true",
                        help="include every linked original Issue/PR in Markdown view")
    options = parser.parse_args(argv)
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", options.org):
        parser.error("invalid --org")
    try:
        report = roadmap_view(GitHub(os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")),
                              org=options.org, requested=options.repo,
                              only_active=options.only_active,
                              live_original=options.live_original)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(report, ensure_ascii=False, indent=2)
          if options.format == "json" else markdown(report, show_links=(options.show_links or options.live_original)),
          end="\n" if options.format == "json" else "")
    return 0 if report["coverage"]["scan_complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
