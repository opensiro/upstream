"""Offline consistency checks for the single Upstream contribution-protocol SemVer."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\Z")
CHECKPOINT = re.compile(r"\*\*Historical checkpoint:\*\* `([0-9a-f]{40})`")


def parts(value: str):
    return tuple(int(piece) for piece in value.split("."))


class ContributionProtocolSemverTests(unittest.TestCase):
    def test_single_semver_and_descending_packages(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertRegex(version, SEMVER)
        text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        versions = re.findall(r"^## \[([0-9]+\.[0-9]+\.[0-9]+)\]\(changes/v[0-9]+\.[0-9]+\.[0-9]+\.md\)", text, re.M)
        self.assertTrue(versions)
        self.assertEqual(versions[0], version)
        self.assertEqual(len(versions), len(set(versions)))
        self.assertEqual(versions, sorted(versions, key=parts, reverse=True))
        files = {p.name for p in (ROOT / "changes").glob("v*.md")}
        self.assertEqual(files, {f"v{v}.md" for v in versions})

    def test_each_package_has_source_checkpoint_and_scope(self):
        versions = re.findall(r"^## \[([0-9]+\.[0-9]+\.[0-9]+)\]", (ROOT / "CHANGELOG.md").read_text(), re.M)
        for version in versions:
            with self.subTest(version=version):
                text = (ROOT / "changes" / f"v{version}.md").read_text(encoding="utf-8")
                self.assertTrue(text.startswith(f"# v{version} — "))
                self.assertIsNotNone(CHECKPOINT.search(text))
                self.assertIn("https://github.com/opensiro/upstream/pull/", text)
                self.assertIn("## Protocol changes", text)
                self.assertIn("## Boundary and compatibility", text)

    def test_historical_backfill_not_misreported_as_old_releases(self):
        text = (ROOT / "VERSIONING.md").read_text(encoding="utf-8")
        self.assertIn("retrospective", text.lower())
        self.assertIn("not backdated", text.lower())
        self.assertIn("No automatic tagging workflow", text)
        self.assertIn("does not extend", text)


    def test_080_opportunity_depth_release_is_traceable_and_compatibly_scoped(self):
        """A new upgrade-mode obligation must remain tied to one SemVer release."""
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        if parts(version) < (0, 8, 0):
            self.skipTest("pre-0.8.0 historical protocol snapshot")
        package = (ROOT / "changes" / "v0.8.0.md").read_text(encoding="utf-8")
        contract = (ROOT / "docs" / "ASSESSMENT_CANDIDATE_BATCHES.md").read_text(encoding="utf-8")
        for name in ("README.md", "UPSTREAMING.md"):
            with self.subTest(entry=name):
                self.assertIn(f"SemVer `{version}`", (ROOT / name).read_text(encoding="utf-8"))
        for phrase in ("MINOR", "four", "source-first", "pre-source",
                       "batch 39", "## Boundary and compatibility"):
            with self.subTest(package=phrase):
                self.assertIn(phrase.lower(), package.lower())
        for phrase in ("SCREENING_COMPLETE", "OPPORTUNITY_RESEARCH_PENDING",
                       "OPPORTUNITY_DECIDED", "six-function",
                       "need=PENDING", "counterfactual=PENDING",
                       "a separate runner", "four gates",
                       "no new manifest enum"):
            with self.subTest(contract=phrase):
                self.assertIn(phrase.lower(), contract.lower())

if __name__ == "__main__":
    unittest.main()
