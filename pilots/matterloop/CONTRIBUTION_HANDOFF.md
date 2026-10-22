# matterloop — duplicate restored task states are silently discarded

**Stage:** `AWAITING_EXTERNAL`. Internal native patch and evidence only; no external fork, issue, commit, PR, or merge.

- **Source:** `huleidada/matterloop@a98e384fb02814de3e6ba3902cfee2c041e2d40f`, pinned from the included `S1=A` Index assessment at `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`, not `ASSESSMENT_DERIVED`. The assessment surfaced TaskGraph snapshot recovery and strict transition validation; the duplicate-state acceptance hole was found by direct-script source screening.
- **Need — PASS:** restoring states uses `{state.spec.task_id: state for state in states}`. Two snapshot entries with the same task ID (even conflicting statuses) therefore collapse into one value before set-membership checks. `TaskGraph((task,), states=(TaskState(task), TaskState(task)))` incorrectly succeeds while one snapshot record is discarded without audit.
- **Mechanism — PASS:** compare the restored mapping size to the original list/tuple count and reject duplicates with the existing `InvalidTaskGraphError` before validating task coverage and definitions. No changes to execution, review, approval, retry, model adapters or replay-safe scheduling.
- **Counterfactual — PASS (bounded):** four fixed-input real-source stdlib `unittest` cases: before **2 PASS / 2 RED**; after **4 PASS / 0 FAIL**. Tests cover duplicate identical and conflicting entries plus exact-once and missing-state cases. They execute only `TaskGraph` construction, without an agent/provider run.
- **Scope — PASS:** one validation guard in `matterloop-agents/.../task_graph.py`, plus a standalone stdlib direct-source test script.

## Native checks and limitations

| Check | Result |
| --- | --- |
| `PYTHONPATH=matterloop-core/src/python python3 matterloop-agents/tests/native_taskgraph_restore_unittest.py -v` before | **2 PASS / 2 RED** |
| Same native script after | **4 PASS / 0 FAIL** |
| `python3 -m compileall -q` for both changed Python files | PASS |
| `git diff --check` | PASS |
| `git apply --reverse --check` on modified pinned checkout | PASS |
| First-party `pytest matterloop-agents/tests/test_collaboration_task_graph.py` | **Not run:** pytest absent, normal `matterloop_agents` imports require additional optional packages |
| Full first-party suite / process-recovery integration / live agent | **Not run / not claimed** |

**Patch:** [restore-duplicate-state-guard.patch](restore-duplicate-state-guard.patch), SHA256 `4db0427bdc9c6a8ba2ea6abb9a8d0fc844711eeee607d0f2b9091e8259847b95`, identical to the tested first-party Git diff. Reverse-apply check passed. External code remains local, uncommitted, and unpushed.

**Adversarial review:** The standalone test imports real `TaskGraph`, value models and errors through a private in-process package namespace to avoid unrelated optional agent/runtime imports. The guard does not verify snapshot provenance, duplicate records in upstream stores before deserialization, atomic persistence, or runtime concurrency. Maintainers should run their normal Python environment/CI before adoption.

**Continuation:** External PR is human-owned. Generic `continue` advances directly to freezing another full nonduplicate, included S1=A assessment cohort once this final row is recorded.
