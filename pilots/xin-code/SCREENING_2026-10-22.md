# Xin Code — bounded source screening (batch 02, row 5)

**Disposition:** BLOCKED_EVIDENCE. No accepted intervention, source modification, external PR or model run.

- Canonical Index assessment: `assessments/xi/xin-code.md` at `396a54bb690f8ec7ce966bf9b00b241b30036307`; reviewed source `xincode-ai/xin-code@c5a7969309f7286d1f513caf0821256d4036f4d7`. On 2026-10-22 live `main` resolves to the same SHA.
- First-party `internal/tool/executor.go`: `ExecuteWithPermission` returns explicit errors for denial, unknown tools and execution failure. `ResultNeedAsk` proceeds if the optional `askFn` is nil, which the source explicitly describes as backward compatibility; this is not evidence of an accidental permission bypass.
- The same function ignores the error returned from the pre-tool hook (`allowed, _ := hookRunner.RunPreToolUse(...)`). Whether this permits execution on an errored hook depends on the hook's implementation/contract; no failure is claimed until a native fixed-input Go test proves it.
- The existing `internal/tool/executor_test.go` covers batch dispatch and plan-mode write denial, but not the hypothesized hook-error path. No relevant issue or PR appeared in bounded search. The current environment does not have Go installed, so native RED/GREEN cannot be run.

| Fit gate | Status | Reason |
| --- | --- | --- |
| Need | PENDING | Hook failure behavior not reproduced |
| Mechanism | PASS | Exact pre-tool permission/hook path identified |
| Counterfactual | PENDING | No native RED/GREEN fixture |
| Scope | PASS | Bounded executor path |

**Continuation:** Leave this row evidence-blocked. Advance after the batch is exhausted; no agent-model benchmark may substitute for script tests.
