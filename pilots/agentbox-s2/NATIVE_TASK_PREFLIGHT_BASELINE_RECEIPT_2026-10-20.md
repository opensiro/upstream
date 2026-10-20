# AgentBox Phase 4 task-identity preflight — executed source-native receipt

**Date:** 2026-10-20. **Owning pilot:** [OpenSiro Upstream #61](https://github.com/opensiro/upstream/issues/61) under [#56](https://github.com/opensiro/upstream/issues/56). **Research PR:** [#64](https://github.com/opensiro/upstream/pull/64). **Classification:** `ASSESSMENT_DERIVED_CANDIDATE / NATIVE_BASELINE_CONFIRMED / IMPLEMENTATION_NOT_ADMITTED`.

## Authoritative origin and pinned source

- Canonical Index `main@5393b698bfdfa4ca14d97a79238234eca20694e5`: [included AgentBox assessment](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ag/agentbox.md), assessed ref `463a6a0a20176147f0b0dbfa8a261aba5e43cbd6`, finding: **avoiding conflicting concurrent box edits remains manual**, and Phase 4 manager conflict grouping lacks first-party operational closure.
- Fresh [AgentBox `main@605ee75d63319003c188bc532d4e5b2ba36a51d6`](https://github.com/madarco/agentbox/commit/605ee75d63319003c188bc532d4e5b2ba36a51d6): same explicit gap in first-party [manager plan](https://github.com/madarco/agentbox/blob/605ee75d63319003c188bc532d4e5b2ba36a51d6/docs/workspaces-tasks-manager-plan.md); existing native `WorkTask` schema with `description/dependsOn/boxId` but without authoritative intended-write paths; native `preflightTaskAssignment` checks task identity/workspace before provisioning and `assignTasksBestEffort` assigns afterward.

## Actual execution

[GitHub Actions #39483148398](https://github.com/opensiro/upstream/actions/runs/39483148398/job/118836633332) **SUCCESS**. Immutable public AgentBox source in disposable GitHub Ubuntu runner, Node 22, pnpm 9.15.0, `pnpm install --frozen-lockfile` PASS, `pnpm build` PASS (26/26 native build tasks), injected single research [Vitest](assessment_native_task_conflict_baseline.test.ts) **PASS: 1 test in 1 file**, no Docker, real coding agents, model calls or provider credentials. Original AgentBox repository, branches and PRs untouched; CI uses read-only repository permissions with no persisted checkout credentials.

### Synthetic task assignment workload

- `T-1`: task description names `src/payments/handler.ts` → proposed `box-A`.
- `T-2`: task description names the same `src/payments/handler.ts` → proposed separate `box-B`.
- `T-3`: description names `docs/README.md` → proposed separate `box-C`.

A mock HubApiClient returns only valid task IDs/current workspace and records assignments. **Real exported AgentBox CLI functions** are called for each task. The observed application logs included:

```text
tasks assigned: T-1
tasks assigned: T-2
tasks assigned: T-3
Test Files  1 passed (1)
Tests       1 passed (1)
```

| Measured observable | Result | Important qualification |
| --- | --- | --- |
| Upstream native toolchain build | 26/26 tasks PASS | This is a build, not a Phase 4 product acceptance test |
| Task identity preflight for all three valid IDs | 3/3 succeed | Overlap intent exists **only in task descriptions**, not verified paths |
| Separate intended box assignments | Three accepted calls (`A`, `B`, `C`) | In-memory stub, **no actual box created** |
| Conflict-specific refusal / rescope | None by this CLI preflight | Does not prove other manager/backends can never catch conflicts |
| Real conflicting file edits | **Not performed** | No actual cross-box overwrite, losses or baseline frequency measured |

## Causal limitation and stage gate

The Index finding predicted that the system already has operations and work assignment but lacks a shipped file-conflict-specific regulator at this level. The pinned live first-party plan and source establish the boundary, and the executed CLI test confirms the specific predispatch surface **does not compare proposed mutable file scopes**. This is a narrow **native implementation baseline**, not demonstrated overall AgentBox hazard frequency.

Improving this surface may require adding trustworthy file-intent scopes, changing the Phase 4 manager brief, or giving the manager an explicit `NEEDS_SCOPE_REVIEW` result; blindly inferring paths from natural-language descriptions would not be safe. The first-party roadmap supports the product **problem**, but not an arbitrary implementation. [AgentBox CONTRIBUTING](https://github.com/madarco/agentbox/blob/605ee75d63319003c188bc532d4e5b2ba36a51d6/CONTRIBUTING.md) asks for a **new design issue before changes larger than bug fixes**, and acceptance/CLA remain first-party/human-controlled.

**Verdict:** `BASELINE_BEHAVIOR_CONFIRMED`; `NATIVE_NEED=PASS_ROADMAP`; `MECHANISM/EXTERNAL_DESIGN=BLOCKED_FEEDBACK`; `AFTER_EFFECT=NOT_MEASURED`; `NO_EXTERNAL_PR`. Do **not** score an improved S2 ownership state. [Human-owned design inquiry draft](AGENTBOX_DESIGN_INQUIRY_DRAFT.md) remains unpublished, and there is no external AgentBox fork mutation or issue.
