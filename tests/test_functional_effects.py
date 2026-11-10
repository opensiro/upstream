import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.functional_effects import DATA, load_and_validate, render


class FunctionalEffectsTest(unittest.TestCase):
    def test_live_data_renders_checked_document(self):
        payload = load_and_validate()
        self.assertEqual(payload["owner"], "opensiro/upstream")
        rendered = render(payload)
        self.assertIn("1/2 intended updates preserved", rendered)
        self.assertIn("20/20 new native Vitest checks", rendered)
        self.assertIn("shared-registry delegate_task replay lost 29/30", rendered)
        self.assertIn("NOT_MEASURED", rendered)
        kram = next(case for case in payload["cases"] if case["id"] == "kram-s2-native-edit-atomicity")
        self.assertEqual(kram["measurement_level"], "NATIVE_TOOL_BEHAVIOR")
        self.assertEqual(kram["product_benefit"], "NOT_MEASURED")
        self.assertEqual(kram["external_delivery"], "NONE")
        self.assertIn("technical gate satisfied", kram["next_gate"])
        self.assertIn("native scripted tests only", rendered)
        self.assertEqual(
            rendered,
            (DATA.parent.parent / "docs" / "FUNCTIONAL_EFFECTS.md").read_text(encoding="utf-8"),
        )

    def test_rejects_duplicate_case_and_unverified_promotion(self):
        payload = load_and_validate()
        for variant in ("duplicate", "promotion", "url"):
            altered = copy.deepcopy(payload)
            if variant == "duplicate":
                altered["cases"].append(copy.deepcopy(altered["cases"][0]))
            elif variant == "promotion":
                altered["cases"][0]["product_benefit"] = "SUPPORTED"
            else:
                altered["cases"][0]["receipts"][0] = "http://not-evidence/"
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "data.json"
                path.write_text(json.dumps(altered), encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_and_validate(path)

    def test_native_tool_replay_cannot_claim_product_benefit(self):
        altered = copy.deepcopy(load_and_validate())
        altered["cases"][0]["product_benefit"] = "SUPPORTED"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.json"
            path.write_text(json.dumps(altered), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "product benefit requires measured real workload"):
                load_and_validate(path)

    def test_rejects_llm_agent_test_as_next_gate(self):
        for forbidden in ("provider-backed real child tasks", "cross-agent/model workload", "real-model paired quality study"):
            altered = copy.deepcopy(load_and_validate())
            altered["cases"][0]["next_gate"] = forbidden
            with self.subTest(forbidden=forbidden), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "data.json"
                path.write_text(json.dumps(altered), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "live LLM-agent testing cannot be a required next gate"):
                    load_and_validate(path)


if __name__ == "__main__":
    unittest.main()
