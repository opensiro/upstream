"""Source-owned issue observation and fork-local CAS publication tests (offline)."""
import base64
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from aggregate import APIError, aggregate
from issue_watch import (validate_watch, load_target, observe, apply_change, GitHubWriter,
                         readonly_descriptor_target)

FORK = "opensiro-contributions/openclaw"
ORIGINAL = "openclaw/openclaw"
IDENT = "openclaw-fallback-model-thinking-defaults"
ISSUE = "https://github.com/openclaw/openclaw/issues/147509"
ANCHOR = ISSUE + "#issuecomment-6919296247"
HEAD = "a"*40
BASE = "2026-11-16T14:31:00Z"
AFTER = "2026-11-16T15:00:00Z"


def descriptor():
    return {"schema_version": 1, "issue_url": ISSUE, "anchor_comment_url": ANCHOR,
            "expected_decisions": ["Can fallback models use their own thinking default?",
                                   "Is a code PR allowed before a source maintainer decision?"],
            "relevant_labels": ["clawsweeper:no-new-fix-pr", "clawsweeper:needs-product-decision",
                                "clawsweeper:needs-maintainer-review"],
            "baseline": {"state": "open",
                         "labels": ["clawsweeper:needs-maintainer-review",
                                    "clawsweeper:needs-product-decision",
                                    "clawsweeper:no-new-fix-pr", "enhancement"],
                         "last_comment_id": 6919296247, "observed_at": BASE},
            "last_alert_fingerprint": None}


def source_comment(ident, author="maintainer", role="MEMBER", text="Please submit a PR for this.",
                   user_type="User", updated=None):
    return {"id": ident, "html_url": ISSUE + "#issuecomment-" + str(ident),
            "user": {"login": author, "type": user_type}, "author_association": role,
            "body": text, "updated_at": updated or AFTER, "created_at": AFTER}


def blob(value):
    return {"type": "file", "sha": "b"*40, "encoding": "base64",
            "content": base64.b64encode(json.dumps(value).encode()).decode()}


class FakeGitHub:
    def __init__(self):
        self.head = HEAD
        self.record = {"schema_version": 1, "id": IDENT,
                       "original_repository": ORIGINAL, "work_state": "BUILD",
                       "title": "Fallback thinking defaults",
                       "external_prs": [], "issue_watch": descriptor(),
                       "next_action": "AWAITING_MAINTAINER_DECISION",
                       "last_event_id": "prior-event"}
        self.state = {"schema_version": 1, "original_repository": ORIGINAL,
                      "working_fork": FORK, "attention": "ACTIVE", "owner_control": "ALLOW",
                      "last_event_id": "some-other-event"}
        self.issue = {"number": 147509, "html_url": ISSUE, "state": "open",
                      "labels": [{"name": n} for n in descriptor()["baseline"]["labels"]]}
        self.comments = [source_comment(6919296247, author="xLagerFeuer",
                                        role="NONE", text="Request for maintainer decision.")]
        self.posts = []
        self.files = {}
        self.rejected_cas = False

    def get(self, path):
        if path == "/repos/" + FORK:
            return {"fork": True, "parent": {"full_name": ORIGINAL}}
        if path == "/repos/" + FORK + "/git/ref/heads/opensiro/meta":
            return {"object": {"sha": self.head}}
        if path.startswith("/repos/" + FORK + "/contents/"):
            if path.endswith("state.json?ref=" + self.head):
                return blob(self.state)
            if path.endswith(IDENT + ".json?ref=" + self.head):
                return blob(self.record)
            raise APIError(404, "missing fork-local source")
        if path == "/repos/" + FORK + "/git/commits/" + self.head:
            return {"tree": {"sha": "c"*40}}
        if path == "/repos/" + ORIGINAL + "/issues/147509":
            return self.issue
        if path == "/repos/" + ORIGINAL + "/issues/147509/comments?per_page=100&page=1":
            return self.comments
        raise APIError(404, "missing fake source: " + path)

    def write(self, method, suffix, payload):
        self.posts.append((method, suffix, payload))
        if method == "POST" and suffix == "git/trees":
            self.files = {entry["path"]: json.loads(entry["content"]) for entry in payload["tree"]}
            return {"sha": "d"*40}
        if method == "POST" and suffix == "git/commits":
            self.parent = payload["parents"][0]
            return {"sha": "e"*40}
        if method == "PATCH" and suffix == "git/refs/heads/opensiro/meta":
            if self.rejected_cas:
                raise APIError(422, "non-fastforward")
            if self.head != self.parent or payload.get("force") is not False:
                raise AssertionError("no lost-update or forced ref writes allowed")
            self.head = "e"*40
            self.state = self.files[".opensiro/state.json"]
            self.record = self.files[".opensiro/contributions/" + IDENT + ".json"]
            return {"object": {"sha": self.head}}
        raise AssertionError("not a permitted bounded fork-local endpoint")


