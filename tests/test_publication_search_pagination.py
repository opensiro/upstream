"""Regression: bounded REST search must actually read all available pages."""
import sys
from pathlib import Path
import unittest
from urllib.parse import quote
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from aggregate import APIError
from publication_history import search_original, keywords
from test_publication_history import PublicationFake, TITLE
from test_publication_recheck import prepare_search
from test_roadmap_view import ORIGINAL, NOW


def fixture(total, count=100, start=1):
    return {"total_count": total, "incomplete_results": False,
            "items": [{"html_url": f"https://github.com/{ORIGINAL}/pull/{i}",
                       "title": f"Related proposal {i}", "user": {"login": "maintainer"},
                       "state": "open", "updated_at": NOW}
                      for i in range(start, start + count)]}


class SearchPaginationTests(unittest.TestCase):
    def setUp(self):
        self.client = prepare_search(PublicationFake())
        terms = sorted(keywords(TITLE), key=lambda w: (-len(w), w))[:2]
        self.route = "/search/issues?q=" + quote(
            f"repo:{ORIGINAL} is:pr " + " ".join(terms)) + "&per_page=100"
        self.client.routes[self.route] = fixture(173)
        self.client.routes[self.route + "&page=2"] = fixture(173, 73, 101)

    def run_search(self):
        return search_original(self.client, ORIGINAL, TITLE, expanded=True)

    def test_hermes_two_pages_173_distinct(self):
        rows, errors = self.run_search()
        self.assertEqual(errors, [])
        self.assertEqual(len(rows), 173)
        self.assertEqual(len({r["url"] for r in rows}), 173)

    def test_exact_page_count_not_truncated(self):
        self.client.routes[self.route] = fixture(100)
        del self.client.routes[self.route + "&page=2"]
        rows, errors = self.run_search()
        self.assertEqual((len(rows), errors), (100, []))

    def test_drift_duplicates_and_partial_pages_fail_closed(self):
        for bad_page in (fixture(174, 73, 101), fixture(173, 73, 100),
                         fixture(173, 72, 101), dict(fixture(173, 73, 101), incomplete_results=True),
                         APIError(403, "rate-limit")):
            with self.subTest(page=type(bad_page).__name__):
                self.client.routes[self.route + "&page=2"] = bad_page
                rows, errors = self.run_search()
                self.assertTrue(errors)
                self.assertGreaterEqual(len(rows), 100)

    def test_provider_cap_never_claims_complete(self):
        self.client.routes[self.route] = fixture(1001)
        rows, errors = self.run_search()
        self.assertEqual(len(rows), 100)
        self.assertTrue(any("SEARCH_TRUNCATED" in e for e in errors))

    def test_wrong_channel_and_duplicate_first_page_block(self):
        first = fixture(100)
        first["items"][1] = dict(first["items"][0])
        first["items"][2]["html_url"] = f"https://github.com/{ORIGINAL}/issues/3"
        self.client.routes[self.route] = first
        rows, errors = self.run_search()
        self.assertTrue(any("DUPLICATE" in e for e in errors))
        self.assertTrue(any("IDENTITY_UNVERIFIED" in e for e in errors))
        self.assertEqual(len(rows), 98)


if __name__ == "__main__":
    unittest.main()
