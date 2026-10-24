"""Offline deterministic tests for Upstream's bounded PR maintenance watcher."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("pr_watch", ROOT / "scripts/pr_maintenance_watch.py")
watch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(watch)

URL = "https://github.com/Example/project/pull/3"


def pr():
    return {"url": URL, "repository": "Example/project", "number": 3,
            "state": "open", "draft": False, "merged_at": None,
            "head": "a" * 40, "base": "b" * 40, "updated_at": "2026-10-24T09:00:00Z",
            "mergeable": True, "mergeable_state": "clean",
            "comments": [], "reviews": [], "inline": [], "checks": [], "legacy_status": "pending"}


def snap(item=None):
    x = item or pr()
    return {"schema_version": 1, "observed_at": "2026-10-24T10:00:00Z", "prs": {URL: x}}


def review(id=17, state="CHANGES_REQUESTED", author="upstream-maintainer"):
    return {"id": id, "state": state, "author": author,
            "url": URL + "#pullrequestreview-" + str(id), "submitted_at": "2026-10-24T11:00:00Z"}


def comment(id=12, author="upstream-maintainer"):
    return {"id": id, "author": author, "url": URL + "#issuecomment-" + str(id),
            "updated_at": "2026-10-24T11:00:00Z", "created_at": "2026-10-24T11:00:00Z"}


def check(id=77, conclusion="failure"):
    return {"id": id, "name": "native", "status": "completed", "conclusion": conclusion,
            "completed_at": "2026-10-24T11:00:00Z",
            "url": URL + "/checks/" + str(id)}


class MockAPI:
    """Simulate actual GitHub issue-comment checkpoint behavior; no network."""
    def __init__(self):
        self.issue_comments = []
        self.writes = []
        self.broken_checkpoint_once = False
        self.external = None

    def get(self, path):
        if path == "/repos/opensiro/upstream/issues/125":
            return {"state": "open"}
        if self.external is not None:
            if path.endswith("/pulls/3"):
                return self.external["pr"]
            if "/check-runs?" in path:
                return {"total_count": len(self.external.get("checks", [])),
                        "check_runs": self.external.get("checks", [])}
            if path.endswith("/status"):
                return {"state": self.external.get("legacy", "pending")}
        raise AssertionError("Unexpected GET: " + path)

    def pages(self, path):
        if path == "/repos/opensiro/upstream/issues/125/comments?per_page=100":
            return self.issue_comments
        if self.external is not None:
            if path.endswith("/issues/3/comments?per_page=100"):
                return self.external.get("comments", [])
            if path.endswith("/pulls/3/reviews?per_page=100"):
                return self.external.get("reviews", [])
            if path.endswith("/pulls/3/comments?per_page=100"):
                return self.external.get("inline", [])
        raise AssertionError("Unexpected paginated GET: " + path)

    def request(self, path, method="GET", payload=None):
        assert method in ("PATCH", "POST"), "Only issue notifications may be written"
        assert (path == "/repos/opensiro/upstream/issues/125/comments" or
                path.startswith("/repos/opensiro/upstream/issues/comments/")), "No external GitHub mutation is permitted"
        if self.broken_checkpoint_once and method == "PATCH" and watch.CHECKPOINT_PREFIX in payload["body"]:
            self.broken_checkpoint_once = False
            raise OSError("simulated failing checkpoint update")
        self.writes.append((path, method, payload))
        if method == "POST":
            cid = len(self.issue_comments) + 1
            self.issue_comments.append({"id": cid, "body": payload["body"],
                                        "user": {"login": "github-actions[bot]"}})
            return {"id": cid}, ""
        cid = int(path.rsplit("/", 1)[1])
        for item in self.issue_comments:
            if item["id"] == cid:
                item["body"] = payload["body"]
                return item, ""
        raise AssertionError("checkpoint id unknown")


def source():
    return {"pr": {"number": 3, "html_url": URL, "state": "open", "draft": False,
                   "head": {"sha": "a" * 40}, "base": {"sha": "b" * 40},
                   "merged_at": None, "updated_at": "2026-10-24T10:00:00Z",
                   "mergeable": True, "mergeable_state": "clean"},
            "comments": [], "reviews": [], "inline": [], "checks": [], "legacy": "pending"}


class WatchTests(unittest.TestCase):
    def write_targets(self, root):
        p = Path(root) / "targets.json"
        p.write_text(json.dumps({"schema_version": 1,
                                "inbox_issue": "https://github.com/opensiro/upstream/issues/125",
                                "targets": [{"repository": "Example/project", "number": 3, "url": URL}]}))
        return p

    def test_exact_manifest_has_fifteen_targets_and_no_duplicates(self):
        data = watch.validate_targets()
        self.assertEqual(len(data["targets"]), 15)
        self.assertEqual(len({t["url"] for t in data["targets"]}), 15)
        self.assertIn("https://github.com/cbrock84/headcount/pull/47",
                      [t["url"] for t in data["targets"]])
        self.assertIn("https://github.com/chumingjun/dsh-harness-one/pull/173",
                      [t["url"] for t in data["targets"]])
        self.assertIn("https://github.com/Coral-Bricks-AI/reef/pull/19",
                      [t["url"] for t in data["targets"]])
        self.assertIn("https://github.com/CorticalComputer/Spartan/pull/1",
                      [t["url"] for t in data["targets"]])

    def test_reject_malformed_source_and_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.write_targets(tmp)
            item = json.loads(p.read_text())
            item["targets"].append(copy.deepcopy(item["targets"][0]))
            p.write_text(json.dumps(item))
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                watch.validate_targets(p)
            item["targets"] = item["targets"][:1]
            item["targets"][0]["url"] = "https://github.com/NotSource/other/pull/3"
            p.write_text(json.dumps(item))
            with self.assertRaisesRegex(ValueError, "does not match"):
                watch.validate_targets(p)

    def test_review_requested_and_reviewer_comment_are_actionable(self):
        newer = snap()
        newer["prs"][URL]["reviews"] = [review()]
        newer["prs"][URL]["comments"] = [comment()]
        newer["prs"][URL]["inline"] = [comment(19)]
        kinds = [e["kind"] for e in watch.classify(snap(), newer)]
        self.assertEqual(kinds, ["NEW_MAINTAINER_COMMENT", "NEW_REVIEW_COMMENT", "CHANGES_REQUESTED"])
        self.assertTrue(all(e["level"] == "action_required" for e in watch.classify(snap(), newer)))
        self.assertEqual(watch.classify(newer, newer), [])

    def test_ignore_own_and_bot_comments(self):
        x = snap()
        x["prs"][URL]["comments"] = [comment(21, "xLagerFeuer"), comment(22, "ci[bot]")]
        x["prs"][URL]["reviews"] = [review(17, author="xLagerFeuer")]
        self.assertEqual(watch.classify(snap(), x), [])

    def test_edited_maintainer_comment_and_inline_review_are_actionable_once(self):
        old = snap()
        old["prs"][URL]["comments"] = [comment(12)]
        old["prs"][URL]["inline"] = [comment(19)]
        new = copy.deepcopy(old)
        new["prs"][URL]["comments"][0]["updated_at"] = "2026-10-24T12:00:00Z"
        new["prs"][URL]["inline"][0]["updated_at"] = "2026-10-24T12:01:00Z"
        events = watch.classify(old, new)
        self.assertEqual([e["kind"] for e in events],
                         ["EDITED_MAINTAINER_COMMENT", "EDITED_REVIEW_COMMENT"])
        self.assertTrue(all(e["level"] == "action_required" for e in events))
        self.assertEqual(watch.classify(new, new), [])
        again = copy.deepcopy(new)
        again["prs"][URL]["comments"][0]["updated_at"] = "2026-10-24T12:02:00Z"
        self.assertNotEqual(watch.classify(old, new)[0]["key"],
                            watch.classify(new, again)[0]["key"])

    def test_edit_detection_ignores_own_comment_and_missing_old_timestamp(self):
        old = snap()
        old["prs"][URL]["comments"] = [comment(12, "xLagerFeuer"), comment(13)]
        old["prs"][URL]["comments"][1]["updated_at"] = None
        new = copy.deepcopy(old)
        for x in new["prs"][URL]["comments"]:
            x["updated_at"] = "2026-10-24T12:00:00Z"
        self.assertEqual(watch.classify(old, new), [])

    def test_status_and_checks_are_separate_from_review(self):
        a, b = snap(), snap()
        b["prs"][URL]["checks"] = [check()]
        b["prs"][URL]["legacy_status"] = "failure"
        self.assertEqual({e["kind"] for e in watch.classify(a, b)}, {"CI_FAILED", "CI_LEGACY_FAILED"})
        c = copy.deepcopy(b)
        c["prs"][URL]["checks"] = [check(88, "success")]
        c["prs"][URL]["legacy_status"] = "success"
        self.assertEqual(watch.classify(b, c), [])
        c["prs"][URL]["merged_at"] = "2026-10-24T11:00:00Z"
        c["prs"][URL]["state"] = "closed"
        self.assertEqual([e["kind"] for e in watch.classify(b, c)], ["MERGED"])

    def test_new_confirmed_merge_conflict_alerts_once_not_policy_block(self):
        old, new = snap(), snap()
        new["prs"][URL]["mergeable"] = False
        new["prs"][URL]["mergeable_state"] = "dirty"
        ev = watch.classify(old, new)
        self.assertEqual([e["kind"] for e in ev], ["MERGE_CONFLICT"])
        self.assertEqual(ev[0]["level"], "action_required")
        self.assertEqual(watch.classify(new, new), [])
        policy = copy.deepcopy(new)
        policy["prs"][URL]["mergeable_state"] = "blocked"
        self.assertEqual(watch.classify(old, policy), [])

    def test_mergeability_unknown_and_legacy_checkpoint_do_not_fake_new_conflict(self):
        new = snap()
        new["prs"][URL]["mergeable"] = False
        new["prs"][URL]["mergeable_state"] = "dirty"
        legacy = snap()
        del legacy["prs"][URL]["mergeable"]
        del legacy["prs"][URL]["mergeable_state"]
        self.assertEqual(watch.classify(legacy, new), [])
        unknown = snap()
        unknown["prs"][URL]["mergeable"] = None
        unknown["prs"][URL]["mergeable_state"] = "unknown"
        self.assertEqual(watch.classify(unknown, new), [])

    def test_unknown_api_observation_preserves_prior_settled_conflict_state(self):
        m = MockAPI()
        m.external = source()
        with tempfile.TemporaryDirectory() as tmp:
            p = self.write_targets(tmp)
            watch.run(m, p)
            m.external["pr"]["mergeable"] = None
            m.external["pr"]["mergeable_state"] = "unknown"
            self.assertEqual(watch.run(m, p), [])
            m.external["pr"]["mergeable"] = False
            m.external["pr"]["mergeable_state"] = "dirty"
            self.assertEqual([e["kind"] for e in watch.run(m, p)], ["MERGE_CONFLICT"])
            watch.run(m, p)
            self.assertEqual(sum(watch.ALERT_PREFIX in x[2]["body"] for x in m.writes), 1)

    def test_live_snapshot_rejects_malformed_mergeability(self):
        m = MockAPI()
        m.external = source()
        m.external["pr"]["mergeable"] = "false"
        with self.assertRaisesRegex(ValueError, "mergeability"):
            watch.snapshot_one(m, {"repository": "Example/project", "number": 3, "url": URL})

    def test_checkpoint_roundtrip_and_corruption_fail_closed(self):
        token = watch.encode_checkpoint(snap())
        self.assertEqual(watch.decode_checkpoint(token), snap())
        with self.assertRaises(ValueError):
            watch.decode_checkpoint("not a checkpoint")
        self.assertNotIn("Authorization", token)

    def test_first_run_is_baseline_and_repeat_is_idempotent(self):
        m = MockAPI()
        m.external = source()
        m.external["comments"] = [{"id": 1, "user": {"login": "upstream-maintainer"},
                                    "html_url": URL + "#issuecomment-1"}]
        with tempfile.TemporaryDirectory() as tmp:
            p = self.write_targets(tmp)
            self.assertEqual(watch.run(m, p), [])
            self.assertEqual(len(m.writes), 1)  # checkpoint only
            self.assertIn(watch.CHECKPOINT_PREFIX, m.writes[0][2]["body"])
            self.assertEqual(watch.run(m, p), [])
            self.assertEqual(len(m.writes), 1)  # no-op scan produces zero additional writes
            self.assertEqual(sum(watch.ALERT_PREFIX in r[2]["body"] for r in m.writes), 0)

    def test_reviewed_additive_checkpoint_migration_baselines_without_replay(self):
        m = MockAPI()
        m.external = source()
        extra_url = "https://github.com/chumingjun/dsh-harness-one/pull/173"
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_targets(tmp)
            watch.run(m, path)
            targets = json.loads(path.read_text())
            targets["targets"].append({"repository": "chumingjun/dsh-harness-one", "number": 173,
                                       "url": extra_url})
            path.write_text(json.dumps(targets))
            extra = pr()
            extra.update(url=extra_url, repository="chumingjun/dsh-harness-one", number=173)

            def snapshot(_, target):
                return extra if target["url"] == extra_url else pr()

            with patch.object(watch, "snapshot_one", side_effect=snapshot):
                self.assertEqual([e["kind"] for e in watch.run(m, path, probe_only=True)],
                                 ["NEW_TRACKED_PR"])
                self.assertEqual(len(m.writes), 1)  # probe is still read-only
                self.assertEqual([e["kind"] for e in watch.run(m, path)], ["NEW_TRACKED_PR"])
                self.assertEqual(len(m.writes), 2)  # checkpoint, no alert
                self.assertEqual(watch.run(m, path), [])
                self.assertEqual(len(m.writes), 2)
                extra["comments"] = [dict(comment(41), url=extra_url + "#issuecomment-41")]
                self.assertEqual([e["kind"] for e in watch.run(m, path)],
                                 ["NEW_MAINTAINER_COMMENT"])
                self.assertEqual(sum(watch.ALERT_PREFIX in x[2]["body"] for x in m.writes), 1)

                targets["targets"] = targets["targets"][:1]
                path.write_text(json.dumps(targets))
                before = len(m.writes)
                with self.assertRaisesRegex(ValueError, "baseline migration required"):
                    watch.run(m, path)
                self.assertEqual(len(m.writes), before)

                targets["targets"].append({"repository": "Other/repo", "number": 5,
                                           "url": "https://github.com/Other/repo/pull/5"})
                path.write_text(json.dumps(targets))
                with self.assertRaisesRegex(ValueError, "baseline migration required"):
                    watch.run(m, path)
                self.assertEqual(len(m.writes), before)

    def test_sequential_corrective_additions_preserve_checkpoint_without_alert(self):
        m = MockAPI()
        m.external = source()
        dsh = "https://github.com/chumingjun/dsh-harness-one/pull/173"
        reef = "https://github.com/Coral-Bricks-AI/reef/pull/19"
        spartan = "https://github.com/CorticalComputer/Spartan/pull/1"

        def fake_snapshot(_, target):
            item = pr()
            item.update(url=target["url"], repository=target["repository"],
                        number=target["number"], draft=target["url"] in {reef, spartan})
            return item

        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_targets(tmp)
            with patch.object(watch, "snapshot_one", side_effect=fake_snapshot):
                self.assertEqual(watch.run(m, path), [])
                targets = json.loads(path.read_text())
                targets["targets"].append({"repository": "chumingjun/dsh-harness-one",
                                           "number": 173, "url": dsh})
                path.write_text(json.dumps(targets))
                self.assertEqual([e["kind"] for e in watch.run(m, path)], ["NEW_TRACKED_PR"])
                targets["targets"].append({"repository": "Coral-Bricks-AI/reef",
                                           "number": 19, "url": reef})
                path.write_text(json.dumps(targets))
                self.assertEqual([e["kind"] for e in watch.run(m, path, probe_only=True)],
                                 ["NEW_TRACKED_PR"])
                self.assertEqual(len(m.writes), 2)
                self.assertEqual([e["kind"] for e in watch.run(m, path)], ["NEW_TRACKED_PR"])
                self.assertEqual(len(m.writes), 3)  # only checkpoint writes
                self.assertEqual(watch.run(m, path), [])
                self.assertEqual(len(m.writes), 3)
                targets["targets"].append({"repository": "CorticalComputer/Spartan",
                                           "number": 1, "url": spartan})
                path.write_text(json.dumps(targets))
                self.assertEqual([e["kind"] for e in watch.run(m, path, probe_only=True)],
                                 ["NEW_TRACKED_PR"])
                self.assertEqual(len(m.writes), 3)
                self.assertEqual([e["kind"] for e in watch.run(m, path)], ["NEW_TRACKED_PR"])
                self.assertEqual(len(m.writes), 4)
                self.assertEqual(watch.run(m, path), [])
                self.assertEqual(len(m.writes), 4)
                self.assertFalse(any(watch.ALERT_PREFIX in write[2]["body"] for write in m.writes))

    def test_actual_new_review_posts_one_alert_and_then_checkpoint(self):
        m = MockAPI()
        m.external = source()
        with tempfile.TemporaryDirectory() as tmp:
            p = self.write_targets(tmp)
            watch.run(m, p)
            m.external["reviews"] = [{"id": 25, "user": {"login": "upstream-maintainer"},
                                      "state": "CHANGES_REQUESTED", "html_url": URL + "#review-25",
                                      "submitted_at": "2026-10-24T12:00:00Z"}]
            events = watch.run(m, p)
            self.assertEqual([x["kind"] for x in events], ["CHANGES_REQUESTED"])
            self.assertEqual(m.writes[-2][1], "POST")
            self.assertIn(watch.ALERT_PREFIX, m.writes[-2][2]["body"])
            watch.run(m, p)
            self.assertEqual(sum(watch.ALERT_PREFIX in x[2]["body"] for x in m.writes), 1)

    def test_edited_comment_posts_once_per_actual_edit(self):
        m = MockAPI()
        m.external = source()
        m.external["comments"] = [{"id": 20, "user": {"login": "upstream-maintainer"},
                                   "html_url": URL + "#issuecomment-20",
                                   "created_at": "2026-10-24T10:00:00Z",
                                   "updated_at": "2026-10-24T10:00:00Z"}]
        with tempfile.TemporaryDirectory() as tmp:
            p = self.write_targets(tmp)
            watch.run(m, p)  # existing comment is historical baseline
            self.assertEqual(sum(watch.ALERT_PREFIX in x[2]["body"] for x in m.writes), 0)
            m.external["comments"][0]["updated_at"] = "2026-10-24T11:00:00Z"
            self.assertEqual([e["kind"] for e in watch.run(m, p)], ["EDITED_MAINTAINER_COMMENT"])
            watch.run(m, p)
            self.assertEqual(sum(watch.ALERT_PREFIX in x[2]["body"] for x in m.writes), 1)
            m.external["comments"][0]["updated_at"] = "2026-10-24T12:00:00Z"
            self.assertEqual([e["kind"] for e in watch.run(m, p)], ["EDITED_MAINTAINER_COMMENT"])
            self.assertEqual(sum(watch.ALERT_PREFIX in x[2]["body"] for x in m.writes), 2)

    def test_notification_retry_deduplicated_after_checkpoint_failure(self):
        m = MockAPI()
        m.external = source()
        with tempfile.TemporaryDirectory() as tmp:
            p = self.write_targets(tmp)
            watch.run(m, p)
            m.external["inline"] = [{"id": 37, "user": {"login": "upstream-maintainer"},
                                     "html_url": URL + "#review-comment-37"}]
            m.broken_checkpoint_once = True
            with self.assertRaises(OSError):
                watch.run(m, p)
            self.assertEqual(sum(watch.ALERT_PREFIX in x[2]["body"] for x in m.writes), 1)
            watch.run(m, p)
            self.assertEqual(sum(watch.ALERT_PREFIX in x[2]["body"] for x in m.writes), 1)

    def test_probe_only_reads_realistic_source_without_writes(self):
        m = MockAPI()
        m.external = source()
        with tempfile.TemporaryDirectory() as tmp:
            p = self.write_targets(tmp)
            self.assertEqual(watch.run(m, p, probe_only=True), [])
            self.assertEqual(m.writes, [])

    def test_merge_is_notified_once_without_automatic_merge(self):
        m = MockAPI()
        m.external = source()
        with tempfile.TemporaryDirectory() as tmp:
            p = self.write_targets(tmp)
            watch.run(m, p)
            m.external["pr"]["state"] = "closed"
            m.external["pr"]["merged_at"] = "2026-10-24T11:00:00Z"
            events = watch.run(m, p)
            self.assertEqual([e["kind"] for e in events], ["MERGED"])
            self.assertEqual(sum(watch.ALERT_PREFIX in x[2]["body"] for x in m.writes), 1)
            watch.run(m, p)
            self.assertEqual(sum(watch.ALERT_PREFIX in x[2]["body"] for x in m.writes), 1)

    def test_wrong_source_fails_before_any_write(self):
        m = MockAPI()
        m.external = source()
        m.external["pr"]["html_url"] = "https://github.com/impostor/wrong/pull/3"
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "identity mismatch"):
                watch.run(m, self.write_targets(tmp))
        self.assertFalse(m.writes)

    def test_checkpoint_never_leaks_token(self):
        with self.assertRaisesRegex(ValueError, "GITHUB_TOKEN required"):
            watch.Github("")


if __name__ == "__main__":
    unittest.main()
