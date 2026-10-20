"""Offline operator-signature tests: ephemeral keys only, no live approval."""
import base64
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from connected_stage_adapter import StageBlocked
from signed_one_use_prepare_host import (AUDIENCE, SignedOneUsePrepareHost,
                                         canonical_json, sha256)


class SignedPrepareGrantTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        self.private = self.path / "operator-private.pem"
        self.public = self.path / "operator-public.pem"
        self.grant_file = self.path / "signed-grant.json"
        self.ledger_dir = self.path / "host-ledger"
        self.ledger_dir.mkdir(mode=0o700)
        self.ledger = self.ledger_dir / "replay.sqlite"
        subprocess.run(["openssl", "ecparam", "-name", "prime256v1",
                        "-genkey", "-noout", "-out", str(self.private)],
                       capture_output=True, check=True)
        subprocess.run(["openssl", "pkey", "-in", str(self.private),
                        "-pubout", "-out", str(self.public)],
                       capture_output=True, check=True)
        self.key_hash = sha256(self.public.read_bytes())
        self.now = 1850000000
        self.intent = {
            "stage": "prepare_contribution",
            "actor": "xLagerFeuer",
            "working_repo": "opensiro-contributions/HarnessDesk",
            "source_sha": "81d5e34e0e8e3d7e0945bc680695940b41ab852f",
            "fork_observed_sha": "4029e95189c61485f934f158c6725ef6eeb7ef35",
            "new_branch": "opensiro/fix-toolgateway-1772",
            "patch_sha256": "12b5c7e55a6f730fb9a2465ca30dd47321690c87c0d887e7b8c9d6990ec186e7",
        }

    def make_host(self, **overrides):
        args = dict(public_key_file=self.public, trusted_key_sha256=self.key_hash,
                    issuer_actor="xLagerFeuer", signed_grant_file=self.grant_file,
                    replay_db=self.ledger, clock=lambda: self.now)
        args.update(overrides)
        return SignedOneUsePrepareHost(**args)

    def signed_payload(self, **overrides):
        payload = {
            "schema_version": 1, "audience": AUDIENCE,
            "issuer_actor": "xLagerFeuer", "subject_actor": "xLagerFeuer",
            "intent_sha256": sha256(canonical_json(self.intent)),
            "grant_id": "0123456789abcdef0123456789abcdef",
            "issued_at": self.now - 30, "expires_at": self.now + 300,
            "public_key_sha256": self.key_hash,
        }
        payload.update(overrides)
        message = self.path / "canonical-payload.json"
        signature = self.path / "signature.bin"
        message.write_bytes(canonical_json(payload))
        subprocess.run(["openssl", "dgst", "-sha256", "-sign", str(self.private),
                        "-out", str(signature), str(message)],
                       capture_output=True, check=True)
        envelope = dict(payload=payload,
                        signature_b64=base64.b64encode(signature.read_bytes()).decode())
        self.grant_file.write_text(json.dumps(envelope))
        self.grant_file.chmod(0o600)
        return envelope

    def test_real_signature_consumed_once_and_restart_replay_rejected(self):
        self.signed_payload()
        host = self.make_host()
        grant = host.verify_exact_prepare(self.intent)
        self.assertNotIsInstance(grant, (bool, int, str, dict))
        self.assertTrue(host.authorize_exact_stage(grant, self.intent))
        with self.assertRaisesRegex(StageBlocked, "already consumed"):
            self.make_host().verify_exact_prepare(self.intent)
        self.assertEqual(stat.S_IMODE(self.ledger.stat().st_mode), 0o600)

    def test_missing_grant_fails_closed(self):
        with self.assertRaisesRegex(StageBlocked, "missing or revoked"):
            self.make_host().verify_exact_prepare(self.intent)

    def test_mutated_action_after_verify_rejected_without_consuming(self):
        self.signed_payload()
        host = self.make_host()
        grant = host.verify_exact_prepare(self.intent)
        other = {**self.intent, "new_branch": "opensiro/other"}
        with self.assertRaisesRegex(StageBlocked, "exact action"):
            host.authorize_exact_stage(grant, other)
        self.assertFalse(self.ledger.exists())

    def test_wrong_actor_and_stage(self):
        self.signed_payload()
        host = self.make_host()
        with self.assertRaises(StageBlocked):
            host.verify_exact_prepare({**self.intent, "actor": "other"})
        with self.assertRaises(StageBlocked):
            host.verify_exact_prepare({**self.intent, "stage": "submit_external_pr"})

    def test_signature_tampering_fails(self):
        env = self.signed_payload()
        env["payload"]["expires_at"] += 1
        self.grant_file.write_text(json.dumps(env))
        self.grant_file.chmod(0o600)
        with self.assertRaisesRegex(StageBlocked, "signature is not valid"):
            self.make_host().verify_exact_prepare(self.intent)

    def test_wrong_signature_key_fingerprint(self):
        self.signed_payload()
        with self.assertRaisesRegex(StageBlocked, "fingerprint"):
            self.make_host(trusted_key_sha256="0" * 64)

    def test_invalid_key_subject_and_audience(self):
        for payload in ({"subject_actor": "someone-else"},
                        {"audience": "other/action"},
                        {"issuer_actor": "other"}):
            with self.subTest(payload=payload):
                self.signed_payload(**payload)
                with self.assertRaises(StageBlocked):
                    self.make_host().verify_exact_prepare(self.intent)

    def test_expired_premature_and_too_long(self):
        for fields in ({"issued_at": self.now - 1000, "expires_at": self.now - 1},
                       {"issued_at": self.now + 2, "expires_at": self.now + 300},
                       {"issued_at": self.now - 30, "expires_at": self.now + 1000}):
            with self.subTest(fields=fields):
                self.signed_payload(**fields)
                with self.assertRaisesRegex(StageBlocked, "15-minute maximum"):
                    self.make_host().verify_exact_prepare(self.intent)

    def test_removal_revokes_between_verify_and_authorize(self):
        self.signed_payload()
        host = self.make_host()
        grant = host.verify_exact_prepare(self.intent)
        self.grant_file.unlink()
        with self.assertRaisesRegex(StageBlocked, "missing or revoked"):
            host.authorize_exact_stage(grant, self.intent)
        self.assertFalse(self.ledger.exists())

    def test_changed_signed_grant_revokes_old_verified_object(self):
        self.signed_payload()
        host = self.make_host()
        grant = host.verify_exact_prepare(self.intent)
        self.signed_payload(grant_id="fedcba9876543210fedcba9876543210")
        with self.assertRaisesRegex(StageBlocked, "changed or revoked"):
            host.authorize_exact_stage(grant, self.intent)

    def test_duplicate_json_payload_rejected(self):
        self.signed_payload()
        raw = self.grant_file.read_text()
        self.grant_file.write_text(raw.replace('"signature_b64":', '"signature_b64": "ABC", "signature_b64":'))
        self.grant_file.chmod(0o600)
        with self.assertRaisesRegex(StageBlocked, "Malformed"):
            self.make_host().verify_exact_prepare(self.intent)

    def test_world_writable_grant_and_replay_directory_denied(self):
        self.signed_payload()
        self.grant_file.chmod(0o666)
        with self.assertRaisesRegex(StageBlocked, "protected regular file"):
            self.make_host().verify_exact_prepare(self.intent)
        self.grant_file.chmod(0o600)
        self.ledger_dir.chmod(0o777)
        with self.assertRaisesRegex(StageBlocked, "private"):
            self.make_host()

    def test_fabricated_grant_and_boolean_denied(self):
        self.signed_payload()
        host = self.make_host()
        host.verify_exact_prepare(self.intent)
        with self.assertRaisesRegex(StageBlocked, "host-issued object"):
            host.authorize_exact_stage(True, self.intent)

    def test_signature_verifier_ignores_untrusted_path_and_openssl_config(self):
        self.signed_payload()
        env = self.grant_file.read_text()
        parsed = json.loads(env)
        parsed["signature_b64"] = base64.b64encode(b"x" * 72).decode()
        self.grant_file.write_text(json.dumps(parsed))
        self.grant_file.chmod(0o600)
        fake_dir = self.path / "hostile-bin"
        fake_dir.mkdir()
        fake = fake_dir / "openssl"
        fake.write_text("#!/bin/sh\nexit 0\n")
        fake.chmod(0o755)
        old_path = os.environ.get("PATH")
        old_config = os.environ.get("OPENSSL_CONF")
        try:
            os.environ["PATH"] = str(fake_dir)
            os.environ["OPENSSL_CONF"] = str(fake_dir / "untrusted.conf")
            with self.assertRaisesRegex(StageBlocked, "signature is not valid"):
                self.make_host().verify_exact_prepare(self.intent)
        finally:
            if old_path is None:
                os.environ.pop("PATH", None)
            else:
                os.environ["PATH"] = old_path
            if old_config is None:
                os.environ.pop("OPENSSL_CONF", None)
            else:
                os.environ["OPENSSL_CONF"] = old_config

    def test_unpinned_openssl_executable_rejected(self):
        self.signed_payload()
        with self.assertRaisesRegex(StageBlocked, "pinned system OpenSSL"):
            self.make_host(openssl="openssl")

    def test_signature_for_different_hash_denied(self):
        self.signed_payload(intent_sha256="a" * 64)
        with self.assertRaisesRegex(StageBlocked, "exact intent mismatch"):
            self.make_host().verify_exact_prepare(self.intent)


if __name__ == "__main__":
    unittest.main()
