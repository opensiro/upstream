"""Deterministic negative/positive cryptographic *precheck* cases, no CLA POST."""
import base64
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "cla_chat_attestation", ROOT / "scripts" / "cla_chat_attestation.py")
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


class PacketAndFailClosedTests(unittest.TestCase):
    def setUp(self):
        self.packet = dict(
            schema_version=1, template_id="kumihoio-revka-cla-1",
            repository="KumihoIO/Revka", counterparty="Kumiho Inc.",
            terms_sha256="a" * 64, fork_repository="opensiro-contributions/Revka",
            fork_branch="opensiro/fix-validator-deep-dag",
            fork_head_sha="b" * 40, target_base_sha="c" * 40,
            signer_actor="xLagerFeuer", signer_capacity="individual",
            exact_action="PR_SUBMISSION_CONSTITUTES_ASSENT",
        )

    def test_exact_packet_digest_is_stable(self):
        self.assertEqual(gate.packet_digest(self.packet),
                         gate.packet_digest(dict(reversed(list(self.packet.items())))))

    def test_each_scoped_field_is_bound(self):
        expected = gate.packet_digest(self.packet)
        for field in ("repository", "counterparty", "terms_sha256",
                      "fork_repository", "fork_branch", "fork_head_sha",
                      "target_base_sha", "signer_actor", "signer_capacity",
                      "exact_action", "template_id"):
            changed = dict(self.packet)
            changed[field] = ("corporate" if field == "signer_capacity"
                              else "EXPLICIT_BOT_COMMENT_ASSENT" if field == "exact_action"
                              else "d" * 64 if field == "terms_sha256"
                              else "d" * 40 if field.endswith("_sha")
                              else "changed-" + self.packet[field])
            if field == "fork_branch":
                changed[field] = "opensiro/changed"
            if field in {"repository", "fork_repository"}:
                changed[field] = "other/changed"
            try:
                new = gate.packet_digest(changed)
                self.assertNotEqual(new, expected, field)
            except ValueError:
                pass

    def test_unknown_fields_and_bad_sha_rejected(self):
        data = dict(self.packet, permit=True)
        with self.assertRaisesRegex(ValueError, "INVALID_PACKET_FIELDS"):
            gate.packet_digest(data)
        data = dict(self.packet, fork_head_sha="unverified")
        with self.assertRaisesRegex(ValueError, "INVALID_SOURCE_SHA"):
            gate.packet_digest(data)

    def test_missing_provider_receipt_fails(self):
        out = gate.verify_receipt(self.packet, {}, issuer_keys={},
                                  signer_subjects={}, consumed_nonces=set(),
                                  now=datetime.now(timezone.utc))
        self.assertEqual(out["status"], "BLOCKED")
        self.assertEqual(out["reason"], "MISSING_OR_MALFORMED_PROVIDER_RECEIPT")


