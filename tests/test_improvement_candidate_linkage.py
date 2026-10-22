"""Fail-closed, source-only tests for candidate → existing proposal identity linkage.

All repositories, drafts and promotion-looking claims in these fixtures are synthetic.
No network, GitHub API, live Index attestation, authorization, or write execution.
"""
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from improvement_candidate_linkage import LinkageBlocked, main, preview_linkage  # noqa: E402

REVIEW = "463a6a0a20176147f0b0dbfa8a261aba5e43cbd6"
ASSESSMENT_PATH = "assessments/ag/agentbox.md"
CANDIDATE_ID = "IMPR-AGENTBOX-S2-OVERLAP-20261020"
PROPOSAL_ID = "agentbox-manager-preview"
TARGET = "madarco/agentbox"


def git(root, *args):
    proc = subprocess.run(["git", "-C", str(root), *args],
                          capture_output=True, text=True, check=True)
    return proc.stdout.strip()


class CandidateLinkageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.cards = root / "candidates"
        self.cards.mkdir()
        self.card = self.cards / "agentbox-overlap-manager-20261020.md"
        shutil.copyfile(ROOT / "candidates" / self.card.name, self.card)
        self.index = root / "index"
        self.index.mkdir()
        git(self.index, "init", "-q")
        git(self.index, "config", "user.email", "test@example.invalid")
        git(self.index, "config", "user.name", "Local Test")
        assessment = self.index / ASSESSMENT_PATH
        assessment.parent.mkdir(parents=True)
        assessment.write_text(
            "---\n"
            "harness_id: agentbox\n"
            "repository: https://github.com/madarco/agentbox\n"
            f"review_ref: {REVIEW}\n"
            "status: included\n"
            "autonomy_s1: A\n"
            "autonomy_s2: —\n"
            "autonomy_s3: —\n"
            "autonomy_s3_star: —\n"
            "autonomy_s4: —\n"
            "autonomy_s5: —\n"
            "---\n\n# Synthetic test assessment — NOT canonical\n"
        )
        git(self.index, "add", ".")
        git(self.index, "commit", "-q", "-m", "Synthetic-only local assessment")
        self.index_sha = git(self.index, "rev-parse", "HEAD")
        self.card_edit("index_sha: 5393b698bfdfa4ca14d97a79238234eca20694e5",
                       "index_sha: " + self.index_sha)
        self.manifest = root / "upstream-20261020-linkage-fixture.json"
        self.draft = {
            "schema_version": 1, "batch_id": self.manifest.stem,
            "revision": 1, "status": "proposal_only",
            "candidates": [{
                "id": PROPOSAL_ID,
                "source": TARGET,
                "fork_name": "agentbox",
                "stages": ["prepare_contribution"],
                "expected_license": "MIT",
                "proposal": {
                    "system_component": "Workspace manager brief",
                    "problem": "Independent box work may overlap in intended code files",
                    "planned_change": "Propose opt-in manager grouping before box dispatch",
                    "expected_improvement": "Reduce incompatible independent box task selection",
                    "validation": "Compare native execution before and after grouping",
                    "evidence_url":
                    "https://github.com/madarco/agentbox/blob/main/docs/workspaces-tasks-manager-plan.md",
                },
                "blockers": [],
            }],
        }
        self.save_draft()

    def card_edit(self, before, after):
        s = self.card.read_text()
        self.assertIn(before, s)
        self.card.write_text(s.replace(before, after))

    def save_draft(self):
        self.manifest.write_text(json.dumps(self.draft, indent=2))

    def qualify(self):
        self.card_edit("state: BLOCKED_EVIDENCE", "state: QUALIFIED")
        for key in ("fit_mechanism", "fit_value", "fit_scope"):
            self.card_edit(key + ": PENDING", key + ": PASS")

    def preview(self, **changes):
        kw = {
            "candidate_root": self.cards,
            "candidate_id": CANDIDATE_ID,
            "index_root": self.index,
            "manifest": self.manifest,
            "proposal_id": PROPOSAL_ID,
        }
        kw.update(changes)
        return preview_linkage(**kw)

    def test_real_current_card_blocked(self):
        with self.assertRaisesRegex(LinkageBlocked, "not qualified"):
            self.preview()

    def test_synthetic_matching_identity_only_never_authorizes(self):
        self.qualify()
        original = (self.card.read_bytes(), self.manifest.read_bytes())
        result = self.preview()
        self.assertEqual(result["status"], "OFFLINE_LINKAGE_PREVIEW_ONLY")
        self.assertEqual(result["assessment_path"], ASSESSMENT_PATH)
        self.assertEqual(result["assessed_review_ref"], REVIEW)
        self.assertEqual(result["improvement_candidate_id"], CANDIDATE_ID)
        self.assertEqual(result["proposal_id"], PROPOSAL_ID)
        self.assertEqual(result["origin_class"], "ASSESSMENT_DERIVED")
        self.assertEqual(result["proposal_status"], "proposal_only")
        for key in ("candidate_selection_authenticated", "candidate_native_fit_verified",
                    "live_index_verified", "upstream_source_freshness_verified",
                    "proposal_created", "execution_available"):
            self.assertFalse(result[key], key)
        self.assertEqual(result["authorization_status"], "NOT_APPROVED_NO_GITHUB_WRITES")
        self.assertEqual((self.card.read_bytes(), self.manifest.read_bytes()), original)

    def test_selected_still_not_authorized(self):
        self.qualify()
        self.card_edit("state: QUALIFIED", "state: SELECTED")
        result = self.preview()
        self.assertFalse(result["candidate_selection_authenticated"])
        self.assertFalse(result["execution_available"])

    def test_informed_origin_not_laundered_into_derived(self):
        self.qualify()
        self.card_edit("origin_class: ASSESSMENT_DERIVED",
                       "origin_class: ASSESSMENT_INFORMED")
        self.assertEqual(self.preview()["origin_class"], "ASSESSMENT_INFORMED")

    def test_generic_origin_does_not_get_derived_path(self):
        self.qualify()
        self.card_edit("origin_class: ASSESSMENT_DERIVED",
                       "origin_class: GENERAL_UPSTREAM")
        with self.assertRaises(LinkageBlocked):
            self.preview()

    def test_pretended_qualified_with_pending_fit_rejected(self):
        self.card_edit("state: BLOCKED_EVIDENCE", "state: QUALIFIED")
        with self.assertRaisesRegex(LinkageBlocked, "Blocked candidate"):
            self.preview()

    def test_stale_local_index_pin_rejected(self):
        self.qualify()
        self.card_edit("index_sha: " + self.index_sha,
                       "index_sha: " + ("0" * 40))
        with self.assertRaisesRegex(LinkageBlocked, "HEAD differs"):
            self.preview()

    def test_mismatched_review_ref_rejected(self):
        self.qualify()
        self.card_edit("review_ref: " + REVIEW, "review_ref: " + ("1" * 40))
        with self.assertRaisesRegex(LinkageBlocked, "revision differs"):
            self.preview()

    def test_mismatched_target_rejected(self):
        self.qualify()
        self.draft["candidates"][0]["source"] = "someone/other"
        self.save_draft()
        with self.assertRaisesRegex(LinkageBlocked, "target differs"):
            self.preview()

    def test_mismatched_assessment_path_rejected(self):
        self.qualify()
        self.card_edit("assessment_path: " + ASSESSMENT_PATH,
                       "assessment_path: assessments/zz/zztarget.md")
        with self.assertRaises(LinkageBlocked):
            self.preview()

    def test_proposal_blockers_rejected(self):
        self.qualify()
        self.draft["candidates"][0]["blockers"] = ["First-party design needs confirmation"]
        self.save_draft()
        with self.assertRaisesRegex(LinkageBlocked, "still has blockers"):
            self.preview()

    def test_invalid_proposal_or_unknown_id_rejected(self):
        self.qualify()
        with self.assertRaisesRegex(LinkageBlocked, "missing or ambiguous"):
            self.preview(proposal_id="different-id")
        self.draft["candidates"][0]["expected_license"] = "UNKNOWN"
        self.save_draft()
        with self.assertRaises(LinkageBlocked):
            self.preview()

    def test_duplicate_improvement_id_fails_before_linkage(self):
        self.qualify()
        (self.cards / "duplicate.md").write_text(self.card.read_text())
        with self.assertRaisesRegex(LinkageBlocked, "Duplicate candidate ID"):
            self.preview()

    def test_disagreeing_candidate_selector_rejected(self):
        self.qualify()
        with self.assertRaisesRegex(LinkageBlocked, "Unknown or duplicate"):
            self.preview(candidate_id="IMPR-NONEXISTENT")

    def test_multiple_research_candidates_same_target_do_not_auto_combine(self):
        self.qualify()
        alternate = self.cards / "alternate-agentbox.md"
        second_id = "IMPR-AGENTBOX-ALTERNATE-20261020"
        alternate.write_text(
            self.card.read_text().replace(CANDIDATE_ID, second_id)
            .replace("state: QUALIFIED", "state: PARKED")
        )
        result = self.preview()
        self.assertEqual(result["improvement_candidate_id"], CANDIDATE_ID)
        self.assertEqual(result["proposal_id"], PROPOSAL_ID)
        with self.assertRaisesRegex(LinkageBlocked, "not qualified"):
            self.preview(candidate_id=second_id)

    def test_existing_batch_rejects_two_items_for_same_upstream(self):
        self.qualify()
        duplicate = dict(self.draft["candidates"][0])
        duplicate["id"] = "another-proposal-row"
        self.draft["candidates"].append(duplicate)
        self.save_draft()
        with self.assertRaisesRegex(LinkageBlocked, "Duplicate candidate ID or upstream source"):
            self.preview()

    def test_cli_json_preview_only(self):
        self.qualify()
        args = ["--candidate-root", str(self.cards), "--candidate-id", CANDIDATE_ID,
                "--index-root", str(self.index), "--manifest", str(self.manifest),
                "--proposal-id", PROPOSAL_ID]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(main(args), 0)
        result = json.loads(out.getvalue())
        self.assertFalse(result["execution_available"])
        self.assertFalse(result["candidate_selection_authenticated"])
        self.assertEqual(result["authorization_status"], "NOT_APPROVED_NO_GITHUB_WRITES")
        self.card_edit("state: QUALIFIED", "state: BLOCKED_EVIDENCE")
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(args), 2)


if __name__ == "__main__":
    unittest.main()
