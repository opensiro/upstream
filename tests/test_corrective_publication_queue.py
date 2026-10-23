"""Native offline checks of the finite external Corrective PR mandate."""

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/corrective_publication_queue.py"
SPEC = importlib.util.spec_from_file_location("corrective_publication_queue", SCRIPT)
queue = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(queue)
LEDGER = ROOT / "data/corrective-publication/2026-10-23-01.json"


class CorrectiveMandateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(LEDGER.read_text(encoding="utf-8"))

    def test_exact_finite_snapshot_and_native_only_mode(self):
        board = queue.report(self.data)
        self.assertEqual(board["authorized_count"], 34)
        expected_next = next((case["id"] for case in self.data["cases"]
                              if case["publication"] == "QUEUED"), None)
        self.assertEqual(board["next_candidate"], expected_next)
        self.assertEqual(sum(board["counts"].values()), 34)
        self.assertEqual(board["test_mode"], "NATIVE_SCRIPT_ONLY_NO_LLM_AGENTS")
        self.assertTrue(board["no_external_writes_performed_by_this_command"])

    def test_blocked_case_moves_to_next_with_source_history_unchanged(self):
        ledger = copy.deepcopy(self.data)
        queued = next((case for case in ledger["cases"]
                       if case["publication"] == "QUEUED"), None)
        if queued is None:
            self.skipTest("No queued publication case remains")
        queued["publication"] = "BLOCKED"
        queued["reason"] = "The current upstream source already fixed the defect."
        expected_next = next((case["id"] for case in ledger["cases"]
                              if case["publication"] == "QUEUED"), None)
        self.assertEqual(queue.report(ledger)["next_candidate"], expected_next)

    def test_reject_out_of_scope_reordering_and_unsupported_stage(self):
        transforms = (
            lambda d: d["cases"].pop(),
            lambda d: d["cases"].reverse(),
            lambda d: d["cases"][0].update(id="citadel-native-claim-exclusivity"),
            lambda d: d["cases"][0].update(publication="ACTIVE"),
            lambda d: d["cases"][0].update(publication="QUEUED"),
            lambda d: d["cases"][0].update(pr_url="https://github.com/not-a-pr"),
            lambda d: d.update(candidate_snapshot_sha="0" * 40),
        )
        for mutate in transforms:
            with self.subTest(mutate=mutate):
                ledger = copy.deepcopy(self.data)
                mutate(ledger)
                with self.assertRaises(queue.QueueError):
                    queue.validate(ledger)

    def test_submitted_requires_genuine_actor_receipt_and_upstream_target(self):
        ledger = copy.deepcopy(self.data)
        row = ledger["cases"][0]
        row.update(
            publication="SUBMITTED",
            pr_url="https://github.com/Rohith-s-hub/Oblivion-agent/pull/123",
            actor="xLagerFeuer",
            base_sha="a" * 40,
            head_sha="b" * 40,
            native_test_receipt="fixed fixture RED->GREEN verified on source",
        )
        queue.validate(ledger)
        row["pr_url"] = "https://github.com/opensiro/upstream/pull/123"
        with self.assertRaisesRegex(queue.QueueError, "exact target upstream"):
            queue.validate(ledger)

    def test_shallow_checkout_offline_blob_validation_rejects_mutation(self):
        original = queue._git_show(queue.FROZEN_SNAPSHOT_SHA, queue.SOURCE_BATCHES[0])
        self.assertTrue(original["candidates"])
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / queue.SOURCE_BATCHES[0]
            target.parent.mkdir(parents=True)
            target.write_text(json.dumps(original) + "\n", encoding="utf-8")
            with patch.object(queue, "ROOT", Path(root)):
                with self.assertRaisesRegex(queue.QueueError, "manifest changed"):
                    queue._git_show(queue.FROZEN_SNAPSHOT_SHA, queue.SOURCE_BATCHES[0])


if __name__ == "__main__":
    unittest.main()
