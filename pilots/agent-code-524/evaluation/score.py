#!/usr/bin/env python3
"""Score paired agent-code #524 reviews from separately adjudicated observations.

This command never starts a model and NEVER infers successful improvement.
It refuses incomplete, unpaired, or unadjudicated observations.
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path


def require(ok, why):
    if not ok:
        raise ValueError(why)


def load(path):
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    require(obj.get("schema_version") == 1, f"{path}: schema_version must be 1")
    return obj


def score(cases_doc, runs_doc, judgements_doc):
    cases = {}
    for c in cases_doc["cases"]:
        require(c["id"] not in cases, f"duplicate case {c['id']}")
        require(isinstance(c["truth_ids"], list) and
                len(c["truth_ids"]) == len(set(c["truth_ids"])), f"invalid truths {c['id']}")
        require(c.get("source_sha") and c.get("input_sha256"), f"missing case pins {c['id']}")
        cases[c["id"]] = c
    require(cases, "at least one predeclared case required")

    by_id, pairs = {}, defaultdict(dict)
    for run in runs_doc["runs"]:
        rid, cid, arm = run["id"], run["case_id"], run["arm"]
        require(rid not in by_id, f"duplicate run {rid}")
        require(cid in cases, f"unknown case {cid}")
        require(arm in ("baseline", "isolated"), f"invalid arm {arm}")
        require(run["source_type"] in ("live_provider", "mock_provider", "manual"),
                f"unknown source type in {rid}")
        c = cases[cid]
        require(run["source_sha"] == c["source_sha"] and
                run["input_sha256"] == c["input_sha256"],
                f"case source/input mismatch in {rid}")
        require(isinstance(run["repeat"], int) and run["repeat"] > 0, f"bad repeat {rid}")
        require(isinstance(run["findings"], list), f"missing findings {rid}")
        require(run.get("model") and run.get("context_condition"), f"missing arm metadata {rid}")
        require(isinstance(run.get("duration_ms"), int) and run["duration_ms"] >= 0,
                f"bad duration {rid}")
        require(isinstance(run.get("total_tokens"), int) and run["total_tokens"] >= 0,
                f"bad token usage {rid}")
        key = (cid, run["repeat"], run["context_condition"])
        require(arm not in pairs[key], f"duplicate {arm} in pair {key}")
        pairs[key][arm] = run
        by_id[rid] = run
    require(by_id, "no observations: quality outcome is NOT_MEASURED")
    require(set(cases) == {k[0] for k in pairs}, "one or more predeclared cases lack observations")
    require(all(set(v) == {"baseline", "isolated"} for v in pairs.values()),
            "unpaired arm: both baseline and isolated are required")
    for k, v in pairs.items():
        b, i = v["baseline"], v["isolated"]
        require(b["model"] == i["model"] and b["source_type"] == i["source_type"],
                f"model/source type mismatch in pair {k}")
        # The rubrics/prompts can differ by arm, but their hashes MUST be recorded.
        require(b.get("prompt_sha256") and i.get("prompt_sha256"),
                f"unrecorded prompts in pair {k}")

    judgements = judgements_doc["adjudications"]
    require(isinstance(judgements, dict) and set(judgements) == set(by_id),
            "adjudication must contain exactly all run IDs (including zero-finding runs)")
    require(judgements_doc.get("blinded_adjudication") is True,
            "blinded_adjudication must be explicitly attested, not silently assumed")
    totals = {arm: dict(tp=0, fp=0, fn=0, clean_fp=0, tokens=0, duration_ms=0, runs=0)
              for arm in ("baseline", "isolated")}
    per_run = {}
    for rid, run in by_id.items():
        case = cases[run["case_id"]]
        matches = judgements[rid]
        require(isinstance(matches, list) and len(matches) == len(run["findings"]),
                f"adjudication count mismatch in {rid}")
        require(all(m is None or (isinstance(m, str) and m in case["truth_ids"])
                    for m in matches), f"unknown truth ID in {rid}")
        used = set()
        tp = 0
        for m in matches:
            if m is not None and m not in used:
                used.add(m)
                tp += 1
        fp, fn = len(matches) - tp, len(case["truth_ids"]) - tp
        require(fn >= 0, f"negative FN {rid}")
        st = totals[run["arm"]]
        st["tp"] += tp
        st["fp"] += fp
        st["fn"] += fn
        st["tokens"] += run["total_tokens"]
        st["duration_ms"] += run["duration_ms"]
        st["runs"] += 1
        if not case["truth_ids"]:
            st["clean_fp"] += fp
        per_run[rid] = {"tp": tp, "fp": fp, "fn": fn}
    for st in totals.values():
        st["precision"] = round(st["tp"] / (st["tp"] + st["fp"]), 4) if st["tp"] + st["fp"] else None
        st["recall"] = round(st["tp"] / (st["tp"] + st["fn"]), 4) if st["tp"] + st["fn"] else None
        st["avg_tokens"] = round(st["tokens"] / st["runs"], 2)
        st["avg_duration_ms"] = round(st["duration_ms"] / st["runs"], 2)
    deltas = []
    for (cid, rep, condition), two in sorted(pairs.items()):
        b, i = two["baseline"], two["isolated"]
        deltas.append({
            "case_id": cid, "repeat": rep, "context_condition": condition,
            "tp_delta": per_run[i["id"]]["tp"] - per_run[b["id"]]["tp"],
            "fp_delta": per_run[i["id"]]["fp"] - per_run[b["id"]]["fp"],
            "token_delta": i["total_tokens"] - b["total_tokens"],
            "duration_ms_delta": i["duration_ms"] - b["duration_ms"]
        })
    types = sorted({r["source_type"] for r in by_id.values()})
    return {
        "evidence_class": ("LIVE_OBSERVATIONS_REQUIRE_INDEPENDENT_AUDIT"
                           if types == ["live_provider"] else "NON_LIVE_NOT_PRODUCT_BENEFIT"),
        "benefit_verdict": "NOT_AUTO_ADJUDICATED",
        "provider_types": types, "pairs": len(pairs), "case_count": len(cases),
        "baseline": totals["baseline"], "isolated": totals["isolated"],
        "paired_deltas": deltas,
        "limitations": [
            "Finding-to-truth mappings require genuinely blinded human verification.",
            "Recorded provenance is a declaration, not cryptographic proof of live inference.",
            "A prompt/rubric change is a confounder; this score does not isolate the effect of context isolation.",
            "No effect size, statistical power, or causal improvement is inferred by this script."
        ]
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cases", required=True)
    p.add_argument("--runs", required=True)
    p.add_argument("--adjudications", required=True)
    args = p.parse_args()
    try:
        print(json.dumps(score(load(args.cases), load(args.runs),
                               load(args.adjudications)), indent=2, sort_keys=True))
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        p.exit(2, f"INSUFFICIENT_EVIDENCE: {exc}\n")


if __name__ == "__main__":
    main()
