#!/usr/bin/env python3
"""Read-only, exact external upstream PR handoff for an organization-owned fork.

No create/publish option, no POST, no token reads, no auth/grant issuance.
Prints the reviewed GitHub REST payload for a SEPARATE human-owned action.
A green handoff is not permission to publish.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import quote

from rest_fork_port import _repo, _branch, StageBlocked

SHA = re.compile(r"^[0-9a-f]{40}$")
LOGIN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]{0,38}$")
CONTRIB_BRANCH = re.compile(r"^opensiro/[a-z0-9][a-z0-9._/-]{0,79}$")
ALLOWED_OWNERS = {"opensiro", "opensiro-contributions"}


class PRBlocked(Exception):
    pass


def _need(value, reason):
    if not value:
        raise PRBlocked(reason)


def _valid_repo(value):
    try:
        return _repo(value)
    except StageBlocked as exc:
        raise PRBlocked(str(exc)) from None


def _json_sha(value, reason):
    _need(type(value) is str and SHA.fullmatch(value), reason)
    return value


def _valid_branch(branch, *, contribution=False):
    try:
        _branch(branch)
    except StageBlocked:
        raise PRBlocked("Invalid branch name") from None
    if contribution:
        _need(CONTRIB_BRANCH.fullmatch(branch) is not None,
              "Head branch must be namespaced opensiro/*")
    return branch


def _get(endpoint, *, runner=subprocess.run):
    # Fixed gh invocation: the program does not issue any HTTP write.
    try:
        result = runner(["gh", "api", "--method", "GET", endpoint],
                        capture_output=True, text=True, check=False, timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        raise PRBlocked("Authenticated read transport unavailable") from None
    _need(result.returncode == 0, "Authenticated GitHub GET unavailable")
    try:
        return json.loads(result.stdout)
    except (TypeError, ValueError):
        raise PRBlocked("Malformed authenticated GitHub response") from None


def prepare_pr_handoff(*, upstream, fork, head_branch, head_sha, base_branch,
                       base_sha, title, body, runner=subprocess.run):
    upstream = _valid_repo(upstream)
    fork = _valid_repo(fork)
    head_branch = _valid_branch(head_branch, contribution=True)
    base_branch = _valid_branch(base_branch)
    head_sha = _json_sha(head_sha, "Head requires pinned 40-hex SHA")
    base_sha = _json_sha(base_sha, "Base requires pinned 40-hex SHA")
    _need(fork != upstream and fork.split("/")[0] in ALLOWED_OWNERS,
          "Fork must be in an explicitly supported OpenSiro organization")
    _need(type(title) is str and 5 <= len(title.strip()) <= 180
          and "\n" not in title, "PR title must be bounded single-line text")
    _need(type(body) is str and 1 <= len(body.encode("utf-8")) <= 16384,
          "PR body must be reviewed and within size limit")

    actor = _get("user", runner=runner)
    _need(type(actor) is dict and type(actor.get("login")) is str
          and LOGIN.fullmatch(actor["login"]) is not None,
          "Authenticated GitHub user not verified")

    original = _get("repos/" + upstream, runner=runner)
    working = _get("repos/" + fork, runner=runner)
    _need(type(original) is dict and
          original.get("full_name", "").casefold() == upstream.casefold()
          and original.get("private") is False and original.get("archived") is False
          and original.get("disabled") is not True,
          "Unverified or inactive public upstream")
    _need(type(working) is dict and
          working.get("full_name", "").casefold() == fork.casefold()
          and working.get("private") is False and working.get("archived") is False
          and working.get("fork") is True
          and (working.get("parent") or {}).get("full_name", "").casefold()
          == upstream.casefold()
          and (working.get("permissions") or {}).get("push") is True,
          "Fork parent/public status or authenticated push rights invalid")

    observed_base = _get("repos/" + upstream + "/branches/" +
                         quote(base_branch, safe=""), runner=runner)
    observed_head = _get("repos/" + fork + "/branches/" +
                         quote(head_branch, safe=""), runner=runner)
    _need(type(observed_base) is dict and type(observed_head) is dict,
          "Missing base/head branch")
    _need((observed_base.get("commit") or {}).get("sha") == base_sha,
          "Upstream base branch moved after review")
    _need((observed_head.get("commit") or {}).get("sha") == head_sha,
          "Fork PR head branch moved after review")

    # GitHub compare supports BASE...OWNER:BRANCH across the same fork network.
    cmp_path = ("repos/" + upstream + "/compare/" +
                quote(base_branch, safe="") + "..." +
                quote(fork.split("/")[0] + ":" + head_branch, safe=""))
    comparison = _get(cmp_path, runner=runner)
    _need(type(comparison) is dict
          and comparison.get("status") in ("ahead", "diverged")
          and type(comparison.get("ahead_by")) is int
          and comparison["ahead_by"] > 0
          and type(comparison.get("files")) is list
          and 0 < len(comparison["files"]) < 300,
          "No verified nonempty contribution diff or compare was truncated")

    query = ("?state=open&head=" +
             quote(fork.split("/")[0] + ":" + head_branch, safe="") +
             "&base=" + quote(base_branch, safe="") + "&per_page=100")
    existing = _get("repos/" + upstream + "/pulls" + query, runner=runner)
    _need(type(existing) is list and len(existing) < 100,
          "Open upstream PR inventory unavailable or truncated")
    _need(not existing, "An open upstream PR already targets this fork branch/base")

    post = {"title": title.strip(), "body": body,
            "head": fork.split("/")[0] + ":" + head_branch,
            "base": base_branch, "draft": True,
            "maintainer_can_modify": True}
    if upstream.split("/")[0].casefold() == fork.split("/")[0].casefold():
        post["head_repo"] = fork.split("/")[1]

    evidence = {
        "actor": actor["login"], "upstream": upstream, "fork": fork,
        "base_branch": base_branch, "base_sha": base_sha,
        "head_branch": head_branch, "head_sha": head_sha,
        "ahead_by": comparison["ahead_by"],
        "changed_files_observed": len(comparison["files"]),
        "proposal_stage": "submit_external_pr",
        "title_sha256": hashlib.sha256(title.strip().encode()).hexdigest(),
        "body_sha256": hashlib.sha256(body.encode()).hexdigest(),
    }
    canonical = json.dumps({"evidence": evidence, "payload": post},
                           sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return {
        "status": "PR_READY_FOR_MANUAL_REVIEW_NOT_PUBLISHED",
        "authorization": "EXTERNAL_PR_HUMAN_OWNED_NO_WRITE",
        "api_method_if_separately_approved": "POST",
        "api_path_if_separately_approved": "repos/" + upstream + "/pulls",
        "draft_request_body": post, "evidence": evidence,
        "intent_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
        "notes": [
            "This handoff performs authenticated GET operations ONLY.",
            "A body/digest/preview is not signed approval or an execution permit.",
            "Revalidate branch refs, policy, duplicate PRs and diff before manual publication.",
            "Use GitHub REST for organization heads; gh pr create --head ORG:branch is not supported.",
            "Do not POST from an unprotected runner or publish an upstream PR automatically.",
        ],
    }


def main(argv=None, *, runner=subprocess.run):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", required=True)
    parser.add_argument("--fork", required=True)
    parser.add_argument("--head-branch", required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--base-branch", required=True)
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--body-file", required=True)
    args = parser.parse_args(argv)
    try:
        body_path = Path(args.body_file)
        if not body_path.is_file() or body_path.stat().st_size > 16384:
            raise PRBlocked("Reviewed PR body file missing or oversized")
        result = prepare_pr_handoff(
            upstream=args.upstream, fork=args.fork,
            head_branch=args.head_branch, head_sha=args.head_sha,
            base_branch=args.base_branch, base_sha=args.base_sha,
            title=args.title, body=body_path.read_text(encoding="utf-8"),
            runner=runner)
    except (PRBlocked, StageBlocked, OSError, UnicodeError) as exc:
        result = {"status": "PR_BLOCKED_NO_WRITE",
                  "authorization": "EXTERNAL_PR_HUMAN_OWNED_NO_WRITE",
                  "reason": str(exc)}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "PR_READY_FOR_MANUAL_REVIEW_NOT_PUBLISHED" else 2


if __name__ == "__main__":
    sys.exit(main())
