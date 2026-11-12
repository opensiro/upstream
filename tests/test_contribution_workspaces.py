"""Offline-only tests for the additive source/fork outbox."""

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/contribution_workspaces.py"
SPEC = importlib.util.spec_from_file_location("contribution_workspaces", SCRIPT)
workspaces = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(workspaces)


class WorkspaceTests(unittest.TestCase):
    def test_priority_pool_plus_all_integrated_screening_batches(self):
        report = workspaces.build()
        counts = report["counts"]
        self.assertEqual(counts["priority_sources"], 100)
        self.assertGreaterEqual(counts["historical_extras"], 83)
        self.assertGreaterEqual(counts["batch_only_extras"], 70)
        self.assertGreaterEqual(counts["pilot_only_extras"], 5)
        self.assertGreaterEqual(counts["portfolio_only_extras"], 8)
        self.assertGreaterEqual(counts["unique_sources"], 183)
        self.assertGreaterEqual(counts["batch_cases"], 125)
        self.assertGreaterEqual(counts["technical_handoffs"], 50)
        self.assertEqual(counts["historical_fork_mappings"], 16)
        self.assertGreaterEqual(counts["dated_fork_readbacks"], 16)
        self.assertGreaterEqual(counts["same_named_ref_matches_at_readback"], 0)
        self.assertGreaterEqual(counts["name_collision_sources"], 10)
        self.assertEqual(len({r["source"].casefold() for r in report["sources"]}),
                         counts["unique_sources"])

    def test_other_native_pilots_and_historical_pr_projects_are_not_lost(self):
        report = workspaces.build()
        by_source = {r["source"].casefold(): r for r in report["sources"]}
        self.assertEqual(by_source["speakeasy-api/kit"]["priority_group"], "PILOT_EXTRA")
        self.assertEqual(by_source["avala-ai/agent-code"]["next_step"],
                         "RECONCILE_NATIVE_PILOT_BEFORE_FORK_STAGE")
        self.assertEqual(by_source["codexmark/kram"]["pilot_links"][0]["case_id"],
                         "kram-s2-native-edit-atomicity")
        self.assertEqual(by_source["topoteretes/cognee-community"]["priority_group"],
                         "PORTFOLIO_EXTRA")
        self.assertEqual(by_source["shep-ai/shep"]["historical_prs"],
                         ["https://github.com/shep-ai/shep/pull/933",
                          "https://github.com/shep-ai/shep/pull/934"])
        self.assertEqual(by_source["shep-ai/shep"]["next_step"],
                         "HISTORICAL_PR_TRACK_ONLY_NO_NEW_PUBLICATION")

    def test_no_fork_or_pr_write_claimed_and_no_wrong_parent_by_basename(self):
        report = workspaces.build()
        by_source = {row["source"].casefold(): row for row in report["sources"]}
        phoenix = by_source["phoenixrr2113/agent-harness"]
        talktorana = by_source["talktorana/agent-harness"]
        self.assertEqual(phoenix["fork"], "opensiro-contributions/agent-harness")
        self.assertEqual(phoenix["fork_state"], "HISTORICAL_MAPPING_REQUIRES_LIVE_READBACK")
        self.assertEqual(phoenix["dated_fork_readback"]["fork"],
                         "opensiro-contributions/agent-harness")
        self.assertTrue(phoenix["dated_fork_readback"]["recheck_before_any_write"])
        self.assertIsNotNone(by_source["harnessdesk/harnessdesk"]["dated_fork_readback"])
        self.assertIsNone(talktorana["fork"])
        self.assertIsNone(talktorana["proposed_fork"])
        self.assertEqual(talktorana["next_step"], "RESOLVE_FORK_PARENT_AND_NAME")
        self.assertEqual(report["execution"]["external_pr"],
                         "CHECK_EFFECTIVE_STANDING_MANDATE_AND_NATIVE_GATES")
        self.assertEqual(report["execution"]["external_pr_policy_source"],
                         "policies/standing-external-publication-p1.json")
        self.assertTrue((ROOT / report["execution"]["external_pr_policy_source"]).is_file())
        self.assertFalse(report["execution"]["auto_external_pr"])
        self.assertFalse(report["execution"]["live_forks_verified_by_this_script"])
        self.assertFalse(report["execution"]["dated_fork_readback_is_live_authority"])

    def test_negative_and_blocked_rows_remain_tracked_without_patch_claim(self):
        report = workspaces.build()
        by_source = {r["source"].casefold(): r for r in report["sources"]}
        self.assertEqual(by_source["openjiuwen-ai/agent-runtime"]["latest_stage"], "CLOSED_NO_CHANGE")
        self.assertEqual(by_source["openjiuwen-ai/agent-runtime"]["handoffs"], [])
        self.assertEqual(by_source["codewhale-hq/codewhale"]["latest_stage"], "BLOCKED_EVIDENCE")
        self.assertEqual(by_source["codewhale-hq/codewhale"]["handoffs"], [])
        self.assertEqual(by_source["ayandexyz/honey-i-shrunk-the-harness"]["latest_stage"], "AWAITING_EXTERNAL")
        self.assertTrue(by_source["ayandexyz/honey-i-shrunk-the-harness"]["handoffs"])

    def test_local_pilot_artifacts_are_bound_to_registry_without_auto_selection(self):
        by_source = {r["source"].casefold(): r for r in workspaces.build()["sources"]}
        known = by_source["0xnyk/lacp"]["handoffs"][0]["technical_packet"]
        self.assertEqual(known["state"], "EXPLICIT_PATCH_HASH_MATCHED")
        self.assertEqual(
            known["explicit_patch"]["sha256"],
            by_source["0xnyk/lacp"]["handoffs"][0]["patch_sha256"],
        )
        discovered = by_source["agentenv/agentflow"]["handoffs"][0]["technical_packet"]
        self.assertEqual(discovered["state"], "LOCAL_SINGLE_PATCH_UNREVIEWED")
        self.assertTrue(discovered["pilot"]["content_sha256"])
        ambiguous = by_source["evermind-ai/raven"]["handoffs"][0]["technical_packet"]
        self.assertEqual(ambiguous["state"], "LOCAL_MULTI_PATCH_SELECTION_REQUIRED")
        self.assertGreater(len(ambiguous["pilot"]["patch_candidates"]), 1)
        remote = by_source["sethgammon/citadel"]["handoffs"][0]["technical_packet"]
        self.assertEqual(remote["state"], "NO_LOCAL_PACKET_OR_PR_ONLY_HANDOFF")
        standalone = by_source["codexmark/kram"]["pilot_links"][0]
        self.assertTrue(standalone["local_evidence"]["content_sha256"])
        self.assertTrue(standalone["local_patch_sha256"])
        counts = workspaces.build()["counts"]
        self.assertEqual(sum(counts["technical_packet_states"].values()),
                         counts["technical_handoffs"])
        self.assertGreaterEqual(counts["technical_packet_states"]
                                ["EXPLICIT_PATCH_HASH_MATCHED"], 10)

    def test_selected_legacy_packets_are_exact_and_frozen_batches_unchanged(self):
        by_source = {r["source"].casefold(): r for r in workspaces.build()["sources"]}
        for source, digest in (
            ("microsoft/fara", "fce42386bd6b1cf1ea0fed6c22a206589239cdeeb37f53cfaa48eb027da9002e"),
            ("kumihoio/revka", "61c63244a659849c4c25adee79eb1d6abc4ee859eff906069284579365fb82e5"),
            ("kstawiski/evidence-gated-scientific-agent",
             "0974cdefa228cfdf37e1b750144e01c269c8f2dee6d9aa8ea01e86dd79b23646"),
        ):
            handoff = by_source[source]["handoffs"][0]
            self.assertEqual(handoff["technical_packet"]["state"],
                             "EXPLICIT_PATCH_HASH_MATCHED")
            self.assertEqual(handoff["patch_sha256"], digest)
            self.assertEqual(handoff["technical_packet"]["explicit_patch"]["sha256"], digest)
        frozen = json.loads((ROOT / workspaces.BATCH_DIR / "2026-10-23-11.json").read_text())
        for item in frozen["candidates"]:
            if item["source"].casefold() in (
                "microsoft/fara", "kstawiski/evidence-gated-scientific-agent"
            ):
                self.assertNotIn("patch_path", item)
                self.assertNotIn("patch_sha256", item)

    def test_selected_packet_duplicate_and_missing_receipt_fail_closed(self):
        data = json.loads((ROOT / workspaces.SELECTED_PACKETS).read_text())
        # This isolated negative case tests one receipt, independent of later selections.
        data["selections"] = data["selections"][:1]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            destination = root / workspaces.SELECTED_PACKETS
            destination.parent.mkdir(parents=True)
            destination.write_text(json.dumps(data))
            with self.assertRaisesRegex(workspaces.WorkspaceError,
                                        "native validation receipt"):
                workspaces._selected_patch_packets(root)
            report = root / data["selections"][0]["receipt"]
            report.parent.mkdir(parents=True)
            report.write_text("verified")
            data["selections"].append(dict(data["selections"][0]))
            destination.write_text(json.dumps(data))
            with self.assertRaisesRegex(workspaces.WorkspaceError,
                                        "Duplicate selected packet"):
                workspaces._selected_patch_packets(root)

    def test_wave_pilot_only_sources_not_misclassified_as_stage_ready(self):
        by_source = {r["source"].casefold(): r for r in workspaces.build()["sources"]}
        for source, pr in (("scaleml/agentspex", 116),
                           ("howl-anderson/agentsilex", 115)):
            row = by_source[source]
            self.assertEqual(row["priority_group"], "PILOT_EXTRA")
            self.assertEqual(row["handoffs"], [])
            self.assertIsNone(row["latest_stage"])
            self.assertEqual(len(row["pilot_links"]), 1)
            self.assertEqual(row["pilot_links"][0]["evidence"],
                             "https://github.com/opensiro/upstream/pull/" + str(pr))
            self.assertFalse(row["license_review"])

    def test_generated_registry_is_current_and_check_is_read_only(self):
        self.assertEqual((ROOT / workspaces.REGISTRY).read_text(encoding="utf-8"),
                         workspaces.encoded(workspaces.build()))
        result = subprocess.run(["python3", str(SCRIPT), "check"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_new_batch_source_is_automatically_included_after_sync(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pool = root / workspaces.POOL
            pool.parent.mkdir(parents=True)
            shutil.copyfile(ROOT / workspaces.POOL, pool)
            pilot_path = root / workspaces.PILOTS
            pilot_path.parent.mkdir(parents=True, exist_ok=True)
            # The test deliberately creates an empty supplementary pilot ledger.
            pilot_path.write_text(json.dumps({"schema_version": 1, "cases": []}), encoding="utf-8")
            historical_path = root / workspaces.PR_HISTORY
            historical_path.parent.mkdir(parents=True, exist_ok=True)
            historical_path.write_text(json.dumps({"schema_version": 2, "records": [],
                                                  "registry_records": []}), encoding="utf-8")
            batches = root / workspaces.BATCH_DIR
            batches.mkdir(parents=True)
            source_batch = ROOT / workspaces.BATCH_DIR / "2026-11-09-22.json"
            manifest = json.loads(source_batch.read_text(encoding="utf-8"))
            manifest["batch_id"] = "assessment-upstream-2026-11-10-23"
            manifest["candidates"] = [{
                "source": "someone/BrandNewHarness", "stage": "AWAITING_EXTERNAL",
                "id": "new-source-native-change", "origin": "ASSESSMENT_DERIVED",
                "handoff_url": "https://github.com/opensiro/upstream/issues/56",
                "patch_path": "pilots/brand-new/native-fix.patch",
            }]
            (batches / "2026-11-10-23.json").write_text(json.dumps(manifest), encoding="utf-8")
            before = workspaces.build(root)
            self.assertEqual(before["counts"]["historical_extras"], 1)
            self.assertEqual(before["counts"]["unique_sources"], 101)
            command = ["python3", str(SCRIPT)]
            self.assertNotEqual(subprocess.run(command + ["check", "--root", tmp], capture_output=True).returncode, 0)
            self.assertEqual(subprocess.run(command + ["sync", "--root", tmp], capture_output=True).returncode, 0)
            self.assertEqual(subprocess.run(command + ["check", "--root", tmp], capture_output=True).returncode, 0)
            rec = next(r for r in workspaces.build(root)["sources"] if r["source"] == "someone/BrandNewHarness")
            self.assertEqual(rec["proposed_fork"], "opensiro-contributions/BrandNewHarness")
            self.assertEqual(rec["fork_state"], "UNVERIFIED_NOT_PROVISIONED")
            self.assertEqual(rec["next_step"], "VERIFY_FORK_AND_PREPARE_PATCH_WITH_STAGE_GRANT")
            self.assertEqual(rec["handoffs"][0]["technical_packet"]["state"],
                             "EXPLICIT_PATCH_MISSING_OR_UNSAFE")
            pilot = root / "pilots/brand-new"
            pilot.mkdir(parents=True)
            patch = pilot / "native-fix.patch"
            patch.write_text("original patch", encoding="utf-8")
            self.assertNotEqual(subprocess.run(command + ["check", "--root", tmp],
                                              capture_output=True).returncode, 0)
            self.assertEqual(subprocess.run(command + ["sync", "--root", tmp],
                                            capture_output=True).returncode, 0)
            patch.write_text("changed patch", encoding="utf-8")
            self.assertNotEqual(subprocess.run(command + ["check", "--root", tmp],
                                              capture_output=True).returncode, 0)

    def test_duplicate_pool_identity_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / workspaces.POOL
            path.parent.mkdir(parents=True)
            pool = json.loads((ROOT / workspaces.POOL).read_text(encoding="utf-8"))
            pool["new_index_hypothesis_screens"].append(dict(pool["existing_forks"][0]))
            path.write_text(json.dumps(pool), encoding="utf-8")
            with self.assertRaisesRegex(workspaces.WorkspaceError, "Duplicate priority source"):
                workspaces.build(root)

    def test_fork_readback_without_exact_api_provenance_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = root / workspaces.FORK_READBACK_DIR
            directory.mkdir(parents=True)
            (directory / "2026-11-09.json").write_text(json.dumps({
                "schema_version": 1, "observed_on": "2026-11-09",
                "source": "CONNECTED_GITHUB_REST_READ_ONLY",
                "entries": [{
                    "source": "Phoenixrr2113/agent-harness",
                    "fork": "opensiro-contributions/agent-harness",
                    "parent_verified": True, "public_fork_verified": True,
                    "branch": "main", "fork_sha": "a" * 40,
                    "source_same_named_branch_sha": "a" * 40,
                    "ref_relation": "MATCH",
                    "repo_evidence": "https://example.com/unverified",
                    "fork_branch_evidence": "https://example.com/unverified",
                    "source_branch_evidence": "https://example.com/unverified",
                }],
            }), encoding="utf-8")
            with self.assertRaisesRegex(workspaces.WorkspaceError,
                                        "Missing or mismatched GitHub readback provenance"):
                workspaces.build(root)

    def test_new_fork_readback_is_additive_without_rewriting_priority_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pool = root / workspaces.POOL
            pool.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / workspaces.POOL, pool)
            pilots = root / workspaces.PILOTS
            pilots.parent.mkdir(parents=True, exist_ok=True)
            pilots.write_text(json.dumps({"schema_version": 1, "cases": []}),
                              encoding="utf-8")
            history = root / workspaces.PR_HISTORY
            history.parent.mkdir(parents=True, exist_ok=True)
            history.write_text(json.dumps({"schema_version": 2, "records": [],
                                           "registry_records": []}), encoding="utf-8")
            directory = root / workspaces.FORK_READBACK_DIR
            directory.mkdir(parents=True)
            source = "talktorana/agent-harness"
            fork = "opensiro-contributions/agent-harness-talktorana"
            (directory / "2026-11-10.json").write_text(json.dumps({
                "schema_version": 1, "observed_on": "2026-11-10",
                "source": "CONNECTED_GITHUB_REST_READ_ONLY",
                "entries": [{
                    "source": source, "fork": fork,
                    "parent_verified": True, "public_fork_verified": True,
                    "branch": "main", "fork_sha": "a" * 40,
                    "source_same_named_branch_sha": "a" * 40,
                    "ref_relation": "MATCH",
                    "repo_evidence": f"https://api.github.com/repos/{fork}",
                    "fork_branch_evidence":
                        f"https://api.github.com/repos/{fork}/branches/main",
                    "source_branch_evidence":
                        f"https://api.github.com/repos/{source}/branches/main",
                }],
            }), encoding="utf-8")
            report = workspaces.build(root)
            row = next(r for r in report["sources"]
                       if r["source"].casefold() == source)
            self.assertIsNone(row["fork"])
            self.assertEqual(row["proposed_fork"], fork)
            self.assertEqual(row["fork_state"], "DATED_MAPPING_REQUIRES_LIVE_READBACK")
            self.assertTrue(row["dated_fork_readback"]["recheck_before_any_write"])


if __name__ == "__main__":
    unittest.main()
