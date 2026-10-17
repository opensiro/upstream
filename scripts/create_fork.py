#!/usr/bin/env python3
"""Dry-run or create a verified public GitHub fork; no external PR or archive."""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

DEST = "opensiro-contributions"
API = "https://api.github.com"
SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$")
ATTEMPTS = 30

class ForkError(Exception):
    pass

def slug(value):
    if not SLUG.fullmatch(value) or value.endswith("."):
        raise ForkError("Invalid GitHub owner/repository slug")
    return value

def api(method, path, *, token=None, body=None):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2026-03-10",
        "User-Agent": "opensiro-fork-lifecycle",
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    data = json.dumps(body).encode() if body is not None else None
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(API + path, data=data,
                                     headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=20) as resp:
            return resp.status, json.load(resp)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return 404, {}
        raise ForkError("GitHub API HTTP " + str(exc.code)) from None
    except (urllib.error.URLError, ValueError) as exc:
        raise ForkError("GitHub response failure: " + type(exc).__name__) from None

def verify(data, source):
    if not data.get("fork"):
        raise ForkError("Destination occupied by a non-fork")
    parent = (data.get("parent") or {}).get("full_name", "")
    if parent.casefold() != source.casefold():
        raise ForkError("Existing fork has a different parent")
    if data.get("private"):
        raise ForkError("Fork is not public")
    return {"status": "EXISTS_VERIFIED", "fork": data.get("html_url"),
            "parent": parent}

def run(source, fork_name=None, *, execute=False, all_branches=False,
        request=api, sleep=time.sleep):
    if source.count("/") != 1:
        raise ForkError("Source must be OWNER/REPOSITORY")
    owner, name = [slug(part) for part in source.split("/")]
    if owner.casefold() == DEST.casefold():
        raise ForkError("Source may not be inside destination organization")
    fork_name = slug(fork_name) if fork_name else name
    source = owner + "/" + name
    destination = DEST + "/" + fork_name
    code, upstream = request("GET", "/repos/" + source)
    if code != 200 or upstream.get("full_name", "").casefold() != source.casefold():
        raise ForkError("Public source missing or identity mismatch")
    if upstream.get("private") or upstream.get("archived") or upstream.get("disabled"):
        raise ForkError("Source must be public, active and enabled")
    if upstream.get("forking_allowed") is False:
        raise ForkError("Source forbids forking")
    license_id = (upstream.get("license") or {}).get("spdx_id") or "UNKNOWN"
    code, existing = request("GET", "/repos/" + destination)
    if code == 200:
        result = verify(existing, source)
        result["license_observed"] = license_id
        return result
    if code != 404:
        raise ForkError("Could not inspect destination")

    plan = {"status": "DRY_RUN", "source": source, "destination": destination,
            "default_branch_only": not all_branches, "license_observed": license_id}
    if not execute:
        return plan
    token = os.environ.get("UPSTREAM_FORK_TOKEN")
    if not token:
        raise ForkError("UPSTREAM_FORK_TOKEN missing")
    code, created = request(
        "POST", "/repos/" + source + "/forks", token=token,
        body={"organization": DEST, "name": fork_name,
              "default_branch_only": not all_branches})
    if code != 202:
        raise ForkError("GitHub did not accept fork creation")
    if (created.get("owner") or {}).get("login", "").casefold() != DEST.casefold():
        raise ForkError("Unexpected returned owner")
    if created.get("name", "").casefold() != fork_name.casefold():
        raise ForkError("Unexpected returned repository name")

    for n in range(ATTEMPTS):
        code, observed = request("GET", "/repos/" + destination, token=token)
        if code == 200 and observed.get("parent"):
            result = verify(observed, source)
            result["status"] = "CREATED_VERIFIED"
            result["license_observed"] = license_id
            return result
        if code == 200 and not observed.get("fork"):
            raise ForkError("Destination became a non-fork")
        if code not in (200, 404):
            raise ForkError("Cannot verify fork creation")
        if n != ATTEMPTS - 1:
            sleep(2)
    return {"status": "PENDING_VERIFICATION", "destination": destination,
            "note": "Creation accepted but parent not verified. Do not register as completed."}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--fork-name")
    p.add_argument("--execute", action="store_true")
    p.add_argument("--all-branches", action="store_true")
    args = p.parse_args()
    try:
        result = run(args.source, args.fork_name, execute=args.execute,
                     all_branches=args.all_branches)
        message = json.dumps(result, sort_keys=True)
        print(message)
        if result["status"] == "PENDING_VERIFICATION":
            print("FORK_ERROR: Creation pending independent verification", file=sys.stderr)
            return 2
        if os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf8") as f:
                f.write("### OpenSiro fork lifecycle\n\n" + message + "\n")
        return 0
    except ForkError as exc:
        print("FORK_ERROR: " + str(exc), file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
