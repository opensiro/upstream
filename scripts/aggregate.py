#!/usr/bin/env python3
"""Read-only, source-dated fork-local OpenSiro portfolio view (GitHub REST).

No persistent sync, writes, scheduler, old-ledger import, or outcome grading.
"""
import argparse
import base64
import csv
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

ORGANIZATION = "opensiro-contributions"
REF = "opensiro/meta"
ATTENTION = {"ACTIVE", "WATCHING", "DORMANT", "ARCHIVED"}
CONTROL = {"ALLOW", "PAUSE", "STOP"}
STAGES = {"RESEARCH", "BUILD", "READY", "DELIVERED", "MAINTENANCE",
          "CLOSED_NO_CHANGE", "CLOSED", "BLOCKED"}
PR_STATES = ("OPEN", "MERGED", "CLOSED_UNMERGED", "UNKNOWN")
REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
PR_LINK = re.compile(r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/pull/([1-9][0-9]*)/?$")
ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,127}$")


class APIError(Exception):
    def __init__(self, status, message):
        self.status = status
        super().__init__(message)


class GitHub:
    def __init__(self, token=None):
        self.token = token

    def get(self, path):
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "opensiro-readonly-aggregator",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        request = Request("https://api.github.com" + path, headers=headers)
        try:
            with urlopen(request, timeout=25) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            raise APIError(error.code, f"GitHub HTTP {error.code} for {path}") from error
        except (URLError, OSError, ValueError) as error:
            raise APIError(0, f"GitHub request failed for {path}: {error}") from error


def api(repo, suffix):
    if not REPOSITORY.fullmatch(repo):
        raise ValueError(f"invalid repository identity: {repo!r}")
    return f"/repos/{repo}" + ("/" + suffix if suffix else "")


def read_file(client, repo, path, ref_sha):
    result = client.get(api(repo, "contents/" + path) + "?ref=" + ref_sha)
    if not isinstance(result, dict) or result.get("type") != "file":
        raise ValueError(f"{repo}/{path}: not a GitHub file")
    if result.get("encoding") != "base64":
        raise ValueError(f"{repo}/{path}: unsupported content encoding")
    raw = base64.b64decode(result["content"], validate=False)
    item = json.loads(raw.decode("utf-8"))
    if not isinstance(item, dict):
        raise ValueError(f"{repo}/{path}: expected JSON object")
    return item, result["sha"]


def check_state(item, repo, original):
    if item.get("schema_version") != 1:
        raise ValueError("unsupported state schema")
    if item.get("working_fork") != repo or item.get("original_repository", "").lower() != original.lower():
        raise ValueError("fork state and first-party parent mismatch")
    if item.get("attention") not in ATTENTION or item.get("owner_control") not in CONTROL:
        raise ValueError("invalid attention or owner control")


def check_contribution(item, path, original):
    filename = path.rsplit("/", 1)[-1]
    ident = item.get("id")
    if item.get("schema_version") != 1 or not isinstance(ident, str) or not ID.fullmatch(ident):
        raise ValueError("invalid contribution schema or id")
    if filename != ident + ".json" or item.get("original_repository", "").lower() != original.lower():
        raise ValueError("contribution filename/source mismatch")
    if item.get("work_state") not in STAGES:
        raise ValueError("invalid work_state")
    links = item.get("external_prs")
    if not isinstance(links, list) or not all(isinstance(x, str) for x in links):
        raise ValueError("external_prs must be a list of strings")
    if len(set(links)) != len(links):
        raise ValueError("duplicate external PR URL in improvement")
    return links


def pr_observation(client, url, original, now, live):
    result = {"url": url, "status": "UNKNOWN", "observed_at": now}
    match = PR_LINK.fullmatch(url)
    if not match:
        result["reason"] = "INVALID_GITHUB_PR_URL"
        return result
    target = match.group(1) + "/" + match.group(2)
    if target.lower() != original.lower():
        result["reason"] = "NOT_ORIGINAL_SOURCE_REPOSITORY"
        return result
    if not live:
        result["reason"] = "LIVE_READBACK_DISABLED"
        return result
    try:
        pr = client.get(api(target, "pulls/" + match.group(3)))
        if pr.get("merged_at") is not None:
            status = "MERGED"
        elif pr.get("state") == "open":
            status = "OPEN"
        elif pr.get("state") == "closed":
            status = "CLOSED_UNMERGED"
        else:
            status = "UNKNOWN"
        result.update({"status": status, "draft": bool(pr.get("draft")),
                       "updated_at": pr.get("updated_at"), "merged_at": pr.get("merged_at")})
        if status == "UNKNOWN":
            result["reason"] = "UNRECOGNIZED_FIRST_PARTY_STATE"
    except APIError as error:
        result["reason"] = f"GITHUB_HTTP_{error.status}" if error.status else "GITHUB_UNAVAILABLE"
    return result


