#!/usr/bin/env python3
"""Source-first provenance classification for fork-local Upstream contributions.

v1 historical records remain readable but MUST be labeled UNCLASSIFIED_LEGACY
when the provenance type was never recorded. All new writes require v2 and
a source-backed classification. This is not an AI/VSM benefit grader.
"""
import argparse
from datetime import date
import json
from pathlib import Path
import re

ORIGIN_TYPES = (
    "ASSESSMENT_DERIVED",
    "ASSESSMENT_INFORMED",
    "GENERAL_UPSTREAM",
    "INSUFFICIENT",
)
UNCLASSIFIED_LEGACY = "UNCLASSIFIED_LEGACY"
PINNED_INDEX = re.compile(
    r"^https://github\.com/opensiro/vsm-harness-index/blob/[a-f0-9]{40}/[^?#\s]+$")
SOURCE_URL = re.compile(r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/(?:issues|pull)/[1-9]\d*/?$")
PINNED_EVIDENCE = re.compile(
    r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/(?:blob|commit)/[a-f0-9]{40}(?:/[^?#\s]+)?$")


def _day(value):
    if not isinstance(value, str):
        raise ValueError("assessment date must be an ISO calendar day")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("assessment date must be an ISO calendar day") from exc


def classification(item):
    """Return source-backed type; expose v1 holes without fabricated claims."""
    schema = item.get("schema_version")
    if schema not in (1, 2) or type(schema) is not int:
        raise ValueError("unsupported contribution schema_version")
    label = item.get("contribution_type")
    if schema == 1 and label is None:
        return UNCLASSIFIED_LEGACY
    if label not in ORIGIN_TYPES:
        raise ValueError("contribution_type must be an explicit canonical provenance category")
    reason = item.get("classification_rationale")
    if not isinstance(reason, str) or len(reason.strip()) < 25:
        raise ValueError("classification_rationale requires a meaningful source-backed reason")
    evidence = item.get("classification_evidence")
    if not isinstance(evidence, list) or not all(
            isinstance(url, str) and (SOURCE_URL.fullmatch(url) or PINNED_EVIDENCE.fullmatch(url)
                                      or PINNED_INDEX.fullmatch(url))
            for url in evidence):
        raise ValueError("classification_evidence must be a list of verifiable source URLs")
    if label != "INSUFFICIENT" and not evidence:
        raise ValueError("classified contribution requires source-backed evidence")
    if len(set(evidence)) != len(evidence):
        raise ValueError("duplicate provenance evidence URL")

    pin = item.get("assessment_pin")
    if label in ("ASSESSMENT_DERIVED", "ASSESSMENT_INFORMED"):
        if not isinstance(pin, dict) or not PINNED_INDEX.fullmatch(pin.get("url", "")):
            raise ValueError("assessment origin requires an immutable Index assessment URL")
        _day(pin.get("reviewed_at"))
        if not re.fullmatch(r"[a-f0-9]{40}", str(pin.get("assessed_source_revision", ""))):
            raise ValueError("assessment origin requires a pinned assessed source revision")
        if pin["url"] not in evidence:
            raise ValueError("Index pin must be included in classification_evidence")
    if label == "ASSESSMENT_DERIVED":
        if not PINNED_EVIDENCE.fullmatch(item.get("prior_prediction_url", "")):
            raise ValueError("ASSESSMENT_DERIVED requires an immutable pre-implementation prediction receipt")
        if item["prior_prediction_url"] not in evidence:
            raise ValueError("prior prediction must be in classification_evidence")
        prediction = _day(item.get("prior_prediction_date"))
        implementation = _day(item.get("implementation_started_at"))
        if prediction >= implementation:
            raise ValueError("ASSESSMENT_DERIVED prediction must be dated before implementation")
    if label == "GENERAL_UPSTREAM":
        original = str(item.get("original_repository", "")).lower()
        if not any(SOURCE_URL.fullmatch(url) and "/".join(url.split("/")[3:5]).lower() == original
                   for url in evidence):
            raise ValueError("GENERAL_UPSTREAM requires an issue or PR from its exact original repository")
    return label


def validate_new_contribution(item):
    if item.get("schema_version") != 2:
        raise ValueError("new contributions MUST use schema_version 2; v1 is legacy read-only")
    return classification(item)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    args = parser.parse_args(argv)
    try:
        obj = json.loads(args.file.read_text(encoding="utf-8"))
        if not isinstance(obj, dict):
            raise ValueError("expected a JSON object")
        label = validate_new_contribution(obj)
    except (OSError, ValueError, TypeError) as exc:
        parser.error(str(exc))
    print(f"Fork-local contribution schema v2 and origin: {label} — OK")


if __name__ == "__main__":
    main()
