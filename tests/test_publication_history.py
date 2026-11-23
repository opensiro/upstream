"""Offline, no-GitHub-write tests of Upstream publication-history loop guard (#109)."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from aggregate import APIError
from publication_history import (
    evaluate, feedback_observation, parse_url, provider_observation,
    publication_history, published_event, receipt_urls, sha256, search_original,
)
from test_roadmap_view import Fake, file_blob, FORK, ORIGINAL, META, NOW, RECEIPT, HUMAN, AI, ROOT

CASE = "resource-control-20261118"
CASE_DIR = ".opensiro/issues/" + CASE
EVENTS = ROOT + "/contents/.opensiro/events?ref=" + META
TITLE = "Proposal: task resource admission and feedback"
OUTBOUND = "A task-level resource decision and feedback path."
ISSUE = f"https://github.com/{ORIGINAL}/issues/1063"
FORK_ISSUE = f"https://github.com/{FORK}/issues/1"
DISCUSSION = f"https://github.com/{ORIGINAL}/discussions/15831"


def provider_fixture(title=TITLE, body=OUTBOUND, comments=0, state="open", author="xLagerFeuer"):
    return {"title": title, "body": body, "state": state,
            "user": {"login": author}, "created_at": NOW,
            "updated_at": NOW, "comments": comments, "labels": []}


class PublicationFake(Fake):
    def __init__(self):
        super().__init__()
        self.fork().case(CASE, {
            "README.md": ("# Historical PREPARED — NOT PUBLISHED\n"
                          f"Prior reference {ISSUE}\n"),
            "roadmap.md": RECEIPT, "issue.md": HUMAN,
            "constructor-sufficiency.md": AI})
        self.routes[EVENTS] = []

    def event(self, event, name="20261123T080000Z--original-issue-published.json"):
        path = ".opensiro/events/" + name
        self.routes[EVENTS].append({"name": name, "type": "file", "path": path})
        self.routes[f"{ROOT}/contents/{path}?ref={META}"] = file_blob(json.dumps(event))
        return self

    def receipt(self, body):
        base = f"{ROOT}/contents/{CASE_DIR}"
        path = CASE_DIR + "/publication-receipt.md"
        self.routes[base + "?ref=" + META].append({"name": "publication-receipt.md",
                                                     "type": "file", "path": path})
        self.routes[f"{ROOT}/contents/{path}?ref={META}"] = file_blob(body)
        return self

    def verified_issue(self, number=1063, title=TITLE, body=OUTBOUND,
                       comments=0, state="open", author="xLagerFeuer"):
        self.routes[f"/repos/{ORIGINAL}/issues/{number}"] = provider_fixture(
            title=title, body=body, comments=comments, state=state, author=author)
        return self


def publication_event(url=ISSUE):
    return {"schema_version": 1, "kind": "EXTERNAL_ORIGINAL_ISSUE_PUBLISHED",
            "decision": "PUBLICATION_VERIFIED_READBACK",
            "case_id": CASE, "original_issue_url": url,
            "title_sha256": sha256(TITLE), "body_sha256": sha256(OUTBOUND),
            "recorded_at": NOW}


class FakeWithGraphQL(PublicationFake):
    def discussion(self, repo, number):
        if number != 15831 or repo != ORIGINAL:
            raise APIError(404, "wrong discussion")
        return {"title": TITLE, "body": OUTBOUND, "createdAt": NOW,
                "updatedAt": NOW, "author": {"login": "xLagerFeuer"},
                "comments": {"totalCount": 0, "pageInfo": {"hasNextPage": False},
                             "nodes": []}}


class PublicationHistoryTests(unittest.TestCase):
    def test_same_case_publication_blocks_renamed_second_issue(self):
        client = PublicationFake().event(publication_event()).verified_issue()
        report = publication_history(client, requested=[FORK], observed_at=NOW,
                                     candidate_original=ORIGINAL,
                                     candidate_case=CASE,
                                     candidate_title="A DIFFERENT title for the same capability",
                                     search=False)
        self.assertEqual(report["coverage"]["publications_found"], 1)
        self.assertEqual(report["preflight"]["status"], "ALREADY_PUBLISHED")
        self.assertEqual(report["preflight"]["same_case_publications"][0]["url"], ISSUE)
        self.assertFalse(report["preflight"]["permits_automatic_publication"])
        self.assertTrue(report["coverage"]["scan_complete"])

    def test_receipt_merges_with_event_and_not_published_preview_stays_historical(self):
        receipt = ("# Public original Issue publication receipt\n"
                   f"**PUBLICATION VERIFIED** [Browser Issue #1063]({ISSUE})\n"
                   f"**GitHub URL / ID:** {ISSUE}\n"
                   f"Other existing issue https://github.com/{ORIGINAL}/issues/582\n")
        client = PublicationFake().event(publication_event()).receipt(receipt).verified_issue()
        report = publication_history(client, requested=[FORK], observed_at=NOW)
        self.assertEqual(len(report["publications"]), 1)
        entry = report["publications"][0]
        self.assertEqual(set(entry["evidence_types"]), {"EVENT", "RECEIPT"})
        self.assertEqual(len(entry["provenance"]), 2)
        self.assertTrue(report["coverage"]["scan_complete"])

    def test_draft_or_plain_cited_issue_is_not_publication(self):
        client = PublicationFake()
        client.event({"kind": "PREPARED_REVISION", "decision": "NOT_PUBLISHED",
                      "evidence_urls": [ISSUE]}, name="20261123T083000Z--draft-published-plan.json")
        report = publication_history(client, requested=[FORK], observed_at=NOW)
        self.assertEqual(report["publications"], [])
        self.assertTrue(report["coverage"]["scan_complete"])
        self.assertFalse(published_event({"kind": "EXTERNAL_ORIGINAL_ISSUE_PUBLISHED",
                                           "decision": "NOT_PUBLISHED"}))
        self.assertEqual(receipt_urls("Draft — NOT PUBLISHED: " + ISSUE, ORIGINAL, FORK), [])

    def test_original_issue_fork_issue_and_discussion_are_distinct(self):
        client = FakeWithGraphQL().verified_issue()
        client.routes[f"/repos/{FORK}/issues/1"] = provider_fixture(title="Fork", body="Fork body")
        client.event({"kind": "PUBLICATION",
                      "decision": "ORIGINAL_GITHUB_ISSUE_PUBLISHED",
                      "case_id": CASE, "evidence_urls": [ISSUE, FORK_ISSUE, DISCUSSION]})
        report = publication_history(client, requested=[FORK], observed_at=NOW)
        self.assertEqual({x["kind"] for x in report["publications"]},
                         {"original_issue", "fork_issue", "original_discussion"})
        self.assertEqual(report["coverage"]["provider_unverified"], 0)
        self.assertEqual({x["url"] for x in report["publications"]},
                         {ISSUE, FORK_ISSUE, DISCUSSION})

    def test_unavailable_discussion_is_unverified_not_deleted(self):
        client = PublicationFake().event({"kind": "PUBLICATION",
            "decision": "CLINE_ORIGINAL_FEATURE_REQUEST_DISCUSSION_PUBLISHED",
            "evidence_urls": [DISCUSSION]})
        report = publication_history(client, requested=[FORK], observed_at=NOW)
        self.assertEqual(report["publications"][0]["provider"]["status"], "UNVERIFIED")
        self.assertEqual(report["publications"][0]["provider"]["reason"],
                         "DISCUSSION_GRAPHQL_READBACK_REQUIRED")
        self.assertFalse(report["coverage"]["scan_complete"])

    def test_old_readme_publication_can_be_recovered_without_event(self):
        """README-only proof is not confused with a generic referenced issue."""
        client = PublicationFake().verified_issue()
        client.routes[f"/repos/{FORK}/issues/1"] = provider_fixture(title="Fork", body="Fork body")
        client.routes[f"{ROOT}/contents/{CASE_DIR}/README.md?ref={META}"] = file_blob(
            "# Case\n"
            f"**Public fork Issue:** [{FORK_ISSUE}]({FORK_ISSUE}) — OPEN; published. "
            f"**Original maintainer Issue:** [{ISSUE}]({ISSUE}) — OPEN and published.\n"
            f"Existing third-party Issue https://github.com/{ORIGINAL}/issues/582\n"
            f"Original Issue NOT_PUBLISHED: https://github.com/{ORIGINAL}/issues/902\n")
        result = publication_history(client, requested=[FORK], observed_at=NOW)
        self.assertEqual({p["url"] for p in result["publications"]}, {ISSUE, FORK_ISSUE})
        self.assertTrue(all("README_CLAIM" in p["evidence_types"]
                            for p in result["publications"]))

    def test_opencode_legacy_event_without_case_id_links_both_audiences(self):
        client = PublicationFake().verified_issue()
        client.routes[f"/repos/{FORK}/issues/1"] = provider_fixture(title="Fork", body="Fork")
        client.event({"schema_version": 1, "kind": "PUBLICATION",
                      "decision": "ORIGINAL_GITHUB_ISSUE_PUBLISHED / EXACT_APPROVAL",
                      "evidence_urls": [ISSUE, FORK_ISSUE,
                                        "https://github.com/opensiro/upstream/issues/93"]})
        report = publication_history(client, requested=[FORK], observed_at=NOW)
        self.assertEqual(len(report["publications"]), 2)
        self.assertEqual({p["kind"] for p in report["publications"]},
                         {"fork_issue", "original_issue"})

    def test_gastown_legacy_external_issue_field(self):
        client = PublicationFake().verified_issue()
        client.event({"schema_version": 1, "kind": "EXTERNAL_ORIGINAL_ISSUE_PUBLICATION_VERIFIED",
                      "decision": "PUBLISHED_AND_READBACK_VERIFIED", "case_id": CASE,
                      "external_issue_url": ISSUE, "body_sha256": sha256(OUTBOUND)})
        report = publication_history(client, requested=[FORK], observed_at=NOW)
        self.assertEqual(len(report["publications"]), 1)
        self.assertEqual(report["publications"][0]["provider"]["status"], "OPEN")

    def test_cline_discussion_event_without_case_id_is_typed(self):
        client = FakeWithGraphQL()
        client.event({"kind": "PUBLICATION",
                      "decision": "CLINE_ORIGINAL_FEATURE_REQUEST_DISCUSSION_PUBLISHED",
                      "evidence_urls": [DISCUSSION]})
        report = publication_history(client, requested=[FORK], observed_at=NOW)
        self.assertEqual(report["publications"][0]["kind"], "original_discussion")
        self.assertEqual(report["publications"][0]["provider"]["status"],
                         "PUBLISHED_STATE_NOT_CHECKED")

    def test_original_provider_hash_edit_blocks_silent_acceptance(self):
        client = PublicationFake().event(publication_event()).verified_issue(body="Edited after posting")
        report = publication_history(client, requested=[FORK], observed_at=NOW)
        item = report["publications"][0]
        self.assertEqual(item["provider"]["status"], "UNVERIFIED")
        self.assertEqual(item["provider"]["reason"], "BODY_SHA256_MISMATCH_OR_EDIT")
        self.assertFalse(report["coverage"]["scan_complete"])

    def test_unreachable_original_issue_does_not_look_unpublished(self):
        client = PublicationFake().event(publication_event())
        client.routes[f"/repos/{ORIGINAL}/issues/1063"] = APIError(404, "deleted")
        report = publication_history(client, requested=[FORK], observed_at=NOW)
        self.assertEqual(report["publications"][0]["provider"]["reason"], "GITHUB_HTTP_404")
        self.assertEqual(report["preflight"]["status"], "HISTORY_UNVERIFIED") if "preflight" in report else None
        self.assertFalse(report["coverage"]["scan_complete"])

    def test_comments_are_bounded_bot_tagged_and_never_accepted(self):
        client = PublicationFake().event(publication_event()).verified_issue(comments=1)
        client.routes[f"/repos/{ORIGINAL}/issues/1063/comments?per_page=100&page=1"] = [
            {"user": {"login": "reviewer[bot]", "type": "Bot"},
             "author_association": "NONE", "body": "Existing plugin API may already work",
             "html_url": ISSUE + "#issuecomment-1000", "created_at": NOW}]
        report = publication_history(client, requested=[FORK], observed_at=NOW)
        item = report["publications"][0]
        self.assertTrue(item["provider"]["feedback"]["items"][0]["is_bot"])
        self.assertEqual(item["provider"]["feedback"]["status"], "COMPLETE")
        self.assertNotIn("accepted", str(item["provider"]).lower())
        self.assertTrue(report["coverage"]["scan_complete"])

    def test_comment_pagination_or_api_failure_is_unverified(self):
        client = PublicationFake().event(publication_event()).verified_issue(comments=2)
        client.routes[f"/repos/{ORIGINAL}/issues/1063/comments?per_page=100&page=1"] = APIError(403, "rate-limit")
        report = publication_history(client, requested=[FORK], observed_at=NOW)
        self.assertEqual(report["publications"][0]["provider"]["reason"], "COMMENTS_UNVERIFIED")
        self.assertFalse(report["coverage"]["scan_complete"])

    def test_same_original_related_case_is_potential_overlap(self):
        base = {"original_repository": ORIGINAL, "case_id": "different-case",
                "url": f"https://github.com/{ORIGINAL}/issues/501",
                "provider": {"status": "OPEN", "title": "Task queue priority"}}
        report = {"cases": [{"original_repository": ORIGINAL, "id": CASE}],
                  "coverage": {"scan_complete": True}, "publications": [base]}
        outcome = evaluate(report, ORIGINAL, CASE, "Resource admission priorities")
        self.assertEqual(outcome["status"], "POSSIBLE_OVERLAP")
        self.assertEqual(outcome["possible_overlaps"][0]["reason"], "PRIOR_OPENSIRO_SAME_ORIGINAL")

    def test_same_case_fork_issue_does_not_block_separate_original_channel(self):
        """One research case may have independently approved fork and original Issues."""
        client = PublicationFake()
        client.event({"kind": "PUBLICATION", "decision": "FORK_ISSUE_PUBLISHED",
                      "case_id": CASE, "evidence_urls": [FORK_ISSUE]})
        client.routes[f"/repos/{FORK}/issues/1"] = provider_fixture(
            title="Fork publication", body="Fork only")
        report = publication_history(client, requested=[FORK], observed_at=NOW)
        result = evaluate(report, ORIGINAL, CASE, TITLE, target_kind="original_issue")
        self.assertEqual(result["status"], "POSSIBLE_OVERLAP")
        self.assertEqual(result["same_case_publications"], [])
        self.assertEqual(result["same_case_other_channels"][0]["url"], FORK_ISSUE)
        fork_again = evaluate(report, ORIGINAL, CASE, TITLE, target_kind="fork_issue")
        self.assertEqual(fork_again["status"], "ALREADY_PUBLISHED")

    def test_exact_older_author_title_routes_to_reuse_existing(self):
        report = {"cases": [{"original_repository": ORIGINAL, "id": CASE}],
                  "coverage": {"scan_complete": True}, "publications": []}
        search = [{"url": ISSUE, "title": TITLE, "author": "xLagerFeuer"}]
        result = evaluate(report, ORIGINAL, CASE, TITLE, search_results=search)
        self.assertEqual(result["status"], "REUSE_EXISTING")
        self.assertFalse(result["permits_automatic_publication"])

    def test_cross_repository_similar_vsm_grade_not_equal_user_need(self):
        base = {"original_repository": "other/other", "case_id": "case2",
                "url": "https://github.com/other/other/issues/8",
                "provider": {"status": "OPEN", "title": "Different user-facing outcome"}}
        report = {"cases": [{"original_repository": ORIGINAL, "id": CASE}],
                  "coverage": {"scan_complete": True}, "publications": [base]}
        outcome = evaluate(report, ORIGINAL, CASE,
                           "S3 task admission and resource coordination")
        self.assertEqual(outcome["status"], "NEW_PROPOSAL")
        self.assertFalse(outcome["history_complete"])
        self.assertTrue(outcome["requires_exact_owner_approval"])

    def test_incomplete_metadata_or_search_errors_are_fail_closed(self):
        report = {"cases": [], "coverage": {"scan_complete": False}, "publications": []}
        outcome = evaluate(report, ORIGINAL, CASE, TITLE, search_errors=["API_403"])
        self.assertEqual(outcome["status"], "HISTORY_UNVERIFIED")
        client = PublicationFake()
        client.routes[f"/repos/{FORK}"] = APIError(403, "forbidden")
        out = publication_history(client, requested=[FORK], observed_at=NOW)
        self.assertFalse(out["coverage"]["scan_complete"])
        self.assertGreater(out["coverage"]["errors"], 0)

    def test_original_first_party_search_and_truncation(self):
        client = PublicationFake()
        base = f"repo:{ORIGINAL} is:issue"
        from publication_history import keywords
        terms = sorted(keywords(TITLE), key=len, reverse=True)[:2]
        from urllib.parse import quote
        client.routes["/search/issues?q=" + quote(base + " author:xLagerFeuer") + "&per_page=100"] = {
            "items": [], "total_count": 0, "incomplete_results": False}
        client.routes["/search/issues?q=" + quote(base + " " + " ".join(terms)) + "&per_page=100"] = {
            "items": [{"html_url": ISSUE, "title": TITLE, "user": {"login": "xLagerFeuer"},
                       "state": "open"}], "total_count": 1, "incomplete_results": False}
        matches, errors = search_original(client, ORIGINAL, TITLE)
        self.assertEqual(errors, [])
        self.assertEqual(matches[0]["url"], ISSUE)
        client.routes["/search/issues?q=" + quote(base + " " + " ".join(terms)) + "&per_page=100"]["incomplete_results"] = True
        matches, errors = search_original(client, ORIGINAL, TITLE)
        self.assertTrue(any("TRUNCATED" in x for x in errors))

    def test_url_family_and_identity_guard(self):
        self.assertEqual(parse_url(ISSUE, ORIGINAL, FORK)["kind"], "original_issue")
        self.assertEqual(parse_url(FORK_ISSUE, ORIGINAL, FORK)["kind"], "fork_issue")
        self.assertEqual(parse_url(DISCUSSION, ORIGINAL, FORK)["kind"], "original_discussion")
        self.assertIsNone(parse_url("https://evil.com/"+ORIGINAL+"/issues/5", ORIGINAL, FORK))
        self.assertIsNone(parse_url(f"https://github.com/other/x/issues/1", ORIGINAL, FORK))


if __name__ == "__main__":
    unittest.main()
