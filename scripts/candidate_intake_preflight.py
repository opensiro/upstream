#!/usr/bin/env python3
"""Read-only first-party upstream candidate intake, before any derivative work.

This inspector collects license text evidence and contributor/issue/PR hints.
It cannot grant copyright permission, certify DCO/CLA, approve a branch or PR,
or authorize any GitHub write. GitHub observations are potentially incomplete.
"""

import argparse
import base64
import binascii
import hashlib
import json
import math
import re
import sys
from urllib.parse import quote

from fork_public_preflight import ReadOnlyError, public_get
from rest_fork_port import StageBlocked, _branch, _repo

MAX_TEXT_BYTES = 256 * 1024
MAX_ITEMS = 100
MAX_PAGES = 30
LICENSE_NAME = re.compile(
    r"^(licen[sc]e(?:[-_.](?:mit|apache|bsd|isc|mpl|gpl|lgpl|agpl)"
    r"(?:[-_.]?[0-9]+(?:\.[0-9]+)?)?)?|copying|unlicense)"
    r"(?:\.(md|txt|rst))?$", re.I)
POLICY_NAME = re.compile(
    r"^(contributing|agents|claude|development|pull_request_template|codeowners)"
    r"(\.(md|txt|rst))?$", re.I)
POLICY_FOLDERS = (".github", "docs")
TOPIC = re.compile(r"[A-Za-z0-9][A-Za-z0-9 ._-]{2,79}\Z")

POLICY_PATTERNS = (
    ("DCO_SIGNOFF_MENTIONED", r"\bDCO\b|Signed-off-by", "BEFORE_DRAFT"),
    ("CLA_MENTIONED", r"\bCLA\b|contributor license agreement", "BEFORE_DRAFT"),
    ("ISSUE_WORKFLOW_MENTIONED", r"\bissue\b|\bassigned\b", "BEFORE_IMPLEMENTATION"),
    ("BRANCH_NAMING_MENTIONED", r"\bbranch\b|\bbranches\b", "BEFORE_IMPLEMENTATION"),
    ("TEST_OR_CI_GATE_MENTIONED", r"\bCI\b|\btests?\b|\bchecks?\b", "BEFORE_READY"),
    ("DRAFT_PR_GATE_MENTIONED",
     r"\bbefore (?:opening|submitting|creating) (?:a )?(?:draft )?(?:PR|pull request)\b",
     "BEFORE_DRAFT"),
    ("READY_PR_GATE_MENTIONED", r"\bready for review\b|\bmark (?:the )?PR ready\b",
     "BEFORE_READY"),
    ("MERGE_GATE_MENTIONED", r"\bbefore merg(?:e|ing)\b|\bprior to merg(?:e|ing)\b",
     "BEFORE_MERGE"),
)


class IntakeError(ValueError):
    """A source fact was unverified; do not treat this as license absence."""


def _get(get, path, *, missing_ok=False, list_ok=False):
    if not isinstance(path, str) or not path.startswith("/repos/"):
        raise IntakeError("Only fixed repository-scoped GET paths are allowed")
    response = get(path)
    if (type(response) is not tuple or len(response) != 2
            or type(response[0]) is not int):
        raise IntakeError("Unverified GitHub API response")
    status, data = response
    if status == 404 and missing_ok:
        return None
    if status in (401, 403, 429):
        raise IntakeError("GitHub access denied or rate limited, not license absence")
    if status != 200:
        raise IntakeError("Unexpected GitHub API status: " + str(status))
    if type(data) is not (list if list_ok else dict):
        raise IntakeError("Malformed GitHub API response shape")
    return data


def _contents_path(source, path, ref):
    if any(part in ("", ".", "..") for part in path.split("/")):
        raise IntakeError("Unsafe path in repository listing")
    encoded = "/".join(quote(part, safe="") for part in path.split("/"))
    return "/repos/" + source + "/contents/" + encoded + "?ref=" + quote(ref, safe="")