class IssueWatchTests(unittest.TestCase):
    def setUp(self):
        self.gh = FakeGitHub()
        self.target = load_target(self.gh, FORK, IDENT)

    def check(self):
        return observe(self.gh, self.target, now=AFTER)

    def test_initial_unchanged(self):
        x = self.check()
        self.assertEqual(x["status"], "UNCHANGED")
        self.assertFalse(x["alert"])
        self.assertFalse(x["applied"])

    def test_explicit_maintainer_answer_has_pinned_comment(self):
        self.gh.comments.append(source_comment(7000000000))
        x = self.check()
        self.assertEqual(x["status"], "DECISION_CONFIRMED")
        self.assertEqual(x["change"]["decisions"][0]["verdict"], "APPROVED_FOR_DISCUSSION")
        self.assertEqual(x["source_links"], [ISSUE + "#issuecomment-7000000000"])
        self.assertTrue(x["alert"])

    def test_maintainer_rejection_not_misread_as_approval(self):
        self.gh.comments.append(source_comment(7000000000, text="We will not accept this PR."))
        x = self.check()
        self.assertEqual(x["change"]["decisions"][0]["verdict"], "REJECTED")
        self.assertEqual(x["status"], "DECISION_CONFIRMED")

    def test_unrelated_user_comment_never_confirms_maintainer_decision(self):
        self.gh.comments.append(source_comment(7000000000, "user42", "NONE",
                                                "I think you can open a PR"))
        x = self.check()
        self.assertEqual(x["status"], "NEW_ACTIVITY_NEEDS_REVIEW")
        self.assertEqual(x["change"]["decisions"], [])

    def test_bot_churn_not_reported_as_approval_or_alert(self):
        self.gh.comments.append(source_comment(7000000000, "clawsweeper[bot]", "CONTRIBUTOR",
                                                "Approved", "Bot"))
        self.assertEqual(self.check()["status"], "UNCHANGED")

    def test_relevant_label_change_needs_review_not_approval(self):
        self.gh.issue["labels"] = [{"name":"enhancement"}, {"name":"clawsweeper:needs-product-decision"}]
        x = self.check()
        self.assertEqual(x["status"], "NEW_ACTIVITY_NEEDS_REVIEW")
        self.assertEqual(len(x["change"]["changed_relevant_labels"]), 2)
        self.assertIn(ISSUE, x["source_links"])

    def test_irrelevant_label_churn_is_not_alert(self):
        self.gh.issue["labels"].append({"name":"P3"})
        self.assertEqual(self.check()["status"], "UNCHANGED")

    def test_close_or_reopen_is_review_not_pr_permission(self):
        self.gh.issue["state"] = "closed"
        x = self.check()
        self.assertEqual(x["status"], "NEW_ACTIVITY_NEEDS_REVIEW")
        self.assertEqual(x["change"]["after_state"], "closed")
        self.assertFalse(x["applied"])

    def test_missing_unreadable_source_and_api_failures_are_unknown(self):
        original = self.gh.get
        for failure in (APIError(403, "Forbidden"), APIError(429, "Rate limited"),
                        APIError(404, "Not found")):
            def fake(path):
                if path == "/repos/openclaw/openclaw/issues/147509":
                    raise failure
                return original(path)
            self.gh.get = fake
            with self.subTest(code=failure.status):
                x = self.check()
                self.assertEqual(x["status"], "UNKNOWN")
                self.assertFalse(x["alert"])
            self.gh.get = original
        self.gh.comments = []
        self.assertEqual(self.check()["status"], "UNKNOWN")

    def test_source_identity_and_cursor_fails_closed(self):
        for mutation in ("issue_url", "anchor_comment_url", "cursor"):
            w = descriptor()
            if mutation == "issue_url":
                w["issue_url"] = "https://github.com/other/openclaw/issues/147509"
            elif mutation == "anchor_comment_url":
                w["anchor_comment_url"] = "https://github.com/openclaw/openclaw/issues/19#issuecomment-6919296247"
            else:
                w["baseline"]["last_comment_id"] = 1
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_watch(w, ORIGINAL)

    def test_immutable_event_cas_and_dedup_across_reruns(self):
        self.gh.comments.append(source_comment(7000000000))
        x = self.check()
        result = apply_change(self.gh, self.target, x, actor="unit test")
        self.assertTrue(result["applied"])
        self.assertEqual(result["meta_commit"], "e"*40)
        self.assertEqual(self.gh.state["attention"], "ACTIVE")
        self.assertEqual(self.gh.record["work_state"], "BUILD")
        self.assertEqual(self.gh.record["external_prs"], [])
        self.assertEqual(self.gh.record["issue_watch"]["last_alert_fingerprint"], x["fingerprint"])
        events = [p for p in self.gh.files if p.startswith(".opensiro/events/")]
        self.assertEqual(len(events), 1)
        self.assertEqual(self.gh.files[events[0]]["evidence_urls"], [ISSUE+"#issuecomment-7000000000"])
        self.assertEqual(self.gh.record["last_event_id"], self.gh.state["last_event_id"])
        self.assertTrue(all("git/" in suffix and not suffix.startswith("issues")
                            for _, suffix, _ in self.gh.posts))
        self.target = load_target(self.gh, FORK, IDENT)
        again = self.check()
        self.assertEqual(again["status"], "UNCHANGED")
        self.assertFalse(again["alert"])
        self.assertEqual(len(self.gh.posts), 3)

    def test_prewrite_and_midwrite_cas_collisions(self):
        self.gh.comments.append(source_comment(7000000000))
        alert = self.check()
        self.gh.head = "f"*40
        with self.assertRaisesRegex(RuntimeError, "CAS_PRECONDITION_FAILED"):
            apply_change(self.gh, self.target, alert, actor="unit test")
        self.assertEqual(self.gh.posts, [])
        self.gh.head = HEAD
        self.gh.rejected_cas = True
        with self.assertRaises(APIError):
            apply_change(self.gh, self.target, alert, actor="unit test")
        self.assertEqual(self.gh.head, HEAD)

    def test_fork_pause_or_stop_blocks_effectful_write(self):
        self.gh.comments.append(source_comment(7000000000))
        alert = self.check()
        for control in ("PAUSE", "STOP"):
            target=copy.deepcopy(self.target)
            target["state"]["owner_control"] = control
            with self.subTest(control=control), self.assertRaises(PermissionError):
                apply_change(self.gh, target, alert, actor="unit test")
        self.assertEqual(self.gh.posts, [])

    def test_write_api_only_allows_nonforce_fork_local_git(self):
        with self.assertRaises(ValueError):
            GitHubWriter("secret", "example/openclaw")
        writer=GitHubWriter("test-token", FORK)
        for method,suffix,payload in (("POST","issues",{}),
                                      ("POST","git/refs",{}),
                                      ("PATCH","git/refs/heads/opensiro/meta",{"force":True})):
            with self.subTest(suffix=suffix),self.assertRaises(ValueError):
                writer.write(method,suffix,payload)

    def test_aggregate_pr_metrics_separate_from_watches(self):
        from aggregate import check_contribution
        record = self.gh.record
        self.assertEqual(check_contribution(record, ".opensiro/contributions/"+IDENT+".json", ORIGINAL), [])
        self.assertEqual(record["external_prs"], [])


