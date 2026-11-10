# AgentBox Phase 4 — ready-to-post native design issue (unpublished)

**Target:** [madarco/agentbox](https://github.com/madarco/agentbox). Its [CONTRIBUTING.md](https://github.com/madarco/agentbox/blob/main/CONTRIBUTING.md) asks for an issue before changes larger than a bugfix. This is a prepared **human-owned issue body**, not published upstream or an implementation branch in AgentBox.

## Suggested title

Phase 4 manager brief: opt-in overlap-aware task grouping with explicit write scopes

## Suggested issue body

The [Workspaces, Tasks and Manager plan](https://github.com/madarco/agentbox/blob/main/docs/workspaces-tasks-manager-plan.md) explicitly treats avoiding simultaneous edits to the same files as manual today, and the Phase 4 manager brief remains planned.

I've explored a **minimal, opt-in advisory** using the current task list and explicit intended write scopes supplied by the operator/manager rather than guessed from natural-language titles. It produces grouping suggestions before parallel box dispatch: two tasks targeting the same file or directory should be grouped or explicitly reviewed; a disjoint docs task should remain independently parallel; unknown scopes or unfinished dependencies should not be treated as safe dispatch.

This deliberately **does not** change `addTask/assignTasks`, task state/permissions, sandbox provisioning, worker ownership or default manager behavior, and never treats inferred lexical paths as a security/OS file lock. Stale workspace state and actual file path identity require a stronger contract before any automation.

An [OpenSiro source-pinned, read-only research pilot](https://github.com/opensiro/upstream/pull/72) demonstrates the limited advisor with real AgentBox TypeScript/Vitest and compares it with the existing task preflight. It does **not** show a real box collision or production benefit. The source-only baseline is independently [recorded here](https://github.com/opensiro/upstream/pull/64). None of this has been submitted as product changes to AgentBox.

Would a standalone opt-in manager planning brief using current task APIs (no persistent write-scope schema and no hard task-store gating) fit your Phase 4 direction? If not, which existing manager entry point or instruction format is preferred? I'd keep implementation confined to whichever interface is useful and validate it on overlapping and disjoint tasks before proposing a code PR.

## Rules of engagement

The operator controls posting this first-party issue and any external PR. Do not use this proposal to claim S2 autonomy, full conflict prevention, successful user benefit, AgentBox maintainer acceptance, or a new Index assessment. Do not open a GitHub PR until a contributor fork/writable branch is specifically authorized by the existing OpenSiro stage process. If the issue is rejected, retain a negative result; do not force implementation.

**Evidence:** [Index AgentBox S2 assessment](https://github.com/opensiro/vsm-harness-index/blob/main/assessments/ag/agentbox.md); [OpenSiro #61](https://github.com/opensiro/upstream/issues/61); [prototype PR #72](https://github.com/opensiro/upstream/pull/72).
