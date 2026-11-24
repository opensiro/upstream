"""Regression: exact action attribution, all native search channels, approval drift."""
import copy
from pathlib import Path
import sys
import unittest
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from aggregate import APIError
from publication_history import (apply_recheck, candidate_snapshot, event_urls,
                                 provider_observation, search_original, keywords, sha256)
from test_publication_history import PublicationFake, CASE, TITLE, OUTBOUND, ISSUE, FORK_ISSUE, DISCUSSION, provider_fixture
from test_roadmap_view import ORIGINAL, FORK, NOW

HEAD = "a" * 40

def prepare_search(client, discussions=False):
    terms = sorted(keywords(TITLE), key=lambda w: (-len(w), w))[:2]
    for kind in ("issue", "pr"):
        for suffix in ("author:xLagerFeuer", " ".join(terms)):
            key = "/search/issues?q=" + quote(f"repo:{ORIGINAL} is:{kind} {suffix}") + "&per_page=100"
            client.routes[key] = {"items": [], "total_count": 0, "incomplete_results": False}
    client.routes[f"/repos/{ORIGINAL}"] = {"has_discussions": discussions, "default_branch": "main"}
    client.routes[f"/repos/{ORIGINAL}/git/ref/heads/main"] = {"object": {"sha": HEAD}}
    return client


def sample_report():
    return {"generated_at": NOW, "coverage": {"scan_complete": True},
            "cases": [{"id": CASE, "meta_head_sha": "b" * 40}],
            "publications": [{"url": ISSUE, "provider": {
                "status": "OPEN", "updated_at": NOW, "observed_at": NOW,
                "feedback": {"items": [{"body_sha256": sha256("feedback")}]}}}],
            "preflight": {"original": ORIGINAL, "candidate_title": TITLE,
                "case_id": CASE, "candidate_kind": "original_issue",
                "status": "NEW_PROPOSAL", "reasons": []}}


class RecheckTests(unittest.TestCase):
    def test_explicit_action_does_not_inherit_other_evidence_urls(self):
        event = {"kind": "PUBLICATION", "decision": "ORIGINAL_GITHUB_ISSUE_PUBLISHED",
                 "original_issue_url": ISSUE,
                 "evidence_urls": [ISSUE, FORK_ISSUE, f"https://github.com/{ORIGINAL}/issues/123"]}
        self.assertEqual([x["url"] for x in event_urls(event, ORIGINAL, FORK)], [ISSUE])

    def test_ambiguous_legacy_action_is_not_guessed(self):
        event = {"kind": "PUBLICATION", "decision": "ORIGINAL_GITHUB_ISSUE_PUBLISHED",
                 "evidence_urls": [ISSUE, f"https://github.com/{ORIGINAL}/issues/123"]}
        with self.assertRaises(ValueError):
            event_urls(event, ORIGINAL, FORK)

    def test_expanded_search_finds_original_pr_and_discussion(self):
        class Client(PublicationFake):
            def discussion_search(self, repo, terms):
                return [{"url": DISCUSSION, "title": "Related Discussion", "author": {"login":"maintainer"}, "updatedAt": NOW}]
        client = prepare_search(Client(), discussions=True)
        key = "/search/issues?q=" + quote(f"repo:{ORIGINAL} is:pr author:xLagerFeuer") + "&per_page=100"
        pr = f"https://github.com/{ORIGINAL}/pull/34"
        client.routes[key] = {"items": [{"html_url": pr, "title": TITLE, "user": {"login":"xLagerFeuer"},
                                          "state":"closed", "updated_at": NOW}],
                              "total_count": 1, "incomplete_results": False}
        results, errors = search_original(client, ORIGINAL, TITLE, expanded=True)
        self.assertEqual(errors, [])
        self.assertEqual({x["kind"] for x in results}, {"original_pr", "original_discussion"})
        self.assertEqual({x["url"] for x in results}, {DISCUSSION, pr})

    def test_discussion_search_unavailable_is_not_empty_success(self):
        client = prepare_search(PublicationFake(), discussions=True)
        rows, errors = search_original(client, ORIGINAL, TITLE, expanded=True)
        self.assertEqual(rows, [])
        self.assertTrue(any("DISCUSSION_SEARCH_UNVERIFIED" in x for x in errors))

    def test_issue_endpoint_returning_pr_is_not_verified_issue(self):
        client = PublicationFake()
        item = provider_fixture()
        item["pull_request"] = {"url": "https://api.github.com/repos/x/y/pulls/1"}
        client.routes[f"/repos/{ORIGINAL}/issues/1063"] = item
        obs = provider_observation(client, {"kind":"original_issue","repository":ORIGINAL,
                                             "number":1063,"url":ISSUE}, NOW)
        self.assertEqual(obs["status"], "UNVERIFIED")

    def test_recheck_stable_observation_timestamp(self):
        client = prepare_search(PublicationFake())
        old = sample_report()
        old["candidate_snapshot"] = candidate_snapshot(client, old, OUTBOUND.encode())
        new = copy.deepcopy(old)
        new["generated_at"] = "later"
        new["publications"][0]["provider"]["observed_at"] = "later"
        new["candidate_snapshot"] = candidate_snapshot(client, new, OUTBOUND.encode())
        self.assertEqual(apply_recheck(new, old)["recheck"]["status"], "UNCHANGED")

    def test_recheck_blocks_changed_body_head_or_feedback(self):
        client = prepare_search(PublicationFake())
        old = sample_report()
        old["candidate_snapshot"] = candidate_snapshot(client, old, OUTBOUND.encode())
        for change in ("body", "head", "feedback"):
            with self.subTest(change=change):
                client = prepare_search(PublicationFake())
                new = sample_report()
                body = OUTBOUND.encode()
                if change == "body":
                    body += b" changed"
                elif change == "head":
                    client.routes[f"/repos/{ORIGINAL}/git/ref/heads/main"] = {"object":{"sha":"c"*40}}
                else:
                    new["publications"][0]["provider"]["feedback"]["items"][0]["body_sha256"] = sha256("changed feedback")
                new["candidate_snapshot"] = candidate_snapshot(client, new, body)
                apply_recheck(new, old)
                self.assertEqual(new["recheck"]["status"], "CHANGED_OR_UNVERIFIED")
                self.assertEqual(new["preflight"]["status"], "HISTORY_UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
