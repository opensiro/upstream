---
candidate_id: IMPR-AGENTBOX-DEPENDENCY-20261020
state: PARKED
origin_class: ASSESSMENT_INFORMED
target_repo: madarco/agentbox
index_sha: 5393b698bfdfa4ca14d97a79238234eca20694e5
assessment_path: assessments/ag/agentbox.md
review_ref: 463a6a0a20176147f0b0dbfa8a261aba5e43cbd6
source_sha: 605ee75d63319003c188bc532d4e5b2ba36a51d6
fit_need: PENDING
fit_mechanism: PENDING
fit_value: PENDING
fit_scope: PENDING
---

# IMPR-AGENTBOX-DEPENDENCY-20261020 — clarify dependent task readiness

**Candidate state:** `PARKED` (`PRODUCT_SEMANTICS_UNCLEAR`).
**Origin class:** `ASSESSMENT_INFORMED`, **not** an independently assessment-diagnosed hard dependency bug.
**Owner:** [Upstream #61](https://github.com/opensiro/upstream/issues/61) and [#56](https://github.com/opensiro/upstream/issues/56).
**Target:** [madarco/agentbox](https://github.com/madarco/agentbox), `main@605ee75d63319003c188bc532d4e5b2ba36a51d6` checked 2026-10-20.
**Index context:** [AgentBox S2 assessment, Index @5393b698](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ag/agentbox.md) identifies manual inter-box coordination, at assessed target ref `463a6a0a20176147f0b0dbfa8a261aba5e43cbd6`. **It does not specifically report a `dependsOn` readiness bug.** The exact observation was identified in a later independent source inspection.

## Independent native observation

The [native task-store baseline](../pilots/agentbox-s2/NATIVE_DEPENDENCY_DISPATCH_RECEIPT_2026-10-20.md), [PR #65](https://github.com/opensiro/upstream/pull/65), uses *actual* `@agentbox/relay` task-store functions. It finds **two of two tested paths** that allocate a dependent task to a box/job while its predecessor remains `todo`, marking the dependent task `in_progress`. A completed-dependency positive control also enters `in_progress`. CI passed.

**Crucial limitation:** task `in_progress` can represent **assignment**, not a coding worker's actual execution. There is **no demonstrated premature agent action**, overwritten change, failed product contract or proof that blocking assignment improves AgentBox. First-party records explicitly allow many tasks to be allocated to a single box.

## Hypothesis and falsifier

Question only: should the future Phase 4 manager **defer worker dispatch** for unfinished `dependsOn` relations while preserving legal early allocation? Or is dependency metadata advisory and ordering delegated to managers/humans?

- **Candidate minimal behavior (unapproved):** at opt-in manager planning time, show an explicit `not_ready`/wait recommendation for a task whose dependency is unfinished; refresh readiness before dispatch; leave task-store acceptance/status alone.
- **Falsifier:** if task allocation is intentionally independent of execution/readiness, the observed native behavior is correct and no product change is warranted. Enforcing a new rejection at `addTask` or `assignTasks` may break legitimate workflows.

## Four native fit gates

| Gate | Verdict | Reason |
| --- | --- | --- |
| Need | `PENDING` | First-party documentation describes dependencies, but no product-native requirement to gate the *allocation* APIs has been established |
| Mechanism | `PENDING` | Candidate location likely manager dispatch, not native task-store; no approved interface |
| Counterfactual benefit | `PENDING` | No actual worker started early, so no before/after execution harm/benefit measured |
| Scope | `PENDING` | Changing default task status/assignment semantics may violate intended product use |

**Baseline:** `MEASURED_NATIVE_METADATA`. **Product after:** `NOT_TESTED`. **External contribution:** `NONE`. **Next evidence:** first-party semantics decision under [unpublished AgentBox inquiry](../pilots/agentbox-s2/AGENTBOX_DESIGN_INQUIRY_DRAFT.md); separate candidate even though the discovery context overlaps the file-grouping proposal.

Do **not** merge this card with the assessment-derived overlap candidate merely to improve a VSM grade or make a larger upstream PR.
