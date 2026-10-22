#!/usr/bin/env python3
"""Exercise pinned MAREF transaction code directly, without LLM or pytest imports."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


def load_transaction_module(repo: Path):
    """Load the actual source module, bypassing optional package-wide integrations."""
    source = repo / "src/maref/recursive/recursive_evolution_loop.py"
    spec = importlib.util.spec_from_file_location("_maref_rel_native_probe", source)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load pinned MAREF source: {source}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TransactionRollbackTests(unittest.TestCase):
    """Test real rollback state/bytes with local disposable files only."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manager_class = MAREF.RELTransactionManager
        self.previous_snapshot_root = self.manager_class._SNAPSHOT_DIR
        self.manager_class._SNAPSHOT_DIR = str(self.root / "snapshots")
        self.addCleanup(setattr, self.manager_class, "_SNAPSHOT_DIR", self.previous_snapshot_root)
        self.manager = self.manager_class()

    def test_rollback_restores_preexisting_file(self) -> None:
        file = self.root / "existing.py"
        file.write_text("original\n", encoding="utf-8")
        tx = self.manager.begin([str(file)])
        file.write_text("changed\n", encoding="utf-8")
        self.assertTrue(self.manager.rollback(tx))
        self.assertEqual(file.read_text(encoding="utf-8"), "original\n")

    def test_rollback_removes_later_registered_generated_file(self) -> None:
        file = self.root / "registered_after_begin.py"
        tx = self.manager.begin([])
        file.write_text("generated\n", encoding="utf-8")
        tx.generated_files.append(str(file))
        self.assertTrue(self.manager.rollback(tx))
        self.assertFalse(file.exists())

    def test_rollback_removes_new_file_declared_at_begin(self) -> None:
        file = self.root / "planned_new.py"
        tx = self.manager.begin([str(file)])
        file.write_text("generated\n", encoding="utf-8")
        self.assertTrue(self.manager.rollback(tx))
        self.assertFalse(file.exists(), "rollback must remove a newly created planned output")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 verify_new_file_rollback.py /path/to/maref")
    MAREF = load_transaction_module(Path(sys.argv.pop(1)))
    unittest.main()
