# orch — checkpoint roundtrip drops repository context and update time

**Stage:** `AWAITING_EXTERNAL`. Internal native evidence only; no external fork, issue, commit, PR, or merge.

- **Source:** `fbrubacher/orch@16960b40ed6293e27e4536bbd99d62989264a87e`, pinned from the included `S1=A` Index assessment at `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`, not `ASSESSMENT_DERIVED`. The assessment identifies the workflow checkpoint/resume mechanism; the concrete omitted state fields were found during this native source screen.
- **Need — PASS:** `WorkflowState` contains `repository_context`, but `to_dict` never writes it and `from_dict` does not load it. `save_state`/`load_state` silently returns an empty context after a real disk roundtrip. The serialized `updated_at` timestamp also disappears on load because a new default timestamp is generated.
- **Mechanism — PASS:** add the two state fields to the existing JSON to/from mapping, preserving a default for earlier checkpoints that lack them. Does not change atomic replacement, orchestrator phases, resume policy, client adapters, or external finalizer.
- **Counterfactual — PASS (bounded):** four fixed-input, real-source Python stdlib `unittest` cases: before **1 PASS / 2 FAIL / 1 ERROR**, all three field-preservation assertions RED; after **4 PASS / 0 FAIL**. Direct-source imports use a private Python package namespace to bypass optional imports from top-level `orchestrator/__init__.py` (`requests` is absent here); the actual `state.py` and `persistence.py` functions are still executed. No LLM agents, dummy clients, or provider calls were run.
- **Scope — PASS:** two added dictionary mappings and `updated_at` load in `orchestrator/state.py`, plus one direct-source stdlib test file.

## Native checks and limitations

| Check | Result |
| --- | --- |
| `python3 -m unittest -v tests/test_checkpoint_roundtrip_unittest.py` before patch | 1 PASS / 2 FAIL / 1 ERROR (three RED assertions) |
| Same native test after patch | **4 PASS / 0 FAIL** |
| `python3 -m compileall -q orchestrator/state.py orchestrator/persistence.py tests/test_checkpoint_roundtrip_unittest.py` | PASS |
| `git diff --check` | PASS |
| `git apply --reverse --check` against pinned checkout | PASS |
| Shipped `pytest tests/test_offline.py` | **Not run:** pytest/requests absent here; broad test module imports optional OpenRouter integration |
| Live router/planner/executor, full CI and real checkpointed provider workflow | **Not run / not claimed** |

**Patch:** [checkpoint-state-roundtrip.patch](checkpoint-state-roundtrip.patch), SHA256 `b8f86eb2d761470846246308da94e733711969ca5203de4b1d6001b22de44207`, equal to the tested native Git diff. Reverse apply check passed. Local external source remains uncommitted and unpushed.

**Adversarial review:** `repository_context` is currently defined on `WorkflowState` but not read by the shipped orchestrator control loop, so this is a correctness fix to the persistence contract, **not evidence of improved actual agent resume success**. The patch does not enforce `STATE_VERSION`, test concurrent checkpoint writers, or guarantee filesystem durability after a power loss. Maintainership should run the full suite and decide whether this unused context field is intended to be persisted.

**Continuation:** External publication remains human-owned. Generic `continue` skips this `AWAITING_EXTERNAL` row and advances to `matterloop-taskgraph-checkpoint-recovery`.

## 2026-10-25 publication licence gate

Upstream `main` remains the original tested SHA `16960b40ed6293e27e4536bbd99d62989264a87e`; the omitted `repository_context` and `updated_at` roundtrip fields are still visible. No overlapping fix PR was identified in the bounded search. The previous first-party RED/GREEN is preserved, but **no current-session tests were run**.

The upstream public repository has **no LICENSE file**, and its live GitHub repository API reports `license: null`; neither `CONTRIBUTING.md` nor an explicit external contribution licence was found. Public source visibility alone does not grant reuse rights.

**Publication: BLOCKED (missing upstream licence).** No fork, push, commit or external PR was created. The candidate remains part of the frozen 34-case history; the next queued row is selected by the finite ledger.
