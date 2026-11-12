"""Evidence gates for the read-only Upstream verified-outcome candidates."""

import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location(
    "verified_external_outcomes", ROOT / "scripts/verified_external_outcomes.py")
outcomes = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(outcomes)


def improved_case():
    return next(row for row in outcomes.cohort()[0] if row["id"].startswith("improvement:"))


def pr_payload(item, *, state="closed", merged=True):
    case = item["source"]
    url = item["pr_urls"][0]
    repository, number = outcomes.portfolio_reconcile.identity(url)
    return {
        "html_url": url, "number": number, "state": state,
        "merged_at": case["merged_at"] if merged else None,
        "merge_commit_sha": case["merge_commit_sha"] if merged else None,
        "merged_by": {"login": case["merged_by"]} if merged else None,
        "user": {"login": item["actor"]},
        "head": {"sha": case["merged_pr_head_sha"],
                 "repo": {"full_name": case["public_fork"]}},
        "base": {"repo": {"full_name": repository}, "ref": case["external_pr_base"]},
    }


def native_run(item):
    case = item["source"]
    num = int(case["internal_draft"].rsplit("/", 1)[1])
    sha = "a" * 40
    return {"html_url": case["github_native_evidence"],
            "repository": {"full_name": "opensiro/upstream"},
            "status": "completed", "conclusion": "success", "head_sha": sha,
            "pull_requests": [{"number": num, "head": {"sha": sha}}]}


class FakeAPI:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def get(self, path):
        self.calls.append(path)
        value = self.responses[path]
        if value == "404":
            raise HTTPError("https://api.github.com" + path, 404,
                            "Not Found", {}, io.BytesIO())
        return value


def pr_path(url):
    repo, number = outcomes.portfolio_reconcile.identity(url)
    return f"/repos/{repo}/pulls/{number}"


def improved_api(item, pr=None, run=None):
    case = item["source"]
    run_id = case["github_native_evidence"].rsplit("/", 1)[1]
    data = {pr_path(item["pr_urls"][0]): pr or pr_payload(item),
            f"/repos/opensiro/upstream/actions/runs/{run_id}": run or native_run(item)}
    old, new = case["external_pr_head_sha"], case["merged_pr_head_sha"]
    if old != new:
        data[f"/repos/{case['public_fork']}/compare/{old}...{new}"] = {
            "status": "ahead", "base_commit": {"sha": old},
            "merge_base_commit": {"sha": old}, "total_commits": 2,
            "commits": [{}, {}],
            "files": [{"status": "modified", "filename": ".github/workflows/hol-plugin-scanner.yml"}]}
    return FakeAPI(data)


