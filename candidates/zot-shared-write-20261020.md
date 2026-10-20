---
candidate_id: IMPR-ZOT-SHARED-WRITE-20261020
state: PARKED
origin_class: ASSESSMENT_DERIVED
target_repo: patriceckhart/zot
index_sha: 5393b698bfdfa4ca14d97a79238234eca20694e5
assessment_path: assessments/zo/zot.md
review_ref: 2a19df15ba8278dd6a92240ab6c2ae267c3cf6c3
source_sha: c62d1c549d52cd33390968ffa50667cb79609152
fit_need: PENDING
fit_mechanism: PENDING
fit_value: PENDING
fit_scope: PENDING
---

# IMPR-ZOT-SHARED-WRITE-20261020 — preserve independent swarm edits

**Candidate state:** `PARKED` (new built-in behavior has `BLOCKED_EVIDENCE` native demand).
**Origin class:** `ASSESSMENT_DERIVED` mechanism hypothesis, **not** a validated product improvement.
**Owner:** [Upstream #56](https://github.com/opensiro/upstream/issues/56).
**Target:** [patriceckhart/zot](https://github.com/patriceckhart/zot), frozen current-source investigation `main@c62d1c549d52cd33390968ffa50667cb79609152`.
**Index origin:** [Zot S2 assessment @ Index 5393b698](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/zo/zot.md), assessed upstream ref `2a19df15ba8278dd6a92240ab6c2ae267c3cf6c3`, explicitly identifies parallel workers sharing a writable RepoRoot with no inter-worker write-claim arbiter.

## Actual mechanism and independent product concern

First-party Zot swarm intentionally gives parallel workers the same RepoRoot. A deterministic native `Swarm`/`WriteTool` source fixture demonstrated two write actions reporting success while only one of two intended edits survived in the shared file. Source-native manual Git worktrees **preserved both branch edits** (2/2), but left one explicit Git merge conflict for later resolution.

[Executed, pinned receipt](../pilots/zot-shared-workspace/WORKTREES_COUNTERFACTUAL_RECEIPT_2026-10-20.md), [OpenSiro PR #62](https://github.com/opensiro/upstream/pull/62); full affected Go tests and race test passed. This is **no-Zot-code manual containment**, not shipped automatic coordination, typical user frequency, or acceptance by maintainers.

## Candidate intervention and falsifier

Possible new *opt-in* Zot-native worktree isolation, with explicit branch integration and conflict feedback, could avoid silent same-file write replacement. But this could violate Zot's deliberately lightweight shared-directory model or duplicate documented manual Git worktrees.

**Falsifier:** if maintainers intentionally favor manual worktrees and would not adopt the added lifecycle complexity, a built-in isolation feature has no demonstrated product-native fit even though the experimental conflict is real.

## Four native fit gates

| Gate | Verdict | Reason |
| --- | --- | --- |
| Need | `PENDING` | No verified maintainer request/user incident for automatic Zot-managed isolation |
| Mechanism | `PENDING` | Native shared-root limitation measured, but minimal production-safe lifecycle/cancellation/write-tool design not approved |
| Counterfactual benefit | `PENDING` | Manual containment works in source fixture; additional value of changing Zot itself not measured |
| Scope | `PENDING` | Shared-root contract and simple binary architecture could make automatic manager inappropriate |

**Baseline:** `MEASURED_NATIVE_FIXTURE`. **Product after:** `NOT_IMPLEMENTED`. **Effect verdict:** `INCONCLUSIVE` for a built-in Zot change. **External fork/issue/PR:** `NONE`.

**Next gate:** independent first-party need and design suitability, or retain `PARKED` rather than adding another manager. No required Index regrade or invented write right.
