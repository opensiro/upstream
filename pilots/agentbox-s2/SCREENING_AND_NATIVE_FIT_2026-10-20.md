# AgentBox S2 — Index-derived first-party roadmap candidate

**Screened:** 2026-10-20. **Owning work:** [Upstream #61](https://github.com/opensiro/upstream/issues/61), within [assessment-to-improvement #56](https://github.com/opensiro/upstream/issues/56).

**Gate decision: `SELECT_FOR_DESIGN_INQUIRY / NOT_ADMITTED_FOR_IMPLEMENTATION`.** There is stronger **first-party documented product need** than Zot, but no approved intervention design, baseline or real before/after yet. No external issue, fork, PR or code change to AgentBox was made.

## 1. Independent Index-first origin

- Canonical Index `main@5393b698bfdfa4ca14d97a79238234eca20694e5`: [AgentBox included assessment](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ag/agentbox.md).
- Assessment published 2026-09-17, assessed AgentBox `463a6a0a20176147f0b0dbfa8a261aba5e43cbd6`. S1 `A`, S2 `—`, S3 `—`: **the finding, not the score, is controlling**. The system offers separate autonomous coding-agent boxes, workspace/task storage and manager sessions, but prevents file-overlap interference manually. It does **not** show an operating conflict-specific S2 loop returning work coordination to the agents.
- Zot's previously reproduced collisions remain a separately selected experiment. AgentBox was included in the original [five-case Index screening](../zot-shared-workspace/SCREENING_2026-10-20.md) **before** this updated native inspection, not selected by scanning GitHub issues and assigning VSM scores afterward.

## 2. Fresh AgentBox source and the actual functional gap

Current upstream `madarco/agentbox main@605ee75d63319003c188bc532d4e5b2ba36a51d6`, active source/policy checked on 2026-10-20:

- [First-party Workspaces/Tasks/Manager plan](https://github.com/madarco/agentbox/blob/605ee75d63319003c188bc532d4e5b2ba36a51d6/docs/workspaces-tasks-manager-plan.md) says, in its **Context**, that deciding which boxes do which work and making sure they don't fight over the same files remains manual. It proposes a local manager that groups overlapping tasks in one box and watches PRs. Status table still marks **Phase 4 — manager's brief** as `planned`; known gaps say the manager starts as a plain agent with `AGENTBOX_WORKSPACE`, and file-overlap grouping and box-merged follow-ups remain unspecified.
- [`packages/relay/src/workspaces/types.ts`](https://github.com/madarco/agentbox/blob/605ee75d63319003c188bc532d4e5b2ba36a51d6/packages/relay/src/workspaces/types.ts): native `WorkTask` has `title`, optional `description`, `dependsOn`, `projectId`, `boxId/boxJobId`, `managerId`. **No first-party authoritative proposed-write-file list** exists on the task record. Task title/description text **cannot be treated as a verified path claim**.
- [`apps/cli/src/lib/tasks-assign.ts`](https://github.com/madarco/agentbox/blob/605ee75d63319003c188bc532d4e5b2ba36a51d6/apps/cli/src/lib/tasks-assign.ts): `preflightTaskAssignment` validates tasks and workspace ownership before provisioning; `assignTasksBestEffort` assigns after creation. Neither resolves intended write-scope overlaps.
- [`apps/cli/src/commands/manager.ts`](https://github.com/madarco/agentbox/blob/605ee75d63319003c188bc532d4e5b2ba36a51d6/apps/cli/src/commands/manager.ts) and [relay manager](https://github.com/madarco/agentbox/blob/605ee75d63319003c188bc532d4e5b2ba36a51d6/packages/relay/src/workspaces/manager.ts): manager/session lifecycle and communication surfaces exist. These do not by themselves imply the Phase 4 conflict grouping decisions are shipped.

The desired product benefit originates in AgentBox's **own roadmap**, not a demand to raise S2 from `—` to `A`. Avoid silently changing permissions, workspaces, session ownership, or creating autonomous managers without an accepted scope.

## 3. Falsifiable native candidate

Hypothesis: an **optional conflict-aware manager plan** can refuse or regroup overlapping independent work *before* launching separate boxes while preserving independent parallel tasks and returning an actionable explanation to the manager/worker.

Concrete bounded protocol proposed for maintainer design feedback (not implemented):

1. Read current workspace tasks + dependencies and intended paths, gathered from **explicit user/manager planning evidence**, not guessed from task title as if it were authoritative.
2. Two tasks with overlapping intended mutable paths (e.g. `src/payments/**`) must be grouped into one box, serialized as dependent work, or escalated for human decision **before conflicting parallel dispatch**. Unknown paths are `NEEDS_SCOPE_REVIEW`, not safe independent work.
3. A disjoint docs task can run alongside the grouped/serial payments work.
4. On changed task assignments, dependency updates, path-content disagreement or a stale task snapshot, re-read authoritative current task state before committing a new assignment/box. Return specific overlap+owners to affected workers/manager.
5. Keep a reversible, opt-in path, existing human approval and default manager/box operation, and all host/provisioner safety constraints.

This is a **design question**. The actual owner may prefer a manager instruction/brief with manual oversight rather than adding schema fields or a global lock.

### Proposed matched acceptance scenarios

| Scenario | Before / native behavior to capture | After criterion *if approved* |
| --- | --- | --- |
| Two independent tasks target `src/payments/**` | Current Task records/CLI assignment alone have no verified file-overlap refusal | Must not dispatch to two conflicting writable boxes without explicit rescope/group/approval |
| Task on `docs/**` is disjoint | Native task assignment accepts valid IDs, not a file-conflict proof | Preserve parallelism without introducing a global manager bottleneck |
| Path scope absent or ambiguous | Native `WorkTask` has no authoritative paths | Return `NEEDS_SCOPE_REVIEW` (no implied safe independence) |
| `dependsOn` chain pending | Task dependencies already exist as data | Do not violate dependency order; actionable feedback and unchanged valid histories |
| Work status or intended scope changes after planning | Source-backed tasks/assignments can change | Fail safely on stale plan; re-plan/return corrections rather than silently dispatch |
| Rollback/cancel/resume | Existing box/manager lifecycle exists | New coordination must not strand unrelated tasks, override human choices or change host boundaries |

Before/after must execute against a **single pinned native AgentBox source** under official Node 22 + pnpm tests; observations, sample sizes, failures and counterfactual human effort must be recorded, not expected metrics portrayed as results. Running normal tests alone would prove engineering checks, **not product improvement**. No baseline or after-case has been run for this AgentBox candidate at this stage.

## 4. Explicit native-fit gates and stop rule

| Gate | Status | Evidence |
| --- | --- | --- |
| Assessment-derived origin | `PASS` | Included pinned assessment identified the specific still-manual S2 cross-box write-interference gap |
| Product-native need | `PASS_ROADMAP` | **Same first-party AgentBox plan**, Phase 4 planned; no independent user acceptance of the *proposed scope mechanism* yet |
| Scope/mechanism | `PENDING` | `WorkTask` lacks scope provenance, CLI checks identity but not overlapping edits; manager brief approach must be agreed |
| Counterfactual value | `PENDING` | No measured baseline or after behavior; against existing manual grouping / Git worktrees |
| Maintainer compatibility | `PENDING` | [AgentBox CONTRIBUTING](https://github.com/madarco/agentbox/blob/605ee75d63319003c188bc532d4e5b2ba36a51d6/CONTRIBUTING.md): **open an upstream issue before anything larger than a bug fix**. Contributor license agreement before merge; docs updates with behavioral change |

Do **not** implement an external feature or create a contributor fork branch without a reviewed solution envelope and existing Control Plane authorization. Proposal wording is available in [the unpublished maintainer design draft](AGENTBOX_DESIGN_INQUIRY_DRAFT.md). External publication remains human-owned.

### Overlap/deduplication

- [AgentBox issue #401](https://github.com/madarco/agentbox/issues/401) has a direct open [PR #402](https://github.com/madarco/agentbox/pull/402) to sync the second agent's host config. Not the S2 conflict-grouping improvement; do not duplicate.
- [Issue #407](https://github.com/madarco/agentbox/issues/407): first-party reproducible orphan/zombie process bug, genuine product reliability. **Not derived** from this assessment's file-conflict mechanism. Would be `ASSESSMENT_INFORMED`/general if selected for engineering work.
- [Issue #405](https://github.com/madarco/agentbox/issues/405): request for network egress controls, not the same S2 operating loop.

## 5. Zot candidate disposition

[Zot actual native writer/turn-boundary evidence](../zot-shared-workspace/NATIVE_TOOL_TURN_BOUNDARY_RECEIPT_2026-10-20.md) demonstrates the earlier voluntary prototype does not intercept actual edits or release at end of logical tasks. Zot intentionally chooses shared writable cwd and currently has no competing maintainer request/design evidence for first-party overlap regulation. Thus `HOLD_UNTIL_NATIVE_NEED` for **upstream implementation**; its experimental `1/2 → 2/2` remains a bounded synthetic mechanism result, **not a product-improvement claim**. No new Zot code, issue or fork.

**Cross-project decision:** AgentBox is the stronger *native-product-plan* route within #56, not an admitted intervention or a predicted PR acceptance. No Index assessment grade was altered.
