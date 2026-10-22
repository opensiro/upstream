---
candidate_id: IMPR-AO-REVIEWER-READONLY-20261021
state: SCREENING
origin_class: ASSESSMENT_INFORMED
target_repo: Untrivial-ai/agent-orchestrator
index_sha: 5393b698bfdfa4ca14d97a79238234eca20694e5
assessment_path: assessments/ag/agent-orchestrator.md
review_ref: 1e4a394b20c470d281b2a7f6f63fd47c30af5019
source_sha: 30723c0be55edde1a012a4cd3d25039c43002e26
fit_need: PASS
fit_mechanism: PENDING
fit_value: PENDING
fit_scope: PENDING
---

# IMPR-AO-REVIEWER-READONLY-20261021 — enforce actual read-only reviewer execution

**State:** `SCREENING`; `ASSESSMENT_INFORMED`, not a directly diagnosed Index failure. The [Index assessment](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ag/agent-orchestrator.md) credits a separate reviewer S3*=A, independently inspecting code in a constrained role. It does **not** report filesystem redirection as a bypass. The current native issue supplies a new product-specific failure of an intended review safety invariant.

## Current identity and first-party native report

The frozen assessment records `Untrivial-ai/agent-orchestrator`. GitHub public API currently redirects this repository to **`OrchestratorInc/agent-orchestrator`**; the current public default commit inspected through the alias is `30723c0be55edde1a012a4cd3d25039c43002e26`. A proposal must resolve and revalidate **canonical owner/CLA/repository** before any execution; the card retains the **assessed target spelling** to preserve read-only Index-source matching.

[Open native issue #6962](https://github.com/OrchestratorInc/agent-orchestrator/issues/6962) reports that read-only reviewers cannot use `Write/Edit/NotebookEdit` but still have Bash shell redirection that can write local files. It reports actual field observations in versions 0.14.3/0.14.4, including unapproved temporary payload staging. The governing contract reportedly uses stdin submission `ao review submit --body -`, not filesystem staging. This is an **upstream reporter's evidence**; no independent execution test was run here.

## Bounded intervention hypothesis

Determine how to enforce the already-declared no-write invariant **against the shell and child-process surface**, not merely by denying three tool names. Reviewers must retain required source-inspection capability and sanctioned stdin submission. Do not assume that blocking a shell command string is a robust filesystem sandbox; the owner must define a real OS/tool execution boundary and supported workflows.

## Four native fit gates

| Gate | Status | Evidence |
| --- | --- | --- |
| Need | `PASS` | Specific first-party issue #6962 plus original reviewer read-only role |
| Mechanism | `PENDING` | Safe OS sandbox or verified command-execution constraint not chosen/tested |
| Counterfactual benefit | `PENDING` | No real current-head before/after no-write regression execution |
| Scope | `PENDING` | Canonical repo redirect, owner policy, review submission pathway, maintained reviewer interfaces and overlapping fixes require current check |

**Baseline:** `ISSUE_REPORTED`, current public HEAD identified, independent reproduction `NOT_RUN`. **After:** `NOT_IMPLEMENTED`. **Falsifier:** an already-shipped supported reviewer configuration demonstrably prevents both redirection and equivalent writes, or upstream maintainers explicitly narrow the claimed no-write contract instead. **Next gate:** read-only command capability inventory and isolated no-write property test with no external credentials. This does not authorize attempts against real user workspaces, GitHub writes, changes to Index, or automatic contribution publication.
