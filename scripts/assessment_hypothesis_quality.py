#!/usr/bin/env python3
"""Read-only, non-KPI screening quality census from frozen Upstream batches.

Never confuses source-first hypotheses, native test outcomes, publication
receipts, external PR adoption, and deployed product benefit. No GitHub writes.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re

import assessment_candidate_batches as batches
import portfolio_reconcile

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "data/assessment-candidate-batches"
READBACKS = ROOT / "data/external-pr-publication-readbacks"
NUMBER = re.compile(r"\d{4}-\d{2}-\d{2}-(\d+)\.json\Z")


def frozen_files(folder=MANIFESTS):
    found = []
    for path in Path(folder).glob("*.json"):
        m = NUMBER.fullmatch(path.name)
        if m:
            found.append((int(m.group(1)), path))
    found.sort(key=lambda x: x[0])
    if len({n for n, _ in found}) != len(found):
        raise ValueError("Duplicate frozen batch numbers")
    return found


def publication_readbacks(root=READBACKS):
    result = {}
    for path in sorted(Path(root).glob("????-??-??.json")):
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        if (snapshot.get("schema_version") != 1
                or snapshot.get("observed_at") != path.stem
                or snapshot.get("authenticated_actor") != "xLagerFeuer"
                or not isinstance(snapshot.get("cases"), list)):
            raise ValueError(f"Invalid publication readback: {path}")
        for item in snapshot["cases"]:
            ident, source, url = item.get("id"), item.get("repository"), item.get("pr_url")
            if (not isinstance(ident, str) or not ident or not isinstance(source, str)
                    or not isinstance(url, str)
                    or not isinstance(item.get("public_fork"), str)
                    or not item["public_fork"].startswith("opensiro-contributions/")
                    or not re.fullmatch(r"[0-9a-f]{40}", item.get("head_sha") or "")
                    or type(item.get("pr_commits")) is not int or item["pr_commits"] < 1):
                raise ValueError(f"Invalid published PR case in {path}")
            repo, _ = portfolio_reconcile.identity(url)
            if repo.casefold() != source.casefold() or ident in result:
                raise ValueError("Publication identity duplicate/source mismatch")
            result[ident] = {"source": source, "url": url, "receipt": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)}
    return result


def audit(files, readbacks=None, prereg_folder=MANIFESTS):
    if not files:
        raise ValueError("Empty frozen cohort")
    readbacks = publication_readbacks() if readbacks is None else readbacks
    per_batch, rows, seen = [], [], set()
    for n, path in files:
        manifest = batches.validate(json.loads(Path(path).read_text(encoding="utf-8")))
        if int(manifest["batch_id"].split("-")[-1]) != n:
            raise ValueError("Batch identity/filename mismatch")
        prereg = Path(prereg_folder) / path.name.replace(".json", "-HYPOTHESES.md")
        if not prereg.is_file():
            raise ValueError(f"Missing source-first hypothesis packet for batch {n}")
        batch_rows = []
        for candidate in manifest["candidates"]:
            ident, source = candidate["id"], candidate["source"]
            if ident in seen:
                raise ValueError("Duplicate candidate across screened batches")
            seen.add(ident)
            pub = readbacks.get(ident)
            if pub and pub["source"].casefold() != source.casefold():
                raise ValueError("Dated publication receipt mismatches source")
            row = {"candidate_id": ident, "source": source,
                   "assessment_path": candidate["assessment_path"],
                   "index_sha": manifest["index_sha"], "function": candidate["function"],
                   "origin": candidate["origin"], "stage": candidate["stage"],
                   "published_pr": pub["url"] if pub else None,
                   "publication_receipt": pub["receipt"] if pub else None,
                   "native_benefit_verified": None,
                   "maintainer_adoption_verified": None,
                   "user_benefit_measured": None}
            batch_rows.append(row)
            rows.append(row)
        per_batch.append({"batch_number": n, "batch_id": manifest["batch_id"],
                          "manifest": str(Path(path).relative_to(ROOT)),
                          "preregistration_packet": str(prereg.relative_to(ROOT)),
                          "index_sha": manifest["index_sha"],
                          "screened": len(batch_rows),
                          "stages": dict(sorted(Counter(x["stage"] for x in batch_rows).items())),
                          "prospective_origin_claims": sum(x["origin"] == "ASSESSMENT_DERIVED" for x in batch_rows),
                          "published_readbacks": sum(x["published_pr"] is not None for x in batch_rows)})
    if len({x["source"].casefold() for x in rows}) != len(rows):
        raise ValueError("Selected screening cohorts overlap in original sources")
    stages = Counter(row["stage"] for row in rows)
    origin = Counter(row["origin"] for row in rows)
    return {"schema_version": 1, "scope": "frozen_screening_readback_only",
            "cohort": {"first": files[0][0], "last": files[-1][0],
                        "batch_count": len(files), "screened": len(rows)},
            "counts": {"stages": dict(sorted(stages.items())), "origins": dict(sorted(origin.items())),
                       "derived_unblocked": sum(r["origin"] == "ASSESSMENT_DERIVED" and
                                                r["stage"] not in {"BLOCKED_EVIDENCE", "CLOSED_NO_CHANGE"}
                                                for r in rows),
                       "dated_published_source_receipts": sum(r["published_pr"] is not None for r in rows),
                       "accepted_merged_changes": None,
                       "measured_product_benefits": None},
            "gates": {"canonical_index_remote": "NOT_REVALIDATED_IN_OFFLINE_CENSUS",
                      "preregistration_chronology": "CHECKPOINT_PACKET_PRESENT_ONLY",
                      "independent_native_red_green": "NOT_REVALIDATED_IN_OFFLINE_CENSUS",
                      "live_external_pr_status": "NOT_REVALIDATED_IN_OFFLINE_CENSUS",
                      "source_verified_acceptance": "NOT_LIVE_CHECKED"},
            "batches": per_batch, "candidates": rows}


def markdown(result):
    c, stats = result["cohort"], result["counts"]
    lines = [f"# Assessment-first hypothesis quality — frozen batches {c['first']}–{c['last']}", "",
             "**Read-only quality intake baseline, not a new KPI.** Source: frozen Upstream",
             "manifests and dated publication readbacks. This is not a live PR, accepted-outcome,",
             "native test, preregistration-chronology or deployed-benefit audit.", "",
             f"**Screened:** {c['screened']} candidates in {c['batch_count']} frozen batches.",
             f"**Stages:** " + ", ".join(f"{k} {v}" for k, v in stats["stages"].items()) + ".",
             f"**Recorded origins:** " + ", ".join(f"{k} {v}" for k, v in stats["origins"].items()) + ".",
             f"**Derived origin without blocking/no-change stage:** {stats['derived_unblocked']}.",
             f"**Exact dated published PR receipts:** {stats['dated_published_source_receipts']}.",
             "**Live verified merges / measured product benefit:** not evaluated by this offline census.", "",
             "| Batch | Screened | Status counts | Prospective derived origins | Exact published PR receipts |",
             "| --- | ---: | --- | ---: | ---: |"]
    for b in result["batches"]:
        state = ", ".join(f"{k}: {v}" for k, v in b["stages"].items())
        lines.append(f"| [{b['batch_number']}](../{b['manifest']}) | {b['screened']} | {state} | "
                     f"{b['prospective_origin_claims']} | {b['published_readbacks']} |")
    lines += ["", "## Source-backed derived hypotheses (not an outcome count)", "",
              "| Candidate | Frozen stage | Dated original PR |",
              "| --- | --- | --- |"]
    for r in result["candidates"]:
        if r["origin"] == "ASSESSMENT_DERIVED":
            pr = f"[PR]({r['published_pr']})" if r["published_pr"] else "Not in dated readbacks"
            lines.append(f"| `{r['candidate_id']}` ({r['source']}) | {r['stage']} | {pr} |")
    lines += ["", "## Attribution and independent checks still required", "",
              "The frozen origin label is not sufficient to claim true preregistration chronology,",
              "an independently validated native fix, maintainer acceptance or measured user effect.",
              "Inspect the exact pre-source commit, target-native before/after runner receipt,",
              "external PR and independent accepted-source export case by case. A blocker can mean",
              "missing permissions/licence/tooling rather than a false VSM hypothesis. `CLOSED_NO_CHANGE`",
              "is a valid negative screen, not a failed contribution. Do not sum these numbers",
              "with the overlapping 42-PR live portfolio or with the two accepted merged-change outputs.", ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--last", type=int, default=8, help="Last N merged frozen batch manifests (default 8)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--output-json", type=Path)
    args = ap.parse_args()
    if args.last < 1:
        ap.error("--last must be positive")
    files = frozen_files()
    if len(files) < args.last:
        ap.error("Fewer frozen manifests than requested")
    result = audit(files[-args.last:])
    if args.output_json:
        args.output_json.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False) if args.json else markdown(result),
          end="\n" if args.json else "")


if __name__ == "__main__":
    main()
