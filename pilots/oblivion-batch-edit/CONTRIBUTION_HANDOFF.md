# Oblivion AI — prevalidate a multi-file edit before changing any file

**Owner:** `opensiro/upstream` [#56](https://github.com/opensiro/upstream/issues/56). **Batch:** [2026-10-22-01](../../data/assessment-candidate-batches/2026-10-22-01.json), row 2/5. **State:** `AWAITING_EXTERNAL` — verified native technical result and an unpublished patch, **no external fork, branch, PR, maintainer contact or merge**. Continue immediately to `gyrfalcon-workspace-guard` while the separate external publication right is pending.

## Origin and fit

- Fresh canonical [Index assessment @ `f2ea54a`](https://github.com/opensiro/vsm-harness-index/blob/f2ea54a19770b21f88d70113fe8c60c72802e19e/assessments/ob/oblivion-ai.md) includes `S1=A` and the source-shipped coding/tool execution loop at reviewed ref `7c57fd23ddd9abb5a2795788364f5dcdf3ec87cb`.
- Read-only GitHub/current `main` and source clone check on 2026-10-22 found the **same** first-party SHA; MIT license. At that check, GitHub returned no open issues or PRs; this is a dated search, not proof of complete duplicate absence or future freshness.
- [Native `tools/batch_edit.py`](https://github.com/Rohith-s-hub/Oblivion-agent/blob/7c57fd23ddd9abb5a2795788364f5dcdf3ec87cb/tools/batch_edit.py) advertises itself as an *atomic multi-file editing tool*, but on an ordered two-edit batch it writes the first file before discovering an invalid `old_text` for the second. It returns both success and errors; the first file remains modified. [Permissions](https://github.com/Rohith-s-hub/Oblivion-agent/blob/7c57fd23ddd9abb5a2795788364f5dcdf3ec87cb/agent/permissions.py) classify `batch_edit` as a mutation but do not supply cross-file rollback.
- **Origin `ASSESSMENT_INFORMED`, not `ASSESSMENT_DERIVED`:** Index selected this product and its tool loop before source inspection, but the precise *partial batch mutation defect* came from first-party code and the script, **not an Index diagnosis**. The benefit is independent of VSM grade changes.
- Independent native fit: `need PASS` (advertised atomic behavior contradicted by reproducible code), `mechanism PASS` (preflight the full list before writes), `counterfactual PASS` (identical source-executing native replay), `scope PASS` (one first-party Python tool, no model or permission semantics changed). A maintainer has **not** approved the design.

## Reproducible native effect

First-party baseline: [`Rohith-s-hub/Oblivion-agent@7c57fd2`](https://github.com/Rohith-s-hub/Oblivion-agent/commit/7c57fd23ddd9abb5a2795788364f5dcdf3ec87cb). Local patch: [`batch-edit-preflight.patch`](batch-edit-preflight.patch), SHA256 `b2264374a0d89eb42b7d66f2fc5076839083a5eb987e4574c9c79c88f38cb601`. Actual product source was loaded by the same [offline replay script](scripted_atomicity_replay.py) in both directories, without LLM, external MCP, provider API, Browser, mock substitute or unrelated first-party behavior.

| Scripted native control | Before (`7c57fd2`) | After (local patch) |
| --- | --- | --- |
| Invalid *second* `old_text`, first file physically changed anyway | **yes (1/1)** | **no (0/1)** |
| Second file unchanged | yes | yes |
| Proper error reported | yes | yes |
| Valid sequential changes to same file | **PASS** | **PASS** |
| Valid independent-file write | **PASS** | **PASS** |

Re-run (the source clone is a local checked-out worktree; refresh exact revisions for future external submission):

```bash
python3 pilots/oblivion-batch-edit/scripted_atomicity_replay.py \
  --target-root /path/to/clean/Oblivion-agent-at-7c57fd2 --expect before
git -C /path/to/patch-worktree apply /path/to/batch-edit-preflight.patch
python3 pilots/oblivion-batch-edit/scripted_atomicity_replay.py \
  --target-root /path/to/patch-worktree --expect after
```

`git apply --check` against the clean source and `git apply --reverse --check` against the modified source both **PASS**. The patch stages edit content (including repeated edits to one path), rejects known invalid input/`old_text` before any physical write and then applies the batch. It **does not provide a true crash-safe multi-file filesystem transaction**, atomic replacement across independent processes, rollback after mid-write I/O failure, or proof of deployed reliability. Native syntax/positive controls passed, but the target repository has not accepted the patch and its full product regression suite was not asserted to have run.

**Reviewable external draft:** `fix(tools): preflight batch_edit before mutating files`. Explain the partial-write bug, deterministic repro and limited scope. External publication remains human-owned; a specific validated fork/branch, fresh overlap/CLA check, actual actor mandate and provider-bound authorization are **not present**. `continue` is not a grant. Record the real external result only if it later happens; meanwhile the frozen batch moves to the next candidate.
