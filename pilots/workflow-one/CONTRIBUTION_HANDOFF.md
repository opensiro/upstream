# Workflow One — active run ID can be overwritten in scheduler registry

**Stage:** `AWAITING_EXTERNAL`. Exact local native script patch only, no external fork, issue, PR, commit, merge or live dsh execution.

- **Frozen source:** `chumingjun/dsh-harness-one@08aef04761e8c6586efaa4077b49d349d4f0f920`, included `S1=A` Index `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`: the assessment locates the workflow state/scheduling boundary. Actual duplicate-ID flaw came from inspecting the current first-party plugin engine `dsh-plugins/dsh-ccpg-orchestrator/lib/engine.js`. Repository instructions explicitly identify the top-level `server/` as legacy, so this packet does not patch that path.
- **Need — PASS:** `Orchestrator.run()` accepts an explicit `runId` and unconditionally `this.runs.set(id, ...)` even if an earlier run with the same ID is active. The second run overwrites the registry entry used for cancel, progress and ownership; when the first finishes it can delete the second run's map entry. This violates multi-run ID isolation.
- **Mechanism — PASS:** before allocating another run state, reject an already-active `runId` with a clear error; completed run IDs may still be reused. No changes to node execution, scheduling order, model APIs, persistence or first-party run ID generation.
- **Counterfactual — PASS (bounded):** three actual plugin engine `node:test` cases executed with `node <file>`: **1 RED / 2 PASS before**, **3 PASS / 0 FAIL after**. Tests cover simultaneous duplicate ID rejection, legitimate completed-ID reuse and two distinct concurrent IDs. To keep the test entirely script-only, a trivial in-process native test node type pauses execution with a Promise; no `agent` nodes, mock provider or dsh runtime are involved.
- **Scope — PASS:** one collision check in current Node plugin engine and one standalone native Node test file.

## Native checks

| Check | Result |
| --- | --- |
| `node dsh-plugins/dsh-ccpg-orchestrator/test/native-runid-isolation.test.mjs` on pinned source | **2 PASS / 1 RED** |
| Same command after local patch | **3 PASS / 0 FAIL** |
| `node --check dsh-plugins/dsh-ccpg-orchestrator/lib/engine.js` | PASS |
| `git diff --check` | PASS |
| `git apply --reverse --check` against patched pinned checkout | PASS |
| Full 17-script engine suite, actual dsh, web UI, all-package build | **Not run / not claimed**; the test is a bounded script demonstration, not release certification |

**Patch:** [active-runid-registry-guard.patch](active-runid-registry-guard.patch), SHA256 `506d93f2dc2fb64988171f4975a1a974941a68346d12478950c254f1ace24b96`, byte-identical to tested source diff. Native `ajv` and other exact lockfile dependencies were installed locally via `npm ci`; no provider or LLM was launched.

**Limitations:** The check applies to IDs concurrently active in one `Orchestrator` instance. It does not establish distributed uniqueness across processes or external database state, nor does it substitute for the project's required dsh/CI acceptance process. Human-owned external publication remains separate. Generic `continue` advances to Recuris.
