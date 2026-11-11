"""Prevent new third-party native CI workflows from landing in Upstream.

The frozen names are historical exceptions pending migration in Upstream #214.
New native tests belong in their source-matched opensiro-contributions fork
(or a distinct deterministic runner). Governance workflows remain here.
"""

from pathlib import Path
import unittest


WORKFLOWS = Path(__file__).resolve().parents[1] / ".github" / "workflows"

UPSTREAM_CONTROL = frozenset({
    "fork-lifecycle.yml",
    "portfolio-reconciliation.yml",
    "pr-maintenance.yml",
    "repository-integrity.yml",
    "upstream-status-freshness.yml",
    "upstream-status-proposal.yml",
    "verified-external-outcomes.yml",
})

# Pre-existing project-specific Actions on upstream/main as of 2026-11-11.
# These may be retired after source-native coverage and historical receipts
# are independently reconciled; do not add new entries to this frozen set.
LEGACY_SOURCE_NATIVE = frozenset({
    "agent-code-524-offline-delta.yml",
    "agent-code-524-offline.yml",
    "agent-code-524-upstream-audit.yml",
    "agentbox-native-dependency-dispatch.yml",
    "agentbox-s2-manager-advisory.yml",
    "agentbox-task-conflict-baseline.yml",
    "harnessdesk-v2-current-source.yml",
    "harnessdesk-v2-macos.yml",
    "kit-222-compat.yml",
    "kit-222-offline.yml",
    "zot-manual-worktrees-counterfactual.yml",
    "zot-native-tool-turn-boundaries.yml",
    "zot-scoped-admission-after.yml",
    "zot-shared-workspace-baseline.yml",
})


class NativeCIPlacementTests(unittest.TestCase):
    def test_no_new_unclassified_upstream_workflows(self):
        observed = {p.name for p in WORKFLOWS.iterdir()
                    if p.suffix in {".yml", ".yaml"} and p.is_file()}
        unexpected = sorted(observed - UPSTREAM_CONTROL - LEGACY_SOURCE_NATIVE)
        self.assertFalse(
            unexpected,
            "New workflow(s) in opensiro/upstream: "
            + ", ".join(unexpected)
            + ". Source-native CI belongs in opensiro-contributions/<target> "
            "or a distinct deterministic runner. A genuinely new Upstream "
            "control workflow requires an explicit, separately reviewed "
            "ownership decision (Upstream #214).",
        )
        self.assertFalse(
            UPSTREAM_CONTROL - observed,
            "Upstream control workflow unexpectedly removed: "
            + ", ".join(sorted(UPSTREAM_CONTROL - observed)),
        )

    def test_retained_legacy_native_workflows_remain_read_only(self):
        for name in sorted(LEGACY_SOURCE_NATIVE):
            path = WORKFLOWS / name
            if not path.exists():
                continue  # Migration/retirement is permitted.
            with self.subTest(name=name):
                self.assertIn(
                    "permissions:\n  contents: read",
                    path.read_text(encoding="utf-8"),
                    "Do not expand the permissions of a legacy target-native "
                    "workflow retained in Upstream; migrate it instead.",
                )


if __name__ == "__main__":
    unittest.main()
