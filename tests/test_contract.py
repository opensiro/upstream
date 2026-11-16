"""Source-only Upstream architecture tests: no GitHub write, network or VSM grading."""
from pathlib import Path
import json
import re
from tempfile import TemporaryDirectory
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_contract import check_contract, REQUIRED  # noqa: E402


class ContractTests(unittest.TestCase):
    def test_repository_contract(self):
        self.assertEqual(check_contract(ROOT), [])

    def test_fork_metadata_examples_have_distinct_identity_and_controls(self):
        content = (ROOT / "docs/FORK_METADATA.md").read_text(encoding="utf-8")
        samples = [json.loads(s) for s in re.findall(r"```json\s*(.*?)\s*```", content, re.S)]
        self.assertEqual(len(samples), 3)
        state, contribution, event = samples
        self.assertEqual(state["schema_version"], 1)
        self.assertEqual(contribution["schema_version"], 1)
        self.assertEqual(event["schema_version"], 1)
        self.assertEqual(state["working_fork"].split("/")[0], "opensiro-contributions")
        self.assertEqual(contribution["original_repository"], state["original_repository"])
        self.assertEqual(event["contribution_id"], contribution["id"])
        self.assertEqual(event["id"], state["last_event_id"])
        self.assertEqual(event["id"], contribution["last_event_id"])
        self.assertIn("STOP", content)
        self.assertIn("DORMANT", content)
        self.assertIn("opensiro/meta", content)

    def test_capability_upgrade_route_preserves_source_evidence_and_authority(self):
        protocol = (ROOT / "PROTOCOL.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("upstream upgrade batch N", protocol)
        self.assertIn("N distinct original harnesses", protocol)
        self.assertIn("S1/S2/S3/S3*/S4/S5", protocol)
        self.assertIn("REPAIR_ONLY", protocol)
        self.assertIn("ASSESSMENT_DERIVED", protocol)
        self.assertIn("exact current-conversation consent", protocol)
        self.assertIn("DORMANT", protocol)
        self.assertIn("PAUSE", protocol)
        self.assertIn("STOP", protocol)
        self.assertIn("upstream batch [N]", agents)
        self.assertIn("upstream upgrade batch 10", readme)
        self.assertIn("not executable CLI commands", readme)
        self.assertTrue((ROOT / "changes/v0.14.0.md").is_file())

    def test_upgrade_popularity_and_chat_only_batch_policy(self):
        protocol = (ROOT / "PROTOCOL.md").read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(version, "0.15.0")
        self.assertIn("unique GitHub contributors", protocol)
        self.assertIn("1× to 2×", protocol)
        self.assertIn("uniform", protocol)
        self.assertIn("chat-level research/reporting sessions", protocol)
        self.assertIn("not an issue, PR", protocol)
        self.assertIn("chat-only hypothesis cannot alone prove", protocol)
        self.assertIn("PAUSE", protocol)
        self.assertIn("native CI placement", protocol)
        self.assertIn("chat-scoped reports only", agents)
        self.assertIn("Batches live in the chat", readme)
        self.assertIn("v0.15.0", (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))

    def test_invalid_semver_is_rejected(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for filename in REQUIRED:
                file = root / filename
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text("", encoding="utf-8")
            (root / "VERSION").write_text("0.12\n", encoding="utf-8")
            self.assertTrue(any("invalid SemVer" in x for x in check_contract(root)))

    def test_missing_change_package_is_rejected(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for filename in REQUIRED:
                file = root / filename
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text("", encoding="utf-8")
            (root / "VERSION").write_text("0.12.0\n", encoding="utf-8")
            self.assertTrue(any("missing changes/" in x for x in check_contract(root)))


if __name__ == "__main__":
    unittest.main()
