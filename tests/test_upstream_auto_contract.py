"""The Upstream auto route remains truthful until task-CAS is implemented."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = (ROOT / "docs" / "UPSTREAM_AUTO.md").read_text(encoding="utf-8")


class UpstreamAutoContractTests(unittest.TestCase):
    def test_readonly_preview_is_not_an_executor(self):
        self.assertIn("`upstream auto status`", CONTRACT)
        self.assertIn("`upstream auto resume`", CONTRACT)
        self.assertIn("NOT_IMPLEMENTED_EXECUTOR", CONTRACT)
        self.assertIn("NOT_IMPLEMENTED_TASK_CLAIM", CONTRACT)
        self.assertIn("NO_VERIFIED_ELIGIBLE_WORK", CONTRACT)
        self.assertIn("BLOCKED_RESERVATION_VISIBILITY", CONTRACT)

    def test_source_cas_is_not_general_task_lock(self):
        self.assertIn("Batch source-CAS is still not a general lock", CONTRACT)
        self.assertIn("same-task collision", CONTRACT)
        self.assertIn("disjoint-task progress", CONTRACT)
        self.assertIn("five-row batch order", CONTRACT)

    def test_vsm_and_external_gates_are_preserved(self):
        for condition in (
            "Organization `S2=A`",
            "agent-owned coordination choice",
            "different admitted",
            "no double-count",
            "no write",
            "Third-party merge remains external",
            "verified_external_outcomes",
        ):
            with self.subTest(condition=condition):
                self.assertIn(condition, CONTRACT)


if __name__ == "__main__":
    unittest.main()
