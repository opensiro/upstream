"""Offline tests for PR-state authority, replacement counting and generated views."""

import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("upstream_status", ROOT / "scripts/upstream_status.py")
status = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(status)


class UpstreamStatusTests(unittest.TestCase):
    def fake_fetch(self, url):
        # Two PRs in Henterprise count once, not twice; Shep reflects merge.
        merged = any(part in url for part in ("marveen/pull/1516", "henterprise/pull/3", "shep/pull/933", "shep/pull/934"))
        closed = any(part in url for part in ("henterprise/pull/1", "scion/pull/2047", "oh-my-agent/pull/819"))
        return {"url": url, "lifecycle": "merged" if merged else "closed_unmerged" if closed else "open",
                "merged_at": "2026-10-19T00:00:00Z" if merged else None, "updated_at": "2026-10-19T00:00:00Z"}

    def test_source_integrity_and_live_cohort(self):
        snapshot, cases = status.sources()
        self.assertEqual(8, len(snapshot["interventions"]))
        self.assertEqual(8, len(cases))
        observed = status.collect(fetch=self.fake_fetch)
        outcomes, fits = status.stats(snapshot, observed)
        self.assertEqual({"merged": 4, "open": 2, "closed_unmerged": 2}, dict(outcomes))
        self.assertEqual({"pass": 3, "pending": 3, "fail": 2}, dict(fits))
        self.assertEqual(8, len(observed["records"]))
        self.assertEqual([{"id": "cognee-community", "url": "https://github.com/topoteretes/cognee-community/pull/434"}],
                         status.registry_prs())
        self.assertEqual(1, len(observed["registry_records"]))
        self.assertEqual("open", observed["registry_records"][0]["pr"]["lifecycle"])
        replacement = next(x for x in observed["records"] if x["id"] == "henterprise-1")
        self.assertEqual("closed_unmerged", replacement["original_pr"]["lifecycle"])
        self.assertEqual("merged", replacement["landing_pr"]["lifecycle"])

    def test_url_validator_requires_exact_public_pr(self):
        self.assertEqual("https://api.github.com/repos/shep-ai/shep/pulls/933",
                         status.pr_api_url("https://github.com/shep-ai/shep/pull/933"))
        for invalid in ("http://github.com/a/b/pull/1", "https://evil.example/a/b/pull/1",
                        "https://github.com/a/b/issues/1", "https://github.com/a/b/pull/1/files"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                status.pr_api_url(invalid)

    def test_unknown_or_failed_remote_never_creates_success(self):
        with self.assertRaises(OSError):
            status.collect(fetch=lambda _: (_ for _ in ()).throw(OSError("rate limited")))

    def test_generation_and_idempotence(self):
        snapshot, cases, observed = status.load_verified()
        markdown = status.render_markdown(snapshot, cases, observed)
        self.assertIn("| **8** | **7** | **4** | **2** | **2** |", markdown)
        self.assertIn("60% (3/5)", markdown)
        self.assertIn("Original PR", markdown)
        self.assertIn("### Separately tracked OpenSiro-owned fork contributions", markdown)
        self.assertIn("cognee-community", markdown)
        raw = status.HTML.read_text(encoding="utf-8")
        first = status.render_html(raw, snapshot, cases, observed)
        self.assertEqual(first, status.render_html(first, snapshot, cases, observed))
        self.assertEqual(8, first.count('<tr class="item"'))
        self.assertIn("cognee-community PR", first)
        self.assertIn('data-outcome="merged" data-fit="pending"', first)
        self.assertEqual(status.render_casebook(status.CASEBOOK.read_text(), snapshot, cases, observed),
                         status.CASEBOOK.read_text())

    def test_missing_anchor_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "anchor missing"):
            status.replace_region("no template", "<!-- BEGIN GENERATED:x -->", "<!-- END GENERATED:x -->", "value")

    def test_fit_snapshot_binding(self):
        snapshot, cases, observed = status.load_verified()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "different-snapshot.json"
            # Same valid observations, changed pinned source digest.
            source.write_text(status.SNAPSHOT.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            with patch.object(status, "SNAPSHOT", source), self.assertRaisesRegex(ValueError, "fit snapshot changed"):
                status.load_verified()

    def test_live_drift_detection(self):
        self.assertEqual(8, status.check_live(fetch=self.fake_fetch))
        def changed(url):
            result = self.fake_fetch(url)
            if url.endswith("/933"):
                result["lifecycle"] = "open"
            return result
        with self.assertRaisesRegex(ValueError, "lifecycle drift"):
            status.check_live(fetch=changed)

        def cognee_merged(url):
            result = self.fake_fetch(url)
            if url.endswith("/434"):
                result["lifecycle"] = "merged"
            return result
        with self.assertRaisesRegex(ValueError, "cognee-community"):
            status.check_live(fetch=cognee_merged)


if __name__ == "__main__":
    unittest.main()
