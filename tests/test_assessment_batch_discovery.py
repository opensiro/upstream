"""Offline exact-Index and live-inventory discovery tests, never touch GitHub."""

import base64
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import assessment_batch_discovery as mod

MAIN, TREE, BLOB, PR, INDEX_MAIN = ("a" * 40, "b" * 40, "c" * 40,
                                     "d" * 40, "e" * 40)
MANIFEST = "data/assessment-candidate-batches/2026-11-12-99.json"


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def b64(value):
    return {"encoding": "base64",
            "content": base64.b64encode(json.dumps(value).encode()).decode()}


class FakeReader:
    def __init__(self, index_sha, merged=None, proposed=None, registry=None,
                 *, missing=None, main_changed=False, pr_changed=False):
        self.index_sha = index_sha
        self.merged = merged
        self.proposed = proposed
        self.registry = registry if registry is not None else ["org/repo03"]
        self.missing = missing
        self.main_changed = main_changed
        self.pr_changed = pr_changed
        self.main_reads = 0
        self.pr_reads = 0

    def get(self, path):
        if path == self.missing:
            raise mod.BatchError("BLOCKED_GITHUB_VISIBILITY: unavailable")
        if path == "/repos/opensiro/vsm-harness-index/branches/main":
            return {"commit": {"sha": INDEX_MAIN}}
        if path == "/repos/opensiro/upstream/branches/main":
            self.main_reads += 1
            return {"commit": {"sha": "f" * 40 if self.main_changed and self.main_reads > 1 else MAIN}}
        if path == f"/repos/opensiro/vsm-harness-index/compare/{self.index_sha}...{INDEX_MAIN}":
            return {"status": "ahead", "behind_by": 0,
                    "base_commit": {"sha": self.index_sha}}
        if path == f"/repos/opensiro/upstream/git/commits/{MAIN}":
            return {"tree": {"sha": TREE}}
        if path == f"/repos/opensiro/upstream/git/trees/{TREE}?recursive=1":
            return {"truncated": False, "tree": ([{"path": MANIFEST, "type": "blob", "sha": BLOB}]
                                                  if self.merged else [])}
        if path == f"/repos/opensiro/upstream/git/blobs/{BLOB}":
            return b64(self.merged)
        if path == f"/repos/opensiro/upstream/contents/data/contribution-workspaces/registry.json?ref={MAIN}":
            return b64({"schema_version": 1,
                        "sources": [{"source": x} for x in self.registry]})
        if path == f"/repos/opensiro/upstream/contents/{MANIFEST}?ref={PR}":
            return b64(self.proposed)
        raise AssertionError("unexpected public GitHub path " + path)

    def pages(self, path):
        if path == "/repos/opensiro/upstream/pulls?state=open":
            self.pr_reads += 1
            if not self.proposed:
                return []
            sha = ("7" * 40) if self.pr_changed and self.pr_reads > 1 else PR
            return [{"number": 42, "head": {
                "sha": sha, "repo": {"full_name": "opensiro/upstream"}}}]
        if path == "/repos/opensiro/upstream/pulls/42/files":
            return [{"filename": MANIFEST, "status": "added"}]
        raise AssertionError("unexpected pagination path " + path)


class DiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.index = Path(cls.tmp.name) / "index"
        subprocess.run(["git", "init", "-q", str(cls.index)], check=True)
        git(cls.index, "config", "user.email", "test@example.org")
        git(cls.index, "config", "user.name", "Offline")
        for i in range(1, 9):
            p = cls.index / f"assessments/te/repo{i:02d}.md"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(f"---\nharness_id: repo{i:02d}\nproject_name: Repo{i:02d}\n"
                         f"repository: https://github.com/Org/Repo{i:02d}\n"
                         f"review_ref: {'1' * 40}\nreviewed_at: 2026-10-27\n"
                         "status: included\nautonomy_s1: A\nautonomy_s2: C\n---\n")
        # Included assessments with S1 != A or S2 != C belong to v2 intake.
        for i, s1, s2 in ((9, "C", "A"), (10, "P", "C"), (11, "A", "A")):
            p = cls.index / f"assessments/te/repo{i:02d}.md"
            p.write_text(f"---\nharness_id: repo{i:02d}\nproject_name: Repo{i:02d}\n"
                         f"repository: https://github.com/Org/Repo{i:02d}\n"
                         f"review_ref: {'1' * 40}\nreviewed_at: 2026-10-26\n"
                         f"status: included\nautonomy_s1: {s1}\nautonomy_s2: {s2}\n---\n")
        p = cls.index / "assessments/te/excluded.md"
        p.write_text("---\nharness_id: excluded\nrepository: https://github.com/Org/excluded\n"
                     f"review_ref: {'1' * 40}\nreviewed_at: 2026-10-27\n"
                     "status: excluded\nautonomy_s1: A\nautonomy_s2: C\n---\n")
        git(cls.index, "add", "assessments")
        git(cls.index, "commit", "-qm", "Canonical Index test fixture")
        cls.sha = git(cls.index, "rev-parse", "HEAD")
        sample = json.loads((ROOT / "data/assessment-candidate-batches/2026-10-22-01.json").read_text())
        cls.merged = copy.deepcopy(sample)
        cls.merged["batch_id"] = "assessment-upstream-2026-11-12-98"
        cls.merged["candidates"][0]["source"] = "ORG/REPO01"
        cls.proposed = copy.deepcopy(sample)
        cls.proposed["batch_id"] = "assessment-upstream-2026-11-12-99"
        cls.proposed["candidates"][0]["source"] = "org/repo02"

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_exact_five_excludes_merged_open_and_registry_aliases(self):
        fake = FakeReader(self.sha, merged=self.merged, proposed=self.proposed)
        report = mod.discover(self.index, self.sha, fake)
        self.assertEqual(report["status"], "PROPOSED_ONLY")
        self.assertEqual([r["source"] for r in report["selected"]],
                         [f"Org/Repo{i:02d}" for i in range(4, 9)])
        self.assertEqual(report["schema_version"], 2)
        self.assertTrue(report["function_assignment_required"])
        self.assertEqual(report["included_filter_count"], 11)
        self.assertEqual(report["eligible_count"], 8)
        self.assertEqual(report["main_manifest_count"], 1)
        self.assertEqual(report["active_pr_manifest_count"], 1)
        self.assertEqual(report["open_pr_count"], 1)
        self.assertTrue(report["remote_visibility_checked"])
        self.assertFalse(report["admission_attested"])
        self.assertFalse(report["external_writes_authorized"])

    def test_v2_default_discovers_non_a_s1_and_non_c_s2_without_inventing_function(self):
        fake = FakeReader(self.sha, registry=[])
        report = mod.discover(self.index, self.sha, fake, count=10)
        self.assertEqual(report["status"], "PROPOSED_ONLY")
        self.assertEqual(report["schema_version"], 2)
        self.assertTrue(report["function_assignment_required"])
        self.assertEqual(report["included_filter_count"], 11)
        selected = report["selected"]
        self.assertEqual(len(selected), 10)
        self.assertIn("Org/Repo09", [row["source"] for row in selected])
        self.assertIn("Org/Repo10", [row["source"] for row in selected])
        self.assertTrue(all("function" not in row for row in selected))

    def test_explicit_v1_preserves_historical_a_c_s2_discovery(self):
        reader = FakeReader(self.sha, registry=[])
        report = mod.discover(self.index, self.sha, reader, schema_version=1)
        self.assertEqual(report["schema_version"], 1)
        self.assertFalse(report["function_assignment_required"])
        self.assertEqual(report["included_filter_count"], 8)
        self.assertEqual([row["source"] for row in report["selected"]],
                         [f"Org/Repo{i:02d}" for i in range(1, 6)])
        self.assertTrue(all(row["function"] == "S2" for row in report["selected"]))
        with self.assertRaisesRegex(mod.BatchError, "Unsupported discovery schema"):
            mod.index_candidates(self.index, self.sha, schema_version=3)

    def test_no_full_five_row_cohort_is_explicit_not_padded(self):
        reader = FakeReader(self.sha, registry=[f"org/repo{i:02d}" for i in range(1, 10)])
        report = mod.discover(self.index, self.sha, reader)
        self.assertEqual(report["status"], "NO_ELIGIBLE_ASSESSMENT_CANDIDATE")
        self.assertEqual(report["eligible_count"], 2)
        self.assertEqual(report["selected"], [])

    def test_missing_index_sha_or_dirty_checkout_fails_closed(self):
        with self.assertRaisesRegex(mod.BatchError, "BLOCKED_INDEX_PROVENANCE"):
            mod.discover(self.index, "f" * 40, FakeReader(self.sha))
        p = self.index / "assessments/te/repo01.md"
        try:
            p.write_text(p.read_text() + "modified\n")
            with self.assertRaisesRegex(mod.BatchError, "dirty"):
                mod.index_candidates(self.index, self.sha)
        finally:
            git(self.index, "checkout", "--", "assessments/te/repo01.md")

    def test_duplicate_alias_in_exact_index_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            clone = Path(temp) / "cloned"
            subprocess.run(["git", "clone", "-q", "--local", str(self.index), str(clone)], check=True)
            git(clone, "config", "user.email", "test@example.org")
            git(clone, "config", "user.name", "Offline")
            p = clone / "assessments/te/repo08.md"
            p.write_text(p.read_text().replace("Org/Repo08", "ORG/REPO07"))
            git(clone, "add", "assessments")
            git(clone, "commit", "-qm", "Case-alias duplicate")
            with self.assertRaisesRegex(mod.BatchError, "duplicate included source"):
                mod.index_candidates(clone, git(clone, "rev-parse", "HEAD"))

    def test_unavailable_github_or_mutating_pr_fails_closed(self):
        missing = f"/repos/opensiro/upstream/contents/data/contribution-workspaces/registry.json?ref={MAIN}"
        with self.assertRaisesRegex(mod.BatchError, "BLOCKED_GITHUB_VISIBILITY"):
            mod.discover(self.index, self.sha, FakeReader(self.sha, missing=missing))
        with self.assertRaisesRegex(mod.BatchError, "repository changed"):
            mod.discover(self.index, self.sha, FakeReader(self.sha, main_changed=True))
        with self.assertRaisesRegex(mod.BatchError, "repository changed"):
            mod.discover(self.index, self.sha, FakeReader(self.sha,
                 proposed=self.proposed, pr_changed=True))

    def test_excluded_records_are_never_selected_and_count_limits(self):
        rows = mod.index_candidates(self.index, self.sha)
        self.assertEqual(len(rows), 11)
        self.assertNotIn("Org/excluded", [r["source"] for r in rows])
        for count in (0, 4, 11):
            with self.assertRaisesRegex(mod.BatchError, "complete 5"):
                mod.discover(self.index, self.sha, FakeReader(self.sha), count)


if __name__ == "__main__":
    unittest.main()
