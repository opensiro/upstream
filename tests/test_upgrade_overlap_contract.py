"""Document contract: Upgrade cannot infer VSM coverage from competing PR presence."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class UpgradeOverlapContractTests(unittest.TestCase):
    def test_protocol_requires_function_ownership_and_native_overlap_receipt(self):
        protocol = (ROOT / "PROTOCOL.md").read_text(encoding="utf-8")
        section = protocol.split("### Existing-work functional overlap and VSM-ownership gate", 1)[1].split("\n### ", 1)[0]
        for required in (
            "historical baseline", "Decision owner and closure",
            "baseline", "competing PR", "remaining gap", "PARTIAL_OVERLAP",
            "OVERLAP_UNVERIFIED", "EVIDENCE_INSUFFICIENT",
            "within the same selected harness",
        ):
            with self.subTest(required=required):
                self.assertIn(required, section)

    def test_review_and_agents_route_to_receipt(self):
        for name in ("AGENTS.md", "docs/UPGRADE_PR_REVIEW.md"):
            with self.subTest(file=name):
                text = (ROOT / name).read_text(encoding="utf-8")
                self.assertIn("existing-work-functional-overlap-and-vsm-ownership-gate", text)
                self.assertIn("consent", text.lower())


if __name__ == "__main__":
    unittest.main()
