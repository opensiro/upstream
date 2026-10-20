"""Operator-signed, fail-closed one-use host grant for prepare_contribution.

Source component only: not a CLI, token reader, live issuer, or write runner.
The actual operator MUST independently sign the exact intent with a private
key that is never accessible to the agent/VM. Host trust anchors, the signed
envelope, its revocation/removal and the replay ledger must be protected from
the executor. Providing an agent-generated key/fingerprint is NOT authority.
"""
import base64
import binascii
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import subprocess
import tempfile
import time

from connected_stage_adapter import StageBlocked

AUDIENCE = "opensiro/upstream:prepare_contribution"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX32 = re.compile(r"^[0-9a-f]{32}$")
FIELDS = {"schema_version", "audience", "issuer_actor", "subject_actor",
          "intent_sha256", "grant_id", "issued_at", "expires_at",
          "public_key_sha256"}


def canonical_json(value):
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, OverflowError):
        raise StageBlocked("Exact authorization intent not JSON canonicalizable") from None


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def need(ok, reason):
    if not ok:
        raise StageBlocked(reason)


class _VerifiedGrant:
    __slots__ = ("intent_hash", "grant_id", "envelope_hash", "expires_at")

    def __init__(self, intent_hash, grant_id, envelope_hash, expires_at):
        self.intent_hash = intent_hash
        self.grant_id = grant_id
        self.envelope_hash = envelope_hash
        self.expires_at = expires_at


