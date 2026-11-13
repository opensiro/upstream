"""Verify *provider-signed* chat intent against an exact CLA packet.

This library performs only a cryptographic and structural precheck. It never
accepts an agreement, posts a GitHub comment/PR, consumes a nonce or grants
legal authority. A trusted runtime must supply independently provisioned
issuer keys and account-to-signatory bindings; model-authored JSON is NOT a
trust anchor. Current ChatGPT sessions do not expose such an attestation.
"""
import base64
import binascii
from datetime import datetime, timedelta, timezone
import hashlib
import json
import re

PACKET_FIELDS = frozenset({
    "schema_version", "template_id", "repository", "counterparty",
    "terms_sha256", "fork_repository", "fork_branch", "fork_head_sha",
    "target_base_sha", "signer_actor", "signer_capacity", "exact_action",
})
RECEIPT_FIELDS = frozenset({
    "schema_version", "issuer", "subject", "decision", "packet_sha256",
    "rights_confirmed", "issued_at", "expires_at", "nonce", "signature_b64",
})
HEX40 = re.compile(r"[a-f0-9]{40}\Z")
HEX64 = re.compile(r"[a-f0-9]{64}\Z")
NONCE = re.compile(r"[A-Za-z0-9_-]{16,128}\Z")


def _block(reason):
    return {"status": "BLOCKED", "reason": reason}


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def packet_digest(packet):
    """Return a digest only for an unambiguous, well-formed exact CLA packet."""
    if not isinstance(packet, dict) or set(packet) != PACKET_FIELDS:
        raise ValueError("INVALID_PACKET_FIELDS")
    if packet["schema_version"] != 1:
        raise ValueError("INVALID_PACKET_VERSION")
    for key in PACKET_FIELDS - {"schema_version"}:
        value = packet[key]
        if not isinstance(value, str) or not value or value != value.strip():
            raise ValueError("INVALID_PACKET_VALUE")
    for key in ("fork_head_sha", "target_base_sha"):
        if not HEX40.fullmatch(packet[key]):
            raise ValueError("INVALID_SOURCE_SHA")
    if not HEX64.fullmatch(packet["terms_sha256"]):
        raise ValueError("INVALID_TERMS_DIGEST")
    if packet["signer_capacity"] not in {"individual", "corporate"}:
        raise ValueError("INVALID_SIGNER_CAPACITY")
    if packet["exact_action"] not in {
        "PR_SUBMISSION_CONSTITUTES_ASSENT", "EXPLICIT_BOT_COMMENT_ASSENT",
    }:
        raise ValueError("INVALID_CLA_ACTION")
    if "/" not in packet["repository"] or "/" not in packet["fork_repository"]:
        raise ValueError("INVALID_REPOSITORY")
    if not packet["fork_branch"].startswith("opensiro/"):
        raise ValueError("INVALID_FORK_BRANCH")
    return hashlib.sha256(b"opensiro-cla-chat-packet-v1\0" + _canonical(packet)).hexdigest()


def _utc_timestamp(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("INVALID_TIME")
    stamp = datetime.fromisoformat(value[:-1] + "+00:00")
    if stamp.tzinfo is None:
        raise ValueError("INVALID_TIME")
    return stamp.astimezone(timezone.utc)


def verify_receipt(packet, receipt, *, issuer_keys, signer_subjects,
                   consumed_nonces, now):
    """Read-only verification; a positive result is NEVER permission to POST.

    issuer_keys: pinned Ed25519 public keys from an independent trusted runtime.
    signer_subjects: independently verified mapping of GitHub actor to provider
                     subject IDs, not values copied from the receipt or a chat.
    consumed_nonces: durable, atomically maintained ledger readback. This
                     method does not reserve or consume an approval nonce.
    """
    try:
        digest = packet_digest(packet)
    except (ValueError, TypeError, OverflowError) as error:
        return _block(str(error))
    if not isinstance(receipt, dict) or set(receipt) != RECEIPT_FIELDS:
        return _block("MISSING_OR_MALFORMED_PROVIDER_RECEIPT")
    if receipt["schema_version"] != 1 or receipt["decision"] != "APPROVE":
        return _block("NOT_AN_EXACT_APPROVAL")
    if receipt["rights_confirmed"] is not True:
        return _block("CONTRIBUTOR_RIGHTS_NOT_ATTESTED")
    if receipt["packet_sha256"] != digest:
        return _block("EXACT_PACKET_MISMATCH")
    issuer, subject, nonce = (receipt["issuer"], receipt["subject"],
                              receipt["nonce"])
    if not all(isinstance(v, str) and v for v in (issuer, subject, nonce)):
        return _block("MALFORMED_ISSUER_OR_SUBJECT")
    if not NONCE.fullmatch(nonce):
        return _block("INVALID_NONCE")
    if not isinstance(issuer_keys, dict) or issuer not in issuer_keys:
        return _block("NO_INDEPENDENT_TRUSTED_ISSUER_KEY")
    subjects = signer_subjects.get(packet["signer_actor"]) if isinstance(signer_subjects, dict) else None
    if not isinstance(subjects, (set, frozenset)) or subject not in subjects:
        return _block("NO_INDEPENDENT_SIGNER_IDENTITY_BINDING")
    if not isinstance(consumed_nonces, (set, frozenset)):
        return _block("NO_DURABLE_REPLAY_READBACK")
    if issuer + ":" + nonce in consumed_nonces:
        return _block("REPLAYED_APPROVAL_NONCE")
    if not isinstance(now, datetime) or now.tzinfo is None:
        return _block("NO_TRUSTED_CURRENT_TIME")
    try:
        issued = _utc_timestamp(receipt["issued_at"])
        expires = _utc_timestamp(receipt["expires_at"])
    except (TypeError, ValueError, OverflowError):
        return _block("INVALID_RECEIPT_TIMESTAMP")
    clock = now.astimezone(timezone.utc)
    if (expires <= issued or expires - issued > timedelta(minutes=10)
            or issued > clock + timedelta(seconds=30) or expires <= clock):
        return _block("EXPIRED_OR_OUT_OF_WINDOW_RECEIPT")
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except ImportError:
        return _block("ED25519_VERIFIER_UNAVAILABLE")
    key = issuer_keys[issuer]
    if not isinstance(key, bytes) or len(key) != 32:
        return _block("INVALID_TRUSTED_ISSUER_KEY")
    raw = receipt["signature_b64"]
    if not isinstance(raw, str):
        return _block("INVALID_SIGNATURE_ENCODING")
    try:
        signature = base64.b64decode(raw, validate=True)
        if len(signature) != 64:
            return _block("INVALID_SIGNATURE")
        payload = {k: v for k, v in receipt.items() if k != "signature_b64"}
        Ed25519PublicKey.from_public_bytes(key).verify(
            signature, b"opensiro-cla-chat-receipt-v1\0" + _canonical(payload))
    except (InvalidSignature, ValueError, TypeError, binascii.Error, OverflowError):
        return _block("INVALID_PROVIDER_SIGNATURE")

    # Deliberately never emit ALLOW. Cryptographic intent is only one gate.
    # A separate trusted executor still needs live terms/branch/rights checks,
    # an enrolled policy, native tests, atomic nonce consumption and target
    # readback. No such executor or trusted chat issuer is available today.
    return {
        "status": "VERIFIED_RECEIPT_NON_EXECUTABLE",
        "reason": "LIVE_LEGAL_AND_TECHNICAL_GATES_AND_ATOMIC_NONCE_PENDING",
        "packet_sha256": digest,
        "nonce_key": issuer + ":" + nonce,
    }
