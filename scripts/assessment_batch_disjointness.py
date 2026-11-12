#!/usr/bin/env python3
"""Offline global source-identity guard for merged assessment batch manifests.

Runs in existing repository-integrity CI; no GitHub/network/writes and no
cross-run admission. Source reservation against unmerged PRs is separate.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from assessment_candidate_batches import BatchError, validate

ROOT = Path(__file__).resolve().parents[1]
FILENAME = re.compile(r"\d{4}-\d{2}-\d{2}-\d{2}\.json\Z")


def check_cohorts(batch_dir):
    root = Path(batch_dir)
    if not root.is_dir():
        raise BatchError("BLOCKED_COHORT_VISIBILITY: missing batch directory")
    files = sorted(root.iterdir())
    manifests = [p for p in files if p.name.endswith(".json")]
    if not manifests:
        raise BatchError("BLOCKED_COHORT_VISIBILITY: no assessment batch manifests")
    seen_sources = {}
    seen_ids = {}
    fingerprint_rows = []
    for path in manifests:
        if not path.is_file() or path.is_symlink() or not FILENAME.fullmatch(path.name):
            raise BatchError("BLOCKED_COHORT_VISIBILITY: unexpected manifest path " + path.name)
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, UnicodeError, OSError) as exc:
            raise BatchError("BLOCKED_COHORT_VISIBILITY: malformed manifest " + path.name) from exc
        validate(manifest)
        batch_id = manifest["batch_id"]
        if path.name != batch_id.removeprefix("assessment-upstream-") + ".json":
            raise BatchError("BLOCKED_COHORT_IDENTITY: filename/batch ID mismatch " + path.name)
        if batch_id in seen_ids:
            raise BatchError("BLOCKED_COHORT_IDENTITY: duplicate batch ID " + batch_id)
        seen_ids[batch_id] = path.name
        for row in manifest["candidates"]:
            source = row["source"].casefold()
            if source in seen_sources:
                raise BatchError(
                    "BLOCKED_DUPLICATE_SOURCE: " + source + " already held by "
                    + seen_sources[source] + ", collided with " + path.name)
            seen_sources[source] = path.name
            fingerprint_rows.append((batch_id, source, row["review_ref"]))
    digest = hashlib.sha256(
        json.dumps(sorted(fingerprint_rows), separators=(",", ":")).encode()).hexdigest()
    return {"status": "MERGED_COHORTS_DISTINCT", "manifest_count": len(manifests),
            "source_count": len(seen_sources), "cohort_sha256": digest,
            "remote_open_prs_checked": False, "admission_attested": False,
            "external_writes_authorized": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-dir", type=Path,
                        default=ROOT / "data/assessment-candidate-batches")
    args = parser.parse_args(argv)
    try:
        result = check_cohorts(args.batch_dir)
    except (BatchError, OSError) as exc:
        parser.exit(2, f"COHORT_GUARD_BLOCKED: {exc}\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
