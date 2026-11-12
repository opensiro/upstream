from __future__ import annotations
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class CurrentP1GuidanceTests(unittest.TestCase):
    def test_current_active_mandates_are_routed(self):
        p = json.loads((ROOT / 'policies/standing-preparation-p1.json').read_text())
        e = json.loads((ROOT / 'policies/standing-external-publication-p1.json').read_text())
        self.assertEqual(p['status'], 'ACTIVE')
        self.assertEqual(e['status'], 'ACTIVE')
        self.assertEqual(p['actor'], e['issuer_actor'])
        self.assertIn('prepare_contribution', p['allowed_stages'])
        self.assertEqual(e['allowed_stage'], 'submit_external_pr')
        for rel in ('docs/ASSESSMENT_CANDIDATE_BATCHES.md', 'docs/ASSESSMENT_DRIVEN_S1_TEST.md'):
            s = (ROOT / rel).read_text()
            self.assertIn('STANDING_PREPARATION_AUTONOMY.md', s)
            self.assertIn('STANDING_EXTERNAL_PR_PUBLICATION.md', s)
            self.assertIn('CLA/DCO', s)

    def test_outdated_human_prompt_guidance_is_not_active(self):
        b = (ROOT / 'docs/ASSESSMENT_CANDIDATE_BATCHES.md').read_text()
        s = (ROOT / 'docs/ASSESSMENT_DRIVEN_S1_TEST.md').read_text()
        self.assertIn('without repeated human approval', b)
        self.assertIn('## Working fork execution under the current P1 envelope', s)
        self.assertNotIn('specific human approval **before any new external PR**', b)
        self.assertNotIn('a distinct, **human-approved**', b)
        self.assertNotIn('publication otherwise **human-owned**', b)
        self.assertNotIn('## Working fork creation route (not yet activated)', s)

if __name__ == '__main__':
    unittest.main()
