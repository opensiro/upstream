# AgentBox dependency-before-dispatch — frozen source-native baseline protocol

**Research owner:** [Upstream #61](https://github.com/opensiro/upstream/issues/61) inside [assessment-driven #56](https://github.com/opensiro/upstream/issues/56).
**Status:** PRE-EXECUTION; hypotheses only, not yet observed.
**Origin:** canonical [Index AgentBox assessment @5393b698bfdfa4ca14d97a79238234eca20694e5](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ag/agentbox.md), which identifies manually closed cross-box coordination.
**Source pin:** [madarco/agentbox@605ee75d63319003c188bc532d4e5b2ba36a51d6](https://github.com/madarco/agentbox/commit/605ee75d63319003c188bc532d4e5b2ba36a51d6). Same source as [initial CLI task-assignment baseline](NATIVE_TASK_PREFLIGHT_BASELINE_RECEIPT_2026-10-20.md).

## Why this is different from a made-up scope policy

First-party [Task CLI](https://github.com/madarco/agentbox/blob/605ee75d63319003c188bc532d4e5b2ba36a51d6/apps/cli/src/commands/tasks.ts) exposes `--depends-on <ids>` as task IDs the task **waits on**. The canonical [WorkTask](https://github.com/madarco/agentbox/blob/605ee75d63319003c188bc532d4e5b2ba36a51d6/packages/relay/src/workspaces/types.ts) records `dependsOn`, `status`, and assigned box/job. The actual [task-store](https://github.com/madarco/agentbox/blob/605ee75d63319003c188bc532d4e5b2ba36a51d6/packages/relay/src/workspaces/task-store.ts) validates dependency IDs at create/patch, but current `assignTasks` and `addTask` when supplied `boxJobId` appear to enter `in_progress` without checking whether dependency tasks are `done`.

This is an exact source-backed control-path hypothesis about first-party metadata, **not** a conclusion that running agents violated a promised scheduler contract. Product may intentionally treat dependencies as advisory. An unapproved manager rewrite or file-path inference is out of scope.

## Falsifiable deterministic tests (native relay task store)

Use the real `@agentbox/relay` task store, real `addWorkspace`, `addTask`, `assignTasks`, `setTaskDone` and `readTasks` in ephemeral `HOME` (same cleanup/helper as native `task-store.test.ts`). No mocked HubApiClient, Docker containers, external model or GitHub write.

1. Create T-1 as `todo`, T-2 with `dependsOn:[T-1]` as `todo`. Assign T-2 to distinct new job while T-1 remains `todo`. Expected source-state: T-2 `in_progress` and assigned, T-1 still `todo`. This is **potential premature dispatch metadata**, not proof agent code executed.
2. Create T-3 with `dependsOn:[T-1]` **and** `boxJobId` in one initial API path while T-1 is unfinished. Expected: T-3 directly `in_progress`.
3. Mark T-1 `done` and assign T-4 with the same finished dependency; expect `in_progress` (positive control). Confirm task ids/statuses/dependencies preserved and the result is independent of description/path guessing.

**Metrics:** 2 intentionally unfinished-dependent allocation paths, count accepted and marked `in_progress`; 1 finished-dependent positive control. No performance claim or actual worker count.

## Readout and next native-fit gate

- If unfinished-dependent task paths enter `in_progress`, record `SOURCE_NATIVE_DEPENDENCY_READINESS_NOT_GATED`, and ask maintainers whether `dependsOn` is advisory scheduling metadata or a hard no-dispatch contract; **do not automatically label it a bug**. Compare optional manager instruction/readiness check versus storage/API rejection; current design feedback remains pending.
- If no such behavior occurs, record falsification; do not manufacture a new feature.
- A genuine before/after product improvement requires a separately accepted behavior expectation and matched execution against a bounded source change. This source-only research **is not that after-case**.
- Frozen evidence must include actual Vitest logs, full pinned build, test status, source SHA, and limits. Existing issue-first/CLA and external publication rules apply. No changes to AgentBox, Index VSM grades or Organizational S1 admission.
