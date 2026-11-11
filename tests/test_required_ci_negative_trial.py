"""Ephemeral negative trial for Organization #305; never merge."""
import unittest


class RequiredCheckNegativeTrial(unittest.TestCase):
    def test_required_ci_rejects_failing_pr(self):
        self.fail("INTENTIONAL_FAILURE_FOR_REQUIRED_CI_GATE_TRIAL_ONLY")
