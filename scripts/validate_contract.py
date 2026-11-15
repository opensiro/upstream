#!/usr/bin/env python3
"""Offline structural checks for new Upstream docs. Not an outcome collector."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "README.md", "AGENTS.md", "CONTRIBUTING.md", "PROTOCOL.md",
    "VERSIONING.md", "CHANGELOG.md", "docs/ARCHITECTURE.md",
    "docs/MIGRATION.md", "docs/EVIDENCE.md",
    ".github/ISSUE_TEMPLATE/improvement.yml",
)
SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")


def check_contract(root=ROOT):
    errors = []
    for filename in REQUIRED:
        if not (root / filename).is_file():
            errors.append(f"missing {filename}")
    if not (root / "VERSION").is_file():
        return errors + ["missing VERSION"]
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER.fullmatch(version):
        return errors + [f"invalid SemVer: {version!r}"]
    package = f"changes/v{version}.md"
    if not (root / package).is_file():
        errors.append(f"missing {package}")
    for filename in ("README.md", "PROTOCOL.md", "CHANGELOG.md", "VERSIONING.md"):
        file = root / filename
        if file.is_file() and version not in file.read_text(encoding="utf-8"):
            errors.append(f"{filename}: missing current version {version}")
    key_anchors = {
        "README.md": ("docs/ARCHITECTURE.md", "upstream-old", "opensiro-contributions", "vsm-oss-organization"),
        "docs/ARCHITECTURE.md": ("TODO.md", "upstream-old", "opensiro-contributions", "verified_external_outcomes"),
        "docs/MIGRATION.md": ("upstream-old/issues/56", "0.11.0"),
        "PROTOCOL.md": ("External-publication consent", "need", "mechanism", "counterfactual", "scope"),
        "CHANGELOG.md": (package, "upstream-old"),
    }
    for filename, anchors in key_anchors.items():
        file = root / filename
        if file.is_file():
            content = file.read_text(encoding="utf-8")
            for anchor in anchors:
                if anchor not in content:
                    errors.append(f"{filename}: missing anchor {anchor}")
    return errors


if __name__ == "__main__":
    errors = check_contract()
    for error in errors:
        print("ERROR:", error, file=sys.stderr)
    if errors:
        raise SystemExit(1)
    print("Upstream SemVer, documentation and ownership anchors: OK")
