"""Directory-level Human / AI / canonical receipt consistency regression.

Synthetic fixture uses a realistic six-function vector but does NOT assert facts
about any original repository, Paperclip, native tests or implementation.
"""
from pathlib import Path
import tempfile
import unittest
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_capability_roadmap import validate_case_dir, validate, parse_vector
from test_capability_roadmap_contract import RECEIPT

VECTOR = "S1=A · S2=A · S3=A(P) · S3*=A · S4=— · S5=P"
PROPOSAL = RECEIPT.replace("## Function ownership",
    "- Receipt contract: proposal-gate\n"
    "- Repository-wide source map: pinned example/harness source, docs, build and tests\n"
    "- Priority rationale: independently selected S4 after six-function source screening\n"
    "- Accepted VSM vector: " + VECTOR + "\n"
    "- S1 disposition: A current operations, no targeted construction\n"
    "- S2 disposition: A coordination, no targeted construction\n"
    "- S3 disposition: A(P) whole-company manager, preserve rights\n"
    "- S3* disposition: A complementary audit, preserve independence\n"
    "- S4 disposition: candidate C; no current future adaptation constructor\n"
    "- S5 disposition: P parent ultimate authority; no local C required\n"
    "- Target transition: S4=— -> S4=C\n"
    "- P1 dependencies: verify supported native adaptation surface\n"
    "- P2 optional: NONE\n"
    "- Proposed C construction: developer composes future adaptation actor with lawful feedback\n"
    "- C sufficiency falsifier: source shows existing closed first-party adaptation path\n"
    "- Scenario basis: HYPOTHETICAL\n"
    "- Proposal-stage decision: GO\n"
    "- Research disposition: NEEDS_EVIDENCE\n"
    "- Proposed validation: native future-change scenario with protected authority\n"
    "- Validation state: NOT_RUN\n"
    "- Proposal falsifier: native current implementation already handles same decision\n\n"
    "## Parallel contribution-on-top review\n"
    "- Evaluation object: S4 future adaptation constructor\n"
    "- Existing-work overlap: current native adapter and policy wiring partial\n"
    "- Our on-top contribution: first-party optional S4 decision/return path\n"
    "- Incremental benefit: hypothetical operator continuity, not measured\n"
    "- Decision scope: one S4 construction proposal\n\n"
    "## Function ownership")

HUMAN = """# Synthetic — Human roadmap
**Canonical decision receipt:** [roadmap.md](roadmap.md)
**Technical companion:** [constructor-sufficiency.md](constructor-sufficiency.md)
**Target transition:** S4=— -> S4=C
**Proposal-stage decision:** GO
**Research disposition:** NEEDS_EVIDENCE
| Function / role | Historical Index state | Current source | Priority |
| --- | --- | --- | --- |
| **S1 · Operations** | A | source | NO_TARGET |
| **S2 · Coordination** | A | source | NO_TARGET |
| **S3 · Current management** | A(P) | source | DEFER |
| **S3* · Independent review** | A | source | NO_TARGET |
| **S4 · Future adaptation** | — | source | P0 |
| **S5 · Identity/policy** | P | parent authority | NO_TARGET |
"""
AI = """# Synthetic technical constructor contract
**Canonical decision receipt:** [roadmap.md](roadmap.md)
**Human:** [issue.md](issue.md)
**Target transition:** S4=— -> S4=C
**Proposal-stage decision:** GO
**Research disposition:** NEEDS_EVIDENCE
No fixed port count, native tests NOT_RUN.
"""


class CanonicalRoadmapCaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        for name, body in (("roadmap.md", PROPOSAL),
                           ("issue.md", HUMAN),
                           ("constructor-sufficiency.md", AI)):
            (self.dir / name).write_text(body, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def set_file(self, name, a, b):
        p = self.dir / name
        s=p.read_text(encoding="utf-8")
        assert a in s
        p.write_text(s.replace(a,b,1),encoding="utf-8")

    def test_complete_unexecuted_go_needs_evidence_is_structurally_valid(self):
        self.assertEqual(validate(PROPOSAL), [])
        self.assertEqual(validate_case_dir(self.dir), [])
        self.assertEqual(parse_vector(VECTOR)["S3"], "A(P)")

    def test_human_verdict_mismatch_is_rejected_not_silently_corrected(self):
        self.set_file("issue.md", "**Proposal-stage decision:** GO",
                      "**Proposal-stage decision:** NO_GO")
        self.assertIn("issue.md Proposal-stage decision disagrees with roadmap.md",
                      validate_case_dir(self.dir))

    def test_ai_target_and_research_status_mismatch_are_rejected(self):
        self.set_file("constructor-sufficiency.md", "S4=— -> S4=C", "S3=— -> S3=C")
        self.set_file("constructor-sufficiency.md", "NEEDS_EVIDENCE", "DECISION_READY")
        errors=validate_case_dir(self.dir)
        self.assertIn("constructor-sufficiency.md Target transition disagrees with roadmap.md",errors)
        self.assertIn("constructor-sufficiency.md Research disposition disagrees with roadmap.md",errors)

    def test_historical_vector_disagreement_and_ai_duplicate_are_rejected(self):
        self.set_file("issue.md", "| **S3 · Current management** | A(P) |",
                      "| **S3 · Current management** | C |")
        self.set_file("constructor-sufficiency.md", "No fixed port count",
                      "| **S1 · Operations** | A | fake second table |\nNo fixed port count")
        errors=validate_case_dir(self.dir)
        self.assertIn("issue.md historical state differs from roadmap.md: S3", errors)
        self.assertIn("AI contract must reference, not duplicate, Human six-function table", errors)

    def test_missing_receipt_or_links_fails_closed(self):
        self.set_file("issue.md", "[roadmap.md](roadmap.md)", "missing receipt")
        self.assertIn("issue.md must link canonical roadmap.md", validate_case_dir(self.dir))
        (self.dir / "roadmap.md").unlink()
        self.assertIn("missing case file: roadmap.md", validate_case_dir(self.dir))

    def test_legacy_receipt_not_forced_to_migrate_to_new_case_fields(self):
        (self.dir / "roadmap.md").write_text(RECEIPT,encoding="utf-8")
        self.assertEqual(validate_case_dir(self.dir), [])


if __name__ == "__main__":
    unittest.main()