class SignedOneUsePrepareHost:
    """Host-injected exact stage decision, verifiable without private key.

    public_key_file + trusted_key_sha256 + issuer_actor are pinned by an
    independently trusted deployment, NEVER read from the proposal/agent.
    signed_grant_file belongs to a separately operator-controlled location:
    removal/replacement revokes before consumption. replay_db persists and
    must be rollback-resistant to the executor. This component only verifies
    and atomically consumes; it cannot generate operator decisions.
    """

    def __init__(self, *, public_key_file, trusted_key_sha256, issuer_actor,
                 signed_grant_file, replay_db, clock=None, openssl="/usr/bin/openssl"):
        need(type(trusted_key_sha256) is str and HEX64.fullmatch(trusted_key_sha256),
             "No pinned operator public-key fingerprint")
        need(type(issuer_actor) is str and issuer_actor == "xLagerFeuer",
             "Unexpected independently enrolled operator")
        need(type(openssl) is str and openssl == "/usr/bin/openssl",
             "Only pinned system OpenSSL verifier supported")
        binary = Path(openssl)
        need(binary.is_file() and not binary.is_symlink()
             and binary.stat().st_uid == 0
             and (stat.S_IMODE(binary.stat().st_mode) & 0o022) == 0
             and all(Path(parent).stat().st_uid == 0
                     and (stat.S_IMODE(Path(parent).stat().st_mode) & 0o022) == 0
                     for parent in ("/usr", "/usr/bin")),
             "System signature verifier/directory is not protected")
        self._openssl = openssl
        self._public_key_file = Path(public_key_file)
        self._grant_file = Path(signed_grant_file)
        self._db = Path(replay_db)
        self._expected_key_hash = trusted_key_sha256
        self._issuer = issuer_actor
        self._clock = clock if clock is not None else time.time
        need(callable(self._clock), "Trusted host clock unavailable")
        self._prepared = None

        need(self._public_key_file.is_file()
             and not self._public_key_file.is_symlink(),
             "Enrolled operator public key unavailable")
        key = self._public_key_file.read_bytes()
        need(len(key) <= 8192 and key.startswith(b"-----BEGIN PUBLIC KEY-----")
             and hmac.compare_digest(sha256(key), trusted_key_sha256),
             "Enrolled operator key does not match trusted fingerprint")
        need(self._db.parent.is_dir() and not self._db.parent.is_symlink()
             and (stat.S_IMODE(self._db.parent.stat().st_mode) & 0o077) == 0,
             "Replay ledger parent must be private to trusted host")
        self._public_key = key

    def _now(self):
        now = self._clock()
        need(type(now) in (float, int) and 0 < now < 4102444800,
             "Trusted clock unavailable")
        return now

    def _read_envelope(self):
        need(self._grant_file.is_file() and not self._grant_file.is_symlink(),
             "Signed operator grant missing or revoked")
        st = self._grant_file.stat()
        need(stat.S_ISREG(st.st_mode) and st.st_size <= 8192
             and (stat.S_IMODE(st.st_mode) & 0o022) == 0,
             "Grant file is not a protected regular file")
        raw = self._grant_file.read_bytes()
        need(len(raw) <= 8192, "Signed grant exceeds bound")
        try:
            env = json.loads(raw, object_pairs_hook=self._no_duplicates)
        except (ValueError, UnicodeError):
            raise StageBlocked("Malformed operator-signed grant") from None
        need(type(env) is dict and set(env) == {"payload", "signature_b64"},
             "Unexpected grant envelope fields")
        return raw, env

    @staticmethod
    def _no_duplicates(pairs):
        data = {}
        for k, v in pairs:
            if k in data:
                raise ValueError("Duplicate JSON key")
            data[k] = v
        return data

    def _verify_signature(self, payload, signature_b64):
        need(type(signature_b64) is str and len(signature_b64) <= 2048,
             "Missing grant signature")
        try:
            signature = base64.b64decode(signature_b64, validate=True)
        except (binascii.Error, ValueError):
            raise StageBlocked("Invalid grant signature encoding") from None
        need(48 <= len(signature) <= 512, "Invalid grant signature length")
        with tempfile.TemporaryDirectory(prefix="opensiro-verify-grant-") as tmp:
            key_path = Path(tmp) / "owner-public.pem"
            message_path = Path(tmp) / "payload.json"
            sig_path = Path(tmp) / "signature.bin"
            key_path.write_bytes(self._public_key)
            message_path.write_bytes(canonical_json(payload))
            sig_path.write_bytes(signature)
            try:
                result = subprocess.run(
                    [self._openssl, "dgst", "-sha256", "-verify", str(key_path),
                     "-signature", str(sig_path), str(message_path)],
                    capture_output=True, timeout=10, check=False,
                    env={"PATH": "/usr/bin:/bin", "HOME": "/nonexistent",
                         "OPENSSL_CONF": "/dev/null"})
            except (OSError, subprocess.TimeoutExpired):
                raise StageBlocked("Operator signature verifier unavailable") from None
            need(result.returncode == 0, "Operator signature is not valid")

    def _verify_payload(self, env, intent_hash):
        payload = env["payload"]
        need(type(payload) is dict and set(payload) == FIELDS,
             "Invalid exact-grant payload")
        need(payload["schema_version"] == 1
             and type(payload["schema_version"]) is int
             and payload["audience"] == AUDIENCE
             and payload["issuer_actor"] == self._issuer
             and type(payload["subject_actor"]) is str
             and type(payload["intent_sha256"]) is str
             and HEX64.fullmatch(payload["intent_sha256"])
             and hmac.compare_digest(payload["intent_sha256"], intent_hash)
             and payload["public_key_sha256"] == self._expected_key_hash
             and type(payload["grant_id"]) is str
             and HEX32.fullmatch(payload["grant_id"]),
             "Grant issuer, actor, audience, key or exact intent mismatch")
        issued, expires = payload["issued_at"], payload["expires_at"]
        need(type(issued) is int and type(expires) is int
             and 0 < expires - issued <= 900
             and issued <= self._now() < expires,
             "Grant expired, premature or outside 15-minute maximum")
        self._verify_signature(payload, env["signature_b64"])
        return payload

    def _ledger_connection(self, *, create=False):
        if self._db.exists():
            need(self._db.is_file() and not self._db.is_symlink()
                 and (stat.S_IMODE(self._db.stat().st_mode) & 0o077) == 0,
                 "Replay ledger is not protected")
        elif create:
            flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            try:
                fd = os.open(self._db, flags, 0o600)
                os.close(fd)
            except FileExistsError:
                pass
        else:
            return None
        db = sqlite3.connect(str(self._db), timeout=3, isolation_level=None)
        db.execute("PRAGMA synchronous=FULL")
        db.execute("CREATE TABLE IF NOT EXISTS consumed (grant_id TEXT PRIMARY KEY, intent_sha256 TEXT NOT NULL, consumed_at INTEGER NOT NULL)")
        return db

    def _already_consumed(self, grant_id):
        try:
            db = self._ledger_connection()
            if db is None:
                return False
            try:
                return db.execute(
                    "SELECT 1 FROM consumed WHERE grant_id=?", (grant_id,)
                ).fetchone() is not None
            finally:
                db.close()
        except sqlite3.Error:
            raise StageBlocked("Replay protection unavailable") from None

    def verify_exact_prepare(self, intent):
        need(type(intent) is dict and intent.get("stage") == "prepare_contribution"
             and intent.get("actor") == self._issuer
             and intent.get("working_repo") == "opensiro-contributions/HarnessDesk",
             "Intent outside enrolled bounded prepare stage")
        intent_hash = sha256(canonical_json(intent))
        raw, env = self._read_envelope()
        payload = self._verify_payload(env, intent_hash)
        need(payload["subject_actor"] == intent["actor"],
             "Signed grant subject does not match current provider actor")
        need(not self._already_consumed(payload["grant_id"]),
             "Signed grant already consumed")
        need(self._prepared is None, "Host already has an outstanding grant")
        grant = _VerifiedGrant(intent_hash, payload["grant_id"],
                               sha256(raw), payload["expires_at"])
        self._prepared = grant
        return grant

    def authorize_exact_stage(self, grant, intent):
        need(grant is not None and grant is self._prepared
             and type(grant) is _VerifiedGrant,
             "Grant is not the authenticated host-issued object")
        need(type(intent) is dict
             and hmac.compare_digest(sha256(canonical_json(intent)), grant.intent_hash),
             "Grant does not authorize this exact action")
        raw, env = self._read_envelope()  # revocation/removal checked AGAIN
        need(hmac.compare_digest(sha256(raw), grant.envelope_hash),
             "Signed grant changed or revoked after verification")
        payload = self._verify_payload(env, grant.intent_hash)
        need(payload["grant_id"] == grant.grant_id
             and self._now() < grant.expires_at,
             "Grant changed or expired before one-use consumption")
        db = None
        try:
            db = self._ledger_connection(create=True)
            db.execute("BEGIN IMMEDIATE")
            existing = db.execute(
                "SELECT 1 FROM consumed WHERE grant_id=?", (grant.grant_id,)
            ).fetchone()
            need(existing is None, "Grant already consumed by another executor")
            db.execute("INSERT INTO consumed(grant_id,intent_sha256,consumed_at) VALUES(?,?,?)",
                       (grant.grant_id, grant.intent_hash, int(self._now())))
            db.execute("COMMIT")
        except (sqlite3.Error, OSError):
            if db is not None:
                try:
                    db.execute("ROLLBACK")
                except sqlite3.Error:
                    pass
            raise StageBlocked("Atomic replay ledger consumption failed") from None
        finally:
            if db is not None:
                db.close()
        self._prepared = None
        return True
