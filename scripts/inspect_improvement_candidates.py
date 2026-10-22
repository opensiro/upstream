#!/usr/bin/env python3
"""Offline integrity inspection for Upstream improvement candidate research cards.

This is NOT a product-fit attestation, Index origin verification, selection,
contribution proposal, authorization or GitHub writer. No external I/O.
"""
import argparse
import json
from pathlib import Path
import re
import sys

FIELDS = {
    "candidate_id", "state", "origin_class", "target_repo", "index_sha",
    "assessment_path", "review_ref", "source_sha", "fit_need",
    "fit_mechanism", "fit_value", "fit_scope",
}
STATES = {
    "DISCOVERED", "SCREENING", "BLOCKED_EVIDENCE", "QUALIFIED",
    "SELECTED", "PARKED", "REJECTED",
}
ORIGINS = {
    "ASSESSMENT_DERIVED", "ASSESSMENT_INFORMED",
    "GENERAL_UPSTREAM", "INSUFFICIENT",
}
GATES = ("fit_need", "fit_mechanism", "fit_value", "fit_scope")
VERDICTS = {"PASS", "PENDING", "FAIL"}
SHA = re.compile(r"^[a-f0-9]{40}$")
CANDIDATE_ID = re.compile(r"^IMPR-[A-Z0-9]+(?:-[A-Z0-9]+)*$")
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
ASSESSMENT = re.compile(r"^assessments/([a-z0-9-]{2})/([a-z0-9-]+)\.md$")

class CandidateError(ValueError):
    """A candidate cannot be safely inspected even as research metadata."""


def read_card(path):
    """Parse only a small, flat and explicitly allowlisted frontmatter format."""
    if path.is_symlink() or not path.is_file() or path.suffix != ".md":
        raise CandidateError("Not a regular Markdown candidate card")
    if path.stat().st_size > 32 * 1024:
        raise CandidateError("Candidate card exceeds 32 KiB")
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise CandidateError("Cannot decode candidate card: " + type(exc).__name__) from None
    if not lines or lines[0] != "---":
        raise CandidateError("Missing candidate frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise CandidateError("Unterminated candidate frontmatter") from None
    if not 1 < end <= 32:
        raise CandidateError("Invalid frontmatter length")
    fields = {}
    for line in lines[1:end]:
        if ":" not in line:
            raise CandidateError("Expected flat key: value metadata")
        key, val = (part.strip() for part in line.split(":", 1))
        if key not in FIELDS or key in fields or not val or any(ord(c) < 32 for c in val):
            raise CandidateError("Unknown, duplicate or empty candidate field")
        # Deliberately forbid YAML/JSON nesting and quoting, so this is not a YAML interpreter.
        if any(x in val for x in ("{", "}", "[", "]", "\t")):
            raise CandidateError("Only simple scalar metadata is supported")
        fields[key] = val
    if fields.keys() != FIELDS:
        raise CandidateError("Candidate metadata fields mismatch")

    ident = fields["candidate_id"]
    if not CANDIDATE_ID.fullmatch(ident):
        raise CandidateError("Invalid candidate ID")
    if fields["state"] not in STATES or fields["origin_class"] not in ORIGINS:
        raise CandidateError("Invalid candidate research state or origin class")
    if not REPO.fullmatch(fields["target_repo"]):
        raise CandidateError("Invalid target repository")
    if not SHA.fullmatch(fields["source_sha"]):
        raise CandidateError("Current product source requires an immutable commit")
    if any(fields[k] not in VERDICTS for k in GATES):
        raise CandidateError("Invalid native-fit gate")
    if fields["state"] in {"QUALIFIED", "SELECTED"} and not all(
        fields[k] == "PASS" for k in GATES
    ):
        raise CandidateError("Blocked candidate cannot claim qualified or selected")
    if fields["origin_class"] in {"ASSESSMENT_DERIVED", "ASSESSMENT_INFORMED"}:
        if not SHA.fullmatch(fields["index_sha"]) or not SHA.fullmatch(fields["review_ref"]):
            raise CandidateError("Assessment-linked candidate requires pinned Index/source")
        m = ASSESSMENT.fullmatch(fields["assessment_path"])
        if m is None or not m.group(2).startswith(m.group(1)):
            raise CandidateError("Invalid canonical assessment path")
    elif any(fields[k] != "none" for k in ("index_sha", "assessment_path", "review_ref")):
        # Do not attach post-hoc canonical assessment credentials to a generic/unknown origin.
        raise CandidateError("Non-assessment origin cannot silently claim assessment provenance")
    if not any(line.startswith("# " + ident + " ") for line in lines[end + 1:]):
        raise CandidateError("Title must expose immutable candidate ID")
    body = "\n".join(lines[end + 1:])
    if len(body.strip()) < 250 or "## Four native fit gates" not in body:
        raise CandidateError("Missing readable evidence and four-gate discussion")
    return {
        **fields,
        "declared_fit_complete": all(fields[k] == "PASS" for k in GATES),
        "card": path.name,
    }


def inspect(root):
    """Return a strictly local structural report; never produce a write-ready token."""
    root = Path(root)
    if not root.is_dir():
        raise CandidateError("Candidate directory missing")
    cards = sorted(p for p in root.glob("*.md") if p.name != "README.md")
    if len(cards) > 500:
        raise CandidateError("Candidate collection oversized")
    seen = set()
    entries = []
    for path in cards:
        try:
            result = read_card(path)
        except (CandidateError, OSError) as exc:
            raise CandidateError(path.name + ": " + str(exc)) from None
        ident = result["candidate_id"]
        if ident in seen:
            raise CandidateError("Duplicate candidate ID: " + ident)
        seen.add(ident)
        entries.append(result)
    return {
        "kind": "IMPROVEMENT_CANDIDATES_STRUCTURAL_INSPECTION",
        "status": "LOCAL_METADATA_ONLY",
        "authorization_status": "NOT_APPROVED_NO_GITHUB_WRITES",
        "live_index_verified": False,
        "native_fit_verified": False,
        "candidate_transition_authorized": False,
        "proposal_created": False,
        "count": len(entries),
        "candidates": entries,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("candidates"))
    parser.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args(argv)
    try:
        report = inspect(args.root)
    except (CandidateError, OSError) as exc:
        print("CANDIDATE_INSPECTION_BLOCKED: " + str(exc), file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(report, sort_keys=True, indent=2))
    else:
        print("LOCAL_METADATA_ONLY / NOT_APPROVED_NO_GITHUB_WRITES")
        for item in report["candidates"]:
            print(f'{item["candidate_id"]}: {item["state"]} / '
                  f'{item["origin_class"]} / declared_fit_complete='
                  f'{str(item["declared_fit_complete"]).lower()}')
        print("Live Index, target behavior and product fit NOT VERIFIED; no transition authorized")
    return 0


if __name__ == "__main__":
    sys.exit(main())
