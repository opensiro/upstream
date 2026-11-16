#!/usr/bin/env python3
"""Render a dated GitHub-style external-PR activity view from the existing Upstream aggregate.

One-shot, read-only GitHub API access: no daemon, schedule, second source-of-truth
ledger, approval inference, or deployed-benefit score.
"""
import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
from html import escape
import json
import os
from pathlib import Path

from aggregate import APIError, GitHub, PR_LINK, api

COLORS = ("#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39")


def parse_timestamp(value, label):
    if not isinstance(value, str):
        raise ValueError(f"{label}: missing UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label}: invalid timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{label}: timezone required")
    return parsed.astimezone(timezone.utc)


def linked_prs(snapshot):
    """One PR URL counts once, even across related interventions or replacement chains."""
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("forks"), list):
        raise ValueError("expected Upstream aggregate JSON with forks")
    coverage = snapshot.get("coverage") or {}
    if not coverage.get("scan_complete") or coverage.get("errors") or coverage.get("filtered_by_attention"):
        raise ValueError("input aggregate is incomplete or attention-filtered; use an unfiltered complete scan")
    if not snapshot["forks"]:
        raise ValueError("no verified metadata forks found")
    seen = {}
    for fork in snapshot["forks"]:
        original = fork.get("original_repository", "")
        for record in fork.get("contributions", []):
            for pr in record.get("external_prs", []):
                url = pr.get("url")
                match = PR_LINK.fullmatch(url or "")
                if not match:
                    raise ValueError(f"invalid original PR link: {url!r}")
                expected = match.group(1) + "/" + match.group(2)
                if expected.lower() != original.lower():
                    raise ValueError(f"external PR does not match verified original: {url}")
                key = url.lower().rstrip("/")
                seen[key] = (url, expected, match.group(3))
    return sorted(seen.values(), key=lambda x: x[0].lower())


def review_approval(client, original, number, closed_at):
    """Was the latest eligible reviewer state APPROVED before closure?

    Review approval is not maintainer acceptance or deployment evidence.
    Fetch all pages or fail closed.
    """
    pages = []
    for page in range(1, 26):
        batch = client.get(api(original, f"pulls/{number}/reviews?per_page=100&page={page}"))
        if not isinstance(batch, list):
            raise ValueError("invalid GitHub PR review response")
        pages.extend(batch)
        if len(batch) < 100:
            break
    else:
        raise ValueError("review pagination safety limit reached")
    latest = {}
    for index, item in enumerate(pages):
        author = (item.get("user") or {}).get("login")
        state = item.get("state")
        stamp = item.get("submitted_at")
        if not isinstance(author, str) or state not in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED", "COMMENTED", "PENDING"):
            continue
        if state in ("COMMENTED", "PENDING") or stamp is None:
            continue
        when = parse_timestamp(stamp, "review.submitted_at")
        if when > closed_at:
            continue
        key = author.lower()
        if key not in latest or (when, index) > latest[key][0]:
            latest[key] = ((when, index), state)
    return any(value[1] == "APPROVED" for value in latest.values())


