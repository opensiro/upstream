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
        self.assertIn("NOT_MEASURED", rendered)
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


if __name__ == "__main__":
    unittest.main()