class VerifiedExternalOutcomeTests(unittest.TestCase):
    def test_owner_ledgers_cover_exact_portfolio_with_one_replacement_chain(self):
        items, blocked = outcomes.cohort()
        self.assertEqual((len(items), sum(len(x["pr_urls"]) for x in items), blocked),
                         (38, 39, 21))
        self.assertEqual(len([x for x in items if x["kind"] == "improvement"]), 2)
        self.assertEqual(len([x for x in items if x["kind"] == "corrective"]), 13)
        self.assertEqual(len([x for x in items if x["kind"] == "casebook"]), 8)
        self.assertEqual(len([x for x in items if x["kind"] == "registry"]), 1)
        self.assertEqual(len([x for x in items if x["kind"] == "publication"]), 14)
        self.assertIn("publication:knowwork-sandbox-start-race",
                      {x["id"] for x in items})
        self.assertIn("publication:runloop-budget-finalization-idempotency",
                      {x["id"] for x in items})
        self.assertIn("publication:yoagent-file-alias-lock", {x["id"] for x in items})
        self.assertIn("publication:clouds-coder-frozen-revision-retry-guard", {x["id"] for x in items})
        self.assertIn("publication:phax-cross-run-overlap-reconciliation", {x["id"] for x in items})
        self.assertIn("publication:codeact-same-session-first-kernel-race",
                      {x["id"] for x in items})
        self.assertEqual(len([x for x in items if len(x["pr_urls"]) > 1]), 1)
        self.assertRegex(outcomes.digest_sources(), r"^[0-9a-f]{64}$")

    def test_publication_readback_is_not_a_verified_adoption_even_after_merge(self):
        item = next(x for x in outcomes.cohort()[0]
                    if x["id"] == "publication:dark-factory")
        url = item["pr_urls"][0]
        repo, number = outcomes.portfolio_reconcile.identity(url)
        pr = {"html_url": url, "number": number, "state": "closed",
              "merged_at": "2026-11-10T16:44:55Z", "merge_commit_sha": "a" * 40,
              "user": {"login": "xLagerFeuer"},
              "head": {"sha": item["source"]["head_sha"]},
              "base": {"repo": {"full_name": repo}}}
        record = outcomes.evaluate(FakeAPI({pr_path(url): pr}), item)
        self.assertEqual(record["status"], "PENDING_REVIEW")
        self.assertEqual(record["reason_codes"],
                         ["PUBLICATION_ONLY_REQUIRES_SEMANTIC_REVIEW"])
        self.assertEqual(record["source_ledger"], item["source_path"])

    def test_verified_requires_exact_external_merge_and_native_ci_run(self):
        item = improved_case()
        api = improved_api(item)
        record = outcomes.evaluate(api, item)
        self.assertEqual((record["status"], record["reason_codes"]), ("VERIFIED", []))
        self.assertEqual(len(api.calls), 2)
        self.assertEqual(record["merge_commit_sha"], item["source"]["merge_commit_sha"])

    def test_citadel_published_head_delta_requires_complete_workflow_only_compare(self):
        item = next(x for x in outcomes.cohort()[0]
                    if x["id"] == "improvement:citadel-native-claim-exclusivity")
        api = improved_api(item)
        record = outcomes.evaluate(api, item)
        self.assertEqual(record["status"], "VERIFIED")
        self.assertEqual(len(api.calls), 3)
        self.assertIn("/compare/", record["source_delta_url"])
        compare_path = next(x for x in api.calls if "/compare/" in x)

        changed = improved_api(item)
        changed.responses[compare_path]["files"] = [
            {"status": "modified", "filename": "src/runtime.ts"}]
        record = outcomes.evaluate(changed, item)
        self.assertEqual(record["status"], "PENDING_REVIEW")
        self.assertIn("UNVERIFIED_POST_PUBLICATION_SOURCE_DELTA", record["reason_codes"])

        truncated = improved_api(item)
        truncated.responses[compare_path]["total_commits"] = 101
        record = outcomes.evaluate(truncated, item)
        self.assertIn("UNVERIFIED_POST_PUBLICATION_SOURCE_DELTA", record["reason_codes"])

    def test_pr_merge_alone_does_not_verify_mismatched_contributor(self):
        item = improved_case()
        pr = pr_payload(item)
        pr["user"]["login"] = "not-our-contributor"
        record = outcomes.evaluate(improved_api(item, pr=pr), item)
        self.assertEqual(record["status"], "PENDING_REVIEW")
        self.assertIn("CONTRIBUTOR_ACTOR_MISMATCH", record["reason_codes"])

    def test_changed_head_or_merge_receipt_does_not_count(self):
        item = improved_case()
        pr = pr_payload(item)
        pr["head"]["sha"] = "f" * 40
        pr["merge_commit_sha"] = "e" * 40
        record = outcomes.evaluate(improved_api(item, pr=pr), item)
        self.assertEqual(record["status"], "PENDING_REVIEW")
        self.assertIn("MERGED_HEAD_DRIFT", record["reason_codes"])
        self.assertIn("MERGE_RECEIPT_DRIFT", record["reason_codes"])

    def test_own_merge_is_not_first_party_disposition(self):
        item = improved_case()
        pr = pr_payload(item)
        pr["merged_by"]["login"] = item["actor"]
        record = outcomes.evaluate(improved_api(item, pr=pr), item)
        self.assertIn("FIRST_PARTY_DISPOSITION_NOT_ATTESTED", record["reason_codes"])

    def test_unlinked_or_failed_native_run_is_not_acceptable(self):
        item = improved_case()
        run = native_run(item)
        run["pull_requests"] = []
        run["conclusion"] = "failure"
        record = outcomes.evaluate(improved_api(item, run=run), item)
        self.assertEqual(record["status"], "PENDING_REVIEW")
        self.assertIn("NATIVE_CI_RUN_NOT_LINKED_TO_INTERNAL_PR", record["reason_codes"])

    def test_open_and_closed_unmerged_are_not_verified(self):
        item = improved_case()
        opened = outcomes.evaluate(improved_api(item, pr=pr_payload(item, state="open", merged=False)), item)
        self.assertEqual(opened["status"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(len(improved_api(item).calls), 0)
        closed = outcomes.evaluate(improved_api(item, pr=pr_payload(item, merged=False)), item)
        self.assertEqual(closed["status"], "PENDING_REVIEW")

    def test_corrective_merged_with_mutable_receipt_requires_review(self):
        item = next(x for x in outcomes.cohort()[0] if x["kind"] == "corrective")
        url = item["pr_urls"][0]
        repo, number = outcomes.portfolio_reconcile.identity(url)
        pr = {"html_url": url, "number": number, "state": "closed",
              "merged_at": "2026-11-07T00:00:00Z", "merge_commit_sha": "a" * 40,
              "user": {"login": item["source"]["actor"]},
              "head": {"sha": item["source"]["head_sha"]},
              "base": {"repo": {"full_name": repo}}}
        record = outcomes.evaluate(FakeAPI({pr_path(url): pr}), item)
        self.assertEqual(record["status"], "PENDING_REVIEW")
        self.assertIn("MUTABLE_OR_MISSING_NATIVE_RECEIPT", record["reason_codes"])
        self.assertIn("PUBLICATION_LEDGER_NOT_YET_REVIEWED_AS_COMPLETED", record["reason_codes"])

    def test_henterprise_replacement_counts_as_one_semantic_review(self):
        item = next(x for x in outcomes.cohort()[0] if len(x["pr_urls"]) == 2)
        original, landing = item["pr_urls"]
        repo, number = outcomes.portfolio_reconcile.identity(original)
        _, replacement_number = outcomes.portfolio_reconcile.identity(landing)
        base = {"repo": {"full_name": repo}}
        api = FakeAPI({pr_path(original): {"html_url": original, "number": number,
                                               "base": base, "state": "closed", "merged_at": None},
                       pr_path(landing): {"html_url": landing, "number": replacement_number,
                                              "base": base, "state": "closed",
                                              "merged_at": "2026-11-01T00:00:00Z",
                                              "merge_commit_sha": "b" * 40}})
        row = outcomes.evaluate(api, item)
        self.assertEqual(row["status"], "PENDING_REVIEW")
        self.assertEqual(row["pr_states"], ["closed_unmerged", "merged"])

    def test_known_404_is_unverifiable_not_accepted(self):
        item = next(x for x in outcomes.cohort()[0]
                    if outcomes.portfolio_reconcile.KNOWN_404 in x["pr_urls"])
        row = outcomes.evaluate(FakeAPI({pr_path(item["pr_urls"][0]): "404"}), item)
        self.assertEqual(row["status"], "UNVERIFIABLE")

    def test_wrong_pr_identity_fails_closed(self):
        item = improved_case()
        pr = pr_payload(item)
        pr["html_url"] = "https://github.com/Else/where/pull/1"
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            outcomes.evaluate(improved_api(item, pr=pr), item)

    def test_mutable_branch_and_main_are_not_pinned_native_evidence(self):
        self.assertFalse(outcomes.immutable_native_receipt(
            "https://github.com/opensiro/upstream/blob/main/pilots/foo/CONTRIBUTION_HANDOFF.md"))
        self.assertFalse(outcomes.immutable_native_receipt(
            "https://github.com/opensiro/upstream/blob/research/branch/receipt.md"))
        self.assertTrue(outcomes.immutable_native_receipt(
            "https://github.com/opensiro/upstream/blob/" + "a" * 40 + "/receipt.md"))

    def test_dedup_is_fail_closed_and_no_live_writes_in_cli(self):
        one = improved_case()
        with patch.object(outcomes.upstream_status, "registry_prs", return_value=[
                {"id": "duplicate", "url": one["pr_urls"][0]}]):
            with self.assertRaisesRegex(ValueError, "Duplicate intervention"):
                outcomes.cohort()
        report = {"schema_version": 1, "observed_at": "2026-11-07T00:00:00Z",
                  "source_exclusions": {"corrective_not_published": 21},
                  "counts": {s: 0 for s in outcomes.STATES}, "records": []}
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "outcomes.json"
            argv = ["verified_external_outcomes.py", "--report", "--output-json", str(target)]
            with patch.object(sys, "argv", argv), patch.object(
                    outcomes.pr_maintenance_watch, "Github"), patch.object(
                    outcomes, "observe", return_value=report), patch("builtins.print"):
                outcomes.main()
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), report)
            target.unlink()
            with patch.object(sys, "argv", argv), patch.object(
                    outcomes.pr_maintenance_watch, "Github"), patch.object(
                    outcomes, "observe", side_effect=ValueError("no upstream proof")):
                with self.assertRaisesRegex(ValueError, "no upstream proof"):
                    outcomes.main()
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
