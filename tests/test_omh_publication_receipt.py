"""Validate source-identity, evidence and watcher consistency for OMH publication."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "witt3rd/oh-my-hermes"
URL = "https://github.com/witt3rd/oh-my-hermes/pull/28"
FORK = "opensiro-contributions/oh-my-hermes"
HEAD = "6eced4fdad9ff4faa7daf0979021d870558e8d26"
BASE = "3b06e33ae67b202b342989b484f08143e65e250d"


class OhMyHermesPublicationReceiptTests(unittest.TestCase):
    @staticmethod
    def read(path):
        return json.loads((ROOT / path).read_text())

    def test_exact_publication_identity_not_adoption(self):
        ledger = self.read("data/external-pr-publication-readbacks/2026-11-12.json")
        matches = [r for r in ledger["cases"] if r["repository"] == SOURCE]
        self.assertEqual(len(matches), 1)
        row = matches[0]
        self.assertEqual(row["id"], "oh-my-hermes-crossprocess-lock")
        self.assertEqual(row["pr_url"], URL)
        self.assertEqual(row["fork_local_pr_url"],
                         "https://github.com/opensiro-contributions/oh-my-hermes/pull/1")
        self.assertEqual((row["head_sha"], row["base_sha"]), (HEAD, BASE))
        self.assertEqual(row["public_fork"], FORK)
        self.assertEqual(row["publication_state"], "OPEN_READY")
        self.assertTrue(row["approved_exact_title_body"])
        self.assertIn("No individual CLA/DCO", row["approval_boundary"])
        self.assertIn("no maintainer merge", ledger["metric_boundary"].lower())

    def test_watchlist_and_dated_authentic_fork(self):
        watch = self.read("data/pr-maintenance/targets.json")
        cases = [p for p in watch["targets"] if p["url"] == URL]
        self.assertEqual(cases, [{"repository": SOURCE, "number": 28, "url": URL}])
        dated = self.read("data/contribution-workspaces/fork-readbacks/2026-11-12.json")
        cases = [p for p in dated["entries"] if p["source"] == SOURCE]
        self.assertEqual(len(cases), 1)
        row = cases[0]
        self.assertEqual(row["fork"], FORK)
        self.assertEqual((row["fork_sha"], row["source_same_named_branch_sha"]),
                         (BASE, BASE))
        self.assertEqual(row["working_commit_sha"], HEAD)
        self.assertTrue(row["parent_verified"] and row["public_fork_verified"])
        self.assertEqual(row["changed_files"],
                         ["plugins/omh/omh_state.py", "plugins/omh/tests/test_state.py"])


if __name__ == "__main__":
    unittest.main()
