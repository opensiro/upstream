"""Source-neutral plan-only receipt tests; real case artifacts live in the fork."""
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_capability_roadmap import validate  # noqa: E402


RECEIPT = """# Synthetic source-neutral plan-only receipt

## Identity and pins
- Original repository: example/harness
- Original HEAD: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
- Observed at: 2026-11-17
- Accepted Index assessment: https://github.com/opensiro/vsm-harness-index/blob/bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb/assessments/ex/example.md
- Accepted assessment blob SHA: cccccccccccccccccccccccccccccccccccccccc
- Accepted review ref: dddddddddddddddddddddddddddddddddddddddd
- Accepted reviewed at: 2026-11-16
- System in focus: one synthetic company in an imaginary harness

## Rights and authority
No publication authority is assumed.

## Existing work / overlap
Source overlap is hypothetical.

## Function ownership
A planned capability is not a classification.

## Capability priority
Native alternative must be considered.

## Implementation options
No code changes are requested.

## Specification and domain alternatives
Profile and Skills own semantics and method.

## Cost experiment
- Cost status: NOT_MEASURED

## Delivery and publication
- Result: PLAN_ONLY
- External issue: DRAFT — NOT PUBLISHED
"""


class CapabilityRoadmapReceiptTests(unittest.TestCase):
    def test_source_pinned_fixture_passes(self):
        self.assertEqual(validate(RECEIPT), [])

    def test_missing_original_pin_fails(self):
        broken = re.sub(r"(?m)^- Original HEAD: .+$", "- Original HEAD: missing", RECEIPT)
        self.assertIn("invalid format: Original HEAD", validate(broken))

    def test_unpinned_index_link_fails(self):
        broken = re.sub(
            r"(?m)^- Accepted Index assessment: .+$",
            "- Accepted Index assessment: https://github.com/opensiro/vsm-harness-index/blob/main/assessments/ex/example.md",
            RECEIPT,
        )
        self.assertIn("Index assessment must use a frozen commit, not main", validate(broken))

    def test_no_automatic_external_issue_from_plan(self):
        broken = RECEIPT.replace("- External issue: DRAFT — NOT PUBLISHED", "- External issue: PUBLISHED")
        self.assertIn("external issue must be explicitly DRAFT — NOT PUBLISHED", validate(broken))

    def test_unmeasured_cost_not_assumed(self):
        broken = RECEIPT.replace("- Cost status: NOT_MEASURED", "- Cost status: VERIFIED_CHEAPER")
        self.assertIn("cost status must remain NOT_MEASURED until independently measured", validate(broken))

    def test_validator_is_structural_not_grade_certification(self):
        self.assertEqual(validate(RECEIPT + "\nA putative S4=C remains unverified.\n"), [])
        guide = (ROOT / "docs/CAPABILITY_ROADMAP.md").read_text()
        self.assertIn("not a changed Index grade", guide)

    def test_fork_case_and_contribution_are_distinct(self):
        metadata = (ROOT / "docs/FORK_METADATA.md").read_text()
        self.assertIn("Plan-only capability roadmaps are not new contribution records", metadata)
        self.assertIn(".opensiro/issues/<stable-case-id>/", metadata)
        self.assertIn("not* itself a qualifying improvement", metadata)
        self.assertIn("schema-v2", metadata)
        self.assertIn("do not claim copied comments, numbering, reactions or ownership", metadata)
        protocol = (ROOT / "PROTOCOL.md").read_text()
        self.assertIn("Fork GitHub Issue", protocol)
        self.assertIn("not a promised GitHub native cross-owner Issue transfer", protocol)
        self.assertIn("obtain **new, separate, exact current-conversation owner approval**", protocol)
        self.assertIn("Do **not** automatically close the internal Issue", protocol)

    def test_only_source_neutral_examples_in_upstream(self):
        for name in (
            "browser-harness-roadmap-20261117.md",
            "paperclip-roadmap-20261117.md",
            "paperclip-s4-constructor-acceptance-20261117.md",
        ):
            self.assertFalse((ROOT / "docs/examples" / name).exists())
        guide = (ROOT / "docs/CAPABILITY_ROADMAP.md").read_text()
        self.assertIn("opensiro-contributions/paperclip/blob/opensiro/meta/.opensiro/issues/", guide)
        self.assertIn("opensiro-contributions/browser-harness/blob/opensiro/meta/.opensiro/issues/", guide)
        self.assertNotIn("docs/examples/", guide)

    def test_roadmap_and_issue_are_not_publication_approval(self):
        guide = (ROOT / "docs/CAPABILITY_ROADMAP.md").read_text()
        self.assertIn("separate exact approval", guide)
        self.assertIn("public fork GitHub Issue", guide)
        self.assertIn("PLAN_ONLY", guide)


if __name__ == "__main__":
    unittest.main()
