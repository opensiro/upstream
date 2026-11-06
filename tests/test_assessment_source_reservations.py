"""Offline reservation-ledger tests; never touch GitHub or external repositories."""

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SCRIPT = ROOT / "scripts/assessment_source_reservations.py"
SPEC = importlib.util.spec_from_file_location("assessment_source_reservations", SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)
MANIFEST = ROOT / "data/assessment-candidate-batches/2026-10-22-01.json"
EVIDENCE = "https://github.com/opensiro/upstream/issues/144"


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def configure(root):
    git(root, "config", "user.email", "tests@example.org")
    git(root, "config", "user.name", "Native offline test")


class ReservationTests(unittest.TestCase):
    def setUp(self):
        self.original = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_ledger_rejects_casefold_collisions_and_duplicate_claims(self):
        event = {"action": "CLAIM", "event_id": "a" * 32, "batch_id": self.original["batch_id"],
                 "sources": ["Example/Repo"], "evidence": EVIDENCE}
        self.assertEqual(mod.replay({"schema_version": 1, "events": [event]}),
                         {"example/repo": self.original["batch_id"]})
        another = dict(event, event_id="b" * 32, batch_id="assessment-upstream-2026-10-22-99",
                       sources=["example/REPO"])
        with self.assertRaisesRegex(mod.BatchError, "BLOCKED_CONCURRENT_RESERVATION"):
            mod.replay({"schema_version": 1, "events": [event, another]})
        with self.assertRaisesRegex(mod.BatchError, "Duplicate reservation source"):
            mod.replay({"schema_version": 1, "events": [dict(event, sources=["A/B", "a/b"])]})
        with self.assertRaisesRegex(mod.BatchError, "Duplicate or malformed"):
            mod.replay({"schema_version": 1, "events": [event, dict(event, event_id="d" * 32)]})

    def test_release_is_auditable_and_allows_new_owner(self):
        batch = self.original["batch_id"]
        event = {"action": "CLAIM", "event_id": "a" * 32, "batch_id": batch, "sources": ["A/B"], "evidence": EVIDENCE}
        release = {"action": "RELEASE", "event_id": "b" * 32, "batch_id": batch, "sources": ["A/B"],
                   "evidence": EVIDENCE, "reason": "Draft abandoned after review"}
        other = dict(event, event_id="c" * 32, batch_id="assessment-upstream-2026-10-22-99")
        self.assertEqual(mod.replay({"schema_version": 1, "events": [event, release, other]}),
                         {"a/b": other["batch_id"]})
        with self.assertRaisesRegex(mod.BatchError, "original live batch"):
            mod.replay({"schema_version": 1, "events": [event, dict(release, sources=["A/C"])]})
        with self.assertRaisesRegex(mod.BatchError, "original live batch"):
            mod.replay({"schema_version": 1, "events": [event, release, dict(release, event_id="d" * 32)]})

    def _fixture(self, work):
        remote = work / "reservations.git"
        subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
        one = work / "worker-one"
        subprocess.run(["git", "clone", "-q", str(remote), str(one)], check=True)
        configure(one)
        (one / "reservations.json").write_text(
            json.dumps({"schema_version": 1, "events": []}) + "\n", encoding="utf-8")
        git(one, "add", "reservations.json")
        git(one, "commit", "-qm", "Initialize auditable reservation ledger")
        git(one, "push", "-q", "origin", "HEAD:refs/heads/batch-upstream-reservations")
        two = work / "worker-two"
        subprocess.run(["git", "clone", "-q", str(remote), str(two)], check=True)
        configure(two)
        index = work / "index"
        subprocess.run(["git", "init", "-q", str(index)], check=True)
        configure(index)
        data = copy.deepcopy(self.original)
        for candidate in data["candidates"]:
            file = index / candidate["assessment_path"]
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text("---\n" + "\n".join((
                f"harness_id: {file.stem}",
                f"repository: https://github.com/{candidate['source']}",
                f"review_ref: {candidate['review_ref']}",
                f"reviewed_at: {candidate['reviewed_at']}",
                "status: included", "autonomy_s1: A"
            )) + "\n---\n", encoding="utf-8")
        git(index, "add", "assessments")
        git(index, "commit", "-qm", "Index fixture")
        data["index_sha"] = git(index, "rev-parse", "HEAD")
        left, right = work / "left.json", work / "right.json"
        left.write_text(json.dumps(data), encoding="utf-8")
        data["batch_id"] = "assessment-upstream-2026-10-22-99"
        right.write_text(json.dumps(data), encoding="utf-8")
        return one, two, index, left, right

    def test_two_stale_concurrent_claims_at_most_one_pushes(self):
        with tempfile.TemporaryDirectory() as temp:
            one, two, index, left, right = self._fixture(Path(temp))
            before_one = mod.fetch_ledger(one, "origin")
            before_two = mod.fetch_ledger(two, "origin")
            self.assertEqual(before_one[0], before_two[0])
            with patch.object(mod, "fetch_ledger", return_value=before_one):
                receipt = mod.claim(one, "origin", left, index, EVIDENCE, write=True)
            self.assertEqual(receipt["status"], "CLAIMED_CAS")
            self.assertFalse(receipt["admission_attested"])
            with patch.object(mod, "fetch_ledger", return_value=before_two):
                with self.assertRaisesRegex(mod.BatchError, "non-fast-forward CAS rejected"):
                    mod.claim(two, "origin", right, index, EVIDENCE, write=True)
            _, ledger = mod.fetch_ledger(two, "origin")
            self.assertEqual(len(ledger["events"]), 1)
            with self.assertRaisesRegex(mod.BatchError, "BLOCKED_CONCURRENT_RESERVATION"):
                mod.claim(two, "origin", right, index, EVIDENCE, write=False)

    def test_index_pin_and_full_five_are_mandatory(self):
        with tempfile.TemporaryDirectory() as temp:
            one, _, index, left, _ = self._fixture(Path(temp))
            report = mod.claim(one, "origin", left, index, EVIDENCE)
            self.assertEqual(report["status"], "PREVIEW_ONLY")
            self.assertFalse(report["admission_attested"])
            payload = json.loads(left.read_text(encoding="utf-8"))
            payload["index_sha"] = "0" * 40
            left.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(mod.BatchError, "Index HEAD differs"):
                mod.claim(one, "origin", left, index, EVIDENCE)
            payload["index_sha"] = git(index, "rev-parse", "HEAD")
            payload["candidates"].pop()
            left.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(mod.BatchError, "Freeze a full cohort"):
                mod.claim(one, "origin", left, index, EVIDENCE)

    def test_missing_remote_reservation_ref_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            local = Path(temp)
            subprocess.run(["git", "init", "-q", str(local)], check=True)
            with self.assertRaisesRegex(mod.BatchError, "BLOCKED_GITHUB_VISIBILITY"):
                mod.fetch_ledger(local, "origin")


if __name__ == "__main__":
    unittest.main()
