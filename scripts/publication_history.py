#!/usr/bin/env python3
"""Read-only prior-publication inventory and fail-closed Roadmap Issue loop check.

Authority: verified fork opensiro/meta case files and append-only events for what
OpenSiro says it published; original GitHub objects for live state. This is a
projection, never a separate mutable registry or publication permission.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
from datetime import datetime, timezone
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from aggregate import APIError, GitHub, api, REPOSITORY
from roadmap_view import roadmap_view, read_text
from publication_archive import discover_archive
from roadmap_proposal_gate import (ACTIONS, BLOCKED, VERIFIED, GATE_ERRORS,
    original_head, candidate_destination, comment_target, review_evidence_sha256,
    verify_persisted_case)

URL = re.compile(
    r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)"
    r"/(issues|discussions|pull)/([1-9][0-9]*)(?:/)?$"
)
BODY_LINK = re.compile(
    r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/"
    r"(?:issues|discussions|pull)/[1-9][0-9]*"
)
WORDS = re.compile(r"[a-z0-9][a-z0-9_-]{2,}")
STOP = set("""proposal optional opensiro vsm architecture review request feature issue
the and for with from this that which what about not can when after before
using into between through would could should then have there also user users
native source original public github agent agents system systems browser tool
from into their existing first party first-party future current project
""".split())
MAX_EVENTS = 999
SEARCH_PAGE_SIZE = 100
MAX_SEARCH_RESULTS = 1000  # GitHub REST search's maximum retrievable results per query
MAX_COMMENTS = 500
MAX_TEXT = 200_000
ALLOWED_KINDS = {"original_issue", "fork_issue", "original_discussion", "original_pr", "fork_pr"}
CANDIDATE_KINDS = ALLOWED_KINDS | {"original_issue_comment"}
PUBLICATION_STATUSES = {"ALREADY_PUBLISHED", "REUSE_EXISTING", "POSSIBLE_OVERLAP",
                        "NEW_PROPOSAL", "HISTORY_UNVERIFIED"}


def parse_url(url, original=None, fork=None):
    if not isinstance(url, str):
        return None
    match = URL.fullmatch(url)
    if not match:
        return None
    repo = match.group(1) + "/" + match.group(2)
    family = match.group(3)
    if original and repo.lower() == original.lower():
        kind = {"issues": "original_issue", "discussions": "original_discussion",
                "pull": "original_pr"}[family]
    elif fork and repo.lower() == fork.lower():
        kind = {"issues": "fork_issue", "pull": "fork_pr"}.get(family)
    else:
        return None
    return {"url": "https://github.com/" + repo + "/" + family + "/" + match.group(4),
            "repository": repo, "kind": kind, "number": int(match.group(4))} if kind else None


def sha256(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def keywords(s):
    return {x for x in WORDS.findall(str(s).lower()) if x not in STOP}


def published_event(item):
    if not isinstance(item, dict):
        return False
    kind = str(item.get("kind") or "").upper()
    decision = str(item.get("decision") or "").upper()
    # Event filename is NOT proof. Exclude previews and merely prepared drafts.
    return (("PUBLISH" in kind or "PUBLICATION" in kind)
            and ("PUBLISHED" in decision or "VERIFIED" in kind
                 or "PUBLISHED" in kind)
            and not re.search(r"NOT[_ -]PUBLISHED|NOT[_ -]AUTHORIZED|PREVIEW|DRAFT|PENDING", decision))


def event_urls(event, original, fork):
    """A publication event owns its action URL, not every cited evidence URL."""
    fields = {
        "original_issue_url": "original_issue", "external_issue_url": "original_issue",
        "public_fork_issue_url": "fork_issue", "fork_issue_url": "fork_issue",
        "original_discussion_url": "original_discussion",
        "external_discussion_url": "original_discussion",
        "original_pr_url": "original_pr", "external_pr_url": "original_pr",
        "fork_pr_url": "fork_pr",
    }
    explicit = {}
    for field, kind in fields.items():
        if event.get(field):
            parsed = parse_url(event[field], original, fork)
            if not parsed or parsed["kind"] != kind:
                raise ValueError("publication action URL does not match field/channel")
            explicit[parsed["url"].casefold()] = parsed
    if explicit:
        if len(explicit) != 1:
            raise ValueError("multiple action URLs in a single publication event")
        return list(explicit.values())
    # Historic PUBLICATION events carry action type in decision, not a typed URL.
    decision = (str(event.get("kind", "")) + " " +
                str(event.get("decision", ""))).upper()
    if "DISCUSSION" in decision:
        kind = "original_discussion"
    elif "FORK" in decision and "ISSUE" in decision:
        kind = "fork_issue"
    elif "ORIGINAL" in decision and "ISSUE" in decision:
        kind = "original_issue"
    elif "ORIGINAL" in decision and ("PR_" in decision or "PULL_REQUEST" in decision):
        kind = "original_pr"
    else:
        raise ValueError("publication event channel unverified")
    candidates = {}
    for url in event.get("evidence_urls") or []:
        parsed = parse_url(url, original, fork)
        if parsed and parsed["kind"] == kind:
            candidates[parsed["url"].casefold()] = parsed
    if len(candidates) != 1:
        raise ValueError("legacy event action URL ambiguous or missing")
    return list(candidates.values())


def receipt_urls(text, original, fork):
    """Read only explicit publication-identity lines, not overlap citations."""
    heading = text[:600].upper()
    if not any(k in heading for k in ("PUBLICATION VERIFIED", "PUBLISHED / OPEN",
                                       "PUBLICATION OUTCOME", "PUBLICATION COMPLETED")):
        return []
    result = {}
    for line in text.splitlines():
        if not re.search(r"^\s*(?:[-*]\s+)?\*\*(?:PUBLICATION VERIFIED|CURRENT PUBLICATION OUTCOME|GITHUB URL / ID|PUBLICATION COMPLETED|PUBLISHED / OPEN|PUBLISHED EXTERNAL)", line, re.I):
            continue
        # One explicit identity field, never every related URL in the receipt.
        match = BODY_LINK.search(line)
        if match:
            parsed = parse_url(match.group(0), original, fork)
            if parsed:
                result[parsed["url"].casefold()] = parsed
    return list(result.values())


class ReadOnlyGitHub(GitHub):
    """Bounded GraphQL *query* only; no mutation or external communication write."""

    def _query(self, query, variables):
        if not self.token:
            raise APIError(0, "GraphQL readback requires configured GitHub token")
        payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
        req = Request("https://api.github.com/graphql", data=payload,
                      headers={"Authorization": "Bearer " + self.token,
                               "Accept": "application/vnd.github+json",
                               "Content-Type": "application/json",
                               "User-Agent": "opensiro-readonly-publication-history"},
                      method="POST")
        try:
            with urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if data.get("errors") or not isinstance(data.get("data"), dict):
                raise APIError(0, "GraphQL readback errors")
            return data["data"]
        except HTTPError as exc:
            raise APIError(exc.code, "GraphQL readback HTTP failure") from exc
        except (URLError, OSError, ValueError) as exc:
            raise APIError(0, "GraphQL readback unavailable") from exc

    def discussion(self, repo, number):
        owner, name = repo.split("/", 1)
        query = """query($owner:String!, $name:String!, $number:Int!) {
          repository(owner:$owner, name:$name) {
            discussion(number:$number) {
              title body createdAt updatedAt author { login }
              comments(first: 100) {
                totalCount pageInfo { hasNextPage }
                nodes { url body author { login } authorAssociation createdAt updatedAt }
              }
            }
          }
        }"""
        data = self._query(query, {"owner": owner, "name": name, "number": number})
        item = (data.get("repository") or {}).get("discussion")
        if not isinstance(item, dict):
            raise APIError(0, "GraphQL discussion missing")
        return item

    def discussion_search(self, repo, terms):
        """Bounded first-party Discussion enumeration, not a semantic classifier."""
        owner, name = repo.split("/", 1)
        query = """query($owner:String!, $name:String!, $cursor:String) {
          repository(owner:$owner, name:$name) {
            discussions(first: 100, after:$cursor) {
              totalCount pageInfo { hasNextPage endCursor }
              nodes { number url title body updatedAt author { login } }
            }
          }
        }"""
        cursor = None
        rows = []
        seen = set()
        for _ in range(5):
            data = self._query(query, {"owner": owner, "name": name, "cursor": cursor})
            page = (data.get("repository") or {}).get("discussions")
            if not isinstance(page, dict) or not isinstance(page.get("nodes"), list):
                raise APIError(0, "GraphQL discussion listing invalid")
            for item in page["nodes"]:
                number = item.get("number")
                if not isinstance(number, int) or number in seen:
                    raise APIError(0, "GraphQL discussion pagination changed")
                seen.add(number)
                author = (item.get("author") or {}).get("login")
                if (str(author or "").casefold() == "xlagerfeuer" or
                    len(terms & keywords(str(item.get("title", "")) + " " +
                                         str(item.get("body", "")))) >= min(2, len(terms))):
                    rows.append(item)
            info = page.get("pageInfo") or {}
            if not info.get("hasNextPage"):
                if page.get("totalCount") != len(seen):
                    raise APIError(0, "GraphQL discussion inventory changed or truncated")
                return rows
            new_cursor = info.get("endCursor")
            if not isinstance(new_cursor, str) or new_cursor == cursor:
                raise APIError(0, "GraphQL discussion cursor invalid")
            cursor = new_cursor
        raise APIError(0, "GraphQL discussion scan bound reached")


def feedback_observation(client, repo, number, expected_count):
    """Bounded original Issue comments; do not score bot replies as acceptance."""
    if expected_count == 0:
        return {"status": "COMPLETE", "items": []}
    if not isinstance(expected_count, int) or expected_count < 0 or expected_count > MAX_COMMENTS:
        return {"status": "UNVERIFIED", "reason": "COMMENTS_COUNT_UNVERIFIED", "items": []}
    seen = []
    try:
        for page in range(1, 7):
            data = client.get(api(repo, "issues/" + str(number) +
                                  "/comments?per_page=100&page=" + str(page)))
            if not isinstance(data, list):
                raise ValueError("invalid comments response")
            for item in data:
                author = (item.get("user") or {}).get("login")
                if not isinstance(author, str):
                    raise ValueError("missing comment author")
                seen.append({"url": item.get("html_url"), "author": author,
                             "association": item.get("author_association"),
                             "is_bot": (item.get("user") or {}).get("type") == "Bot" or
                                       author.lower().endswith("[bot]"),
                             "body_excerpt": str(item.get("body") or "")[:350],
                             "body_sha256": sha256(str(item.get("body") or "")),
                             "updated_at": item.get("updated_at"),
                             "created_at": item.get("created_at")})
            if len(seen) >= expected_count and len(data) < 100:
                break
        if len(seen) == expected_count:
            return {"status": "COMPLETE", "items": seen}
        return {"status": "UNVERIFIED", "reason": "COMMENTS_TRUNCATED_OR_CHANGED", "items": seen}
    except (APIError, ValueError, TypeError):
        return {"status": "UNVERIFIED", "reason": "COMMENTS_PROVIDER_UNAVAILABLE", "items": seen}


def readme_published_urls(text, original, fork):
    """Conservatively recover old publications from explicit case README lines.

    Generic Issue/PR references and historical draft-only checkpoints are not
    publication receipts. The provider still needs independent readback.
    """
    found = []
    for line in text.splitlines():
        if ("https://github.com/" not in line or
            re.search(r"NOT_PUBLISHED|NOT PUBLISHED|UNAPPROVED|DRAFT ONLY", line, re.I)):
            continue
        # Require both a publication assertion and a known channel.
        if not re.search(r"PUBLICATION VERIFIED|PUBLISHED / OPEN|PUBLISHED EXTERNAL|"
                         r"PUBLIC FORK ISSUE:.*PUBLISHED|ORIGINAL MAINTAINER ISSUE:.*PUBLISHED|"
                         r"ORIGINAL ISSUE PUBLISHED|SUBMITTED TO THE OFFICIAL", line, re.I):
            continue
        found.extend(p for url in BODY_LINK.findall(line)
                     if (p := parse_url(url, original, fork)))
    return found


def provider_observation(client, publication, observed_at, expected_author=None,
                         expected_title_hash=None, expected_body_hash=None):
    result = {"status": "UNVERIFIED", "observed_at": observed_at,
              "reason": "NOT_REQUESTED"}
    kind = publication["kind"]
    if kind.endswith("discussion"):
        if not hasattr(client, "discussion"):
            result["reason"] = "DISCUSSION_GRAPHQL_READBACK_REQUIRED"
            return result
        try:
            d = client.discussion(publication["repository"], publication["number"])
            author = (d.get("author") or {}).get("login")
            if not isinstance(d.get("title"), str) or not isinstance(d.get("body"), str) or not isinstance(author, str):
                raise ValueError("invalid Discussion GraphQL response")
            comment_data = d.get("comments") or {}
            nodes = comment_data.get("nodes") or []
            feedback = {"status": "COMPLETE" if (
                        comment_data.get("totalCount") == len(nodes)
                        and not (comment_data.get("pageInfo") or {}).get("hasNextPage"))
                        else "UNVERIFIED", "items": [
                            {"url": item.get("url"), "author": (item.get("author") or {}).get("login"),
                             "association": item.get("authorAssociation"),
                             "is_bot": str((item.get("author") or {}).get("login") or "").lower().endswith("[bot]"),
                             "body_excerpt": str(item.get("body") or "")[:350],
                             "body_sha256": sha256(str(item.get("body") or "")),
                             "updated_at": item.get("updatedAt"),
                             "created_at": item.get("createdAt")} for item in nodes]}
            result.update(status="PUBLISHED_STATE_NOT_CHECKED", reason=None,
                          title=d["title"], author=author,
                          title_sha256=sha256(d["title"]), body_sha256=sha256(d["body"]),
                          created_at=d.get("createdAt"), updated_at=d.get("updatedAt"),
                          comment_count=comment_data.get("totalCount"), feedback=feedback)
            if ((expected_author and author.lower() != expected_author.lower()) or
                (expected_title_hash and result["title_sha256"] != expected_title_hash) or
                (expected_body_hash and result["body_sha256"] != expected_body_hash)):
                result.update(status="UNVERIFIED", reason="DISCUSSION_AUTHOR_OR_HASH_MISMATCH")
            if feedback["status"] != "COMPLETE":
                result.update(status="UNVERIFIED", reason="DISCUSSION_COMMENTS_PARTIAL")
        except (APIError, ValueError, TypeError):
            result["reason"] = "DISCUSSION_GRAPHQL_UNVERIFIED"
        return result
    route = "pulls/" if kind.endswith("pr") else "issues/"
    try:
        d = client.get(api(publication["repository"], route + str(publication["number"])))
        if (not isinstance(d, dict) or not isinstance(d.get("title"), str)
            or not isinstance(d.get("body"), (str, type(None)))
            or (d.get("html_url") and d["html_url"].casefold() != publication["url"].casefold())
            or (kind.endswith("issue") and d.get("pull_request"))):
            raise ValueError("malformed original provider response")
        if kind.endswith("pr"):
            status = "MERGED" if d.get("merged_at") else "OPEN" if d.get("state") == "open" else "CLOSED_UNMERGED" if d.get("state") == "closed" else None
        else:
            status = "OPEN" if d.get("state") == "open" else "CLOSED" if d.get("state") == "closed" else None
        if not status:
            raise ValueError("unknown provider object state")
        author = (d.get("user") or {}).get("login")
        if not isinstance(author, str):
            raise ValueError("provider author missing")
        title_hash, body_hash = sha256(d["title"]), sha256(d["body"] or "")
        feedback = feedback_observation(client, publication["repository"],
                                        publication["number"], d.get("comments"))
        result.update(status=status, author=author, title=d["title"],
                      created_at=d.get("created_at"), updated_at=d.get("updated_at"),
                      title_sha256=title_hash, body_sha256=body_hash,
                      comment_count=d.get("comments"), feedback=feedback, reason=None)
        if feedback["status"] != "COMPLETE":
            result.update(status="UNVERIFIED", reason="COMMENTS_UNVERIFIED")
        if expected_author and author.lower() != expected_author.lower():
            result.update(status="UNVERIFIED", reason="AUTHOR_MISMATCH")
        if expected_title_hash and title_hash != expected_title_hash:
            result.update(status="UNVERIFIED", reason="TITLE_SHA256_MISMATCH")
        if expected_body_hash and body_hash != expected_body_hash:
            result.update(status="UNVERIFIED", reason="BODY_SHA256_MISMATCH_OR_EDIT")
    except (APIError, ValueError, TypeError, AttributeError) as exc:
        result["reason"] = (f"GITHUB_HTTP_{exc.status}" if isinstance(exc, APIError) and exc.status
                            else "PROVIDER_UNAVAILABLE_OR_MALFORMED")
    return result


def read_publications(client, roadmap, observed_at, live=True):
    """Reuse roadmap_view's verified current case scope; consume only case-owned proofs."""
    coverage = {"cases_seen": len(roadmap["cases"]), "events_seen": 0,
                "publications_found": 0, "provider_unverified": 0,
                "errors": roadmap["coverage"]["errors"], "scan_complete": False}
    records = {}
    warnings = list(roadmap["warnings"])
    events_cache = {}
    for case in roadmap["cases"]:
        fork = case["working_fork"]
        original = case["original_repository"]
        head = case["meta_head_sha"]
        case_id = case["id"]
        key = (fork, head)
        base = f".opensiro/issues/{case_id}"
        found = []
        receipt_url = f"https://github.com/{fork}/blob/{head}/{base}/publication-receipt.md"
        try:
            listing = client.get(api(fork, "contents/" + base) + "?ref=" + head)
            if not isinstance(listing, list) or len(listing) >= 1000:
                raise ValueError("invalid case listing")
            files = {x.get("name") for x in listing if x.get("type") == "file"}
            if "publication-receipt.md" in files:
                receipt = read_text(client, fork, base + "/publication-receipt.md", head)
                if len(receipt.encode("utf-8")) > MAX_TEXT:
                    raise ValueError("oversized receipt")
                for p in receipt_urls(receipt, original, fork):
                    found.append((p, "RECEIPT", receipt_url, None))
            # Older cases may record a verified publication only in README.md.
            # Parsing is intentionally narrow; provider identity is checked later.
            if "README.md" in files:
                readme_path = base + "/README.md"
                readme = read_text(client, fork, readme_path, head)
                if len(readme.encode("utf-8")) > MAX_TEXT:
                    raise ValueError("oversized README")
                for p in readme_published_urls(readme, original, fork):
                    found.append((p, "README_CLAIM",
                                  f"https://github.com/{fork}/blob/{head}/{readme_path}", None))
            if key not in events_cache:
                try:
                    events = client.get(api(fork, "contents/.opensiro/events") + "?ref=" + head)
                except APIError as e:
                    if e.status != 404:
                        raise
                    events = []
                if not isinstance(events, list) or len(events) > MAX_EVENTS:
                    raise ValueError("events pagination/truncation unknown")
                events_cache[key] = events
            for entry in events_cache[key]:
                name = entry.get("name")
                if not isinstance(name, str) or not name.endswith(".json"):
                    continue
                if not ("publish" in name.lower() or "publication" in name.lower()):
                    continue
                path = ".opensiro/events/" + name
                item = json.loads(read_text(client, fork, path, head))
                coverage["events_seen"] += 1
                if not published_event(item):
                    continue
                if item.get("case_id") and item["case_id"] != case_id:
                    continue
                # An old event without case_id belongs only to a single matching
                # case; otherwise do not attribute it to a random case.
                same_fork_cases = [c for c in roadmap["cases"] if c["working_fork"] == fork]
                if not item.get("case_id") and len(same_fork_cases) != 1:
                    warnings.append(f"{fork}: event {name} case identity unverified")
                    coverage["errors"] += 1
                    continue
                for p in event_urls(item, original, fork):
                    found.append((p, "EVENT", f"https://github.com/{fork}/blob/{head}/{path}", item))
            for p, provenance, source_url, event in found:
                unique = (fork.lower(), case_id, p["url"].lower())
                existing = records.get(unique)
                if existing is None:
                    expected_body = event.get("body_sha256") if event else None
                    expected_title = event.get("title_sha256") if event else None
                    records[unique] = {**p, "working_fork": fork, "original_repository": original,
                                       "case_id": case_id, "meta_head_sha": head,
                                       "provenance": [source_url],
                                       "evidence_types": [provenance],
                                       "expected_title_sha256": expected_title,
                                       "expected_body_sha256": expected_body}
                else:
                    if source_url not in existing["provenance"]:
                        existing["provenance"].append(source_url)
                    if provenance not in existing["evidence_types"]:
                        existing["evidence_types"].append(provenance)
                    if event:
                        for name in ("title", "body"):
                            h = event.get(f"{name}_sha256")
                            if h:
                                old = existing.get(f"expected_{name}_sha256")
                                if old and old != h:
                                    warnings.append(f"{fork}/{case_id}: inconsistent receipt hash for {p['url']}")
                                    coverage["errors"] += 1
                                existing[f"expected_{name}_sha256"] = h
        except (APIError, ValueError, TypeError, KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            coverage["errors"] += 1
            warnings.append(f"{fork}/{case_id}: publication readback incomplete: {exc}")
    records = sorted(records.values(), key=lambda x: (x["repository"].lower(), x["kind"], x["number"], x["case_id"]))
    coverage["publications_found"] = len(records)
    for item in records:
        item["provider"] = (provider_observation(client, item, observed_at,
                             expected_author="xLagerFeuer",
                             expected_title_hash=item.get("expected_title_sha256"),
                             expected_body_hash=item.get("expected_body_sha256"))
                            if live else {"status": "UNVERIFIED", "reason": "LIVE_READBACK_DISABLED",
                                          "observed_at": observed_at})
        coverage["provider_unverified"] += item["provider"]["status"] == "UNVERIFIED"
    coverage["scan_complete"] = (roadmap["coverage"]["scan_complete"] and coverage["errors"] == 0
                                 and coverage["provider_unverified"] == 0)
    return records, coverage, warnings


def search_original(client, original, title, expanded=False):
    """Bounded native Issue/PR/Discussion candidate discovery, not proof of novelty.

    expanded=False retains the old library interface for callers with only REST
    issue fixtures. The CLI always requests all supported native channels.
    """
    terms = sorted(keywords(title), key=lambda w: (-len(w), w))[:4]
    if not terms:
        return [], ["CANDIDATE_KEYWORDS_EMPTY"]
    kinds = ("issue", "pr") if expanded else ("issue",)
    queries = []
    for kind in kinds:
        queries.extend([f"repo:{original} is:{kind} author:xLagerFeuer",
                        f"repo:{original} is:{kind} " + " ".join(terms[:2])])
    results = {}
    errors = []
    for q in queries:
        # The first page is not the search boundary. Keep GitHub's explicit
        # maximum and fail closed if pagination cannot prove bounded coverage.
        route = "/search/issues?q=" + quote(q) + "&per_page=" + str(SEARCH_PAGE_SIZE)
        expected_kind = "original_pr" if " is:pr " in q else "original_issue"
        seen = set()
        total = None
        for page in range(1, MAX_SEARCH_RESULTS // SEARCH_PAGE_SIZE + 1):
            try:
                data = client.get(route + (f"&page={page}" if page > 1 else ""))
                if not isinstance(data, dict) or not isinstance(data.get("items"), list):
                    raise ValueError("malformed native search")
                count = data.get("total_count")
                if type(count) is not int or count < 0:
                    raise ValueError("invalid native search total_count")
                if total is None:
                    total = count
                complete_page = (data.get("incomplete_results") is False
                                 and count == total
                                 and total <= MAX_SEARCH_RESULTS
                                 and len(data["items"]) == min(SEARCH_PAGE_SIZE,
                                                              max(0, total - (page - 1) * SEARCH_PAGE_SIZE)))
                if not complete_page:
                    errors.append(f"SEARCH_TRUNCATED: {q} / page {page}, total {count}")
                for item in data["items"]:
                    if not isinstance(item, dict):
                        errors.append(f"SEARCH_IDENTITY_UNVERIFIED: {q} / page {page}")
                        complete_page = False
                        continue
                    parsed = parse_url(item.get("html_url"), original, None)
                    if not parsed or parsed["kind"] != expected_kind:
                        errors.append(f"SEARCH_IDENTITY_UNVERIFIED: {q} / page {page}")
                        complete_page = False
                        continue
                    identity = parsed["url"].casefold()
                    if identity in seen:
                        errors.append(f"SEARCH_PAGINATION_DUPLICATE: {q} / page {page}")
                        complete_page = False
                    seen.add(identity)
                    results[parsed["url"]] = {"url": parsed["url"],
                        "kind": parsed["kind"], "title": item.get("title"),
                        "author": (item.get("user") or {}).get("login"),
                        "state": item.get("state"), "updated_at": item.get("updated_at")}
                if not complete_page or len(seen) == total:
                    break
            except (APIError, ValueError, TypeError, AttributeError) as exc:
                errors.append(f"SEARCH_UNVERIFIED: {q} / page {page} / {exc}")
                break
        if total is not None and len(seen) != total:
            errors.append(f"SEARCH_PAGINATION_INCOMPLETE: {q} / {len(seen)} of {total}")
    if expanded:
        try:
            info = client.get(api(original, ""))
            if info.get("has_discussions") is not False:
                if info.get("has_discussions") is not True or not hasattr(client, "discussion_search"):
                    raise ValueError("native Discussion availability/readback unknown")
                for item in client.discussion_search(original, set(terms)):
                    parsed = parse_url(item.get("url"), original, None)
                    if not parsed or parsed["kind"] != "original_discussion":
                        raise ValueError("Discussion candidate identity unverified")
                    results[parsed["url"]] = {"url": parsed["url"],
                        "kind": "original_discussion", "title": item.get("title"),
                        "author": (item.get("author") or {}).get("login"),
                        "state": "STATE_NOT_CHECKED", "updated_at": item.get("updatedAt")}
        except (APIError, ValueError, TypeError, AttributeError) as exc:
            errors.append(f"DISCUSSION_SEARCH_UNVERIFIED: {original} / {exc}")
    return sorted(results.values(), key=lambda x: x["url"].casefold()), errors


def evaluate(report, original, case_id, title, target_kind="original_issue",
             search_results=None, search_errors=None, user_delta=None):
    """Separate duplicate *action* from same-case second audience and semantic hints."""
    if not REPOSITORY.fullmatch(original) or target_kind not in CANDIDATE_KINDS:
        raise ValueError("invalid candidate original repository or kind")
    items = report["publications"]
    same_case = [p for p in items if p["original_repository"].lower() == original.lower()
                 and p.get("case_id") == case_id]
    same_action = [p for p in same_case if p["kind"] == target_kind]
    different_channel = [p for p in same_case if p["kind"] != target_kind]
    same_original = [p for p in items if p["original_repository"].lower() == original.lower()
                     and p not in same_case]
    # Cross-repository resemblance is advisory only. Do not conflate Sx transitions.
    cross_pattern = [p for p in items if p["original_repository"].lower() != original.lower()
                     and p.get("provider", {}).get("title")
                     and len(keywords(title) & keywords(p["provider"]["title"])) >= 2]
    related = list(search_results or [])
    errors = list(search_errors or [])
    overlapping = [{"url": p["url"], "reason": "SAME_CASE_DIFFERENT_PUBLICATION_CHANNEL"}
                   for p in different_channel]
    overlapping += [{"url": p["url"], "reason": "PRIOR_OPENSIRO_SAME_ORIGINAL"}
                    for p in same_original]
    overlapping += [{"url": p["url"], "reason": "CROSS_REPOSITORY_PATTERN_ONLY"}
                    for p in cross_pattern]
    for p in related:
        if not any(z["url"] == p["url"] for z in overlapping):
            overlapping.append({"url": p["url"], "reason": "FIRST_PARTY_SEARCH_POSSIBLE_OVERLAP"})
    scanned = [c for c in report["cases"] if c["original_repository"].lower() == original.lower()
               and c["id"] == case_id]
    reasons = []
    if same_action and any(p["provider"]["status"] == "UNVERIFIED" for p in same_action):
        status = "HISTORY_UNVERIFIED"
        reasons.append("A prior same-channel publication is recorded but provider identity/readback is unresolved; do not repeat POST.")
    elif same_action:
        status = "ALREADY_PUBLISHED"
        reasons.append("Already published in this channel from the same stable case; no repeat POST.")
    elif not scanned or not report["coverage"]["scan_complete"] or errors:
        status = "HISTORY_UNVERIFIED"
        reasons.append("Incomplete verified case/provider/search coverage; cannot assert no prior publication.")
    elif target_kind != "original_issue":
        status = "HISTORY_UNVERIFIED"
        reasons.append("Native channel search not covered for fork Issues, Discussions or PRs; do not claim novelty.")
    elif any(p["provider"]["status"] == "UNVERIFIED" for p in same_original + different_channel):
        status = "HISTORY_UNVERIFIED"
        reasons.append("Earlier publication on this original/case could not be reconciled with GitHub.")
    elif any(str(p.get("author") or "").lower() == "xlagerfeuer"
             and p.get("kind", "original_issue") == target_kind
             and str(p.get("title") or "").strip().casefold() == title.strip().casefold()
             for p in related):
        status = "REUSE_EXISTING"
        reasons.append("Exact same public title already exists under the OpenSiro publisher in original Issues.")
    elif overlapping:
        status = "POSSIBLE_OVERLAP"
        reasons.append("Previous public action or native Issue may overlap; compare new user-visible outcome.")
        if not user_delta:
            reasons.append("Missing explicit what-changed/user-visible delta for a related proposal.")
    else:
        status = "NEW_PROPOSAL"
        reasons.append("No prior matching publication found within checked bounded scope; not global novelty proof.")
    return {"status": status, "original": original, "case_id": case_id,
            "candidate_kind": target_kind, "candidate_title": title,
            "same_case_publications": same_action,
            "same_case_other_channels": different_channel,
            "possible_overlaps": overlapping,
            "original_search_results": related, "search_errors": errors,
            "user_visible_delta": user_delta,
            "reasons": reasons, "requires_exact_owner_approval": True,
            "permits_automatic_publication": False,
            "history_complete": False}

def merge_archive(client, records, coverage, warnings, original, observed_at, live):
    archived, scope = discover_archive(client, original)
    by_url = {p["url"].casefold(): p for p in records}
    for item in archived:
        key = item["url"].casefold()
        if key in by_url:
            present = by_url[key]
            present["provenance"] = sorted(set(present["provenance"] + item["provenance"]))
            present["evidence_types"] = sorted(set(present["evidence_types"] + ["LEGACY_ARCHIVE"]))
            continue
        item["provider"] = (provider_observation(client, item, observed_at,
                                expected_author="xLagerFeuer") if live else
                            {"status": "UNVERIFIED", "reason": "LIVE_READBACK_DISABLED",
                             "observed_at": observed_at})
        records.append(item)
    scope["candidate_records"] = len(archived)
    scope["unmatched_records"] = sum(p["case_id"] is None for p in records)
    coverage["publications_found"] = len(records)
    coverage["provider_unverified"] = sum(p["provider"]["status"] == "UNVERIFIED" for p in records)
    coverage["archive"] = scope
    if scope["status"] != "CHECKED_BOUNDED":
        warnings.extend("upstream-old: " + e for e in scope["errors"])
        coverage["errors"] += len(scope["errors"])
    coverage["scan_complete"] = (coverage["scan_complete"] and not scope["errors"]
                                 and not coverage["provider_unverified"])
    return records


def publication_history(client, requested=None, candidate_original=None,
                        candidate_case=None, candidate_title=None,
                        candidate_kind="original_issue", candidate_delta=None,
                        live=True, search=True, observed_at=None,
                        include_archive=False, expanded_search=False):
    now = observed_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    roadmap = roadmap_view(client, requested=requested, observed_at=now)
    records, coverage, warnings = read_publications(client, roadmap, now, live=live)
    if include_archive:
        records = merge_archive(client, records, coverage, warnings,
                                candidate_original, now, live)
    else:
        coverage["archive"] = {"status": "NOT_REQUESTED", "historical_inventory_complete": False}
    report = {"generated_at": now, "scope": roadmap["scope"],
              "historical_inventory_complete": False,
              "coverage": {**roadmap["coverage"], **coverage},
              "cases": [{"original_repository": c["original_repository"],
                         "working_fork": c["working_fork"], "id": c["id"],
                         "meta_head_sha": c["meta_head_sha"]}
                        for c in roadmap["cases"]],
              "publications": records, "warnings": warnings}
    if candidate_original or candidate_case or candidate_title:
        if not (candidate_original and candidate_case and candidate_title):
            raise ValueError("candidate original/case/title must be supplied together")
        matched, errs = (search_original(client, candidate_original, candidate_title, expanded=expanded_search)
                         if search else ([], ["FIRST_PARTY_SEARCH_NOT_RUN"]))
        report["preflight"] = evaluate(report, candidate_original, candidate_case,
                                       candidate_title, candidate_kind, matched, errs, user_delta=candidate_delta)
    return report


def attach_roadmap_gate(client, report, case_ref, body, destination=None,
                        source_before=None, source_error=None, live_checks=True):
    """A discovery scan is useful before persistence, but never approval-ready.

    The review digest intentionally excludes the commit that records the review;
    the final approval snapshot binds that exact commit and payload separately.
    """
    pre = report["preflight"]
    action = pre["candidate_kind"]
    if action not in ACTIONS:
        return
    report["roadmap_gate"] = {"status": BLOCKED}
    try:
        if source_error:
            raise ValueError(source_error)
        original = pre["original"]
        matches = [c for c in report["cases"]
                   if c["original_repository"].casefold() == original.casefold()
                   and c["id"] == pre["case_id"]]
        if len(matches) != 1:
            raise ValueError("exactly one verified stable fork-local case required")
        selected = matches[0]
        fork = selected["working_fork"]
        head = original_head(client, original)
        if source_before != head:
            raise ValueError("original HEAD changed or was not verified before scan")
        destination = candidate_destination(original, fork, action, destination)
        target = comment_target(client, original, action, destination)
        history_sha = review_evidence_sha256(report, head, destination, target)
        report["review_context"] = {"source_head": head, "destination": destination,
                                    "target": target}
        report["review_evidence_sha256"] = history_sha
        if not live_checks or not report["coverage"]["scan_complete"] or pre["search_errors"]:
            raise ValueError("live bounded publication/history search incomplete")
        if report["coverage"].get("archive", {}).get("status") != "CHECKED_BOUNDED":
            raise ValueError("named archive coverage unverified")
        if pre["status"] in {"ALREADY_PUBLISHED", "REUSE_EXISTING"} and action != "original_issue_comment":
            raise ValueError("prior same-channel object must be reused, not republished")
        if action == "original_issue" and pre["status"] == "HISTORY_UNVERIFIED":
            raise ValueError("original Issue history is unverified")
        if not case_ref or selected["meta_head_sha"] != case_ref:
            raise ValueError("candidate requires current persisted case-ref matching history scan")
        if body is None:
            raise ValueError("exact committed outbound body required; discovery only")
        proof = verify_persisted_case(client, fork, pre["case_id"], case_ref, original,
                                      head, action, destination, pre["candidate_title"],
                                      body, history_sha)
        # The existing target's state/body may change while the case is checked.
        if comment_target(client, original, action, destination) != target:
            raise ValueError("original Issue target changed during review")
        report["roadmap_gate"] = proof
    except GATE_ERRORS as exc:
        report["roadmap_gate"] = {"status": BLOCKED, "reason": str(exc)}


def candidate_snapshot(client, report, body_bytes):
    """Read-only fingerprint of the candidate, source pin and observed prior evidence."""
    pre = report["preflight"]
    if not body_bytes or not body_bytes.strip():
        raise ValueError("exact candidate body is empty")
    original = pre["original"]
    info = client.get(api(original, ""))
    default = info.get("default_branch")
    if not isinstance(default, str) or not default:
        raise ValueError("original default branch unknown")
    ref = client.get(api(original, "git/ref/heads/" + quote(default, safe="/")))
    head = (ref.get("object") or {}).get("sha")
    if not isinstance(head, str) or not re.fullmatch(r"[0-9a-f]{40}", head):
        raise ValueError("original HEAD unverified")
    # Strip per-observation timestamps only. Content and provider update timestamps
    # remain in the fingerprint, as do scope, comments and search result identities.
    def stable(value):
        if isinstance(value, dict):
            return {k: stable(v) for k, v in value.items()
                    if k not in {"generated_at", "observed_at"}}
        if isinstance(value, list):
            return [stable(x) for x in value]
        return value
    evidence = {"original_head": head, "title_sha256": sha256(pre["candidate_title"]),
                "body_sha256": hashlib.sha256(body_bytes).hexdigest(),
                "candidate": stable(pre),
                "scope": stable(report.get("coverage")),
                "cases": stable(report.get("cases")),
                "publications": stable(report.get("publications")),
                "roadmap_gate": stable(report.get("roadmap_gate")),
                "review_context": stable(report.get("review_context")),
                "review_evidence_sha256": report.get("review_evidence_sha256")}
    raw = json.dumps(evidence, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return {"original_head": head, "title_sha256": evidence["title_sha256"],
            "body_sha256": evidence["body_sha256"], "evidence_sha256": sha256(raw)}


def apply_recheck(report, previous):
    pre = report["preflight"]
    expected = previous.get("candidate_snapshot")
    actual = report.get("candidate_snapshot")
    changed = not isinstance(expected, dict) or not isinstance(actual, dict) or expected != actual
    report["recheck"] = {"status": "CHANGED_OR_UNVERIFIED" if changed else "UNCHANGED",
                         "previous": expected, "current": actual}
    if changed and pre["status"] not in {"ALREADY_PUBLISHED", "REUSE_EXISTING"}:
        pre["status"] = "HISTORY_UNVERIFIED"
        pre["reasons"].append("Approval-time evidence or exact outbound payload changed; re-review required.")
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", action="append", help="restrict to verified opensiro-contributions forks")
    p.add_argument("--candidate-original", help="original OWNER/REPO")
    p.add_argument("--candidate-case", help="stable fork-local case ID")
    p.add_argument("--candidate-title", help="exact proposed title")
    p.add_argument("--candidate-kind", choices=sorted(CANDIDATE_KINDS), default="original_issue")
    p.add_argument("--candidate-delta", help="what changed for the user vs related prior publication")
    p.add_argument("--case-ref", help="exact current opensiro/meta commit; omitted for discovery only")
    p.add_argument("--candidate-destination", help="exact original Issue URL for an existing-Issue comment")
    p.add_argument("--no-live", action="store_true", help="offline evidence only: provider state unverified")
    p.add_argument("--no-search", action="store_true", help="do not query first-party Issues: never infer novelty")
    p.add_argument("--no-archive", action="store_true", help="skip archive read; candidate novelty stays unverified")
    p.add_argument("--candidate-body-file", type=Path,
                   help="exact outbound body bytes for approval/pre-POST evidence fingerprint")
    p.add_argument("--previous-report", type=Path,
                   help="approval-time JSON report; any changed evidence requires re-review")
    p.add_argument("--format", choices=["json"], default="json")
    a = p.parse_args(argv)
    client = ReadOnlyGitHub(os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN"))
    source_before = source_error = None
    if a.candidate_original and a.candidate_kind in ACTIONS:
        try:
            source_before = original_head(client, a.candidate_original)
        except GATE_ERRORS as exc:
            source_error = "original source before scan unverified: " + str(exc)
    try:
        report = publication_history(client,
            requested=a.repo, candidate_original=a.candidate_original,
            candidate_case=a.candidate_case, candidate_title=a.candidate_title,
            candidate_kind=a.candidate_kind, candidate_delta=a.candidate_delta,
            live=not a.no_live, search=not a.no_search, include_archive=not a.no_archive, expanded_search=True)
    except ValueError as exc:
        p.error(str(exc))
    if a.no_archive and report.get("preflight", {}).get("status") == "NEW_PROPOSAL":
        report["preflight"]["status"] = "HISTORY_UNVERIFIED"
        report["preflight"]["reasons"].append("Archive history check explicitly skipped.")
    if "preflight" in report:
        body_bytes = None
        body_error = None
        if a.candidate_body_file:
            try:
                body_bytes = a.candidate_body_file.read_bytes()
            except OSError as exc:
                body_error = str(exc)
        attach_roadmap_gate(client, report, a.case_ref, body_bytes,
                            destination=a.candidate_destination, source_before=source_before,
                            source_error=source_error,
                            live_checks=not (a.no_live or a.no_search or a.no_archive))
        if not a.candidate_body_file:
            if report["preflight"]["status"] == "NEW_PROPOSAL":
                report["preflight"]["status"] = "HISTORY_UNVERIFIED"
                report["preflight"]["reasons"].append("Exact candidate body bytes not supplied.")
        else:
            try:
                if body_error:
                    raise ValueError(body_error)
                report["candidate_snapshot"] = candidate_snapshot(client, report, body_bytes)
                if (report.get("roadmap_gate", {}).get("status") == VERIFIED
                        and report["candidate_snapshot"]["original_head"] != report["roadmap_gate"]["source_head"]):
                    raise ValueError("source changed after persistence gate")
            except (APIError, OSError, ValueError, TypeError, AttributeError) as exc:
                if report["preflight"]["status"] == "NEW_PROPOSAL":
                    report["preflight"]["status"] = "HISTORY_UNVERIFIED"
                report["preflight"]["reasons"].append("Candidate snapshot unverified: " + str(exc))
                if a.candidate_kind in ACTIONS:
                    report["roadmap_gate"] = {"status": BLOCKED, "reason": str(exc)}
        if a.previous_report:
            try:
                previous = json.loads(a.previous_report.read_text(encoding="utf-8"))
                if not isinstance(previous, dict):
                    raise ValueError("previous report must be an object")
            except (OSError, ValueError):
                previous = {}
            apply_recheck(report, previous)
    elif a.candidate_body_file or a.previous_report or a.case_ref or a.candidate_destination:
        p.error("body, case-ref, destination and previous-report require a candidate")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    # Strict CLI nonzero prevents a successful-looking scan when provider/metadata unknown;
    # preflight never grants consent. Same-case publication is a hard block.
    status = report.get("preflight", {}).get("status")
    persisted = (status is None or a.candidate_kind not in ACTIONS
                 or report.get("roadmap_gate", {}).get("status") == VERIFIED)
    return 0 if (persisted and report["coverage"]["scan_complete"]
                 and status in (None, "NEW_PROPOSAL")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
