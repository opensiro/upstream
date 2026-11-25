"""Regression: a syntactically valid local Roadmap is not a persisted approval source."""
import base64
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout
from io import StringIO

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from aggregate import APIError
from roadmap_proposal_gate import (BLOCKED, VERIFIED, digest, verify_persisted_case,
                                    review_evidence_sha256)
from publication_history import attach_roadmap_gate, candidate_snapshot, apply_recheck
from validate_public_issue_payload import (verify_issue_approval_case, main as payload_main)
from validate_roadmap_publication import check_publication_ready
from test_roadmap_publication_template_gate import PROPOSAL, fill

FORK = "opensiro-contributions/synthetic"
ORIGINAL = "example/harness"
CASE = "case-example"
REF = "b" * 40
HEAD = "a" * 40
TITLE = "Proposal: scheduled option review for Synthetic — Opensiro VSM architecture review"
BODY = b"# Exact original proposal\n"
DEST = "https://github.com/" + ORIGINAL
PREFIX = ".opensiro/issues/" + CASE + "/"


class Provider:
    def __init__(self):
        self.routes = {}
        self.calls = []
        self.routes["/repos/" + FORK] = {
            "full_name": FORK, "fork": True, "parent": {"full_name": ORIGINAL}}
        self.routes["/repos/" + ORIGINAL] = {
            "full_name": ORIGINAL, "default_branch": "main"}
        self.routes["/repos/" + FORK + "/git/ref/heads/opensiro/meta"] = {"object": {"sha": REF}}
        self.routes["/repos/" + ORIGINAL + "/git/ref/heads/main"] = {"object": {"sha": HEAD}}
        self.store(".opensiro/state.json", json.dumps({
            "schema_version": 1, "working_fork": FORK, "original_repository": ORIGINAL,
            "attention": "ACTIVE", "owner_control": "ALLOW"}))

    def store(self, name, text):
        raw = text.encode("utf-8") if isinstance(text, str) else text
        self.routes["/repos/" + FORK + "/contents/" + name + "?ref=" + REF] = {
            "type": "file", "encoding": "base64",
            "content": base64.b64encode(raw).decode("ascii"), "sha": "c" * 40}

    def get(self, url):
        self.calls.append(url)
        if url not in self.routes:
            raise APIError(404, "missing fixture: " + url)
        return copy.deepcopy(self.routes[url])


