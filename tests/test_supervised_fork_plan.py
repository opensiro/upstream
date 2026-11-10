"""Validate the simple operator-facing plan remains non-executable."""

import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import supervised_fork_plan as plan  # noqa: E402


class SupervisedForkPlanTests(unittest.TestCase):
    def test_first_batch_preserves_identity_scope_and_no_execution(self):
        result = plan.plan(ROOT, "bootstrap-001")
        self.assertEqual(result["state"], "DISPLAY_ONLY_NO_WRITE_AUTHORITY")
        self.assertEqual(result["external_pr"], "HUMAN_APPROVAL_PER_EXACT_PR")
        self.assertEqual(len(result["items"]), 10)
        self.assertRegex(result["selection_sha256"], r"^[0-9a-f]{64}$")
        self.assertTrue(all(x["command_after_approval"].startswith("gh repo fork ")
                            and "--org opensiro-contributions" in x["command_after_approval"]
                            and "--clone=false" in x["command_after_approval"]
                            for x in result["items"]))

    def test_unknown_batch_and_unapproved_state_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "Unknown bootstrap batch"):
            plan.plan(ROOT, "bootstrap-999")
        result = subprocess.run(["python3", str(ROOT / "scripts/supervised_fork_plan.py"),
                                 "execute", "--batch", "bootstrap-001"],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid choice", result.stderr)

    def test_cli_is_read_only_json_display(self):
        result = subprocess.run(["python3", str(ROOT / "scripts/supervised_fork_plan.py"),
                                 "show", "--batch", "bootstrap-001"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["items"], plan.plan(ROOT, "bootstrap-001")["items"])


if __name__ == "__main__":
    unittest.main()
