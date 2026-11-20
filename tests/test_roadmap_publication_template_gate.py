"""Regressions for fail-closed template/file checks before Roadmap-derived external PRs."""
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_roadmap_publication import check_publication_ready
from test_roadmap_case_consistency import PROPOSAL, HUMAN as OLD_HUMAN, AI as OLD_AI, VECTOR

STATES = dict(part.split("=", 1) for part in VECTOR.split(" · "))
PLACEHOLDER = re.compile(r"\[([^\]\n]+)\](?!\()")


def fill(template_name):
    s = (ROOT / "templates" / template_name).read_text(encoding="utf-8")
    s = s.replace("# [HARNESS]", "# Synthetic Harness")
    s = s.replace("opensiro-contributions/<fork>", "opensiro-contributions/synthetic")
    s = s.replace("<case-id>", "case-example")
    for fn, state in STATES.items():
        s = s.replace(fn + "=[accepted]", fn + "=" + state)
    if template_name.startswith("FORK_"):
        lines = s.splitlines()
        for i, line in enumerate(lines):
            for fn, state in STATES.items():
                if line.startswith("| **" + fn + " ·"):
                    parts = line.split("|")
                    parts[2] = " " + state + " "
                    lines[i] = "|".join(parts)
        s = "\n".join(lines) + "\n"
        s = re.sub(r"(?m)^> \*\*..S1=.*?\*\*$", "> **" + chr(96) + VECTOR + chr(96) + "**", s)
        s = re.sub(r"(?m)^\*\*Target transition:\*\*.*$",
                   "**Target transition:** S4=— -> S4=C", s)
        s = s.replace("proposal-stage [GO / NO_GO / BLOCKED]", "proposal-stage GO")
        s = s.replace("research [DECISION_READY / NEEDS_EVIDENCE / NO_USEFUL_CHANGE]",
                      "research NEEDS_EVIDENCE")
    else:
        s = s.replace("## 3. Minimal complete [selected function] first-party C construction",
                      "## 3. Minimal complete S4 first-party C construction")
        s = re.sub(r"(?m)^\*\*Target transition:\*\*.*$",
                   "**Target transition:** S4=— -> S4=C", s)
    s = re.sub(r"(?m)^\*\*Proposal-stage decision:\*\*.*$",
               "**Proposal-stage decision:** GO", s)
    s = re.sub(r"(?m)^\*\*Research disposition:\*\*.*$",
               "**Research disposition:** NEEDS_EVIDENCE", s)
    s = PLACEHOLDER.sub("source-grounded plan-only evidence", s)
    return s


class RoadmapPublicationGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.case = Path(self.tmp.name)
        (self.case / "roadmap.md").write_text(PROPOSAL, encoding="utf-8")
        (self.case / "README.md").write_text(
            "# Case\n[roadmap.md](roadmap.md) [issue.md](issue.md) "
            "[constructor-sufficiency.md](constructor-sufficiency.md)", encoding="utf-8")
        (self.case / "issue.md").write_text(fill("FORK_CAPABILITY_ROADMAP_ISSUE.md"), encoding="utf-8")
        (self.case / "constructor-sufficiency.md").write_text(
            fill("ROADMAP_AI_CONSTRUCTOR_CONTRACT.md"), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def edit(self, filename, needle, replacement):
        path = self.case / filename
        s = path.read_text(encoding="utf-8")
        self.assertIn(needle, s)
        path.write_text(s.replace(needle, replacement, 1), encoding="utf-8")

    def test_all_present_and_completed_template_pass(self):
        self.assertEqual(check_publication_ready(self.case), [])

    def test_old_receipt_pass_but_incomplete_human_ai_fail_external_pr(self):
        (self.case / "issue.md").write_text(OLD_HUMAN, encoding="utf-8")
        (self.case / "constructor-sufficiency.md").write_text(OLD_AI, encoding="utf-8")
        errors = check_publication_ready(self.case)
        self.assertTrue(any("8 numbered sections" in x for x in errors))
        self.assertTrue(any("6 numbered sections" in x for x in errors))

    def test_versioned_human_appendix_fails_on_case_write(self):
        with (self.case / "issue.md").open("a", encoding="utf-8") as f:
            f.write("\n## v0.18.1 Human acceptance refinement — internal log\n\n")
        errors = check_publication_ready(self.case)
        self.assertTrue(any("unexpected top-level section" in e for e in errors), errors)

    def test_versioned_ai_appendix_fails_on_case_write(self):
        with (self.case / "constructor-sufficiency.md").open("a", encoding="utf-8") as f:
            f.write("\n## v0.18.1 AI constructor refinement\n\n")
        errors = check_publication_ready(self.case)
        self.assertTrue(any("unexpected top-level section" in e for e in errors), errors)

    def test_nested_source_evidence_remains_allowed(self):
        with (self.case / "constructor-sufficiency.md").open("a", encoding="utf-8") as f:
            f.write("\n### Specific source evidence\n\nAdded native details inside section six.\n")
        self.assertEqual(check_publication_ready(self.case), [])

    def test_missing_file_fails(self):
        (self.case / "README.md").unlink()
        self.assertIn("missing required roadmap case file: README.md",
                      check_publication_ready(self.case))

    def test_human_heading_mismatch_fails(self):
        self.edit("issue.md", "## 1. Why Opensiro and central accepted VSM assessment",
                  "## 1. Summary instead")
        self.assertTrue(any("section 1 template mismatch" in x
                            for x in check_publication_ready(self.case)))

    def test_missing_human_required_field_fails(self):
        self.edit("issue.md", "**One-sentence proposal:**", "**Short proposal:**")
        self.assertTrue(any("missing or empty template field: One-sentence proposal" in x
                            for x in check_publication_ready(self.case)))

    def test_missing_ai_section_fails(self):
        self.edit("constructor-sufficiency.md",
                  "## 3. Minimal complete S4 first-party C construction",
                  "## 3. Generic adaptation")
        self.assertTrue(any("section 3 template mismatch" in x
                            for x in check_publication_ready(self.case)))

    def test_unfilled_placeholder_fails(self):
        self.edit("issue.md", "**One-sentence proposal:** source-grounded plan-only evidence",
                  "**One-sentence proposal:** [selected feature]")
        self.assertTrue(any("unfilled template placeholder" in x
                            for x in check_publication_ready(self.case)))

    def test_historical_vector_mismatch_fails(self):
        self.edit("issue.md", VECTOR, "S1=C · S2=A · S3=A(P) · S3*=A · S4=— · S5=P")
        self.assertTrue(any("historical" in x for x in check_publication_ready(self.case)))


if __name__ == "__main__":
    unittest.main()
