"""Read-only tests for the cross-plugin organization-fork bootstrap proposal."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import contribution_workspaces as workspaces  # noqa: E402
import fork_bootstrap_manifest as bootstrap  # noqa: E402


class ForkBootstrapProposalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proposal = bootstrap.build()

    def test_all_sources_preserved_and_negative_cases_held(self):
        report = self.proposal
        self.assertEqual(report["counts"]["sources"], 183)
        self.assertEqual(report["counts"]["priority_sources"], 100)
        self.assertEqual(report["counts"]["additive_extras"], 83)
        self.assertEqual(report["counts"]["by_state"]["RECHECK_MAPPED_FORK"], 16)
        self.assertEqual(report["counts"]["by_state"]["HOLD_LICENSE_REVIEW"], 5)
        self.assertEqual(report["counts"]["collision_name_proposals"], 10)
        by_source = {r["source"].casefold(): r for r in report["sources"]}
        self.assertEqual(by_source["harnessdesk/harnessdesk"]["state"],
                         "RECHECK_MAPPED_FORK")
        self.assertEqual(by_source["openjiuwen-ai/agent-runtime"]["state"],
                         "HOLD_HISTORICAL_OR_NEGATIVE_CASE")
        self.assertEqual(by_source["qin-sor/agent-context-lab"]["state"],
                         "HOLD_LICENSE_REVIEW")
        self.assertEqual(by_source["shep-ai/shep"]["state"],
                         "HOLD_HISTORICAL_OR_NEGATIVE_CASE")
        self.assertEqual(report["state"], "READ_ONLY_PROPOSAL_NOT_APPROVED")
        self.assertEqual(report["authority"]["one_use_revocable_batch_grant"],
                         "NOT_ISSUED")
        self.assertFalse(report["authority"]["auto_external_pr"])

    def test_unique_fork_name_candidates_including_collisions(self):
        names = [r["candidate_fork"].casefold() for r in self.proposal["sources"]]
        self.assertEqual(len(names), len(set(names)))
        by_source = {r["source"].casefold(): r for r in self.proposal["sources"]}
        original = by_source["phoenixrr2113/agent-harness"]
        proposed = by_source["talktorana/agent-harness"]
        self.assertEqual(original["candidate_fork"],
                         "opensiro-contributions/agent-harness")
        self.assertEqual(proposed["candidate_fork"],
                         "opensiro-contributions/talktorana--agent-harness")
        self.assertTrue(proposed["collision_name_proposal"])
        self.assertTrue(proposed["requires_fresh_source_license_policy_and_destination_checks"])
        self.assertFalse(original["collision_name_proposal"])

    def test_batches_bind_exact_sources_names_stage_and_registry(self):
        report = self.proposal
        selected = [row for batch in report["batches"] for row in batch["selection"]]
        expected = [r for r in report["sources"]
                    if r["state"] == "PROPOSE_CREATE_REQUIRES_LIVE_PREFLIGHT"]
        self.assertEqual(len(selected), len(expected))
        self.assertEqual(len(report["batches"]), (len(expected) + 9) // 10)
        self.assertTrue(all(1 <= b["source_count"] <= 10
                            and b["state"] == "UNAPPROVED_REQUIRES_TRUSTED_PREFLIGHT"
                            for b in report["batches"]))
        self.assertEqual(selected, [{"source": r["source"],
                                     "candidate_fork": r["candidate_fork"]}
                                    for r in expected])
        for batch in report["batches"]:
            envelope = {"stage": "create_public_fork",
                        "destination_org": report["destination_org"],
                        "selection": batch["selection"],
                        "registry_sha256": report["source_registry_sha256"]}
            self.assertEqual(batch["selection_sha256"], bootstrap.digest(envelope))

    def test_digest_cannot_stay_equal_if_selection_changes(self):
        batch = self.proposal["batches"][0]
        copied = copy.deepcopy(batch["selection"])
        before = bootstrap.digest(copied)
        copied[0]["candidate_fork"] += "-unreviewed"
        self.assertNotEqual(before, bootstrap.digest(copied))

    def test_generated_proposal_is_deterministic_and_current(self):
        self.assertEqual(self.proposal, bootstrap.build())
        saved = json.loads((ROOT / bootstrap.OUTPUT).read_text(encoding="utf-8"))
        self.assertEqual(saved, self.proposal)
        r = subprocess.run(["python3", str(ROOT / "scripts/fork_bootstrap_manifest.py"),
                            "check"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_priority_pool_omission_is_rejected(self):
        inventory = workspaces.build()
        inventory["sources"] = [x for x in inventory["sources"]
                                if x["source"].casefold() != "harnessdesk/harnessdesk"]
        inventory["counts"]["unique_sources"] -= 1
        with self.assertRaisesRegex(workspaces.WorkspaceError, "Priority identity missing"):
            bootstrap.build(inventory=inventory)

    def test_newly_worked_source_propagates_into_next_bootstrap_proposal(self):
        inventory = workspaces.build()
        inventory["sources"].append({
            "source": "later-contributor/new-harness",
            "priority_group": "HISTORICAL_EXTRA", "next_step": "SCREEN_BEFORE_FORK_WRITE",
            "latest_stage": "SCREENING", "fork": None,
            "fork_state": "UNVERIFIED_NOT_PROVISIONED",
            "proposed_fork": "opensiro-contributions/new-harness",
            "license_review": False,
        })
        inventory["counts"]["unique_sources"] += 1
        new = bootstrap.build(inventory=inventory)
        self.assertEqual(new["counts"]["sources"], 184)
        self.assertEqual(new["counts"]["priority_sources"], 100)
        self.assertNotEqual(new["source_registry_sha256"],
                            self.proposal["source_registry_sha256"])
        added = next(row for row in new["sources"]
                     if row["source"] == "later-contributor/new-harness")
        self.assertEqual(added["state"],
                         "PROPOSE_CREATE_REQUIRES_LIVE_PREFLIGHT")

    def test_candidate_name_colliding_with_existing_fork_fails_closed(self):
        inventory = workspaces.build()
        by_source = {r["source"].casefold(): r for r in inventory["sources"]}
        # Simulate mistaken reservation of a real fork name for another source.
        by_source["talktorana/agent-harness"]["proposed_fork"] = (
            "opensiro-contributions/agent-harness")
        with self.assertRaisesRegex(workspaces.WorkspaceError,
                                    "Proposed destination collision"):
            bootstrap.build(inventory=inventory)


if __name__ == "__main__":
    unittest.main()
