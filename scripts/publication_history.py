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
MAX_ISSUES = 100
MAX_COMMENTS = 500
MAX_TEXT = 200_000
ALLOWED_KINDS = {"original_issue", "fork_issue", "original_discussion", "original_pr", "fork_pr"}
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
            and "NOT_PUBLISHED" not in decision
            and "NOT_AUTHORIZED" not in decision)


def event_urls(event, original, fork):
    urls = []
    for key in ("original_issue_url", "external_issue_url", "public_fork_issue_url",
                "fork_issue_url", "original_discussion_url", "external_discussion_url"):
        url = event.get(key)
        if url:
            urls.append(url)
    # Current historical events also store publication URLs in evidence_urls.
    urls.extend(event.get("evidence_urls") or [])
    return [p for u in urls if (p := parse_url(u, original, fork))]


def receipt_urls(text, original, fork):
    """Only assert receipt links when the document itself states verified publication."""
    heading = text[:600].upper()
    if not any(k in heading for k in ("PUBLICATION VERIFIED", "PUBLISHED / OPEN",
                                       "PUBLICATION OUTCOME", "PUBLICATION COMPLETED")):
        return []
    lines = text.splitlines()
    selected = []
    for line in lines:
        # Do not misidentify a quoted existing Issue/PR as the outward publication.
        if any(k in line.lower() for k in ("publication verified", "publication outcome",
                                            "github url / id", "published", "target/action",
                                            "new public original")):
            selected.extend(BODY_LINK.findall(line))
    return [p for u in selected if (p := parse_url(u, original, fork))]


class ReadOnlyGitHub(GitHub):
    """Bounded GraphQL *query* only; no mutation or external communication write."""

    def discussion(self, repo, number):
        if not self.token:
            raise APIError(0, "GraphQL readback requires configured GitHub token")
        owner, name = repo.split("/", 1)
        query = """query($owner:String!, $name:String!, $number:Int!) {
          repository(owner:$owner, name:$name) {
            discussion(number:$number) {
              title body createdAt updatedAt author { login }
              comments(first: 100) {
                totalCount pageInfo { hasNextPage }
                nodes { url body author { login } authorAssociation createdAt }
              }
            }
          }
        }"""
        payload = json.dumps({"query": query,
                              "variables": {"owner": owner, "name": name,
                                            "number": number}}).encode("utf-8")
        req = Request("https://api.github.com/graphql", data=payload,
                      headers={"Authorization": "Bearer " + self.token,
                               "Accept": "application/vnd.github+json",
                               "Content-Type": "application/json",
                               "User-Agent": "opensiro-readonly-publication-history"},
                      method="POST")
        try:
            with urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if data.get("errors"):
                raise APIError(0, "GraphQL readback errors")
            item = ((data.get("data") or {}).get("repository") or {}).get("discussion")
            if not isinstance(item, dict):
                raise APIError(0, "GraphQL discussion missing")
            return item
        except HTTPError as exc:
            raise APIError(exc.code, "GraphQL readback HTTP failure") from exc
        except (URLError, OSError, ValueError) as exc:
            raise APIError(0, "GraphQL readback unavailable") from exc


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
                             "body_excerpt": str(item.get("body") or "")[:350]})
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
                             "body_excerpt": str(item.get("body") or "")[:350]} for item in nodes]}
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
        if not isinstance(d, dict) or not isinstance(d.get("title"), str) or not isinstance(d.get("body"), (str, type(None))):
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
    except (APIError, ValueError, TypeError) as exc:
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