@unittest.skipUnless(HAS_CRYPTO, "cryptography Ed25519 verifier not installed")
class SignedReceiptTests(PacketAndFailClosedTests):
    def setUp(self):
        super().setUp()
        self.key = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
        self.public = self.key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.issuer = "test-provider-only"
        self.subject = "test-subject-only"
        self.clock = datetime(2026, 11, 13, 17, 36, tzinfo=timezone.utc)
        self.receipt = {
            "schema_version": 1,
            "issuer": self.issuer,
            "subject": self.subject,
            "decision": "APPROVE",
            "packet_sha256": gate.packet_digest(self.packet),
            "rights_confirmed": True,
            "issued_at": "2026-11-13T17:35:00Z",
            "expires_at": "2026-11-13T17:40:00Z",
            "nonce": "test-nonce-20261113",
        }
        self.sign()

    def sign(self):
        payload = gate._canonical(self.receipt)
        signature = self.key.sign(b"opensiro-cla-chat-receipt-v1\\0".replace(b"\\0", b"\\x00") + payload)
        self.receipt["signature_b64"] = base64.b64encode(signature).decode()

    def verify(self, **kwargs):
        args = {
            "issuer_keys": {self.issuer: self.public},
            "signer_subjects": {"xLagerFeuer": {self.subject}},
            "consumed_nonces": set(),
            "now": self.clock,
        }
        args.update(kwargs)
        return gate.verify_receipt(self.packet, self.receipt, **args)

    def test_signature_matches_but_never_authorizes_legal_post(self):
        out = self.verify()
        self.assertEqual(out["status"], "VERIFIED_RECEIPT_NON_EXECUTABLE")
        self.assertNotIn("ALLOW", out["status"])
        self.assertEqual(out["packet_sha256"], gate.packet_digest(self.packet))

    def test_no_trusted_issuer_blocks(self):
        self.assertEqual(self.verify(issuer_keys={})["reason"],
                         "NO_INDEPENDENT_TRUSTED_ISSUER_KEY")

    def test_spoofed_identity_blocks(self):
        self.assertEqual(self.verify(signer_subjects={"xLagerFeuer": {"other-person"}})["reason"],
                         "NO_INDEPENDENT_SIGNER_IDENTITY_BINDING")

    def test_tampered_head_or_terms_blocks(self):
        for key, value in (("fork_head_sha", "e" * 40),
                           ("terms_sha256", "e" * 64),
                           ("signer_actor", "another-actor")):
            with self.subTest(key=key):
                old = self.packet[key]
                self.packet[key] = value
                self.assertEqual(self.verify()["reason"], "EXACT_PACKET_MISMATCH")
                self.packet[key] = old

    def test_reply_with_no_rights_statement_blocks(self):
        self.receipt["rights_confirmed"] = False
        self.assertEqual(self.verify()["reason"], "CONTRIBUTOR_RIGHTS_NOT_ATTESTED")

    def test_changed_decision_blocks(self):
        self.receipt["decision"] = "CONTINUE"
        self.assertEqual(self.verify()["reason"], "NOT_AN_EXACT_APPROVAL")

    def test_malformed_signature_blocks(self):
        self.receipt["signature_b64"] = base64.b64encode(b"garbage").decode()
        self.assertEqual(self.verify()["reason"], "INVALID_SIGNATURE")

    def test_tampered_signed_claim_blocks(self):
        self.receipt["nonce"] = "different-valid-nonce"
        self.assertEqual(self.verify()["reason"], "INVALID_PROVIDER_SIGNATURE")

    def test_expired_signature_blocks(self):
        self.assertEqual(self.verify(now=datetime(2026, 11, 13, 17, 41, tzinfo=timezone.utc))["reason"],
                         "EXPIRED_OR_OUT_OF_WINDOW_RECEIPT")

    def test_future_approval_blocks(self):
        self.assertEqual(self.verify(now=datetime(2026, 11, 13, 17, 30, tzinfo=timezone.utc))["reason"],
                         "EXPIRED_OR_OUT_OF_WINDOW_RECEIPT")

    def test_long_lived_approval_blocks(self):
        self.receipt["expires_at"] = "2026-11-13T18:35:00Z"
        self.assertEqual(self.verify()["reason"], "EXPIRED_OR_OUT_OF_WINDOW_RECEIPT")

    def test_replayed_nonce_blocks(self):
        used = {self.issuer + ":" + self.receipt["nonce"]}
        self.assertEqual(self.verify(consumed_nonces=used)["reason"],
                         "REPLAYED_APPROVAL_NONCE")

    def test_durable_nonce_readback_is_required(self):
        self.assertEqual(self.verify(consumed_nonces=None)["reason"],
                         "NO_DURABLE_REPLAY_READBACK")

    def test_verifier_key_cannot_be_replaced(self):
        other = Ed25519PrivateKey.generate()
        different_public = other.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.assertEqual(self.verify(issuer_keys={self.issuer: different_public})["reason"],
                         "INVALID_PROVIDER_SIGNATURE")


if __name__ == "__main__":
    unittest.main()