def collect(client, snapshot, observed_at=None):
    now = parse_timestamp(observed_at, "observed_at") if observed_at else datetime.now(timezone.utc)
    refs = linked_prs(snapshot)
    events = []
    records = []
    warnings = []
    statuses = Counter()
    for url, original, number in refs:
        try:
            pr = client.get(api(original, f"pulls/{number}"))
            if not isinstance(pr, dict):
                raise ValueError("invalid original PR readback")
            if pr.get("html_url", "").lower().rstrip("/") != url.lower().rstrip("/"):
                raise ValueError("original GitHub PR URL mismatch")
            created = parse_timestamp(pr.get("created_at"), "PR.created_at")
            if created > now:
                raise ValueError("future PR publication date")
            merged = parse_timestamp(pr["merged_at"], "PR.merged_at") if pr.get("merged_at") else None
            closed = parse_timestamp(pr["closed_at"], "PR.closed_at") if pr.get("closed_at") else None
            if merged:
                status = "MERGED"
                if not closed or merged > now:
                    raise ValueError("invalid merged PR chronology")
                events.append({"date": merged.date().isoformat(), "type": "merged", "url": url})
            elif pr.get("state") == "open":
                status = "OPEN"
                if closed:
                    raise ValueError("open PR has closed_at")
            elif pr.get("state") == "closed":
                status = "CLOSED_UNMERGED"
                if not closed or closed > now:
                    raise ValueError("closed PR has no valid closed_at")
                events.append({"date": closed.date().isoformat(), "type": "closed_unmerged", "url": url})
            else:
                raise ValueError("unrecognized original PR status")
            approved_closed = False
            if status == "CLOSED_UNMERGED":
                approved_closed = review_approval(client, original, number, closed)
            events.append({"date": created.date().isoformat(), "type": "published", "url": url})
            statuses[status] += 1
            records.append({"url": url, "status": status, "published_at": created.isoformat(),
                            "merged_at": merged.isoformat() if merged else None,
                            "closed_at": closed.isoformat() if closed else None,
                            "closed_with_approval_review": approved_closed})
        except (APIError, ValueError, TypeError, KeyError) as exc:
            warnings.append(f"{url}: {exc}")
    total = len(refs)
    complete = not warnings and len(records) == total
    return {
        "observed_at": now.isoformat().replace("+00:00", "Z"),
        "source": "verified fork-local links + first-party GitHub PR and review APIs",
        "scope": "linked PRs from verified .opensiro/ metadata; NOT all historic research or user benefit",
        "metadata_forks": len(snapshot["forks"]),
        "independent_contributions": sum(len(x.get("contributions", [])) for x in snapshot["forks"]),
        "total_linked_prs": total,
        "complete": complete,
        "warnings": warnings,
        "summary": {
            "published": sum(1 for r in records if r.get("published_at")),
            "merged": statuses["MERGED"],
            "open": statuses["OPEN"],
            "closed_unmerged": statuses["CLOSED_UNMERGED"],
            "closed_with_approval_review": sum(1 for r in records if r["closed_with_approval_review"]),
            "unknown": total - len(records),
        },
        "events": sorted(events, key=lambda x: (x["date"], x["type"], x["url"])),
        "prs": records,
    }


def check_complete(report):
    if not report.get("complete") or report.get("summary", {}).get("unknown"):
        raise ValueError("refuse to render complete-looking chart from incomplete live PR readback")
    summary = report["summary"]
    if summary["published"] != report["total_linked_prs"]:
        raise ValueError("missing publication dates")
    if summary["merged"] + summary["open"] + summary["closed_unmerged"] != summary["published"]:
        raise ValueError("non-partitioned PR status counts")
    if summary["closed_with_approval_review"] > summary["closed_unmerged"]:
        raise ValueError("approval subset greater than closed count")


