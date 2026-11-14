"""Keep the KnowWork false-positive correction and executable SDK probe reviewable."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
from pathlib import Path
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "pilots" / "knowwork-start-race-s2"
PROBE = CASE / "verify_docker_start_semantics.py"


class ExternalDependencyNeedTests(unittest.TestCase):
    def test_need_and_publication_rules_reject_fake_only_dependency_error(self):
        required = {
            "docs/ASSESSMENT_TO_IMPROVEMENT.md": ("dependency semantics", "need=FAIL"),
            "docs/ASSESSMENT_CANDIDATE_BATCHES.md": ("third-party API assumptions", "BLOCKED_EVIDENCE"),
            "docs/STANDING_EXTERNAL_PR_PUBLICATION.md": ("Need-verification subgate", "fake-only"),
            "docs/EXTERNAL_PUBLICATION_WAVES.md": ("Dependency-native need check", "Fake-injected"),
        }
        for rel, words in required.items():
            with self.subTest(file=rel):
                content = (ROOT / rel).read_text(encoding="utf-8")
                for word in words:
                    self.assertIn(word.lower(), content.lower())

    def test_invalidated_knowwork_claim_is_prominent_but_history_retained(self):
        handoff = (CASE / "CONTRIBUTION_HANDOFF.md").read_text()
        receipt = (CASE / "INDEPENDENT_HOST_RECEIPT_2026-11-10.md").read_text()
        correction = (CASE / "CORRECTION_2026-11-14.md").read_text()
        self.assertIn("need=FAIL", handoff.split("**Status:**")[0])
        self.assertIn("CLOSED_UNMERGED", handoff)
        self.assertIn("FakeDocker", receipt.split("## Frozen source and provenance")[0])
        self.assertIn("304", correction)
        self.assertIn("not", correction.lower())
        self.assertIn("12", receipt)  # the historical record remains available

    def test_frozen_patch_files_are_unmodified(self):
        hashes = {
            "native-regression.patch": "30702f011b0487580fc9fd58e2253f5afacaabaf1d82344eef97765a13139192",
            "native-fix.patch": "fcc24402da2b1dc7219fbed9098b3a893d54728620a6bc069f5a56f3bf6b60ca",
        }
        for filename, expected in hashes.items():
            with self.subTest(filename=filename):
                actual = hashlib.sha256((CASE / filename).read_bytes()).hexdigest()
                self.assertEqual(actual, expected)

    def test_actual_sdk_probe_is_parseable_and_does_not_inject_apierror(self):
        source = PROBE.read_text(encoding="utf-8")
        ast.parse(source, filename=str(PROBE))
        self.assertIn("client.start(", source)
        self.assertIn("client._post", source)
        self.assertNotIn("raise APIError(", source)
        self.assertNotIn("FakeDocker", source)

    @unittest.skipUnless(importlib.util.find_spec("docker") is not None,
                         "docker SDK not installed in generic Upstream CI; run source-native probe separately")
    def test_real_sdk_observation_when_dependency_is_installed(self):
        module = runpy.run_path(str(PROBE))
        self.assertEqual(module["observe"](304), "NO_EXCEPTION")
        self.assertEqual(module["observe"](409), "APIError(409)")
        self.assertEqual(module["observe"](500), "APIError(500)")


if __name__ == "__main__":
    unittest.main()
