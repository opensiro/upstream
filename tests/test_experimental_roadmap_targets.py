"""Synthetic experimental A/P cases; no real source, authority or publication claim."""
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_capability_roadmap import validate, validate_case_dir
from validate_roadmap_publication import check_case_structure, check_publication_ready
from test_roadmap_case_consistency import PROPOSAL, VECTOR

BASE_FIELDS = {
    "Current selected function state": "—",
    "Mode preservation": "PRESERVE",
    "Mode rationale": "Preserve supported modes; synthetic evidence",
    "Prospective authority": "Synthetic bounded authority hypothesis only",
    "Cross-function authority compatibility": "Synthetic scope and return; no new authority",
}


def receipt(target="A", current="—", after=None, decision="GO", preservation="PRESERVE",
            fn="S4", historical="—", no_target=False):
    after = target if after is None else after
    fields = dict(BASE_FIELDS, **{
        "Target family": target,
        "Current selected function state": current,
        "Mode preservation": preservation,
        "Target transition": f"NO_QUALIFIED_{target}_TARGET" if no_target else
            f"{fn}={historical} -> {fn}={after}",
        "Proposal-stage decision": decision,
        "Research disposition": "NEEDS_EVIDENCE",
    })
    vector = dict(part.split("=", 1) for part in VECTOR.split(" · "))
    vector[fn] = historical
    vector_text = " · ".join(f"{key}={state}" for key, state in vector.items())
    body = (PROPOSAL.replace("proposal-gate", "experimental-proposal-gate", 1)
            .replace(VECTOR, vector_text)
            .replace("Proposed C construction", "Proposed target construction")
            .replace("C sufficiency falsifier", "Target sufficiency falsifier"))
    for key, val in fields.items():
        pattern = r"(?m)^- " + re.escape(key) + r":.*$"
        if re.search(pattern, body):
            body = re.sub(pattern, lambda _: f"- {key}: {val}", body)
        else:
            body = body.replace("## Function ownership", f"- {key}: {val}\n\n## Function ownership", 1)
    return body, fields, vector, vector_text


def make_case(directory, target="A", **kwargs):
    body, fields, vector, vector_text = receipt(target, **kwargs)
    (directory / "roadmap.md").write_text(body, encoding="utf-8")
    (directory / "README.md").write_text("# Case\nEXPERIMENTAL — DRAFT ONLY\n"
        "[roadmap.md](roadmap.md) [issue.md](issue.md) "
        "[constructor-sufficiency.md](constructor-sufficiency.md)\n", encoding="utf-8")
    for filename, template in (("issue.md", "EXPERIMENTAL_ROADMAP_HUMAN.md"),
                               ("constructor-sufficiency.md", "EXPERIMENTAL_ROADMAP_AI.md")):
        text = (ROOT / "templates" / template).read_text(encoding="utf-8")
        text = text.replace("[HARNESS]", "Synthetic harness").replace("[selected function]", "S4")
        if filename == "issue.md":
            for fn, state in vector.items():
                text = re.sub(r"(?m)^(\| \*\*" + re.escape(fn) + r" ·[^|]+\|) \[accepted\]",
                              lambda m: m[1] + " " + state, text)
            text = re.sub(r"(?m)^\*\*ACCEPTED HISTORICAL INDEX\*\*.*$",
                          "**ACCEPTED HISTORICAL INDEX** — " + vector_text, text)
        for key, val in fields.items():
            text = re.sub(r"(?m)^\*\*" + re.escape(key) + r":\*\*.*$",
                          lambda _: f"**{key}:** {val}", text)
        text = re.sub(r"\[([^\]\n]+)\](?!\()", "synthetic source-grounded draft", text)
        (directory / filename).write_text(text, encoding="utf-8")


class ExperimentalRoadmapTests(unittest.TestCase):
    def test_explicit_a_p_and_composite(self):
        for target, current, after in (
            ("A", "—", "A"), ("A", "C", "A"), ("A", "P", "A(P)"),
            ("A", "C(P)", "A(P)"), ("P", "—", "P"),
            ("P", "C", "C(P)"), ("P", "A", "A(P)"),
        ):
            with self.subTest(target=target, current=current, after=after):
                body, *_ = receipt(target, current, after)
                self.assertEqual(validate(body, experimental_target=target), [])
                self.assertTrue(validate(body))  # never accepted by default C gate

    def test_default_c_unchanged(self):
        self.assertEqual(validate(PROPOSAL), [])
        self.assertTrue(validate(PROPOSAL, experimental_target="A"))

    def test_parent_notation_function_boundary(self):
        for fn, historical in (("S1", "A"), ("S2", "A"), ("S3*", "A")):
            body, *_ = receipt("P", "A", "A(P)", fn=fn, historical=historical)
            self.assertTrue(any("only for" in e for e in validate(body, experimental_target="P")))

    def test_preserve_parent_and_autonomous_modes(self):
        for target, current, after in (("A", "P", "A"), ("P", "C", "P"), ("P", "A", "P")):
            body, *_ = receipt(target, current, after)
            self.assertTrue(any("preserved current modes" in e for e in validate(body, experimental_target=target)))

    def test_explicit_hypothetical_replacement(self):
        body, *_ = receipt("A", "P", "A", preservation="REPLACE")
        self.assertEqual(validate(body, experimental_target="A"), [])
        self.assertTrue(validate(body.replace("- Mode rationale: Preserve supported modes; synthetic evidence\n", ""),
                                 experimental_target="A"))

    def test_no_go_and_blocked(self):
        body, *_ = receipt("P", current="NONE", preservation="NOT_APPLICABLE", decision="NO_GO", no_target=True)
        self.assertEqual(validate(body, experimental_target="P"), [])
        body, *_ = receipt("A", current="?", preservation="UNRESOLVED", decision="BLOCKED")
        self.assertEqual(validate(body, experimental_target="A"), [])
        self.assertTrue(validate(body.replace("decision: BLOCKED", "decision: GO"), experimental_target="A"))
        body, *_ = receipt("A", current="A", after="A")
        self.assertTrue(any("already established" in e for e in validate(body, experimental_target="A")))

    def test_wrong_family_and_historical_mismatch(self):
        body, *_ = receipt("A")
        self.assertTrue(validate(body, experimental_target="P"))
        self.assertTrue(validate(body.replace("S4=— -> S4=A", "S4=C -> S4=A"), experimental_target="A"))

    def test_full_four_file_draft_and_production_gate_rejects(self):
        for target in ("A", "P"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp)
                make_case(path, target)
                self.assertEqual(validate_case_dir(path, experimental_target=target), [])
                self.assertEqual(check_case_structure(path, experimental_target=target), [])
                self.assertTrue(check_publication_ready(path))
                self.assertTrue(check_case_structure(path, experimental_target="P" if target == "A" else "A"))
                ai = path / "constructor-sufficiency.md"
                ai.write_text(ai.read_text().replace("**Mode preservation:** PRESERVE", "**Mode preservation:** REPLACE"))
                self.assertTrue(any("Mode preservation disagrees" in e for e in check_case_structure(path, experimental_target=target)))

    def test_missing_marker_or_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            make_case(path)
            readme = path / "README.md"
            readme.write_text(readme.read_text().replace("EXPERIMENTAL — DRAFT ONLY", "DRAFT"))
            self.assertTrue(any("missing experimental draft-only marker" in e for e in check_case_structure(path, experimental_target="A")))
            readme.unlink()
            self.assertTrue(check_case_structure(path, experimental_target="A"))


if __name__ == "__main__":
    unittest.main()
