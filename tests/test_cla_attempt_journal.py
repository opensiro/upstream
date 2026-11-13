"""Source-native offline tests: single-use claims never mean CLA permission."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.cla_attempt_journal import AttemptJournal


class AttemptJournalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = str(Path(self.tmp.name) / "journal.sqlite3")
        self.journal = AttemptJournal(self.db)
        self.args = dict(
            nonce_key="test-issuer:test-nonce-20261113",
            packet_hash="a" * 64,
            target="KumihoIO/Revka",
            fork_head="b" * 40,
            now=datetime(2026, 11, 13, 17, 30, tzinfo=timezone.utc),
        )

    def test_record_is_not_a_legal_approval(self):
        result = self.journal.reserve(**self.args)
        self.assertEqual(result["status"], "RECORDED_NON_EXECUTABLE")
        self.assertEqual(result["phase"], "RESERVED_NO_POST")
        self.assertNotIn("ALLOW", result["status"])

    def test_duplicate_nonce_denied_even_same_packet(self):
        self.journal.reserve(**self.args)
        result = self.journal.reserve(**self.args)
        self.assertEqual(result["reason"], "NONCE_USED_OR_INVALID_STATE")

    def test_duplicate_nonce_denied_other_target(self):
        self.journal.reserve(**self.args)
        args = dict(self.args, target="microsoft/fara")
        self.assertEqual(self.journal.reserve(**args)["reason"],
                         "NONCE_USED_OR_INVALID_STATE")

    def test_duplicate_nonce_denied_new_content(self):
        self.journal.reserve(**self.args)
        args = dict(self.args, packet_hash="c" * 64)
        self.assertEqual(self.journal.reserve(**args)["reason"],
                         "NONCE_USED_OR_INVALID_STATE")

    def test_durable_nonce_survives_reopen(self):
        self.journal.reserve(**self.args)
        reopened = AttemptJournal(self.db)
        self.assertEqual(reopened.reserve(**self.args)["status"], "BLOCKED")
        self.assertEqual(reopened.inspect(self.args["nonce_key"])["phase"],
                         "RESERVED_NO_POST")

    def test_wrong_head_cannot_start_dispatch(self):
        self.journal.reserve(**self.args)
        args = dict(self.args, fork_head="c" * 40)
        self.assertEqual(self.journal.begin_attempt(**args)["status"], "BLOCKED")
        self.assertEqual(self.journal.inspect(self.args["nonce_key"])["dispatch_count"], 0)

    def test_wrong_packet_cannot_start_dispatch(self):
        self.journal.reserve(**self.args)
        args = dict(self.args, packet_hash="c" * 64)
        self.assertEqual(self.journal.begin_attempt(**args)["status"], "BLOCKED")

    def test_cannot_begin_attempt_without_reservation(self):
        self.assertEqual(self.journal.begin_attempt(**self.args)["status"], "BLOCKED")

    def test_dispatch_flag_is_one_way(self):
        self.journal.reserve(**self.args)
        first = self.journal.begin_attempt(**self.args)
        self.assertEqual(first["phase"], "DISPATCH_BEGAN_UNCONFIRMED")
        self.assertEqual(self.journal.begin_attempt(**self.args)["status"], "BLOCKED")
        self.assertEqual(self.journal.inspect(self.args["nonce_key"])["dispatch_count"], 1)

    def test_dispatch_remains_ambiguous_after_restart(self):
        self.journal.reserve(**self.args)
        self.journal.begin_attempt(**self.args)
        reopened = AttemptJournal(self.db)
        self.assertEqual(reopened.begin_attempt(**self.args)["status"], "BLOCKED")
        self.assertEqual(reopened.inspect(self.args["nonce_key"])["phase"],
                         "DISPATCH_BEGAN_UNCONFIRMED")

    def test_readback_cannot_precede_dispatch(self):
        self.journal.reserve(**self.args)
        self.assertEqual(self.journal.record_readback(
            **self.args, target_url="https://github.com/KumihoIO/Revka/pull/123")["status"], "BLOCKED")

    def test_readback_is_annotated_as_unverified(self):
        self.journal.reserve(**self.args)
        self.journal.begin_attempt(**self.args)
        result = self.journal.record_readback(
            **self.args, target_url="https://github.com/KumihoIO/Revka/pull/123")
        self.assertEqual(result["phase"], "READBACK_REPORTED_UNVERIFIED")
        self.assertEqual(self.journal.inspect(self.args["nonce_key"])["dispatch_count"], 1)
        self.assertEqual(self.journal.begin_attempt(**self.args)["status"], "BLOCKED")

    def test_wrong_target_or_bogus_url_denied(self):
        self.journal.reserve(**self.args)
        self.journal.begin_attempt(**self.args)
        for url in ("https://github.com/microsoft/fara/pull/2",
                    "https://github.com/KumihoIO/Revka/issues/2",
                    "http://github.com/KumihoIO/Revka/pull/3",
                    "https://evil.example/pull/4",
                    "https://github.com/KumihoIO/Revka/pull/0"):
            with self.subTest(url=url):
                self.assertEqual(self.journal.record_readback(
                    **self.args, target_url=url)["status"], "BLOCKED")

    def test_no_raw_nonce_stored(self):
        self.journal.reserve(**self.args)
        record = Path(self.db).read_bytes()
        self.assertNotIn(self.args["nonce_key"].encode(), record)

    def test_naive_time_fails_closed(self):
        args = dict(self.args, now=datetime(2026, 11, 13, 17, 30))
        self.assertEqual(self.journal.reserve(**args)["reason"],
                         "MISSING_TRUSTED_CURRENT_TIME")

    def test_malformed_inputs_block(self):
        values = (
            ("nonce_key", "short"),
            ("packet_hash", "invalid"),
            ("fork_head", "bad"),
            ("target", "../unsafe"),
        )
        for key, value in values:
            with self.subTest(key=key):
                self.assertEqual(self.journal.reserve(
                    **dict(self.args, **{key: value}))["status"], "BLOCKED")

    def test_nonpersistent_db_rejected(self):
        with self.assertRaisesRegex(ValueError, "PERSISTENT_DATABASE_PATH_REQUIRED"):
            AttemptJournal(":memory:")

    def test_concurrent_double_spend_only_one_reservation(self):
        # Each worker opens a distinct SQLite connection to the same durable file.
        with ThreadPoolExecutor(max_workers=12) as pool:
            results = list(pool.map(lambda _: self.journal.reserve(**self.args),
                                    range(24)))
        self.assertEqual(sum(x["status"] == "RECORDED_NON_EXECUTABLE" for x in results), 1)
        self.assertEqual(sum(x["status"] == "BLOCKED" for x in results), 23)

    def test_concurrent_dispatch_only_one_attempt(self):
        self.journal.reserve(**self.args)
        with ThreadPoolExecutor(max_workers=12) as pool:
            results = list(pool.map(lambda _: self.journal.begin_attempt(**self.args),
                                    range(24)))
        self.assertEqual(sum(x["phase"] == "DISPATCH_BEGAN_UNCONFIRMED"
                             for x in results if x["status"] == "RECORDED_NON_EXECUTABLE"), 1)
        self.assertEqual(self.journal.inspect(self.args["nonce_key"])["dispatch_count"], 1)


if __name__ == "__main__":
    unittest.main()
