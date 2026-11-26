"""VSM OSS only: source-pinned local drafts never enter production gates."""
import hashlib
import re
import tempfile
import unittest
from pathlib import Path
from test_experimental_roadmap_targets import make_case, receipt
from validate_capability_roadmap import validate, validate_case_dir
from validate_roadmap_publication import check_case_structure, check_publication_ready

REPO = "opensiro/vsm-oss-organization"
EVIDENCE = b"synthetic local assessment evidence"
LOCAL = {
    "Local assessment source": "https://github.com/" + REPO + "/issues/346",
    "Local assessment SHA-256": hashlib.sha256(EVIDENCE).hexdigest(),
    "Local assessed ref": "b" * 40,
    "Local assessed at": "2026-11-26",
    "Profile ref": "https://github.com/opensiro/vsm-harness-profile/blob/" + "c"*40 + "/PROFILE.md",
    "Methodology ref": "https://github.com/opensiro/vsm-harness-skills/blob/" + "d"*40 + "/METHODOLOGY.md",
}

def localize(body):
    body = re.sub(r"(?m)^- Original repository:.*$", "- Original repository: "+REPO, body)
    body = re.sub(r"(?m)^- Accepted (?:Index assessment|assessment blob SHA|review ref|reviewed at):.*\n", "", body)
    body = body.replace("Accepted VSM vector:", "Local VSM vector:")
    return body.replace("## Function ownership", "\n".join(f"- {k}: {v}" for k,v in LOCAL.items())+"\n\n## Function ownership", 1)

class ReferenceRoadmapTests(unittest.TestCase):
    def test_c_p_a_exact_reference_and_ordinary_rejection(self):
        for target in ("C", "P", "A"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp)
                make_case(path, target)
                (path/"local-assessment-source.md").write_bytes(EVIDENCE)
                r = path/"roadmap.md"
                r.write_text(localize(r.read_text()))
                h = path/"issue.md"
                h.write_text(h.read_text().replace("ACCEPTED HISTORICAL INDEX", "LOCAL REFERENCE ASSESSMENT").replace("Historical Index state", "Historical local state"))
                self.assertEqual(validate_case_dir(path, experimental_target=target, reference_realization=True), [])
                self.assertEqual(check_case_structure(path, experimental_target=target, reference_realization=True), [])
                self.assertTrue(check_case_structure(path, experimental_target=target))
                self.assertTrue(check_publication_ready(path))
                (path/"local-assessment-source.md").write_bytes(b"tampered")
                self.assertTrue(any("digest mismatch" in e for e in check_case_structure(path, experimental_target=target, reference_realization=True)))
    def test_identity_provenance_and_no_index_laundering(self):
        body = localize(receipt("A")[0])
        for bad in (body.replace("- Original repository: "+REPO, "- Original repository: opensiro/upstream"),
                    body.replace("- Original repository: "+REPO, "- Original repository: opensiro-contributions/vsm-oss-organization"),
                    body.replace(LOCAL["Local assessment source"], "https://github.com/other/project/issues/1"),
                    body.replace(LOCAL["Profile ref"], "https://github.com/opensiro/vsm-harness-profile/blob/main/PROFILE.md"),
                    body.replace(LOCAL["Local assessment SHA-256"], "unknown"),
                    body+"\n- Accepted Index assessment: fake\n"):
            self.assertTrue(validate(bad, experimental_target="A", reference_realization=True))
        self.assertTrue(validate(receipt("A")[0], experimental_target="A", reference_realization=True))
    def test_reference_c_boundary(self):
        self.assertTrue(validate(localize(receipt("C", fn="S1", historical="A")[0]), experimental_target="C", reference_realization=True))
        body=localize(receipt("C", current="P", after="C(P)")[0])
        self.assertEqual(validate(body, experimental_target="C", reference_realization=True), [])
        self.assertTrue(validate(body.replace("S4=C(P)", "S4=C"), experimental_target="C", reference_realization=True))