def _file_text(get, source, path, ref):
    result = _get(get, _contents_path(source, path, ref))
    if (result.get("type") != "file" or result.get("encoding") != "base64"
            or not isinstance(result.get("content"), str)
            or not isinstance(result.get("size"), int)
            or not 0 <= result["size"] <= MAX_TEXT_BYTES):
        raise IntakeError("License/policy file is unreadable or too large: " + path)
    try:
        data = base64.b64decode(result["content"].replace("\n", ""), validate=True)
        if len(data) > MAX_TEXT_BYTES or len(data) != result["size"]:
            raise IntakeError("File exceeds bounded content limit: " + path)
        return data.decode("utf-8")
    except (binascii.Error, UnicodeError) as exc:
        raise IntakeError("License/policy text could not be verified: " + path) from exc


def _matches(items, topic):
    if topic is None:
        return []
    tokens = set(re.findall(r"[a-z0-9]+", topic.casefold()))
    matches = []
    for item in items:
        if type(item) is not dict:
            raise IntakeError("Malformed issue/PR listing entry")
        title = item.get("title", "")
        if not isinstance(title, str):
            raise IntakeError("Malformed issue/PR title")
        body = item.get("body") or ""
        if not isinstance(body, str):
            raise IntakeError("Malformed issue/PR body")
        title_tokens = set(re.findall(r"[a-z0-9]+", title.casefold()))
        body_tokens = set(re.findall(r"[a-z0-9]+", body.casefold()))
        title_hit = tokens <= title_tokens
        body_hit = tokens <= body_tokens
        matched = tokens & (title_tokens | body_tokens)
        threshold = min(len(tokens), max(2, math.ceil(len(tokens) / 2)))
        if len(matched) >= threshold:
            matches.append({"number": item.get("number"), "title": title[:200],
                            "url": item.get("html_url"), "state": item.get("state"),
                            "matched_in": ("title" if title_hit else "body" if body_hit
                                           else "combined"),
                            "matched_tokens": sorted(matched)})
    return matches


def _inventory(get, source, kind):
    """Traverse both open and closed records; bound work and disclose truncation."""
    collected = []
    for page in range(1, MAX_PAGES + 1):
        path = (f"/repos/{source}/{kind}?state=all&per_page={MAX_ITEMS}&page={page}")
        rows = _get(get, path, list_ok=True)
        if len(rows) > MAX_ITEMS:
            raise IntakeError("GitHub inventory page exceeds advertised page size")
        collected.extend(rows)
        if len(rows) < MAX_ITEMS:
            return collected, True, page
    return collected, False, MAX_PAGES


def _policy_paths(get, source, root, sha):
    """Only bounded first-party paths; templates and nested instructions are not silently ignored."""
    seen = set()
    for entry in root:
        if entry.get("type") == "file" and POLICY_NAME.fullmatch(entry["name"]):
            seen.add(entry["name"])
    for folder in POLICY_FOLDERS:
        if not any(e.get("name") == folder and e.get("type") == "dir" for e in root):
            continue
        entries = _get(get, _contents_path(source, folder, sha), list_ok=True)
        for entry in entries:
            if (type(entry) is not dict or not isinstance(entry.get("name"), str)
                    or entry.get("type") not in ("file", "dir")):
                raise IntakeError("Malformed contributor policy directory: " + folder)
            if entry["type"] == "file" and POLICY_NAME.fullmatch(entry["name"]):
                seen.add(folder + "/" + entry["name"])
            if folder == ".github" and entry["type"] == "dir" and entry["name"] in (
                    "ISSUE_TEMPLATE", "PULL_REQUEST_TEMPLATE"):
                templates = _get(get, _contents_path(source, folder + "/" + entry["name"], sha),
                                 list_ok=True)
                for child in templates:
                    if (type(child) is not dict or not isinstance(child.get("name"), str)
                            or child.get("type") not in ("file", "dir")):
                        raise IntakeError("Malformed contributor template directory")
                    if child["type"] == "file" and child["name"].lower().endswith(
                            (".md", ".txt", ".rst", ".yml", ".yaml")):
                        seen.add(folder + "/" + entry["name"] + "/" + child["name"])
    return sorted(seen)


def _policy_evidence(contents, path):
    observations = []
    for line_number, line in enumerate(contents.splitlines(), 1):
        for label, pattern, stage in POLICY_PATTERNS:
            if re.search(pattern, line, re.I):
                observations.append({"path": path, "line": line_number, "stage": stage,
                                     "code": label, "excerpt": line.strip()[:240]})
    if len(observations) > 250:
        raise IntakeError("Contributor policy evidence limit exceeded: " + path)
    return observations


