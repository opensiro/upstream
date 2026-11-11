"""Keep source-specific PR proposal prose in contributor forks, not Upstream.

Only the three dated historical proposal files predating the fork-local
contract are allowed here. New proposal title/body belongs in a fork-local
PR description on the matching opensiro-contributions project.
"""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_PROPOSALS = frozenset({
    "reports/2026-11-11-external-wave-02-knowwork-pr-body.md",
    "reports/2026-11-11-external-wave-02-runloop-pr-body.md",
    "reports/2026-11-11-external-wave-03-evidence-bench-pr-body.md",
})


class ProposalPlacementTests(unittest.TestCase):
    def test_no_new_upstream_publication_body_staging(self):
        observed = set()
        for path in (ROOT / "reports").glob("*.md"):
            contents = path.read_text(encoding="utf-8")
            if "pr-body" in path.name.lower() or contents.startswith("# Proposed external PR:"):
                observed.add(path.relative_to(ROOT).as_posix())
        unexpected = sorted(observed - HISTORICAL_PROPOSALS)
        self.assertFalse(
            unexpected,
            "New target-specific PR body proposal(s) in Upstream: "
            + ", ".join(unexpected)
            + ". Store the title/body in the matching "
              "opensiro-contributions/<target> fork-local PR; "
              "Upstream retains only its URL, approval and actual result.",
        )


if __name__ == "__main__":
    unittest.main()
