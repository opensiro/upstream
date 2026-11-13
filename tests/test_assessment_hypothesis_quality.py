"""Frozen-census quality readback must not turn hypotheses into outcomes."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import assessment_hypothesis_quality as quality


class AssessmentHypothesisQualityTests(unittest.TestCase):
    def cohort(self):
        # The first launch is a pinned historical eight-cohort baseline, not the newest eight.
        return [row for row in quality.frozen_files() if 27 <= row[0] <= 34]

    def test_first_launch_frozen_eight_batch_counts(self):
        files = self.cohort()
        self.assertEqual([x[0] for x in files], list(range(27, 35)))
        result = quality.audit(files)
        self.assertEqual(result['cohort']['screened'], 40)
        self.assertEqual(result['counts']['stages'],
                         {'AWAITING_EXTERNAL': 1, 'BLOCKED_EVIDENCE': 16, 'CLOSED_NO_CHANGE': 23})
        self.assertEqual(result['counts']['origins'],
                         {'ASSESSMENT_DERIVED': 3, 'INSUFFICIENT': 37})
        self.assertEqual(result['counts']['derived_unblocked'], 1)
        self.assertEqual(result['counts']['dated_published_source_receipts'], 1)
        self.assertIsNone(result['counts']['accepted_merged_changes'])
        self.assertIsNone(result['counts']['measured_product_benefits'])
        self.assertEqual(result['gates']['source_verified_acceptance'], 'NOT_LIVE_CHECKED')
        self.assertEqual(len({r['source'].casefold() for r in result['candidates']}), 40)
        hermes = next(r for r in result['candidates']
                      if r['candidate_id'] == 'oh-my-hermes-crossprocess-lock')
        self.assertEqual(hermes['published_pr'],
                         'https://github.com/witt3rd/oh-my-hermes/pull/28')
        self.assertIsNone(hermes['maintainer_adoption_verified'])
        for r in result['candidates']:
            self.assertIsNone(r['user_benefit_measured'])
            self.assertIsNone(r['native_benefit_verified'])
        self.assertEqual(quality.markdown(result),
                         (ROOT / 'reports/2026-11-13-assessment-hypothesis-quality-baseline.md').read_text())

    def test_refuse_missing_preregistration_and_duplicate_batches(self):
        files = self.cohort()
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'Missing source-first hypothesis'):
                quality.audit(files, prereg_folder=Path(tmp))
            with self.assertRaisesRegex(ValueError, 'Duplicate candidate'):
                quality.audit(files + files[-1:])

    def test_forged_publication_does_not_create_a_live_success(self):
        files = self.cohort()
        readbacks = quality.publication_readbacks()
        forged = copy.deepcopy(readbacks)
        forged['oh-my-hermes-crossprocess-lock']['source'] = 'wrong/target'
        with self.assertRaisesRegex(ValueError, 'mismatches source'):
            quality.audit(files, readbacks=forged)
        forged = copy.deepcopy(readbacks)
        forged['ada-copyback-claim-release'] = {'source': 'black141312/ada',
                                                 'url': 'https://github.com/black141312/ada/pull/999',
                                                 'receipt': 'untrusted'}
        result = quality.audit(files, readbacks=forged)
        self.assertEqual(result['counts']['dated_published_source_receipts'], 2)
        self.assertIsNone(result['counts']['accepted_merged_changes'])
        self.assertIsNone(result['counts']['measured_product_benefits'])

    def test_published_readback_source_and_duplicate_fail_closed(self):
        packet = {'schema_version': 1, 'observed_at': '2026-11-13',
                  'authenticated_actor': 'xLagerFeuer',
                  'cases': [{'id': 'new', 'repository': 'example/fork',
                             'public_fork': 'opensiro-contributions/fork',
                             'pr_url': 'https://github.com/example/fork/pull/2',
                             'head_sha': 'a' * 40, 'pr_commits': 1}]}
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / '2026-11-13.json'
            p.write_text(json.dumps(packet))
            self.assertEqual(len(quality.publication_readbacks(tmp)), 1)
            packet['cases'].append(copy.deepcopy(packet['cases'][0]))
            p.write_text(json.dumps(packet))
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                quality.publication_readbacks(tmp)
            packet['cases'] = [packet['cases'][0]]
            packet['cases'][0]['repository'] = 'other/repo'
            p.write_text(json.dumps(packet))
            with self.assertRaisesRegex(ValueError, 'mismatch'):
                quality.publication_readbacks(tmp)


if __name__ == '__main__':
    unittest.main()
