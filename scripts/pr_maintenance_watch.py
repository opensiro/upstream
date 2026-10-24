#!/usr/bin/env python3
"""Upstream PR Maintenance: bounded GitHub watcher with issue-owned checkpoint.

No external GitHub writes, no model/agent runs, no automatic patch/merge.
The only writes are comments in the configured opensiro/upstream inbox issue.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from datetime import datetime, timezone
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
import zlib

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "data/pr-maintenance/targets.json"
INBOX_REPO = "opensiro/upstream"
INBOX_NUMBER = 125
CHECKPOINT_PREFIX = "<!-- opensiro-pr-maintenance-checkpoint-v1:"
ALERT_PREFIX = "<!-- opensiro-pr-maintenance-alert-v1:"
UA = "opensiro-pr-maintenance/1"
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
MAX_PAGES = 10
FAILURES = {"failure", "timed_out", "action_required", "cancelled"}
BOT_SUFFIX = "[bot]"


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def validate_targets(path=TARGETS):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("targets"), list):
        raise ValueError("Unknown watchlist schema")
    if data.get("inbox_issue") != f"https://github.com/{INBOX_REPO}/issues/{INBOX_NUMBER}":
        raise ValueError("Unexpected inbox identity")
    seen = set()
    for item in data["targets"]:
        if set(item) != {"repository", "number", "url"}:
            raise ValueError(f"Unexpected target keys: {item}")
        repo, number = item["repository"], item["number"]
        if not isinstance(repo, str) or not REPO.fullmatch(repo):
            raise ValueError("Invalid repository")
        if type(number) is not int or number <= 0:
            raise ValueError("Invalid pull number")
        if item["url"] != f"https://github.com/{repo}/pull/{number}":
            raise ValueError("PR URL does not match its structured identity")
        if item["url"] in seen:
            raise ValueError("Duplicate target")
        seen.add(item["url"])
    if not data["targets"]:
        raise ValueError("Empty target set")
    return data


class Github:
    def __init__(self, token: str):
        if not token:
            raise ValueError("GITHUB_TOKEN required (fail closed)")
        self.token = token

    def request(self, path, method="GET", payload=None):
        if not path.startswith("/") or "//" in path or ".." in path:
            raise ValueError("Unsafe API path")
        url = "https://api.github.com" + path
        body = json.dumps(payload).encode() if payload is not None else None
        headers = {"Accept": "application/vnd.github+json",
                   "User-Agent": UA,
                   "X-GitHub-Api-Version": "2022-11-28",
                   "Authorization": f"Bearer {self.token}"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        with urlopen(Request(url, data=body, method=method, headers=headers), timeout=25) as response:
            return json.load(response), response.headers.get("Link", "")

    def get(self, path):
        return self.request(path)[0]

    def pages(self, path):
        output = []
        for _ in range(MAX_PAGES):
            # Complete pagination is mandatory. Silent truncation could lose review events.
            data, links = self.request(path)
            if not isinstance(data, list):
                raise ValueError(f"Expected array from {path}")
            output.extend(data)
            next_link = re.search(r'<(https://api\.github\.com/[^>]+)>;\s*rel="next"', links)
            if not next_link:
                return output
            next_path = urlparse(next_link.group(1)).path
            if urlparse(next_link.group(1)).query:
                next_path += "?" + urlparse(next_link.group(1)).query
            path = next_path
        raise ValueError("GitHub pagination exceeded guard; do not truncate events")


def compact_comment(x):
    return {"id": x["id"], "author": x["user"]["login"],
            "url": x["html_url"], "updated_at": x.get("updated_at"),
            "created_at": x.get("created_at")}


def compact_review(x):
    return {"id": x["id"], "author": x["user"]["login"], "state": x["state"],
            "url": x.get("html_url"), "submitted_at": x.get("submitted_at")}


def snapshot_one(api, target):
    repo, num = target["repository"], target["number"]
    prefix = f"/repos/{repo}"
    pr = api.get(f"{prefix}/pulls/{num}")
    if pr.get("html_url") != target["url"] or pr.get("number") != num:
        raise ValueError("PR source identity mismatch")
    if pr.get("state") not in ("open", "closed") or type(pr.get("draft")) is not bool:
        raise ValueError("Missing/unknown PR lifecycle")
    if pr.get("head", {}).get("sha") is None or pr.get("base", {}).get("sha") is None:
        raise ValueError("Incomplete GitHub PR refs")
    head = pr["head"]["sha"]
    comments = api.pages(f"{prefix}/issues/{num}/comments?per_page=100")
    reviews = api.pages(f"{prefix}/pulls/{num}/reviews?per_page=100")
    inline = api.pages(f"{prefix}/pulls/{num}/comments?per_page=100")
    checks_data = api.get(f"{prefix}/commits/{head}/check-runs?per_page=100")
    if checks_data.get("total_count", 0) > len(checks_data.get("check_runs", [])):
        # GitHub exposes >100 check-runs only through the paginated /check-runs endpoint.
        checks = []
        for page in range(1, 11):
            batch = api.get(f"{prefix}/commits/{head}/check-runs?per_page=100&page={page}")
            checks.extend(batch["check_runs"])
            if len(batch["check_runs"]) < 100:
                break
        if len(checks) != checks_data["total_count"]:
            raise ValueError("Truncated checks: refusing silent partial snapshot")
    else:
        checks = checks_data["check_runs"]
    status_data = api.get(f"{prefix}/commits/{head}/status")
    if status_data.get("state") not in {"pending", "success", "failure", "error"}:
        raise ValueError("Unexpected legacy commit status")
    return {
        "url": target["url"], "repository": repo, "number": num,
        "state": pr["state"], "draft": pr["draft"],
        "merged_at": pr.get("merged_at"), "head": head, "base": pr["base"]["sha"],
        "updated_at": pr.get("updated_at"),
        "comments": sorted([compact_comment(c) for c in comments], key=lambda c: c["id"]),
        "reviews": sorted([compact_review(v) for v in reviews], key=lambda v: v["id"]),
        "inline": sorted([compact_comment(c) for c in inline], key=lambda c: c["id"]),
        "checks": sorted([{"id": c["id"], "name": c["name"], "status": c["status"],
                            "conclusion": c.get("conclusion"), "url": c.get("html_url"),
                            "completed_at": c.get("completed_at")}
                           for c in checks], key=lambda c: c["id"]),
        "legacy_status": status_data["state"],
    }


def human(name, contributor="xLagerFeuer"):
    return isinstance(name, str) and name.lower() != contributor.lower() and not name.endswith(BOT_SUFFIX)


def classify(previous, current, contributor="xLagerFeuer"):
    """Return only meaningful transitions. The first run establishes a baseline."""
    if previous is None:
        return []
    events = []
    old = previous.get("prs", {})
    for url, pr in current["prs"].items():
        before = old.get(url)
        if before is None:
            events.append((url, "NEW_TRACKED_PR", "info", url))
            continue

        def emit(kind, level, link, fingerprint=""):
            events.append((url, kind, level, link or url, fingerprint))

        was_merged = bool(before.get("merged_at"))
        is_merged = bool(pr.get("merged_at"))
        if not was_merged and is_merged:
            emit("MERGED", "info", url)
        elif before.get("state") != pr["state"]:
            emit("CLOSED_UNMERGED" if pr["state"] == "closed" else "REOPENED", "info", url)
        if before.get("draft") != pr["draft"]:
            emit("DRAFT_CHANGED", "info", url)
        if before.get("head") != pr["head"]:
            emit("HEAD_UPDATED", "info", url)
        if before.get("base") != pr["base"]:
            emit("BASE_UPDATED", "info", url)

        for field, kind, edited_kind in (("comments", "NEW_MAINTAINER_COMMENT", "EDITED_MAINTAINER_COMMENT"),
                                         ("inline", "NEW_REVIEW_COMMENT", "EDITED_REVIEW_COMMENT")):
            previous_by_id = {x["id"]: x for x in before.get(field, [])}
            for item in pr[field]:
                if not human(item["author"], contributor):
                    continue
                past = previous_by_id.get(item["id"])
                if past is None:
                    emit(kind, "action_required", item["url"], str(item["id"]))
                elif (past.get("updated_at") and item.get("updated_at")
                      and past["updated_at"] != item["updated_at"]):
                    # An upstream maintainer can revise an existing request.
                    # Keep only public metadata, never comment bodies.
                    emit(edited_kind, "action_required", item["url"],
                         f"{item['id']}:{item['updated_at']}")

        old_reviews = {x["id"]: x for x in before.get("reviews", [])}
        for item in pr["reviews"]:
            past = old_reviews.get(item["id"])
            if human(item["author"], contributor) and (past is None or past.get("state") != item["state"]):
                state = item["state"]
                if state == "CHANGES_REQUESTED":
                    emit("CHANGES_REQUESTED", "action_required", item.get("url"), f"{item['id']}:{item.get('submitted_at')}")
                elif state == "APPROVED":
                    emit("APPROVED", "info", item.get("url"))
                elif state == "DISMISSED":
                    emit("REVIEW_DISMISSED", "info", item.get("url"))
                elif state == "COMMENTED":
                    emit("REVIEW_COMMENTED", "action_required", item.get("url"), f"{item['id']}:{item.get('submitted_at')}")

        old_checks = {(x["id"], x.get("conclusion")) for x in before.get("checks", [])}
        # Check results can change on same head without a new PR event.
        for x in pr.get("checks", []):
            if x.get("conclusion") in FAILURES and (x["id"], x["conclusion"]) not in old_checks:
                emit("CI_FAILED", "action_required", x.get("url"), f"{x['id']}:{x.get('completed_at')}")
        if pr["legacy_status"] in {"failure", "error"} and pr["legacy_status"] != before.get("legacy_status"):
            emit("CI_LEGACY_FAILED", "action_required", url, pr["head"] + ":" + pr["legacy_status"])

    return [{"pr": u, "kind": k, "level": l, "url": link,
             "key": hashlib.sha256(json.dumps([u, k, link, fingerprint], sort_keys=True).encode()).hexdigest()[:20]}
            for u, k, l, link, fingerprint in events]


def encode_checkpoint(snapshot):
    packed = zlib.compress(json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode(), 9)
    return CHECKPOINT_PREFIX + base64.urlsafe_b64encode(packed).decode() + " -->"


def decode_checkpoint(body):
    match = re.search(re.escape(CHECKPOINT_PREFIX) + r"([A-Za-z0-9_\-=]+) -->", body)
    if not match:
        raise ValueError("Unrecognized checkpoint format")
    blob = base64.urlsafe_b64decode(match.group(1))
    if len(blob) > 400_000:
        raise ValueError("Checkpoint too large")
    decomp = zlib.decompressobj()
    decoded = decomp.decompress(blob, 400_001)
    if not decomp.eof or len(decoded) > 400_000 or decomp.unconsumed_tail:
        raise ValueError("Oversized/incomplete checkpoint")
    data = json.loads(decoded)
    if data.get("schema_version") != 1 or not isinstance(data.get("prs"), dict):
        raise ValueError("Corrupt checkpoint schema")
    return data


def inbox_state(api):
    issue = api.get(f"/repos/{INBOX_REPO}/issues/{INBOX_NUMBER}")
    if issue.get("state") != "open":
        raise ValueError("Monitoring inbox is not open")
    comments = api.pages(f"/repos/{INBOX_REPO}/issues/{INBOX_NUMBER}/comments?per_page=100")
    markers = [c for c in comments if CHECKPOINT_PREFIX in c.get("body", "")
               and c.get("user", {}).get("login") == "github-actions[bot]"]
    if len(markers) > 1:
        raise ValueError("Multiple machine checkpoints: manual review required")
    state = decode_checkpoint(markers[0]["body"]) if markers else None
    posted = {key for c in comments for key in re.findall(re.escape(ALERT_PREFIX) + r"([a-f0-9]{64}) -->", c.get("body", ""))
              if c.get("user", {}).get("login") == "github-actions[bot]"}
    return (markers[0]["id"] if markers else None), state, posted


def render(events, scanned, initial=False):
    lines = [f"### Upstream PR Maintenance — {now()}", "",
             f"Scanned **{scanned}** pinned external PRs. "
             + ("Initial baseline captured; historical activity was not reported as new." if initial else
                f"Found **{len(events)}** new transitions."),
             ""]
    if events:
        for e in events:
            lines.append(f"- **{e['kind']}** ({e['level']}): {e['pr']} — {e['url']}")
    else:
        lines.append("No new actionable review/CI change.")
    lines += ["", "Automated public GitHub readback, no source mutations or external comments. "
              "Review/repair must respect the per-PR contributor and authority gates."]
    return "\n".join(lines)


def run(api, targets_path=TARGETS, *, probe_only=False):
    data = validate_targets(targets_path)
    checkpoint_id, previous, posted = inbox_state(api)
    current = {"schema_version": 1, "observed_at": now(), "prs": {}}
    for t in data["targets"]:
        current["prs"][t["url"]] = snapshot_one(api, t)
    if previous is not None and set(previous["prs"]) != set(current["prs"]):
        # Explicit watchlist edits are a separate reviewed decision. Do not lose
        # previously tracked PRs or claim lifecycle outcomes via implicit removal.
        raise ValueError("Watchlist changed; baseline migration required")
    events = classify(previous, current)
    notifiable = [e for e in events if e["level"] == "action_required" or
                  e["kind"] in {"MERGED", "CLOSED_UNMERGED", "APPROVED", "REOPENED"}]
    if probe_only:
        print(render(events, len(data["targets"]), initial=previous is None))
        print("PROBE_ONLY: no GitHub writes")
        return events
    if previous is not None and notifiable:
        unique = sorted({e["key"] for e in notifiable})
        alert_id = hashlib.sha256(" ".join(unique).encode()).hexdigest()
        if alert_id not in posted:
            summary = render(notifiable, len(data["targets"]))
            api.request(f"/repos/{INBOX_REPO}/issues/{INBOX_NUMBER}/comments",
                        method="POST", payload={"body": ALERT_PREFIX + alert_id + " -->\n" + summary})
    # Do not edit the inbox checkpoint when no relevant PR state changed.
    if previous is not None and current["prs"] == previous["prs"]:
        print(render(events, len(data["targets"])))
        return events
    # Only persist the next checkpoint after any required notification succeeds.
    body = encode_checkpoint(current) + "\n\nMachine-only deduplication checkpoint. "
    body += "PR comments and reviews remain authoritative on their external GitHub URLs."
    path = f"/repos/{INBOX_REPO}/issues/comments/{checkpoint_id}" if checkpoint_id else f"/repos/{INBOX_REPO}/issues/{INBOX_NUMBER}/comments"
    api.request(path, method="PATCH" if checkpoint_id else "POST", payload={"body": body})
    print(render(events, len(data["targets"]), initial=previous is None))
    return events


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--targets", type=Path, default=TARGETS)
    ap.add_argument("--validate-only", action="store_true")
    ap.add_argument("--probe-only", action="store_true", help="Live GET-only scan, no checkpoint writes")
    args = ap.parse_args()
    if args.validate_only:
        d = validate_targets(args.targets)
        print(f"Validated {len(d['targets'])} external PR targets")
        return
    run(Github(os.environ.get("GITHUB_TOKEN", "")), args.targets, probe_only=args.probe_only)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, RuntimeError) as e:
        print(f"FAIL_CLOSED: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
