# AgentBox S2 — native CLI task preflight baseline

**Experimental source-only baseline; do not treat the expected result as measured until a GitHub Actions run passes.** Owning [Upstream #61](https://github.com/opensiro/upstream/issues/61), within [#56](https://github.com/opensiro/upstream/issues/56).

## Evidence selection

First-party [AgentBox manager plan](https://github.com/madarco/agentbox/blob/605ee75d63319003c188bc532d4e5b2ba36a51d6/docs/workspaces-tasks-manager-plan.md) declares avoiding file conflicts among boxes a currently **manual** responsibility and lists the manager brief Phase 4 as **planned**. This directly corroborates [the Index S2 finding](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ag/agentbox.md).

**Pinned executable source:** AgentBox `main@605ee75d63319003c188bc532d4e5b2ba36a51d6`. Actual `apps/cli/src/lib/tasks-assign.ts` checks workspace and task existence at preflight and separately assigns after creation; the task `WorkTask` schema has no authoritative intended-write-path scope. Source-only test [`assessment_native_task_conflict_baseline.test.ts`](assessment_native_task_conflict_baseline.test.ts) uses those genuine exported CLI functions with an in-memory stub of the hub interface; **no boxes, Docker, model API, network service, real filesystem change or credentials**.

## Reproducible synthetic setup

Three existing tasks in a synthetic workspace:

- `T-1`: title/description says edit `src/payments/handler.ts`
- `T-2`: title/description says edit `src/payments/handler.ts`
- `T-3`: separate `docs/README.md` task

Preflight `T-1` for `box-A`, `T-2` for `box-B`, `T-3` for `box-C`. These are descriptive intents, **not verified write sets**. The test expects the current code to accept all valid task IDs and record all three requested assignments. This shows that the **current specific CLI preflight** is not an inter-task write-conflict admission gate; it does not demonstrate that actual boxes were created, a collision occurred, or that AgentBox guarantees conflict prevention elsewhere.

The [read-only workflow](../../.github/workflows/agentbox-task-conflict-baseline.yml) checks out the immutable public AgentBox commit into an ephemeral GitHub Actions runner, copies one test file into `apps/cli/test/`, executes Node 22, pnpm 9.15.0 `pnpm install --frozen-lockfile` and the upstream `pnpm build`, then runs actual `@madarco/agentbox` Vitest. Only one untracked fixture is injected; no public GitHub files or upstream branch modified.

## What a valid subsequent improvement would test

**Conditional on first-party design feedback/Phase 4 agreement**, any new manager planning capability must distinguish a real S2 benefit: grouping/serializing conflicting payment tasks (or presenting an explicit `NEEDS_SCOPE_REVIEW` decision), allowing docs work concurrently, preserving `dependsOn` and human assignments, and returning overlap feedback to affected S1 workers. It must not infer guaranteed paths from titles, or silently claim full write enforcement. Use a matched pre/post native task protocol, record any rejected tasks, operator burden and unchanged behavior outside the optional mode. The provenance, interface, rollback, CLA and external PR gates remain as in [candidate selection](SCREENING_AND_NATIVE_FIT_2026-10-20.md).

**Stop rule:** green baseline is evidence of an existing intentional/manual decision boundary, not a bug fix, product-benefit result, or an automatic permit to change AgentBox. External [CONTRIBUTING](https://github.com/madarco/agentbox/blob/605ee75d63319003c188bc532d4e5b2ba36a51d6/CONTRIBUTING.md) calls for **an issue first** on changes larger than bugs; unpublished [design inquiry](AGENTBOX_DESIGN_INQUIRY_DRAFT.md) remains human-owned.
