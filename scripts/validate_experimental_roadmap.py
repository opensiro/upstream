#!/usr/bin/env python3
"""Structural draft-only validation of explicit A/P Roadmap experiments."""
from __future__ import annotations

import argparse
from pathlib import Path

from validate_roadmap_publication import check_case_structure


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, choices=("A", "P"))
    parser.add_argument("case_dir", type=Path)
    args = parser.parse_args(argv)
    errors = check_case_structure(args.case_dir, experimental_target=args.target)
    if errors:
        for error in errors:
            print("EXPERIMENTAL_DRAFT_INVALID: " + error)
        return 1
    print("EXPERIMENTAL_DRAFT_STRUCTURE_PASS — NOT PERSISTENCE OR PUBLICATION APPROVAL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
