"""Preserve explicit source classification without fabricating legacy causal claims."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from contribution_classification import classification, validate_new_contribution, UNCLASSIFIED_LEGACY
from aggregate import check_contribution

PIN = "https://github.com/opensiro/vsm-harness-index/blob/" + "a"*40 + "/assessments/br/browser-harness.md"
PREDICTION = "https://github.com/opensiro/upstream-old/blob/" + "b"*40 + "/research/prediction.md"
NATIVE = "https://github.com/browser-use/browser-harness/issues/998"


def sample():
    return {
        "schema_version": 2, "id": "browser-harness-fail-closed-tab-reconnection",
        "original_repository": "browser-use/browser-harness",
        "work_state": "DELIVERED", "external_prs": ["https://github.com/browser-use/browser-harness/pull/1034"],
        "contribution_type": "GENERAL_UPSTREAM",
        "classification_rationale": "Original project issue #998 first established the functional need, not a pinned Index-first prediction.",
        "classification_evidence": [NATIVE]}


class TypeTests(unittest.TestCase):
    def test_original_source_classification(self):
        r = sample()
        self.assertEqual(validate_new_contribution(r), "GENERAL_UPSTREAM")
        self.assertEqual(check_contribution(r, ".opensiro/contributions/"+r["id"]+".json", r["original_repository"]),
                         r["external_prs"])

    def test_v1_legacy_is_visible_but_not_valid_for_new_writes(self):
        r = sample()
        r["schema_version"] = 1
        for key in ("contribution_type","classification_rationale","classification_evidence"):
            r.pop(key)
        self.assertEqual(classification(r), UNCLASSIFIED_LEGACY)
        with self.assertRaisesRegex(ValueError,"schema_version 2"):
            validate_new_contribution(r)

    def test_v2_missing_or_spoofed_type_is_rejected(self):
        for origin in (None, "VSM_DERIVED", "UNCLASSIFIED_LEGACY", "ASSESSMENT_DERIVED"):
            r = sample()
            if origin is None: r.pop("contribution_type")
            else: r["contribution_type"] = origin
            with self.subTest(origin=origin), self.assertRaises(ValueError):
                validate_new_contribution(r)

    def test_wrong_original_evidence_cannot_validate_general(self):
        r=sample()
        r["classification_evidence"]=["https://github.com/other/project/issues/998"]
        with self.assertRaisesRegex(ValueError, "exact original repository"):
            validate_new_contribution(r)

    def test_derived_requires_immutable_pin_and_preimplementation_prediction(self):
        r=sample()
        r["contribution_type"]="ASSESSMENT_DERIVED"
        r["classification_evidence"]=[PIN,PREDICTION]
        r["assessment_pin"]={"url":PIN, "reviewed_at":"2026-09-18","assessed_source_revision":"c"*40}
        r["prior_prediction_url"]=PREDICTION
        r["prior_prediction_date"]="2026-11-01"
        r["implementation_started_at"]="2026-10-01"
        with self.assertRaisesRegex(ValueError,"before implementation"):
            validate_new_contribution(r)
        r["implementation_started_at"]="2026-11-02"
        self.assertEqual(validate_new_contribution(r),"ASSESSMENT_DERIVED")

    def test_informed_is_not_derived(self):
        r=sample()
        r["contribution_type"]="ASSESSMENT_INFORMED"
        r["assessment_pin"]={"url":PIN,"reviewed_at":"2026-09-18","assessed_source_revision":"c"*40}
        r["classification_evidence"]=[PIN]
        self.assertEqual(validate_new_contribution(r),"ASSESSMENT_INFORMED")
        r["assessment_pin"]["url"]=PIN.replace("/blob/","/main/")
        with self.assertRaises(ValueError):
            validate_new_contribution(r)

    def test_insufficient_is_explicit_and_is_not_assessment_derived(self):
        r=sample()
        r["contribution_type"]="INSUFFICIENT"
        r["classification_evidence"]=[]
        self.assertEqual(validate_new_contribution(r),"INSUFFICIENT")
        r["classification_rationale"]=""
        with self.assertRaises(ValueError):
            validate_new_contribution(r)


if __name__ == "__main__":
    unittest.main()
