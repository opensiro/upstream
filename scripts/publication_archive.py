"""Read-only projection of explicit archived Upstream publication sources.

The archive identifies historical candidates, not current authorship. Only
provider readback establishes ownership; replacement PRs are not silently
credited to the OpenSiro publisher. No registry is written.
"""
import re
from aggregate import APIError, api, REPOSITORY
from roadmap_view import read_text, SHA

ARCHIVE = "opensiro/upstream-old"
ARCHIVE_SOURCES = ("registry.yaml", "data/upstream-lifecycle.json",
                   "data/pr-maintenance/targets.json")
MAX_CASES = 100
MAX_ARCHIVE_RECORDS = 500
LINK = re.compile(r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/(issues|pull)/([1-9][0-9]*)\b")
CASE_FIELD = re.compile(r"^\s*-\s+\*\*(?:Upstream issue|Original(?: upstream| contributor)? PR|PR lifecycle(?: \([^)]*\))?):\*\*", re.I)
REGISTRY_FIELD = re.compile(r"^\s+upstream_(?:issue|pr):\s*(https://github\.com/[^\s]+)\s*$", re.M)


def discover_archive(client, original=None):
    """Pin current archive HEAD, read named ledgers and casebook, bound all reads."""
    import json
    records = {}
    errors = []
    seen_paths = []
    head = None

    def register(url, path):
        match = LINK.fullmatch(url)
        if not match:
            return
        repo, family, num = match.groups()
        if original and repo.casefold() != original.casefold():
            return
        if repo.split("/")[0].lower() in {"opensiro", "opensiro-contributions"}:
            return
        if len(records) >= MAX_ARCHIVE_RECORDS and url.casefold() not in records:
            raise ValueError("legacy archive record bound reached")
        key = url.casefold()
        item = records.setdefault(key, {
            "url": url, "repository": repo, "original_repository": repo,
            "kind": "original_issue" if family == "issues" else "original_pr",
            "number": int(num), "case_id": None, "working_fork": None,
            "meta_head_sha": None, "archive_head_sha": head,
            "evidence_types": ["LEGACY_ARCHIVE"], "provenance": [],
            "expected_title_sha256": None, "expected_body_sha256": None,
        })
        source = f"https://github.com/{ARCHIVE}/blob/{head}/{path}"
        if source not in item["provenance"]:
            item["provenance"].append(source)

    def load(path):
        value = read_text(client, ARCHIVE, path, head)
        seen_paths.append(path)
        return value

    try:
        head = (client.get(api(ARCHIVE, "git/ref/heads/main")).get("object") or {}).get("sha")
        if not isinstance(head, str) or not SHA.fullmatch(head):
            raise ValueError("invalid archive head")
        listing = client.get(api(ARCHIVE, "contents/cases") + "?ref=" + head)
        if not isinstance(listing, list) or len(listing) > MAX_CASES:
            raise ValueError("legacy case listing missing/truncated")
    except (APIError, ValueError, TypeError, AttributeError) as exc:
        return [], {"head": head, "status": "UNVERIFIED", "sources": [], "errors": [str(exc)]}

    for entry in listing:
        name = entry.get("name") if isinstance(entry, dict) else None
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_-]+\.md", name) or entry.get("type") != "file":
            errors.append("unexpected legacy case directory entry")
            continue
        if name == "README.md":
            continue
        path = "cases/" + name
        try:
            text = load(path)
            for line in text.splitlines():
                if CASE_FIELD.match(line):
                    # Exclude later links in explanatory closure text and events.
                    # Casebook's explicit heading is the historical action field.
                    links = list(LINK.finditer(line))
                    if "PR lifecycle" not in line:
                        links = links[:1]
                    for m in links:
                        register(m.group(0), path)
        except (APIError, ValueError, TypeError, KeyError, UnicodeDecodeError) as exc:
            errors.append(f"{path}: {exc}")
    for path in ARCHIVE_SOURCES:
        try:
            text = load(path)
            if path == "registry.yaml":
                # Only known scalar publication fields; not arbitrary YAML execution.
                for match in REGISTRY_FIELD.finditer(text):
                    register(match.group(1), path)
                if "upstream_issue:" not in text and "upstream_pr:" not in text:
                    errors.append("legacy registry publication fields not recognized")
            else:
                item = json.loads(text)
                if path.endswith("targets.json"):
                    targets = item.get("targets")
                    if not isinstance(targets, list) or len(targets) > MAX_ARCHIVE_RECORDS:
                        raise ValueError("invalid/truncated watchlist")
                    for target in targets:
                        register(target["url"], path)
                else:
                    rows = item.get("records")
                    registry = item.get("registry_records")
                    if not isinstance(rows, list) or not isinstance(registry, list):
                        raise ValueError("invalid archived lifecycle")
                    for row in rows:
                        if row.get("original_pr"):
                            register(row["original_pr"]["url"], path)
                        # landing_pr can be maintainer-authored: not our publication.
                    for row in registry:
                        if row.get("pr"):
                            register(row["pr"]["url"], path)
        except (APIError, ValueError, TypeError, KeyError, AttributeError, UnicodeDecodeError) as exc:
            errors.append(f"{path}: {exc}")
    return sorted(records.values(), key=lambda x: x["url"].casefold()), {
        "head": head, "status": "PARTIAL" if errors else "CHECKED_BOUNDED",
        "sources": sorted(seen_paths), "errors": errors,
        "historical_inventory_complete": False,
        "scope": "named archive ledgers and explicit casebook publication fields; not all historical Git trees",
    }
