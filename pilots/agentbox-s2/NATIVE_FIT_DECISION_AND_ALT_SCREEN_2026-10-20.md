# Upstream #56 — AgentBox S2 decision point and bounded new Index-first screen

**Date:** 2026-10-20. **Owner:** [Upstream #56](https://github.com/opensiro/upstream/issues/56) / [AgentBox #61](https://github.com/opensiro/upstream/issues/61).
**Status:** `BLOCKED_NATIVE_DESIGN_FEEDBACK` for product modification, `SOURCE_SCREEN_ONLY` for alternates. **Do not count this note as a product improvement.**

## Frozen authorities and selection order

- [Canonical Index@5393b698bfdfa4ca14d97a79238234eca20694e5](https://github.com/opensiro/vsm-harness-index/commit/5393b698bfdfa4ca14d97a79238234eca20694e5) was verified directly against the current default branch. The Index assessments were consulted **before** evaluating the new public projects.
- [AgentBox assessment](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ag/agentbox.md), assessed ref `463a6a0a20176147f0b0dbfa8a261aba5e43cbd6`, specifically describes manual cross-box collision avoidance and a planned manager brief.
- Live [AgentBox main@605ee75d63319003c188bc532d4e5b2ba36a51d6](https://github.com/madarco/agentbox/commit/605ee75d63319003c188bc532d4e5b2ba36a51d6) still names Phase 4 manager's brief as **planned** in [its first-party plan](https://github.com/madarco/agentbox/blob/605ee75d63319003c188bc532d4e5b2ba36a51d6/docs/workspaces-tasks-manager-plan.md); contributors are asked to open an issue before implementing features larger than bug fixes.
- This update checked a locally cloned **exact Index HEAD** (678 markdown files under `assessments/`) and screened a bounded S2 subset with described interference, not a fabricated exhaustive ranking.

## Existing AgentBox evidence vs. a real improvement

| Dimension | State | Supporting evidence / limitation |
| --- | --- | --- |
| Index first / function-to-mechanism | `PASS` at coordination *area* | Assessment names remaining manual inter-box collision control, but **does not** explicitly diagnose a specific `dependsOn` bug |
| First-party product need | `PASS_ROADMAP` | Native Phase 4 manager description groups same-file tasks, still planned |
| Source-native CLI baseline | `OBSERVED` | [PR #64](https://github.com/opensiro/upstream/pull/64): two task descriptions suggesting same file independently assigned; no real boxes or verified write sets |
| Source-native task-store baseline | `OBSERVED` | [PR #65](https://github.com/opensiro/upstream/pull/65) / [receipt](NATIVE_DEPENDENCY_DISPATCH_RECEIPT_2026-10-20.md): **2/2** unfinished-dependent assignment paths enter `in_progress` (native task-store), positive control after predecessor completion; not evidence of actual premature execution |
| Desired improvement / acceptance | `BLOCKED_FEEDBACK` | Whether `dependsOn` is advisory metadata vs a scheduling constraint; no agreed first-party manager brief/API boundary |
| AgentBox intervention / matched after / shipped effect | `NOT_STARTED` | No product diff, no actual worker/box run, no real file conflict, no measured before/after user benefit |
| External publication / maintainer opinion | `NOT_STARTED` | No AgentBox issue, fork, PR, or maintainer feedback. [Unpublished inquiry](AGENTBOX_DESIGN_INQUIRY_DRAFT.md) remains human-owned |

**Important fit observation:** native [`WorkTask`](https://github.com/madarco/agentbox/blob/605ee75d63319003c188bc532d4e5b2ba36a51d6/packages/relay/src/workspaces/types.ts) intentionally supports many tasks in one box. [`assignTasks`](https://github.com/madarco/agentbox/blob/605ee75d63319003c188bc532d4e5b2ba36a51d6/packages/relay/src/workspaces/task-store.ts) records allocation (and sets `in_progress`); it is not an authenticated write-scope admission or a proof that an agent has started. Hard rejection of unfinished dependencies at storage level could break useful preassignment. Do **not** ship this behavior change without first-party input.

**Minimal question to maintainer if authorized to publish:** would the Phase 4 manager brief use existing `agentbox tasks` and manager messaging to *advise/group/defer* independent box dispatch based on explicit file intent and pending `dependsOn`, without changing the default task-store allocation semantics? Which bounded acceptance criterion would the maintainer want tested?

## Fresh bounded alternatives — current Index → independent upstream check

| Candidate | Canonical assessed source | Current default source | Product-fit disposition |
| --- | --- | --- | --- |
| [Claw Code](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/cl/claw-code.md) | `08106b0c3771ef5b4a5aa176acccd460e88b7325`; S2: detector `detect_branch_lock_collisions` not wired into operational attenuation | [ultraworkers/claw-code@22fe36072a37cb1c489589f2e98ff3dd5357bb5a](https://github.com/ultraworkers/claw-code/commit/22fe36072a37cb1c489589f2e98ff3dd5357bb5a); detector still exported with no additional use found in current code search. [First-party README](https://github.com/ultraworkers/claw-code/blob/22fe36072a37cb1c489589f2e98ff3dd5357bb5a/README.md) explicitly calls this an agent-managed *museum exhibit*, directing genuine usage to other projects; [coordination issue #3153](https://github.com/ultraworkers/claw-code/issues/3153) **CLOSED**, [related PR #3250](https://github.com/ultraworkers/claw-code/pull/3250) closed **unmerged** | `NO_GO_PRODUCT_PRIORITY`: detector is real, but repo disclaims its suitability as main production agent product. No new patch justified just to wire S2 |
| [KairoCode](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ka/kairocode.md) | `018c74035de1354f69a92eda626ddbb210fbebcc`; S2 without verified integration conflict-return loop | [yangf-Veda/KairoCode@018c74035de1354f69a92eda626ddbb210fbebcc](https://github.com/yangf-Veda/KairoCode/commit/018c74035de1354f69a92eda626ddbb210fbebcc); [README](https://github.com/yangf-Veda/KairoCode/blob/main/README.md) calls it a runnable *prototype*, not production code execution sandbox. Task dependencies and isolated worktrees already exist | `NO_GO_FOR_CURRENT_PRODUCT_CLAIM`: no first-party demand or measured remaining conflict; grade absence alone insufficient |
| [AtomCode](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/at/atomcode.md) | `152b2cc132dda9b177c3a030e21cfacd95494ea3`; S2 lacks a returned inter-worker interference decision | [karlorz/atomcode@152b2cc132dda9b177c3a030e21cfacd95494ea3](https://github.com/karlorz/atomcode/commit/152b2cc132dda9b177c3a030e21cfacd95494ea3); parallel work already partitioned by file and concurrency capped | `BLOCKED_EVIDENCE`: no independently proven collision scenario or maintainer need for new arbiter |
| [Dendrophis](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/de/dendrophis.md) | `dbc8e7883e7473f9450865d511d91e30c58724e2`; `modifies_files` metadata, but standard subagent path sequential | [sp1d3rx/dendrophis@b448c795d601f5c4a63f6cb4d503bd263b48a9f1](https://github.com/sp1d3rx/dendrophis/commit/b448c795d601f5c4a63f6cb4d503bd263b48a9f1); new source not evaluated for a distinct live parallel S1 path | `NO_CANDIDATE_YET`: assessment does not establish actual inter-S1 competition; no reason to invent mutex or scheduler |

This is a **bounded source/intent screen**, not a run of these four products or proof that their maintainers would reject all improvements. No fresh behavior changes, issue posts, external forks/PRs, regraded assessments, or Organization S1 admission.

## Decision / next step

Keep AgentBox #61 primary (`SELECTED_FOR_NATIVE_DESIGN_FEEDBACK`). **No new code or more synthetic green CI** should be treated as product improvement. Further native edit dispatch/manager design work is gated on an applicable external maintainer response or an independently established *specific* implementation defect, not on generating more tests from the absent grade.

If external design discussion is authorized and maintainers accept a bounded manager-only opt-in, preregister actual box/worker before/after, including conflict count, independent parallelism, unknown scopes, unfinished dependencies, stale plan revalidation, operator intervention, and rollback. If rejected or no qualified path survives a bounded search, mark `BLOCKED_EVIDENCE / NO_ELIGIBLE_ASSESSMENT_CANDIDATE` for this cycle rather than invent an intervention. Keep #56 open as work not yet completed.
