# CubeLoop — in-memory checkpoint lets callers mutate saved state by reference

**Stage:** `AWAITING_EXTERNAL`. Technical patch and measured direct-code test receipt only; no external fork, issue, PR, commit, or merge.

- **Frozen source:** `cubeplexai/cubeloop@eb798f9a20c1f516d6a59a991a63a9d4c630f4bf`, canonical included `S1=A` Index snapshot `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`. The VSM assessment surfaced first-party checkpoint/session state; the reference-aliasing bug was found by reading `MemoryCheckpointer` and testing its real implementation, not by inference from the grade.
- **Need — PASS:** `load()` exposes an internal mutable `CheckpointData` object directly; `append()` holds references to caller-owned Pydantic messages; `save_extra()` shallowly copies caller-owned nested dicts. As a result, a caller can mutate persisted messages/metadata after a save or through a loaded snapshot, bypassing checkpointer write methods and the intended write lock. Disk-backed checkpointers do not share this same in-process reference behavior.
- **Mechanism — PASS:** copy on `load()` under the checkpointer lock, deep-copy appended messages using existing first-party helper, deep-copy `extra` before merging. Keep the existing protocol and merge semantics; no session, provider, agent loop or external database changes.
- **Counterfactual — PASS (bounded):** four stdlib `IsolatedAsyncioTestCase` checks against pinned `MemoryCheckpointer`: **3 RED / 1 PASS before**, **4 PASS / 0 FAIL after**. Cases: loaded nested extra mutation, post-save caller dict mutation, post-append caller message mutation and ordinary append/metadata round-trip.
- **Scope — PASS:** one in-memory checkpointer module plus a standalone deterministic test script. Native tests have **no agent instance, model/provider call, faux model, network, database or external service**.

## Execution receipts and limits

| Check | Result |
| --- | --- |
| `UV_CACHE_DIR=/tmp/opensiro-uv-cache-reins-20261022 uv run --no-project --python python3 python -m unittest discover -s tests/checkpointer -p test_memory_copy_boundary_unittest.py -v` before | **1 PASS / 3 RED** |
| Same exact native command after | **4 PASS / 0 FAIL** |
| `python3 -m compileall -q` changed files | PASS |
| `git diff --check` | PASS |
| `git apply --reverse --check` on isolated patched pinned worktree | PASS |
| First-party pytest/ruff/mypy, database/backpressure and full integration | **Not run / not claimed**; upstream maintainers should execute normal CI |

**Patch:** [memory-checkpoint-copy-boundaries.patch](memory-checkpoint-copy-boundaries.patch), SHA256 `6ca11f1be9da3b897b8724710f440c6f48cb100a95129d45e8de2debb91341a6`, byte-identical to tested first-party source diff. All code testing was in a date-scoped local git worktree on the frozen revision, preserving the upstream checkout; there was no external push.

**Adversarial review:** Deep copies add memory/CPU overhead relative to reference returns; this handoff does not benchmark that overhead. It does not address other checkpoint APIs (pending HITL request objects, answers, snapshots, durable providers), and is not a claim of thread-safe full agent execution. Human-owned external publication remains separate. Generic `continue` advances immediately to Evidence Loom.
