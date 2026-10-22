#!/usr/bin/env python3
"""Validate and render bounded upstream functional-effect observations.

This ledger deliberately does not reuse PR-lifecycle or Organization-fit data.
An offline check cannot confirm that external PRs or hosted tests are still live.
"""

import argparse
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "functional-effects.json"
OUTPUT = ROOT / "docs" / "FUNCTIONAL_EFFECTS.md"
ORIGINS = {"ASSESSMENT_DERIVED_HYPOTHESIS", "ASSESSMENT_INFORMED", "GENERAL_UPSTREAM", "INSUFFICIENT"}
LEVELS = {"SOURCE_ONLY_MECHANISM", "SOURCE_ONLY_PLANNING", "NATIVE_CLI_BEHAVIOR", "NATIVE_TOOL_BEHAVIOR", "SOURCE_REGRESSION_ONLY", "REAL_WORKLOAD"}
BENEFITS = {"NOT_MEASURED", "SUPPORTED", "NO_BENEFIT_OBSERVED", "INCONCLUSIVE"}
DELIVERY = {"NONE", "SUBMITTED", "MERGED", "CLOSED_UNMERGED"}


def load_and_validate(path=DATA):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1 or payload.get("owner") != "opensiro/upstream":
        raise ValueError("unsupported functional-effect ledger schema/owner")
    if not isinstance(payload.get("as_of"), str):
        raise ValueError("missing evidence date")
    try:
        if date.fromisoformat(payload["as_of"]).isoformat() != payload["as_of"]:
            raise ValueError("noncanonical evidence date")
    except ValueError as error:
        raise ValueError("invalid evidence date") from error
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("cases must be a nonempty list")
    seen = set()
    for case in cases:
        required = ("id", "project", "experiment", "origin", "measurement_level",
                    "before", "after", "comparability", "product_benefit",
                    "external_delivery", "receipts", "next_gate")
        if any(not case.get(field) for field in required):
            raise ValueError("incomplete case: " + str(case.get("id")))
        if case["id"] in seen:
            raise ValueError("duplicate functional effect case: " + case["id"])
        seen.add(case["id"])
        for field, allowed in (("origin", ORIGINS), ("measurement_level", LEVELS),
                               ("product_benefit", BENEFITS), ("external_delivery", DELIVERY)):
            if case[field] not in allowed:
                raise ValueError("invalid " + field + " in " + case["id"])
        if case["product_benefit"] == "SUPPORTED" and case["measurement_level"] != "REAL_WORKLOAD":
            # Source-only mechanism/CLI tests cannot self-certify user benefit.
            raise ValueError("product benefit requires measured real workload")
        if not isinstance(case["receipts"], list) or len(case["receipts"]) < 2:
            raise ValueError("case needs at least two independent evidence links")
        for url in [case["experiment"], *case["receipts"]]:
            parsed = urlparse(url)
            if parsed.scheme != "https" or parsed.netloc != "github.com" or not parsed.path.strip("/"):
                raise ValueError("unsupported evidence URL: " + url)
    return payload


def render(payload):
    lines = [
        "# Functional effects — evidence ledger",
        "",
        f"**Evidence date:** {payload['as_of']}. **Owner:** `opensiro/upstream`.",
        "This is **not** the eight-intervention PR acceptance dashboard, the Organization-owned product-native fit snapshot, or a VSM S2 regrade.",
        "Source-only matched tests and a green CI run cannot be counted as an improvement deployed to users.",
        "",
        "| Pilot | Origin | Before | After | Evidence level | Product benefit | External delivery |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for case in payload["cases"]:
        link = f"[{case['project']}]({case['experiment']})"
        cells = [link, f"`{case['origin']}`", case["before"], case["after"],
                 f"`{case['measurement_level']}`", f"`{case['product_benefit']}`",
                 f"`{case['external_delivery']}`"]
        lines.append("| " + " | ".join(cell.replace("|", "&#124;").replace("\n", " ") for cell in cells) + " |")
    lines.extend([
        "",
        "## Reproducibility and next gate",
        "",
    ])
    for case in payload["cases"]:
        lines.append(f"### {case['project']} — `{case['id']}`")
        lines.append("")
        lines.append(f"- **Comparability:** {case['comparability']}")
        lines.append(f"- **Next gate:** {case['next_gate']}")
        lines.append("- **Receipts:** " + ", ".join(f"[{i + 1}]({url})" for i, url in enumerate(case["receipts"])))
        lines.append("")
    lines.extend([
        "## Classification boundary",
        "",
        "- `ASSESSMENT_DERIVED_HYPOTHESIS` is the **selection origin**, not a completed native improvement.",
        "- `ASSESSMENT_INFORMED` means the first-party report supplied the concrete defect; do not retroactively credit Index with discovery.",
        "- `SOURCE_ONLY_*` and `SOURCE_REGRESSION_ONLY` establish narrow mechanisms/tests, not a deployed change.",
        "- `NATIVE_CLI_BEHAVIOR` can establish a genuine product-code execution difference on a frozen fixture, without establishing live adoption.",
        "- `NATIVE_TOOL_BEHAVIOR` measures actual shipped tool code under a controlled concurrent fixture, not provider-selected agent work or deployed user benefit.",
        "- `external_delivery=NONE` concerns the *pilot's third-party PR*, not internal OpenSiro PRs or the separate eight-case portfolio.",
        "",
        "Only an independently accepted native need and a matched real workload can justify stronger product impact claims; external delivery is a separate dimension. Follow [the experiment method](ASSESSMENT_TO_IMPROVEMENT.md) and [#56](https://github.com/opensiro/upstream/issues/56).",
        "",
        "Regenerate: `python3 scripts/functional_effects.py --write`; verify: `python3 scripts/functional_effects.py --check`.",
        "",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()
    output = render(load_and_validate())
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != output:
            parser.error("functional effect document is out of date; use --write")
        print("functional effect ledger consistent")
    else:
        OUTPUT.write_text(output, encoding="utf-8")
        print(str(OUTPUT))


if __name__ == "__main__":
    main()
