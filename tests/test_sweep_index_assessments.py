"""Synthetic-only tests for Index-wide, six-function improvement intake coverage."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from sweep_index_assessments import (FUNCTIONS, SweepError, audit, main,
                                    parse_assessment)  # noqa: E402

REAL_INDEX = "5393b698bfdfa4ca14d97a79238234eca20694e5"
REVIEW = "463a6a0a20176147f0b0dbfa8a261aba5e43cbd6"
CID = "IMPR-AGENTBOX-S2-OVERLAP-20261020"


def git(root, *args):
    p = subprocess.run(["git", "-C", str(root), *args], check=True,
                       capture_output=True, text=True)
    return p.stdout.strip()


def assessment(name, repo, status="included", extra="last_checked_ref: " + "a" * 40):
    lines = [
        "---", "harness_id: " + name, "repository: https://github.com/" + repo,
        "review_ref: " + REVIEW, "status: " + status,
        "profile_version: 0.2.4",
        "assessment_procedure_version: 0.3.7",
        extra,
        *("autonomy_" + f.lower().replace("*", "_star") + ": —" for f in FUNCTIONS),
        "---", "", "# " + name, "", "## Review boundary",
        "Synthetic review without any external product evidence.",
    ]
    for f in FUNCTIONS:
        lines.extend(("", "## " + f + " — Synthetic function", "Some local fixture text."))
    return "\n".join(lines) + "\n"


class FullIndexSweepTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.index = root / "index"
        self.index.mkdir()
        self.reviews = root / "sweeps"
        self.reviews.mkdir()
        self.cards = root / "candidates"
        self.cards.mkdir()
        git(self.index, "init", "-q")
        git(self.index, "config", "user.name", "Example")
        git(self.index, "config", "user.email", "example@example.invalid")
        for filename, target, status in (
            ("ag/agentbox.md", "madarco/agentbox", "included"),
            ("be/beta.md", "someowner/beta", "included"),
            ("ex/excluded.md", "someowner/excluded", "excluded-no-agentic-vsm"),
            ("pr/proposed.md", "someowner/proposed", "proposed"),
        ):
            p = self.index / "assessments" / filename
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(assessment(p.stem, target, status))
        git(self.index, "add", ".")
        git(self.index, "commit", "-q", "-m", "synthetic four system corpus")
        self.sha = git(self.index, "rev-parse", "HEAD")
        orig = ROOT / "candidates/agentbox-overlap-manager-20261020.md"
        copy = orig.read_text().replace(REAL_INDEX, self.sha)
        (self.cards / orig.name).write_text(copy)
        self.receipt = self.reviews / "agentbox.json"
        self.declaration = json.loads((ROOT / "sweeps/agentbox.json").read_text())
        self.declaration["index_sha"] = self.sha
        self.save()

    def save(self):
        self.receipt.write_text(json.dumps(self.declaration, indent=2))

    def inspect(self, **kwargs):
        args = dict(index_root=self.index, index_sha=self.sha,
                    reviews_root=self.reviews, candidate_root=self.cards,
                    limit=1000)
        args.update(kwargs)
        return audit(**args)

    def test_two_included_out_of_four_records_six_function_slots_each(self):
        result = self.inspect()
        self.assertEqual(result["assessment_files"], 4)
        self.assertEqual(result["publication_counts"], {
            "included": 2, "excluded-no-agentic-vsm": 1, "proposed": 1})
        self.assertEqual(result["required_function_slots"], 12)
        self.assertEqual(result["reviewed_function_slots_declared"], 6)
        self.assertEqual(result["systems_fully_screened_declared"], 1)
        self.assertEqual(result["systems_incomplete"], 1)
        self.assertEqual(result["queue"][0]["harness_id"], "beta")
        self.assertEqual(result["queue"][0]["reviewed_functions"], 0)
        for k in ("native_fit_verified", "actual_product_improvement_verified",
                  "live_canonical_index_attested", "execution_available"):
            self.assertFalse(result[k])
        self.assertEqual(result["authorization_status"], "NOT_APPROVED_NO_GITHUB_WRITES")

    def test_zero_candidate_six_function_review_is_valid(self):
        self.declaration["functions"]["S2"] = {
            "outcome": "REVIEWED_ZERO",
            "rationale": "No separate supported product improvement emerges from this bounded local functional review; further native evidence is needed.",
            "candidate_ids": [],
        }
        self.save()
        result = self.inspect()
        self.assertEqual(result["systems_fully_screened_declared"], 1)
        self.assertEqual(result["reviewed_function_slots_declared"], 6)

    def test_missing_receipt_is_not_silent_zero_outcome(self):
        self.receipt.unlink()
        result = self.inspect()
        self.assertEqual(result["systems_fully_screened_declared"], 0)
        self.assertEqual(result["reviewed_function_slots_declared"], 0)
        self.assertEqual(result["systems_incomplete"], 2)

    def test_blocked_slot_does_not_count_as_complete(self):
        self.declaration["functions"]["S3"]["outcome"] = "BLOCKED_EVIDENCE"
        self.save()
        result = self.inspect()
        self.assertEqual(result["reviewed_function_slots_declared"], 5)
        self.assertEqual(result["systems_fully_screened_declared"], 0)
        self.assertEqual(result["queue"][0]["reviewed_functions"], 5)

    def test_partial_unreviewed_requires_clear_empty_rationale(self):
        self.declaration["functions"]["S3"] = {
            "outcome": "UNREVIEWED", "rationale": "", "candidate_ids": []}
        self.save()
        self.assertEqual(self.inspect()["reviewed_function_slots_declared"], 5)
        self.declaration["functions"]["S3"]["rationale"] = "pretend complete"
        self.save()
        with self.assertRaisesRegex(SweepError, "Unreviewed slot"):
            self.inspect()

    def test_all_six_slots_are_mandatory_in_receipts(self):
        self.declaration["functions"].pop("S3*")
        self.save()
        with self.assertRaisesRegex(SweepError, "six function slots"):
            self.inspect()

    def test_false_hypothesis_without_card_is_rejected(self):
        self.declaration["functions"]["S4"]["outcome"] = "HYPOTHESES_RECORDED"
        self.save()
        with self.assertRaisesRegex(SweepError, "Hypothesis review"):
            self.inspect()
        self.declaration["functions"]["S4"]["candidate_ids"] = ["IMPR-FAKE"]
        self.save()
        with self.assertRaisesRegex(SweepError, "Unknown/repeated candidate"):
            self.inspect()

    def test_mismatched_card_index_linkage_rejected(self):
        card = next(self.cards.glob("*.md"))
        card.write_text(card.read_text().replace("target_repo: madarco/agentbox",
                                                 "target_repo: someone/other"))
        with self.assertRaisesRegex(SweepError, "Candidate origin/target"):
            self.inspect()

    def test_stale_or_invented_index_head_rejected(self):
        with self.assertRaisesRegex(SweepError, "HEAD differs"):
            self.inspect(index_sha="f" * 40)
        self.declaration["index_sha"] = "f" * 40
        self.save()
        with self.assertRaisesRegex(SweepError, "different index_sha"):
            self.inspect()

    def test_orphan_or_unknown_receipt_blocked(self):
        (self.reviews / "no-such-harness.json").write_text("{}")
        with self.assertRaisesRegex(SweepError, "Unknown/orphan review receipt"):
            self.inspect()

    def test_included_missing_S3_star_section_blocks_entire_sweep(self):
        source = assessment("beta", "someowner/beta")
        source = source.replace("## S3* — Synthetic function", "## Unrelated section")
        with self.assertRaisesRegex(SweepError, "missing function section S3"):
            parse_assessment(source.encode(), "assessments/be/beta.md")

    def test_duplicate_JSON_metadata_rejected(self):
        content = self.receipt.read_text()
        self.receipt.write_text(content.replace('"schema_version": 1,',
                                                '"schema_version": 1, "schema_version": 1,'))
        with self.assertRaisesRegex(SweepError, "Duplicate JSON field"):
            self.inspect()

    def test_old_extra_metadata_is_allowed_but_duplicate_identity_is_not(self):
        raw = assessment("agentbox", "madarco/agentbox",
                         extra="last_reassessment_round: R2")
        entry = parse_assessment(raw.encode(), "assessments/ag/agentbox.md")
        self.assertEqual(entry["publication_status"], "included")
        with self.assertRaisesRegex(SweepError, "Duplicate/invalid"):
            parse_assessment(raw.replace("status: included",
                                         "status: included\nstatus: proposed").encode(),
                             "assessments/ag/agentbox.md")

    def test_paginated_queue_deterministic_and_no_writes(self):
        first = self.inspect(offset=0, limit=1)
        self.assertEqual(len(first["queue"]), 1)
        self.assertEqual(first["queue"][0]["harness_id"], "beta")
        self.assertEqual(self.inspect(offset=1, limit=1)["queue"], [])
        with self.assertRaisesRegex(SweepError, "Invalid bounded"):
            self.inspect(limit=-1)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(["--index-root", str(self.index),
                         "--index-sha", self.sha,
                         "--reviews-root", str(self.reviews),
                         "--candidate-root", str(self.cards)])
        self.assertEqual(code, 0)
        self.assertIn("NOT_APPROVED_NO_GITHUB_WRITES", out.getvalue())
        self.assertIn("1/2", out.getvalue())


if __name__ == "__main__":
    unittest.main()
