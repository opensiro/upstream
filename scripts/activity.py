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

BASE_CELL = "#eaeef2"
# Separate intensity scales: an empty stripe is gray, positive activity is typed.
BAND_COLORS = {
    "published": (BASE_CELL, "#9be9a8", "#40c463", "#30a14e", "#216e39"),
    "merged": (BASE_CELL, "#c7dfff", "#8ab4f8", "#1f6feb", "#054da7"),
    "closed_unmerged": (BASE_CELL, "#ffe1a6", "#f2b84b", "#d29922", "#895700"),
}
APPROVAL_COLOR = "#8250df"


def band_color(kind, count):
    """Independent four-level color scale, never mix unlike event types."""
    if count < 0:
        raise ValueError("negative event count")
    if count == 0:
        return BASE_CELL
    return BAND_COLORS[kind][1 if count == 1 else 2 if count <= 3 else 3 if count <= 6 else 4]


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
                # Add the closure event only after the original GitHub review readback.
            else:
                raise ValueError("unrecognized original PR status")
            approved_closed = False
            if status == "CLOSED_UNMERGED":
                approved_closed = review_approval(client, original, number, closed)
                events.append({"date": closed.date().isoformat(), "type": "closed_unmerged",
                               "approved": approved_closed, "url": url})
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
    events = report.get("events", [])
    kinds = Counter(e.get("type") for e in events)
    for kind, total in (("published", summary["published"]),
                        ("merged", summary["merged"]),
                        ("closed_unmerged", summary["closed_unmerged"])):
        if kinds[kind] != total:
            raise ValueError(f"{kind} event count does not match source PR totals")
    approved_events = sum(bool(e.get("approved")) for e in events
                          if e.get("type") == "closed_unmerged")
    if approved_events != summary["closed_with_approval_review"]:
        raise ValueError("approved closure markers do not match review-derived count")


