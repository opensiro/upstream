"""Deterministic offline GitHub visibility/preflight fixtures; no network calls."""

import base64
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
PATH = ROOT / "scripts/assessment_batch_conflict_preflight.py"
SPEC = importlib.util.spec_from_file_location("assessment_batch_conflict_preflight", PATH)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)
ORIGINAL = ROOT / "data/assessment-candidate-batches/2026-10-22-01.json"
MAIN_SHA, BLOB_SHA, PR_SHA, TREE_SHA = "1" * 40, "2" * 40, "3" * 40, "4" * 40
MAIN_PATH = "data/assessment-candidate-batches/2026-10-22-97.json"
PR_PATH = "data/assessment-candidate-batches/2026-10-22-98.json"


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def blob(payload):
    return {"encoding": "base64", "content": base64.b64encode(json.dumps(payload).encode()).decode()}


class FakeGithub:
    def __init__(self, *, main=None, pr=None, broken=None, changed=False, truncated=False):
        self.main = main
        self.pr = pr
        self.broken = broken
        self.changed = changed
        self.truncated = truncated
        self.branch_reads = 0

    def get(self, path):
        if path == self.broken:
            raise mod.BatchError("BLOCKED_GITHUB_VISIBILITY: simulated API failure")
        if path == "/repos/opensiro/upstream/branches/main":
            self.branch_reads += 1
            return {"commit": {"sha": "9" * 40 if self.changed and self.branch_reads > 1 else MAIN_SHA}}
        if path == f"/repos/opensiro/upstream/git/commits/{MAIN_SHA}":
            return {"tree": {"sha": TREE_SHA}}
        if path == f"/repos/opensiro/upstream/git/trees/{TREE_SHA}?recursive=1":
            return {"truncated": self.truncated, "tree": ([
                {"path": MAIN_PATH, "type": "blob", "sha": BLOB_SHA}]
                if self.main is not None else [])}
        if path == f"/repos/opensiro/upstream/git/blobs/{BLOB_SHA}" and self.main is not None:
            return blob(self.main)
        if path == f"/repos/opensiro/upstream/contents/{PR_PATH}?ref={PR_SHA}" and self.pr is not None:
            return blob(self.pr)
        raise AssertionError("Unexpected GitHub API path: " + path)

    def pages(self, path):
        if path == "/repos/opensiro/upstream/pulls?state=open":
            return ([{"number": 999, "head": {"sha": PR_SHA,
                      "repo": {"full_name": "opensiro/upstream"}}}]
                    if self.pr is not None else [])
        if path == "/repos/opensiro/upstream/pulls/999/files" and self.pr is not None:
            return [{"filename": PR_PATH, "status": "added"}]
        raise AssertionError("Unexpected GitHub pagination: " + path)


class PreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = tempfile.TemporaryDirectory()
        cls.index = Path(cls.fixture.name) / "index"
        subprocess.run(["git", "init", "-q", str(cls.index)], check=True)
        git(cls.index, "config", "user.email", "test@example.org")
        git(cls.index, "config", "user.name", "Offline test")
        cls.original = json.loads(ORIGINAL.read_text(encoding="utf-8"))
        for row in cls.original["candidates"]:
            file = cls.index / row["assessment_path"]
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text("---\n" + "\n".join((
                f"harness_id: {file.stem}",
                f"repository: https://github.com/{row['source']}",
                f"review_ref: {row['review_ref']}",
                f"reviewed_at: {row['reviewed_at']}",
                "status: included", "autonomy_s1: A"
            )) + "\n---\n", encoding="utf-8")
        git(cls.index, "add", "assessments")
        git(cls.index, "commit", "-qm", "Index fixture")
        cls.original["index_sha"] = git(cls.index, "rev-parse", "HEAD")

    @classmethod
    def tearDownClass(cls):
        cls.fixture.cleanup()

    def unrelated(self):
        payload = copy.deepcopy(self.original)
        payload["batch_id"] = "assessment-upstream-2026-10-22-97"
        for i, row in enumerate(payload["candidates"]):
            row["source"] = f"UnrelatedOwner/OtherRepo{i}"
        return payload

    def test_clear_snapshot_checks_both_merged_and_open_manifest(self):
        reader = FakeGithub(main=self.unrelated(), pr=self.unrelated())
        report = mod.preflight(self.original, self.index, reader)
        self.assertEqual(report["status"], "CLEAR_PREVIEW_ONLY")
        self.assertFalse(report["admission_attested"])
        self.assertEqual(report["main_manifest_count"], 1)
        self.assertEqual(report["active_pr_manifest_count"], 1)
        self.assertEqual(report["open_pr_count"], 1)

    def test_merged_source_casefold_collision_is_blocked(self):
        merged = self.unrelated()
        merged["candidates"][1]["source"] = self.original["candidates"][0]["source"].upper()
        report = mod.preflight(self.original, self.index, FakeGithub(main=merged))
        self.assertEqual(report["status"], "BLOCKED_DUPLICATE_SOURCE")
        self.assertEqual(len(report["collisions"]), 1)
        self.assertTrue(report["collisions"][0]["location"].startswith("main@"))

    def test_open_draft_collision_is_blocked(self):
        active = self.unrelated()
        active["candidates"][3]["source"] = self.original["candidates"][0]["source"]
        report = mod.preflight(self.original, self.index, FakeGithub(pr=active))
        self.assertEqual(report["status"], "BLOCKED_DUPLICATE_SOURCE")
        self.assertIn("PR#999", report["collisions"][0]["location"])

    def test_own_pr_only_excluded_when_manifest_matches(self):
        reader = FakeGithub(pr=copy.deepcopy(self.original))
        report = mod.preflight(self.original, self.index, reader, own_pr=999)
        self.assertEqual(report["status"], "CLEAR_PREVIEW_ONLY")
        with self.assertRaisesRegex(mod.BatchError, "own PR manifest differs"):
            mod.preflight(self.original, self.index, FakeGithub(pr=self.unrelated()), own_pr=999)
        with self.assertRaisesRegex(mod.BatchError, "own PR must contain exactly one"):
            mod.preflight(self.original, self.index, FakeGithub(), own_pr=999)

    def test_visibility_failure_truncated_tree_and_changed_main_fail_closed(self):
        for reader, message in ((FakeGithub(truncated=True), "incomplete canonical main tree"),
                                (FakeGithub(changed=True), "repository changed during preflight"),
                                (FakeGithub(broken=f"/repos/opensiro/upstream/git/trees/{TREE_SHA}?recursive=1"),
                                 "BLOCKED_GITHUB_VISIBILITY")):
            with self.subTest(message=message):
                with self.assertRaisesRegex(mod.BatchError, message):
                    mod.preflight(self.original, self.index, reader)

    def test_invalid_index_pin_and_partial_cohort_fail_before_github(self):
        manifest = copy.deepcopy(self.original)
        manifest["index_sha"] = "0" * 40
        with self.assertRaisesRegex(mod.BatchError, "Index HEAD differs"):
            mod.preflight(manifest, self.index, FakeGithub())
        manifest = copy.deepcopy(self.original)
        manifest["candidates"].pop()
        with self.assertRaisesRegex(mod.BatchError, "Freeze a full cohort"):
            mod.preflight(manifest, self.index, FakeGithub())


if __name__ == "__main__":
    unittest.main()
