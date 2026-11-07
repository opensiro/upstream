"""Offline regression tests for exact-cohort historical PR reconciliation."""

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("portfolio_history", ROOT / "scripts/portfolio_history.py")
history = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(history)

import portfolio_reconcile as portfolio


def report(at, outcome="open", *, second=False):
    records = [{"url": "https://github.com/Owner/repo/pull/1",
                "groups": ["watchlist"], "outcome": outcome}]
    if second:
        records.append({"url": "https://github.com/Owner/repo/pull/2",
                        "groups": ["casebook"], "outcome": "open"})
    return {"schema_version": 1, "observed_at": at,
            "cohort_sha256": portfolio.cohort_fingerprint(records), "records": records}


class PortfolioHistoryTests(unittest.TestCase):
    def test_sorted_history_same_cohort_with_real_resolution(self):
        first = report("2026-11-07T10:00:00+00:00")
        second = report("2026-11-08T10:00:00+00:00", "merged")
        rows = history.series([second, first])
        self.assertEqual([r["watchlist"]["rate"] for r in rows], [None, 1.0])
        self.assertIn("1/1 (100.0%)", history.render(rows))
        self.assertIn("not** a verified adoption", history.render(rows))

    def test_mixed_cohort_fails(self):
        with self.assertRaisesRegex(ValueError, "different PR cohorts"):
            history.series([report("2026-11-07T10:00:00Z"),
                            report("2026-11-08T10:00:00Z", second=True)])

    def test_invalid_metadata_fails_closed(self):
        current = report("2026-11-07T10:00:00Z")
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            history.series([current, current])
        with self.assertRaisesRegex(ValueError, "timezone"):
            history.series([report("2026-11-07T10:00:00")])
        with self.assertRaisesRegex(ValueError, "lacks cohort"):
            legacy = dict(current)
            legacy.pop("cohort_sha256")
            history.series([legacy])
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            tampered = dict(current)
            tampered["records"] = [dict(current["records"][0], groups=["registry"])]
            history.series([tampered])


if __name__ == "__main__":
    unittest.main()
