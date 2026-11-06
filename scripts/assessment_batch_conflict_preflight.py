#!/usr/bin/env python3
"""Read-only GitHub-visible source-conflict preflight for one frozen five-row batch.

This is NOT atomic admission. It detects already-visible merged/open manifest
collisions, but only the separate CAS reservation step serializes new claims.
"""

import argparse
import base64
import json
import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import HTTPRedirectHandler, Request, build_opener

from assessment_candidate_batches import BatchError, validate

REPO = "opensiro/upstream"
PREFIX = "data/assessment-candidate-batches/"
FILE_PATTERN = re.compile(r"data/assessment-candidate-batches/[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}\.json\Z")
NAME_PATTERN = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")


def normalize(value):
    if not isinstance(value, str) or not NAME_PATTERN.fullmatch(value):
        raise BatchError("Invalid source identity in collision preflight")
    return value.casefold()


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise BatchError("BLOCKED_GITHUB_VISIBILITY: unexpected API redirect")


class GithubReader:
    """GET-only bounded REST reader. Any visibility failure is a hard stop."""

    def __init__(self, token=None):
        self.token = token
        self.opener = build_opener(_NoRedirect())

    def get(self, path):
        if not path.startswith("/repos/") or "//" in path:
            raise BatchError("Invalid GitHub API path")
        headers = {"Accept": "application/vnd.github+json",
                   "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "opensiro-batch-preflight"}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        try:
            with self.opener.open(Request("https://api.github.com" + path, headers=headers), timeout=20) as response:
                raw = response.read(3_000_001)
                if len(raw) > 3_000_000:
                    raise BatchError("BLOCKED_GITHUB_VISIBILITY: API response too large")
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise BatchError("BLOCKED_GITHUB_VISIBILITY: GitHub API unavailable (" + type(exc).__name__ + ")") from exc
        try:
            return json.loads(raw)
        except (ValueError, UnicodeDecodeError) as exc:
            raise BatchError("BLOCKED_GITHUB_VISIBILITY: malformed GitHub JSON") from exc

    def pages(self, path):
        items = []
        for number in range(1, 101):
            sep = "&" if "?" in path else "?"
            page = self.get(f"{path}{sep}per_page=100&page={number}")
            if not isinstance(page, list):
                raise BatchError("BLOCKED_GITHUB_VISIBILITY: expected GitHub page")
            items.extend(page)
            if len(page) < 100:
                return items
        raise BatchError("BLOCKED_GITHUB_VISIBILITY: unexpected pagination length")


def decode_blob(record):
    if not isinstance(record, dict) or record.get("encoding") != "base64":
        raise BatchError("BLOCKED_GITHUB_VISIBILITY: missing base64 GitHub blob")
    try:
        content = base64.b64decode(record["content"], validate=False)
        if len(content) > 512_000:
            raise BatchError("BLOCKED_GITHUB_VISIBILITY: oversized manifest")
        return json.loads(content)
    except (ValueError, TypeError, KeyError, UnicodeDecodeError) as exc:
        raise BatchError("BLOCKED_GITHUB_VISIBILITY: invalid manifest blob") from exc


def _manifest_rows(payload, source_label):
    validate(payload)
    return [(normalize(candidate["source"]), source_label, payload["batch_id"])
            for candidate in payload["candidates"]]


def _open_snapshot(reader):
    prs = reader.pages(f"/repos/{REPO}/pulls?state=open")
    snapshot = {}
    for pr in prs:
        if not isinstance(pr, dict) or type(pr.get("number")) is not int or not isinstance(pr.get("head"), dict):
            raise BatchError("BLOCKED_GITHUB_VISIBILITY: incomplete open PR inventory")
        sha = pr["head"].get("sha")
        if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise BatchError("BLOCKED_GITHUB_VISIBILITY: missing open PR head SHA")
        if pr["number"] in snapshot:
            raise BatchError("BLOCKED_GITHUB_VISIBILITY: duplicate open PR")
        snapshot[pr["number"]] = pr
    return snapshot


def preflight(manifest, index_root, reader, *, own_pr=None):
    """Prove no visible collision in one stable read window, NOT atomic admission."""
    validate(manifest, index_root)
    if len(manifest["candidates"]) != 5:
        raise BatchError("Preflight requires exactly five assessed sources")
    proposed = {normalize(x["source"]) for x in manifest["candidates"]}
    branch = reader.get(f"/repos/{REPO}/branches/main")
    main_sha = branch.get("commit", {}).get("sha") if isinstance(branch, dict) else None
    if not isinstance(main_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", main_sha):
        raise BatchError("BLOCKED_GITHUB_VISIBILITY: missing canonical main SHA")
    commit = reader.get(f"/repos/{REPO}/git/commits/{main_sha}")
    tree_sha = commit.get("tree", {}).get("sha") if isinstance(commit, dict) else None
    if not isinstance(tree_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", tree_sha):
        raise BatchError("BLOCKED_GITHUB_VISIBILITY: missing canonical tree SHA")
    tree = reader.get(f"/repos/{REPO}/git/trees/{tree_sha}?recursive=1")
    if not isinstance(tree, dict) or tree.get("truncated") is not False or not isinstance(tree.get("tree"), list):
        raise BatchError("BLOCKED_GITHUB_VISIBILITY: incomplete canonical main tree")
    merged_paths = []
    for entry in tree["tree"]:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise BatchError("BLOCKED_GITHUB_VISIBILITY: malformed canonical tree entry")
        if FILE_PATTERN.fullmatch(entry["path"]):
            if (entry.get("type") != "blob" or not isinstance(entry.get("sha"), str)
                    or not re.fullmatch(r"[0-9a-f]{40}", entry["sha"])):
                raise BatchError("BLOCKED_GITHUB_VISIBILITY: invalid canonical manifest entry")
            merged_paths.append((entry["path"], entry["sha"]))
    if len(set(path for path, _ in merged_paths)) != len(merged_paths):
        raise BatchError("BLOCKED_GITHUB_VISIBILITY: duplicate canonical paths")
    seen = []
    for path, sha in merged_paths:
        payload = decode_blob(reader.get(f"/repos/{REPO}/git/blobs/{sha}"))
        seen.extend(_manifest_rows(payload, f"main@{main_sha}:{path}"))

    prs = _open_snapshot(reader)
    active_manifest_count = 0
    own_match_count = 0
    for number, pr in sorted(prs.items()):
        files = reader.pages(f"/repos/{REPO}/pulls/{number}/files")
        paths = set()
        for file in files:
            if not isinstance(file, dict) or not isinstance(file.get("filename"), str):
                raise BatchError("BLOCKED_GITHUB_VISIBILITY: malformed open PR file")
            path = file["filename"]
            if FILE_PATTERN.fullmatch(path) and file.get("status") != "removed":
                paths.add(path)
        if not paths:
            continue
        head = pr["head"]
        owner = head.get("repo", {}).get("full_name") if isinstance(head.get("repo"), dict) else None
        if not isinstance(owner, str) or not NAME_PATTERN.fullmatch(owner):
            raise BatchError("BLOCKED_GITHUB_VISIBILITY: inaccessible source PR repository")
        for path in sorted(paths):
            api_path = f"/repos/{owner}/contents/{quote(path, safe='/')}?ref={head['sha']}"
            payload = decode_blob(reader.get(api_path))
            active_manifest_count += 1
            rows = _manifest_rows(payload, f"PR#{number}@{head['sha']}:{path}")
            if number == own_pr:
                if ({source for source, _, _ in rows}
                        != proposed or payload.get("batch_id") != manifest["batch_id"]):
                    raise BatchError("BLOCKED_GITHUB_VISIBILITY: own PR manifest differs from proposal")
                own_match_count += 1
            else:
                seen.extend(rows)
    if own_pr is not None and own_match_count != 1:
        raise BatchError("BLOCKED_GITHUB_VISIBILITY: own PR must contain exactly one matching manifest")

    # Detect changes during pagination and blob reads; still NOT an atomic lock.
    final_branch = reader.get(f"/repos/{REPO}/branches/main")
    final_sha = final_branch.get("commit", {}).get("sha") if isinstance(final_branch, dict) else None
    final_prs = _open_snapshot(reader)
    if (main_sha != final_sha or
            {n: p["head"]["sha"] for n, p in prs.items()} !=
            {n: p["head"]["sha"] for n, p in final_prs.items()}):
        raise BatchError("BLOCKED_GITHUB_VISIBILITY: repository changed during preflight")

    collisions = [{"source": source, "location": location, "batch_id": batch}
                  for source, location, batch in seen if source in proposed]
    return {
        "status": "BLOCKED_DUPLICATE_SOURCE" if collisions else "CLEAR_PREVIEW_ONLY",
        "batch_id": manifest["batch_id"], "sources": sorted(proposed),
        "main_sha": main_sha, "main_manifest_count": len(merged_paths),
        "open_pr_count": len(prs), "active_pr_manifest_count": active_manifest_count,
        "collisions": collisions, "remote_visibility_checked": True,
        "admission_attested": False, "external_writes_authorized": False,
        "limitation": "No atomic PR/main snapshot or CAS claim; recheck at admission/merge"
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--index-root", type=Path, required=True)
    parser.add_argument("--own-pr", type=int, help="If proposed in an existing open PR, exclude its own file from collision comparison")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.manifest.read_text(encoding="utf-8"))
        result = preflight(payload, args.index_root, GithubReader(os.environ.get("GITHUB_TOKEN")), own_pr=args.own_pr)
    except (BatchError, ValueError, OSError) as exc:
        parser.exit(2, f"PREFLIGHT_BLOCKED: {exc}\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "CLEAR_PREVIEW_ONLY" else 2


if __name__ == "__main__":
    sys.exit(main())
