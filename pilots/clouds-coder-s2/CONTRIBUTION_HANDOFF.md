# Clouds-Coder — preserve human-owned frozen conflicts across child-process writes (S2)

**Internal technical handoff only.** Upstream [#56](https://github.com/opensiro/upstream/issues/56), batch 15, reviewable [PR #183](https://github.com/opensiro/upstream/pull/183). No fork/branch/external PR at `FonaTech/Clouds-Coder` was created; general external stage authorization is still gated by Upstream [#6](https://github.com/opensiro/upstream/issues/6).

## Strict assessment-derived origin

The pinned [Index assessment](https://github.com/opensiro/vsm-harness-index/blob/46219bf103b0b122d86abc3ca70ae3d8bc820e2c/assessments/cl/clouds-coder.md) identifies a constructor-owned `S2=C` conflict/revision/freeze enforcement loop with human-owned disputed merge settlement. The [immutable pre-code checkpoint `b97eefe`](https://github.com/opensiro/upstream/blob/b97eefe613dca3c4776c449659f2735425e298b9/data/assessment-candidate-batches/2026-11-08-15-HYPOTHESES.md) predicted that an operating bridge might bypass freeze on a retry or process write. It recorded the null case and falsifier **before** fresh first-party code/issue inspection. This label does not promise `C → A`.

The first-party MIT implementation at [`83a0d25`](https://github.com/FonaTech/Clouds-Coder/blob/83a0d25aa59ef1bc8e295ec45104a9c7f0819c83/Clouds_Coder.py) checks `row["frozen"]` for normal whole-file writes, OT operations, deletes and renames. But `CollaborationStore.adopt_process_write()` and `adopt_process_delete()` independently settle file effects *already made on disk* by agent/shell processes under a project mutation lease: when the expected revision matches, neither checks the frozen flag before committing a new revision or deleting conflict records. `CollaborationWriteCoordinator.finish_process()` reaches both paths. Thus a frozen case can be bypassed even with no stale revision mismatch; merely returning an error is insufficient without restoring the protected on-disk file.

## Minimal repair and independent verification

| Artifact | Function |
| --- | --- |
| [`frozen-process-regression-tests.patch`](frozen-process-regression-tests.patch) | Two additions to original `tests/test_collaboration.py`: process overwrite and process deletion during a pending frozen conflict, asserting refusal, preserved revision/case and restored content. |
| [`frozen-process-fix.patch`](frozen-process-fix.patch) | Update canonical `Clouds_Coder.py` before same-revision process settlement: reject the mutation, roll back DB transaction, restore protected disk bytes, emit bounded `document_frozen` result. Existing divergent-stale candidate handling is unchanged. |
| [`independent-runner.sh`](independent-runner.sh) | Archived non-active recipe for a distinct deterministic host/CI runner; sources are pinned and matched before/after. |
| [Independent host receipt](INDEPENDENT_HOST_RECEIPT_2026-11-08.md) | Separate `systemd` unit, 2 baseline failures, 2 repaired regressions and 2 original controls passing; generated distribution validated. |

The `Code_Structure` tree is **generated** from `Clouds_Coder.py`; do not patch generated `core.py` as the sole source. Apply the patch to the monolith and run the project's splitter (`python3 split_coder.py Clouds_Coder.py -o Code_Structure --update`) before assembling an external contribution. A stale attempt against only the generated split was recorded as failed setup, not counted. The patch dry-checks on the later observed public main `6f187a3`, but future publication must freshly rebase tests/derived files on the latest upstream default and run native validation again.

**Fit:** `need=PASS`, `mechanism=PASS`, `counterfactual=PASS`, `scope=PASS`; origin `ASSESSMENT_DERIVED`, bounded benefit `SOURCE_NATIVE_CORRECTNESS`, operational stage `AWAITING_EXTERNAL`, external action `NOT_EXECUTED`. This fixes a concrete S2 freeze interference path; it neither autonomizes human conflict review nor changes the Index grade. Preserve licensing, contributor-policy, effective fork/branch/PR rights and maintainer decisions separately before any external write.
