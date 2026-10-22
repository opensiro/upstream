# Fractale — native-first batch screen, no admitted patch

**Batch:** [`2026-10-22-01`](../../data/assessment-candidate-batches/2026-10-22-01.json) row 1/5. **Verdict:** `BLOCKED_EVIDENCE` at read-only screening; **next:** `oblivion-agent-tool-loop`. This is not an external project intervention, contributor PR, negative verdict on the project's quality or evidence of a VSM grade change.

- Canonical general Index at [`f2ea54a`](https://github.com/opensiro/vsm-harness-index/blob/f2ea54a19770b21f88d70113fe8c60c72802e19e/assessments/fr/fractale.md) includes Fractale `S1=A` and describes a model/tool-feedback workflow with first-party native state transitions. The assessment does **not** diagnose a specific defect in long-running MCP task handling.
- Read-only live GitHub repo check on 2026-10-22: [`converged-computing/fractale`](https://github.com/converged-computing/fractale) default branch `main` still at `b62ff1bce01e191828b90c5fa468f81197629e32`, exactly the Index `review_ref`; LICENSE is MIT. This is a dated check, not future freshness assurance.
- First-party [issue #10](https://github.com/converged-computing/fractale/issues/10) requests **support for long-running tasks** in the MCP API, including tagging Docker build-like functions. Need `PASS` as an actual maintainer issue; it does **not** imply a specified or accepted patch.
- Native [`AgentBase.call_tool`](https://github.com/converged-computing/fractale/blob/b62ff1bce01e191828b90c5fa468f81197629e32/fractale/agents/base.py) awaits `mcp_client.call_tool` and records a completed event; [`Manager.run_tool`](https://github.com/converged-computing/fractale/blob/b62ff1bce01e191828b90c5fa468f81197629e32/fractale/engines/native/engine.py) synchronously invokes that coroutine, records events and routes returned state transitions. A mature long-running-task design may need async task identity, polling, cancellation and transition semantics, but **no demonstrated defect or correct first-party implementation boundary has yet been established**. The dependency's task protocol is outside the reviewed source.
- Open-PR read-only search found [#15 (version bump)](https://github.com/converged-computing/fractale/pull/15); that does not resolve #10 or prove comprehensive non-overlap. No current `tests/` tree was present at this source SHA; an actual product-code native baseline must be created and exercised before an implementation can be admitted. **No model/provider call may be used to fill that gap.**

| Independent upstream fit gate | Verdict |
| --- | --- |
| First-party need | `PASS` — issue #10 |
| Precise native mechanism | `PENDING` — FastMCP task protocol and first-party ownership boundary unverified |
| Counterfactual measurable benefit | `PENDING` — matched native script not yet designed/run |
| Scope/overlap and regression compatibility | `PENDING` — exact supported behavior and acceptance criteria missing |

**Origin:** `INSUFFICIENT`, not `ASSESSMENT_DERIVED`: Index-first screening alone does not demonstrate that its finding identified this exact issue. **No patch, tests, fork, issue comments, external PR or maintainer contact were performed.** The serial queue must move on; Fractale may be revisited with new source evidence or an explicit targeted decision.
