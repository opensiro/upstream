"""Offline Upstream Auto selection and concurrency safety tests."""

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("upstream_auto", ROOT / "scripts/upstream_auto.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)
NOW = datetime(2026, 11, 7, 17, 0, 0, tzinfo=timezone.utc)
SHA = "1" * 40
HEAD = "a" * 40


def stamp(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def task(id, *, lane="maintenance", repo="example/repo", priority="P2",
         queued_hours=1, status="ACTIONABLE", resources=None):
    if resources is None:
        resources = [f"source:{repo}", f"pr:{repo}#4"]
    return {"task_id": id, "lane": lane, "owner_issue": mod.LANE_OWNER[lane],
            "resources": resources,
            "evidence_url": f"https://github.com/{repo}/pull/4",
            "queued_at": stamp(NOW - timedelta(hours=queued_hours)),
            "observed_at": stamp(NOW - timedelta(minutes=3)),
            "status": status, "priority": priority, "operation": "READ_ONLY_REVIEW",
            "head_sha": HEAD if any(k.startswith("pr:") for k in resources) else None}


def manifest(*tasks):
    return {"schema_version": 1, "upstream_main_sha": SHA,
            "observed_at": stamp(NOW), "tasks": list(tasks)}


class FakeReader:
    def get(self, path):
        if path == "/repos/opensiro/upstream/branches/main":
            return {"commit": {"sha": SHA}}
        if path in ("/repos/opensiro/upstream/issues/125",
                    "/repos/opensiro/upstream/issues/159",
                    "/repos/opensiro/upstream/issues/150",
                    "/repos/opensiro/upstream/issues/56"):
            return {"state": "open"}
        if path in ("/repos/example/repo/pulls/4", "/repos/other/repo/pulls/4"):
            return {"state": "open", "head": {"sha": HEAD}}
        raise AssertionError("Unexpected GitHub API path: " + path)


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def make_fixture(base):
    remote = base / "reservations.git"
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
    workers = []
    for name in ("worker-one", "worker-two"):
        worker = base / name
        subprocess.run(["git", "clone", "-q", str(remote), str(worker)], check=True)
        git(worker, "config", "user.email", "test@opensiro.example")
        git(worker, "config", "user.name", "Offline task test")
        workers.append(worker)
    worker = workers[0]
    (worker / "reservations.json").write_text(
        json.dumps({"schema_version": 1, "events": []}) + "\n", encoding="utf-8")
    git(worker, "add", "reservations.json")
    git(worker, "commit", "-qm", "Initialize task reservations")
    git(worker, "push", "-q", "origin", "HEAD:" + mod.LEDGER_REF)
    return workers


class UpstreamAutoTests(unittest.TestCase):
    def test_priority_urgent_feedback_and_age_fairness(self):
        high = task("maintenance:urgent", priority="P0", queued_hours=1)
        ordinary = task("outcomes:normal", lane="outcomes", repo="other/repo",
                        priority="P2", queued_hours=1)
        choice = mod.plan(manifest(ordinary, high), {"schema_version": 1, "events": []}, now=NOW)
        self.assertEqual(choice["selected"]["task_id"], high["task_id"])
        old = task("outcomes:old", lane="outcomes", repo="old/repo", priority="P3",
                   queued_hours=40)
        recent = task("maintenance:new", priority="P2", queued_hours=1)
        self.assertEqual(mod.plan(manifest(old, recent), {"schema_version": 1, "events": []},
                                  now=NOW)["selected"]["task_id"], old["task_id"])

    def test_duplicate_id_stale_evidence_and_forbidden_operation_fail_closed(self):
        item = task("maintenance:test")
        with self.assertRaisesRegex(mod.AutoError, "Duplicate or malformed"):
            mod.validate_manifest(manifest(item, item), now=NOW)
        bogus = copy.deepcopy(item)
        bogus["operation"] = "EXTERNAL_PR_PUBLICATION"
        with self.assertRaisesRegex(mod.AutoError, "External writes"):
            mod.validate_manifest(manifest(bogus), now=NOW)
        stale = manifest(item)
        stale["observed_at"] = stamp(NOW - timedelta(hours=2))
        with self.assertRaisesRegex(mod.AutoError, "BLOCKED_STALE_EVIDENCE"):
            mod.validate_manifest(stale, now=NOW)
        item["owner_issue"] = 307
        with self.assertRaisesRegex(mod.AutoError, "admitted Upstream owner"):
            mod.validate_manifest(manifest(item), now=NOW)

    def test_pr_identity_evidence_and_resource_lock_must_agree(self):
        item = task("maintenance:identity")
        item["evidence_url"] = "https://github.com/unrelated/project/pull/4"
        with self.assertRaisesRegex(mod.AutoError, "exact target PR"):
            mod.validate_manifest(manifest(item), now=NOW)
        item["evidence_url"] = "https://github.com/example/repo/pull/4"
        item["resources"] = ["pr:example/repo#4"]
        with self.assertRaisesRegex(mod.AutoError, "source resource lock"):
            mod.validate_manifest(manifest(item), now=NOW)
        item["resources"] = ["source:EXAMPLE/REPO", "source:example/repo", "pr:example/repo#4"]
        with self.assertRaisesRegex(mod.AutoError, "duplicate resource key"):
            mod.validate_manifest(manifest(item), now=NOW)

    def test_blocked_or_empty_proposal_is_not_auto_promoted(self):
        blocked = task("maintenance:blocked", status="AWAITING_EXTERNAL")
        view = mod.plan(manifest(blocked), {"schema_version": 1, "events": []}, now=NOW)
        self.assertEqual(view["status"], "NO_VERIFIED_ELIGIBLE_WORK")
        self.assertIsNone(view["selected"])
        self.assertEqual(mod.plan(manifest(), {"schema_version": 1, "events": []},
                                  now=NOW)["status"], "NO_VERIFIED_ELIGIBLE_WORK")

    def test_dedup_busy_and_wip_caps(self):
        first = task("maintenance:one")
        second = task("maintenance:two", repo="other/repo")
        third = task("outcomes:three", lane="outcomes", repo="third/repo")
        active_claim = {"action": "CLAIM", "claim_id": "a" * 32,
                        "task_id": "maintenance:existing", "actor": "agent-one",
                        "resources": first["resources"], "owner_issue": 125,
                        "evidence_url": first["evidence_url"],
                        "timestamp": stamp(NOW - timedelta(minutes=5))}
        ledger = {"schema_version": 1, "events": [active_claim]}
        view = mod.plan(manifest(first, second, third), ledger, now=NOW)
        self.assertIn({"task_id": first["task_id"], "reason": "CLAIMED_RESOURCE"}, view["blocked"])
        self.assertNotEqual(view["selected"]["task_id"], first["task_id"])
        second_claim = dict(active_claim, claim_id="b" * 32, task_id="maintenance:other",
                            resources=second["resources"])
        view = mod.plan(manifest(first, second, third),
                        {"schema_version": 1, "events": [active_claim, second_claim]}, now=NOW)
        self.assertEqual(view["selected"]["task_id"], third["task_id"])

    def test_frozen_batch_requires_identity_and_keeps_owner(self):
        batch = task("batch:review", lane="batch", resources=[
            "batch:assessment-upstream-2026-11-07-01",
            "source:example/one", "source:example/two", "source:example/three",
            "source:example/four", "source:example/five"])
        self.assertEqual(mod.validate_manifest(manifest(batch), now=NOW)[0]["owner_issue"], 56)
        batch["resources"] = ["source:other/repo"]
        with self.assertRaisesRegex(mod.AutoError, "frozen batch identity"):
            mod.validate_manifest(manifest(batch), now=NOW)

    def test_live_preflight_mismatched_pr_head_and_owner(self):
        item = task("maintenance:review")
        self.assertEqual(mod.live_preflight(manifest(item), item, FakeReader())["status"],
                         "LIVE_PREFLIGHT_PASS")

        class MovedHead(FakeReader):
            def get(self, path):
                data = super().get(path)
                if path.endswith("/pulls/4"):
                    data["head"]["sha"] = "b" * 40
                return data

        with self.assertRaisesRegex(mod.AutoError, "BLOCKED_PR_HEAD_CHANGED"):
            mod.live_preflight(manifest(item), item, MovedHead())

        class ClosedOwner(FakeReader):
            def get(self, path):
                data = super().get(path)
                if path.endswith("/issues/125"):
                    data["state"] = "closed"
                return data

        with self.assertRaisesRegex(mod.AutoError, "BLOCKED_OWNER_ISSUE"):
            mod.live_preflight(manifest(item), item, ClosedOwner())

        class MovedMain(FakeReader):
            def get(self, path):
                data = super().get(path)
                if path.endswith("/branches/main"):
                    data["commit"]["sha"] = "f" * 40
                return data

        with self.assertRaisesRegex(mod.AutoError, "BLOCKED_STALE_SOURCE_CUT"):
            mod.live_preflight(manifest(item), item, MovedMain())
        with self.assertRaisesRegex(mod.AutoError, "live reader required"):
            mod.live_preflight(manifest(item), item, None)

    def test_batch_write_fails_without_independent_five_source_cas(self):
        with tempfile.TemporaryDirectory() as temp:
            one, _ = make_fixture(Path(temp))
            batch = task("batch:review", lane="batch", resources=[
                "batch:assessment-upstream-2026-11-07-01",
                "source:example/one", "source:example/two", "source:example/three",
                "source:example/four", "source:example/five"])
            with self.assertRaisesRegex(mod.AutoError, "BLOCKED_BATCH_SOURCE_CAS"):
                mod.claim(one, "origin", manifest(batch), "agent-one", write=True,
                          reader=FakeReader(), now=NOW)

    def test_two_stale_concurrent_claims_one_wins_then_disjoint_progress(self):
        with tempfile.TemporaryDirectory() as temp:
            one, two = make_fixture(Path(temp))
            inp = manifest(task("maintenance:one"), task("outcomes:two", lane="outcomes", repo="other/repo"))
            before_one = mod.fetch_ledger(one, "origin")
            before_two = mod.fetch_ledger(two, "origin")
            self.assertEqual(before_one[0], before_two[0])
            with patch.object(mod, "fetch_ledger", return_value=before_one):
                result = mod.claim(one, "origin", inp, "agent-one", task_id="maintenance:one",
                                   write=True, reader=FakeReader(), now=NOW)
            self.assertEqual(result["status"], "WRITTEN_CAS")
            self.assertFalse(result["external_writes_authorized"])
            with patch.object(mod, "fetch_ledger", return_value=before_two):
                with self.assertRaisesRegex(mod.AutoError, "BLOCKED_CONCURRENT_RESERVATION"):
                    mod.claim(two, "origin", manifest(task("maintenance:alternate")), "agent-two",
                              write=True, reader=FakeReader(), now=NOW)
            self.assertEqual(len(mod.replay(mod.fetch_ledger(two, "origin")[1])), 1)
            duplicate_source = manifest(task("maintenance:alternate"))
            with self.assertRaisesRegex(mod.AutoError, "NO_VERIFIED_ELIGIBLE_WORK"):
                mod.claim(two, "origin", duplicate_source, "agent-two", write=False, now=NOW)
            different = mod.claim(two, "origin", inp, "agent-two", task_id="outcomes:two",
                                  write=True, reader=FakeReader(), now=NOW)
            self.assertEqual(different["status"], "WRITTEN_CAS")
            self.assertEqual(len(mod.replay(mod.fetch_ledger(one, "origin")[1])), 2)

    def test_release_requires_claim_owner_and_reason_and_resume_is_non_mutating(self):
        with tempfile.TemporaryDirectory() as temp:
            one, _ = make_fixture(Path(temp))
            inp = manifest(task("maintenance:review"))
            receipt = mod.claim(one, "origin", inp, "agent-one", write=True,
                                reader=FakeReader(), now=NOW)
            before = mod.fetch_ledger(one, "origin")[0]
            self.assertEqual(mod.resume(one, "origin", "agent-one", now=NOW)["claims"][0]["status"],
                             "CLAIMED_NEEDS_REVALIDATION")
            self.assertEqual(mod.resume(one, "origin", "agent-one", now=NOW + timedelta(hours=25))
                             ["claims"][0]["status"], "STALE_CLAIM_UNRESOLVED")
            self.assertEqual(mod.fetch_ledger(one, "origin")[0], before)
            with self.assertRaisesRegex(mod.AutoError, "only original actor"):
                mod.release(one, "origin", receipt["claim_id"], "agent-two",
                            "Reviewed evidence and handoff", receipt["live_preflight"] and inp["tasks"][0]["evidence_url"], now=NOW)
            with self.assertRaisesRegex(mod.AutoError, "reason"):
                mod.release(one, "origin", receipt["claim_id"], "agent-one",
                            "done", inp["tasks"][0]["evidence_url"], now=NOW)
            result = mod.release(one, "origin", receipt["claim_id"], "agent-one",
                                 "Owner issue records the reviewed result",
                                 inp["tasks"][0]["evidence_url"], write=True,
                                 now=NOW + timedelta(hours=25))
            self.assertEqual(result["status"], "WRITTEN_CAS")
            self.assertEqual(mod.resume(one, "origin", "agent-one", now=NOW)["claims"], [])

    def test_no_reservation_ref_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            local = Path(temp)
            subprocess.run(["git", "init", "-q", str(local)], check=True)
            with self.assertRaisesRegex(mod.AutoError, "BLOCKED_RESERVATION_VISIBILITY"):
                mod.fetch_ledger(local, "origin")


if __name__ == "__main__":
    unittest.main()