if __name__ == "__main__":
    unittest.main()


class PausedBBReadOnlyTests(unittest.TestCase):
    def bb_case(self):
        path = ROOT / "docs" / "issue-watch-bb-readonly.json"
        descriptor = json.loads(path.read_text())
        target = {"fork": "opensiro-contributions/bb",
                  "id": "getbb-worktree-archive-safety-20261116",
                  "original": "get-bb/bb",
                  "state": {"owner_control": "PAUSE", "attention": "WATCHING"},
                  "record": {"id": "getbb-worktree-archive-safety-20261116",
                             "work_state": "BLOCKED", "original_repository": "get-bb/bb"}}
        return target, descriptor

    def test_paused_bb_can_be_observed_without_changing_original_metadata(self):
        target, descriptor = self.bb_case()
        preview = readonly_descriptor_target(target, descriptor)
        self.assertEqual(preview["record"]["issue_watch"], descriptor)
        self.assertEqual(preview["state"]["owner_control"], "PAUSE")
        self.assertEqual(preview["record"]["work_state"], "BLOCKED")
        self.assertNotIn("issue_watch", target["record"])
        self.assertIsNot(preview["record"], target["record"])
        self.assertEqual(validate_watch(descriptor, "get-bb/bb"),
                         ("get-bb/bb", 5952, 6919385474))

    def test_wrong_source_descriptor_fails_closed(self):
        target, descriptor = self.bb_case()
        descriptor["issue_url"] = ISSUE
        with self.assertRaises(ValueError):
            readonly_descriptor_target(target, descriptor)

    def test_cannot_override_existing_registered_watch(self):
        target, descriptor = self.bb_case()
        target["record"]["issue_watch"] = descriptor
        with self.assertRaisesRegex(ValueError, "must not be overridden"):
            readonly_descriptor_target(target, descriptor)

    def test_workflow_uses_read_only_schedule_and_requires_optin_for_write(self):
        content=(ROOT/".github/workflows/observe-issues.yml").read_text()
        self.assertIn("if [[ \"$APPLY_INPUT\" = \"true\" ]]", content)
        self.assertIn("--read-only-descriptor docs/issue-watch-bb-readonly.json", content)
        self.assertNotIn('if [[ "$EVENT" = "schedule" ||', content)
        self.assertIn("vars.UPSTREAM_ISSUE_WATCH_ENABLED", content)
        self.assertIn("OPENSIRO_FORK_WATCH_TOKEN", content)
