"""Plan-only receipt checks: structure, not live GitHub or VSM semantics."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from validate_capability_roadmap import validate  # noqa: E402

PILOT=(ROOT/"docs/examples/browser-harness-roadmap-20261117.md").read_text(encoding="utf-8")


class CapabilityRoadmapReceiptTests(unittest.TestCase):
    def test_source_pinned_pilot_passes(self):
        self.assertEqual(validate(PILOT), [])

    def test_missing_original_pin_fails(self):
        import re
        broken=re.sub(r"(?m)^- Original HEAD: .+$","- Original HEAD: missing",PILOT)
        self.assertIn("invalid format: Original HEAD",validate(broken))

    def test_unpinned_index_link_fails(self):
        import re
        broken=re.sub(r"(?m)^- Accepted Index assessment: .+$",
            "- Accepted Index assessment: https://github.com/opensiro/vsm-harness-index/blob/main/assessments/br/browser-harness.md",PILOT)
        self.assertIn("Index assessment must use a frozen commit, not main",validate(broken))

    def test_no_external_write_authorization_from_plan(self):
        self.assertIn("external issue must be explicitly DRAFT — NOT PUBLISHED",
            validate(PILOT.replace("- External issue: DRAFT — NOT PUBLISHED","- External issue: PUBLISHED")))

    def test_no_unmeasured_cost_shortcut(self):
        self.assertIn("cost status must remain NOT_MEASURED until independently measured",
            validate(PILOT.replace("- Cost status: NOT_MEASURED","- Cost status: VERIFIED_CHEAPER")))

    def test_grade_claim_cannot_be_structurally_certified(self):
        self.assertIn("S3=C is only a speculative target",PILOT)
        self.assertIn("not a general VSM solution",PILOT)
        self.assertIn("does not establish runtime s5",PILOT.lower())
        self.assertIn("NOT BEEN CREATED",PILOT)

    def test_guide_preserves_noncanonical_scope(self):
        s=(ROOT/"docs/FORK_METADATA.md").read_text()
        self.assertIn("Plan-only capability roadmaps are not new fork records",s)
        self.assertIn("not* itself a qualifying improvement",s)
        self.assertIn("schema-v2",s)
        h=(ROOT/"docs/UPGRADE_PR_REVIEW.md").read_text()
        self.assertIn("Architecture-roadmap dependency handoff",h)
        self.assertIn("DRAFT — NOT PUBLISHED",h)

if __name__=="__main__":
    unittest.main()
