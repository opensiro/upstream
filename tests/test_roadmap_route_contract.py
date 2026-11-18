"""Document contract only, not proof of real VSM functions or engineering savings."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class RoadmapRouteContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol=(ROOT/"PROTOCOL.md").read_text()
        cls.route=cls.protocol.split("## Architecture-first `upstream roadmap OWNER/REPO` (plan-only)".replace("`",chr(96)),1)[1].split("\n## ",1)[0]
        cls.guide=(ROOT/"docs/CAPABILITY_ROADMAP.md").read_text()
        cls.template=(ROOT/"templates/EXTERNAL_ARCHITECTURE_ISSUE.md").read_text()

    def test_separate_plan_only_route(self):
        for phrase in ("plan-only", "one source", "zero product changes", "upstream upgrade", "separate", "read-only", "not a compulsory", "not a mandatory"):
            if phrase in ("one source", "not a compulsory", "not a mandatory"):
                continue
            self.assertIn(phrase.lower(),self.route.lower())
        self.assertIn("## Capability-first `upstream upgrade`".replace("`",chr(96)),self.protocol)

    def test_named_roadmap_full_cycle_reaches_fork_issue_gate(self):
        readme=(ROOT/"README.md").read_text()
        changelog=(ROOT/"CHANGELOG.md").read_text()
        for phrase in (
            "PLAN_ONLY full cycle to a fork-local GitHub Issue",
            "Durable roadmap capture is the default completion obligation",
            "READY_FOR_FORK_ISSUE_APPROVAL — NOT PUBLISHED",
            "verify or provision",
            "separate exact current-conversation",
        ):
            self.assertIn(phrase.lower(), self.route.lower())
        self.assertIn("complete fork-local Issue cycle by default", self.guide)
        self.assertIn("plan-only full cycle to a fork-local GitHub Issue", readme)
        self.assertIn("Roadmap full cycle to fork-local Issue (unreleased)", changelog)
        self.assertIn("PERSISTENCE_BLOCKED", self.route)
        self.assertIn("PLAN_ONLY", self.route)
        agents=(ROOT/"AGENTS.md").read_text()
        self.assertIn("PLAN_ONLY full cycle to fork-local Issue", agents)
        self.assertIn("named command default", agents)
        self.assertIn("READY_FOR_FORK_ISSUE_APPROVAL — NOT PUBLISHED", agents)
        self.assertIn("separate exact current-conversation owner approval", agents)

    def test_provenance_and_legal_preflights(self):
        for phrase in ("historical", "original default HEAD", "PR heads/diffs/tests", "license/formalities", "autonomy preflights", "Profile", "Skills", "Index"):
            self.assertIn(phrase,self.route)

    def test_parent_mode_not_a_ladder(self):
        for phrase in ("C(P)", "A(P)", "only for S3/S4/S5", "not a universal grade ladder", "S1/S2/S3*", "P` alone".replace("`",chr(96))):
            self.assertIn(phrase,self.route)

    def test_no_false_cost_or_auto_publication(self):
        for phrase in ("NOT_MEASURED", "exact current-conversation owner approval", "DRAFT — NOT PUBLISHED", "schema-v2"):
            self.assertIn(phrase,self.route)
        self.assertIn("no automatic publication",self.guide.lower())
        self.assertIn("Cost reduction remains a hypothesis",self.template)

    def test_no_intermediate_roadmap_wait_or_publication_shortcut(self):
        agents = (ROOT / "AGENTS.md").read_text()
        self.assertIn("Single-pass roadmap completion; no intermediate operator waiting", self.route)
        self.assertIn("not user review gates", self.route)
        self.assertIn("One-pass completion and user attention", self.guide)
        self.assertIn("not user review gates", self.guide)
        self.assertIn("no routine intermediate waits or user reviews", agents)
        for document in (self.route, self.guide, agents):
            self.assertIn("exact", document.lower())
            self.assertIn("publication", document.lower())
        changelog = (ROOT / "CHANGELOG.md").read_text()
        self.assertLess(changelog.index("## Unreleased"), changelog.index("Roadmap one-pass completion; no intermediate operator waiting"))

    def test_explicit_opensiro_persistence_is_not_a_chat_export(self):
        metadata = (ROOT / "docs/FORK_METADATA.md").read_text()
        agents = (ROOT / "AGENTS.md").read_text()
        for phrase in ("Durable roadmap capture", "PERSISTENCE_BLOCKED", "NOT_PERSISTED", "read back", ".opensiro/issues/<case-id>/"):
            self.assertIn(phrase.lower(), self.route.lower())
        for phrase in ("Persistence completion gate", "scripts/validate_capability_roadmap.py", "A chat archive alone", "PAUSE/STOP"):
            self.assertIn(phrase.lower(), self.guide.lower())
        self.assertIn("Required readback for explicitly retained research cases", metadata)
        self.assertIn("Roadmap `.opensiro` persistence", agents)
        for scope in (self.route, self.guide, agents, metadata):
            self.assertIn("public", scope.lower())
            self.assertIn("contributions/", scope)

    def test_current_case_files_do_not_inherit_versions(self):
        self.assertIn('Stable case filenames, no version suffix', self.route)
        for filename in ('issue.md', 'constructor-sufficiency.md', 'roadmap.md'):
            self.assertIn(filename, self.route)
        self.assertIn('schema_version: 2', self.route)

    def test_three_options_and_source_native_alternative(self):
        for phrase in ("Improve this harness", "Challenge or improve the open specification", "Explore a domain-specific fork", "Closest existing project-native solution", "AI involvement"):
            self.assertIn(phrase,self.template)
        self.assertIn("DRAFT — NOT PUBLISHED",self.template)

if __name__=="__main__":
    unittest.main()
