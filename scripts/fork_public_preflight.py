#!/usr/bin/env python3
"""Public GitHub fork readiness observations only. No credentials, no POST.

A public read cannot attest organization creation permission, actor identity,
unlisted/private destination repositories, or Control Plane authorization.
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from urllib.parse import quote

from rest_fork_port import _branch, _repo, _slug, StageBlocked

DEST = "opensiro-contributions"
SHA = re.compile(r"^[0-9a-f]{40}$")
HEADERS = {"Accept": "application/vnd.github+json",
           "X-GitHub-Api-Version": "2026-03-10",
           "User-Agent": "opensiro-public-fork-readiness"}


class ReadOnlyError(Exception):
    pass


def public_get(path):
    """Uncredentialed GET to GitHub's fixed API host; never send secrets."""
    if type(path) is not str or not path.startswith("/repos/"):
        raise ReadOnlyError("Unapproved public GitHub API path")
    request = urllib.request.Request(
        "https://api.github.com" + path, headers=HEADERS, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as exc:
        return exc.code, {}
    except (urllib.error.URLError, OSError, ValueError) as exc:
        raise ReadOnlyError("Unverified GitHub network response: " +
                            type(exc).__name__) from None


def _load(get, path):
    result = get(path)
    if (type(result) is not tuple or len(result) != 2
            or type(result[0]) is not int):
        raise ReadOnlyError("Invalid public GET response")
    status, data = result
    if status in (401, 403, 429):
        raise ReadOnlyError("Public API denied or rate limited; not a 404")
    if status not in (200, 404):
        raise ReadOnlyError("Unexpected public API status " + str(status))
    if status == 200 and type(data) is not dict:
        raise ReadOnlyError("Malformed public API data")
    return status, data


def inspect_public_fork(*, source, fork_name, working_branch,
                        expected_sha=None, expected_license=None,
                        all_branches=False, get=public_get):
    """Return evidence with NO_WRITES status. Never return an approval token."""
    source = _repo(source)
    fork_name = _slug(fork_name)
    working_branch = _branch(working_branch)
    if source.split("/")[0].casefold() == DEST:
        raise ReadOnlyError("Forking from destination organization prohibited")
    if type(all_branches) is not bool:
        raise ReadOnlyError("All-branches option must be boolean")
    if expected_sha is not None and (type(expected_sha) is not str
                                     or not SHA.fullmatch(expected_sha)):
        raise ReadOnlyError("Expected source SHA must be exact 40-hex")
    if expected_license is not None and (type(expected_license) is not str
                                          or not re.fullmatch(
                                              r"[A-Za-z0-9.+-]{1,50}",
                                              expected_license)):
        raise ReadOnlyError("Invalid expected SPDX identifier")

    destination = DEST + "/" + fork_name
    outcome = {
        "status": "BLOCKED_SOURCE",
        "authorization": "NOT_APPROVED_NO_WRITES",
        "fork_create_permission": "NOT_TESTED_NO_CREDENTIALS",
        "destination_absence_proof": "PUBLIC_READ_ONLY",
        "source": source,
        "destination": destination,
        "working_branch": working_branch,
        "expected_source_sha": expected_sha,
        "expected_license": expected_license,
        "default_branch_only": not all_branches,
        "observed_source_sha": None,
        "observed_license": None,
        "reasons": [],
        "notes": [
            "Public API observations do not prove owner authorization, "
            "destination writability or GitHub App source installation.",
            "No POST or privileged workflow is available in this preflight.",
        ],
    }
    source_status, upstream = _load(get, "/repos/" + source)
    if source_status == 404:
        outcome["reasons"].append("Source repository is not publicly observable")
        return outcome
    if (upstream.get("full_name", "").casefold() != source.casefold()
            or upstream.get("private") is not False
            or upstream.get("archived") is not False
            or upstream.get("disabled") is not False
            or upstream.get("forking_allowed") is False):
        outcome["reasons"].append("Public source identity/status is unsuitable")
        return outcome

    license_id = (upstream.get("license") or {}).get("spdx_id")
    outcome["observed_license"] = license_id
    outcome["default_branch"] = upstream.get("default_branch")
    if not isinstance(upstream.get("default_branch"), str):
        outcome["reasons"].append("Source default branch missing")
    if expected_license is None:
        outcome["reasons"].append("Expected SPDX has not been independently reviewed")
    elif license_id != expected_license:
        outcome["reasons"].append("Source SPDX observation differs from expected")
    if not all_branches and working_branch != upstream.get("default_branch"):
        outcome["reasons"].append(
            "Default-only fork cannot preserve required nondefault branch")

    status, branch = _load(get, "/repos/" + source + "/branches/" +
                          quote(working_branch, safe=""))
    if status != 200:
        outcome["reasons"].append("Required source branch not publicly observable")
    else:
        observed_sha = (branch.get("commit") or {}).get("sha")
        if type(observed_sha) is not str or not SHA.fullmatch(observed_sha):
            outcome["reasons"].append("Required source branch SHA malformed")
        else:
            outcome["observed_source_sha"] = observed_sha
            if expected_sha is None:
                outcome["reasons"].append("Current SHA is observed but not approved/pinned")
            elif expected_sha != observed_sha:
                outcome["reasons"].append("Required source branch SHA drift")

    target_status, target = _load(get, "/repos/" + destination)
    if target_status == 200:
        outcome["observed_destination"] = {
            "full_name": target.get("full_name"),
            "fork": target.get("fork"),
            "parent": (target.get("parent") or {}).get("full_name"),
        }
        outcome["reasons"].append("Destination repository is already publicly visible")
    else:
        outcome["observed_destination"] = "NOT_PUBLICLY_VISIBLE"
        outcome["notes"].append(
            "A public 404 cannot exclude hidden/private destination collision")

    if outcome["reasons"]:
        outcome["status"] = "BLOCKED_PUBLIC_PREFLIGHT"
    else:
        outcome["status"] = "PUBLIC_PREFLIGHT_OK_NOT_AUTHORIZED"
    return outcome


def main(argv=None, *, get=public_get):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--fork-name", required=True)
    parser.add_argument("--working-branch", required=True)
    parser.add_argument("--expected-sha")
    parser.add_argument("--expected-license")
    parser.add_argument("--all-branches", action="store_true")
    args = parser.parse_args(argv)
    try:
        outcome = inspect_public_fork(
            source=args.source, fork_name=args.fork_name,
            working_branch=args.working_branch, expected_sha=args.expected_sha,
            expected_license=args.expected_license, all_branches=args.all_branches,
            get=get)
    except (ReadOnlyError, StageBlocked) as exc:
        outcome = {"status": "BLOCKED_PUBLIC_PREFLIGHT",
                   "authorization": "NOT_APPROVED_NO_WRITES",
                   "fork_create_permission": "NOT_TESTED_NO_CREDENTIALS",
                   "reasons": [str(exc)]}
    print(json.dumps(outcome, sort_keys=True))
    return 0 if outcome["status"] == "PUBLIC_PREFLIGHT_OK_NOT_AUTHORIZED" else 2


if __name__ == "__main__":
    sys.exit(main())
