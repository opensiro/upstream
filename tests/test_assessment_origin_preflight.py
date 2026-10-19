"""Offline tests for the limited Index source → Upstream proposal origin gate."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from assessment_origin_preflight import OriginBlocked, preflight


SOURCE = "fixtureowner/fixture-harness"
ASSESSMENT_PATH = "assessments/fi/fixture-harness.md"
REF = "a" * 40


def source():
    return f"""---
harness_id: fixture-harness
project_name: Test Harness
repository: https://github.com/{SOURCE}
review_ref: {REF}
status: included
autonomy_s1: A
autonomy_s2: —
autonomy_s3: C
autonomy_s3_star: —
autonomy_s4: P
autonomy_s5: —
---

# Fixture-only assessment: not public Index evidence
"""


def manifest():
    return {
        "schema_version": 1, "batch_id": "upstream-20261019-origin-fixture",
        "revision": 1, "status": "proposal_only",
        "candidates": [{
            "id": "fixture-gap", "source": SOURCE, "fork_name": "fixture-harness",
            "stages": ["prepare_contribution"], "expected_license": "MIT",
            "proposal": {
                "system_component": "Concurrent agent task interaction",
                "problem": "A specific native inter-agent check requires regression coverage",
                "planned_change": "Add a focused contract test for the known interaction",
                "expected_improvement": "Detect previously observed behavior regression",
                "validation": "Run native isolated regression tests under exact source",
                "evidence_url": f"https://github.com/{SOURCE}/issues/123",
            }, "blockers": [],
        }],
    }


def git(root, *args):
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                       text=True, check=False)
    if p.returncode:
        raise AssertionError(p.stderr)
    return p.stdout.strip()


class AssessmentOriginTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / "index"
        self.root.mkdir()
        git(self.root, "init", "-q")
        path = self.root / ASSESSMENT_PATH
        path.parent.mkdir(parents=True)
        path.write_text(source(), encoding="utf-8")
        git(self.root, "add", "--all")
        git(self.root, "-c", "user.name=Fixture", "-c",
            "user.email=fixture@example.invalid", "commit", "-qm", "fixture")
        self.sha = git(self.root, "rev-parse", "HEAD")
        self.manifest = self.base / "upstream-20261019-origin-fixture.json"
        self.draft = manifest()
        self.save()

    def save(self):
        self.manifest.write_text(json.dumps(self.draft), encoding="utf-8")

    def invoke(self, **overrides):
        values = {
            "index_root": self.root, "index_sha": self.sha,
            "assessment_path": ASSESSMENT_PATH,
            "manifest": self.manifest, "candidate_id": "fixture-gap",
        }
        values.update(overrides)
        return preflight(**values)

    def blocked(self, **overrides):
        with self.assertRaises(OriginBlocked):
            self.invoke(**overrides)

    def test_pinned_origin_can_only_return_nonexecuting_local_receipt(self):
        receipt = self.invoke()
        self.assertEqual(receipt["status"], "LOCAL_INDEX_ORIGIN_PRECHECK_ONLY")
        self.assertEqual(receipt["authorization_status"], "NOT_APPROVED_NO_GITHUB_WRITES")
        self.assertFalse(receipt["execution_available"])
        self.assertEqual(receipt["index_commit_sha"], self.sha)
        self.assertEqual(receipt["assessed_upstream"], SOURCE)
        self.assertEqual(receipt["candidate_id"], "fixture-gap")
        self.assertEqual(receipt["function_states"]["S2"], "—")
        self.assertEqual(receipt["function_states"]["S3"], "C")
        self.assertEqual(
            receipt["assessment_sha256"],
            hashlib.sha256(source().encode("utf-8")).hexdigest(),
        )
        self.assertIn("UNVERIFIED", receipt["native_fit_status"])
        self.assertIn("UNVERIFIED", receipt["canonical_index_source_status"])
        self.assertNotIn("approve", receipt)

    def test_head_mismatch_fails_closed(self):
        self.blocked(index_sha="b" * 40)
        self.blocked(index_sha="main")

    def test_invalid_path_and_wrong_shard_rejected(self):
        for path in ("../../secret", "assessments/xx/fixture-harness.md",
                     "assessments/fi/../fi/fixture-harness.md", "README.md"):
            with self.subTest(path=path):
                self.blocked(assessment_path=path)

    def test_uncommitted_assessment_mutation_not_promoted(self):
        path = self.root / ASSESSMENT_PATH
        path.write_text(source().replace("autonomy_s2: —", "autonomy_s2: A"),
                        encoding="utf-8")
        self.assertEqual(self.invoke()["function_states"]["S2"], "—")

    def test_target_identity_mismatch_is_blocked(self):
        self.draft["candidates"][0]["source"] = "other/fixture-harness"
        self.save()
        self.blocked()

    def test_pending_and_blocked_proposals_are_not_admitted(self):
        self.draft["candidates"][0]["blockers"] = ["Native fit not proven"]
        self.save()
        self.blocked()

    def test_absent_candidate_and_fake_approval_rejected(self):
        self.blocked(candidate_id="unknown")
        self.draft["approved_by"] = "fake"
        self.save()
        self.blocked()

    def test_no_network_for_local_origin_check(self):
        with patch("urllib.request.urlopen", side_effect=AssertionError("network used")):
            self.assertEqual(self.invoke()["status"], "LOCAL_INDEX_ORIGIN_PRECHECK_ONLY")

    def test_nonincluded_and_duplicate_assessment_headers_rejected(self):
        path = self.root / ASSESSMENT_PATH
        path.write_text(source().replace("status: included", "status: proposed"),
                        encoding="utf-8")
        git(self.root, "add", "--all")
        git(self.root, "-c", "user.name=Fixture", "-c",
            "user.email=fixture@example.invalid", "commit", "-qm", "proposed")
        self.sha = git(self.root, "rev-parse", "HEAD")
        self.blocked()
        path.write_text(source().replace("status: included",
                        "status: included\nstatus: included"), encoding="utf-8")
        git(self.root, "add", "--all")
        git(self.root, "-c", "user.name=Fixture", "-c",
            "user.email=fixture@example.invalid", "commit", "-qm", "duplicate")
        self.sha = git(self.root, "rev-parse", "HEAD")
        self.blocked()

    def test_no_git_substitution_through_path(self):
        self.blocked(assessment_path="assessments/fi/fixture-harness.md:HEAD")


if __name__ == "__main__":
    unittest.main()
