"""No-network tests: never invent a review PR or silently reuse stale approval."""
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from upgrade_handoff import render_handoff, validate_body_against_handoff  # noqa: E402

FORK = "opensiro-contributions/openclaw"
BRANCH = "opensiro/upgrade-workboard-197312-recheck"
HEAD = "f" * 40
META = "a" * 40
INDEX = "https://github.com/opensiro/vsm-harness-index/blob/" + "b"*40 + "/assessments/op/openclaw.md"
SOURCE = "https://github.com/openclaw/openclaw/issues/197312"
STATE = {"original_repository": "openclaw/openclaw", "working_fork": FORK,
         "owner_control": "ALLOW", "attention": "ACTIVE"}
CONTRIBUTION = {
    "schema_version": 2,
    "id": "openclaw-workboard-atomic-recheck-197312",
    "original_repository": "openclaw/openclaw",
    "source_revision": "c"*40,
    "contribution_type": "ASSESSMENT_INFORMED",
    "classification_rationale": "A source-first Workboard issue informed by prior S2 Index mapping.",
    "classification_evidence": [SOURCE, INDEX],
    "assessment_pin": {"url": INDEX, "reviewed_at": "2026-09-16", "assessed_source_revision": "d"*40},
    "work_branches": [BRANCH],
    "native_evidence": [SOURCE],
    "validation_summary": {"not_validated": "Full suite not confirmed"},
    "next_action": "Stop publication until actual approval.",
    "handoff_publication_hold": True,
}


def render(**changes):
    args = dict(contribution=CONTRIBUTION, state=STATE, fork=FORK,
                product_branch=BRANCH, product_sha=HEAD, meta_sha=META, base_branch="main")
    args.update(changes)
    return render_handoff(**args)


class UpgradeHandoffTests(unittest.TestCase):
    def test_all_five_links_and_source_context_survive_resumption(self):
        body = render()
        for fragment in (
            f"https://github.com/{FORK})",
            f"/tree/{BRANCH})",
            f"/commit/{HEAD})",
            "Fork-local review PR:** NOT_CREATED — awaiting exact fork-local PR consent",
            f"/blob/{META}/.opensiro/contributions/openclaw-workboard-atomic-recheck-197312.json)",
            SOURCE,
            "ASSESSMENT_INFORMED",
            "Full suite not confirmed",
            "Publication gate:** HOLD",
        ):
            self.assertIn(fragment, body)

    def test_external_submission_requires_actual_review_and_fresh_consent(self):
        with self.assertRaisesRegex(ValueError, "fork-local review PR"):
            render(stage="new")
        with self.assertRaisesRegex(ValueError, "owner STOP"):
            render(stage="new", review_pr_url=f"https://github.com/{FORK}/pull/9")
        resumed = dict(CONTRIBUTION, handoff_publication_hold=False)
        self.assertIn("/pull/9", render(stage="new", contribution=resumed,
                                        review_pr_url=f"https://github.com/{FORK}/pull/9"))

    def test_wrong_fork_and_mismatched_controls_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "mismatch"):
            render(fork="opensiro-contributions/browser-harness")
        with self.assertRaisesRegex(ValueError, "PAUSE/STOP"):
            render(state={**STATE, "owner_control": "PAUSE"})
        with self.assertRaisesRegex(ValueError, "Original issue URL"):
            render(contribution=dict(CONTRIBUTION, classification_evidence=[INDEX]))

    def test_draft_body_must_have_actual_five_links_even_if_approval_was_given(self):
        body = """
<!-- opensiro-ai-assessment-disclosure:review-gated -->
**AI involvement:** Tests and code were AI-assisted.
**Original source request:** https://github.com/openclaw/openclaw/issues/197312
**Improvement origin:** ASSESSMENT_INFORMED — source-backed S2 coordination context.
**VSM assessment (when verified):** No verified matching general VSM assessment
**Native validation:** Focused tests passed.
**Human/publication status:** No external publication.
**Authority:** External maintainers retain discretion.
"""
        with self.assertRaisesRegex(ValueError, "Working fork: required field missing"):
            validate_body_against_handoff(
                body=body, stage="preview", fork=FORK, product_branch=BRANCH,
                product_sha=HEAD, meta_sha=META,
                contribution_id=CONTRIBUTION["id"], review_pr_url=None,
                contribution=CONTRIBUTION,
            )

    def test_wrong_head_branch_review_url_are_not_accepted(self):
        with self.assertRaisesRegex(ValueError, "40-character"):
            render(product_sha="f"*7)
        with self.assertRaisesRegex(ValueError, "not listed"):
            render(product_branch="other")
        with self.assertRaisesRegex(ValueError, "mismatches"):
            render(review_pr_url="https://github.com/opensiro-contributions/ag2/pull/9")


if __name__ == "__main__":
    unittest.main()
