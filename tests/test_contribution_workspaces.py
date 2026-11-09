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
        self.assertEqual(counts["historical_extras"], 70)
        self.assertEqual(counts["unique_sources"], 170)
        self.assertEqual(counts["batch_cases"], 125)
        self.assertEqual(counts["technical_handoffs"], 50)
        self.assertEqual(counts["historical_fork_mappings"], 16)
        self.assertEqual(counts["name_collision_sources"], 10)
        self.assertEqual(len({r["source"].casefold() for r in report["sources"]}), 170)

    def test_no_fork_or_pr_write_claimed_and_no_wrong_parent_by_basename(self):
        report = workspaces.build()
        by_source = {row["source"].casefold(): row for row in report["sources"]}
        phoenix = by_source["phoenixrr2113/agent-harness"]
        talktorana = by_source["talktorana/agent-harness"]
        self.assertEqual(phoenix["fork"], "opensiro-contributions/agent-harness")
        self.assertEqual(phoenix["fork_state"], "HISTORICAL_MAPPING_REQUIRES_LIVE_READBACK")
        self.assertIsNone(talktorana["fork"])
        self.assertIsNone(talktorana["proposed_fork"])
        self.assertEqual(talktorana["next_step"], "RESOLVE_FORK_PARENT_AND_NAME")
        self.assertEqual(report["execution"]["external_pr"], "HUMAN_EXPLICIT_APPROVAL_REQUIRED")
        self.assertFalse(report["execution"]["auto_external_pr"])
        self.assertFalse(report["execution"]["live_forks_verified_by_this_script"])

    def test_negative_and_blocked_rows_remain_tracked_without_patch_claim(self):
        report = workspaces.build()
        by_source = {r["source"].casefold(): r for r in report["sources"]}
        self.assertEqual(by_source["openjiuwen-ai/agent-runtime"]["latest_stage"], "CLOSED_NO_CHANGE")
        self.assertEqual(by_source["openjiuwen-ai/agent-runtime"]["handoffs"], [])
        self.assertEqual(by_source["codewhale-hq/codewhale"]["latest_stage"], "BLOCKED_EVIDENCE")
        self.assertEqual(by_source["codewhale-hq/codewhale"]["handoffs"], [])
        self.assertEqual(by_source["ayandexyz/honey-i-shrunk-the-harness"]["latest_stage"], "AWAITING_EXTERNAL")
        self.assertTrue(by_source["ayandexyz/honey-i-shrunk-the-harness"]["handoffs"])

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


if __name__ == "__main__":
    unittest.main()
