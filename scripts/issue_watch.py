#!/usr/bin/env python3
"""Fork-local, source-backed external issue decision watch (opt-in, no outbound PRs).

A read-only scan never claims durable alert delivery. --apply persists a verified
meaningful change in the owning fork's opensiro/meta through a non-force Git
fast-forward update. GitHub issue state/comments/labels remain source authority.
"""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from aggregate import APIError, GitHub, api, check_contribution, check_state, read_file

ISSUE_URL = re.compile(r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/issues/([1-9]\d*)$")
ANCHOR_URL = re.compile(r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/issues/([1-9]\d*)#issuecomment-([1-9]\d*)$")
FORK = re.compile(r"^opensiro-contributions/[A-Za-z0-9_.-]+$")
SHA = re.compile(r"^[a-f0-9]{40}$")
ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,127}$")
DECISION_ROLES = {"OWNER", "MEMBER", "COLLABORATOR"}
REJECT = re.compile(r"\b(?:not accepting (?:new )?(?:pull requests?|prs?)|"
                    r"(?:we |i )?(?:will not|won't) (?:accept|implement)|"
                    r"not planned|declined|rejected)\b", re.I)
APPROVE = re.compile(r"\b(?:approved for (?:implementation|a pr)|"
                     r"(?:please|feel free to) (?:open|submit) (?:a )?(?:pull request|pr)|"
                     r"we will accept (?:a )?(?:pull request|pr))\b", re.I)
STATUSES = {"UNCHANGED", "NEW_ACTIVITY_NEEDS_REVIEW", "DECISION_CONFIRMED", "UNKNOWN"}


def utc(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("expected UTC ISO timestamp with trailing Z")
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as error:
        raise ValueError("invalid UTC timestamp") from error


def validate_watch(item, original):
    if item is None:
        return None
    if not isinstance(item, dict) or item.get("schema_version") != 1:
        raise ValueError("invalid issue_watch schema")
    url, anchor = item.get("issue_url"), item.get("anchor_comment_url")
    m, a = ISSUE_URL.fullmatch(url or ""), ANCHOR_URL.fullmatch(anchor or "")
    if not m or not a or m.group(0).split("/")[3:5] != a.group(0).split("/")[3:5]:
        raise ValueError("invalid original issue or anchor URL")
    if tuple(m.groups()) != tuple(a.groups()[:3]) or (m.group(1)+"/"+m.group(2)).lower() != original.lower():
        raise ValueError("issue watch original source and anchor identity mismatch")
    baseline = item.get("baseline")
    if not isinstance(baseline, dict) or baseline.get("state") not in {"open", "closed"}:
        raise ValueError("issue watch baseline state missing")
    labels = baseline.get("labels")
    if (not isinstance(labels, list) or any(not isinstance(x, str) or not x for x in labels)
            or labels != sorted(set(labels))):
        raise ValueError("baseline labels must be sorted, unique strings")
    cursor = baseline.get("last_comment_id")
    if type(cursor) is not int or cursor < int(a.group(4)):
        raise ValueError("baseline cursor must include anchor comment")
    utc(baseline.get("observed_at"))
    questions = item.get("expected_decisions")
    if not isinstance(questions, list) or not questions or any(
            not isinstance(q, str) or not (12 <= len(q) <= 500) for q in questions):
        raise ValueError("issue watch requires bounded expected decision questions")
    relevant = item.get("relevant_labels")
    if not isinstance(relevant, list) or any(not isinstance(s, str) or not s for s in relevant):
        raise ValueError("issue watch needs explicit relevant label names")
    if len(relevant) != len(set(relevant)):
        raise ValueError("duplicate relevant labels")
    if item.get("last_alert_fingerprint") is not None and not re.fullmatch(
            r"[a-f0-9]{64}", str(item["last_alert_fingerprint"])):
        raise ValueError("invalid alert fingerprint")
    return m.group(1) + "/" + m.group(2), int(m.group(3)), int(a.group(4))


def load_target(client, fork, ident):
    if not FORK.fullmatch(fork) or not ID.fullmatch(ident):
        raise ValueError("invalid verified fork or stable contribution id")
    details = client.get(api(fork, ""))
    if details.get("fork") is not True or not isinstance(details.get("parent"), dict):
        raise ValueError("not a verified upstream fork")
    original = details["parent"].get("full_name")
    if not isinstance(original, str):
        raise ValueError("missing original repository")
    ref = client.get(api(fork, "git/ref/heads/opensiro/meta"))
    head = ref.get("object", {}).get("sha")
    if not isinstance(head, str) or not SHA.fullmatch(head):
        raise ValueError("unreadable fork-local meta SHA")
    state, _ = read_file(client, fork, ".opensiro/state.json", head)
    check_state(state, fork, original)
    path = ".opensiro/contributions/" + ident + ".json"
    record, _ = read_file(client, fork, path, head)
    check_contribution(record, path, original)
    validate_watch(record.get("issue_watch"), original)
    return {"fork": fork, "id": ident, "original": original, "head": head,
            "state": state, "record": record, "path": path}


def readonly_descriptor_target(target, descriptor):
    """Transient source-verified watch for a paused fork; no metadata mutation.

    The descriptor is a read-only bootstrap observation, not a second ledger.
    Its use never constitutes RESUME, nor an authorized event write.
    """
    if target["record"].get("issue_watch") is not None:
        raise ValueError("registered fork-local issue watch must not be overridden")
    validate_watch(descriptor, target["original"])
    view = copy.deepcopy(target)
    view["record"]["issue_watch"] = copy.deepcopy(descriptor)
    return view


def read_issue(client, original, issue_number, anchor_id):
    path = api(original, "issues/" + str(issue_number))
    issue = client.get(path)
    expected = "https://github.com/" + original + "/issues/" + str(issue_number)
    if (not isinstance(issue, dict) or issue.get("html_url", "").lower() != expected.lower()
            or issue.get("number") != issue_number or "pull_request" in issue
            or issue.get("state") not in ("open", "closed")
            or not isinstance(issue.get("labels"), list)):
        raise ValueError("issue readback does not match source identity")
    labels = sorted(set(lbl["name"] for lbl in issue["labels"] if isinstance(lbl, dict)
                        and isinstance(lbl.get("name"), str)))
    if len(labels) != len(issue["labels"]):
        raise ValueError("invalid issue labels response")
    comments = []
    for page in range(1, 51):
        data = client.get(path + "/comments?per_page=100&page=" + str(page))
        if not isinstance(data, list):
            raise ValueError("invalid issue comments page")
        for comment in data:
            if (not isinstance(comment, dict) or type(comment.get("id")) is not int
                    or not str(comment.get("html_url", "")).lower().startswith(expected.lower() + "#issuecomment-")
                    or str(comment["id"]) != str(comment["html_url"]).split("#issuecomment-")[-1]
                    or not isinstance(comment.get("user"), dict)):
                raise ValueError("untrusted issue comment source identity")
            comments.append(comment)
        if len(data) < 100:
            break
    else:
        raise ValueError("issue comment pagination exceeds safety bound")
    if len(set(c["id"] for c in comments)) != len(comments):
        raise ValueError("duplicate source comment ids")
    if not any(c["id"] == anchor_id for c in comments):
        raise ValueError("verified issue anchor comment is missing")
    return {"url": expected, "state": issue["state"], "labels": labels,
            "comments": sorted(comments, key=lambda c: c["id"])}


def observe(client, target, *, now=None):
    watch = target["record"].get("issue_watch")
    if not watch:
        raise ValueError("contribution has no source-linked issue watch")
    original, issue_number, anchor = validate_watch(watch, target["original"])
    now = now or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    utc(now)
    try:
        live = read_issue(client, original, issue_number, anchor)
    except (APIError, ValueError, KeyError, TypeError) as exc:
        return {"status": "UNKNOWN", "checked_at": now, "issue_url": watch["issue_url"],
                "reason": type(exc).__name__, "source_error": str(exc)[:280],
                "alert": False, "applied": False}
    baseline = watch["baseline"]
    cursor = baseline["last_comment_id"]
    new = [c for c in live["comments"] if c["id"] > cursor]
    edited = [c for c in live["comments"] if c["id"] <= cursor and c["id"] != anchor
              and c.get("updated_at") and utc(c["updated_at"]) > utc(baseline["observed_at"])]
    fresh = sorted(new + edited, key=lambda c: c["id"])
    human = [c for c in fresh if c.get("user", {}).get("type") != "Bot"
             and not c.get("user", {}).get("login", "").endswith("[bot]")]
    maintainer = [c for c in human if c.get("author_association") in DECISION_ROLES]
    decisions = []
    for c in maintainer:
        body = c.get("body") or ""
        verdict = ("REJECTED" if REJECT.search(body) else
                   "APPROVED_FOR_DISCUSSION" if APPROVE.search(body) else None)
        if verdict:
            decisions.append({"url": c["html_url"], "verdict": verdict,
                              "author": c["user"]["login"], "id": c["id"]})
    old_labels, new_labels = set(baseline["labels"]), set(live["labels"])
    relevant = set(watch["relevant_labels"])
    changed_labels = sorted((old_labels ^ new_labels) & relevant)
    state_changed = live["state"] != baseline["state"]
    meaningful = bool(human or changed_labels or state_changed)
    status = ("DECISION_CONFIRMED" if decisions else
              "NEW_ACTIVITY_NEEDS_REVIEW" if meaningful else "UNCHANGED")
    links = [d["url"] for d in decisions]
    if status == "NEW_ACTIVITY_NEEDS_REVIEW":
        links += [c["html_url"] for c in human]
    if changed_labels or state_changed:
        links.append(live["url"])
    links = sorted(set(links))
    change = {"before_state": baseline["state"], "after_state": live["state"],
              "changed_relevant_labels": changed_labels,
              "human_comment_ids": sorted(c["id"] for c in human),
              "decisions": decisions, "source_links": links}
    material = {"contribution_id": target["id"], "issue": live["url"],
                "baseline": {"state": baseline["state"], "labels": baseline["labels"],
                             "last_comment_id": cursor},
                "after": {"state": live["state"], "labels": live["labels"],
                          "last_comment_id": max((c["id"] for c in live["comments"]), default=cursor)},
                "change": change}
    signature = hashlib.sha256(json.dumps(material, sort_keys=True,
                                          separators=(",", ":")).encode()).hexdigest()
    return {"status": status, "checked_at": now, "issue_url": live["url"],
            "source_links": links, "change": change,
            "fingerprint": signature, "alert": meaningful, "applied": False,
            "current": {"state": live["state"], "labels": live["labels"],
                        "last_comment_id": material["after"]["last_comment_id"],
                        "observed_at": now}}


class GitHubWriter(GitHub):
    """Git-data-only, non-force writes to the verified fork; no original issue/PR writes."""

    def __init__(self, token, fork):
        super().__init__(token)
        if not token or not FORK.fullmatch(fork):
            raise ValueError("explicit fork-write credential and verified fork required")
        self.fork = fork

    def write(self, method, suffix, payload):
        if method == "POST" and suffix in ("git/trees", "git/commits"):
            pass
        elif method == "PATCH" and suffix == "git/refs/heads/opensiro/meta":
            if payload.get("force") is not False:
                raise ValueError("ref write must be non-force")
        else:
            raise ValueError("issue watch forbids this GitHub write endpoint")
        url = api(self.fork, suffix)
        body = json.dumps(payload).encode()
        request = Request("https://api.github.com" + url, data=body, method=method,
                          headers={"Authorization": "Bearer " + self.token,
                                   "Accept": "application/vnd.github+json",
                                   "Content-Type": "application/json",
                                   "User-Agent": "opensiro-fork-local-issue-watch",
                                   "X-GitHub-Api-Version": "2022-11-28"})
        try:
            with urlopen(request, timeout=25) as response:
                return json.loads(response.read().decode())
        except HTTPError as error:
            raise APIError(error.code, "GitHub rejected fork-local write HTTP " + str(error.code)) from error
        except (URLError, OSError, ValueError) as error:
            raise APIError(0, "Fork-local write unavailable") from error


def apply_change(client, target, observation, *, actor):
    if observation["status"] not in ("DECISION_CONFIRMED", "NEW_ACTIVITY_NEEDS_REVIEW"):
        raise ValueError("no meaningful verified source change to persist")
    if target["state"]["owner_control"] != "ALLOW":
        raise PermissionError("fork owner PAUSE/STOP disallows meta writes")
    if target["state"]["attention"] not in ("ACTIVE", "WATCHING"):
        raise PermissionError("fork DORMANT/ARCHIVED; no automatic effectful watch")
    if not actor or len(actor) > 100:
        raise ValueError("attributed actor identity required")
    old = target["head"]
    # Double-check ref immediately before preparing a commit; a non-force
    # update will reject a later concurrent state/event change.
    remote = client.get(api(target["fork"], "git/ref/heads/opensiro/meta"))
    if remote.get("object", {}).get("sha") != old:
        raise RuntimeError("CAS_PRECONDITION_FAILED: opensiro/meta moved")
    record = copy.deepcopy(target["record"])
    state = copy.deepcopy(target["state"])
    if record["issue_watch"].get("last_alert_fingerprint") == observation["fingerprint"]:
        raise ValueError("already recorded source change")
    stamp = utc(observation["checked_at"]).strftime("%Y%m%dT%H%M%SZ")
    event_id = f"{stamp}--issue-watch-{target['id']}-{observation['fingerprint'][:12]}"
    event = {"schema_version": 1, "id": event_id, "recorded_at": observation["checked_at"],
             "actor": actor, "kind": "OBSERVATION", "contribution_id": target["id"],
             "decision": observation["status"], "evidence_urls": observation["source_links"],
             "source_issue": observation["issue_url"], "source_change": observation["change"],
             "baseline_meta_sha": old,
             "next_action": "Review the source-linked issue decision; no external PR is authorized."}
    watch = record["issue_watch"]
    watch["baseline"] = observation["current"]
    watch["last_alert_fingerprint"] = observation["fingerprint"]
    watch["last_observation"] = {"status": observation["status"], "checked_at": observation["checked_at"],
                                  "evidence_urls": observation["source_links"]}
    record["last_event_id"] = event_id
    record["next_action"] = ("AWAITING_MAINTAINER_DECISION: source-linked issue change " +
                             observation["status"] + " observed; review " + observation["issue_url"] +
                             ". No external PR without separate owner consent.")
    state["last_event_id"] = event_id
    state["updated_at"] = observation["checked_at"]
    paths = {
        ".opensiro/state.json": state,
        target["path"]: record,
        ".opensiro/events/" + event_id + ".json": event,
    }
    # Exact base tree can only come from the pinned meta commit.
    commit = client.get(api(target["fork"], "git/commits/" + old))
    tree_sha = commit.get("tree", {}).get("sha")
    if not isinstance(tree_sha, str) or not SHA.fullmatch(tree_sha):
        raise ValueError("unverified pinned parent tree SHA")
    tree = client.write("POST", "git/trees",
                        {"base_tree": tree_sha,
                         "tree": [{"path": path, "mode": "100644", "type": "blob",
                                   "content": json.dumps(value, indent=2) + "\n"}
                                  for path, value in sorted(paths.items())]})
    new_tree = tree.get("sha")
    if not isinstance(new_tree, str) or not SHA.fullmatch(new_tree):
        raise ValueError("invalid GitHub-created tree")
    made = client.write("POST", "git/commits",
                        {"message": "meta(issue-watch): record verified original issue change",
                         "tree": new_tree, "parents": [old]})
    new_sha = made.get("sha")
    if not isinstance(new_sha, str) or not SHA.fullmatch(new_sha):
        raise ValueError("invalid GitHub-created commit")
    # force=false is the concurrency fence: if another write advanced meta,
    # our one-parent commit cannot fast-forward it, so GitHub rejects the push.
    client.write("PATCH", "git/refs/heads/opensiro/meta",
                 {"sha": new_sha, "force": False})
    check = client.get(api(target["fork"], "git/ref/heads/opensiro/meta"))
    if check.get("object", {}).get("sha") != new_sha:
        raise RuntimeError("post-write readback failed; do not claim delivered notification")
    saved, _ = read_file(client, target["fork"], target["path"], new_sha)
    if saved.get("last_event_id") != event_id or saved.get("issue_watch", {}).get("last_alert_fingerprint") != observation["fingerprint"]:
        raise RuntimeError("contribution readback does not match published event")
    return {"status": observation["status"], "alert": True, "applied": True,
            "meta_commit": new_sha, "event_id": event_id,
            "source_links": observation["source_links"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fork", required=True)
    parser.add_argument("--contribution", required=True)
    parser.add_argument("--apply", action="store_true", help="Persist confirmed change on fork-local metadata branch")
    parser.add_argument("--allow-fork-write", action="store_true", help="Explicitly authorize bounded fork metadata write")
    parser.add_argument("--actor", default="OpenSiro GitHub Actions issue-watch")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--read-only-descriptor", type=Path,
                        help="Transient source-verified watch for PAUSE fork; never modifies metadata")
    args = parser.parse_args(argv)
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    client = GitHubWriter(token, args.fork) if args.apply and args.allow_fork_write else GitHub(token)
    if args.apply and args.read_only_descriptor is not None:
        parser.error("--read-only-descriptor forbids --apply and all fork metadata writes")
    if args.apply and not args.allow_fork_write:
        parser.error("--apply requires --allow-fork-write; no implicit effectful autonomy")
    try:
        target = load_target(client, args.fork, args.contribution)
        if args.read_only_descriptor is not None:
            descriptor = json.loads(args.read_only_descriptor.read_text(encoding="utf-8"))
            target = readonly_descriptor_target(target, descriptor)
        observation = observe(client, target)
        if args.apply and observation["alert"] and observation["status"] != "UNKNOWN":
            result = apply_change(client, target, observation, actor=args.actor)
            observation.update(result)
        if observation["status"] == "UNKNOWN":
            print(json.dumps(observation, indent=2))
            return 2
        if not args.apply and observation["alert"]:
            observation["preview_only"] = True
        body = json.dumps(observation, indent=2)
        if args.output:
            args.output.write_text(body + "\n", encoding="utf-8")
        print(body)
        return 0
    except (APIError, OSError, ValueError, KeyError, TypeError, PermissionError, RuntimeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    sys.exit(main())
