# IMPR-AGENTBOX-S2-OVERLAP-20261020 — group potentially conflicting box tasks

**Candidate state:** `BLOCKED_EVIDENCE` (first-party design boundary).
**Origin class:** `ASSESSMENT_DERIVED` **candidate hypothesis**, **not** a demonstrated improved product.
**Owner:** [Upstream #61](https://github.com/opensiro/upstream/issues/61) under [experiment #56](https://github.com/opensiro/upstream/issues/56).
**Target:** [madarco/agentbox](https://github.com/madarco/agentbox), `main@605ee75d63319003c188bc532d4e5b2ba36a51d6` checked 2026-10-20.
**Index:** [canonical Index @5393b698, AgentBox assessment](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ag/agentbox.md), originally assessed `463a6a0a20176147f0b0dbfa8a261aba5e43cbd6`, specifically S2 first-party **manual** avoidance of same-file box conflicts; [Index-first selection receipt](../pilots/agentbox-s2/SCREENING_AND_NATIVE_FIT_2026-10-20.md).

## What is actually wrong / desired

AgentBox's [native manager plan](https://github.com/madarco/agentbox/blob/605ee75d63319003c188bc532d4e5b2ba36a51d6/docs/workspaces-tasks-manager-plan.md) lists deciding how to group tasks touching the same files as **manual**, and places its manager brief in planned Phase 4. Two tasks with descriptions suggesting the same target can be allocated to separate boxes because task assignment checks task identity/workspace, not verifiable file-intent collisions.

**Existing measured baseline:** [internal PR #64](https://github.com/opensiro/upstream/pull/64) executes first-party CLI preflight with a mocked API client: duplicate `src/payments/handler.ts` descriptions admitted to different boxes. This **does not prove** those tasks would actually modify the same file, that running boxes collide, or that the manager is entitled to read/edit their working trees.

## One candidate mechanism and falsifier

**Hypothesis:** a **small, opt-in Phase 4 manager brief** using existing task/manager surfaces could collect *explicit* intended write scopes, warn or group overlapping tasks into one box (or propose serialization), and allow unrelated tasks to run independently. Unknown paths should be reported as unknown, **not** guessed from titles.

**Counterexample / null:** if task scope is unavailable, manager suggestions are ignored, or a pair of isolated worktrees never requires such grouping in a real workflow, the proposal may provide no net benefit. Extra coordination could reduce parallelism or increase human overhead. No automatic global path lock or core task-store behavior change is authorized.

## Four native fit gates

| Gate | Verdict | Reason |
| --- | --- | --- |
| Need | `PASS` for **documented roadmap need only** | First-party plan says manual grouping is a known job, **not approval of this API/design** |
| Mechanism | `PENDING` | Existing task/manager surfaces verified, but exact manager brief/role and write-intent representation require product feedback |
| Counterfactual benefit | `PENDING` | No real AgentBox boxes/agent jobs before/after tested |
| Scope | `PENDING` | Maintainer acceptance, API compatibility and optional behavior unresolved; CONTRIBUTING requests issue first for features |

## Execution, outcome and next gate

- Baseline: `MEASURED_SOURCE_CLI_ONLY`, [receipt](../pilots/agentbox-s2/NATIVE_TASK_PREFLIGHT_BASELINE_RECEIPT_2026-10-20.md).
- Changed product: `NONE`; after: `NOT_TESTED`; benefit: `INCONCLUSIVE`.
- External AgentBox issue / fork / PR / maintainer acceptance: **NONE**. `registry.yaml` remains unchanged.
- **Next owner decision:** first-party design inquiry: is opt-in Phase 4 manager-level grouping desired, or should coordination stay human-driven? [Unpublished external issue draft](../pilots/agentbox-s2/AGENTBOX_DESIGN_INQUIRY_DRAFT.md).
- Research source note: [negative alternatives and fit checkpoint](../pilots/agentbox-s2/NATIVE_FIT_DECISION_AND_ALT_SCREEN_2026-10-20.md).

A positive outcome here would be measured **product-native reduction of incompatible simultaneous work** while preserving disjoint parallel tasks, not an automatic Index S2 upgrade.