def scan(action="original_issue"):
    return {"scope": "selected_repositories",
            "coverage": {"scan_complete": True, "archive": {"status": "CHECKED_BOUNDED",
                            "head": "e" * 40}},
            "cases": [{"original_repository": ORIGINAL, "working_fork": FORK,
                       "id": CASE, "meta_head_sha": REF}],
            "publications": [], "warnings": [],
            "preflight": {"original": ORIGINAL, "case_id": CASE,
                          "candidate_title": TITLE, "candidate_kind": action,
                          "status": "NEW_PROPOSAL" if action == "original_issue" else "HISTORY_UNVERIFIED",
                          "search_errors": [], "reasons": [], "possible_overlaps": [],
                          "original_search_results": [], "user_visible_delta": "distinct outcome"}}


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.case = Path(self.temp.name) / ".opensiro" / "issues" / CASE
        self.case.mkdir(parents=True)
        self.client = Provider()
        self.report = scan()
        self.history = review_evidence_sha256(self.report, HEAD, DEST)
        self.files = {
            "README.md": "# Case\n[roadmap.md](roadmap.md) [issue.md](issue.md) "
                         "[constructor-sufficiency.md](constructor-sufficiency.md)\n",
            "roadmap.md": self.receipt(),
            "issue.md": fill("FORK_CAPABILITY_ROADMAP_ISSUE.md"),
            "constructor-sufficiency.md": fill("ROADMAP_AI_CONSTRUCTOR_CONTRACT.md"),
            "original-issue-draft.md": BODY.decode("utf-8"),
        }
        for name, data in self.files.items():
            (self.case / name).write_text(data, encoding="utf-8")
            self.client.store(PREFIX + name, data)

    def tearDown(self):
        self.temp.cleanup()

    def receipt(self, action="original_issue", destination=DEST, history=None):
        return PROPOSAL + "\n## External proposal reconciliation\n" + "\n".join([
            "- Publication review source HEAD: " + HEAD,
            "- Publication review action: " + action,
            "- Publication review destination: " + destination,
            "- Publication review title SHA256: " + digest(TITLE.encode("utf-8")),
            "- Publication review history SHA256: " + (history or self.history),
            "- Publication review resolution: " + ("REUSE_EXISTING" if action == "original_issue_comment"
                                                  else "NEW_DISTINCT_OUTCOME"),
            "- Publication review rationale: Native alternatives and previous evidence were reconciled in this synthetic fixture.",
        ]) + "\n"

    def verify(self, **overrides):
        args = dict(client=self.client, fork=FORK, case_id=CASE, case_ref=REF,
                    original=ORIGINAL, source_head=HEAD, action="original_issue",
                    destination=DEST, title=TITLE, body=BODY, history_sha=self.history,
                    local_case=self.case)
        args.update(overrides)
        return verify_persisted_case(**args)

    def attach(self, **overrides):
        args = dict(client=self.client, report=self.report, case_ref=REF, body=BODY,
                    source_before=HEAD)
        args.update(overrides)
        attach_roadmap_gate(**args)
        return self.report["roadmap_gate"]

    def test_current_committed_case_and_exact_payload_pass(self):
        proof = self.verify()
        self.assertEqual(proof["status"], VERIFIED)
        self.assertIn("/blob/" + REF + "/", proof["roadmap_url"])
        self.assertEqual(proof["body_sha256"], digest(BODY))
        self.assertEqual(proof["target_transition"], "S4=— -> S4=C")

    def test_hypothetical_go_needs_evidence_passes_without_empirical_benefit(self):
        proof = self.verify()
        self.assertEqual(proof["status"], VERIFIED)
        self.assertEqual(proof["proposal_decision"], "GO")
        self.assertEqual(proof["research_disposition"], "NEEDS_EVIDENCE")
        self.assertEqual(proof["promotion_decision"], "OWNER_RESERVED")
        self.assertIs(proof["empirical_benefit_required_for_roadmap_proposal"], False)

    def test_hermes_regression_local_valid_but_stored_roadmap_stale(self):
        self.assertEqual(check_publication_ready(self.case), [])
        self.client.store(PREFIX + "roadmap.md", PROPOSAL)
        with self.assertRaisesRegex(ValueError, "local case differs from committed bytes"):
            self.verify()
        self.assertEqual(self.attach()["status"], BLOCKED)
        self.assertIn("missing/ambiguous canonical", self.report["roadmap_gate"]["reason"])

    def test_claimed_case_ref_cannot_be_old(self):
        self.client.routes["/repos/" + FORK + "/git/ref/heads/opensiro/meta"] = {
            "object": {"sha": "d" * 40}}
        with self.assertRaisesRegex(ValueError, "current opensiro/meta HEAD"):
            self.verify()

    def test_missing_remote_file_and_pause_fail_closed(self):
        del self.client.routes["/repos/" + FORK + "/contents/" + PREFIX + "README.md?ref=" + REF]
        self.assertEqual(self.attach()["status"], BLOCKED)
        self.client.store(".opensiro/state.json", json.dumps({
            "schema_version": 1, "working_fork": FORK, "original_repository": ORIGINAL,
            "attention": "ACTIVE", "owner_control": "PAUSE"}))
        with self.assertRaisesRegex(ValueError, "ACTIVE/ALLOW"):
            self.verify()

    def test_source_head_drift_and_history_drift_fail(self):
        with self.assertRaisesRegex(ValueError, "history SHA256"):
            self.verify(history_sha="f" * 64)
        self.client.routes["/repos/" + ORIGINAL + "/git/ref/heads/main"] = {
            "object": {"sha": "d" * 40}}
        with self.assertRaisesRegex(ValueError, "original HEAD changed"):
            self.verify()

    def test_changed_outbound_bytes_and_title_fail(self):
        with self.assertRaisesRegex(ValueError, "exact outbound body"):
            self.verify(body=BODY + b"changed")
        with self.assertRaisesRegex(ValueError, "title SHA256"):
            self.verify(title=TITLE + " edited")

    def test_duplicate_review_fields_are_not_accepted(self):
        self.client.store(PREFIX + "roadmap.md", self.receipt()
                          + "- Publication review source HEAD: " + HEAD + "\n")
        with self.assertRaisesRegex(ValueError, "missing/ambiguous canonical"):
            self.verify(local_case=None)

    def test_history_scan_is_preparation_only_without_case_ref(self):
        result = self.attach(case_ref=None)
        self.assertEqual(result["status"], BLOCKED)
        self.assertEqual(self.report["review_evidence_sha256"], self.history)

    def test_reconciliation_digest_stable_across_case_persistence_but_not_new_evidence(self):
        report = copy.deepcopy(self.report)
        report["cases"][0]["meta_head_sha"] = "f" * 40
        report["generated_at"] = "later"
        report["coverage"]["events_seen"] = 1  # a non-publication preparation event
        self.assertEqual(review_evidence_sha256(report, HEAD, DEST), self.history)
        report["preflight"]["possible_overlaps"] = [{"url": DEST + "/issues/17", "reason": "RELATED"}]
        self.assertNotEqual(review_evidence_sha256(report, HEAD, DEST), self.history)

    def test_changed_overlap_requires_fresh_canonical_record(self):
        self.report["preflight"]["possible_overlaps"] = [{"url": DEST + "/issues/17", "reason": "RELATED"}]
        self.report["preflight"]["status"] = "POSSIBLE_OVERLAP"
        self.assertEqual(self.attach()["status"], BLOCKED)
        self.assertIn("history SHA256", self.report["roadmap_gate"]["reason"])

    def test_prior_publication_and_partial_scan_block(self):
        for status in ("ALREADY_PUBLISHED", "REUSE_EXISTING", "HISTORY_UNVERIFIED"):
            with self.subTest(status=status):
                self.report["preflight"]["status"] = status
                self.assertEqual(self.attach()["status"], BLOCKED)
        self.report["preflight"]["status"] = "NEW_PROPOSAL"
        self.report["coverage"]["scan_complete"] = False
        self.assertEqual(self.attach()["status"], BLOCKED)

    def test_existing_issue_comment_requires_exact_target_and_body(self):
        self.report = scan("original_issue_comment")
        dest = DEST + "/issues/17"
        self.client.routes["/repos/" + ORIGINAL + "/issues/17"] = {
            "html_url": dest, "state": "open", "updated_at": "2026-11-24T00:00:00Z",
            "title": "Native existing request", "body": "Existing need", "comments": 0}
        self.assertEqual(self.attach(destination=dest)["status"], BLOCKED)
        history = self.report["review_evidence_sha256"]
        self.client.store(PREFIX + "roadmap.md", self.receipt("original_issue_comment", dest, history))
        self.client.store(PREFIX + "maintainer-comment-draft.md", BODY)
        self.assertEqual(self.attach(destination=dest)["status"], VERIFIED)
        self.assertEqual(self.report["preflight"]["status"], "HISTORY_UNVERIFIED")
        self.assertEqual(self.attach(destination=DEST + "/issues/18")["status"], BLOCKED)

    def test_discussion_requires_committed_separate_draft(self):
        self.report = scan("original_discussion")
        self.assertEqual(self.attach()["status"], BLOCKED)
        history = self.report["review_evidence_sha256"]
        self.client.store(PREFIX + "roadmap.md", self.receipt("original_discussion", DEST, history))
        self.assertEqual(self.attach()["status"], BLOCKED)
        self.client.store(PREFIX + "original-discussion-draft.md", BODY)
        self.assertEqual(self.attach()["status"], VERIFIED)

    def test_payload_gate_reads_remote_again_and_binds_report(self):
        self.assertEqual(self.attach()["status"], VERIFIED)
        self.report["candidate_snapshot"] = candidate_snapshot(self.client, self.report, BODY)
        proof = verify_issue_approval_case(self.client, self.report, "original", self.case,
                                           ORIGINAL, REF, TITLE, BODY, HEAD)
        self.assertEqual(proof["status"], VERIFIED)
        report2 = copy.deepcopy(self.report)
        report2["preflight"]["user_visible_delta"] = "different evidence"
        with self.assertRaisesRegex(ValueError, "digest"):
            verify_issue_approval_case(self.client, report2, "original", self.case,
                                       ORIGINAL, REF, TITLE, BODY, HEAD)
        with self.assertRaisesRegex(ValueError, "snapshot"):
            verify_issue_approval_case(self.client, self.report, "original", self.case,
                                       ORIGINAL, REF, TITLE, BODY + b"edited", HEAD)

    def test_prepost_snapshot_detects_metadata_drift(self):
        self.assertEqual(self.attach()["status"], VERIFIED)
        self.report["candidate_snapshot"] = candidate_snapshot(self.client, self.report, BODY)
        new = copy.deepcopy(self.report)
        new["cases"][0]["meta_head_sha"] = "f" * 40
        new["roadmap_gate"] = {"status": BLOCKED, "reason": "metadata changed"}
        new["candidate_snapshot"] = candidate_snapshot(self.client, new, BODY)
        self.assertEqual(apply_recheck(new, self.report)["recheck"]["status"],
                         "CHANGED_OR_UNVERIFIED")

    def test_cli_local_pass_never_masquerades_as_approval(self):
        title_path = self.case / "title.txt"
        body_path = self.case / "original-issue-draft.md"
        title_path.write_text(TITLE + "\n", encoding="utf-8")
        args = ["validate_public_issue_payload", "--kind", "original",
                "--case-dir", str(self.case), "--repo", ORIGINAL,
                "--case-ref", REF, "--source-head", HEAD,
                "--title-file", str(title_path), "--body-file", str(body_path)]
        # Structural pass is isolated here: the original regression was exactly
        # a successful local payload check with no verified remote commit.
        with patch("validate_public_issue_payload.check_payload", return_value=[]):
            for extra, code, marker in (([], 1, BLOCKED),
                                        (["--draft-only"], 0, "LOCAL_DRAFT_PAYLOAD_PASS_NOT_APPROVAL_READY")):
                with self.subTest(extra=extra), patch.object(sys, "argv", args + extra):
                    out = StringIO()
                    with redirect_stdout(out):
                        self.assertEqual(payload_main(), code)
                    self.assertIn(marker, out.getvalue())


if __name__ == "__main__":
    unittest.main()
