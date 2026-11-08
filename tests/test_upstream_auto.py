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
         queued_hours=1, status="ACTIONABLE", resources=None,
         pr_number=4, operation="READ_ONLY_REVIEW"):
    if resources is None:
        resources = [f"pr:{repo}#{pr_number}"]
        if operation == "INTERNAL_PREPARE":
            resources.append(f"source:{repo}")
    return {"task_id": id, "lane": lane, "owner_issue": mod.LANE_OWNER[lane],
            "resources": resources,
            "evidence_url": f"https://github.com/{repo}/pull/{pr_number}",
            "queued_at": stamp(NOW - timedelta(hours=queued_hours)),
            "observed_at": stamp(NOW - timedelta(minutes=3)),
            "status": status, "priority": priority, "operation": operation,
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
        if path in ("/repos/example/repo/pulls/4", "/repos/other/repo/pulls/4",
                    "/repos/opensiro/upstream/pulls/111", "/repos/opensiro/upstream/pulls/55"):
            return {"state": "open", "head": {"sha": HEAD},
                    "base": {"sha": SHA}}
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
    def test_existing_fractional_utc_claims_replay_without_widening_manifest(self):
        item = task("portfolio:fractional", lane="portfolio", repo="opensiro/upstream",
                    pr_number=119)
        claim = {"action": "CLAIM", "claim_id": "f" * 32,
                 "task_id": item["task_id"], "actor": "agent-one",
                 "resources": item["resources"], "owner_issue": 150,
                 "operation": "READ_ONLY_REVIEW", "evidence_url": item["evidence_url"],
                 "timestamp": "2026-11-07T16:58:52.432Z"}
        release = {**claim, "action": "RELEASE",
                   "timestamp": "2026-11-07T16:59:11.103Z",
                   "reason": "Reviewed and recorded owner evidence"}
        historic = {"schema_version": 1, "events": [claim, release]}
        self.assertEqual(mod.replay(historic), {})
        self.assertEqual(mod.plan_batch(manifest(item), historic, now=NOW)["selected_count"], 1)
        active = {"schema_version": 1, "events": [claim]}
        self.assertEqual(mod.replay(active)[claim["claim_id"]], claim)
        reversed_within_second = {**release, "timestamp": "2026-11-07T16:58:52.103Z"}
        with self.assertRaisesRegex(mod.AutoError, "Release requires active original"):
            mod.replay({"schema_version": 1, "events": [claim, reversed_within_second]})

        for invalid in ("2026-11-07T16:58:52.1234567Z",
                        "2026-11-07T16:58:52.432+00:00",
                        "2026-11-07T16:58:52.432Zjunk",
                        "2026-11-07T16:58:99.432Z"):
            with self.subTest(invalid=invalid), self.assertRaises(mod.AutoError):
                mod.replay({"schema_version": 1, "events": [{**claim, "timestamp": invalid}]})
        with self.assertRaisesRegex(mod.AutoError, "Invalid UTC timestamp"):
            mod.validate_manifest({**manifest(item),
                                   "observed_at": "2026-11-07T17:00:00.123Z"}, now=NOW)

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

    def test_batch_selector_packs_five_independent_tasks_with_shared_wip(self):
        tasks = [
            task("maintenance:urgent", priority="P0"),
            task("maintenance:duplicate", priority="P1"),
            task("maintenance:second", repo="other/repo", priority="P1"),
            task("outcomes:first", lane="outcomes", repo="outcomes/a", priority="P1"),
            task("outcomes:second", lane="outcomes", repo="outcomes/b", priority="P2"),
            task("portfolio:111", lane="portfolio", repo="opensiro/upstream", pr_number=111),
            task("portfolio:55", lane="portfolio", repo="opensiro/upstream", pr_number=55),
        ]
        view = mod.plan_batch(manifest(*tasks), {"schema_version": 1, "events": []},
                              size=5, now=NOW)
        self.assertEqual(view["fill"], "FULL")
        self.assertEqual(view["selected_count"], 5)
        ids = {item["task_id"] for item in view["selected"]}
        self.assertIn("maintenance:urgent", ids)
        self.assertNotIn("maintenance:duplicate", ids)
        self.assertEqual(len([item for item in view["selected"] if item["lane"] == "maintenance"]), 2)
        self.assertIn({"task_id": "maintenance:duplicate", "reason": "CLAIMED_RESOURCE"}, view["blocked"])
        self.assertEqual(len({key for item in view["selected"] for key in item["resources"]}),
                         sum(len(item["resources"]) for item in view["selected"]))

    def test_batch_size_partial_fill_and_no_work(self):
        only = task("maintenance:only")
        source = {"schema_version": 1, "events": []}
        view = mod.plan_batch(manifest(only), source, size=5, now=NOW)
        self.assertEqual((view["selected_count"], view["requested_count"], view["fill"]),
                         (1, 5, "PARTIAL"))
        self.assertEqual(source["events"], [])
        self.assertEqual(mod.plan_batch(manifest(), source, now=NOW)["status"],
                         "NO_VERIFIED_ELIGIBLE_WORK")
        for bad in (0, 11, -1, True, 1.5):
            with self.subTest(size=bad), self.assertRaisesRegex(mod.AutoError, "Batch size"):
                mod.plan_batch(manifest(only), source, size=bad, now=NOW)

    def test_batch_atomic_claim_release_and_resume(self):
        first = task("portfolio:111", lane="portfolio", repo="opensiro/upstream", pr_number=111)
        second = task("portfolio:55", lane="portfolio", repo="opensiro/upstream", pr_number=55)
        inp = manifest(first, second)
        with tempfile.TemporaryDirectory() as temp:
            one, two = make_fixture(Path(temp))
            before, _ = mod.fetch_ledger(one, "origin")
            receipt = mod.claim_batch(one, "origin", inp, "agent-batch", size=5,
                                      workers=["worker-one", "worker-two"],
                                      write=True, reader=FakeReader(), now=NOW)
            self.assertEqual(receipt["status"], "WRITTEN_CAS")
            self.assertEqual(receipt["fill"], "PARTIAL")
            self.assertEqual(receipt["selected_count"], 2)
            self.assertFalse(receipt["work_executed"])
            self.assertFalse(receipt["external_writes_authorized"])
            self.assertEqual(git(one, "rev-parse", receipt["claim_commit"] + "^"), before)
            _, ledger = mod.fetch_ledger(two, "origin")
            self.assertEqual(len(ledger["events"]), 2)
            self.assertEqual({ev["batch_id"] for ev in ledger["events"]}, {receipt["batch_id"]})
            ongoing = [*mod.resume(two, "origin", "worker-one", now=NOW)["claims"],
                       *mod.resume(two, "origin", "worker-two", now=NOW)["claims"]]
            self.assertEqual(len(ongoing), 2)
            self.assertEqual({entry["batch_id"] for entry in ongoing}, {receipt["batch_id"]})
            self.assertEqual({entry["coordinator"] for entry in ongoing}, {"agent-batch"})
            self.assertEqual({entry["actor"] for entry in receipt["claims"]},
                             {"worker-one", "worker-two"})
            self.assertEqual(mod.resume(two, "origin", "agent-batch", now=NOW)["claims"], [])
            with self.assertRaisesRegex(mod.AutoError, "NO_VERIFIED_ELIGIBLE_WORK"):
                mod.claim_batch(two, "origin", inp, "another-agent", write=True,
                                reader=FakeReader(), now=NOW)
            with self.assertRaisesRegex(mod.AutoError, "only original actor"):
                mod.release(two, "origin", receipt["claims"][0]["claim_id"], "agent-batch",
                            "First PR review recorded to owner issue", first["evidence_url"], now=NOW)
            mod.release(two, "origin", receipt["claims"][0]["claim_id"], "worker-one",
                        "First PR review recorded to owner issue", first["evidence_url"],
                        write=True, now=NOW)
            _, after = mod.fetch_ledger(one, "origin")
            self.assertEqual(len(mod.replay(after)), 1)
            self.assertEqual(next(iter(mod.replay(after).values()))["batch_id"], receipt["batch_id"])

    def test_batch_coordinator_and_worker_roster_cannot_be_tampered(self):
        event = {"action": "CLAIM", "claim_id": "a" * 32, "batch_id": "b" * 32,
                 "coordinator": "agent-batch", "task_id": "maintenance:one",
                 "actor": "worker-one", "resources": ["pr:example/repo#4"],
                 "owner_issue": 125, "operation": "READ_ONLY_REVIEW",
                 "evidence_url": "https://github.com/example/repo/pull/4",
                 "timestamp": stamp(NOW)}
        release = {**event, "action": "RELEASE", "reason": "Owner confirmed worker handoff"}
        self.assertEqual(mod.replay({"schema_version": 1, "events": [event, release]}), {})
        with self.assertRaisesRegex(mod.AutoError, "Release requires active original"):
            mod.replay({"schema_version": 1, "events": [event,
                       {**release, "coordinator": "other-agent"}]})
        with self.assertRaisesRegex(mod.AutoError, "Malformed batch coordinator"):
            mod.replay({"schema_version": 1, "events": [{**event, "coordinator": "bad value"}]})
        with tempfile.TemporaryDirectory() as temp:
            one, _ = make_fixture(Path(temp))
            with self.assertRaisesRegex(mod.AutoError, "Worker roster"):
                mod.claim_batch(one, "origin", manifest(task("maintenance:one")),
                                "agent-batch", workers=["same", "same"], now=NOW)

    def test_batch_preflight_failure_never_leaves_partial_claims(self):
        first = task("portfolio:111", lane="portfolio", repo="opensiro/upstream", pr_number=111)
        second = task("portfolio:55", lane="portfolio", repo="opensiro/upstream", pr_number=55)

        class SecondHeadMoved(FakeReader):
            def get(self, path):
                data = super().get(path)
                if path.endswith("/pulls/55"):
                    data["head"]["sha"] = "f" * 40
                return data

        with tempfile.TemporaryDirectory() as temp:
            one, _ = make_fixture(Path(temp))
            before, _ = mod.fetch_ledger(one, "origin")
            with self.assertRaisesRegex(mod.AutoError, "BLOCKED_PR_HEAD_CHANGED"):
                mod.claim_batch(one, "origin", manifest(first, second), "agent-batch",
                                write=True, reader=SecondHeadMoved(), now=NOW)
            after, ledger = mod.fetch_ledger(one, "origin")
            self.assertEqual(before, after)
            self.assertEqual(ledger["events"], [])

    def test_batch_cas_race_one_winner_and_replan(self):
        first = task("portfolio:111", lane="portfolio", repo="opensiro/upstream", pr_number=111)
        second = task("portfolio:55", lane="portfolio", repo="opensiro/upstream", pr_number=55)
        with tempfile.TemporaryDirectory() as temp:
            one, two = make_fixture(Path(temp))
            stale = mod.fetch_ledger(two, "origin")
            own = mod.claim_batch(one, "origin", manifest(first), "first-agent", size=1,
                                  write=True, reader=FakeReader(), now=NOW)
            self.assertEqual(own["selected_count"], 1)
            with patch.object(mod, "fetch_ledger", return_value=stale):
                with self.assertRaisesRegex(mod.AutoError, "BLOCKED_CONCURRENT_RESERVATION"):
                    mod.claim_batch(two, "origin", manifest(first, second), "second-agent",
                                    write=True, reader=FakeReader(), now=NOW)
            fresh = mod.claim_batch(two, "origin", manifest(first, second), "second-agent",
                                    write=True, reader=FakeReader(), now=NOW)
            self.assertEqual([item["task_id"] for item in fresh["claims"]], [second["task_id"]])
            self.assertEqual(len(mod.replay(mod.fetch_ledger(one, "origin")[1])), 2)

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
        self.assertEqual(mod.validate_manifest(manifest(item), now=NOW)[0]["resources"],
                         ["pr:example/repo#4"])
        item["resources"] = ["source:example/repo", "pr:example/repo#4"]
        with self.assertRaisesRegex(mod.AutoError, "READ_ONLY_REVIEW PR"):
            mod.validate_manifest(manifest(item), now=NOW)
        item["operation"] = "INTERNAL_PREPARE"
        self.assertEqual(mod.validate_manifest(manifest(item), now=NOW)[0]["operation"],
                         "INTERNAL_PREPARE")
        item["resources"] = ["pr:example/repo#4"]
        with self.assertRaisesRegex(mod.AutoError, "requires source locks"):
            mod.validate_manifest(manifest(item), now=NOW)
        item["resources"] = ["source:EXAMPLE/REPO", "source:example/repo", "pr:example/repo#4"]
        with self.assertRaisesRegex(mod.AutoError, "duplicate resource key"):
            mod.validate_manifest(manifest(item), now=NOW)

    def test_independent_portfolio_pr_reviews_do_not_take_repo_wide_lock(self):
        pr111 = task("portfolio:111", lane="portfolio", repo="opensiro/upstream", pr_number=111)
        pr55 = task("portfolio:55", lane="portfolio", repo="opensiro/upstream", pr_number=55)
        worklist = manifest(pr111, pr55)
        self.assertEqual(mod.validate_manifest(worklist, now=NOW)[0]["resources"],
                         ["pr:opensiro/upstream#111"])
        with tempfile.TemporaryDirectory() as temp:
            one, two = make_fixture(Path(temp))
            first = mod.claim(one, "origin", worklist, "agent-one", task_id=pr111["task_id"],
                              write=True, reader=FakeReader(), now=NOW)
            self.assertEqual(first["status"], "WRITTEN_CAS")
            view = mod.plan(worklist, mod.fetch_ledger(two, "origin")[1], now=NOW)
            self.assertEqual(view["selected"]["task_id"], pr55["task_id"])
            duplicate = copy.deepcopy(pr111)
            duplicate["task_id"] = "portfolio:duplicate111"
            self.assertIn({"task_id": duplicate["task_id"], "reason": "CLAIMED_RESOURCE"},
                          mod.plan(manifest(duplicate), mod.fetch_ledger(two, "origin")[1],
                                   now=NOW)["blocked"])
            second = mod.claim(two, "origin", worklist, "agent-two", task_id=pr55["task_id"],
                               write=True, reader=FakeReader(), now=NOW)
            self.assertEqual(second["status"], "WRITTEN_CAS")
            active = mod.replay(mod.fetch_ledger(one, "origin")[1])
            self.assertEqual(len(active), 2)
            self.assertEqual({e["operation"] for e in active.values()}, {"READ_ONLY_REVIEW"})
            third = task("portfolio:third", lane="portfolio", repo="other/repo")
            third_view = mod.plan(manifest(third), mod.fetch_ledger(one, "origin")[1], now=NOW)
            self.assertIn({"task_id": third["task_id"], "reason": "PORTFOLIO_OPERATION_WIP_CAP"},
                          third_view["blocked"])

    def test_overlapping_mutable_portfolio_pr_tasks_remain_serial(self):
        first = task("portfolio:write111", lane="portfolio", repo="opensiro/upstream",
                     pr_number=111, operation="INTERNAL_PREPARE")
        second = task("portfolio:write55", lane="portfolio", repo="opensiro/upstream",
                      pr_number=55, operation="INTERNAL_PREPARE")
        active = {"schema_version": 1, "events": [{"action": "CLAIM", "claim_id": "a" * 32,
                  "task_id": first["task_id"], "actor": "agent-one", "resources": sorted(first["resources"]),
                  "owner_issue": 150, "evidence_url": first["evidence_url"],
                  "operation": "INTERNAL_PREPARE", "timestamp": stamp(NOW)}]}
        view = mod.plan(manifest(first, second), active, now=NOW)
        self.assertIn({"task_id": second["task_id"], "reason": "CLAIMED_RESOURCE"}, view["blocked"])
        distinct = task("portfolio:write-other", lane="portfolio", repo="other/repo",
                        operation="INTERNAL_PREPARE")
        view = mod.plan(manifest(distinct), active, now=NOW)
        self.assertIn({"task_id": distinct["task_id"], "reason": "PORTFOLIO_OPERATION_WIP_CAP"},
                      view["blocked"])

    def test_legacy_portfolio_claim_is_conservative_and_release_replays(self):
        old = task("portfolio:old111", lane="portfolio", repo="opensiro/upstream", pr_number=111)
        historical = {"action": "CLAIM", "claim_id": "a" * 32,
                      "task_id": old["task_id"], "actor": "agent-one",
                      "resources": ["pr:opensiro/upstream#111", "source:opensiro/upstream"],
                      "owner_issue": 150, "evidence_url": old["evidence_url"],
                      "timestamp": stamp(NOW)}
        remaining = task("portfolio:review55", lane="portfolio", repo="opensiro/upstream",
                         pr_number=55)
        write = task("portfolio:write55", lane="portfolio", repo="opensiro/upstream",
                     pr_number=55, operation="INTERNAL_PREPARE")
        ledger = {"schema_version": 1, "events": [historical]}
        view = mod.plan(manifest(remaining, write), ledger, now=NOW)
        self.assertEqual(view["selected"]["task_id"], remaining["task_id"])
        self.assertIn({"task_id": write["task_id"], "reason": "CLAIMED_RESOURCE"}, view["blocked"])
        other_write = task("portfolio:write-other", lane="portfolio", repo="other/repo",
                           operation="INTERNAL_PREPARE")
        other_view = mod.plan(manifest(other_write), ledger, now=NOW)
        self.assertIn({"task_id": other_write["task_id"],
                       "reason": "PORTFOLIO_OPERATION_WIP_CAP"}, other_view["blocked"])
        released = {**historical, "action": "RELEASE", "timestamp": stamp(NOW),
                    "reason": "Legacy review handoff recorded to owner"}
        self.assertEqual(mod.replay({"schema_version": 1, "events": [historical, released]}), {})

    def test_new_claim_operation_is_attributable_and_cannot_change_on_release(self):
        item = task("portfolio:new", lane="portfolio", repo="opensiro/upstream", pr_number=111)
        event = {"action": "CLAIM", "claim_id": "a" * 32, "task_id": item["task_id"],
                 "actor": "agent-one", "resources": item["resources"],
                 "owner_issue": 150, "evidence_url": item["evidence_url"],
                 "operation": "READ_ONLY_REVIEW", "timestamp": stamp(NOW)}
        release = {**event, "action": "RELEASE", "reason": "Attributable complete owner handoff"}
        self.assertEqual(mod.replay({"schema_version": 1, "events": [event, release]}), {})
        tampered = {**release, "operation": "INTERNAL_PREPARE"}
        with self.assertRaisesRegex(mod.AutoError, "Release requires active original"):
            mod.replay({"schema_version": 1, "events": [event, tampered]})
        malformed = {**event, "operation": ["READ_ONLY_REVIEW"]}
        with self.assertRaisesRegex(mod.AutoError, "Unknown task claim operation"):
            mod.replay({"schema_version": 1, "events": [malformed]})

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
        mutable = task("portfolio:prepare", lane="portfolio", operation="INTERNAL_PREPARE")
        self.assertEqual(mod.live_preflight(manifest(mutable), mutable, FakeReader())
                         ["pr_base_shas"]["example/repo#4"], SHA)

        class MissingBase(FakeReader):
            def get(self, path):
                data = super().get(path)
                if path.endswith("/pulls/4"):
                    data.pop("base", None)
                return data

        with self.assertRaisesRegex(mod.AutoError, "BLOCKED_PR_BASE_VISIBILITY"):
            mod.live_preflight(manifest(mutable), mutable, MissingBase())

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