def list_repositories(client, org):
    names = set()
    # Full traversal with an explicit bound: fail closed rather than silently truncate.
    for page in range(1, 51):
        batch = client.get(f"/orgs/{org}/repos?per_page=100&page={page}&type=all")
        if not isinstance(batch, list):
            raise ValueError("unexpected organization repositories response")
        for item in batch:
            name = item.get("full_name")
            if not isinstance(name, str) or not REPOSITORY.fullmatch(name):
                raise ValueError("invalid repository identity in organization response")
            if name.split("/")[0].lower() != org.lower():
                raise ValueError("repository outside requested organization")
            names.add(name)
        if len(batch) < 100:
            return sorted(names, key=str.lower)
    raise ValueError("organization repository listing exceeds safety page limit")


def aggregate(client, org=ORGANIZATION, requested=None, only_active=False,
              live_prs=True, observed_at=None):
    now = observed_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    report = {
        "generated_at": now,
        "source": "GitHub REST; original PRs + verified fork opensiro/meta",
        "organization": org,
        "scope": "selected_repositories" if requested else "public_organization_repositories",
        "historical_inventory_complete": False,
        "coverage": {"repositories_discovered": 0, "verified_forks": 0,
                     "missing_meta": 0, "included_forks": 0,
                     "filtered_by_attention": 0, "skipped_nonfork": 0,
                     "errors": 0, "scan_complete": False},
        "summary": {},
        "forks": [],
        "warnings": [],
    }
    coverage = report["coverage"]
    if requested:
        repos = sorted(set(requested), key=str.lower)
        for repo in repos:
            if not REPOSITORY.fullmatch(repo) or repo.split("/")[0].lower() != org.lower():
                raise ValueError(f"--repo must be a {org} repository: {repo}")
    else:
        try:
            repos = list_repositories(client, org)
        except (APIError, ValueError) as error:
            report["warnings"].append(f"organization discovery unavailable: {error}")
            coverage["errors"] += 1
            repos = []
    coverage["repositories_discovered"] = len(repos)
    seen_improvements = set()
    pr_cache = {}
    for repo in repos:
        try:
            info = client.get(api(repo, ""))
            parent = (info.get("parent") or {}).get("full_name")
            if not info.get("fork") or not isinstance(parent, str) or not REPOSITORY.fullmatch(parent):
                coverage["skipped_nonfork"] += 1
                continue
            coverage["verified_forks"] += 1
            try:
                ref = client.get(api(repo, "git/ref/heads/opensiro/meta"))
            except APIError as error:
                if error.status == 404:
                    coverage["missing_meta"] += 1
                    continue
                raise
            sha = (ref.get("object") or {}).get("sha")
            if not isinstance(sha, str) or not re.fullmatch(r"[a-f0-9]{40}", sha):
                raise ValueError("invalid meta branch SHA")
            state, blob_sha = read_file(client, repo, ".opensiro/state.json", sha)
            check_state(state, repo, parent)
            if only_active and state["attention"] != "ACTIVE":
                coverage["filtered_by_attention"] += 1
                continue
            entries = client.get(api(repo, "contents/.opensiro/contributions") + "?ref=" + sha)
            if not isinstance(entries, list) or len(entries) >= 1000:
                raise ValueError("missing, malformed or truncated contribution listing")
            paths = sorted(entry["path"] for entry in entries
                           if entry.get("type") == "file" and entry.get("name", "").endswith(".json")
                           and entry.get("path", "").startswith(".opensiro/contributions/"))
            if len(paths) != len(entries):
                raise ValueError("unexpected entry in contributions directory")
            contributions = []
            for path in paths:
                item, item_sha = read_file(client, repo, path, sha)
                links = check_contribution(item, path, parent)
                key = (parent.lower(), item["id"])
                if key in seen_improvements:
                    raise ValueError("repeated original + contribution identity")
                seen_improvements.add(key)
                prs = []
                for link in links:
                    if link not in pr_cache:
                        pr_cache[link] = pr_observation(client, link, parent, now, live_prs)
                    prs.append(pr_cache[link])
                contributions.append({"id": item["id"], "title": item.get("title", ""),
                                      "work_state": item["work_state"],
                                      "next_action": item.get("next_action", ""),
                                      "source_revision": item.get("source_revision"),
                                      "record_sha": item_sha,
                                      "external_prs": prs})
            report["forks"].append({"working_fork": repo, "original_repository": parent,
                                    "meta_head_sha": sha, "state_blob_sha": blob_sha,
                                    "attention": state["attention"], "owner_control": state["owner_control"],
                                    "contributions": contributions})
            coverage["included_forks"] += 1
        except (APIError, ValueError, KeyError, TypeError, UnicodeDecodeError) as error:
            coverage["errors"] += 1
            report["warnings"].append(f"{repo}: {error}")
    coverage["scan_complete"] = coverage["errors"] == 0
    work_states = {s: 0 for s in sorted(STAGES)}
    attention = {s: 0 for s in sorted(ATTENTION)}
    for fork in report["forks"]:
        attention[fork["attention"]] += 1
        for record in fork["contributions"]:
            work_states[record["work_state"]] += 1
    pr_states = {s: 0 for s in PR_STATES}
    for entry in pr_cache.values():
        pr_states[entry["status"]] += 1
    report["summary"] = {
        "forks_with_metadata": len(report["forks"]),
        "independent_contributions": sum(len(f["contributions"]) for f in report["forks"]),
        "linked_unique_external_prs": len(pr_cache),
        "pr_statuses": pr_states,
        "attention": attention,
        "work_states": work_states,
    }
    coverage["pr_readback"] = ("NOT_REQUESTED" if not live_prs else
                               "PARTIAL" if pr_states["UNKNOWN"] else "COMPLETE")
    coverage["scan_complete"] = (coverage["errors"] == 0 and
                                 (not live_prs or pr_states["UNKNOWN"] == 0))
    report["coverage"]["portfolio_complete"] = False  # historical eligibility is not known from GitHub alone
    return report


