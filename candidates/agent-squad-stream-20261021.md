---
candidate_id: IMPR-AGENT-SQUAD-STREAM-20261021
state: PARKED
origin_class: ASSESSMENT_INFORMED
target_repo: 2FastLabs/agent-squad
index_sha: 5393b698bfdfa4ca14d97a79238234eca20694e5
assessment_path: assessments/ag/agent-squad.md
review_ref: 31eccfeb0d546262d1d0ec2e2e5239186f8d2954
source_sha: 729d5f52869c8280f599a9fa5cf27fc1df445602
fit_need: PASS
fit_mechanism: PENDING
fit_value: PENDING
fit_scope: FAIL
---

# IMPR-AGENT-SQUAD-STREAM-20261021 — bound background streaming on cancellation

**Research state:** `PARKED / ASSESSMENT_INFORMED`, blocker `BLOCKED_DUPLICATE_OPEN_PR`. [Agent Squad's Index assessment](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ag/agent-squad.md) maps request-to-specialist routing and optional supervisor composition as S1 operations. It **does not diagnose** streaming resource exhaustion, and the absence of S3 is not a justification for a new management agent.

Specific [upstream issue #662](https://github.com/2FastLabs/agent-squad/issues/662) reports that a consumer disconnect does not stop a selected agent's background streaming iterator, which continues consuming chunks and storing all text. A related [issue #661](https://github.com/2FastLabs/agent-squad/issues/661) may overlap; **one candidate covers this mechanism**, not two duplicate opportunities.

At current target `main@729d5f52869c8280f599a9fa5cf27fc1df445602`, first-party [`typescript/src/orchestrator.ts`](https://github.com/2FastLabs/agent-squad/blob/729d5f52869c8280f599a9fa5cf27fc1df445602/typescript/src/orchestrator.ts) still invokes `processStreamInBackground(agentResponse, accumulatorTransform, ...)` when returning the `AccumulatorTransform` to the client. [`typescript/src/utils/helpers.ts`](https://github.com/2FastLabs/agent-squad/blob/729d5f52869c8280f599a9fa5cf27fc1df445602/typescript/src/utils/helpers.ts) appends each emitted text chunk to a growing `accumulator` string. The code excerpts corroborate a buffering/cancellation concern, **not independently measured current-memory exhaustion**.

**Candidate native fix:** propagate consumer close/abort and upstream provider cancellation into the background iterator and enforce finite retained response capacity; preserve normal stream persistence and storage semantics for completed responses.

## Four native fit gates

| Gate | State | Evidence |
| --- | --- | --- |
| Need | `PASS` | First-party issue #662 documents client abort and background memory use; current source still shows the implicated flow |
| Mechanism | `PENDING` | Provider-specific stream cancellation, storage behavior and backpressure need contract examination |
| Counterfactual benefit | `PENDING` | No isolated abort + controlled-length response memory profile before/after |
| Scope | `FAIL` | Existing [upstream PR #689](https://github.com/2FastLabs/agent-squad/pull/689) already implements cancellation, stream byte/chunk bounds and corresponding tests; a second PR would duplicate the contribution. |

**2026-10-23 source-first follow-up:** broader upstream PR search found **open [#689](https://github.com/2FastLabs/agent-squad/pull/689)** (created 2026-09-17), targeting exactly the candidate's consumer-cancellation and resource-bounds mechanism. Candidate is parked rather than proposed for external PR; neither this card nor the local experiment claims authorship of #689.

**Independent bounded technical screen (local only):** checkout of original `main@729d5f5`; before tests: existing Jest **216/216 PASS**, three new first-party-code lifecycle tests **RED** (cancellation persisted partial text; no byte/chunk limits). A separate, **unpublished and redundant** local prototype made those regressions GREEN, with final native Jest **221/221 PASS**, `tsc --noEmit` and ESLint PASS. The tests use deterministic async iterators, never live LLM agents or public traffic. This shows a bounded mechanism test, not a reason to submit overlapping source code; no public code artifact or deployment is claimed.

**Decision:** `PARKED / BLOCKED_DUPLICATE_OPEN_PR`; follow upstream #689 rather than open a competing implementation. Product benefit in deployed Agent Squad, code merge/adoption, and Index grade are **NOT MEASURED**. No OpenSiro external PR, fork or upstream issue was created.
