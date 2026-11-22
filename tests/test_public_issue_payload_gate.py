"""Exact public payload regression, including the earlier free-form OpenCode failure."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_public_issue_payload import (check_payload, render_fork, accepted_version,
                                           accepted_profile_skills_versions)
from test_roadmap_publication_template_gate import fill, PROPOSAL

REF = "8a264aa1c2da59e5c3d17fbbc893ddf80a2850cb"


class PublicIssuePayloadTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.case = Path(self.temp.name) / ".opensiro" / "issues" / "synthetic"
        self.case.mkdir(parents=True)
        self.repo = "opensiro-contributions/synthetic"
        (self.case.parent.parent / "state.json").write_text(
            json.dumps({"working_fork": self.repo, "attention": "ACTIVE", "owner_control": "ALLOW"}),
            encoding="utf-8")
        (self.case / "README.md").write_text(
            "# Case\n[roadmap.md](roadmap.md) [issue.md](issue.md) "
            "[constructor-sufficiency.md](constructor-sufficiency.md)", encoding="utf-8")
        (self.case / "roadmap.md").write_text(PROPOSAL, encoding="utf-8")
        human = fill("FORK_CAPABILITY_ROADMAP_ISSUE.md")
        human += ("\n**Public fork Issue title (draft only):** Example — optional S4 composition\n"
                  "\n**Public fork Issue body (draft only):** DRAFT — NOT PUBLISHED\n")
        (self.case / "issue.md").write_text(human, encoding="utf-8")
        (self.case / "constructor-sufficiency.md").write_text(
            fill("ROADMAP_AI_CONSTRUCTOR_CONTRACT.md"), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def check(self, title, body, kind="fork"):
        return check_payload(kind, self.case, self.repo, REF, title, body)

    def test_canonical_template_render_passes(self):
        title, body = render_fork(self.case, self.repo, REF)
        self.assertEqual(self.check(title, body), [])
        self.assertEqual(len(__import__("re").findall(r"(?m)^## ", body)), 8)
        self.assertIn("/blob/" + REF + "/.opensiro/issues/synthetic/roadmap.md", body)
        self.assertNotIn("DRAFT — NOT PUBLISHED", body)

    def test_previous_freeform_opencode_public_text_fails(self):
        title, _ = render_fork(self.case, self.repo, REF)
        body = ("# " + title + "\n\n## Purpose\n## Existing OpenCode behavior\n"
                "## Proposed minimal construction\n## OpenSiro assessment context\n"
                "## Research record and status\n")
        errors = self.check(title, body)
        self.assertTrue(any("differs from deterministic" in e for e in errors), errors)
        self.assertTrue(any("template requires 8 numbered sections" in e for e in errors), errors)

    def test_body_change_after_approval_fails(self):
        title, body = render_fork(self.case, self.repo, REF)
        self.assertTrue(any("differs from deterministic" in e for e in
                            self.check(title, body.replace("source-grounded plan-only evidence",
                                                           "unreviewed new claim", 1))))

    def test_missing_six_function_row_fails(self):
        title, body = render_fork(self.case, self.repo, REF)
        body = "\n".join(x for x in body.splitlines() if not x.startswith("| **S3* ·")) + "\n"
        self.assertTrue(any("missing accepted six-function row" in e for e in self.check(title, body)))

    def test_draft_status_fails(self):
        title, body = render_fork(self.case, self.repo, REF)
        body = body.replace("PUBLIC FORK ROADMAP PROPOSAL", "DRAFT — NOT PUBLISHED")
        self.assertTrue(any("draft status in public body" in e for e in self.check(title, body)))

    def test_wrong_fork_fails(self):
        with self.assertRaisesRegex(ValueError, "identity"):
            render_fork(self.case, "opensiro-contributions/different", REF)

    def test_original_requires_separate_template(self):
        title, body = render_fork(self.case, self.repo, REF)
        errors = self.check(title, body, "original")
        self.assertTrue(any("external template seven section mismatch" in e for e in errors), errors)

    def test_external_methodology_legacy_alias_is_accepted(self):
        receipt = "- Accepted Skills methodology version: 0.3.1\n"
        self.assertEqual(accepted_version(receipt, "Accepted Methodology version",
                                          "Accepted Skills methodology version"), "0.3.1")
        self.assertEqual(accepted_version(
            "- Assessment procedure version: 0.3.1\n",
            "Accepted Methodology version", "Assessment procedure version"), "0.3.1")

    def test_external_methodology_conflicting_versions_fail_closed(self):
        receipt = ("- Accepted Methodology version: 0.3.1\n"
                   "- Accepted Skills methodology version: 0.4.0\n")
        self.assertIsNone(accepted_version(receipt, "Accepted Methodology version",
                                            "Accepted Skills methodology version"))
        self.assertIsNone(accepted_version("", "Accepted Methodology version",
                                            "Accepted Skills methodology version"))

    def test_external_combined_profile_skills_receipt_is_supported(self):
        receipt = "- Profile / Skills procedure: 0.2.4 / 0.3.8\n"
        self.assertEqual(accepted_profile_skills_versions(receipt), ("0.2.4", "0.3.8"))

    def test_external_combined_and_separate_consistent_receipts(self):
        receipt = ("- Profile / Skills procedure: 0.2.4 / 0.3.8\n"
                   "- Profile version: 0.2.4\n"
                   "- Assessment procedure version: 0.3.8\n")
        self.assertEqual(accepted_profile_skills_versions(receipt), ("0.2.4", "0.3.8"))

    def test_external_combined_pin_conflict_fails_closed(self):
        receipt = ("- Profile / Skills procedure: 0.2.4 / 0.3.8\n"
                   "- Accepted Profile version: 0.2.5\n")
        self.assertEqual(accepted_profile_skills_versions(receipt), (None, None))
        malformed = "- Profile / Skills procedure: maybe / unknown\n"
        self.assertEqual(accepted_profile_skills_versions(malformed), (None, None))
        incomplete = "- Profile version: 0.2.4\n"
        self.assertEqual(accepted_profile_skills_versions(incomplete), (None, None))

    def test_mismatch_to_current_source_head_fails(self):
        title, body = render_fork(self.case, self.repo, REF)
        errors = check_payload("fork", self.case, self.repo, REF, title, body,
                               "ee5fe34e136488a1839ac73bcca8321c51a31b75")
        self.assertTrue(any("observed current original HEAD" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