def transitions(report, previous):
    old = {}
    for fork in previous.get("forks", []):
        for contribution in fork.get("contributions", []):
            for pr in contribution.get("external_prs", []):
                old[pr.get("url")] = pr.get("status")
    result = []
    seen = set()
    for fork in report["forks"]:
        for contribution in fork["contributions"]:
            for pr in contribution["external_prs"]:
                url = pr["url"]
                if url not in seen and old.get(url) in PR_STATES and old[url] != "UNKNOWN" and pr["status"] != "UNKNOWN" and old[url] != pr["status"]:
                    result.append({"url": url, "from": old[url], "to": pr["status"]})
                seen.add(url)
    return result


def markdown(report):
    s = report["summary"]
    c = report["coverage"]
    lines = ["# OpenSiro fork-local portfolio (read-only)", "",
             f"Observed: {report['generated_at']} · scope: {report['scope']}",
             f"Forks with valid metadata: **{s['forks_with_metadata']}**; independent improvements: **{s['independent_contributions']}**.",
             f"Unique linked external PRs: **{s['linked_unique_external_prs']}**; " +
             ", ".join(f"{k}: {v}" for k, v in s["pr_statuses"].items()) + ".",
             f"Discovery: {c['repositories_discovered']} repositories; {c['missing_meta']} verified forks without meta; {c['errors']} errors.",
             "**Historical inventory completeness: UNKNOWN.** This is not an outcome/usefulness measure.", "",
             "| Original | Fork | Attention / control | Improvement | Work state | External PR | Live PR status |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    safe = lambda v: str(v).replace("|", "\\|").replace("\n", " ")
    for fork in report["forks"]:
        for record in fork["contributions"]:
            prs = record["external_prs"] or [{"url": "—", "status": "—"}]
            for pr in prs:
                lines.append("| " + " | ".join(map(safe, [
                    fork["original_repository"], fork["working_fork"],
                    fork["attention"] + " / " + fork["owner_control"], record["id"],
                    record["work_state"], pr["url"], pr["status"]
                ])) + " |")
    if report.get("pr_transitions"):
        lines.extend(["", "PR status changes since previous JSON:", ""])
        for item in report["pr_transitions"]:
            lines.append(f"- {item['url']}: {item['from']} → {item['to']}")
    if report["warnings"]:
        lines.extend(["", "## Unknowns / warnings", ""])
        lines.extend("- " + safe(x) for x in report["warnings"])
    return "\n".join(lines) + "\n"


def csv_output(report):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["original_repository", "working_fork", "meta_head_sha",
                     "attention", "owner_control", "contribution_id",
                     "work_state", "external_pr_url", "external_pr_status", "pr_observed_at"])
    for fork in report["forks"]:
        for record in fork["contributions"]:
            for pr in (record["external_prs"] or [{"url": "", "status": "", "observed_at": ""}]):
                writer.writerow([fork["original_repository"], fork["working_fork"], fork["meta_head_sha"],
                                 fork["attention"], fork["owner_control"], record["id"],
                                 record["work_state"], pr["url"], pr["status"], pr["observed_at"]])
    return buffer.getvalue()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--org", default=ORGANIZATION)
    parser.add_argument("--repo", action="append", metavar="ORG/REPO",
                        help="limit scope to one or several forks (repeatable)")
    parser.add_argument("--format", choices=["json", "markdown", "csv"], default="json")
    parser.add_argument("--only-active", action="store_true")
    parser.add_argument("--no-prs", action="store_true", help="do not request live third-party PR states")
    parser.add_argument("--compare", type=Path, help="compare external PR states to an earlier JSON output")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", args.org):
        parser.error("invalid --org")
    report = aggregate(GitHub(os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")),
                       org=args.org, requested=args.repo, only_active=args.only_active,
                       live_prs=not args.no_prs)
    if args.compare:
        try:
            previous = json.loads(args.compare.read_text(encoding="utf-8"))
            if not isinstance(previous, dict):
                raise ValueError("comparison input must be a JSON object")
            report["pr_transitions"] = transitions(report, previous)
        except (OSError, ValueError) as error:
            parser.error(f"invalid --compare: {error}")
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    elif args.format == "markdown":
        print(markdown(report), end="")
    else:
        print(csv_output(report), end="")
        if report["warnings"]:
            print("WARNING: partial data, inspect --format json for details", file=sys.stderr)
    return 0 if report["coverage"]["scan_complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
