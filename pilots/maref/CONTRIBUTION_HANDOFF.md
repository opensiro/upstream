# MAREF — rollback leaves a newly created planned source file on disk

**Stage:** `AWAITING_EXTERNAL`. This is an internal evidence packet only: no external fork, issue, code commit, PR or merge.

- **Source:** `maref-org/maref@35b1d8108887bf162711c2212b7a67d6e21d9342`, pinned from the included `S1=A` Index assessment at `396a54bb690f8ec7ce966bf9b00b241b30036307`. Current `origin/main` was separately observed at `8c57c098343d15b1d922d8584fbcae0168c7c9f2` on 2026-10-22; the same rollback conditional remained, but testing was performed against the **pinned** source.
- **Origin:** `ASSESSMENT_INFORMED`, not `ASSESSMENT_DERIVED`. The assessment identifies MAREF's code-evolution transaction/rollback function; it did not already identify this exact file-deletion failure.
- **Need — PASS:** `RELTransactionManager.begin(files)` records every planned output in both `snapshots` and `generated_files`, including files not yet present. During `rollback()`, `backup_paths = {snap.path for snap in tx.snapshots}` therefore causes every such planned new file to be skipped during removal, even though no existing version could be restored. The transaction can claim `ROLLED_BACK` while a new generated file persists.
- **Mechanism — PASS:** protect from removal only paths with a real pretransaction backup, leaving newly created paths eligible for removal in the existing rollback loop. No safety gate or constitutional setting is changed.
- **Counterfactual — PASS (bounded):** independent stdlib [source-only probe](verify_new_file_rollback.py) runs the pinned real `recursive_evolution_loop.py` via direct module import, without importing the optional package-wide integrations. Three temporary-file cases: before patch **2 PASS / 1 RED** (new file survives); after patch **3 PASS / 0 FAIL**. The new expected behaviour is also added to the genuine first-party `tests/recursive/test_rel_transaction.py` pytest file, but **that pytest test was not run** in this environment.
- **Scope — PASS:** one source conditional and one first-party test file. Local source edits remain uncommitted and unpushed.

## Native checks and limitations

| Check | Result |
| --- | --- |
| `python3 pilots/maref/verify_new_file_rollback.py /path/to/maref` on pinned baseline | 2 PASS / 1 RED |
| Same stdlib script after patch | 3 PASS / 0 FAIL |
| `python3 -m py_compile` for both changed first-party files | PASS |
| `git diff --check` | PASS |
| First-party `pytest tests/recursive/test_rel_transaction.py` | **Not runnable here**: pytest absent; package import also fails on missing `structlog` |
| Entire first-party suite / ruff / mypy / formal and governance checks | **Not run**, no full-suite or policy-gate claim |

**Patch:** [rollback-new-files.patch](rollback-new-files.patch). SHA256 `166570b6402c60a87c96b4adae4110b2a5756057db2f617b808cd29ecc1525f9`, exactly equal to the tested first-party Git diff. Reverse apply check PASS on the modified pinned checkout.

**Adversarial review:** This narrowly fixes the missing-file/backup identity error. It does not add atomic file operations, check concurrent source modifications, or address the existing behaviour that ignores deletion errors. It cannot establish end-to-end REL safety, maintainers' acceptance, benchmark gains, or a full MAREF green gate. A maintainer should run the new pytest case and project gates with its proper dependencies and verify the live main version before adopting.

**Continuation:** External publication requires a separately attributable human-owned decision. Generic `continue` must skip this `AWAITING_EXTERNAL` row and advance to `ateles-python-dispatch-gate` in the same frozen five-row batch.
