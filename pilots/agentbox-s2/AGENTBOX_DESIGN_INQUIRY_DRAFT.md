# AgentBox upstream design inquiry — DRAFT, NOT POSTED

**External target:** [madarco/agentbox](https://github.com/madarco/agentbox). **Candidate:** [IMPR-AGENTBOX-S2-OVERLAP-20261020](../../candidates/agentbox-overlap-manager-20261020.md).
**Publication/implementation:** human-owned and **NOT AUTHORIZED BY THIS DOCUMENT**. Recheck first-party default branch, duplicates and [CONTRIBUTING](https://github.com/madarco/agentbox/blob/main/CONTRIBUTING.md) before publication. This is a question about product fit, **not** a feature demand or bug report.

## Suggested issue title

Phase 4 design question: opt-in grouping for overlapping workspace tasks?

## Suggested issue body (copy for human review)

The [workspace/tasks/manager plan](https://github.com/madarco/agentbox/blob/605ee75d63319003c188bc532d4e5b2ba36a51d6/docs/workspaces-tasks-manager-plan.md) describes deciding which tasks can safely run in separate boxes—and preventing boxes from editing overlapping files—as a manual task. The Phase 4 manager brief appears to be the planned place for that decision.

I am exploring a small **opt-in manager planning step** for this workflow rather than a general locking service or a change to task storage. A possible first version would:

- ask for **explicit intended file scopes** (never infer authority from free-text task titles);
- propose putting overlapping tasks in one box or sequencing them, while letting non-overlapping tasks continue independently;
- report unknown scopes or stale plans for human/manager review instead of silently claiming safety.

Before preparing any implementation: **Would this fit the planned Phase 4 direction, or is there a preferred existing mechanism / reason to leave it manual?** If it fits, would you prefer the behavior as manager instructions using the current task/manager API, with no new persisted scope field?

For context, [a source-pinned CLI preflight experiment](https://github.com/opensiro/upstream/blob/main/pilots/agentbox-s2/NATIVE_TASK_PREFLIGHT_BASELINE_RECEIPT_2026-10-20.md) shows that valid tasks with overlapping *descriptions* can be allocated to different boxes. This is **not** a reproduced collision between running workers, nor proof that an automatic scope checker belongs in AgentBox.

I have not opened an implementation PR or changed AgentBox. I would prepare a small native before/after scenario if the scope matches your plans.

## Separate candidate: dependency readiness

A subsequent [native task-store experiment](https://github.com/opensiro/upstream/blob/main/pilots/agentbox-s2/NATIVE_DEPENDENCY_DISPATCH_RECEIPT_2026-10-20.md) showed that task allocation can mark a dependent task `in_progress` while its `dependsOn` predecessor is `todo`. This is **not** a demonstrated prematurely executing worker or necessarily a bug. It is a **different, parked improvement candidate** ([card](../../candidates/agentbox-dependency-readiness-20261020.md)), intentionally **not bundled** into the file-overlap discussion or a proposed first patch. If maintainers later clarify manager dispatch semantics, it can be evaluated separately.

## Boundaries

- The issue body above is for deliberate human review/publication; no issue, fork or PR in AgentBox was created by drafting it.
- Do not claim AgentBox has a product bug merely because an Index assessment did not credit S2 autonomy; no grade change is requested.
- AgentBox requests an issue first for features bigger than bug fixes, and an eventual PR requires the CLA and matching public docs for CLI/API changes.
- A favorable answer is product **design feedback**, not authorization to push an external patch or publish an external PR. Preserve the existing OpenSiro stage permissions.
