"""Offline checks for the joined Harness -> Intervention -> PR projection."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("harness_status", ROOT / "scripts/harness_status.py")
status = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(status)


class HarnessStatusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.view = status.build_view()
        cls.interventions = {row["id"]: row for row in cls.view["interventions"]}
        cls.harnesses = {row["id"]: row for row in cls.view["harnesses"]}

    def test_multifunction_v2_screen_remains_distinct_from_external_delivery(self):
        self.assertIn("assessment-upstream-2026-11-13-37", {b["id"] for b in self.view["batches"]})
        for ident, function, stage in (("roboharness-observation-receipt-diagnostics", "S1", "CLOSED_NO_CHANGE"),
                                      ("helix-framework-candidate-comparison", "S4", "BLOCKED_EVIDENCE"),
                                      ("hyperscale-report-discrepancy-triage", "S3*", "CLOSED_NO_CHANGE")):
            row = self.interventions["assessment:" + ident]
            self.assertEqual(row["vsm_functions"], [function])
            self.assertEqual(row["technical_status"], stage)
            self.assertEqual(row["external_status"], "NONE")
            self.assertEqual(row["pr_urls"], [])

    def test_reconciles_independent_owning_sources(self):
        self.assertGreaterEqual(self.view["sources"]["batch_manifests"], 12)
        self.assertGreaterEqual(len(self.view["harnesses"]), 1)
        self.assertEqual(sum(len(b["interventions"]) for b in self.view["batches"]),
                         sum(i["kind"] == "assessment_batch" for i in self.view["interventions"]))
        self.assertEqual(34, sum("publication_ref" in i and "corrective-publication" in i["publication_ref"]
                                 for i in self.view["interventions"]))
        self.assertEqual(2, sum(i["external_status"] == "MERGED_UPSTREAM"
                                for i in self.view["interventions"]))
        self.assertEqual(len(self.view["prs"]), len({r["url"] for r in self.view["prs"]}))
        for harness in self.view["harnesses"]:
            for ident in harness["interventions"]:
                self.assertEqual(harness["id"], self.interventions[ident]["harness_id"])

    def test_two_independent_changes_in_one_harness(self):
        shep = self.harnesses["shep-ai/shep"]
        self.assertIn("portfolio:shep-933", shep["interventions"])
        self.assertIn("portfolio:shep-934", shep["interventions"])
        self.assertNotEqual(self.interventions["portfolio:shep-933"]["pr_urls"],
                            self.interventions["portfolio:shep-934"]["pr_urls"])

    def test_publication_overlay_does_not_rewrite_frozen_batch(self):
        citadel = self.interventions["assessment:citadel-native-claim-exclusivity"]
        crewdeck = self.interventions["assessment:crewdeck-s2-manual-claim-admission"]
        self.assertEqual("AWAITING_EXTERNAL", citadel["technical_status"])
        self.assertEqual("MERGED_UPSTREAM", citadel["external_status"])
        self.assertIn("Accepted externally", status.next_action(citadel))
        self.assertEqual("AWAITING_EXTERNAL", crewdeck["technical_status"])
        self.assertEqual("NOT_SUBMITTED", crewdeck["external_status"])
        self.assertEqual([], crewdeck["pr_urls"])

    def test_intervention_can_have_replacement_pr_and_pr_can_link_multiple_changes(self):
        project = self.interventions["portfolio:henterprise-1"]
        self.assertEqual(2, len(project["pr_urls"]))
        synthetic = {}
        url = "https://github.com/example/repo/pull/123"
        status.add_pr(synthetic, url, "assessment:a", "OPEN", "source-a")
        status.add_pr(synthetic, url, "assessment:b", "OPEN", "source-b")
        status.add_pr(synthetic, url, "assessment:a", "OPEN", "source-a")
        self.assertEqual(["assessment:a", "assessment:b"], synthetic[url]["interventions"])
        self.assertEqual(2, len(synthetic[url]["observations"]))

    def test_filter_preserves_references_and_does_not_count_merged_as_pending(self):
        merged = status.filter_view(self.view, "merged")
        awaiting = status.filter_view(self.view, "awaiting-external")
        blocked = status.filter_view(self.view, "blocked")
        actionable = status.filter_view(self.view, "actionable")
        self.assertIn("assessment:citadel-native-claim-exclusivity", {i["id"] for i in merged["interventions"]})
        self.assertNotIn("assessment:citadel-native-claim-exclusivity", {i["id"] for i in awaiting["interventions"]})
        self.assertIn("assessment:crewdeck-s2-manual-claim-admission", {i["id"] for i in awaiting["interventions"]})
        self.assertTrue(blocked["interventions"])
        self.assertTrue(actionable["interventions"])
        for selection in (merged, awaiting, blocked, actionable):
            known = {i["id"] for i in selection["interventions"]}
            self.assertTrue(all(set(h["interventions"]).issubset(known) for h in selection["harnesses"]))
            self.assertTrue(all(set(p["interventions"]).issubset(known) for p in selection["prs"]))
            self.assertTrue(all(set(b["interventions"]).issubset(known) for b in selection["batches"]))

    def test_invalid_source_and_pr_fail_closed(self):
        for source in ("owner/repo/path", "https://github.com/owner/repo", "../repo", ""):
            with self.subTest(source=source), self.assertRaises(ValueError):
                status.repo_key(source)
        with self.assertRaises(ValueError):
            status.pr_repo("https://github.com/example/repo/issues/1")

    def test_reproducible_document_and_cli(self):
        content = status.render_markdown(self.view)
        self.assertEqual(content, (ROOT / "HARNESS_STATUS.md").read_text(encoding="utf-8"))
        self.assertIn("one row per independent change", content)
        self.assertIn("SUBMITTED_UNVERIFIED_LIVE", content)
        process = subprocess.run([sys.executable, str(ROOT / "scripts/harness_status.py"),
                                  "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stderr)
        forbidden = subprocess.run([sys.executable, str(ROOT / "scripts/harness_status.py"),
                                    "--write", "--filter", "merged"], cwd=ROOT, capture_output=True, text=True)
        self.assertNotEqual(forbidden.returncode, 0)
        self.assertIn("Cannot write/check a filtered projection", forbidden.stderr)


if __name__ == "__main__":
    unittest.main()