def _gates(result):
    """Stages are evidence summaries, never substituted for real approvals."""
    evidence = result["contributor_policy"]["evidence"]
    gates = {}
    for stage in ("BEFORE_IMPLEMENTATION", "BEFORE_DRAFT", "BEFORE_READY", "BEFORE_MERGE"):
        codes = sorted({e["code"] for e in evidence if e["stage"] == stage})
        gates[stage] = {"status": "NOT_CLEARED", "policy_hints": codes,
                        "reasons": ["FIRST_PARTY_POLICY_REVIEW_REQUIRED"]}
    gates["BEFORE_IMPLEMENTATION"]["reasons"].extend(
        ["LICENSE_COMPATIBILITY_REVIEW_REQUIRED", "NATIVE_DEFECT_NOT_VERIFIED"])
    gates["BEFORE_DRAFT"]["reasons"].extend(
        ["NATIVE_RED_GREEN_REQUIRED", "FORK_ACTOR_AND_DIFF_REQUIRED", "DCO_CLA_IF_APPLICABLE"])
    gates["BEFORE_READY"]["reasons"].append("REQUIRED_REVIEW_AND_CHECKS_NOT_OBSERVED")
    gates["BEFORE_MERGE"]["reasons"].append("UPSTREAM_MAINTAINER_MERGE_RESERVED")
    if result["overlap"]["status"] == "INVENTORY_INCOMPLETE":
        gates["BEFORE_IMPLEMENTATION"]["reasons"].append("DUPLICATE_INVENTORY_INCOMPLETE")
    if result["overlap"]["issues"] or result["overlap"]["pull_requests"]:
        gates["BEFORE_IMPLEMENTATION"]["reasons"].append("POTENTIAL_DUPLICATE_REVIEW_REQUIRED")
    return gates


