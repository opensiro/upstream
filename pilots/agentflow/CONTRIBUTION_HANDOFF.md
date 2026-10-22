# AgentFlow — node IDs escape first-party artifact path boundaries

**Stage:** `AWAITING_EXTERNAL`. Exact tested native source patch; **no** external fork, issue, PR, provider call, task agent or simulated model run.

- **Frozen first-party source:** `agentenv/agentflow@eb51a2e7a5c7d65da5718c4a41843098b60c80e0`; included `S1=A` Index `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`. Index describes graph specification and persistence; this exact path-containment defect was found in `agentflow/specs.py::NodeSpec` and `agentflow/store.py::RunStore.node_artifact_dir` during native code inspection, not derived from an Index score.
- **Need — PASS:** A pipeline could validate a node ID like `../../outside`, an absolute filesystem path, `..`, or nested paths. The genuine `RunStore` uses such node IDs directly under its artifact storage root, allowing directory creation to resolve outside the designated node directory.
- **Mechanism — PASS:** Add one Pydantic `NodeSpec.id` field validator rejecting empty/whitespace-only IDs, `.` and `..`, and path separators for both POSIX and Windows, preserving ordinary IDs and the existing dependency schema.
- **Counterfactual — PASS:** Six native Python `unittest` cases on the **real** `PipelineSpec` validator and AST-extracted **unchanged first-party** `RunStore` path functions, with an isolated temporary directory. Prior: **1 PASS / 5 FAIL**; patched: **6 PASS / 0 FAIL**. No storage action outside the disposable temporary root.
- **Scope — PASS:** Only `agentflow/specs.py`, one native regression script in `tests/`; no orchestrator, agent execution, model API, shell bridge or external state mutation. Optional Jinja2 runtime imports are not available in this environment, so the test loads only the first-party path methods directly from source; the complete upstream suite was not claimed.

## Verification

| Check | Result |
| --- | --- |
| `python3 -m unittest discover -s tests -p test_node_id_artifact_safety.py -v` before | 1 PASS / 5 FAIL |
| Same native test after | 6 PASS / 0 FAIL |
| `git apply --reverse --check` with the source patched | PASS |
| Model, agent, provider, external maintainer acceptance | **Not run / not claimed** |

**Reproducible patch:** [node-id-artifact-path-guard.patch](node-id-artifact-path-guard.patch), SHA256 `4f5a735192cfa294ddfed593b89a7e15eea40c5a8b3d9546f31303e254dafac2`.

**Limits:** Validated pipeline node IDs no longer carry directory components. This is not a guarantee against symlink substitution, arbitrary direct `RunStore` API callers, or OS-level process filesystem access. External publication and maintainer decisions remain with their human owners; generic `continue` proceeds to ConnectOnion.
