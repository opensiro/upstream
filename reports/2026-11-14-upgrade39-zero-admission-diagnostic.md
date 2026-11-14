# Why upgrade batch 39 admitted zero harness improvements

**Date:** 2026-11-14 UTC · **Scope:** retrospective, read-only root-cause analysis of frozen `assessment-upstream-2026-11-14-39`. **Owner:** [Upstream #56](https://github.com/opensiro/upstream/issues/56). **Status:** process diagnosis and proposed follow-up, not a new technical mandate or proof that the underlying harnesses have no improvable functionality.

## Executive diagnosis

**Batch 39 did not fail because ten harnesses were shown to need no new features.** It failed to progress **nine plausible feature hypotheses** beyond source inspection to independent evidence of product need and counterfactual value, while a tenth feature proposal was *already provided* by the original harness.

The two most consequential process shortcomings were:

1. **Opportunity-blind admission:** the default selector prioritized **recent canonical Index assessments**, not independent demand for a useful native capability. The batch did not pass a `--priority-evidence` source-first lead file, though that path exists for separately attributed work.
2. **Breadth without deep adjudication:** the required six-function sweep produced 60 source-path inspections but only ten primary prospective feature questions. Nearly every post-source function row fell back to a generic statement plus a *future* test, rather than carrying out a bounded native experiment that could resolve `need` or the counterfactual.

**The four-gate refusal was appropriate.** Do not turn insufficient evidence into permission to write code. Change how evidence is gathered and how useful capability leads are selected, not the standard of proof.

## Evidence and exact arithmetic

Canonical Index frozen in batch: [ce58f217](https://github.com/opensiro/vsm-harness-index/commit/ce58f2172bcccbf96fc0248db8886a8847ae4f24).

Immutable before-source [hypothesis checkpoint 8cb7941](https://github.com/opensiro/upstream/commit/8cb7941163276283bf8fca046f67d0f8d679a17e) precedes fresh original repository inspection.

Frozen original [batch 39 manifest](https://github.com/opensiro/upstream/blob/8a5ebb36058140e2b84ae4fb1b0751c9b0be7d89/data/assessment-candidate-batches/2026-11-14-39.json), [HYPOTHESES.md](https://github.com/opensiro/upstream/blob/8a5ebb36058140e2b84ae4fb1b0751c9b0be7d89/data/assessment-candidate-batches/2026-11-14-39-HYPOTHESES.md), and [SUMMARY.md](https://github.com/opensiro/upstream/blob/8a5ebb36058140e2b84ae4fb1b0751c9b0be7d89/data/assessment-candidate-batches/2026-11-14-39-SUMMARY.md) are analyzed without changing any historical artifact.

| Observation | Direct evidence | Correct interpretation |
| --- | --- | --- |
| 10 selected sources; 60 VSM rows | Six rows per source in pre-source checkpoint and summary | Coverage, *not* 60 independent product improvements or native tests |
| **50/60** prospective function rows say `NO_SUPPORTED_HYPOTHESIS` | Count of six-function *table* rows in HYPOTHESES; ten remaining rows hold the selected primary question | Eighty-three percent of function rows had no specific prior new-feature hypothesis; some may be correctly out of scope |
| **59/60** post-source function rows repeat `Scoped code inspected, no fully justified new intervention from this function yet.` | Literal recurring disposition phrase across summary rows | Weak discrimination: a path inspection and generic next-test prompt, not actual resolution of individual functional opportunities |
| 9 `BLOCKED_EVIDENCE`, 1 `CLOSED_NO_CHANGE` | Exact manifest `stage` values | 90% unresolved *not rejected*; one scoped proposed capability duplicated an existing feature |
| `need`: 9 PENDING, 1 FAIL; `counterfactual`: 9 PENDING, 1 FAIL | Exact four native-fit gates | **Decisive blocker:** none had independently accepted user/native need and incremental benefit |
| `mechanism`: 10 PASS; `scope`: 10 PASS | Exact four native-fit gates | Source-level plausible implementation/scope alone does not qualify a feature; these judgments are not ten native runner validations |
| 10 `origin=INSUFFICIENT`; 0 native before/after; 0 external PR | Exact manifest and summary | No assessed derived benefit, no claim of successful deployment |
| Two current-source/review-ref drifts (Go Agent Harness, WittyCode) | Original SHA versus Index `review_ref` in summary | Important provenance to retain, **not** demonstrated reason for zero admission |

**Counting note:** The checkpoint also contains one introductory sentence mentioning `NO_SUPPORTED_HYPOTHESIS`; **50** is the count *inside the 60 function-table rows*, not the overall string occurrence count (51). The summary's 59 repetitive rows have one exception: HexaShell's S1 row explicitly identifies an existing equivalent trace/export.

## Per-repository causal findings and exact next falsifier

All next actions are **research proposals only**. Nothing below is already an admitted patch.

| # | Original repository / primary VSM link | Why the preregistered capability did not qualify | One decisive native/source step before a patch |
| --- | --- | --- | --- |
| 1 | [Akmatori](https://github.com/akmatori/akmatori/issues/67) · S3* | Proposed *read-only incident-memory provenance view* lacked an independently shown operator need. Original issue #67 asks for **different** capabilities: cross-incident corroboration and outcome-backed verification. | Test whether an operator cannot trace a disputed promoted memory. If that need fails, explicitly split the **source-first** #67 enhancements into their own demand-backed candidate; never retrofit derived attribution. |
| 2 | [AI-Scientist-v3](https://github.com/SakanaAI/AI-Scientist-v3/issues/5) · S3* | Per-claim manuscript audit export was proposed, but `AuditFinding` already contains structured claim/evidence fields. Original issue #5 describes a *different* evaluator nondeterminism bug; its attempted native pytest setup was blocked by missing `hydra` (environment, not a reproduced RED). | Inspect actual saved audit payload and consumer for a missing repair use case. Work on #5 only as separately labeled source-first bug-fix evidence. |
| 3 | [sapper-v2](https://github.com/N1nEmAn/sapper-v2/blob/7b75e6f1f5d5b4ae0c55878b0dd0994d9b08f1fb/lib/sapper.py) · S3* | Original verify path already emits VERIFIED/FAILED, while the supposed lost verifier identity in a downstream board/worker was unproven. | Verify and reject a fact, read it from a different worker, then determine whether the persisted fact exposes enough source/verdict provenance. |
| 4 | [sailry-harness](https://github.com/sailry/sailry-harness/blob/eaad1b7f18e448c8c4e9e9286e19560c8a351ae1/crates/node-runtime/src/agent/prompt/modes.rs) · S2 | Prompt mandates disjoint child work and parent integration. No first-party runtime collision, missing preview, or benefit from more coordination was shown. | Native two-child overlapping-write versus disjoint-write scenario; inspect the actual spawn/scope path and test false positives. |
| 5 | [slack-agent-runtime](https://github.com/sakomws/slack-agent-runtime/blob/16bb262715b7bacb64c7466cf106063c2fdf6c93/src/slack_agent_runtime/coding/reviewer.py) · S3* | Reviewer receives bounded diff and emits findings, but does not itself fetch a complete PR file inventory. No observed consumer falsely treating a partial diff as complete review was shown. | Trace the caller supplying the diff, inject a partial changed-file input through first-party test seams, and inspect current coverage semantics before proposing a reviewed/omitted-files receipt. |
| 6 | [go-agent-harness](https://github.com/shalyhinpavel/go-agent-harness/blob/63a2a15315c3a52964bcbc8b15d48f97f49f5a21/trace/trace.go) · S1 | Persistent JSONL tool_result observability exists, but exactly-once side-effect settlement on interruption/resume is not a proven product contract. Index reviewed SHA differs from current checked SHA. | Native crash/resume boundary after an actual deterministic tool effect; first verify whether recovery is a supported host workflow at all. |
| 7 | [WittyCode](https://github.com/WittyRyuji/WittyCode/blob/555b3c060de633c4cd98b21ba56c84d7487be527/desktop/core/harness/permissions.py) · S1 | Existing path resolution and preview logic makes a new write-target preview uncertain. **But no native permission-dialog test proved that a symlinked target displays its canonical path**; hence its actual stage is `BLOCKED_EVIDENCE`, not closed duplicate. Current original SHA differs from reviewed Index SHA. | Execute current permission-dialog/target symlink fixture; distinguish canonical-path exposure from existing diff preview. |
| 8 | [open-agent-sdk-python](https://github.com/codeany-ai/open-agent-sdk-python/blob/ab068156bf7db79cd23a883e8264a12803e23966/src/open_agent_sdk/engine.py) · S2 | Proposed two-agent mailbox/acknowledgment is a speculative scope expansion beyond the inspected single-session SDK; no supported host consumer or receiver contract. | Demonstrate two first-party supported agents with a real missing send/receive/ack workflow and maintainer-native API expectation. |
| 9 | [srchd](https://github.com/dust-tt/srchd/blob/4b5ffb44bdc6bb1d2181d746ec951dd30f89ed08/src/tools/system_prompt_self_edit.ts) · S4 | Constructor supporting append/edit of system prompt through `agent.evolve` already exists. Whether its lack of CLI exposure is deliberate, safely reversible or user-demanded was not established. | Trace CLI server registration and an explicitly supported user opt-in/inspect/revert contract; seek maintainer design fit before exposing sensitive self-modification. |
| 10 | [HexaShell](https://github.com/HexaFuture/HexaShell/blob/e0190ddb757955131578e9f9071f4ee8e7113f7a/hexashell/runtime/episode.py) · S1 | **The actual `CLOSED_NO_CHANGE`**: `Episode._cell` already stores code, outputs/errors, calls, timing and before/after steps; wrap-up writes transcript/result JSON. Proposed new offline read-only trace export added no established value. | Do not duplicate. A *different* deterministic full replay capability needs a new explicit missing-evidence/consumer claim, not retroactive reopening. |

**Important correction to conversation summaries:** batch 39's **WittyCode is blocked**, and **HexaShell is the single closed duplicate**. Earlier chat description swapped the two. The frozen batch controls, not that description.

## Root cause tree: what is proven versus inferred

### A. Selection is not an opportunity model — confirmed by selector implementation

The [selector](../scripts/assessment_batch_discovery.py) sorts Index candidates primarily by descending `reviewed_at`. It uses `--priority-evidence` only if explicitly supplied; otherwise `selection_policy=index_recency`. That optional source-first evidence file verifies URL shape at intake but not independent demand. Batch 39's checkpoint advertises 814 eligible and 289 excluded/reserved sources, then takes ten source-disjoint records without independent feature-signal ranking.

This is a **mechanistic explanation for weak prior demand filtering**, not causal proof that a different selection would have produced a successful feature. It also explains why ten apparently diverse repos can all pass license/scope preflight yet produce no admissible feature.

### B. A six-function audit was interpreted as a search — confirmed by artifact text

The checklists required all S1/S2/S3/S3*/S4/S5 sections and one current original-file path each. It satisfied exactly that bounded coverage. **But** 50 provisional `NO_SUPPORTED_HYPOTHESIS` rows plus 59 nearly identical post-source dispositions indicate the added five functions per source usually received no concrete new-feature candidate, ownership-specific counterfactual, or original native probe capable of settling its need.

Six file citations are *not* six deep product investigations. Do **not** infer a 0/60 feature-conversion rate, as only ten primary hypotheses were screened.

### C. The local research process stopped at `PENDING` — confirmed for this batch

All nine blocked primary candidates remained need/counterfactual pending, often with a **specific next executable test already written**. At most one independently attempted native pytest probe (AI-Scientist-v3) is documented, and it stopped on a missing testing dependency, not a product verdict. The current workflow can truthfully call its bounded screening complete while leaving the investigation's crucial falsifier unexecuted.

The four-PASS rule is justified; the gap is the **missing owned next research step** for promising blocked opportunities. Do not silently treat `PENDING` as `FAIL`, `NO_SUPPORTED_HYPOTHESIS`, or a reason to advance forever to newer repos.

### D. Attribution rules constrained fallback but did not forbid it — confirmed

After the Index-first checkpoint, first-party issue signals such as [Akmatori #67](https://github.com/akmatori/akmatori/issues/67) and [AI-Scientist-v3 #5](https://github.com/SakanaAI/AI-Scientist-v3/issues/5) appeared. They are legitimate **source-first** opportunities and must remain `ASSESSMENT_INFORMED` or `GENERAL_UPSTREAM` unless independent chronology supports otherwise. The contract allows that lane. The observed batch did **not** turn the strongest available source-first functional lead into a separately qualified follow-up.

Do not hide demand evidence just to preserve a perfect `ASSESSMENT_DERIVED` narrative. Distinguish the *goal of demonstrating VSM-derived discovery* from the broader goal of *usefully advancing harness functionality*.

### E. There is no evidence that legal permissions or VSM labels caused the zero

Original roots had readable MIT/Apache-2.0 LICENSE files; no primary row was recorded as license-blocked. All ten selected primary `mechanism` and `scope` gates say PASS, while demand/counterfactual did not. No target needed an A/C/P grade increase. This is not evidence that all ten products lack opportunities, or that VSM itself is unsuitable.

## Corrective follow-up (proposal, not an enacted new policy)

1. **Separate discovery from admission and from implementation:** after the six-function preregistration, allow cheap native source probes and demand reconstruction. **Do not** automatically freeze the outcome after one file citation if a concrete, licensed, bounded native falsifier is feasible; log execution or exact runner/dependency blocker.
2. **Use opportunity-first evidence without attribution laundering:** explicitly supply verified first-party backlog/workflow evidence for the source-first lane, plus a separate, genuinely Index-first cohort for strict causal VSM discovery. Never mix the two origin denominators.
3. **Require discriminating post-source function notes:** each of six rows should report the *specific observed existing capability, plausible missing native workflow, or precise out-of-scope condition*; a reused generic line is not enough to claim comprehensive functional screening. Six independent native tests are **not** required per repo.
4. **Treat promising `PENDING` as a research queue, not an admission:** retain a scoped owner, exact next runnable falsifier, input/test seam and priority; revisit before selecting ten more recent Index rows when the evidence acquisition cost is reasonable. This does not create a new scheduler or source reservation automatically.
5. **Pilot two bounded deeper feature cases, not ten more shallow ones:** investigate (a) Akmatori #67's outcome-backed memory verification as **source-first** and (b) slack-agent-runtime's incomplete-review coverage case as an **Index-first possible S3*** hypothesis. Use the actual original product path, independent native runner and four gates. Choose *no implementation* if the missing workflow or value fails. Keep AgentBox #61 as a separate already-owned strict-derived design-feedback case.
6. **Record selection and economics:** log source-first lead provenance, specific falsification work done, native validation availability and cost, eligibility of an alternative feature, and whether independent evidence changed a later decision. Compare with an ordinary feature-discovery/coding baseline before claiming VSM superiority.

### Acceptance checks for a prospective procedure change

- A selected repository with `need=PENDING` has a **tested** scoped counterexample or an exact documented reason it could not be run, not only a sentence instructing someone to run it later.
- The final disposition differentiates `ALREADY_PRESENT`, `OUT_OF_SCOPE`, `NEED_UNVERIFIED`, `TEST_BLOCKED`, `NO_BENEFIT_OBSERVED`, and `QUALIFIED` in prose or a separately proposed schema; frozen manifest enum values stay intact.
- Reviewer can trace one potential new native feature from independently grounded demand → source-native null → native fit gates → prospective test → independently executed before/after or a credible stop.
- No requirement to produce at least one patch, no invented VSM failure, no relaxed gate, no original upstream write, no retrospective change to batch 39, no new authority or hidden paid-model tests.

## Disposition

**Batch 39 = SCREENING_COMPLETE / IMPLEMENTATION_ADMISSION_ZERO / PRODUCT_OPPORTUNITY_SPACE_UNRESOLVED.**

The existing report is factually a bounded source-screen; the error was **interpreting that screen as sufficient depth to finish the quest for meaningful functional improvements**. This memo supplies a falsifiable diagnosis and next work without reopening frozen records or falsely claiming a product improvement.
