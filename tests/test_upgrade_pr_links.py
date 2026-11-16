"""Regression tests for source-only Upgrade PR disclosure link requirements."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_upgrade_pr_links import validate_pr_links  # noqa: E402


FORK = "https://github.com/opensiro-contributions/browser-harness"
HEAD = "4056c5aece6e4a83ea999d60e42482b84f9eed7b"
META = "a" * 40
REVIEW = f"[Review PR #7]({FORK}/pull/7)"
ASSESSMENT = "854c6e5441709b014c01f803c23311fdf366a354"
REVIEW_REF = "afbcc381b963040c19627d788e40c7e7663171ee"
CURRENT_ASSESSMENT = (
    "https://github.com/opensiro/vsm-harness-index/blob/main/"
    "assessments/br/browser-harness.md"
)
PINNED_ASSESSMENT = (
    f"https://github.com/opensiro/vsm-harness-index/blob/{ASSESSMENT}/"
    "assessments/br/browser-harness.md"
)


def example_body(review=REVIEW):
    return f"""## Summary

A real, native-tested feature.

<!-- opensiro-ai-assessment-disclosure:review-gated -->
## AI-assisted contribution disclosure

**AI involvement:** AI-assisted, without claimed independent human technical review.
**Working fork:** [opensiro-contributions/browser-harness]({FORK})
**Implementation branch:** [opensiro/upgrade-tabs]({FORK}/tree/opensiro/upgrade-tabs)
**Implementation commit:** [{HEAD}]({FORK}/commit/{HEAD})
**Fork-local review PR:** {review}
**Fork-local metadata record:** [tab-reconnect]({FORK}/blob/{META}/.opensiro/contributions/tab-reconnect.json)
**Original source request:** https://github.com/browser-use/browser-harness/issues/998
**Improvement origin:** GENERAL_UPSTREAM — original source request.
**VSM assessment (when verified):** [Current record]({CURRENT_ASSESSMENT}) · [Pinned record]({PINNED_ASSESSMENT})
**Assessment date:** 2026-09-18 (reviewed_at)
**Assessed source revision:** `{REVIEW_REF}`
**Assessment relationship:** context only, no claimed causal VSM derivation.
**Native validation:** pytest -q, 7 passed.
**Human/publication status:** review-gated, no technical certification.
**Authority:** external maintainers retain approval and merge authority.
"""


class UpgradePrLinkTests(unittest.TestCase):
    def test_new_pr_requires_all_same_fork_links_and_assessment_provenance(self):
        self.assertEqual(validate_pr_links(example_body(), stage="new"), [])

    def test_origin_type_requires_canonical_value_and_source_explanation(self):
        invalid = example_body().replace(
            "**Improvement origin:** GENERAL_UPSTREAM — original source request.",
            "**Improvement origin:** VSM_DERIVED — guessed from Index."
        )
        self.assertTrue(any("Improvement origin" in e for e in validate_pr_links(invalid, "new")))
        missing_reason = example_body().replace(
            "**Improvement origin:** GENERAL_UPSTREAM — original source request.",
            "**Improvement origin:** ASSESSMENT_DERIVED — unknown"
        )
        self.assertTrue(any("Improvement origin" in e for e in validate_pr_links(missing_reason, "new")))
        self.assertEqual(validate_pr_links(example_body(), "new"), [])

    def test_missing_review_link_blocks_new_external_publication(self):
        body = example_body("NOT_CREATED — awaiting exact fork-local PR consent")
        self.assertEqual(validate_pr_links(body, stage="preview"), [])
        errors = validate_pr_links(body, stage="new")
        self.assertTrue(any("Fork-local review PR" in e for e in errors))

    def test_historical_unreviewed_pr_is_disclosed_without_fabrication(self):
        body = example_body("NOT_CREATED — historical PR; no prior fork-local review PR")
        self.assertEqual(validate_pr_links(body, stage="historical"), [])
        self.assertTrue(validate_pr_links(body, stage="new"))

    def test_mismatched_organization_fork_cannot_pass(self):
        body = example_body().replace(
            f"{FORK}/commit/{HEAD}",
            f"https://github.com/opensiro-contributions/ag2/commit/{HEAD}",
        )
        self.assertIn("Implementation commit: working fork identity mismatch",
                      validate_pr_links(body, "new"))

    def test_wrong_organization_link_cannot_pass(self):
        body = example_body().replace(
            f"[opensiro-contributions/browser-harness]({FORK})",
            "[opensiro-contributions/browser-harness](https://github.com/opensiro-promotion/browser-harness)",
        )
        errors = validate_pr_links(body, "new")
        self.assertTrue(any("Working fork" in e for e in errors))

    def test_non_pinned_commit_and_meta_are_rejected(self):
        body = example_body().replace(f"/commit/{HEAD}", "/commit/short")
        body = body.replace(f"/blob/{META}/", "/blob/main/")
        errors = validate_pr_links(body, "new")
        self.assertTrue(any("Implementation commit" in e for e in errors))
        self.assertTrue(any("Fork-local metadata record" in e for e in errors))

    def test_missing_source_and_assessment_evidence_rejected(self):
        body = example_body().replace(
            f"**Assessed source revision:** `{REVIEW_REF}`",
            "**Assessed source revision:** UNKNOWN",
        ).replace(f"/blob/{ASSESSMENT}/", "/blob/main/")
        errors = validate_pr_links(body, "new")
        self.assertTrue(any("Assessed source revision" in e for e in errors))
        self.assertTrue(any("VSM assessment" in e for e in errors))

    def test_approved_looking_draft_without_fork_links_is_still_blocked(self):
        body = example_body("NOT_CREATED — awaiting exact fork-local PR consent")
        for label in ("Working fork", "Implementation branch", "Implementation commit",
                      "Fork-local review PR", "Fork-local metadata record"):
            body = "\\n".join(
                line for line in body.splitlines()
                if not line.startswith(f"**{label}:**")
            ) + "\\n"
        self.assertGreaterEqual(len(validate_pr_links(body, "preview")), 5)
        self.assertGreaterEqual(len(validate_pr_links(body, "new")), 5)

    def test_generic_ai_assistance_is_not_valid_disclosure(self):
        errors = validate_pr_links("## AI assistance\nAI helped write code.\n", "new")
        self.assertTrue(any("disclosure marker missing" in e for e in errors))
        self.assertTrue(any("Working fork" in e for e in errors))

    def test_missing_assessment_can_be_truthfully_declared(self):
        body = example_body()
        a = f"**VSM assessment (when verified):** [Current record]({CURRENT_ASSESSMENT}) · [Pinned record]({PINNED_ASSESSMENT})"
        body = body.replace(a, "**VSM assessment (when verified):** No verified matching general VSM assessment")
        body = body.replace("**Assessment date:** 2026-09-18 (reviewed_at)\n", "")
        body = body.replace(f"**Assessed source revision:** `{REVIEW_REF}`\n", "")
        self.assertEqual(validate_pr_links(body, "new"), [])


if __name__ == "__main__":
    unittest.main()
