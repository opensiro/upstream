"""Accepted external outcome ledger must fail closed on counterfeit acceptance."""

from collections import Counter
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import accepted_external_outcomes as accepted
import test_verified_external_outcomes as fixtures
import verified_external_outcomes as observer


DECISION_URL = "https://github.com/opensiro/upstream/pull/177"


def candidate():
    return next(item for item in observer.cohort()[0]
                if item["id"] == "improvement:agent-fleet-native-lease-contract")


def decision(item=None):
    item = item or candidate()
    src = item["source"]
    return {"intervention_id": item["id"],
            "source_pr_urls": item["pr_urls"],
            "effective_pr_url": item["pr_urls"][-1],
            "merge_commit_sha": src["merge_commit_sha"],
            "merged_at": src["merged_at"],
            "native_receipt": src["github_native_evidence"],
            "decision_actor": "xLagerFeuer",
            "decision_pr_url": DECISION_URL,
            "decision": "ACCEPTED_MERGED_CHANGE_ONLY",
            "benefit_claim": "NOT_MEASURED"}


def proposed_ledger(*rows):
    return {"schema_version": 1, "scope": "opensiro/upstream", "accepted": list(rows)}


def validate_local(ledger):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "proposed.json"
        path.write_text(json.dumps(ledger), encoding="utf-8")
        return accepted.load_ledger(path)


def fake_report(accepted_item=None):
    records = []
    for item in observer.cohort()[0]:
        records.append({"id": item["id"], "kind": item["kind"],
                        "pr_urls": item["pr_urls"], "pr_states": ["open"] * len(item["pr_urls"]),
                        "status": "INSUFFICIENT_EVIDENCE",
                        "reason_codes": ["EXTERNAL_PR_NOT_MERGED"],
                        "merged_at": None, "merge_commit_sha": None})
    if accepted_item:
        actual = observer.evaluate(fixtures.improved_api(accepted_item), accepted_item)
        index = next(i for i, row in enumerate(records) if row["id"] == accepted_item["id"])
        records[index] = actual
    counts = Counter(row["status"] for row in records)
    return {"schema_version": 1, "observed_at": datetime.now(timezone.utc).isoformat(),
            "source_sha256": observer.digest_sources(),
            "portfolio_cohort_sha256": observer.portfolio_reconcile.cohort_fingerprint(
                observer.portfolio_reconcile.cohort()),
            "source_exclusions": {"corrective_not_published": observer.cohort()[1]},
            "counts": {key: counts[key] for key in observer.STATES},
            "metric_status": "CANDIDATE_ONLY_NOT_ORGANIZATION_CLAIMED",
            "records": records}


def owner_decision_api(item=None):
    item = item or candidate()
    api = fixtures.improved_api(item)
    api.responses["/repos/opensiro/upstream/pulls/177"] = {
        "html_url": DECISION_URL,
        "state": "closed", "merged_at": "2026-11-08T16:02:00Z",
        "user": {"login": "xLagerFeuer"},
        "merged_by": {"login": "xLagerFeuer"},
        "head": {"sha": "a" * 40},
        "base": {"repo": {"full_name": "opensiro/upstream"}},
        "body": "\n".join((f"Outcome-Acceptance: {item['id']}",
                          f"Outcome-Merge: {item['source']['merge_commit_sha']}",
                          f"Outcome-Native-Receipt: {item['source']['github_native_evidence']}"))}
    return api


