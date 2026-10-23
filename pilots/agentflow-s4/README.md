# AgentFlow S4 — opt-in rollback of failed graph-optimizer revisions

**Status:** `SOURCE_PREPARED / INTERNAL_DRAFT`. External AgentFlow fork, branch, issue and PR: **NONE**. This is a source-native technical prototype, not a completed strict Upstream #56 contribution.

## Origin and fit

- **Index first:** [included AgentFlow assessment](https://github.com/opensiro/vsm-harness-index/blob/114dd45cbe462a4a5ae2a85d02c60d1e15b16a77/assessments/ag/agentflow.md), first-party assessed source `eb51a2e7a5c7d65da5718c4a41843098b60c80e0`. The observed **S4=A** path revises a pipeline after a run; its acceptance currently checks *load/schema validity*, not observed improvement. This is a concrete **positive S4 mechanism with a documented acceptance weakness**, not a missing-grade repair.
- **Selection origin:** `ASSESSMENT_DERIVED` *hypothesis*. The assessment finding was inspected before selecting this intervention; first-party code and [README's Graph Optimization Rounds](https://github.com/agentenv/agentflow/blob/eb51a2e7a5c7d65da5718c4a41843098b60c80e0/README.md) independently confirm the mechanism and warn that a structurally accepted graph need not improve results. This does **not** mean the maintainer has requested this precise policy.
- **First-party baseline:** [agentenv/agentflow `master@eb51a2e7`](https://github.com/agentenv/agentflow/commit/eb51a2e7a5c7d65da5718c4a41843098b60c80e0). Root `LICENSE`: **MIT**. No root `CONTRIBUTING.md` or `.github/` contributor policy in the pinned tree; re-check before any external write. Existing first-party open PRs inspected, including [#28](https://github.com/agentenv/agentflow/pull/28) (child-pipeline loading timeout, **not** this runtime rollback). No identified open/closed exact PR duplicate.
- **Scope:** optional `rollback_on_failed_optimization=True` on `Graph` / `PipelineSpec`. Default behavior unchanged. After an actual optimized *child run* fails and a prior successful child exists, retain the failed child receipt but select/restore the last successful graph/output and use it in remaining rounds. The optimizer cannot turn off the user's original opt-in guard by editing generated graph data. Cancellations are not promoted to success.

## First-party native scripted effect (no model/provider call)

The scripted optimizer edits generated `pipeline.py` to replace a successful `plan` task with a valid-schema but failing `fail_always` task, executed by the first-party `Orchestrator` and `MockAdapter` subprocess runner.

| Same two-round fixture | Original source / default semantics | Patched opt-in |
| --- | --- | --- |
| Round 1: original graph | `COMPLETED` | `COMPLETED` |
| Round 2: valid edited graph | `FAILED` | `FAILED`, receipt preserved |
| Parent selected graph | Failing revision | Previous successful graph |
| Parent final status | `FAILED` | `COMPLETED` (recovery explicitly recorded) |
| Next round (3-round control) | Not part of two-round fixture | Restored successful graph reruns |

**Actual test observations (2026-10-23):**
- Pristine original checkout with an added deterministic fixture asserting the failure: **1 PASS** (observed original behavior, no new feature).
- New opt-in test against unmodified original source: `rollback_on_failed_optimization` is rejected by `PipelineSpec` (`extra_forbidden`) — expected RED for absent capability.
- Patched graph optimizer + DSL + loader regression suites: **42 PASS / 0 FAIL**.
- `git diff --check` and `compileall`: **PASS**.
- Full general suite **not certified**. A broader orchestrator run timed out in an unrelated inference-startup test; that same test also timed out on a separate pristine original checkout. Do not count that as an implementation regression or as a full-suite pass.

## Reproduce

1. Check out the exact first-party commit above and install its `.[dev]` dependencies in an isolated Python environment.
2. Apply [the five-file patch](rollback-on-failed-optimization.patch): `git apply --check rollback-on-failed-optimization.patch` then `git apply rollback-on-failed-optimization.patch`.
3. Run `python -m pytest -q tests/test_graph_optimizer.py tests/test_dsl.py tests/test_loader.py`. All tests use first-party Python/native process mechanisms with fixed actions. No live LLM inference.

## Limits and next gate

This only guards **observed execution failure** of an optimized revision; a completed graph may still have worse correctness, quality, cost or latency. It is neither a general counterfactual evaluator nor proof of user benefit, maintainer fit, security, grade change or external upstream adoption.

Prior to external publication: independent product fit/intent and scope acceptance (the default remains unchanged), policy/license refresh, reviewer tests/CI, then a **separately owned Improvement publication decision**. The existing 34-case Corrective S5 mandate does not apply.