def search_original(client, original, title):
    """Bounded original-native candidate search, not evidence of exhaustive novelty."""
    terms = sorted(keywords(title), key=len, reverse=True)[:4]
    queries = [f"repo:{original} is:issue author:xLagerFeuer",
               f"repo:{original} is:issue " + " ".join(terms[:2])]
    results = {}
    errors = []
    for q in queries:
        try:
            data = client.get("/search/issues?q=" + quote(q) + "&per_page=100")
            if not isinstance(data, dict) or not isinstance(data.get("items"), list):
                raise ValueError("malformed original search")
            if data.get("incomplete_results") or data.get("total_count", 0) > MAX_ISSUES or len(data["items"]) >= MAX_ISSUES:
                errors.append(f"SEARCH_TRUNCATED: {q}")
            for item in data["items"]:
                parsed = parse_url(item.get("html_url"), original, None)
                if parsed:
                    results[parsed["url"]] = {"url": parsed["url"], "title": item.get("title"),
                                               "author": (item.get("user") or {}).get("login"),
                                               "state": item.get("state")}
        except (APIError, ValueError, TypeError) as exc:
            errors.append(f"SEARCH_UNVERIFIED: {q} / {exc}")
    return sorted(results.values(), key=lambda x: x["url"]), errors


def evaluate(report, original, case_id, title, target_kind="original_issue",
             search_results=None, search_errors=None, user_delta=None):
    """Separate duplicate *action* from same-case second audience and semantic hints."""
    if not REPOSITORY.fullmatch(original) or target_kind not in ALLOWED_KINDS:
        raise ValueError("invalid candidate original repository or kind")
    items = report["publications"]
    same_case = [p for p in items if p["original_repository"].lower() == original.lower()
                 and p["case_id"] == case_id]
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
    if same_action:
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
    elif any(p.get("author", "").lower() == "xlagerfeuer"
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

def publication_history(client, requested=None, candidate_original=None,
                        candidate_case=None, candidate_title=None,
                        candidate_kind="original_issue", candidate_delta=None,
                        live=True, search=True, observed_at=None):
    now = observed_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    roadmap = roadmap_view(client, requested=requested, observed_at=now)
    records, coverage, warnings = read_publications(client, roadmap, now, live=live)
    report = {"generated_at": now, "scope": roadmap["scope"],
              "historical_inventory_complete": False,
              "coverage": {**roadmap["coverage"], **coverage},
              "cases": [{"original_repository": c["original_repository"],
                         "working_fork": c["working_fork"], "id": c["id"]}
                        for c in roadmap["cases"]],
              "publications": records, "warnings": warnings}
    if candidate_original or candidate_case or candidate_title:
        if not (candidate_original and candidate_case and candidate_title):
            raise ValueError("candidate original/case/title must be supplied together")
        matched, errs = (search_original(client, candidate_original, candidate_title)
                         if search else ([], ["FIRST_PARTY_SEARCH_NOT_RUN"]))
        report["preflight"] = evaluate(report, candidate_original, candidate_case,
                                       candidate_title, candidate_kind, matched, errs, user_delta=candidate_delta)
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", action="append", help="restrict to verified opensiro-contributions forks")
    p.add_argument("--candidate-original", help="original OWNER/REPO")
    p.add_argument("--candidate-case", help="stable fork-local case ID")
    p.add_argument("--candidate-title", help="exact proposed title")
    p.add_argument("--candidate-kind", choices=sorted(ALLOWED_KINDS), default="original_issue")
    p.add_argument("--candidate-delta", help="what changed for the user vs related prior publication")
    p.add_argument("--no-live", action="store_true", help="offline evidence only: provider state unverified")
    p.add_argument("--no-search", action="store_true", help="do not query first-party Issues: never infer novelty")
    p.add_argument("--format", choices=["json"], default="json")
    a = p.parse_args(argv)
    try:
        report = publication_history(ReadOnlyGitHub(os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")),
            requested=a.repo, candidate_original=a.candidate_original,
            candidate_case=a.candidate_case, candidate_title=a.candidate_title,
            candidate_kind=a.candidate_kind, candidate_delta=a.candidate_delta,
            live=not a.no_live, search=not a.no_search)
    except ValueError as exc:
        p.error(str(exc))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    # Strict CLI nonzero prevents a successful-looking scan when provider/metadata unknown;
    # preflight never grants consent. Same-case publication is a hard block.
    status = report.get("preflight", {}).get("status")
    return 0 if report["coverage"]["scan_complete"] and status in (None, "NEW_PROPOSAL") else 1


if __name__ == "__main__":
    raise SystemExit(main())
