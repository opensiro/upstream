#!/usr/bin/env python3
"""Generate a stable, evidence-only catalog of historical Upstream pilots.

This indexes files and their *artifact roles*, not experiment success,
technical correctness, current fork state, or external PR adoption. Original
paths remain canonical for frozen receipts and GitHub permalinks.
"""

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PILOTS = Path("pilots")
JSON_OUT = PILOTS / "catalog.json"
MARKDOWN_OUT = PILOTS / "CATALOG.md"
BASELINE = PILOTS / "HISTORICAL_BASELINE.json"
KINDS = (
    "EXPERIMENT_SERIES",
    "PATCH_HANDOFF",
    "PATCH_EVIDENCE",
    "SCREEN_ONLY",
    "OTHER_EVIDENCE",
)
LABELS = {
    "EXPERIMENT_SERIES": "Experiments and reproducible protocols",
    "PATCH_HANDOFF": "Patch packets and handoffs",
    "PATCH_EVIDENCE": "Patches with other technical evidence",
    "SCREEN_ONLY": "Screened or blocked hypotheses without a patch",
    "OTHER_EVIDENCE": "Other preserved evidence",
}


class CatalogError(ValueError):
    pass


def _role(path):
    name = path.name.upper()
    if path.suffix.lower() == ".patch":
        return "patch"
    if "RECEIPT" in name or "VALIDATION" in name:
        return "receipt"
    if "PROTOCOL" in name or "EXPERIMENT" in name or "COUNTERFACTUAL" in name:
        return "protocol"
    if "SCREENING" in name or "INTAKE" in name or "FIT_DECISION" in name:
        return "screen"
    if "HANDOFF" in name:
        return "handoff"
    if path.suffix.lower() in {".go", ".py", ".ts", ".tsx", ".sh", ".rs"}:
        return "native_code"
    if path.suffix.lower() in {".json", ".yaml", ".yml"}:
        return "fixture_or_recipe"
    return "other"


def _kind(roles, files):
    if (roles["protocol"] and (roles["receipt"] or roles["native_code"])) or any(
            Path(name).name.upper().startswith("REPLAY_RECEIPT") for name in files):
        return "EXPERIMENT_SERIES"
    if roles["patch"] and roles["handoff"]:
        return "PATCH_HANDOFF"
    if roles["patch"]:
        return "PATCH_EVIDENCE"
    if roles["screen"] and not roles["handoff"]:
        return "SCREEN_ONLY"
    return "OTHER_EVIDENCE"


def _entrypoint(files, roles):
    for preferred in ("README.md", "CONTRIBUTION_HANDOFF.md", "SCREENING.md"):
        for name in files:
            if name == preferred:
                return name
    for name in files:
        if Path(name).name.upper().startswith("SCREENING"):
            return name
    for role in ("screen", "protocol", "handoff", "receipt", "other", "native_code", "patch"):
        for name in files:
            if _role(Path(name)) == role:
                return name
    return files[0]


def _historical_baseline(root):
    path = Path(root) / BASELINE
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CatalogError(f"Cannot read historical pilot baseline: {exc}") from exc
    if record.get("schema_version") != 1 or not isinstance(record.get("entries"), list):
        raise CatalogError("Unsupported historical pilot baseline schema")
    baseline = {}
    for entry in record["entries"]:
        if not isinstance(entry, dict):
            raise CatalogError("Invalid historical pilot baseline entry")
        identity, files = entry.get("id"), entry.get("files")
        if (not isinstance(identity, str) or not identity or "/" in identity
                or identity in {".", ".."} or identity in baseline
                or not isinstance(files, list) or not files
                or any(not isinstance(name, str) or not name
                       or name.startswith("/") or ".." in Path(name).parts
                       for name in files)
                or len(set(files)) != len(files)):
            raise CatalogError(f"Invalid historical pilot identity/files: {identity!r}")
        baseline[identity] = set(files)
    return baseline