def svg(report, weeks=53):
    check_complete(report)
    if not isinstance(weeks, int) or not (4 <= weeks <= 54):
        raise ValueError("weeks must be between 4 and 54")
    end = parse_timestamp(report["observed_at"], "observed_at").date()
    # GitHub-like Sunday-Saturday weeks; rightmost column holds observation day.
    first = end - timedelta(days=7 * (weeks - 1) + ((end.weekday() + 1) % 7))
    kinds_by_day = {}
    approvals_by_day = Counter()
    for event in report["events"]:
        day = event["date"]
        kinds_by_day.setdefault(day, Counter())[event["type"]] += 1
        if event["type"] == "closed_unmerged" and event.get("approved"):
            approvals_by_day[day] += 1
    x0, y0, step, size = 57, 100, 18, 15
    width = x0 + weeks * step + 30
    height = 304
    summary = report["summary"]
    text = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="OpenSiro external pull request activity calendar: green published, blue merged, amber closed unmerged, purple dot approved review">',
            '<style>text{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif;fill:#24292f} .muted{font-size:11px;fill:#57606a} .date{font-size:10px;fill:#57606a}</style>',
            '<rect width="100%" height="100%" fill="#ffffff"/>',
            f'<defs><pattern id="days" width="{step}" height="{step}" patternUnits="userSpaceOnUse" patternTransform="translate({x0} {y0})"><rect width="{size}" height="{size}" rx="2" fill="{BASE_CELL}"/></pattern></defs>',
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
        text.append(f'<text x="16" y="{y0 + weekday*step + 11}" class="date">{lbl}</text>')
    last_month = None
    for w in range(weeks):
        sunday = first + timedelta(days=7*w)
        if sunday.month != last_month and sunday <= end:
            text.append(f'<text x="{x0 + w*step}" y="{y0-4}" class="date">{sunday.strftime("%b")}</text>')
            last_month = sunday.month
        for weekday in range(7):
            day = sunday + timedelta(days=weekday)
            if day > end:
                continue
            key = day.isoformat()
            counts = kinds_by_day.get(key)
            if not counts:
                continue
            published, merged, closed = (counts["published"], counts["merged"],
                                         counts["closed_unmerged"])
            total = published + merged + closed
            if not total:
                continue
            approved = approvals_by_day[key]
            if approved > closed:
                raise ValueError(f"{key}: approved closures exceed closures")
            x, y = x0 + w*step, y0 + weekday*step
            hint = (f"{key}: {total} events (published {published}, merged {merged}, "
                    f"closed unmerged {closed}, of closed with APPROVED review {approved})")
            text.append(f'<g data-date="{key}" data-published="{published}" data-merged="{merged}" data-closed="{closed}" data-approved-closed="{approved}">')
            text.append(f'<title>{escape(hint)}</title>')
            text.append(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="2" fill="{BASE_CELL}"/>')
            for kind, dy in (("published", 1), ("merged", 5.5), ("closed_unmerged", 10)):
                color = band_color(kind, counts[kind])
                text.append(f'<rect x="{x+1}" y="{y+dy}" width="{size-2}" height="3.5" rx="1" fill="{color}"/>')
            if approved:
                # Approval is a marker on the closed-unmerged stripe, not a fourth event.
                text.append(f'<circle cx="{x+size-2.5}" cy="{y+size-2.5}" r="2.6" fill="{APPROVAL_COLOR}" stroke="#ffffff" stroke-width=".7"/>')
            text.append('</g>')
    legend = [("published", "Published"), ("merged", "Merged"), ("closed_unmerged", "Closed unmerged")]
    for i, (kind, label) in enumerate(legend):
        x = 57 + (0 if i == 0 else 146 if i == 1 else 263)
        text.append(f'<rect x="{x}" y="240" width="16" height="9" rx="2" fill="{band_color(kind, 4)}"/>')
        text.append(f'<text x="{x+22}" y="248" class="muted">{label}</text>')
    text.append(f'<circle cx="487" cy="244.5" r="4.5" fill="{APPROVAL_COLOR}"/>')
    text.append('<text x="500" y="248" class="muted">Closed w/ APPROVED review</text>')
    text.extend(['<text x="16" y="274" class="muted">Each day is one square: separate stripe intensities represent counts; hover for exact values. Approval is a subset of closed, not another event.</text>',
                 '<text x="16" y="291" class="muted">Bounded to metadata-linked PRs, not all research or deployed benefit. Dated snapshot, not live.</text>',
                 '</svg>'])
    return "\n".join(text) + "\n"

def markdown(report):
    check_complete(report)
    s = report["summary"]
    lines = ["# OpenSiro external PR activity", "",
             f"Observed **{report['observed_at']}** (UTC). This is a **dated** first-party GitHub readback of PR URLs linked from verified fork-local metadata; not all historical research, not a live service or a benefit KPI.", "",
             "![External PR activity](activity.svg)", "", "| PR state / metric | Count |", "| --- | ---: |",
             f"| Published (distinct linked original PR URLs) | **{s['published']}** |",
             f"| Merged | **{s['merged']}** |",
             f"| Open | **{s['open']}** |",
             f"| Closed without merge | **{s['closed_unmerged']}** |",
             f"| Of closed-unmerged: an APPROVED review found | **{s['closed_with_approval_review']}** |", "",
             f"Coverage: **{report['metadata_forks']}** source-verified forks, **{report['independent_contributions']}** improvement records, **{report['total_linked_prs']}** distinct external PR URLs; the first-party PR readback was complete at observation time.", "",
             "**Interpretation:** MERGED is GitHub's actual merged_at, while CLOSED_UNMERGED has no merge. Review APPROVED means an explicit GitHub review object (latest non-comment review per reviewer before close), **not** a merge, maintainer's verbal endorsement, or deployed value. The approved-closed value is **within**, not additional to, closed-unmerged. Replacement PR chains (e.g., Henterprise #1/#3) can create multiple published PRs but still belong to one improvement; all PR URLs are counted once.", "",
             "**Reading one square:** three independent horizontal stripes: green = published, blue = merged, amber = closed without merge. Darker stripe means more events of **that type**, not a combined score. A purple dot marks a closed-unmerged PR whose latest eligible GitHub review was `APPROVED`; it is a subset of closed-unmerged, not an extra event. If none were approved in this snapshot, no purple dots appear. The per-day tooltip is embedded in the SVG; the breakdown table below remains readable when a Markdown renderer does not expose SVG tooltips.", "",
             "Events use their original UTC publication, merge or closure dates, not metadata migration dates. Source owners remain original GitHub repositories; this file is a disposable derived snapshot. This derived view is refreshed from verified fork metadata and original GitHub PR facts; it is not a migration ledger or automatic external PR observer.", ""]
    per_day = {}
    for event in report["events"]:
        values = per_day.setdefault(event["date"], Counter())
        values[event["type"]] += 1
        if event["type"] == "closed_unmerged" and event.get("approved"):
            values["approved_closed"] += 1
    lines.extend(["## Daily event counts (UTC)", "",
                  "| Date | Published | Merged | Closed unmerged | With APPROVED review |",
                  "| --- | ---: | ---: | ---: | ---: |"])
    for day, counts in sorted(per_day.items()):
        lines.append(f'| {day} | {counts["published"]} | {counts["merged"]} | '
                     f'{counts["closed_unmerged"]} | {counts["approved_closed"]} |')
    lines.append("")
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
