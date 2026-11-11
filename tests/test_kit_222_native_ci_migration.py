"""Freeze the Kit source-native CI migration evidence after fork parity."""

import hashlib
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "pilots" / "kit-222"
UPSTREAM_WORKFLOWS = ROOT / ".github" / "workflows"

HISTORICAL_BLOBS = {
    "historical-upstream-offline.yml":
        "b2f6332a5dbd116c2580e40ba064cae929e20622",
    "historical-upstream-compat.yml":
        "fa327f9f4325dbdcc5302afd025db6abc720e132",
}


class KitNativeMigrationTests(unittest.TestCase):
    def test_original_workflow_recipes_are_byte_identical_and_retired(self):
        for filename, expected_blob in HISTORICAL_BLOBS.items():
            with self.subTest(filename=filename):
                data = (PILOT / filename).read_bytes()
                actual = hashlib.sha1(
                    f"blob {len(data)}\0".encode() + data
                ).hexdigest()
                self.assertEqual(actual, expected_blob)
                original = filename.replace("historical-upstream-", "kit-222-")
                self.assertFalse((UPSTREAM_WORKFLOWS / original).exists())
        # Archive placement is complete; macOS runtime parity is unverified.
        self.assertFalse((UPSTREAM_WORKFLOWS / "kit-222-compat.yml").exists())

    def test_fork_native_ci_receipt_is_pinned_and_passed(self):
        receipt = (PILOT / "NATIVE_CI_MIGRATION_2026-11-11.md").read_text()
        for marker in (
            "NATIVE_PARITY_PASS_OFFLINE_ONLY",
            "MACOS_PARITY_UNVERIFIED_ARCHIVED",
            "43097309626",
            "43064797099",
            "43064796979",
            "34c50de1d96fbe4f31dd00334641f398630d2c3a",
            "8f9f08a2b2088381f1cb106dcb9129378f8f0b4e",
            "34463579de4609cab159b6e2d90d4a737bd5a2c96147a6cec0354d5798a61901",
            "951952eef85d5d6e78c763fcbc30a28d620246af3a8991175780a1f89c814659",
            "cc997c7ee350db49c4a4f03789da25a3a4a8760281fefcc178e3a71c6b972389",
            "external_delivery=NONE",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, receipt)


if __name__ == "__main__":
    unittest.main()
