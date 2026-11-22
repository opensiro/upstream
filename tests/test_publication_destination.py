"""Fail-closed provider destination/channel route regression tests."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from preflight_publication_destination import route_errors, feature_form_requirements, feature_form_payload_errors, expected_source_head_errors, markdown_feature_template_requirements, markdown_feature_payload_errors

AG2 = "ag2ai/ag2"
FORK = "opensiro-contributions/ag2"
CLINE = "cline/cline"


def repo(name, **changes):
    data = {"full_name": name, "private": False, "archived": False, "disabled": False,
            "fork": False, "has_issues": True, "has_discussions": True,
            "default_branch": "main"}
    data.update(changes)
    return data


class PublicationDestinationTests(unittest.TestCase):
    def test_original_form_requires_native_headings_and_human_review(self):
        form = ("name: Feature request\n"
                'title: "feat: "\n'
                "body:\n  - type: textarea\n    attributes:\n      label: Motivation\n"
                "    validations:\n      required: true\n"
                "  - type: checkboxes\n    attributes:\n      label: Authorship\n"
                "      options:\n        - label: A human has read this issue and stands behind it.\n"
                "          required: true\n")
        spec = feature_form_requirements(form)
        self.assertEqual(spec["title_prefix"], "feat:")
        self.assertIn("Motivation", spec["required_fields"])
        self.assertEqual(len(spec["required_checkboxes"]), 1)
        errors = feature_form_payload_errors(
            spec, "Proposal: unsupported", "## OpenSiro VSM roadmap\nSome prose\n")
        self.assertNotIn("NATIVE_FEATURE_TITLE_PREFIX_MISMATCH", errors)
        self.assertTrue(any("Motivation" in e for e in errors))
        self.assertTrue(any("human has read" in e for e in errors))
        complete = ("### Motivation\nObserved user problem\n"
                    "- [x] A human has read this issue and stands behind it.\n")
        self.assertEqual(feature_form_payload_errors(spec,"feat: proposal",complete), [])
        self.assertEqual(feature_form_payload_errors(spec,"Proposal: external architecture",complete), [])
        self.assertIn("NATIVE_FEATURE_TITLE_MISSING",feature_form_payload_errors(spec,"",complete))

    def test_original_head_drift_is_fatal_even_when_form_fits(self):
        old = "f4627bc5a305450b2cb93967ae631324c9a9ce22"
        new = "a47ce14d1d187fc17fa8f56d12e5d5e59874f655"
        self.assertEqual(expected_source_head_errors(old, new), ["ORIGINAL_SOURCE_HEAD_DRIFTED"])
        self.assertEqual(expected_source_head_errors(new, new), [])

    def test_missing_original_pin_fails_closed(self):
        self.assertIn("ORIGINAL_SOURCE_HEAD_NOT_PINNED",
                      expected_source_head_errors("", "a"*40))

    def test_legacy_markdown_feature_template_without_config_is_supported(self):
        self.assertEqual(route_errors(
            "gastownhall/gastown","gastownhall/gastown","original_issue",
            "feature_request", repo("gastownhall/gastown"),
            [{"name":"feature_request.md"}], None), [])
        template = ("---\nname: Feature Request\nabout: Suggest a feature\n---\n"
                    "## Problem Statement\n<!-- Describe problem -->\n"
                    "## Proposed Solution\n<!-- Describe solution -->\n")
        spec = markdown_feature_template_requirements(template)
        self.assertEqual(len(spec["required_sections"]),2)
        errors = markdown_feature_payload_errors(spec,"## Opensiro methodology\nIdeas\n")
        self.assertEqual(len(errors),2)
        body = "## Problem Statement\nReal issue\n## Proposed Solution\nConcrete alternative\n"
        self.assertEqual(markdown_feature_payload_errors(spec,body), [])
        empty = "## Problem Statement\n<!-- TODO -->\n## Proposed Solution\nConcrete alternative\n"
        self.assertTrue(any("UNFILLED" in x for x in markdown_feature_payload_errors(spec,empty)))

    def test_unknown_markdown_feature_template_fails_closed(self):
        with self.assertRaises(ValueError):
            markdown_feature_template_requirements("## Not native form")

    def test_unknown_issue_form_stops_preflight(self):
        for text in ("", "body:\n  - type: new_nonstandard_type\n", "name: No form"):
            with self.assertRaises(ValueError):
                feature_form_requirements(text)

    def test_disabled_fork_issue_blocks_before_text_draft(self):
        errors = route_errors(FORK, AG2, "fork_issue", "feature_request",
                              repo(FORK, fork=True, parent={"full_name": AG2},
                                   has_issues=False))
        self.assertIn("ISSUES_DISABLED", errors)

    def test_original_ag2_feature_template_is_supported(self):
        self.assertEqual(route_errors(
            AG2, AG2, "original_issue", "feature_request", repo(AG2),
            [{"name": "feature_request.yml"}, {"name": "config.yml"}],
            "blank_issues_enabled: true"), [])

    def test_cline_original_issue_must_not_bypass_discussions_channel(self):
        errors = route_errors(CLINE, CLINE, "original_issue", "feature_request",
                              repo(CLINE),
                              [{"name": "bug_report.yml"}, {"name": "config.yml"}],
                              "blank_issues_enabled: false\n"
                              "url: https://github.com/cline/cline/discussions/categories/feature-requests")
        self.assertIn("FEATURE_REQUEST_ROUTED_TO_DISCUSSIONS", errors)

    def test_cline_discussion_category_supported(self):
        self.assertEqual(route_errors(
            CLINE, CLINE, "original_discussion", "feature_request", repo(CLINE),
            categories=[{"slug": "feature-requests", "name": "Feature Requests",
                         "id": "DIC_1"}]), [])

    def test_cannot_publish_fork_issue_to_original(self):
        self.assertIn("NOT_A_WORKING_FORK",
                      route_errors(AG2, AG2, "fork_issue", "feature_request", repo(AG2)))

    def test_cannot_publish_original_issue_to_fork(self):
        errs = route_errors(FORK, AG2, "original_issue", "feature_request",
                            repo(FORK, fork=True, parent={"full_name": AG2}),
                            [{"name": "feature_request.yml"}], "blank_issues_enabled: true")
        self.assertIn("ORIGINAL_REPOSITORY_MISMATCH", errs)

    def test_fork_parent_must_match_exact_original(self):
        errs = route_errors(FORK, AG2, "fork_issue", "feature_request",
                            repo(FORK, fork=True, parent={"full_name": CLINE}))
        self.assertIn("FORK_PARENT_MISMATCH", errs)

    def test_private_and_archived_repos_fail_closed(self):
        errs = route_errors(AG2, AG2, "original_issue", "feature_request",
                            repo(AG2, private=True, archived=True),
                            [{"name": "feature_request.yml"}], "blank_issues_enabled: true")
        self.assertIn("PUBLIC_REPOSITORY_NOT_VERIFIED", errs)
        self.assertIn("REPOSITORY_NOT_ACTIVE", errs)

    def test_missing_config_and_template_blocks(self):
        errs = route_errors(AG2, AG2, "original_issue", "feature_request",
                            repo(AG2), templates=None, config=None)
        self.assertIn("ISSUE_CHANNEL_EVIDENCE_UNVERIFIED", errs)

    def test_both_feature_issue_and_discussion_route_is_ambiguous(self):
        errs = route_errors(AG2, AG2, "original_issue", "feature_request",
                            repo(AG2), [{"name": "feature_request.yml"}],
                            "url: https://github.com/ag2ai/ag2/discussions/categories/feature-requests")
        self.assertIn("FEATURE_REQUEST_CHANNEL_AMBIGUOUS", errs)

    def test_disabled_discussion_or_missing_category_blocks(self):
        errs = route_errors(CLINE, CLINE, "original_discussion", "feature_request",
                            repo(CLINE, has_discussions=False), categories=[])
        self.assertIn("DISCUSSIONS_DISABLED", errs)
        self.assertIn("FEATURE_REQUEST_DISCUSSION_CATEGORY_MISSING", errs)

    def test_missing_category_evidence_blocks(self):
        self.assertIn("DISCUSSION_CATEGORY_UNVERIFIED",
                      route_errors(CLINE, CLINE, "original_discussion", "feature_request",
                                   repo(CLINE), categories=None))

    def test_unsupported_user_purpose_or_bad_repo_blocks(self):
        self.assertEqual(route_errors("fake repo", AG2, "fork_issue", "feature_request",
                                      repo(AG2)), ["INVALID_REPOSITORY_IDENTITY"])
        self.assertEqual(route_errors(AG2, AG2, "new_pr", "feature_request",
                                      repo(AG2)), ["UNSUPPORTED_ACTION_OR_PURPOSE"])


if __name__ == "__main__":
    unittest.main()
