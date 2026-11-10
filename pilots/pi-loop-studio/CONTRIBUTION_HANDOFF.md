# Pi Loop Studio — malformed plan list fields pass the first-party host gate

**Stage:** `AWAITING_EXTERNAL`. Internal source-only script packet, not an external fork, issue, PR or model-driven run.

- **Frozen source:** `LEO001020/pi-loop-studio-orchestra@0a6b65c63a0eb11f2e928e773de1774b2c7d5bd7` (MIT), Index included `S1=A` at `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`. The assessment points to the first-party workspace and plan/ownership gate. The malformed-input contract was established from `server/workspace.mjs::validatePlan` and its downstream `server/workflow.mjs` uses, not claimed as an assessment output.
- **Need — PASS:** The plan host validator accepted nonempty strings in place of `successCriteria`, `verificationCommands`, individual task `acceptance` and empty-string `dependsOn`. Downstream code calls `.every()` or `.map()` on lists and spreads verification commands; wrongly accepted strings can therefore cause workflow errors or individual-character commands.
- **Mechanism — PASS:** enforce array/string types at the admission boundary independently of the tool's declared JSON schema; return `INVALID_PLAN_SHAPE` before dependency and acceptance logic. Preserve the existing error for empty acceptance and the valid plan path.
- **Counterfactual — PASS (bounded):** six pure native Node tests against the genuine pinned module: **2 PASS / 4 FAIL before**, **6 PASS / 0 FAIL after**. Four missing-form cases and two controls (valid structured plan, existing missing-acceptance rejection).
- **Scope — PASS:** one first-party JS function and one Node test file. No `Pi` SDK agent loop, model, provider, browser/UI, parallel executor, or task-efficacy test was invoked.

## Verification

| Check | Outcome |
| --- | --- |
| `node tests/native-plan-shape.test.mjs` before | 2 PASS / 4 FAIL |
| Same native script after | 6 PASS / 0 FAIL |
| `node --check server/workspace.mjs`; `git diff --check` | PASS |
| `git apply --reverse --check` against modified pinned source | PASS |
| End-to-end publication, live independent agents, project-wide tests | **Not executed / not claimed** |

**Exact tested patch:** [native-plan-shape-guard.patch](native-plan-shape-guard.patch), SHA256 `e5fe84d5d3b549ec6de6364a89348ca86ff9fd93b7f7564501a828d2f2be261c`. Exact byte match to the local source diff. Dependencies from pinned `package-lock.json` were installed with `npm ci --ignore-scripts --omit=dev`, without package install scripts or any LLM calls.

**Limitations:** Demonstrates malformed direct inputs to `validatePlan`, not that the model runtime frequently emits schema-invalid tool calls; model SDKs may reject those earlier. It does not establish end-to-end agent reliability or imply external acceptance. Human-owned publication is a separate stage. Generic `continue` moves to OpenOrbit.