class AcceptedExternalOutcomeTests(unittest.TestCase):
    def test_empty_versioned_ledger_stays_unclaimed(self):
        ledger = accepted.load_ledger()
        self.assertEqual(ledger, proposed_ledger())
        result = accepted.verify_accepted(ledger, fake_report(), None)
        self.assertEqual(result["accepted_count"], 0)
        self.assertEqual(result["metric_status"], "UNCLAIMED_SEMANTIC_EVIDENCE")
        self.assertFalse(result["organization_metric_claimed"])

    def test_valid_owner_decision_is_source_only_not_organization_kpi(self):
        item = candidate()
        ledger = validate_local(proposed_ledger(decision(item)))
        result = accepted.verify_accepted(ledger, fake_report(item), owner_decision_api(item))
        self.assertEqual(result["accepted_count"], 1)
        self.assertEqual(result["metric_status"], "UPSTREAM_REVIEWED_SOURCE_ONLY")
        self.assertFalse(result["organization_metric_claimed"])
        self.assertEqual(result["accepted"][0]["owner_decision"], DECISION_URL)

    def test_duplicate_id_or_decision_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate accepted"):
            validate_local(proposed_ledger(decision(), decision()))

    def test_replacement_chain_cannot_be_split_or_substituted(self):
        item = next(x for x in observer.cohort()[0] if len(x["pr_urls"]) == 2)
        row = decision()
        row["intervention_id"] = item["id"]
        row["source_pr_urls"] = [item["pr_urls"][-1]]
        row["effective_pr_url"] = item["pr_urls"][-1]
        with self.assertRaisesRegex(ValueError, "replacement chain"):
            validate_local(proposed_ledger(row))

    def test_mutable_receipt_cannot_be_accepted(self):
        row = decision()
        row["native_receipt"] = "https://github.com/opensiro/upstream/blob/main/README.md"
        with self.assertRaisesRegex(ValueError, "immutable"):
            validate_local(proposed_ledger(row))

    def test_owner_may_also_be_contributor_without_s3star_review(self):
        self.assertEqual(candidate()["actor"], "xLagerFeuer")
        self.assertEqual(validate_local(proposed_ledger(decision()))["accepted"][0]
                         ["decision_actor"], "xLagerFeuer")

    def test_unattributed_non_owner_decision_cannot_be_accepted(self):
        row = decision()
        row["decision_actor"] = "unrelated-contributor"
        with self.assertRaisesRegex(ValueError, "decision owner"):
            validate_local(proposed_ledger(row))

    def test_unsupported_benefit_claim_or_extra_field_rejected(self):
        row = decision()
        row["benefit_claim"] = "USER_BENEFIT_PROVEN"
        with self.assertRaisesRegex(ValueError, "benefit claim"):
            validate_local(proposed_ledger(row))
        row = decision()
        row["automatic_approval"] = True
        with self.assertRaisesRegex(ValueError, "Incomplete or unknown"):
            validate_local(proposed_ledger(row))

    def test_observer_artifact_missing_duplicate_or_stale_rejected(self):
        report = fake_report(candidate())
        del report["records"][-1]
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            accepted.validate_observation(report)
        report = fake_report(candidate())
        report["records"][1] = copy.deepcopy(report["records"][0])
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            accepted.validate_observation(report)
        report = fake_report(candidate())
        report["source_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "stale"):
            accepted.validate_observation(report)

    def test_machine_pending_review_cannot_be_promoted_by_human_field(self):
        report = fake_report()
        ledger = validate_local(proposed_ledger(decision()))
        with self.assertRaisesRegex(ValueError, "machine-verified"):
            accepted.verify_accepted(ledger, report, owner_decision_api())

    def test_no_api_for_nonempty_acceptance_fails_closed(self):
        ledger = validate_local(proposed_ledger(decision()))
        with self.assertRaisesRegex(ValueError, "Live GitHub"):
            accepted.verify_accepted(ledger, fake_report(candidate()), None)

    def test_github_owner_decision_must_be_merged_and_attributed(self):
        item = candidate()
        ledger = validate_local(proposed_ledger(decision()))
        api = owner_decision_api(item)
        api.responses["/repos/opensiro/upstream/pulls/177"]["merged_by"]["login"] = "another-user"
        with self.assertRaisesRegex(ValueError, "does not attest"):
            accepted.verify_accepted(ledger, fake_report(item), api)

    def test_unrelated_or_unmerged_decision_pr_cannot_authorize_outcome(self):
        item = candidate()
        ledger = validate_local(proposed_ledger(decision()))
        api = owner_decision_api(item)
        api.responses["/repos/opensiro/upstream/pulls/177"]["body"] = "Looks good, unrelated PR."
        with self.assertRaisesRegex(ValueError, "does not attest"):
            accepted.verify_accepted(ledger, fake_report(item), api)
        api = owner_decision_api(item)
        api.responses["/repos/opensiro/upstream/pulls/177"]["merged_at"] = None
        with self.assertRaisesRegex(ValueError, "does not attest"):
            accepted.verify_accepted(ledger, fake_report(item), api)
        api = owner_decision_api(item)
        api.responses["/repos/opensiro/upstream/pulls/177"]["user"]["login"] = "unrelated"
        with self.assertRaisesRegex(ValueError, "does not attest"):
            accepted.verify_accepted(ledger, fake_report(item), api)

    def test_reobserve_external_first_party_evidence_not_only_artifact(self):
        item = candidate()
        ledger = validate_local(proposed_ledger(decision()))
        api = owner_decision_api(item)
        api.responses[fixtures.pr_path(item["pr_urls"][0])]["user"]["login"] = "intruder"
        with self.assertRaisesRegex(ValueError, "current first-party"):
            accepted.verify_accepted(ledger, fake_report(item), api)


if __name__ == "__main__":
    unittest.main()