def build(root=ROOT):
    pilots_root = Path(root) / PILOTS
    if not pilots_root.is_dir():
        raise CatalogError("Missing pilots/ directory")
    baseline = _historical_baseline(root)
    entries = []
    for directory in sorted(p for p in pilots_root.iterdir() if p.is_dir()):
        if directory.is_symlink():
            raise CatalogError(f"Unexpected symlink pilot directory: {directory.name}")
        descendants = list(directory.rglob("*"))
        if any(p.is_symlink() for p in descendants):
            raise CatalogError(f"Symlink artifact requires review: {directory.name}")
        artifact_paths = sorted((p for p in descendants if p.is_file()),
                                key=lambda p: p.relative_to(directory).as_posix())
        if not artifact_paths:
            raise CatalogError(f"Empty pilot directory: {directory.name}")
        files = [p.relative_to(directory).as_posix() for p in artifact_paths]
        roles = Counter(_role(Path(name)) for name in files)
        entry = {
            "id": directory.name,
            "path": (PILOTS / directory.name).as_posix(),
            "kind": _kind(roles, files),
            "start_here": (PILOTS / directory.name / _entrypoint(files, roles)).as_posix(),
            "artifact_counts": {role: roles[role] for role in (
                "patch", "handoff", "screen", "protocol", "receipt",
                "native_code", "fixture_or_recipe", "other") if roles[role]},
            "files": files,
        }
        entries.append(entry)
    current = {entry["id"]: set(entry["files"]) for entry in entries}
    for identity, original_files in baseline.items():
        if identity not in current:
            raise CatalogError(f"Historical pilot directory was removed: {identity}")
        missing = sorted(original_files - current[identity])
        if missing:
            raise CatalogError(
                f"Historical pilot paths were removed: {identity}: {', '.join(missing)}"
            )
    root_files = sorted(p.name for p in pilots_root.iterdir() if p.is_file()
                        and p.name not in {"README.md", "CATALOG.md", "catalog.json",
                                           "EXPERIMENT_CONTRACT.md"})
    return {
        "schema_version": 1,
        "scope": "HISTORICAL_EXPERIMENT_AND_TECHNICAL_PACKET_INDEX",
        "meaning": "FILE_INVENTORY_ONLY_NO_SUCCESS_OR_EXTERNAL_PUBLICATION_CLAIM",
        "generated_from": "pilots/ direct subdirectories and their preserved files",
        "counts": {
            "pilot_directories": len(entries),
            "artifact_files": sum(len(e["files"]) for e in entries),
            "historical_directories": len(baseline),
            "new_directories": len(entries) - len(baseline),
            "by_kind": {kind: sum(e["kind"] == kind for e in entries) for kind in KINDS},
        },
        "root_shared_files": root_files,
        "entries": entries,
    }


def json_text(report):
    return json.dumps(report, ensure_ascii=False, indent=2) + "\n"


def markdown_text(report):
    counts = report["counts"]
    lines = [
        "# Historical technical experiments and pilot packets",
        "",
        "This catalog indexes preserved source-native evidence in `pilots/`; it is **not**",
        "the live code workspace or a list of successful interventions. Classification",
        "below describes **file types**, not verified experiment outcomes, patch",
        "fitness, fork existence, PR publication, maintainer acceptance, or VSM grades.",
        "See [experiment contract](EXPERIMENT_CONTRACT.md) and",
        "[working-fork pipeline](../docs/CONTINUOUS_WORKING_FORK_PIPELINE.md).",
        "",
        f"**Coverage:** {counts['pilot_directories']} indexed pilot directories · "
        f"{counts['artifact_files']} files. The frozen baseline protects "
        f"{counts['historical_directories']} historical directories and their files; "
        f"{counts['new_directories']} directories were added later.",
        "",
        "Each row links its preferred entry file. Read the actual receipt and governing",
        "batch/PR before attributing positive results or current status.",
        "",
    ]
    for kind in KINDS:
        entries = [e for e in report["entries"] if e["kind"] == kind]
        if not entries:
            continue
        lines.extend([f"## {LABELS[kind]} ({len(entries)})", "",
                      "| Pilot | Entry point | Artifacts |", "| --- | --- | --- |"])
        for entry in entries:
            relative = entry["start_here"].removeprefix("pilots/")
            detail = ", ".join(f"{name}: {number}" for name, number in
                               entry["artifact_counts"].items())
            lines.append(f"| `{entry['id']}` | [Open]({relative}) | {detail} |")
        lines.append("")
    lines.extend(["## Shared root artifacts", ""])
    if report["root_shared_files"]:
        lines.extend(f"- [`{p}`]({p})" for p in report["root_shared_files"])
    else:
        lines.append("None.")
    lines.extend(["", "## Regeneration", "", "```bash",
                  "python3 scripts/pilot_catalog.py sync",
                  "python3 scripts/pilot_catalog.py check", "```", "",
                  "The second command runs in CI. New or renamed pilot files require an",
                  "updated catalog in the same internal PR. No generated field is an",
                  "external publication authorization.", ""])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("status", "sync", "check"))
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        report = build(args.root)
        json_path = args.root / JSON_OUT
        md_path = args.root / MARKDOWN_OUT
        if args.command == "sync":
            json_path.write_text(json_text(report), encoding="utf-8")
            md_path.write_text(markdown_text(report), encoding="utf-8")
        elif args.command == "check":
            if (not json_path.is_file() or not md_path.is_file()
                    or json_path.read_text(encoding="utf-8") != json_text(report)
                    or md_path.read_text(encoding="utf-8") != markdown_text(report)):
                raise CatalogError("Stale pilot catalog; run scripts/pilot_catalog.py sync")
        else:
            print(json.dumps(report["counts"], indent=2))
    except (CatalogError, OSError) as exc:
        parser.exit(2, f"PILOT_CATALOG_INVALID: {exc}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