def svg(report, weeks=53):
    check_complete(report)
    if not isinstance(weeks, int) or not (4 <= weeks <= 54):
        raise ValueError("weeks must be between 4 and 54")
    end = parse_timestamp(report["observed_at"], "observed_at").date()
    # GitHub-like weeks run Sunday -> Saturday; the rightmost column contains today.
    first = end - timedelta(days=7 * (weeks - 1) + ((end.weekday() + 1) % 7))
    count = Counter(x["date"] for x in report["events"])
    kinds = {d: Counter(e["type"] for e in report["events"] if e["date"] == d) for d in count}
    x0, y0, step, size = 57, 92, 14, 11
    width = x0 + weeks * step + 28
    height = 240
    summary = report["summary"]
    text = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="OpenSiro external pull request activity heatmap">',
            '<style>text{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif;fill:#24292f} .muted{font-size:11px;fill:#57606a} .big{font-size:21px;font-weight:600} .date{font-size:10px;fill:#57606a}</style>',
            '<rect width="100%" height="100%" fill="#ffffff"/>',
            f'<defs><pattern id="days" width="{step}" height="{step}" patternUnits="userSpaceOnUse" patternTransform="translate({x0} {y0})"><rect width="{size}" height="{size}" rx="2" fill="{COLORS[0]}"/></pattern></defs>',
            f'<rect x="{x0}" y="{y0}" width="{weeks*step}" height="{7*step}" fill="url(#days)"/>',
            '<text x="16" y="24" font-size="16" font-weight="600">External PR activity · OpenSiro</text>',
            f'<text x="16" y="42" class="muted">UTC · observed {escape(report["observed_at"])} · {report["metadata_forks"]} verified metadata forks · {report["independent_contributions"]} improvements</text>']
    badges = [("Published", summary["published"]), ("Merged", summary["merged"]),
              ("Open", summary["open"]), ("Closed unmerged", summary["closed_unmerged"]),
              ("Closed w/ APPROVED review", summary["closed_with_approval_review"])]
    for i, (title, value) in enumerate(badges):
        x = 16 + i * (width - 18) / 5
        text.append(f'<text x="{x:.1f}" y="64" font-size="13" font-weight="600">{value}</text>')
        text.append(f'<text x="{x:.1f}" y="78" class="date">{escape(title)}</text>')
    for weekday, lbl in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        text.append(f'<text x="16" y="{y0+weekday*step+9}" class="date">{lbl}</text>')
    last_month = None
    for w in range(weeks):
        sunday = first + timedelta(days=7*w)
        if sunday.month != last_month and sunday <= end:
            text.append(f'<text x="{x0 + w*step}" y="88" class="date">{sunday.strftime("%b")}</text>')
            last_month = sunday.month
        for day in range(7):
            d = sunday + timedelta(days=day)
            x = x0 + w*step
            y = y0 + day*step
            if d > end:
                continue
            n = count.get(d.isoformat(), 0)
            if n == 0:
                continue
            fill = COLORS[1 if n == 1 else 2 if n <= 3 else 3 if n <= 6 else 4]
            category = kinds.get(d.isoformat(), {})
            hint = f'{d.isoformat()}: {n} events (published {category.get("published",0)}, merged {category.get("merged",0)}, closed unmerged {category.get("closed_unmerged",0)})'
            text.append(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="2" fill="{fill}"><title>{escape(hint)}</title></rect>')
    text.extend(['<text x="16" y="210" class="muted">Each square = published, merged or closed-unmerged PR events on that UTC day; review approval is a subset, not an event.</text>',
                 '<text x="16" y="228" class="muted">Bounded to metadata-linked PRs, not all historical research or deployed benefit. On-demand snapshot, not live.</text>', '</svg>'])
    return "\n".join(text) + "\n"


def markdown(report):
    check_complete(report)
    s = report["summary"]
    lines = ["# OpenSiro external PR activity", "",
             f"Observed **{report['observed_at']}** (UTC). This is an **on-demand, dated** first-party GitHub readback of PR URLs linked from verified fork-local metadata; not all historical research, not a live service or a benefit KPI.", "",
             "![External PR activity](activity.svg)", "", "| PR state / metric | Count |", "| --- | ---: |",
             f"| Published (distinct linked original PR URLs) | **{s['published']}** |",
             f"| Merged | **{s['merged']}** |",
             f"| Open | **{s['open']}** |",
             f"| Closed without merge | **{s['closed_unmerged']}** |",
             f"| Of closed-unmerged: an APPROVED review found | **{s['closed_with_approval_review']}** |", "",
             f"Coverage: **{report['metadata_forks']}** source-verified forks, **{report['independent_contributions']}** improvement records, **{report['total_linked_prs']}** distinct external PR URLs; the first-party PR readback was complete at observation time.", "",
             "**Interpretation:** MERGED is GitHub's actual merged_at, while CLOSED_UNMERGED has no merge. Review APPROVED means an explicit GitHub review object (latest non-comment review per reviewer before close), **not** a merge, maintainer's verbal endorsement, or deployed value. The approved-closed value is **within**, not additional to, closed-unmerged. Replacement PR chains (e.g., Henterprise #1/#3) can create multiple published PRs but still belong to one improvement; all PR URLs are counted once.", "",
             "The graph counts PR lifecycle events on their original UTC dates: publication, merge and closure without merge. It does not date all historical work by the metadata migration day. Source owners remain original GitHub repositories; this file is a disposable derived snapshot. Regenerate with scripts/aggregate.py + scripts/activity.py; do not schedule a migration observer to update it.", ""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="JSON report from scripts/aggregate.py")
    parser.add_argument("--svg", type=Path, required=True, help="target SVG, write only after complete first-party readback")
    parser.add_argument("--markdown", type=Path, help="optional report Markdown")
    parser.add_argument("--weeks", type=int, default=53)
    args = parser.parse_args(argv)
    try:
        snapshot = json.loads(args.input.read_text(encoding="utf-8"))
        report = collect(GitHub(os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")), snapshot)
        svg_text = svg(report, weeks=args.weeks)
        markdown_text = markdown(report) if args.markdown else None
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))
    args.svg.write_text(svg_text, encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(markdown_text, encoding="utf-8")
    print(json.dumps({"observed_at": report["observed_at"], "scope": report["scope"],
                      "summary": report["summary"], "complete": report["complete"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
