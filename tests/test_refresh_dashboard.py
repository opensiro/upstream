"""Offline tests for safe dashboard refresh and idempotent publication inputs."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from refresh_dashboard import refresh, fingerprint, validate_snapshot
from aggregate import APIError

SHA = "a" * 40
TIME = "2026-11-16T13:00:00Z"
PR = "https://github.com/example/agent/pull/1"


def snapshot():
    return {"generated_at": TIME, "scope": "public_organization_repositories",
            "coverage": {"scan_complete": True, "errors": 0, "filtered_by_attention": 0,
                         "pr_readback": "NOT_REQUESTED", "missing_meta": 12},
            "forks": [{"working_fork": "opensiro-contributions/agent",
                       "original_repository": "example/agent", "meta_head_sha": SHA,
                       "state_blob_sha": SHA,
                       "contributions": [{"id": "upgrade-a", "record_sha": SHA,
                                          "external_prs": [{"url": PR, "status": "UNKNOWN"}]}]}]}


class FakeGitHub:
    def __init__(self):
        self.open = True
        self.fail = False

    def get(self, path):
        if self.fail:
            raise APIError(403, "rate limited")
        if path != "/repos/example/agent/pulls/1":
            raise AssertionError("unexpected API path: " + path)
        if self.open:
            return {"html_url": PR, "created_at": "2026-10-24T12:00:00Z",
                    "state": "open", "closed_at": None, "merged_at": None}
        return {"html_url": PR, "created_at": "2026-10-24T12:00:00Z",
                "state": "closed", "closed_at": "2026-11-16T12:00:00Z",
                "merged_at": "2026-11-16T12:00:00Z"}


class DashboardRefreshTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.paths = {"svg_path": self.root / "activity.svg",
                      "markdown_path": self.root / "ACTIVITY.md",
                      "sources_path": self.root / "activity-sources.json"}
        self.github = FakeGitHub()

    def run_refresh(self, data=None, **kwargs):
        return refresh(data or snapshot(), upstream_revision=SHA,
                       client=self.github, observed_at=kwargs.pop("observed_at", TIME),
                       **self.paths, **kwargs)

    def test_publishes_pinned_sources_and_uses_first_party_pr(self):
        self.assertTrue(self.run_refresh())
        sources = json.loads(self.paths["sources_path"].read_text())
        self.assertEqual(sources["fork_sources"][0]["meta_head_sha"], SHA)
        self.assertEqual(sources["summary"]["open"], 1)
        self.assertEqual(sources["coverage"]["missing_meta"], 12)
        self.assertEqual(sources["upstream_revision"], SHA)
        self.assertEqual(sources["external_pr_readbacks"][0]["url"], PR)
        self.assertIn("**1**", self.paths["markdown_path"].read_text())
        self.assertTrue(self.paths["svg_path"].read_text().startswith("<svg"))

    def test_timestamp_only_run_is_idempotent(self):
        self.run_refresh()
        before = {p: p.read_bytes() for p in self.paths.values()}
        self.assertFalse(self.run_refresh(observed_at="2026-11-16T14:00:00Z"))
        self.assertEqual(before, {p: p.read_bytes() for p in self.paths.values()})

    def test_live_pr_status_change_triggers_refresh(self):
        self.run_refresh()
        self.github.open = False
        self.assertTrue(self.run_refresh(observed_at="2026-11-16T14:00:00Z"))
        receipt = json.loads(self.paths["sources_path"].read_text())
        self.assertEqual(receipt["summary"]["merged"], 1)

    def test_incomplete_live_pr_readback_does_not_touch_files(self):
        self.run_refresh()
        before = {p: p.read_bytes() for p in self.paths.values()}
        self.github.fail = True
        with self.assertRaises(ValueError):
            self.run_refresh()
        self.assertEqual(before, {p: p.read_bytes() for p in self.paths.values()})

    def test_partial_or_filtered_scan_refused(self):
        for key, value in (("scan_complete", False), ("errors", 1),
                           ("filtered_by_attention", 1), ("pr_readback", "PARTIAL")):
            data = snapshot()
            data["coverage"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.run_refresh(data)
            self.assertFalse(any(self.paths["sources_path"].parent.glob("*.json")))

    def test_cannot_publish_selected_subset_or_unpinned_fork(self):
        data = snapshot()
        data["scope"] = "selected_repositories"
        with self.assertRaises(ValueError):
            self.run_refresh(data)
        data = snapshot()
        data["forks"][0]["meta_head_sha"] = "unpinned"
        with self.assertRaises(ValueError):
            self.run_refresh(data)

    def test_detects_modified_published_artifact(self):
        self.run_refresh()
        self.paths["svg_path"].write_text("tampered")
        with self.assertRaisesRegex(ValueError, "differs from its pinned provenance"):
            self.run_refresh()

    def test_fingerprint_does_not_depend_on_order_or_time(self):
        first = snapshot()
        reports = {"prs": [{"url": PR, "status": "OPEN"}]}
        signature = fingerprint(first, reports)
        first["generated_at"] = "2026-11-16T14:00:00Z"
        first["forks"][0]["meta_head_sha"] = "b" * 40
        self.assertEqual(signature, fingerprint(first, reports))


if __name__ == "__main__":
    unittest.main()
