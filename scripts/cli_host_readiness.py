#!/usr/bin/env python3
"""Observe GitHub CLI auth for one VM/host OS account without reading tokens.

This is a GET-only *readiness* probe. No credential-helper 'fill', no PAT
disclosure, no approval, no POST, no fork, no executor capability proof.
"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from rest_fork_port import _branch, _repo, StageBlocked

SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$")
SHA = re.compile(r"^[0-9a-f]{40}$")


def _run(args, runner):
    """Discard stderr, never render gh auth status or credential output."""
    try:
        result = runner(args, capture_output=True, text=True, timeout=12,
                        check=False)
    except (OSError, subprocess.TimeoutExpired):
        return False, ""
    return result.returncode == 0, result.stdout.strip()


def inspect_cli_host(*, source, working_branch, runner=subprocess.run,
                     which=shutil.which, home=None, environ=None):
    source = _repo(source)
    working_branch = _branch(working_branch)
    env = os.environ if environ is None else environ
    home = Path.home() if home is None else Path(home)
    gh_installed = which("gh") is not None
    git_installed = which("git") is not None
    result = {
        "status": "BLOCKED_GH_CLI_UNAVAILABLE",
        "authorization": "NOT_APPROVED_NO_WRITES",
        "fork_create_permission": "NOT_TESTED_NO_WRITES",
        "source": source, "working_branch": working_branch,
        "github_cli_installed": gh_installed,
        "git_installed": git_installed,
        "gh_authenticated": False,
        "github_login": None,
        "source_branch_sha": None,
        "git_credential_store_file_present": (home / ".git-credentials").is_file(),
        "git_credential_helper_configured": False,
        "github_token_env_presence": bool(env.get("GH_TOKEN") or env.get("GITHUB_TOKEN")),
        "notes": [
            "No token bytes or credential-helper output were inspected.",
            "This checks only the current OS user and execution environment.",
            "Git credential-store presence does not prove gh CLI auth or fork rights.",
            "An authenticated GitHub CLI does not prove destination repo-creation rights.",
        ],
    }
    if git_installed:
        ok, _ = _run(["git", "config", "--global", "--get",
                      "credential.helper"], runner)
        result["git_credential_helper_configured"] = ok
    if not gh_installed:
        return result

    ok, _ = _run(["gh", "auth", "status", "--hostname", "github.com"], runner)
    if not ok:
        result["status"] = "BLOCKED_GH_CLI_AUTH"
        return result
    result["gh_authenticated"] = True

    ok, login = _run(["gh", "api", "--method", "GET", "user",
                      "--jq", ".login"], runner)
    if not ok or not SLUG.fullmatch(login):
        result["status"] = "BLOCKED_GH_IDENTITY"
        return result
    result["github_login"] = login

    # Read-only identity + pinned working branch observation. No POST path.
    ok, sha = _run(["gh", "api", "--method", "GET",
                    "repos/" + source + "/branches/" + working_branch,
                    "--jq", ".commit.sha"], runner)
    if not ok or not SHA.fullmatch(sha):
        result["status"] = "BLOCKED_GH_SOURCE_BRANCH_READ"
        return result
    result["source_branch_sha"] = sha
    result["status"] = "CLI_READ_READY_NOT_AUTHORIZED"
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--working-branch", required=True)
    args = parser.parse_args(argv)
    try:
        result = inspect_cli_host(source=args.source,
                                  working_branch=args.working_branch)
    except StageBlocked as exc:
        result = {"status": "BLOCKED_INVALID_INPUT",
                  "authorization": "NOT_APPROVED_NO_WRITES",
                  "fork_create_permission": "NOT_TESTED_NO_WRITES",
                  "reason": str(exc)}
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "CLI_READ_READY_NOT_AUTHORIZED" else 2


if __name__ == "__main__":
    sys.exit(main())
