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
import re
import sys
from urllib.parse import quote

from fork_public_preflight import ReadOnlyError, public_get
from rest_fork_port import StageBlocked, _branch, _repo

MAX_TEXT_BYTES = 256 * 1024
MAX_ITEMS = 100
LICENSE_NAME = re.compile(r"^(licen[sc]e|copying|unlicense)(\.(md|txt|rst))?$", re.I)
POLICY_NAMES = ("CONTRIBUTING.md", "AGENTS.md", "CLAUDE.md")
TOPIC = re.compile(r"[A-Za-z0-9][A-Za-z0-9 ._-]{2,79}\Z")


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
    tokens = topic.casefold().split()
    matches = []
    for item in items:
        if type(item) is not dict:
            raise IntakeError("Malformed issue/PR listing entry")
        title = item.get("title", "")
        if not isinstance(title, str):
            raise IntakeError("Malformed issue/PR title")
        if all(token in title.casefold() for token in tokens):
            matches.append({"number": item.get("number"), "title": title[:200],
                            "url": item.get("html_url")})
    return matches[:20]


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
        "contributor_policy": {"paths": [], "hints": [], "review_required": True},
        "overlap": {"topic": topic, "issues": [], "pull_requests": [],
                    "status": "NOT_SEARCHED"},
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
                quote(observed_branch, safe=""), list_ok=True)
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
        result["license"]["verdict"] = "LICENSE_NOT_FOUND_AT_ROOT"
        result["notes"].append(
            "No root LICENSE/COPYING/UNLICENSE observed; do not create a derivative. "
            "Check subdirectory licenses or obtain rights from the holder.")
        return result
    if len(license_paths) > 1:
        result["notes"].append("Multiple root license candidates: manual scope review required")
    license_path = license_paths[0]
    license_text = _file_text(get, source, license_path, observed_branch)
    if not license_text.strip():
        raise IntakeError("Observed license file is empty")
    result["license"].update({
        "verdict": "LICENSE_TEXT_PRESENT_REVIEW_REQUIRED", "path": license_path,
        "sha256": hashlib.sha256(license_text.encode()).hexdigest(),
        "other_root_license_candidates": license_paths[1:],
    })

    for path in POLICY_NAMES:
        actual = files.get(path.casefold())
        if not actual:
            continue
        contents = _file_text(get, source, actual, observed_branch)
        result["contributor_policy"]["paths"].append({
            "path": actual, "sha256": hashlib.sha256(contents.encode()).hexdigest()})
        for label, pattern in (
            ("DCO_SIGNOFF_MENTIONED", r"\bDCO\b|Signed-off-by"),
            ("CLA_MENTIONED", r"\bCLA\b|contributor license agreement"),
            ("ISSUE_WORKFLOW_MENTIONED", r"\bissue\b"),
            ("BRANCH_NAMING_MENTIONED", r"\bbranch\b|\bbranches\b"),
            ("TEST_OR_CI_GATE_MENTIONED", r"\bCI\b|\btests?\b|\bchecks?\b"),
            ("DRAFT_PR_GATE_MENTIONED", r"\bbefore (?:opening|submitting|creating) (?:a )?(?:draft )?(?:PR|pull request)\b"),
            ("MERGE_GATE_MENTIONED", r"\bbefore merg(?:e|ing)\b|\bprior to merg(?:e|ing)\b"),
        ):
            if re.search(pattern, contents, re.I) and label not in result["contributor_policy"]["hints"]:
                result["contributor_policy"]["hints"].append(label)

    if topic is not None:
        path = "/repos/" + source
        issues = _get(get, path + "/issues?state=all&per_page=100", list_ok=True)
        prs = _get(get, path + "/pulls?state=open&per_page=100", list_ok=True)
        result["overlap"].update({
            "issues": _matches([item for item in issues if "pull_request" not in item], topic),
            "pull_requests": _matches(prs, topic),
            "status": ("PAGINATION_REQUIRED" if len(issues) >= MAX_ITEMS or len(prs) >= MAX_ITEMS
                       else "TITLE_HEURISTIC_ONLY_NOT_PROOF_OF_ABSENCE"),
        })
        if len(issues) >= MAX_ITEMS or len(prs) >= MAX_ITEMS:
            result["notes"].append("Open issue/PR inventory reached page limit; check further pages")
    result["status"] = "LICENSE_REVIEW_REQUIRED"
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
                  "authorization": "READ_ONLY_NO_WRITES", "reason": str(exc)}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "LICENSE_REVIEW_REQUIRED" else 2


if __name__ == "__main__":
    sys.exit(main())
