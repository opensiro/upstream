"""Regression tests for read-only archived publication discovery."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from aggregate import APIError
from publication_archive import ARCHIVE, discover_archive
from publication_history import publication_history
from test_publication_history import PublicationFake, provider_fixture, CASE, TITLE
from test_roadmap_view import file_blob, FORK, ORIGINAL, NOW

HEAD = "5" * 40
ROOT = "/repos/" + ARCHIVE
COGNEE = "topoteretes/cognee-community"
STAR = "androoAGI/starnet"
STAR_ISSUE = f"https://github.com/{STAR}/issues/55"
STAR_PR = f"https://github.com/{STAR}/pull/56"
COGNEE_ISSUE = f"https://github.com/{COGNEE}/issues/435"
COGNEE_PR = f"https://github.com/{COGNEE}/pull/434"

def archive_fixture(client):
    def file(path, text):
        client.routes[ROOT + "/contents/" + path + "?ref=" + HEAD] = file_blob(text)
    client.routes[ROOT + "/git/ref/heads/main"] = {"object": {"sha": HEAD}}
    client.routes[ROOT + "/contents/cases?ref=" + HEAD] = [
        {"name": "README.md", "type": "file"},
        {"name": "starnet.md", "type": "file"},
    ]
    file("cases/starnet.md", f"""# StarNet
- **Upstream issue:** [#55]({STAR_ISSUE})
- **Original contributor PR:** [#56]({STAR_PR}) ([closure comment]({STAR_PR}#issuecomment-123))
- **Landed replacement:** [#99](https://github.com/{STAR}/pull/99)
Other cited issue https://github.com/{STAR}/issues/200
""")
    file("registry.yaml", f"""schema_version: 1
projects:
  - id: cognee-community
    contribution:
      upstream_issue: {COGNEE_ISSUE}
      upstream_pr: {COGNEE_PR}
""")
    file("data/upstream-lifecycle.json", json.dumps({
        "records": [{"id": "starnet", "original_pr": {"url": STAR_PR},
                     "landing_pr": {"url": f"https://github.com/{STAR}/pull/99"}}],
        "registry_records": [{"id": "cognee", "pr": {"url": COGNEE_PR}}]}))
    file("data/pr-maintenance/targets.json", json.dumps({
        "targets": [{"url": STAR_PR}, {"url": COGNEE_PR}]}))
    return client


class PublicationArchiveTests(unittest.TestCase):
    def test_archive_deduplicates_legacy_links_and_preserves_provenance(self):
        client = archive_fixture(PublicationFake())
        rows, scope = discover_archive(client)
        self.assertEqual(scope["status"], "CHECKED_BOUNDED")
        self.assertFalse(scope["historical_inventory_complete"])
        self.assertEqual({p["url"] for p in rows},
                         {STAR_ISSUE, STAR_PR, COGNEE_ISSUE, COGNEE_PR})
        star = next(p for p in rows if p["url"] == STAR_PR)
        self.assertEqual(len(star["provenance"]), 3)
        self.assertIsNone(star["case_id"])
        self.assertTrue(all(HEAD in url for url in star["provenance"]))

    def test_target_scope_restricts_legacy_provider_candidates(self):
        rows, scope = discover_archive(archive_fixture(PublicationFake()), STAR.upper())
        self.assertEqual({p["url"] for p in rows}, {STAR_ISSUE, STAR_PR})
        self.assertEqual(scope["status"], "CHECKED_BOUNDED")

    def test_archive_missing_source_is_partial_not_empty_success(self):
        client = archive_fixture(PublicationFake())
        client.routes[ROOT + "/contents/registry.yaml?ref=" + HEAD] = APIError(403, "forbidden")
        rows, scope = discover_archive(client)
        self.assertEqual(scope["status"], "PARTIAL")
        self.assertTrue(scope["errors"])
        self.assertIn(STAR_ISSUE, {p["url"] for p in rows})

    def test_legacy_live_author_and_404_remain_distinct(self):
        client = archive_fixture(PublicationFake())
        client.routes[f"/repos/{STAR}/issues/55"] = provider_fixture(state="closed")
        client.routes[f"/repos/{STAR}/pulls/56"] = provider_fixture(state="closed")
        client.routes[f"/repos/{COGNEE}/issues/435"] = provider_fixture(author="other-author")
        client.routes[f"/repos/{COGNEE}/pulls/434"] = APIError(404, "unavailable")
        report = publication_history(client, requested=[FORK], include_archive=True,
                                     observed_at=NOW)
        rows = {p["url"]: p["provider"] for p in report["publications"]}
        self.assertEqual(rows[STAR_ISSUE]["status"], "CLOSED")
        self.assertEqual(rows[STAR_PR]["status"], "CLOSED_UNMERGED")
        self.assertEqual(rows[COGNEE_ISSUE]["reason"], "AUTHOR_MISMATCH")
        self.assertEqual(rows[COGNEE_PR]["reason"], "GITHUB_HTTP_404")
        self.assertFalse(report["coverage"]["scan_complete"])

    def test_candidate_cannot_pass_when_archive_is_unavailable(self):
        client = archive_fixture(PublicationFake())
        client.routes[ROOT + "/git/ref/heads/main"] = APIError(403, "forbidden")
        report = publication_history(client, requested=[FORK], include_archive=True,
            candidate_original=ORIGINAL, candidate_case=CASE, candidate_title=TITLE,
            search=False, observed_at=NOW)
        self.assertEqual(report["preflight"]["status"], "HISTORY_UNVERIFIED")
        self.assertEqual(report["coverage"]["archive"]["status"], "UNVERIFIED")
        self.assertFalse(report["coverage"]["scan_complete"])


if __name__ == "__main__":
    unittest.main()
