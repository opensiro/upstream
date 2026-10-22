# OniRoute — nested engine and workspace roots pass isolation validation

**Stage:** `AWAITING_EXTERNAL`. A bounded source-only native patch packet; no external fork, issue, PR, model or agent execution.

- **Frozen source:** `AniruddhaDas1/OniRoute_SwarmAgents@c47d553ad2e1aa547cce000c095a9feda5434ee2` (Apache-2.0), included `S1=A` Index `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`; the assessment covers the Python workspace and governance boundary. The original manifest cited `runtime/validation/engine.py`, but the pinned source has a separate actual `runtime/workspace/validation.py::WorkspaceValidator.validate`, the target of this tested patch.
- **Need — PASS:** The validator rejected only equal engine/workspace roots. Either root nested inside the other was marked valid, including through a symlink alias. This undermines the claimed engine/workspace isolation for subsequent artifact writes.
- **Mechanism — PASS:** After resolving paths, reject equal or ancestor/descendant root pairs. Do not emit the existing separation confirmation for an overlapping pair. Preserve disjoint and equal-path behavior.
- **Counterfactual — PASS (bounded):** Five native Python `unittest` cases exercise the exact first-party class body loaded from its AST, with real local temporary directories and a symlink: disjoint roots, equal roots, two nesting orientations, symlink alias. Baseline **2 PASS / 3 FAIL**; after **5 PASS / 0 FAIL**.
- **Scope — PASS:** only `runtime/workspace/validation.py` and `test_native_workspace_overlap_unittest.py`. AST loading preserves the real validator and Pydantic models while skipping unrelated provider/runtime startup dependencies. No agents, inference, model mocks, workspace generation or external execution.

## Verification

| Command | Result |
| --- | --- |
| `python3 -m unittest -q test_native_workspace_overlap_unittest.py` before | 2 PASS / 3 FAIL |
| Same command after | 5 PASS / 0 FAIL |
| `python3 -m py_compile ...`; `git diff --check` | PASS |
| `git apply --reverse --check` on modified pinned checkout | PASS |
| Full agent workspace generation / upstream acceptance | **Not run / not claimed** |

**Exact tested patch:** [nested-workspace-engine-guard.patch](nested-workspace-engine-guard.patch), SHA256 `4b0a6e51f45bc253c5988b52120c784dc755b58f5f98b507e878f76f024fd4c5`.

**Limits:** Verifies directory overlap handling only. The preexisting `READ_ONLY_ENGINE_CONFIRMED` info name is not independent proof of OS read-only permissions; no sandbox hardening or quality of generated work is claimed. External PR submission remains human-owned. Generic `continue` advances to Active Graph.
