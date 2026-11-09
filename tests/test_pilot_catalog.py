"""Deterministic, no-network validation of historical pilot navigation."""

import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/pilot_catalog.py"
SPEC = importlib.util.spec_from_file_location("pilot_catalog", SCRIPT)
catalog = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(catalog)


class CatalogTests(unittest.TestCase):
    def test_historical_directories_all_present_and_original_paths_stable(self):
        report = catalog.build()
        self.assertEqual(report["counts"]["pilot_directories"], 66)
        self.assertEqual(report["counts"]["artifact_files"], 178)
        self.assertEqual(report["counts"]["by_kind"], {
            "EXPERIMENT_SERIES": 3,
            "PATCH_HANDOFF": 47,
            "PATCH_EVIDENCE": 0,
            "SCREEN_ONLY": 16,
            "OTHER_EVIDENCE": 0,
        })
        self.assertEqual(len(set(e["id"] for e in report["entries"])), 66)
        for entry in report["entries"]:
            self.assertEqual(entry["path"], "pilots/" + entry["id"])
            self.assertTrue((ROOT / entry["start_here"]).is_file())
            self.assertEqual(sum(entry["artifact_counts"].values()), len(entry["files"]))
            self.assertNotIn("SUCCESS", entry)
            self.assertNotIn("external_pr_status", entry)

    def test_examples_are_not_conflated_with_live_forks(self):
        entries = {entry["id"]: entry for entry in catalog.build()["entries"]}
        self.assertEqual(entries["zot-shared-workspace"]["kind"], "EXPERIMENT_SERIES")
        self.assertEqual(entries["agentbox-s2"]["kind"], "EXPERIMENT_SERIES")
        self.assertEqual(entries["kram-s2"]["kind"], "EXPERIMENT_SERIES")
        self.assertEqual(entries["harnessdesk-1772"]["kind"], "PATCH_HANDOFF")
        self.assertEqual(entries["ateles"]["kind"], "SCREEN_ONLY")
        self.assertEqual(entries["agentbox-s2"]["start_here"],
                         "pilots/agentbox-s2/SCREENING_AND_NATIVE_FIT_2026-10-20.md")

    def test_generated_catalog_is_exact_and_ci_check_is_read_only(self):
        report = catalog.build()
        self.assertEqual((ROOT / catalog.JSON_OUT).read_text(encoding="utf-8"),
                         catalog.json_text(report))
        self.assertEqual((ROOT / catalog.MARKDOWN_OUT).read_text(encoding="utf-8"),
                         catalog.markdown_text(report))
        result = subprocess.run(["python3", str(SCRIPT), "check"], text=True,
                                capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_new_experiment_file_invalidates_catalog_until_regenerated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            case = root / "pilots" / "fresh"
            case.mkdir(parents=True)
            (case / "SCREENING.md").write_text("A negative screen", encoding="utf-8")
            command = ["python3", str(SCRIPT)]
            self.assertNotEqual(subprocess.run(command + ["check", "--root", tmp],
                                              capture_output=True).returncode, 0)
            self.assertEqual(subprocess.run(command + ["sync", "--root", tmp],
                                            capture_output=True).returncode, 0)
            self.assertEqual(subprocess.run(command + ["check", "--root", tmp],
                                            capture_output=True).returncode, 0)
            (case / "new-native-test.py").write_text("print('ok')", encoding="utf-8")
            self.assertNotEqual(subprocess.run(command + ["check", "--root", tmp],
                                              capture_output=True).returncode, 0)


if __name__ == "__main__":
    unittest.main()
