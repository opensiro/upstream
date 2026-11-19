"""Source-only Upstream architecture tests: no GitHub write, network or VSM grading."""
from pathlib import Path
import json
import re
from tempfile import TemporaryDirectory
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_contract import check_contract, REQUIRED  # noqa: E402


class ContractTests(unittest.TestCase):
    def test_resumption_reconstructs_context_with_five_links_and_stop_precedence(self):
        protocol = (ROOT / "PROTOCOL.md").read_text(encoding="utf-8")
        instructions = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        review = (ROOT / "docs/UPGRADE_PR_REVIEW.md").read_text(encoding="utf-8")
        self.assertIn("Resumable Upgrade link and context checkpoint", protocol)
        self.assertIn("upgrade_handoff.py", protocol)
        self.assertIn("upgrade_handoff.py", instructions)
        self.assertIn("--stage preview", review)
        self.assertIn("--stage new", review)
        self.assertIn("STOP precedence", review)
        self.assertTrue((ROOT / "scripts/upgrade_handoff.py").is_file())

    def test_repository_contract(self):
        self.assertEqual(check_contract(ROOT), [])

    def test_fork_metadata_examples_have_distinct_identity_and_controls(self):
        content = (ROOT / "docs/FORK_METADATA.md").read_text(encoding="utf-8")
        samples = [json.loads(s) for s in re.findall(r"```json\s*(.*?)\s*```", content, re.S)]
        self.assertEqual(len(samples), 3)
        state, contribution, event = samples
        self.assertEqual(state["schema_version"], 1)
        self.assertEqual(contribution["schema_version"], 2)
        self.assertEqual(contribution["contribution_type"], "GENERAL_UPSTREAM")
        self.assertEqual(event["schema_version"], 1)
        self.assertEqual(state["working_fork"].split("/")[0], "opensiro-contributions")
        self.assertEqual(contribution["original_repository"], state["original_repository"])
        self.assertEqual(event["contribution_id"], contribution["id"])
        self.assertEqual(event["id"], state["last_event_id"])
        self.assertEqual(event["id"], contribution["last_event_id"])
        self.assertIn("STOP", content)
        self.assertIn("DORMANT", content)
        self.assertIn("opensiro/meta", content)

    def test_capability_upgrade_route_preserves_source_evidence_and_authority(self):
        protocol = (ROOT / "PROTOCOL.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("contribution_type", agents)
        self.assertIn("schema_version 2", agents)
        self.assertIn("upstream upgrade batch N", protocol)
        self.assertIn("N distinct original harnesses", protocol)
        self.assertIn("S1/S2/S3/S3*/S4/S5", protocol)
        self.assertIn("REPAIR_ONLY", protocol)
        self.assertIn("ASSESSMENT_DERIVED", protocol)
        self.assertIn("exact current-conversation consent", protocol)
        self.assertIn("DORMANT", protocol)
        self.assertIn("PAUSE", protocol)
        self.assertIn("STOP", protocol)
        self.assertIn("upstream batch [N]", agents)
        self.assertIn("upstream upgrade batch 10", readme)
        self.assertIn("not executable CLI commands", readme)
        self.assertTrue((ROOT / "changes/v0.14.0.md").is_file())

    def test_single_upgrade_one_source_fork_local_pr_and_publication_boundary(self):
        protocol = (ROOT / "PROTOCOL.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        handoff = (ROOT / "docs/UPGRADE_PR_REVIEW.md").read_text(encoding="utf-8")
        section = protocol.split(
            "### End-to-end single-source Upgrade — finish at human PR approval", 1
        )[1].split("### License and formalities first", 1)[0]
        for expected in (
            "exactly ONE original harness",
            "Do not switch to a different original harness",
            "other opportunities inside that same source",
            "without intermediate continuation prompts",
            "READY_FOR_HUMAN_PR_APPROVAL",
            "NOT PUBLISHED",
            "NO_QUALIFIED_IMPROVEMENT",
            "BLOCKED_WITH_HANDOFF",
            "EVIDENCE_INSUFFICIENT",
            "CLA/DCO",
            "PAUSE/STOP",
            "original destination/action",
            "fork-local PR",
            "opensiro-contributions/<fork>",
            "exact proposed fork-local destination",
            "AWAITING_FORK_LOCAL_PR_APPROVAL",
            "current-conversation owner approval",
            "No cross-harness fallback",
        ):
            self.assertIn(expected, section)
        self.assertIn("Stay inside the named original source", section)
        self.assertIn("one-harness, end-to-end engineering route", readme)
        self.assertIn("never switch to another original", agents)
        self.assertIn("review PR in the matching", changelog)
        self.assertIn("Never merge", handoff)
        self.assertIn("public fork-local PR", handoff)
        self.assertIn("browser-use/browser-harness PR #1034", handoff)
        self.assertEqual((ROOT / "VERSION").read_text(encoding="utf-8").strip(), "0.17.0")

    def test_review_gated_ai_disclosure_keeps_verified_assessment_provenance(self):
        handoff = (ROOT / "docs/UPGRADE_PR_REVIEW.md").read_text(encoding="utf-8")
        for phrase in (
            "opensiro-ai-assessment-disclosure:review-gated",
            "Original source request",
            "Improvement origin",
            "VSM assessment (when verified)",
            "ASSESSMENT_INDEX_SHA",
            "ASSESSMENT_PATH",
            "Assessment date",
            "reviewed_at",
            "Assessed source revision",
            "40-character review_ref",
            "Assessment relationship",
            "Native validation",
            "Human/publication status",
            "GENERAL_UPSTREAM",
            "ASSESSMENT_DERIVED",
            "current-conversation",
            "historical v3",
            "2026-09-18",
            "afbcc381b963040c19627d788e40c7e7663171ee",
        ):
            self.assertIn(phrase, handoff)
        self.assertNotIn("without a separate human approval of this PR", handoff)
        self.assertIn("does not edit that external PR", handoff)

    def test_upgrade_pr_disclosure_links_are_mandatory_not_examples(self):
        protocol = (ROOT / "PROTOCOL.md").read_text(encoding="utf-8")
        review = (ROOT / "docs/UPGRADE_PR_REVIEW.md").read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for label in (
            "Working fork",
            "Implementation branch",
            "Implementation commit",
            "Fork-local review PR",
            "Fork-local metadata record",
        ):
            self.assertIn(f"**{label}:**", review)
        for marker in (
            "Normative link requirement",
            "Mandatory link and body preflight",
            "PR_BLOCKED_NO_WRITE",
            "NOT_CREATED — awaiting exact fork-local PR consent",
            "NOT_CREATED — historical PR; no prior fork-local review PR",
            "validate_upgrade_pr_links.py",
        ):
            self.assertIn(marker, review)
        self.assertIn("Mandatory `opensiro-contributions` links", protocol)
        self.assertIn("proposed external PR body", readme)
        self.assertIn("Mandatory Upgrade disclosure/links", agents)
        self.assertIn("current-conversation", review)

    def test_upgrade_popularity_and_chat_only_batch_policy(self):
        protocol = (ROOT / "PROTOCOL.md").read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertIn(f"v{version}", (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))
        self.assertIn("unique GitHub contributors", protocol)
        self.assertIn("1× to 2×", protocol)
        self.assertIn("uniform", protocol)
        self.assertIn("chat-level research/reporting sessions", protocol)
        self.assertIn("not an issue, PR", protocol)
        self.assertIn("chat-only hypothesis cannot alone prove", protocol)
        self.assertIn("PAUSE", protocol)
        self.assertIn("native CI placement", protocol)
        self.assertIn("chat-scoped reports only", agents)
        self.assertIn("Batches live in the chat", readme)
        self.assertIn("v0.15.0", (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))

    def test_formalities_first_precedes_popularity_and_routes_human_decisions(self):
        protocol = (ROOT / "PROTOCOL.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        change = (ROOT / "changes/v0.16.0.md").read_text(encoding="utf-8")
        form = (ROOT / ".github/ISSUE_TEMPLATE/human-gate.yml").read_text(
            encoding="utf-8"
        )
        self.assertLess(protocol.index("### License and formalities first"),
                        protocol.index("### Default popularity priority"))
        self.assertIn("LICENSE_REVIEW_REQUIRED", protocol)
        self.assertIn("SCREENABLE_READ_ONLY", protocol)
        self.assertIn("HUMAN_GATE_PENDING", protocol)
        self.assertIn("INSUFFICIENT_EVIDENCE", protocol)
        self.assertIn("before", change.lower())
        self.assertIn("read-only", protocol)
        self.assertIn("availability/access decision", protocol)
        self.assertIn("not per batch", protocol)
        self.assertIn("human-gate.yml", readme)
        self.assertIn("human-gate.yml", agents)
        self.assertIn("Human gate", form)
        self.assertIn('title: "[Human gate] "', form)
        for field in ("original_repository", "gate_type", "source_revision",
                      "evidence", "decision", "safe_stage", "next"):
            self.assertIn("id: " + field, form)
        self.assertIn("Source / fork / runner access or availability", form)
        self.assertIn("No action by an autonomous executor", form)

    def test_release_bundle_is_agreement_first_not_per_change(self):
        versioning = (ROOT / "VERSIONING.md").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        candidate = (ROOT / "docs/RELEASE_CANDIDATE_v0.16.0.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("## Agreement-first version and release workflow", versioning)
        self.assertIn("## Unreleased", changelog)
        self.assertIn("without an automatic bump", versioning)
        self.assertIn("owner's agreement", versioning)
        self.assertIn("A `VERSION` on `main` may be newer", readme)
        self.assertIn("do **not** bump `VERSION`", agents)
        self.assertIn("v0.13.0", candidate)
        self.assertIn("v0.16.0", candidate)
        for number in (6, 7, 8, 9, 10):
            self.assertIn(f"PR #{number}", candidate)
        self.assertIn("11 merged / 24 open / 7 closed without merge", candidate)
        self.assertIn("NOT A PUBLISHED RELEASE", candidate)
        self.assertIn("Owner agrees", candidate)

    def test_upgrade_provisions_missing_fork_meta_under_actual_authority(self):
        protocol = (ROOT / "PROTOCOL.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        metadata = (ROOT / "docs/FORK_METADATA.md").read_text(encoding="utf-8")
        architecture = (ROOT / "docs/ARCHITECTURE.md").read_text(
            encoding="utf-8"
        )
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        section = protocol.split(
            "### Upgrade metadata materialization — missing `opensiro/meta`", 1
        )[1].split("### License and formalities first", 1)[0]
        for marker in (
            "Mandatory for full-cycle",
            "refs/heads/opensiro/meta",
            "pinned current fork default-branch commit",
            "fork=true",
            "parent.full_name",
            "independently authorize",
            "verified 404 for the branch",
            ".opensiro/state.json",
            ".opensiro/contributions/<stable-id>.json",
            "PAUSE",
            "STOP",
            "ALLOW",
            "ACTIVE",
            "optimistic compare-and-swap",
            "Read back and require coverage",
            "read-only aggregator",
            "Backfill an already published PR without creating another",
            "META_PROVISIONING_BLOCKED",
            "batch N",
        ):
            self.assertIn(marker, section)
        self.assertIn("ensure the fork's `opensiro/meta`", protocol)
        self.assertIn("If the branch is confirmed absent", readme)
        self.assertIn("Required `.opensiro/` provisioning", agents)
        self.assertIn("Materialize on demand during an authorized Upgrade", metadata)
        self.assertIn("Verified permission to write fork metadata?", architecture)
        self.assertIn("Upgrade metadata on demand (included in v0.17.0)", changelog)
        self.assertEqual((ROOT / "VERSION").read_text().strip(), "0.17.0")

    def test_invalid_semver_is_rejected(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for filename in REQUIRED:
                file = root / filename
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text("", encoding="utf-8")
            (root / "VERSION").write_text("0.12\n", encoding="utf-8")
            self.assertTrue(any("invalid SemVer" in x for x in check_contract(root)))

    def test_missing_change_package_is_rejected(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for filename in REQUIRED:
                file = root / filename
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text("", encoding="utf-8")
            (root / "VERSION").write_text("0.12.0\n", encoding="utf-8")
            self.assertTrue(any("missing changes/" in x for x in check_contract(root)))


if __name__ == "__main__":
    unittest.main()
