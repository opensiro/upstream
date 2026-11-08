# Assessment → functional improvement → upstream contribution

**Owner:** `opensiro/upstream`. **Scope:** [the assessment-driven candidate S1 test](ASSESSMENT_DRIVEN_S1_TEST.md), not the generic Upstream portfolio or a fourth admitted Organization S1 domain.

**Tracked experiment:** [Upstream #56](https://github.com/opensiro/upstream/issues/56). Existing GitHub stage/authorization rights remain as defined in [Control Plane handoff](CONTROL_PLANE_HANDOFF.md) and [Upstream #6](https://github.com/opensiro/upstream/issues/6). This document creates no permissions.

**Dated publication exception:** the owner's 2026-10-23 [finite mandate](CORRECTIVE_PR_PUBLICATION.md) authorizes contributor-fork, branch and external **Draft PR** publication for precisely 34 already verified Corrective packets, subject to live source/policy/actor checks. This document itself does not extend that authorization to future candidates or other classifications. The [publication ledger](../data/corrective-publication/2026-10-23-01.json) tracks actual delivery, separate from historical source-only technical outcomes.

## Purpose

The [candidate-batch protocol](ASSESSMENT_CANDIDATE_BATCHES.md) owns **serial
continuation across multiple Index-first screening records**. A complete
native technical/handoff step moves the current row to its real stage and
continues with the next row even when external publication awaits a separately
owned decision; it does not declare the external contribution complete.

Produce **independently useful, measurable changes to real AI harness behavior whose selection and intervention rationale arise from a concrete VSM assessment finding**. A PR is a delivery vehicle; a higher autonomy grade is not the goal, metric or success condition.

```text
current canonical Index assessment @ immutable SHA
  → specific observed VSM function / decision owner / feedback shortfall
  → falsifiable proposed native behavior change
  → independent current-upstream need and fit validation
  → reproducible pre-change baseline, safety requirements
  → bounded implementation and matched post-change evaluation
  → validated product-effect finding (including negative/null results)
  → permissioned contributor-fork preparation and separately authorized external PR
  → actual maintainer feedback, optionally a separately owned reassessment
```

The target's system-in-focus, acceptable behavior and developer/maintainer needs take precedence over making its VSM vector appear stronger. Improving a function **does not necessarily change its autonomy owner or Index grade**.

## Pre-registered hypothesis and separate native execution — 2026-11-08 refinement

A strong `ASSESSMENT_DERIVED` origin is a **prospective, testable prediction from the assessment**, not an upstream issue relabeled afterward. Before inspecting the target's fresh implementation, issues or PRs for the proposed fix, preserve an attributable, dated, immutable or reviewable **hypothesis checkpoint** with:

1. The pinned canonical Index assessment, its exact observed S-function finding, system boundary and present decision/feedback owner.
2. The predicted *product-native* weakness and why that particular assessment evidence predicts it; expected functional benefit **even if the VSM grade stays `C`**, plus a plausible null/negative outcome.
3. The proposed first-party observation/test and falsifier; what evidence would show the behavior is intentional, already solved or outside product scope.
4. The checkpoint ref/time and selection order, followed **later** by independently gathered current source/issue/maintainer evidence. Keep both sides of the chronology; a retrospective narrative does not establish derivation.

**Separate test designer from test executor.** An AI assistant may examine Index evidence, register the hypothesis, inspect native fit, propose a deterministic test/patch and review resulting logs, but **must not directly execute the target's before/after validation tests as the chatbot** for this strict assessment-derived pilot. Submit the pinned first-party test plan/code to a distinct deterministic runner (for example, a repository CI workflow) that executes without a live model; retain the runner identity, workflow/run URL, code/test SHA, actual commands, environment, logs and before/after results. A runner receipt establishes that the tests executed, **not** that the selected test is independently well designed or proves a real product need: verify the genuine first-party path, counterfactual, native-fit gates and matched controls separately. If no suitable runner is available, record `BLOCKED_INDEPENDENT_EXECUTION`; do not substitute an assistant-run test or claim `BENEFIT_SUPPORTED`.

The aim is **more valid assessment-derived discoveries and demonstrated product benefits**, not a target proportion achieved by relabeling. Report each cohort's screened denominator, prospective derived hypotheses, independently confirmed native needs, runner-verified benefits, negative/null results and `ASSESSMENT_INFORMED` cases separately. A function can be improved **within `C`** with no `C → A` transition. Conversely, merely increasing confidence that the old `C` assessment was correct is an assessment/research finding, **not** evidence of an improved product.

This applies prospectively to new strict-derived validation under [#56](https://github.com/opensiro/upstream/issues/56); it does not invalidate historical source-tested `ASSESSMENT_INFORMED` patches, retrofit old records, instantiate a runner, or grant external write rights.

## Where native CI runs

**New external-harness-specific workflows belong outside `opensiro/upstream` CI.** Use the [native CI placement contract](NATIVE_CI_EXECUTION.md): `opensiro/upstream` retains research checkpoints, patch/test packets and attributed before/after receipts, while permitted `opensiro-contributions/<target>` working forks or a separately controlled deterministic host execute the target's native tests. An available external original repository may run CI only under its actual owner's permissions. A successful earlier Upstream pilot workflow remains historical evidence, not precedent for committing one new Upstream workflow per harness.

The independent runner requirement, real first-party code path, licensing, exact source pins and external-stage grants are **unchanged**. A missing authorized executor is `BLOCKED_INDEPENDENT_EXECUTION`; a passing repository-integrity check is not native product validation.

## Mandatory validation boundary — native scripted tests only

**Operator decision (2026-10-22; applies to this experiment and subsequent assessment-to-upstream pilots):** validate changes using **deterministic scripts, native source tests, CLI/tool-level integration tests and first-party regression suites only**. **Do not run, request, require or list as a next gate any live LLM-agent session, model API/provider call, Browser agent-quality trial, paid inference or human-user trial.** An agent-shaped fixture may supply fixed actions/stubbed choices only when the test actually executes the target's native code path; it must be labeled as scripted, never passed off as a model-agent run. Do not invent a surrogate product behavior that bypasses the actual relevant mechanism.

The **technical validation gate is complete** when an independently executed, pinned native baseline demonstrably fails or underperforms on a reproducible, relevant script, the scoped implementation passes a *matched* after-script, and appropriate native regressions/controls pass, with attributable runner receipts as required above for new strict-derived cases. Preserve failures and negative/null results. This is sufficient evidence of the **bounded mechanism effect**; no live agent experiment is a prerequisite for technical completion or for a separately authorized upstream contribution.

This rule **does not** convert the observed scripted delta into measured deployed adoption, user productivity, security assurance, VSM autonomy/grade change, or upstream maintainer acceptance. Record these as unmeasured/unestablished unless independently evidenced. Delivery permissions, separately authorized external publication and maintainer review are separate gates, never additional LLM testing gates. If wider model-agent research is proposed in the future, it is **outside this experiment** and requires a distinct explicit operator decision.

## Classification: origin strength is not implementation status

| Class | Required explanatory evidence | May be counted as evidence of the assessment-derived discovery path? |
| --- | --- | --- |
| `ASSESSMENT_DERIVED` | **Index-first** assessment identifies a specific *observed* functional constraint/feedback or ownership gap; that finding motivates the chosen intervention; a distinct current-source check establishes a useful native weakness; a concrete before/after plan makes the effect falsifiable. | **Yes, if those links are documented.** A proposed case is not yet a proven product improvement. |
| `ASSESSMENT_INFORMED` | Assessment identifies an important subsystem or helps select an area, but the exact defect is independently discovered (issue, maintainer, code) and not diagnosed by the assessment finding. | **No** for strict derived discovery. May proceed as useful upstream engineering. |
| `GENERAL_UPSTREAM` | No verified Index finding → selected behavior/mechanism link. | No. Count only in the ordinary upstream route. |
| `INSUFFICIENT` | Missing/pending canonical pin, finding, native fit or discovery-order evidence. | No until independently established. |

Record **classification** separately from **work stage** (`SOURCE_PREPARED`, `EXERCISED`, `BLOCKED`, `SUBMITTED`, `MERGED`, etc.) and **outcome** (`BENEFIT_SUPPORTED`, `NO_BENEFIT_OBSERVED`, `INCONCLUSIVE`). For example, an assessment-derived hypothesis with negative post-change measurements remains a real derived *test* but not an improved system. A well-tested assessment-informed bug fix remains a valid engineering contribution, not a derived diagnostic success.

Do not promote `ASSESSMENT_INFORMED` into `ASSESSMENT_DERIVED` by finding a post-hoc VSM label compatible with an already-chosen issue. If the actual assessment does not record a decisive weakness, the candidate cannot obtain a stronger origin label by assuming that low `S3`, absent `S4` or human-owned `S5` is necessarily a fault. Equally, a detected functional weakness must be checked against the target's intended product behavior; not every theoretical delegation is desirable.

## Admission gates for a new strong case

1. **Index-first discovery (positive evidence):** refresh the *current canonical Index default branch*; independently select an included assessment before picking an upstream fix or favorite fork; pin Index commit, assessment path, its assessed target `review_ref`, function and exact source-backed decision/feedback owner/constraint. Preserve dated snapshots; a historical assessment never claims the source is still unchanged.
2. **Function-to-mechanism hypothesis (positive evidence):** *before fresh target-code/issue inspection*, preserve the dated hypothesis checkpoint described above. Identify what operational loop does not close as required, which actor currently makes the decisive decision, the specific mechanism proposed to change behavior, expected native benefit and a plausible failure/null outcome. Explain *why the assessment finding predicts/selects this mechanism*, independently of any prospective VSM grade.
3. **Native need/fit (independent evidence):** inspect current target default branch and its genuine contribution target (which can be a distinct `development` branch), first-party code, maintainer signal/issue/PR overlap, licensing/DCO/CLA rules, product scope and impact. Record `PASS`, `PENDING` or `FAIL` separately for **need, mechanism, counterfactual benefit, scope**. A VSM diagnosis or issue citation alone cannot make these pass.
4. **Before/after script protocol (before implementing):** freeze deterministic native test inputs, baseline source SHA, environment, metric/observable, sample or repeated-trial plan, effect threshold or acceptance condition, safety/rollback checks, expected regressions and confounders. Select metrics from the actual function: e.g. preserved concurrent writes, CLI recovery outcome, refusal of unsafe source actions or reliability *where relevant*. Do not impose arbitrary agent autonomy or score-driven targets.
5. **Independent native scripted test and repair:** have the separate deterministic runner demonstrate the pre-change failure/shortfall against actual product source through reproducible scripts; implement one scoped upstream-native change; have the runner re-run the matched workload against changed code and native regressions, and inspect its receipts. Retain exact code, tests, commands, observations and failed attempts. Do not substitute a mock-only pass for a real product-code path. A green CI alone proves checks ran, **not that a deployed/user benefit was measured**. Do not add live LLM agents as an extra verification step.
6. **Decision and outcome:** compare pre/post observations and evidence limits. State `BENEFIT_SUPPORTED`, `NO_BENEFIT_OBSERVED` or `INCONCLUSIVE`, plus functional mechanism effect and whether any authority/decision owner changed. No self-awarded reclassification of Index grades. If scope/policy is incompatible, return `NO_ELIGIBLE_ASSESSMENT_CANDIDATE` / `BLOCKED_EVIDENCE` instead of swapping to a convenient unrelated issue.
7. **Authorized delivery and external feedback:** only write to a permitted fork/branch under effective provider-bound authority. Publish an external PR only under an applicable separate decision: manual for ordinary cases; the finite 2026-10-23 owner mandate for its exact Corrective 34. Track maintainer review, actual merge/non-merge and downstream observed behavior without treating either a push or acceptance as proof of benefit. A later reassessment belongs to Index/Skills under their own procedures.

**Do not require a new agent, automation service, grant signer, fork or duplicated assessment to qualify the idea.** Reuse the existing Control Plane and Upstream engineering route; issue #56 owns the research experiment, issue #6 owns stage execution and authorization, and Organization #274 remains a separate reserved scope decision.

## Minimum evidence record (reviewable prose is sufficient)

| Field | Content |
| --- | --- |
| `index_origin` | Index SHA, assessment URL/path, assessed source `review_ref`, targeted S-function, source lines supporting the finding |
| `selection_order` | Attributable hypothesis checkpoint ref/time **before** fresh implementation/issue inspection, with Index assessment, prediction, null/falsifier, followed by dated independent native-fit evidence; if chronology is missing, do not confidently claim `ASSESSMENT_DERIVED` |
| `weakness_and_hypothesis` | Observed limitation within declared system boundary; current decision owner and feedback failure; planned bounded mechanism; alternate explanations and falsifier |
| `native_fit` | Fresh upstream branch/SHA, actual issue/code/policy/PR overlap and need/mechanism/counterfactual/scope four gates |
| `baseline` | Unmodified product behavior with command/scenario, environment, metric, quantitative or reproducible qualitative observation, safety cases |
| `intervention` | Diff, source/patch pins, specific function/mechanism, changed actor/rights if any; ordinary engineering quality checks |
| `after` | Matched execution with result, failures, regressions, observed delta and validity limits |
| `runner_execution` | Distinct deterministic CI/runner identity, exact run URL/artifact, source/test SHA, commands/environment, before/after logs and checks; or `BLOCKED_INDEPENDENT_EXECUTION` without a supported effect claim |
| `classification_and_outcome` | One origin class, separate execution stage, one effect verdict; explicit counterevidence and unknowns |
| `publication_feedback` | Fork/PR refs **only when they exist**, permissions, human publication decision, maintainer disposition, further investigation |

### Classification example: HarnessDesk #1772

- [Pinned Index assessment](https://github.com/opensiro/vsm-harness-index/blob/13dab0d4f2954614f7f99a9fa044ad5b9a154490/assessments/ha/harnessdesk.md) includes **host/common tool projection** in the assessed system and describes operating S1/S2 agent work. It **does not identify** the second-host Unix-socket deletion bug as a VSM functional weakness.
- The concrete native defect comes from [HarnessDesk's first-party issue #1772](https://github.com/HarnessDesk/HarnessDesk/issues/1772) and current `tool-gateway.ts`, **not from an assessment diagnosis**. The [V2 patch](https://github.com/opensiro/upstream/blob/main/pilots/harnessdesk-1772/tool-gateway-ownership-fix-v2.patch) independently improves socket-owner safety.
- **Origin `ASSESSMENT_INFORMED`**. Actual targeted gateway regressions and [read-only pinned upstream `pnpm check:push` PASS](https://github.com/opensiro/upstream/actions/runs/39467673123) support *source validation*, not measured live/deployed product benefit, autonomous VSM ownership transfer, or a finished external contribution. The external `opensiro/fix-toolgateway-1772` branch and upstream PR remain absent; local policy remains `PROPOSED_NOT_ACTIVE`.
- Keep HarnessDesk #1772 as a legitimate **technical reliability pilot**; do not reclassify it as the new stronger assessment-derived experiment or erase its historical receipts. See [case-specific linkage note](../pilots/harnessdesk-1772/ASSESSMENT_LINKAGE_2026-10-20.md).

### Next case

Select through **fresh Index-first evidence** under [#56](https://github.com/opensiro/upstream/issues/56). A possible functional ownership hypothesis (such as an `S3=C(P)` human-current-control decision in a real harness) is only a **question to investigate**, not an automatically deficient grade, a selected target or an authorized contribution.
