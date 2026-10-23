# AgentHarness S3* — read-only persisted decision-DAG integrity verification

**Status:** `SOURCE_PREPARED / INTERNAL_DRAFT`. This is **not** an external first-party AgentHarness PR, merge or completed Upstream #56 cycle.

## Assessment-first finding → bounded native improvement

- [Included Index assessment](https://github.com/opensiro/vsm-harness-index/blob/114dd45cbe462a4a5ae2a85d02c60d1e15b16a77/assessments/ag/agentharness-alexandrmotologa.md), reviewed source `725ceee14b65bd95365e8e1c2394ac1b245e3b98`: S3*=**C** is an operational constructor for audit/correction backed by host-written content-addressed decision nodes, independent of the model's final answer. This specific finding was read **before** selecting a native intervention.
- The independently refreshed [first-party `main@f42428b9`](https://github.com/alexandrmotologa/agent-harness/commit/f42428b9b616eae8eaa1ac2baa52bda07c2a9964) computes each node's payload/type/parent-hash digest in `DecisionDAG.add_node`, but `DecisionDAG.from_dict` merely reloads persisted hashes and `inspect` displays them without rechecking. A hash **display** is not the same as a hash **verification**.
- First-party root [MIT license](https://github.com/alexandrmotologa/agent-harness/blob/main/LICENSE) **PASS**; [CONTRIBUTING.md](https://github.com/alexandrmotologa/agent-harness/blob/main/CONTRIBUTING.md) asks for a descriptive feature branch, tests, Ruff, and PR to main; no issue-first requirement identified. Current published issue/PR list was checked; no existing equivalent audit verifier was found.
- **Origin class:** `ASSESSMENT_DERIVED` **hypothesis**, not an assertion of maintainer demand, autonomous S3* audit judgment, a VSM grade improvement, or third-party acceptance.

## Implemented opt-in capability

[Four-file native patch](verify-decision-dag.patch) introduces:

1. `DecisionDAG.verify_integrity() -> IntegrityReport`: machine-readable `ok`, `checked_nodes`, `findings[].code/node_id` for stored payload hash mismatch, missing/duplicate parents, missing root/leaf, graph cycles and duplicate serialized node IDs.
2. `agent-harness inspect <run-id> --verify --storage <path>`: read-only integrity PASS/FAIL; non-zero exit for a failed record; ordinary `inspect` remains unchanged.
3. Deterministic native tests for valid round-trip and damaged observation, root, parent and duplicate-ID cases. No model, provider or external service is run.

## Native before/after evidence (2026-10-23)

| Matched persisted-run fixture | Original source | Patched source |
| --- | --- | --- |
| Load a DAG whose serialized observation payload was changed but its stored hash was not | Original CLI `inspect` exits **0** and shows the trajectory without checking integrity; separately rerun pristine-source test **PASS** confirming this behavior | `inspect --verify` exits nonzero with `HASH_MISMATCH` |
| Untampered graph | Normal inspect; verification unavailable | `verify_integrity().ok == True`, CLI `Integrity: PASS` |
| Missing parent / duplicate loaded node | No dedicated integrity check | Machine-readable `MISSING_PARENT` / `DUPLICATE_NODE_ID` findings |

**Executed:** 12/12 focused native tests **PASS**, Ruff lint **PASS**, Python compileall **PASS**, git diff integrity check **PASS**. A broader `tests/unit` run was interrupted after waiting on an unrelated test; no claim of a clean complete suite. The source tree's existing broad Ruff format check requires unrelated formatting; files were not mass-reformatted.

## Reproduce on pinned first-party source

1. Check out `f42428b9b616eae8eaa1ac2baa52bda07c2a9964` and install core runtime and `pytest pytest-asyncio ruff` per `CONTRIBUTING.md` into an isolated Python 3.12 environment.
2. `git apply --check verify-decision-dag.patch`, then `git apply verify-decision-dag.patch`.
3. `python -m pytest -q tests/unit/test_decision_dag.py tests/unit/test_cli.py`.
4. `ruff check src/agent_harness/graph/decision_dag.py src/agent_harness/cli.py tests/unit/test_decision_dag.py tests/unit/test_cli.py`.

## Proof limits and external gate

This checks only the fields included in **existing** `DecisionNode.compute_hash`: payload, node type and parent hashes. It does **not** cryptographically sign authorship, protect unhashed metadata, prove filesystem checkpoint authenticity or defeat a writer who can coherently rewrite the entire DAG and all hashes. It provides no autonomous reviewer/verdict actor or generalized S3* autonomy.

Next: independently confirm first-party product fit for verification UX and retained schema behavior, broader native CI, then separately authorize any **new Improvement** upstream fork/PR. The limited 34-case Corrective publication mandate does not cover this candidate.
