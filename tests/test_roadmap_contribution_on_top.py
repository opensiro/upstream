"""Regression contract for parallel existing-work and independent on-top proposals."""
from pathlib import Path
import unittest

from test_capability_roadmap_contract import RECEIPT
from validate_capability_roadmap import validate

ROOT = Path(__file__).resolve().parents[1]


class ContributionOnTopTests(unittest.TestCase):
    def test_new_receipt_requires_both_tracks_and_bounded_scope(self):
        enhanced = RECEIPT.replace(
            "## Function ownership",
            "- Receipt contract: contribution-on-top\n\n"
            "## Parallel contribution-on-top review\n"
            "- Evaluation object: specific S3* user task\n"
            "- Existing-work overlap: native issue covers visibility only\n"
            "- Our on-top contribution: distinct audit of research results, NOT_EVIDENCED\n"
            "- Incremental benefit: NOT_EVIDENCED pending source review\n"
            "- Decision scope: this proposal only, not whole harness\n\n"
            "## Function ownership",
        )
        self.assertEqual(validate(enhanced), [])
        for field in ("Evaluation object", "Existing-work overlap", "Our on-top contribution",
                      "Incremental benefit", "Decision scope"):
            broken = enhanced.replace("- " + field + ": ", "- Removed-" + field + ": ")
            self.assertIn("missing field: " + field, validate(broken))
        missing_section = enhanced.replace("## Parallel contribution-on-top review",
                                            "## Omitted review")
        self.assertIn("missing section: Parallel contribution-on-top review",
                      validate(missing_section))

    def test_proposal_gate_accepts_hypothetical_go_without_executed_tests(self):
        proposal = RECEIPT.replace(
            "## Function ownership",
            "- Receipt contract: proposal-gate\n"
            "- Scenario basis: HYPOTHETICAL\n"
            "- Proposal-stage decision: GO\n"
            "- Proposed validation: compare exact same first-party task to native option with rights negatives\n"
            "- Validation state: NOT_RUN\n"
            "- Proposal falsifier: native tool already provides equal operator outcome\n\n"
            "## Parallel contribution-on-top review\n"
            "- Evaluation object: optional S3 current-control constructor\n"
            "- Existing-work overlap: deterministic native task router, no independent manager\n"
            "- Our on-top contribution: opt-in actor chooses lawful admit or hold\n"
            "- Incremental benefit: plausible real current commitments management, not measured\n"
            "- Decision scope: one hypothetical task, not the whole harness\n\n"
            "## Function ownership",
        )
        self.assertEqual(validate(proposal), [])
        for field in ("Scenario basis", "Proposal-stage decision", "Proposed validation",
                      "Validation state", "Proposal falsifier"):
            broken = proposal.replace("- " + field + ": ", "- Removed-" + field + ": ")
            self.assertIn("missing field: " + field, validate(broken))
        self.assertTrue(any("invalid Scenario basis" in issue for issue in validate(proposal.replace("HYPOTHETICAL", "FICTION"))))
        self.assertIn("invalid Proposal-stage decision", validate(
            proposal.replace("Proposal-stage decision: GO", "Proposal-stage decision: DONE")))
        self.assertTrue(any("invalid Validation state" in issue for issue in validate(
            proposal.replace("Validation state: NOT_RUN", "Validation state: VALIDATED"))))
        self.assertEqual(validate(RECEIPT), [])  # existing receipts are grandfathered

    def test_legacy_receipt_remains_structurally_valid(self):
        self.assertEqual(validate(RECEIPT), [])
        bad_marker = RECEIPT.replace("## Function ownership",
                                     "- Receipt contract: unknown\n\n## Function ownership")
        self.assertIn("unknown Receipt contract: unknown", validate(bad_marker))

    def test_protocol_and_templates_require_parallel_qualification(self):
        protocol = (ROOT / "PROTOCOL.md").read_text()
        guide = (ROOT / "docs/CAPABILITY_ROADMAP.md").read_text()
        human = (ROOT / "templates/FORK_CAPABILITY_ROADMAP_ISSUE.md").read_text()
        ai = (ROOT / "templates/ROADMAP_AI_CONSTRUCTOR_CONTRACT.md").read_text()
        selector = (ROOT / "scripts/roadmap_select.py").read_text()
        for body in (protocol, guide, human, ai):
            self.assertIn("on-top", body)
            self.assertIn("Issue", body)
            self.assertIn("NO_GO", body)
        self.assertIn("Mandatory parallel contribution-on-top gate", protocol)
        self.assertIn("A matching original Issue/PR is a starting point", protocol)
        self.assertIn("a matching Issue veto", human)
        self.assertIn("parallel_research_required", selector)
        self.assertIn("neither a grade nor overlap decides GO/NO_GO", selector)


if __name__ == "__main__":
    unittest.main()
