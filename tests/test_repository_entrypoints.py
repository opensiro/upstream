"""Repository handoff must remain navigable after documentation refactors."""

from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
ENTRYPOINTS = (
    "README.md", "AGENTS.md", "UPSTREAMING.md", "CONTRIBUTING.md",
    "docs/README.md", "docs/OPERATIONS.md", "data/README.md",
    "pilots/README.md", "reports/README.md",
)
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^\s)]+)(?:\s+[^)]*)?\)")


class RepositoryEntrypointsTests(unittest.TestCase):
    def test_all_entrypoint_relative_links_exist(self):
        for filename in ENTRYPOINTS:
            source = ROOT / filename
            self.assertTrue(source.is_file(), filename)
            text = source.read_text(encoding="utf-8")
            for raw in MARKDOWN_LINK.findall(text):
                parsed = urlsplit(raw)
                if parsed.scheme or raw.startswith("#") or raw.startswith("mailto:"):
                    continue
                with self.subTest(source=filename, link=raw):
                    self.assertFalse(raw.startswith("/"), "Absolute file paths are not portable")
                    self.assertTrue((source.parent / unquote(parsed.path)).exists(),
                                    f"{filename} has broken relative link: {raw}")

    def test_human_and_agent_handoff_and_domain_owners_are_explicit(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        agent = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        contract = (ROOT / "UPSTREAMING.md").read_text(encoding="utf-8")
        for title in ("## I'm human", "## I'm AI", "## Validate locally"):
            self.assertIn(title, readme)
        for filename in ("START_HERE.md", "ECOSYSTEM.md", "TODO.md"):
            self.assertIn(filename, agent)
        for term in ("explicit manifest", "Organization", "closed", "publication",
                     "source-of-truth", "generated"):
            self.assertIn(term.lower(), contract.lower())
        self.assertIn("does **not** grant", readme.lower())


if __name__ == "__main__":
    unittest.main()
