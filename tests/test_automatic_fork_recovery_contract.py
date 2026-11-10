"""Offline invariants for the source-prepared automatic fork recovery route.

These tests deliberately cannot make GitHub API requests or approve writes.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def source(path):
    return (ROOT / path).read_text(encoding="utf-8")


class AutomaticForkRecoveryContractTests(unittest.TestCase):
    def test_original_rest_fork_transport_is_retained_but_not_deployed(self):
        client = source("scripts/create_fork.py")
        workflow = source(".github/workflows/fork-lifecycle.yml")
        self.assertIn('"/forks"', client)
        self.assertIn('"POST"', client)
        self.assertIn('"organization": DEST', client)
        self.assertIn('"default_branch_only": not all_branches', client)
        self.assertIn('name: Fork lifecycle (preview only)', workflow)
        self.assertIn('contents: read', workflow)
        self.assertNotIn('UPSTREAM_FORK_TOKEN', workflow)
        self.assertNotIn('--execute', workflow)
        self.assertNotIn('execute: true', workflow)
        self.assertNotIn('environment: fork-creation', workflow)
        self.assertNotIn('default_branch_only=', workflow)

    def test_recovery_contract_preserves_two_nonactivated_transports(self):
        contract = source("docs/AUTOMATIC_FORK_EXECUTOR_RECOVERY.md")
        for required in (
            "GitHub Actions / GitHub REST executor",
            "Native connected provider method",
            "not a prerequisite",
            "POST /repos/{source}/forks",
            "source-prepared",
            "default_branch_only=false",
            "BLOCKED_PROVIDER",
            "approval",
            "No fork execution is activated",
        ):
            with self.subTest(required=required):
                self.assertIn(required.lower(), contract.lower())

    def test_operator_and_legacy_docs_reference_the_recovery_contract(self):
        for doc in (
            "README.md",
            "docs/FORK_LIFECYCLE.md",
            "docs/OPENSIRO_CONTRIBUTIONS_FORK_ROUTE.md",
        ):
            with self.subTest(doc=doc):
                self.assertIn("AUTOMATIC_FORK_EXECUTOR_RECOVERY.md", source(doc))

    def test_operator_contract_does_not_claim_live_grant(self):
        text = source("docs/AUTOMATIC_FORK_EXECUTOR_RECOVERY.md")
        self.assertIn("unsigned `approved_by`", text)
        self.assertIn("trustworthy", text.lower())
        self.assertIn("stop at source preparation", text.lower())
        self.assertIn("external PR publication", text)
        self.assertIn("no unsafe auto-retry", text)


if __name__ == "__main__":
    unittest.main()
