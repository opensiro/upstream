#!/usr/bin/env python3
"""Offline, fail-closed Index assessment provenance preflight for S1 proposals.

Checks local git-object provenance and proposed target identity only. This is
NOT a live Index source attestation, native product-fit assessment, authorization,
fork creation, GitHub connector or execution path.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

from batch_proposals import BatchError, load_draft

SHA = re.compile(r"^[0-9a-f]{40}$")
ASSESSMENT = re.compile(r"^assessments/([a-z0-9-]{2})/([a-z0-9-]+)\.md$")
REPO_URL = re.compile(r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)/?$")
REQUIRED = {
    "harness_id", "repository", "review_ref", "status",
    "autonomy_s1", "autonomy_s2", "autonomy_s3",
    "autonomy_s3_star", "autonomy_s4", "autonomy_s5",
}
GRADE = {"A", "C", "P", "A(P)", "C(P)", "—", "?"}


class OriginBlocked(Exception):
    """Local source/origin cannot be established. No writes permitted."""


def _need(ok, msg):
    if not ok:
        raise OriginBlocked(msg)


def _git(root, *args):
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *args],
            text=False, capture_output=True, timeout=10, check=False,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        raise OriginBlocked("Cannot inspect local Index git checkout") from None
    _need(proc.returncode == 0, "Index git object/ref unavailable")
    _need(len(proc.stdout) <= 256 * 1024, "Index git output exceeds bound")
    return proc.stdout


def _decode(raw):
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        raise OriginBlocked("Assessment must be UTF-8") from None


def _fields(raw):
    text = _decode(raw)
    lines = text.splitlines()
    _need(lines and lines[0].strip() == "---", "Missing assessment frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise OriginBlocked("Unterminated assessment frontmatter") from None
    _need(1 < end <= 80, "Assessment frontmatter exceeds expected bounds")
    found = {}
    for line in lines[1:end]:
        _need(":" in line, "Unrecognized assessment frontmatter entry")
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip().strip("'").strip('"')
        _need(key and key not in found and key in REQUIRED.union({
            "project_name", "reviewed_at", "profile_version",
            "generated_profile_version", "generated_assessment_procedure_version",
            "assessment_procedure_version", "assessment_changed_at",
        }), "Unexpected or duplicate frontmatter field")
        _need(value, "Empty assessment frontmatter field")
        found[key] = value
    _need(REQUIRED.issubset(found), "Missing required assessment identity or grades")
    _need(found["status"] == "included", "Assessment is not included")
    _need(bool(SHA.fullmatch(found["review_ref"])), "Assessment has no immutable review_ref")
    _need(all(found[key] in GRADE for key in REQUIRED if key.startswith("autonomy_")),
          "Unrecognized assessment function state")
    return found


def preflight(*, index_root, index_sha, assessment_path, manifest, candidate_id):
    """Prove local frozen Index-object identity against one draft candidate.

    A trusted operator/host must separately verify this SHA/path against the
    *actual current public Index*, and native need/fit against current upstream.
    A synthetic git checkout can pass this local consistency check; do not use
    it as an admission or trusted provenance attestation.
    """
    _need(type(index_sha) is str and bool(SHA.fullmatch(index_sha)),
          "Index SHA must be 40 lowercase hex characters")
    _need(type(assessment_path) is str, "Assessment path must be a string")
    match = ASSESSMENT.fullmatch(assessment_path)
    _need(match is not None, "Invalid assessment-relative path")
    _need(match.group(2).startswith(match.group(1)), "Incorrect assessment shard path")
    root = Path(index_root).resolve()
    _need(root.is_dir(), "Index root does not exist")
    actual_root = _decode(_git(root, "rev-parse", "--show-toplevel")).strip()
    _need(Path(actual_root).resolve() == root, "Index root must be the exact git worktree root")
    head = _decode(_git(root, "rev-parse", "HEAD")).strip()
    _need(head == index_sha, "Index HEAD differs from the exact requested source SHA")
    raw = _git(root, "show", f"{index_sha}:{assessment_path}")
    fields = _fields(raw)
    _need(fields["harness_id"] == match.group(2), "Assessment filename/identity mismatch")
    repo_match = REPO_URL.fullmatch(fields["repository"])
    _need(repo_match is not None, "Assessment upstream is not a canonical GitHub URL")
    source = "/".join(repo_match.groups())

    try:
        draft, proposal_hash = load_draft(manifest)
    except BatchError as exc:
        raise OriginBlocked("Invalid Upstream proposal: " + str(exc)) from None
    _need(type(candidate_id) is str, "Invalid candidate selector")
    matches = [c for c in draft["candidates"] if c["id"] == candidate_id]
    _need(len(matches) == 1, "Candidate absent from proposed manifest")
    item = matches[0]
    _need(item["source"].casefold() == source.casefold(),
          "Selected upstream source differs from canonical assessment")
    _need(not item["blockers"], "Candidate is blocked; no stage may be selected")
    _need(item["proposal"]["evidence_url"], "Upstream primary evidence is required")
    return {
        "status": "LOCAL_INDEX_ORIGIN_PRECHECK_ONLY",
        "authorization_status": "NOT_APPROVED_NO_GITHUB_WRITES",
        "native_fit_status": "UNVERIFIED_REQUIRES_INDEPENDENT_UPSTREAM_REVIEW",
        "canonical_index_source_status": "UNVERIFIED_REQUIRES_TRUSTED_GITHUB_SOURCE_CHECK",
        "execution_available": False,
        "index_commit_sha": index_sha,
        "assessment_path": assessment_path,
        "assessment_sha256": hashlib.sha256(raw).hexdigest(),
        "harness_id": fields["harness_id"],
        "assessed_upstream": source,
        "assessment_review_ref": fields["review_ref"],
        "function_states": {
            "S1": fields["autonomy_s1"], "S2": fields["autonomy_s2"],
            "S3": fields["autonomy_s3"], "S3*": fields["autonomy_s3_star"],
            "S4": fields["autonomy_s4"], "S5": fields["autonomy_s5"],
        },
        "candidate_id": candidate_id,
        "proposal_sha256": proposal_hash,
        "upstream_evidence_url": item["proposal"]["evidence_url"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index-root", type=Path, required=True)
    parser.add_argument("--index-sha", required=True)
    parser.add_argument("--assessment-path", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args()
    try:
        receipt = preflight(
            index_root=args.index_root, index_sha=args.index_sha,
            assessment_path=args.assessment_path, manifest=args.manifest,
            candidate_id=args.candidate,
        )
    except OriginBlocked as exc:
        print("ASSESSMENT_ORIGIN_BLOCKED: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
