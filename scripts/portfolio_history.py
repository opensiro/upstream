#!/usr/bin/env python3
"""Compare saved read-only portfolio observations from the same exact PR cohort.

Accepts local JSON artifacts only. Does not call GitHub or claim product adoption.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path

import portfolio_reconcile


def series(reports):
    if not reports:
        raise ValueError("At least one observation is required")
    baseline = None
    dates = set()
    rows = []
    for report in reports:
        if not isinstance(report, dict) or report.get("schema_version") != 1:
            raise ValueError("Unsupported portfolio observation schema")
        observed_at = report.get("observed_at")
        if not isinstance(observed_at, str):
            raise ValueError("Observation timestamp is missing")
        try:
            timestamp = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("Malformed observation timestamp") from exc
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("Observation timestamp must have a timezone")
        normalized = timestamp.isoformat()
        if normalized in dates:
            raise ValueError("Duplicate observation timestamp")
        dates.add(normalized)

        # Recalculate the identity key from every exact URL and membership;
        # outcome-only changes never affect it. Reject mixed cohorts.
        watch = portfolio_reconcile.summarize(report, group="watchlist")
        broad = portfolio_reconcile.summarize(report)
        fingerprint = portfolio_reconcile.cohort_fingerprint(report["records"])
        if "cohort_sha256" not in report:
            raise ValueError("Historical observation lacks cohort fingerprint")
        if baseline is None:
            baseline = fingerprint
        elif baseline != fingerprint:
            raise ValueError("Cannot compare different PR cohorts without a reviewed mapping")
        rows.append({"timestamp": timestamp, "observed_at": observed_at,
                     "watchlist": watch, "union": broad})
    return sorted(rows, key=lambda row: row["timestamp"])


def render(rows):
    lines = ["# External PR observations — cohort-stable history", "",
             "Read-only GitHub PR lifecycle observations; **not** a verified adoption or product-benefit rate.",
             "All rows have the same exact source URL/group fingerprint. Open and unverifiable PRs are",
             "excluded from resolved-only denominators; historical Product-native fit is deprecated.", "",
             "| Observed UTC | Reviewed watchlist (merged/resolved) | Watchlist pending | Broad union (merged/resolved) | Broad pending |",
             "| --- | ---: | ---: | ---: | ---: |"]
    for row in rows:
        def ratio(s):
            return f"{s['merged']}/{s['resolved']} ({s['rate']:.1%})" if s["rate"] is not None else "N/A"

        watch, broad = row["watchlist"], row["union"]
        lines.append(f"| {row['timestamp'].strftime('%Y-%m-%d %H:%M:%S UTC')} | "
                     f"{ratio(watch)} | {watch['open']} open / {watch['unverifiable']} unavailable | "
                     f"{ratio(broad)} | {broad['open']} open / {broad['unverifiable']} unavailable |")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("observations", type=Path, nargs="+", help="Downloaded per-run JSON artifacts")
    args = parser.parse_args()
    reports = [json.loads(path.read_text(encoding="utf-8")) for path in args.observations]
    print(render(series(reports)), end="")


if __name__ == "__main__":
    main()
