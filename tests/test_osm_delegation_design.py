"""Guard the unissued Upstream OSM mandate proposal and current write gates."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class OSMDelegationDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.design = (ROOT / "docs" / "OSM_DELEGATION_DESIGN.md").read_text(
            encoding="utf-8"
        )
        cls.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        cls.handoff = (ROOT / "docs" / "CONTROL_PLANE_HANDOFF.md").read_text(
            encoding="utf-8"
        )
        cls.packet = cls.design.split(
            "## P1 standing-mandate decision packet (unissued)", 1
        )[1].split("## Owner-controlled evolution path", 1)[0]

    def test_design_is_visible_but_no_mandate_is_issued(self):
        self.assertIn("docs/OSM_DELEGATION_DESIGN.md", self.readme)
        self.assertIn("OSM_DELEGATION_DESIGN.md", self.handoff)
        self.assertIn("PROPOSED_NOT_GRANTED", self.packet)
        for phrase in ("not a standing grant", "no attributable #274",
                       "actual authenticated execution identity not identified",
                       "Unset", "revocation", "No effective privileges"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), self.design.lower())

    def test_agent_local_work_and_human_publication_are_distinct(self):
        for phrase in ("unpublished", "Human publication handoff",
                       "external PR submission", "external maintainer",
                       "DCO/CLA", "CLOSED_CHANGE", "CLOSED_NO_CHANGE",
                       "NON_ADMITTED"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), self.design.lower())
        self.assertIn("manual operator action", self.design.lower())

    def test_current_authorization_gate_is_preserved(self):
        for phrase in ("ACTION_PREPARED_NOT_AUTHORIZED",
                       "current-session", "authorize(intent)",
                       "mandatory stop conditions"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), self.handoff.lower())
        self.assertIn("not an authorization source", self.handoff.lower())
        self.assertIn("stop at the existing exact-stage gate", self.design.lower())


if __name__ == "__main__":
    unittest.main()
