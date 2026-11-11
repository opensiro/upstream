"""Preserve native baseline provenance while retiring AgentBox workflow copies."""

import hashlib
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "pilots" / "agentbox-s2"
WORKFLOWS = ROOT / ".github" / "workflows"
HISTORICAL_BLOBS = {
    "historical-upstream-task-conflict-baseline.yml":
        ("558269d64f487326623e8a7920ba6ed294a55420",
         "agentbox-task-conflict-baseline.yml"),
    "historical-upstream-native-dependency-dispatch.yml":
        ("2a779f2d5ec1dffb61dd4c57fb677e5f60d092db",
         "agentbox-native-dependency-dispatch.yml"),
    "historical-upstream-manager-advisory.yml":
        ("0b5479c2dc186b80b3ceabce8b36f4ff88d9f0e6", "agentbox-s2-manager-advisory.yml"),
}


class AgentBoxNativeCIMigrationTests(unittest.TestCase):
    def test_archived_legacy_recipes_match_exact_original_git_blobs(self):
        for filename, (original_sha, original_name) in HISTORICAL_BLOBS.items():
            with self.subTest(filename=filename):
                data = (PILOT / filename).read_bytes()
                self.assertEqual(
                    hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest(),
                    original_sha,
                )
                self.assertFalse((WORKFLOWS / original_name).exists())
        # PR #71 retains its own independent plan-prototype CI on its branch.

    def test_durable_matching_fork_receipt_covers_both_baselines(self):
        receipt = (PILOT / "NATIVE_CI_MIGRATION_2026-11-11.md").read_text()
        for marker in (
            "NATIVE_PARITY_PASS_BASELINES_ONLY",
            "43069016683", "43069017370",
            "56d0835bceac2830bc9f2a0060e9da8bbf04c613",
            "605ee75d63319003c188bc532d4e5b2ba36a51d6",
            "6bb0d9a79f0e67d3c8945dd72100cda454b6c9d701c8be655bff2b1e25427b4a",
            "b55104dcc7110117ab7bbe37336aebfe59f5ca93352721c4c10fdc32ed47af87",
            "manager_advisory=RETAINED_OPEN_PR_71",
            "external_delivery=NONE",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, receipt)

    def test_manager_advisory_fork_parity_receipt(self):
        receipt = (PILOT / "MANAGER_ADVISORY_CI_MIGRATION_2026-11-11.md").read_text()
        for marker in ("43090937771", "e9b40d947463adace9ea09aa8facc28518620b92",
                       "605ee75d63319003c188bc532d4e5b2ba36a51d6",
                       "39683286746", "PR #71"):
            with self.subTest(marker=marker):
                self.assertIn(marker, receipt)


if __name__ == "__main__":
    unittest.main()
