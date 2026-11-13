"""Boundary tests for the read-only CLA template preflight."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("cla_template_gate", ROOT / "scripts" / "cla_template_gate.py")
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class ClaTemplateGateTests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads((ROOT / "policies" / "cla-template-registry-v1.json").read_text())
        self.template = "kumihoio-revka-cla-1"
        self.arguments = {
            "template_id": self.template,
            "repository": "KumihoIO/Revka",
            "actor": "xLagerFeuer",
            "terms_sha256": "a" * 64,
        }

    def check_reason(self, expected, data=None, **overrides):
        args = dict(self.arguments, **overrides)
        result = gate.assess(data if data is not None else self.registry, **args)
        self.assertEqual(result["state"], "BLOCKED")
        self.assertEqual(result["reason"], expected)

    def test_current_registry_fails_closed(self):
        self.check_reason("EXACT_TERMS_NOT_APPROVED")

    def test_observed_revka_source_text_is_not_legal_approval(self):
        entry = self.registry["templates"][0]
        self.assertEqual(entry["observed_source_ref"], "a1acd826502e12a6c2f3d147e488a7d2982c480b")
        self.assertEqual(entry["observed_terms_sha256"], "c6f2f0061d44875d6043530ba2ce0b93a77327dca5672a92787f84afb20de623")
        self.assertEqual(entry["status"], "PENDING_EXACT_TERMS_APPROVAL")
        self.assertIsNone(entry["terms_sha256"])
        self.arguments["terms_sha256"] = entry["observed_terms_sha256"]
        self.check_reason("EXACT_TERMS_NOT_APPROVED")
        entry["status"] = "ENROLLED_EXACT_TERMS"
        self.check_reason("MISSING_EXACT_ENROLMENT_FIELD")

    def test_unknown_template_blocks(self):
        self.check_reason("TEMPLATE_MISSING_OR_AMBIGUOUS", template_id="unknown")

    def test_repository_mismatch_blocks(self):
        self.check_reason("REPOSITORY_MISMATCH", repository="other/repo")

    def test_actor_mismatch_blocks(self):
        self.check_reason("SIGNER_ACTOR_MISMATCH", actor="automated-bot")

    def test_missing_legal_enrolment_blocks(self):
        entry = self.registry["templates"][0]
        entry["status"] = "ENROLLED_EXACT_TERMS"
        self.check_reason("MISSING_EXACT_ENROLMENT_FIELD")

    def test_digest_drift_blocks(self):
        entry = self.registry["templates"][0]
        entry.update(status="ENROLLED_EXACT_TERMS", terms_sha256="b" * 64,
                     signer_capacity="individual", exact_action="AGREED",
                     signer_approval_ref="https://github.com/opensiro/vsm-oss-organization/issues/323#issuecomment-123",
                     valid_until="2027-11-13")
        self.check_reason("TERMS_DIGEST_MISMATCH")

    def test_fake_fully_populated_template_does_not_authorize_action(self):
        entry = self.registry["templates"][0]
        entry.update(status="ENROLLED_EXACT_TERMS", terms_sha256="a" * 64,
                     signer_capacity="individual", exact_action="AGREED",
                     signer_approval_ref="https://example.invalid/attestation",
                     valid_until="2027-11-13")
        self.registry["legal_acceptance_executor_enabled"] = True
        self.check_reason("INDEPENDENT_LIVE_SIGNATORY_AND_SOURCE_VERIFICATION_REQUIRED")

    def test_active_flag_without_execution_blocks(self):
        entry = self.registry["templates"][0]
        entry.update(status="ENROLLED_EXACT_TERMS", terms_sha256="a" * 64,
                     signer_capacity="individual", exact_action="AGREED",
                     signer_approval_ref="https://example.invalid/attestation",
                     valid_until="2027-11-13")
        self.check_reason("EXECUTOR_NOT_ACTIVATED")

    def test_invalid_root_contract_blocks(self):
        self.registry["default_decision"] = "ALLOW"
        self.check_reason("INVALID_REGISTRY_CONTRACT")


if __name__ == "__main__":
    unittest.main()
