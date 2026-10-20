#!/usr/bin/env python3
"""Read-only Index-wide per-function improvement hypothesis coverage.

A verified local git object is NOT an attestation of the live canonical Index.
A review receipt is a human/agent declaration, NOT independent native product
fit, proposal selection, permission or an upstream contribution.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

from inspect_improvement_candidates import CandidateError, inspect

SHA = re.compile(r"^[0-9a-f]{40}$")
ASSESSMENT = re.compile(r"^assessments/([a-z0-9-]{2})/([a-z0-9-]+)\.md$")
REPO = re.compile(r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/?$")
FUNCTIONS = ("S1", "S2", "S3", "S3*", "S4", "S5")
KEYS = dict(zip(FUNCTIONS, ("autonomy_s1", "autonomy_s2", "autonomy_s3",
                            "autonomy_s3_star", "autonomy_s4", "autonomy_s5")))
GRADES = {"A", "C", "P", "A(P)", "C(P)", "—", "?"}
OUTCOMES = {"UNREVIEWED", "REVIEWED_ZERO", "HYPOTHESES_RECORDED", "BLOCKED_EVIDENCE"}
RESULT_FIELDS = {"outcome", "rationale", "candidate_ids"}
RECEIPT_FIELDS = {"schema_version", "index_sha", "assessment_path",
                  "review_ref", "reviewed_at", "functions"}
HEADINGS = {
    "S1": "S1", "S2": "S2", "S3": "S3",
    "S3*": "S3\\*", "S4": "S4", "S5": "S5",
}


class SweepError(ValueError):
    """Fail closed when a pinned assessment or review record is ambiguous."""


def require(condition, message):
    if not condition:
        raise SweepError(message)


def git(root, *args):
    try:
        proc = subprocess.run(["git", "-C", str(root), *args],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=20, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise SweepError("Cannot inspect the frozen local Index Git objects") from None
    require(proc.returncode == 0, "Requested Index git object is unavailable")
    require(len(proc.stdout) <= 1024 * 1024, "Git object output too large")
    return proc.stdout


def parse_assessment(raw, path):
    """Parse canonical scalar identity while allowing historical extra metadata."""
    require(ASSESSMENT.fullmatch(path) is not None, "Invalid assessment path")
    require(len(raw) <= 256 * 1024, "Assessment exceeds read-only size bound")
    try:
        lines = raw.decode("utf-8").splitlines()
    except UnicodeError:
        raise SweepError("Invalid assessment encoding") from None
    require(lines and lines[0] == "---", "Missing assessment frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise SweepError("Unterminated assessment frontmatter") from None
    require(1 < end <= 100, "Unexpected assessment frontmatter length")
    fields = {}
    for line in lines[1:end]:
        require(":" in line, "Invalid assessment scalar metadata")
        k, v = [part.strip() for part in line.split(":", 1)]
        require(k and k not in fields and re.fullmatch(r"[a-z][a-z0-9_]*", k),
                "Duplicate/invalid assessment metadata")
        require(v and not any(ord(c) < 32 for c in v), "Empty/invalid assessment metadata")
        fields[k] = v.strip("'\"")
    for k in ("harness_id", "repository", "review_ref", "status", *KEYS.values()):
        require(k in fields, "Missing required Index identity/function: " + k)
    part = ASSESSMENT.fullmatch(path)
    require(fields["harness_id"] == part.group(2)
            and part.group(2).startswith(part.group(1)),
            "Assessment path/harness ID mismatch")
    require(REPO.fullmatch(fields["repository"]) is not None,
            "Invalid assessment upstream repository identity")
    require(SHA.fullmatch(fields["review_ref"]) is not None,
            "Assessment review_ref is not a pinned commit")
    require(fields["status"] in ("included", "excluded-no-agentic-vsm", "proposed"),
            "Unknown assessment publication status")
    if fields["status"] == "included":
        for fn in FUNCTIONS:
            require(fields[KEYS[fn]] in GRADES, "Invalid autonomy state for " + fn)
            # This checks section existence, NOT that it was critically reviewed.
            pattern = r"^##\s+" + HEADINGS[fn] + r"\s+[—-]\s+"
            require(re.search(pattern, "\n".join(lines[end + 1:]), re.M) is not None,
                    "Included assessment missing function section " + fn)
    return {
        "assessment_path": path, "harness_id": fields["harness_id"],
        "source": "/".join(REPO.fullmatch(fields["repository"]).groups()),
        "review_ref": fields["review_ref"], "publication_status": fields["status"],
        "grades": {fn: fields[KEYS[fn]] for fn in FUNCTIONS},
    }


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON field")
        result[key] = value
    return result


def validate_receipt(root, info, index_sha, candidate_by_id):
    """A review receipt may be incomplete, but cannot assert ungrounded completion."""
    name = info["harness_id"] + ".json"
    path = root / name
    if not path.exists():
        return {fn: "UNREVIEWED" for fn in FUNCTIONS}
    require(not path.is_symlink() and path.is_file(), "Invalid review receipt file")
    require(path.stat().st_size <= 16 * 1024, "Review receipt is too large")
    try:
        data = json.loads(path.read_text(encoding="utf-8"),
                          object_pairs_hook=no_duplicates)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        raise SweepError("Invalid review receipt " + name + ": " + str(exc)) from None
    require(type(data) is dict and set(data) == RECEIPT_FIELDS
            and type(data["schema_version"]) is int and data["schema_version"] == 1,
            "Invalid review receipt schema for " + name)
    for k, expected in (("index_sha", index_sha),
                        ("assessment_path", info["assessment_path"]),
                        ("review_ref", info["review_ref"])):
        require(data[k] == expected, "Review receipt is pinned to a different " + k)
    require(isinstance(data["reviewed_at"], str)
            and re.fullmatch(r"20[0-9]{2}-[01][0-9]-[0-3][0-9]", data["reviewed_at"]),
            "Missing review observation date")
    funcs = data["functions"]
    require(type(funcs) is dict and set(funcs) == set(FUNCTIONS),
            "Review receipt must explicitly address all six function slots")
    reviewed = {}
    for fn in FUNCTIONS:
        entry = funcs[fn]
        require(type(entry) is dict and set(entry) == RESULT_FIELDS,
                "Function review fields missing for " + fn)
        outcome = entry["outcome"]
        rationale = entry["rationale"]
        ids = entry["candidate_ids"]
        require(outcome in OUTCOMES and isinstance(rationale, str)
                and isinstance(ids, list), "Invalid outcome/rationale/candidate IDs " + fn)
        require(len(ids) == len(set(ids)) and all(
            isinstance(x, str) and x in candidate_by_id for x in ids
        ), "Unknown/repeated candidate ID for " + fn)
        if outcome == "UNREVIEWED":
            require(rationale == "" and ids == [],
                    "Unreviewed slot must not claim a finding")
        else:
            require(40 <= len(rationale.strip()) <= 2000 and
                    not any(ord(c) < 32 for c in rationale),
                    "Reviewed function requires a specific rationale " + fn)
        if outcome == "HYPOTHESES_RECORDED":
            require(len(ids) >= 1, "Hypothesis review must link an existing card")
        else:
            require(not ids, "Non-hypothesis outcome cannot claim candidate IDs")
        for cid in ids:
            card = candidate_by_id[cid]
            require(card["index_sha"] == index_sha
                    and card["assessment_path"] == info["assessment_path"]
                    and card["review_ref"] == info["review_ref"]
                    and card["target_repo"].casefold() == info["source"].casefold(),
                    "Candidate origin/target conflicts with reviewed function")
        reviewed[fn] = outcome
    return reviewed


def audit(*, index_root, index_sha, reviews_root, candidate_root, offset=0, limit=10):
    require(isinstance(index_sha, str) and SHA.fullmatch(index_sha),
            "Index SHA must be an immutable 40-character ref")
    root = Path(index_root).resolve()
    require(root.is_dir(), "Frozen Index checkout not found")
    require(Path(git(root, "rev-parse", "--show-toplevel").decode().strip()).resolve() == root,
            "Index root must be exact checkout root")
    require(git(root, "rev-parse", "HEAD").decode().strip() == index_sha,
            "Frozen Index checkout HEAD differs from supplied pin")
    names = git(root, "ls-tree", "-r", "--name-only", index_sha, "--", "assessments").decode().splitlines()
    names = sorted(x for x in names if ASSESSMENT.fullmatch(x))
    require(bool(names) and len(names) <= 30000, "Empty/oversized assessment corpus")
    candidate_by_id = {x["candidate_id"]: x for x in inspect(candidate_root)["candidates"]}
    reviews_root = Path(reviews_root)
    require(reviews_root.is_dir(), "Review receipt directory missing")
    declared_receipts = {x.name for x in reviews_root.iterdir()
                         if x.is_file() and x.name != "README.md"}
    require(all(re.fullmatch(r"[a-z0-9-]+\.json", n) for n in declared_receipts),
            "Unexpected receipt filename")
    count = {"included": 0, "excluded-no-agentic-vsm": 0, "proposed": 0}
    remaining, covered, slots, reviewed_slots = [], [], 0, 0
    found_receipts = set()
    for name in names:
        raw = git(root, "show", index_sha + ":" + name)
        info = parse_assessment(raw, name)
        status = info["publication_status"]
        count[status] += 1
        if status != "included":
            continue
        slots += len(FUNCTIONS)
        receipt_name = info["harness_id"] + ".json"
        if receipt_name in declared_receipts:
            found_receipts.add(receipt_name)
        per = validate_receipt(reviews_root, info, index_sha, candidate_by_id)
        checked = sum(value in {"REVIEWED_ZERO", "HYPOTHESES_RECORDED"}
                      for value in per.values())
        reviewed_slots += checked
        record = {
            "harness_id": info["harness_id"],
            "assessment_path": name, "source": info["source"],
            "review_ref": info["review_ref"],
            "reviewed_functions": checked, "function_outcomes": per,
            "index_grades": info["grades"],
        }
        if checked == len(FUNCTIONS):
            covered.append(record)
        else:
            remaining.append(record)
    require(declared_receipts == found_receipts,
            "Unknown/orphan review receipt: " + repr(sorted(declared_receipts - found_receipts)))
    require(type(offset) is int and offset >= 0 and type(limit) is int and 0 <= limit <= 1000,
            "Invalid bounded worklist scope")
    return {
        "kind": "INDEX_WIDE_FUNCTION_HYPOTHESIS_COVERAGE",
        "status": "OFFLINE_DECLARED_REVIEW_COVERAGE_ONLY",
        "index_sha": index_sha,
        "assessment_files": len(names),
        "publication_counts": count,
        "included_assessments": count["included"],
        "required_function_slots": slots,
        "reviewed_function_slots_declared": reviewed_slots,
        "systems_fully_screened_declared": len(covered),
        "systems_incomplete": len(remaining),
        "candidate_count_in_local_backlog": len(candidate_by_id),
        "remaining_queue_total": len(remaining),
        "queue_offset": offset,
        "queue_limit": limit,
        "queue": remaining[offset:offset+limit],
        "completed_assessments": covered,
        "native_fit_verified": False,
        "actual_product_improvement_verified": False,
        "live_canonical_index_attested": False,
        "authorization_status": "NOT_APPROVED_NO_GITHUB_WRITES",
        "execution_available": False,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--index-root", type=Path, required=True)
    p.add_argument("--index-sha", required=True)
    p.add_argument("--reviews-root", type=Path, default=Path("sweeps"))
    p.add_argument("--candidate-root", type=Path, default=Path("candidates"))
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--format", choices=("text", "json"), default="text")
    args = p.parse_args(argv)
    try:
        report = audit(index_root=args.index_root, index_sha=args.index_sha,
                       reviews_root=args.reviews_root, candidate_root=args.candidate_root,
                       offset=args.offset, limit=args.limit)
    except (SweepError, CandidateError, OSError) as exc:
        print("INDEX_SWEEP_BLOCKED: " + str(exc), file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print(f'INDEX={report["index_sha"]} | included={report["included_assessments"]} '
              f'/ assessment files={report["assessment_files"]}')
        print(f'System sweep declarations: {report["systems_fully_screened_declared"]}/'
              f'{report["included_assessments"]}; function slots '
              f'{report["reviewed_function_slots_declared"]}/'
              f'{report["required_function_slots"]}')
        for item in report["queue"]:
            print(f'{item["assessment_path"]}: '
                  f'{item["reviewed_functions"]}/{len(FUNCTIONS)} function slots reviewed')
        print("OFFLINE_DECLARED_REVIEW_COVERAGE_ONLY / NOT_APPROVED_NO_GITHUB_WRITES")
    return 0


if __name__ == "__main__":
    sys.exit(main())
