import hashlib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PILOT = ROOT / "pilots" / "kram-s2"
PATCH_SHA256 = "c8877dda2405f6d18d5c0693c3620115c8b57907248b4f6c3d42007dec0d030b"
SOURCE_SHA = "5f18406709f432dbdb2d6b09da6f140385516366"


class KramReplayContractTest(unittest.TestCase):
    def test_replay_patch_and_pins_are_immutable(self):
        patch = (PILOT / "s2-edit-file-atomicity-v2.patch").read_bytes()
        self.assertEqual(hashlib.sha256(patch).hexdigest(), PATCH_SHA256)
        receipt = (PILOT / "REPLAY_RECEIPT_2026-10-22.md").read_text()
        self.assertIn(SOURCE_SHA, receipt)
        self.assertIn(PATCH_SHA256, receipt)
        self.assertIn("POTENTIALLY_CONTAMINATED", receipt)

    def test_workflow_is_pinned_read_only_and_preserves_before_after_separation(self):
        workflow = (ROOT / ".github" / "workflows" / "kram-s2-native-replay.yml").read_text()
        self.assertIn("repository: codexmark/kram", workflow)
        self.assertIn("ref: " + SOURCE_SHA, workflow)
        self.assertIn("contents: read", workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertIn("--include='*s2_replay_test.go'", workflow)
        self.assertIn("--include='*edit_file.go'", workflow)
        self.assertIn("go test -race", workflow)
        self.assertNotIn("git push ", workflow)
        self.assertNotIn("gh pr create", workflow)

    def test_product_benefit_is_explicitly_unmeasured(self):
        readme = (PILOT / "README.md").read_text()
        self.assertIn("product_benefit=NOT_MEASURED", readme)
        self.assertIn("external_delivery=NONE", readme)
        self.assertIn("synthetic", readme)


if __name__ == "__main__":
    unittest.main()
