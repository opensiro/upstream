"""Read-only, fail-closed checks for separate improvement candidate intake."""
import contextlib
import io
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from inspect_improvement_candidates import (CandidateError, inspect, main, read_card)  # noqa: E402


class CandidateIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for src in (ROOT / "candidates").glob("*.md"):
            if src.name != "README.md":
                shutil.copyfile(src, self.root / src.name)

    def target(self):
        return self.root / "agentbox-overlap-manager-20261020.md"

    def replace(self, original, updated):
        path = self.target()
        before = path.read_text()
        self.assertIn(original, before)
        path.write_text(before.replace(original, updated))

    def test_current_cards_are_structurally_valid_but_never_authorized(self):
        before = {p.name: p.read_bytes() for p in self.root.glob("*.md")}
        report = inspect(self.root)
        self.assertEqual(report["count"], len(list(self.root.glob("*.md"))))
        self.assertEqual({x["state"] for x in report["candidates"]},
                         {"BLOCKED_EVIDENCE", "PARKED", "SCREENING"})
        self.assertTrue(all(not x["declared_fit_complete"] for x in report["candidates"]))
        for flag in ("live_index_verified", "native_fit_verified",
                     "candidate_transition_authorized", "proposal_created"):
            self.assertIs(report[flag], False)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.glob("*.md")})

    def test_cli_json_and_text_still_say_no_writes(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(main(["--root", str(self.root)]), 0)
        self.assertIn("NOT_APPROVED_NO_GITHUB_WRITES", out.getvalue())
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(main(["--root", str(self.root), "--format", "json"]), 0)
        self.assertIn('"candidate_transition_authorized": false', out.getvalue())

    def test_qualified_without_all_gates_is_rejected(self):
        self.replace("state: BLOCKED_EVIDENCE", "state: QUALIFIED")
        with self.assertRaisesRegex(CandidateError, "Blocked candidate"):
            inspect(self.root)

    def test_self_declared_qualification_never_authorizes(self):
        self.replace("state: BLOCKED_EVIDENCE", "state: QUALIFIED")
        for field in ("fit_mechanism", "fit_value", "fit_scope"):
            self.replace(field + ": PENDING", field + ": PASS")
        report = inspect(self.root)
        card = next(x for x in report["candidates"] if x["state"] == "QUALIFIED")
        self.assertTrue(card["declared_fit_complete"])
        self.assertFalse(report["native_fit_verified"])
        self.assertFalse(report["candidate_transition_authorized"])

    def test_duplicate_candidate_id(self):
        other = self.root / "second.md"
        other.write_text(self.target().read_text())
        with self.assertRaisesRegex(CandidateError, "Duplicate candidate"):
            inspect(self.root)

    def test_bad_index_ref(self):
        self.replace("index_sha: 5393b698bfdfa4ca14d97a79238234eca20694e5",
                     "index_sha: main")
        with self.assertRaisesRegex(CandidateError, "pinned Index"):
            inspect(self.root)

    def test_wrong_assessment_shard(self):
        self.replace("assessments/ag/agentbox.md", "assessments/zz/agentbox.md")
        with self.assertRaisesRegex(CandidateError, "canonical assessment"):
            inspect(self.root)

    def test_unapproved_status_and_unknown_field(self):
        self.replace("state: BLOCKED_EVIDENCE", "state: AUTHORIZED")
        with self.assertRaisesRegex(CandidateError, "state or origin"):
            inspect(self.root)
        self.replace("state: AUTHORIZED", "state: BLOCKED_EVIDENCE")
        self.replace("fit_scope: PENDING", "fit_scope: PENDING\nauthorized: true")
        with self.assertRaisesRegex(CandidateError, "Unknown, duplicate"):
            inspect(self.root)

    def test_duplicate_metadata_field(self):
        self.replace("fit_scope: PENDING", "fit_scope: PENDING\nfit_scope: PASS")
        with self.assertRaisesRegex(CandidateError, "duplicate"):
            inspect(self.root)

    def test_bad_product_identity(self):
        self.replace("target_repo: madarco/agentbox", "target_repo: invalid")
        with self.assertRaisesRegex(CandidateError, "target repository"):
            inspect(self.root)

    def test_missing_metadata_and_title_disagreement(self):
        self.replace("candidate_id: IMPR-AGENTBOX-S2-OVERLAP-20261020",
                     "candidate_id: IMPR-OTHER-20261020")
        with self.assertRaisesRegex(CandidateError, "Title must expose"):
            inspect(self.root)

    def test_missing_evidence_discussion(self):
        self.replace("## Four native fit gates", "## Unknown section")
        with self.assertRaisesRegex(CandidateError, "four-gate discussion"):
            inspect(self.root)

    def test_missing_root_is_fail_closed(self):
        with self.assertRaisesRegex(CandidateError, "directory missing"):
            inspect(self.root / "missing")

    def test_too_large_is_blocked(self):
        path = self.target()
        path.write_text(path.read_text() + "x" * 32768)
        with self.assertRaisesRegex(CandidateError, "exceeds 32 KiB"):
            inspect(self.root)

    def test_empty_collection_is_valid_but_never_selects_anything(self):
        for path in self.root.glob("*.md"):
            path.unlink()
        report = inspect(self.root)
        self.assertEqual(report["count"], 0)
        self.assertEqual(report["candidates"], [])
        self.assertFalse(report["candidate_transition_authorized"])

    def test_symlinks_not_followed(self):
        path = self.target()
        path.unlink()
        path.symlink_to(ROOT / "candidates" / path.name)
        with self.assertRaisesRegex(CandidateError, "regular Markdown"):
            read_card(path)


if __name__ == "__main__":
    unittest.main()
