# AgentBox source-native dependency readiness — executed baseline receipt

**Date:** 2026-10-20.
**Owning experiment:** [Upstream #61](https://github.com/opensiro/upstream/issues/61) within [#56](https://github.com/opensiro/upstream/issues/56).
**Internal reviewable PR:** [#65](https://github.com/opensiro/upstream/pull/65).
**Status:** SOURCE-ONLY BASELINE MEASURED; not an AgentBox change, user-facing fix or before/after product improvement.

## Exact provenance

- Canonical [Index AgentBox assessment @5393b698bfdfa4ca14d97a79238234eca20694e5](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ag/agentbox.md), first-party cross-box S2 coordination remains manual at reviewed source `463a6a0a20176147f0b0dbfa8a261aba5e43cbd6`.
- Frozen tested AgentBox actual default source: [`madarco/agentbox@605ee75d63319003c188bc532d4e5b2ba36a51d6`](https://github.com/madarco/agentbox/commit/605ee75d63319003c188bc532d4e5b2ba36a51d6).
- Native product interfaces: [task-store `addTask`, `assignTasks`, `setTaskDone`](https://github.com/madarco/agentbox/blob/605ee75d63319003c188bc532d4e5b2ba36a51d6/packages/relay/src/workspaces/task-store.ts); [CLI `--depends-on` help text](https://github.com/madarco/agentbox/blob/605ee75d63319003c188bc532d4e5b2ba36a51d6/apps/cli/src/commands/tasks.ts) calls the IDs what a task **waits on**. `WorkTask.dependsOn` is persisted natively.
- [Frozen pre-execution protocol](NATIVE_DEPENDENCY_DISPATCH_PROTOCOL_2026-10-20.md) and [native injected test](assessment_native_dependency_dispatch_baseline.test.ts).

## Actually executed in CI

[GitHub Actions #39485210939](https://github.com/opensiro/upstream/actions/runs/39485210939), [job #118843736032](https://github.com/opensiro/upstream/actions/runs/39485210939/job/118843736032): **SUCCESS**.

Ubuntu, Node 22, pnpm 9.15.0, original AgentBox source at exact SHA, immutable checkout with no persisted credentials; exactly one untracked injected relay test file. `pnpm install --frozen-lockfile` completed, native `pnpm build` completed **26/26 tasks**, then the actual `@agentbox/relay` Vitest:

```text
pnpm --filter @agentbox/relay exec vitest run test/zz_opensiro_dependency_dispatch_baseline.test.ts
✓ test/zz_opensiro_dependency_dispatch_baseline.test.ts (1 test)
Test Files  1 passed (1)
Tests       1 passed (1)
```

The real `addWorkspace`, `addTask`, `assignTasks`, `setTaskDone` and `readTasks` operate in an ephemeral test HOME. No mocked HubApiClient, containers, actual box worker processes, AI inference, shell writes into external projects, or external GitHub repo mutation.

## Exact controlled observations

| First-party path | Dependency state | Allocated task state | Result |
| --- | --- | --- | --- |
| Create dependent T-2, then `assignTasks(T-2, boxJobId)` | T-1 remains `todo` | T-2 `in_progress` with job | Accepted: 1 |
| `addTask` of T-3 with `dependsOn:[T-1]` and `boxJobId` | T-1 remains `todo` | T-3 `in_progress` with job | Accepted: 1 |
| Mark T-1 `done`, then assign dependent T-4 | T-1 `done` | T-4 `in_progress` with job | Accepted (positive control): 1 |

Two of two deliberately **unfinished-dependent** allocation paths recorded `in_progress`; task metadata persisted the dependency identity. The completed-dependent positive control also recorded `in_progress`. Thus these native allocation paths do **not differentiate dependency readiness** when changing task status/assignment.

## Evidence interpretation

**Supported:** `DEPENDS_ON_READINESS_NOT_GATED_AT_NATIVE_ALLOCATION` — first-party task store accepts an assigned/in-progress task even if the declared dependency is unfinished. This is more precise than inferring file names from task descriptions.

**Not supported:** that a child coding agent executed prematurely, that AgentBox advertises hard dependency-enforcement semantics at allocation, that user files collided, that a newly proposed manager improvement helps real users, or that a S2 owner/loop appeared. Native task `in_progress` reflects assignment and may not imply actual execution. Task `dependsOn` may intentionally be advisory, with a future manager responsible for scheduling.

**Classification boundary:** AgentBox was Index-first selected for **the documented cross-box coordination gap**, but the exact `dependsOn` readiness observation arose through deeper first-party source investigation. This receipt is a **secondary native finding**, not standalone proof that the canonical assessment diagnosed a dependency status bug. Do not retrospectively claim the assessment named this exact defect.

## Native-fit decision

- Assessment-origin area: **SUPPORTED**.
- Product need for avoiding cross-box conflicts: **PASS_ROADMAP** from the first-party Phase 4 manager plan.
- Product requirement of hard dependency gating at `addTask/assignTasks`: **PENDING**, potentially intentional advisory semantics.
- Minimal acceptable intervention location (manager brief vs task-store vs CLI), compatibility of assigning tasks before execution, and maintainer acceptance: **PENDING**.
- Source-native before/after improvement: **NOT EXECUTED**, no upstream patch or deployed gain.
- External AgentBox feature/bug issue, fork, PR, maintainer feedback: **NONE**.

Ask maintainer: is `dependsOn` an **advisory planning relation** for the prospective Phase 4 manager, or is allocating an `in_progress` task while dependencies are still `todo` undesirable today? Do not impose a hard source-level rejection without that answer; doing so might break legitimate preassignment. Either way, use the outcome to choose a minimal manager-owned, opt-in coordination solution or return `BLOCKED_EVIDENCE`.

No Zot revival, no AgentBox repo changes, no Index regrade, no fourth Organization S1 admission. The existing [unpublished design inquiry](AGENTBOX_DESIGN_INQUIRY_DRAFT.md) remains human-owned.
