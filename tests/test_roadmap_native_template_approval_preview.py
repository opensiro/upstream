"""Normative user-visible native template preview before outward consent."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class NativeTemplateApprovalPreviewContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = (ROOT / "PROTOCOL.md").read_text()
        cls.guide = (ROOT / "docs/CAPABILITY_ROADMAP.md").read_text()
        cls.external = (ROOT / "templates/EXTERNAL_ARCHITECTURE_ISSUE.md").read_text()

    def test_preapproval_includes_first_party_template_link_and_fields(self):
        self.assertIn("Mandatory original-native template preview before asking", self.protocol)
        self.assertIn("actual repository-native template at its verified source commit", self.protocol)
        self.assertIn("required and optional text fields", self.protocol)
        self.assertIn("required checkboxes/human signoffs", self.protocol)
        self.assertIn("field-by-field comparison", self.protocol)
        self.assertIn("native issue-form/template permalink", self.guide)
        self.assertIn("field-by-field match/deviation summary", self.external)

    def test_no_link_only_approvals_or_fake_human_signoff(self):
        self.assertIn("not substitute for", self.protocol)
        self.assertIn("personally read the proposal", self.protocol)
        self.assertIn("do not tick a human-read checkbox", self.guide)
        self.assertIn("full outbound body", self.guide)
        self.assertIn("never replace showing full text with the link", self.external)

    def test_final_handoff_includes_publication_disposition_even_when_blocked(self):
        for doc in (self.protocol, self.guide):
            for phrase in ("Mandatory owner-facing publication disposition in every Roadmap final handoff", "exact destination URL", "complete outbound body/comment", "PRELIMINARY DRAFT — NOT APPROVAL READY", "do not silently omit this section", "Do not ask for publication approval until"):
                self.assertIn(phrase, doc)

    def test_change_requires_fresh_approval_and_live_recheck(self):
        self.assertIn("Approval-preview change control", self.protocol)
        self.assertIn("renewed exact current-conversation approval", self.protocol)
        self.assertIn("PUBLI" + "CATION_BLOCKED_NATIVE_TEMPLATE_UNVERIFIED", self.protocol)
        self.assertIn("category/rules", self.protocol)
        self.assertIn("re-present everything for new approval", self.guide)
        self.assertIn("separate exact", self.protocol)
        self.assertIn("no native Issue template", self.protocol)
        self.assertIn("blank Issue is permitted", self.protocol)
        self.assertIn("first-party absence", self.guide)
        self.assertIn("blank-Issue permission", self.external)


if __name__ == "__main__":
    unittest.main()
