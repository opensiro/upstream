"""Source-native Python path, preimage and negative fork-stage tests (no live writes)."""
import hashlib
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from connected_stage_adapter import NotFound, StageBlocked
from connected_multifile_stage import _validate, _preflight, classified_paths

BASE = "a" * 40


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


class NativePort:
    def __init__(self, source, prod, test, existing):
        self.source = source
        self.fork = "opensiro-contributions/" + source.split("/")[-1]
        self.prod = prod
        self.test = test
        self.existing = existing
        self.prod_source = "production before\n"
        self.test_source = "test before\n"
        self.fork_test = self.test_source
        self.fork_prod = self.prod_source

    def repo(self, name):
        if name == self.source:
            return {"full_name": name, "private": False, "archived": False,
                    "license": {"spdx_id": "MIT"}}
        if name == self.fork:
            return {"full_name": name, "private": False, "archived": False,
                    "fork": True, "parent": {"full_name": self.source},
                    "permissions": {"push": True}}
        raise AssertionError(name)

    def patch_capability(self, owner):
        return {"owner": owner, "actor": "xLagerFeuer",
                "available": True, "authorized": True}

    def branch(self, name, ref):
        if ref == "main":
            return {"sha": BASE}
        raise NotFound()

    def file(self, name, path, ref):
        if path == self.prod:
            return {"content": self.prod_source if name == self.source
                    else self.fork_prod}
        if path == self.test and self.existing:
            return {"content": self.test_source if name == self.source
                    else self.fork_test}
        raise NotFound()


class NativePythonStageTests(unittest.TestCase):
    def _case(self, *, source, prod, test, patch, existing):
        port = NativePort(source, prod, test, existing)
        pre = {prod: sha(port.prod_source)}
        if existing:
            pre[test] = sha(port.test_source)
        action = {
            "working_repo": port.fork,
            "source_branch": "main", "source_sha": BASE,
            "base_branch": "main", "base_sha": BASE,
            "new_branch": "opensiro/native-python-test",
            "patch_text": (ROOT / patch).read_text(),
            "changed_paths": [prod, test],
            "preimage_sha256": pre,
            "postimage_sha256": {prod: sha("production after\n"),
                                  test: sha("test after\n")},
        }
        action["patch_sha256"] = sha(action["patch_text"])
        return port, action

    def test_fara_new_test_file_exact_native_scope(self):
        prod = "src/fara/core/run_context.py"
        test = "tests/test_run_context_resume_identity.py"
        port, action = self._case(
            source="microsoft/fara", prod=prod, test=test,
            patch="pilots/fara/resume-task-identity.patch", existing=False)
        _validate(action)
        item = {"source": port.source, "expected_license": "MIT",
                "fork_name": "fara"}
        self.assertEqual(_preflight(item, action, port), "xLagerFeuer")
        self.assertEqual(classified_paths(action["changed_paths"]), (prod, test))
        port.existing = True
        with self.assertRaisesRegex(StageBlocked, "new test"):
            _preflight(item, action, port)

    def test_evidence_bench_existing_test_requires_two_exact_preimages(self):
        prod = "scientific_agent/policy.py"
        test = "tests/test_policy.py"
        port, action = self._case(
            source="kstawiski/evidence-gated-scientific-agent", prod=prod,
            test=test, patch="pilots/evidence-bench/retrieval-error-admission.patch",
            existing=True)
        _validate(action)
        item = {"source": port.source, "expected_license": "MIT",
                "fork_name": "evidence-gated-scientific-agent"}
        self.assertEqual(_preflight(item, action, port), "xLagerFeuer")
        port.fork_test = "stale test\n"
        with self.assertRaisesRegex(StageBlocked, "preimage"):
            _preflight(item, action, port)
        action["preimage_sha256"].pop(test)
        with self.assertRaisesRegex(StageBlocked, "New test patch"):
            _validate(action)

    def test_unsafe_or_cross_language_native_paths_rejected(self):
        good = ["scientific_agent/policy.py", "tests/test_policy.py"]
        bad = [
            ["scientific_agent/policy.py", "README.md"],
            ["../scientific_agent/policy.py", "tests/test_policy.py"],
            ["src/fara/core/run_context.py", "packages/a/test/test.ts"],
            ["src/fara/core/run_context.py", "tests/../../bad.py"],
            ["src/fara/core/run_context.py", "tests/test_bad.sh"],
            ["scientific_agent/policy.py", "scientific_agent/policy.py"],
        ]
        self.assertEqual(classified_paths(good), tuple(good))
        for paths in bad:
            with self.subTest(paths=paths), self.assertRaises(StageBlocked):
                classified_paths(paths)

    def test_new_test_mode_cannot_claim_existing_preimage(self):
        prod = "src/fara/core/run_context.py"
        test = "tests/test_run_context_resume_identity.py"
        port, action = self._case(
            source="microsoft/fara", prod=prod, test=test,
            patch="pilots/fara/resume-task-identity.patch", existing=False)
        action["preimage_sha256"][test] = sha("pretend existing")
        with self.assertRaisesRegex(StageBlocked, "Existing test patch"):
            _validate(action)


if __name__ == "__main__":
    unittest.main()