def inspect_candidate(*, source, branch=None, topic=None, get=public_get):
    """Fetch only public repository evidence; never output an approval."""
    source = _repo(source)
    if branch is not None:
        branch = _branch(branch)
    if topic is not None and (type(topic) is not str or not TOPIC.fullmatch(topic)):
        raise IntakeError("Topic must be 3–80 plain search characters")

    result = {
        "status": "INSUFFICIENT_EVIDENCE", "authorization": "READ_ONLY_NO_WRITES",
        "source": source, "source_branch": branch, "source_sha": None,
        "license": {"verdict": "LICENSE_UNRESOLVED", "spdx_metadata": None,
                    "path": None, "sha256": None, "review_required": True},
        "contributor_policy": {"paths": [], "hints": [], "evidence": [],
                               "review_required": True},
        "overlap": {"topic": topic, "issues": [], "pull_requests": [],
                    "status": "NOT_SEARCHED"},
        "gates": {}, "reason_codes": ["LICENSE_NOT_VERIFIED"],
        "notes": ["First-party text may contain additional obligations; review is required.",
                  "No POST, fork, patch, PR, license grant or legal sign-off is possible."],
    }
    repo = _get(get, "/repos/" + source)
    if (repo.get("full_name", "").casefold() != source.casefold()
            or repo.get("private") is not False
            or repo.get("archived") is not False
            or repo.get("disabled") is not False):
        raise IntakeError("Public source identity/status is unsuitable")
    observed_branch = branch or repo.get("default_branch")
    if not isinstance(observed_branch, str):
        raise IntakeError("Upstream default branch unavailable")
    observed_branch = _branch(observed_branch)
    result["source_branch"] = observed_branch
    result["license"]["spdx_metadata"] = (repo.get("license") or {}).get("spdx_id")
    checked = _get(get, "/repos/" + source + "/branches/" + quote(observed_branch, safe=""))
    sha = (checked.get("commit") or {}).get("sha")
    if type(sha) is not str or re.fullmatch(r"[0-9a-f]{40}", sha) is None:
        raise IntakeError("Source revision cannot be pinned")
    result["source_sha"] = sha

    root = _get(get, "/repos/" + source + "/contents?ref=" +
                quote(sha, safe=""), list_ok=True)
    files = {}
    for item in root:
        if type(item) is not dict or not isinstance(item.get("name"), str):
            raise IntakeError("Malformed root directory listing")
        if item.get("type") == "file":
            files[item["name"].casefold()] = item["name"]
    license_paths = sorted((name for name in files.values()
                            if LICENSE_NAME.fullmatch(name)), key=lambda p: p.casefold())
    if not license_paths:
        result["status"] = "LICENSE_BLOCKED"
        result["reason_codes"] = ["ROOT_LICENSE_NOT_FOUND"]
        result["gates"] = {"BEFORE_IMPLEMENTATION": {
            "status": "BLOCKED", "reasons": ["ROOT_LICENSE_NOT_FOUND"]}}
        result["license"]["verdict"] = "LICENSE_NOT_FOUND_AT_ROOT"
        result["notes"].append(
            "No root LICENSE/COPYING/UNLICENSE observed; do not create a derivative. "
            "Check subdirectory licenses or obtain rights from the holder.")
        return result
    if len(license_paths) > 1:
        result["notes"].append("Multiple root license candidates: manual scope review required")
    license_files = []
    for license_path in license_paths:
        license_text = _file_text(get, source, license_path, sha)
        if not license_text.strip():
            raise IntakeError("Observed license file is empty: " + license_path)
        license_files.append({
            "path": license_path,
            "sha256": hashlib.sha256(license_text.encode()).hexdigest(),
        })
    result["license"].update({
        "verdict": "LICENSE_TEXT_PRESENT_REVIEW_REQUIRED",
        "path": license_files[0]["path"],
        "sha256": license_files[0]["sha256"],
        "files": license_files,
        "other_root_license_candidates": license_paths[1:],
    })

    for actual in _policy_paths(get, source, root, sha):
        contents = _file_text(get, source, actual, sha)
        result["contributor_policy"]["paths"].append({
            "path": actual, "sha256": hashlib.sha256(contents.encode()).hexdigest()})
        result["contributor_policy"]["evidence"].extend(_policy_evidence(contents, actual))
    result["contributor_policy"]["hints"] = sorted({
        evidence["code"] for evidence in result["contributor_policy"]["evidence"]})

    if topic is not None:
        issues, issues_complete, issues_pages = _inventory(get, source, "issues")
        prs, prs_complete, prs_pages = _inventory(get, source, "pulls")
        result["overlap"].update({
            "issues": _matches([item for item in issues if "pull_request" not in item], topic),
            "pull_requests": _matches(prs, topic),
            "issues_pages": issues_pages, "pull_requests_pages": prs_pages,
            "issue_count_examined": len(issues), "pull_request_count_examined": len(prs),
            "status": ("TITLE_BODY_HEURISTIC_ONLY_NOT_PROOF_OF_ABSENCE"
                       if issues_complete and prs_complete else "INVENTORY_INCOMPLETE"),
        })
        if not issues_complete or not prs_complete:
            result["notes"].append("Issue/PR inventory exceeded bounded page budget")
    result["status"] = "LICENSE_REVIEW_REQUIRED"
    result["reason_codes"] = ["LICENSE_COMPATIBILITY_REVIEW_REQUIRED"]
    result["gates"] = _gates(result)
    return result


def main(argv=None, *, get=public_get):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="owner/repo")
    parser.add_argument("--branch", help="default branch when omitted")
    parser.add_argument("--topic", help="bounded terms for heuristic issue/PR titles")
    args = parser.parse_args(argv)
    try:
        result = inspect_candidate(source=args.source, branch=args.branch,
                                   topic=args.topic, get=get)
    except (IntakeError, ReadOnlyError, StageBlocked) as exc:
        result = {"status": "INSUFFICIENT_EVIDENCE",
                  "authorization": "READ_ONLY_NO_WRITES", "reason": str(exc),
                  "reason_codes": ["SOURCE_EVIDENCE_UNVERIFIED"],
                  "gates": {"BEFORE_IMPLEMENTATION": {
                      "status": "BLOCKED", "reasons": ["SOURCE_EVIDENCE_UNVERIFIED"]}}}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "LICENSE_REVIEW_REQUIRED" else 2


if __name__ == "__main__":
    sys.exit(main())
