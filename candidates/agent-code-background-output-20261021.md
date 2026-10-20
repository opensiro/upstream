---
candidate_id: IMPR-AGENT-CODE-BACKGROUND-OUTPUT-20261021
state: SCREENING
origin_class: ASSESSMENT_INFORMED
target_repo: avala-ai/agent-code
index_sha: 5393b698bfdfa4ca14d97a79238234eca20694e5
assessment_path: assessments/ag/agent-code.md
review_ref: 2734ab5f18939b20c774b39c4406788383e35255
source_sha: 82e0edfa7372c256d893d0854f954d9099254f88
fit_need: PASS
fit_mechanism: PENDING
fit_value: PENDING
fit_scope: PENDING
---

# IMPR-AGENT-CODE-BACKGROUND-OUTPUT-20261021 — prevent concurrent task-output collisions

**Status:** `SCREENING / ASSESSMENT_INFORMED`, **not assessment-derived S2 proof**. Index [agent-code assessment](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ag/agent-code.md) discusses write-capable child operations and missing first-party sibling interference response. It does **not** identify process-global output paths or duplicate task IDs. The concrete native defect originates from independent [upstream issue #515](https://github.com/avala-ai/agent-code/issues/515), not the Index finding.

At current `main@82e0edfa7372c256d893d0854f954d9099254f88`, [`crates/lib/src/services/background.rs`](https://github.com/avala-ai/agent-code/blob/82e0edfa7372c256d893d0854f954d9099254f88/crates/lib/src/services/background.rs) has `TaskManager::new()` initialize `next_id = 1` per process, `tasks_dir()` use a shared `agent-code/tasks` cache directory, and `task_output_path` use `<id>.out`. Its own test explicitly observes that task IDs recycle across managers and new registration truncates the matching output. In parallel independently running sessions, this may clobber an active task's output or cause incorrect adoption/identity attribution as reported by #515.

**Single bounded change hypothesis:** namespace task artifacts per session with correctly scoped adoption, or implement robust collision-resistant task IDs. Neither migration is yet selected: preserve prior-session resume and previous persisted task identity, correctly handle local/remote processes and prevent cross-session mixing.

| Native gate | Verdict | Evidence |
| --- | --- | --- |
| Need | `PASS` | First-party issue #515 details multi-process collision and current source identity design corroborates the mechanism |
| Mechanism | `PENDING` | Session scoped paths vs ID allocation must be chosen and migration compatibility defined |
| Counterfactual benefit | `PENDING` | No current-main two-process reproduction or matched before/after evidence |
| Scope | `PENDING` | Check adoption, journal persistence, TUI task drill-in, Windows behavior and outstanding PRs |

**Baseline:** `ISSUE_REPORTED_AND_CURRENT_SOURCE_CONSISTENT`; cross-process actual test `NOT_RUN`. **After:** `NOT_IMPLEMENTED`. Falsifier: external process already owns a stable namespace/isolation mechanism not covered by current source inspection, or accepted migration would break valid task resumption. **Next test:** two temporary isolated agent-code sessions using an explicit shared cache fixture; concurrent task ID registration and live stdout capture, then repeat after a minimal backwards-compatible fix. No third-party issue, PR, fork, permission or code change has been made.
