"""Offline deterministic tests for Upstream's bounded PR maintenance watcher."""
import copy
from contextlib import redirect_stdout
from http.client import RemoteDisconnected
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

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
    def test_github_compare_route_accepts_only_exact_immutable_sha_pairs(self):
        left, right = "a" * 40, "b" * 40
        path = f"/repos/opensiro/upstream/compare/{left}...{right}"
        response = io.BytesIO(b'{"status":"ahead"}')
        response.headers = {}
        with patch.object(watch, "urlopen", return_value=response) as opener:
            self.assertEqual(watch.Github("test-token").get(path), {"status": "ahead"})
            self.assertEqual(opener.call_count, 1)
            self.assertEqual(opener.call_args.args[0].full_url,
                             "https://api.github.com" + path)

        unsafe = (
            "/repos/opensiro/upstream/../secrets",
            f"/repos/../upstream/compare/{left}...{right}",
            f"/repos/opensiro/../compare/{left}...{right}",
            f"/repos/opensiro/upstream/compare/{left}...{right}/../secrets",
            f"/repos/opensiro/upstream/compare/{left}...main",
            f"/repos/opensiro/upstream/compare/{left}...{right}/extra",
            "/repos/opensiro//upstream/issues/1",
        )
        with patch.object(watch, "urlopen") as opener:
            for candidate in unsafe:
                with self.subTest(candidate=candidate):
                    with self.assertRaisesRegex(ValueError, "Unsafe API path"):
                        watch.Github("test-token").get(candidate)
            opener.assert_not_called()

    def write_targets(self, root):
        p = Path(root) / "targets.json"
        p.write_text(json.dumps({"schema_version": 1,
                                "inbox_issue": "https://github.com/opensiro/upstream/issues/125",
                                "targets": [{"repository": "Example/project", "number": 3, "url": URL}]}))
        return p

    def test_exact_manifest_has_twenty_seven_targets_and_no_duplicates(self):
        data = watch.validate_targets()
        self.assertEqual(len(data["targets"]), 27)
        self.assertEqual(len({t["url"] for t in data["targets"]}), 27)
        self.assertIn("https://github.com/knowflow-ai/KnowWork/pull/4",
                      {t["url"] for t in data["targets"]})
        self.assertIn("https://github.com/knowflow-ai/KnowWork/pull/4",
                      watch.APPROVED_CHECKPOINT_ADDITIONS)
        self.assertIn("https://github.com/murilo-bassan/durable-agent-runtime/pull/1",
                      {t["url"] for t in data["targets"]})
        self.assertIn("https://github.com/murilo-bassan/durable-agent-runtime/pull/1",
                      watch.APPROVED_CHECKPOINT_ADDITIONS)
        self.assertIn("https://github.com/cbrock84/headcount/pull/47",
                      [t["url"] for t in data["targets"]])
        self.assertIn("https://github.com/chumingjun/dsh-harness-one/pull/173",
                      [t["url"] for t in data["targets"]])
        self.assertIn("https://github.com/Coral-Bricks-AI/reef/pull/19",
                      [t["url"] for t in data["targets"]])
        self.assertIn("https://github.com/CorticalComputer/Spartan/pull/1",
                      [t["url"] for t in data["targets"]])
        self.assertIn("https://github.com/BESSER-PEARL/BESSER-Agentic-Framework/pull/205",
                      [t["url"] for t in data["targets"]])
        self.assertIn("https://github.com/mila-iqia/babyai/pull/128",
                      [t["url"] for t in data["targets"]])
        self.assertIn("https://github.com/Phoenixrr2113/agent-harness/pull/1",
                      [t["url"] for t in data["targets"]])
        for url in (
            "https://github.com/0xNyk/lacp/pull/128",
            "https://github.com/chekusu/wanman/pull/38",
            "https://github.com/gczhuang-cmd/NovaCode/pull/1",
            "https://github.com/mnbresearch/crewdeck/pull/1",
            "https://github.com/ruslantrachuk/dark-factory/pull/106",
            "https://github.com/splashxmoon/friday/pull/23",
            "https://github.com/talktorana/agent-harness/pull/1",
        ):
            self.assertIn(url, [t["url"] for t in data["targets"]])
        exceptions = [t for t in data["targets"] if t.get("monitoring")]
        self.assertEqual(exceptions, [{"repository": "cbrock84/headcount", "number": 47,
                                      "url": watch.KNOWN_404_SOURCE,
                                      "monitoring": watch.KNOWN_404_MODE}])

    def test_availability_only_scope_rejects_unreviewed_target_and_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_targets(tmp)
            data = json.loads(path.read_text())
            data["targets"][0]["monitoring"] = watch.KNOWN_404_MODE
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "Unreviewed source-availability"):
                watch.validate_targets(path)
            data["targets"][0]["url"] = watch.KNOWN_404_SOURCE
            data["targets"][0]["repository"] = "cbrock84/headcount"
            data["targets"][0]["number"] = 47
            data["targets"][0]["monitoring"] = "ignore_all_errors"
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "Unreviewed source-availability"):
                watch.validate_targets(path)

    def test_exact_known_404_is_reported_but_other_PR_events_continue(self):
        class AvailabilityAPI(MockAPI):
            restored = False

            def get(self, path):
                if path == "/repos/cbrock84/headcount/pulls/47":
                    if self.restored:
                        return {"html_url": watch.KNOWN_404_SOURCE, "number": 47,
                                "state": "open"}
                    raise HTTPError("https://api.github.com" + path, 404, "Not Found", {}, None)
                return super().get(path)

        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_targets(tmp)
            data = json.loads(path.read_text())
            data["targets"].append({"repository": "cbrock84/headcount", "number": 47,
                                    "url": watch.KNOWN_404_SOURCE,
                                    "monitoring": watch.KNOWN_404_MODE})
            path.write_text(json.dumps(data))
            api = AvailabilityAPI()
            api.external = source()
            prior = snap()
            # This preexisting accessible Headcount entry is historical evidence;
            # it must never become a fabricated lifecycle transition on 404.
            prior["prs"][watch.KNOWN_404_SOURCE] = {**pr(),
                "url": watch.KNOWN_404_SOURCE, "repository": "cbrock84/headcount",
                "number": 47}
            api.issue_comments = [{"id": 1, "body": watch.encode_checkpoint(prior),
                                   "user": {"login": "github-actions[bot]"}}]
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual([e["kind"] for e in watch.run(api, path, probe_only=True)],
                                 ["SOURCE_UNVERIFIABLE"])
            self.assertIn("Scanned **1** accessible", out.getvalue())
            self.assertIn("**1** explicitly UNVERIFIABLE", out.getvalue())
            self.assertEqual(api.writes, [])

            self.assertEqual([e["kind"] for e in watch.run(api, path)],
                             ["SOURCE_UNVERIFIABLE"])
            self.assertEqual(len(api.writes), 2)  # one alert, then checkpoint
            current = watch.decode_checkpoint(api.issue_comments[0]["body"])
            self.assertEqual(current["prs"][watch.KNOWN_404_SOURCE]["reason"], "HTTP_404")
            self.assertNotIn("state", current["prs"][watch.KNOWN_404_SOURCE])
            self.assertEqual(watch.run(api, path), [])
            self.assertEqual(len(api.writes), 2)

            # An unrelated real maintainer comment still produces a real alert.
            api.external["comments"] = [{"id": 72, "user": {"login": "maintainer"},
                                          "html_url": URL + "#issuecomment-72",
                                          "created_at": "2026-11-05T00:00:00Z",
                                          "updated_at": "2026-11-05T00:00:00Z"}]
            self.assertEqual([e["kind"] for e in watch.run(api, path)],
                             ["NEW_MAINTAINER_COMMENT"])
            self.assertEqual(len(api.writes), 4)

            # Exact source availability recovery is not silently accepted;
            # the reviewed waiver must be removed before resuming monitoring.
            api.restored = True
            with self.assertRaisesRegex(ValueError, "became accessible"):
                watch.run(api, path)
            self.assertEqual(len(api.writes), 4)

    def test_ordinary_404_still_fails_before_any_checkpoint_write(self):
        class LostAPI(MockAPI):
            def get(self, path):
                if path == "/repos/Example/project/pulls/3":
                    raise HTTPError("https://api.github.com" + path, 404, "Not Found", {}, None)
                return super().get(path)

        with tempfile.TemporaryDirectory() as tmp:
            api = LostAPI()
            api.external = source()
            with self.assertRaises(HTTPError):
                watch.run(api, self.write_targets(tmp))
            self.assertEqual(api.writes, [])

    def test_source_restored_is_not_misclassified_as_a_new_lifecycle_event(self):
        before = snap({"url": URL, "repository": "Example/project", "number": 3,
                       "availability": "unverifiable", "reason": "HTTP_404"})
        self.assertEqual([e["kind"] for e in watch.classify(before, snap())],
                         ["SOURCE_RESTORED"])

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

    def test_check_conclusions_have_distinct_meaning_and_no_replay(self):
        cases = [
            ("failure", "CI_FAILED", "action_required"),
            ("timed_out", "CI_TIMED_OUT", "action_required"),
            ("action_required", "CI_ACTION_REQUIRED", "action_required"),
            ("cancelled", "CI_CANCELLED", "info"),
        ]
        for conclusion, kind, level in cases:
            with self.subTest(conclusion=conclusion):
                before, after = snap(), snap()
                after["prs"][URL]["checks"] = [check(conclusion=conclusion)]
                events = watch.classify(before, after)
                self.assertEqual([(e["kind"], e["level"]) for e in events], [(kind, level)])
                self.assertEqual(watch.classify(after, after), [])
        old = snap()
        old["prs"][URL]["checks"] = [check(conclusion="failure")]
        new = copy.deepcopy(old)
        new["prs"][URL]["checks"] = [check(conclusion="action_required")]
        self.assertEqual([e["kind"] for e in watch.classify(old, new)], ["CI_ACTION_REQUIRED"])

    def test_cancelled_check_is_checkpointed_but_not_alerted(self):
        api = MockAPI()
        api.external = source()
        with tempfile.TemporaryDirectory() as tmp:
            target_path = self.write_targets(tmp)
            watch.run(api, target_path)
            api.external["checks"] = [{
                "id": 77, "name": "native", "status": "completed",
                "conclusion": "cancelled", "html_url": URL + "/checks/77",
                "completed_at": "2026-10-24T11:00:00Z",
            }]
            self.assertEqual([e["kind"] for e in watch.run(api, target_path)], ["CI_CANCELLED"])
            self.assertFalse(any(watch.ALERT_PREFIX in w[2]["body"] for w in api.writes))
            self.assertEqual(watch.run(api, target_path), [])
            api.external["checks"][0]["conclusion"] = "action_required"
            self.assertEqual([e["kind"] for e in watch.run(api, target_path)],
                             ["CI_ACTION_REQUIRED"])
            self.assertEqual(sum(watch.ALERT_PREFIX in w[2]["body"] for w in api.writes), 1)

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
        besser = "https://github.com/BESSER-PEARL/BESSER-Agentic-Framework/pull/205"
        babyai = "https://github.com/mila-iqia/babyai/pull/128"
        phoenix = "https://github.com/Phoenixrr2113/agent-harness/pull/1"

        def fake_snapshot(_, target):
            item = pr()
            item.update(url=target["url"], repository=target["repository"],
                        number=target["number"], draft=False)
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
                targets["targets"].append({"repository": "BESSER-PEARL/BESSER-Agentic-Framework",
                                           "number": 205, "url": besser})
                path.write_text(json.dumps(targets))
                self.assertEqual([e["kind"] for e in watch.run(m, path, probe_only=True)],
                                 ["NEW_TRACKED_PR"])
                self.assertEqual(len(m.writes), 4)
                self.assertEqual([e["kind"] for e in watch.run(m, path)], ["NEW_TRACKED_PR"])
                self.assertEqual(len(m.writes), 5)
                self.assertEqual(watch.run(m, path), [])
                self.assertEqual(len(m.writes), 5)
                targets["targets"].append({"repository": "mila-iqia/babyai",
                                           "number": 128, "url": babyai})
                path.write_text(json.dumps(targets))
                self.assertEqual([e["kind"] for e in watch.run(m, path, probe_only=True)],
                                 ["NEW_TRACKED_PR"])
                self.assertEqual(len(m.writes), 5)
                self.assertEqual([e["kind"] for e in watch.run(m, path)], ["NEW_TRACKED_PR"])
                self.assertEqual(len(m.writes), 6)
                self.assertEqual(watch.run(m, path), [])
                self.assertEqual(len(m.writes), 6)
                targets["targets"].append({"repository": "Phoenixrr2113/agent-harness",
                                           "number": 1, "url": phoenix})
                path.write_text(json.dumps(targets))
                self.assertEqual([e["kind"] for e in watch.run(m, path, probe_only=True)],
                                 ["NEW_TRACKED_PR"])
                self.assertEqual(len(m.writes), 6)
                self.assertEqual([e["kind"] for e in watch.run(m, path)], ["NEW_TRACKED_PR"])
                self.assertEqual(len(m.writes), 7)
                self.assertEqual(watch.run(m, path), [])
                self.assertEqual(len(m.writes), 7)
                self.assertFalse(any(watch.ALERT_PREFIX in write[2]["body"] for write in m.writes))

    def test_seven_2026_11_10_publications_migrate_without_replaying_history(self):
        additions = [
            ("chekusu/wanman", 38),
            ("0xNyk/lacp", 128),
            ("splashxmoon/friday", 23),
            ("mnbresearch/crewdeck", 1),
            ("talktorana/agent-harness", 1),
            ("ruslantrachuk/dark-factory", 106),
            ("gczhuang-cmd/NovaCode", 1),
        ]
        m = MockAPI()
        m.external = source()

        def fake_snapshot(_, target):
            item = pr()
            item.update(url=target["url"], repository=target["repository"],
                        number=target["number"], draft=False)
            return item

        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_targets(tmp)
            with patch.object(watch, "snapshot_one", side_effect=fake_snapshot):
                self.assertEqual(watch.run(m, path), [])
                original_checkpoint = watch.decode_checkpoint(m.issue_comments[0]["body"])
                data = json.loads(path.read_text())
                for repository, number in additions:
                    data["targets"].append({
                        "repository": repository, "number": number,
                        "url": f"https://github.com/{repository}/pull/{number}"})
                path.write_text(json.dumps(data))
                probe = watch.run(m, path, probe_only=True)
                self.assertEqual([e["kind"] for e in probe], ["NEW_TRACKED_PR"] * 7)
                self.assertEqual(len(m.writes), 1)
                self.assertEqual([e["kind"] for e in watch.run(m, path)],
                                 ["NEW_TRACKED_PR"] * 7)
                self.assertEqual(len(m.writes), 2)  # checkpoint only; no alerts
                new_checkpoint = watch.decode_checkpoint(m.issue_comments[0]["body"])
                self.assertEqual(new_checkpoint["prs"][URL], original_checkpoint["prs"][URL])
                self.assertEqual(len(new_checkpoint["prs"]), 8)
                self.assertFalse(any(watch.ALERT_PREFIX in x[2]["body"] for x in m.writes))
                self.assertEqual(watch.run(m, path), [])
                self.assertEqual(len(m.writes), 2)

                data["targets"].append({"repository": "Unreviewed/source", "number": 5,
                                        "url": "https://github.com/Unreviewed/source/pull/5"})
                path.write_text(json.dumps(data))
                with self.assertRaisesRegex(ValueError, "baseline migration required"):
                    watch.run(m, path)
                self.assertEqual(len(m.writes), 2)

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

    def test_transient_get_retries_but_never_retries_write(self):
        class Response(io.BytesIO):
            headers = {"Link": ""}

        api = watch.Github("dummy-test-token")
        response = Response(b'{"state":"open"}')
        with patch.object(watch, "urlopen", side_effect=[RemoteDisconnected("closed"), response]) as remote, \
             patch.object(watch.time, "sleep") as delay:
            self.assertEqual({"state": "open"}, api.get("/repos/example/x/pulls/1"))
            self.assertEqual(2, remote.call_count)
            delay.assert_called_once()

        with patch.object(watch, "urlopen", side_effect=RemoteDisconnected("lost response")) as remote, \
             patch.object(watch.time, "sleep") as delay:
            with self.assertRaises(RemoteDisconnected):
                api.request("/repos/opensiro/upstream/issues/125/comments", method="POST", payload={"body": "test"})
            self.assertEqual(1, remote.call_count)
            delay.assert_not_called()

    def test_404_stays_fail_closed_and_is_not_retried(self):
        api = watch.Github("dummy-test-token")
        with patch.object(watch, "urlopen", side_effect=HTTPError("https://api.github.com/test", 404, "Not Found", {}, None)) as remote, \
             patch.object(watch.time, "sleep") as delay:
            with self.assertRaises(HTTPError):
                api.get("/repos/example/x/pulls/47")
            self.assertEqual(1, remote.call_count)
            delay.assert_not_called()


if __name__ == "__main__":
    unittest.main()
