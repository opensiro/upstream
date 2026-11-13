"""Static boundaries for human-directed PR-as-assent CLA, never a signer emulator."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "policies" / "standing-external-publication-p1.json"
REGISTRY = ROOT / "policies" / "cla-template-registry-v1.json"


class ChatFirstClaRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = json.loads(POLICY.read_text(encoding="utf-8"))
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_direct_pr_as_assent_is_explicit_human_directed(self):
        route = self.policy["interactive_pr_as_assent"]
        self.assertEqual(route["status"], "HUMAN_DIRECTED_IN_ACTIVE_CHAT_ONLY")
        self.assertEqual(route["mechanism"], "PR_SUBMISSION_CONSTITUTES_ASSENT")
        self.assertIn("explicit_current_chat_approval", route["human_instruction"])
        self.assertFalse(route["unattended"])
        self.assertFalse(route["provider_signature_required"])

    def test_never_claim_independent_signature_or_autonomous_acceptance(self):
        route = self.policy["interactive_pr_as_assent"]
        self.assertFalse(route["independent_identity_certification_claimed"])
        self.assertTrue(route["does_not_activate_template_executor"])
        self.assertTrue(route["does_not_authorize_standalone_cla_bot_comments"])

    def test_explicit_rights_source_and_original_target_readback(self):
        checks = set(self.policy["interactive_pr_as_assent"]["required_checks"])
        self.assertTrue({
            "live_first_party_cla_and_hash",
            "matching_authenticated_publishing_account",
            "explicit_individual_user_instruction_and_rights_representations",
            "first_party_pre_pr_native_checks_and_pr_template",
            "actual_original_repository_pr_readback",
        }.issubset(checks))

    def test_existing_automated_executor_remains_disabled(self):
        self.assertEqual(self.registry["default_decision"], "BLOCK")
        self.assertFalse(self.registry["legal_acceptance_executor_enabled"])
        revka = next(e for e in self.registry["templates"]
                     if e["id"] == "kumihoio-revka-cla-1")
        self.assertEqual(revka["status"], "PENDING_EXACT_TERMS_APPROVAL")

    def test_standing_mandate_does_not_transfer_personal_legal_rights(self):
        self.assertIn("fabricate_cla_dco_or_personal_attestations",
                      self.policy["reserved_actions"])
        self.assertIn("human_only_legal_attestations",
                      self.policy["required_checks"])


if __name__ == "__main__":
    unittest.main()
