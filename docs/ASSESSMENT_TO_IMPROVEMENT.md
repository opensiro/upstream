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

## Capability-first research choice — prospective v0.9.0

For `upstream upgrade batch` and authorized revisits, first state a **new operator task, observable native output and independently testable benefit** using [capability-first research](CAPABILITY_FIRST_RESEARCH.md). An ordinary reliability fix can be useful without adding new functionality: report `BUG_FIX` separately from `MINOR_FEATURE`/`MAJOR_FEATURE`. A synthetic error, missing symbol or VSM grade is not user demand. Prefer one decisive native capability comparison or maintainer design answer to repeated bug/SDK probes; unresolved value/contract stays `OPPORTUNITY_RESEARCH_PENDING`, with exact owner and next check.

Preserve strict `ASSESSMENT_DERIVED` Index-first chronology, source-first attribution, the four native fit gates, source-native real dependency semantics, independently matched deterministic runner and no-live-LLM/user-trial scope. This does not change the technical right to work on a qualified repair or grant publication authority.

## Upgrade findings: features preferred, fixes still useful

The single [`upstream upgrade batch` command](ASSESSMENT_CANDIDATE_BATCHES.md#control-plane-command-upstream-upgrade-batch) uses **new `MINOR_FEATURE` / `MAJOR_FEATURE` capabilities as its first search priority, `BUG_FIX` as fallback** when no independently supported capability fits the target source. These are **ordinary engineering descriptions**, not new origin classes, evidence verdicts or counters. All S1–S5 functional observations can motivate a hypothesis, including accepted Index assessments with human-owned S1 under new (prospective) schema-v2 intake. Do not infer a defect or new permission from a VSM autonomy label.

A **repair** baseline must show the pinned native code failing an expected contract. A **new capability** baseline may instead show an independently desired workflow is unavailable, without falsely calling it a bug; the after-run must exercise a real new product-native workflow with matched inputs, scoped controls and regressions. Neither an absent feature, a green CI build, a new symbol, nor an issue title alone establishes a genuine need or observed end-user benefit. Large-feature design proposals must follow the target's normal maintainer issue/RFC/design gate before implementation. The existing independent deterministic runner requirement and no-live-model/user-trial scope remain unchanged.

Preserve `ASSESSMENT_DERIVED` only for specifically preregistered Index-first hypotheses, whether capability or repair. A valid later issue/code-driven bug fix stays `ASSESSMENT_INFORMED` (or `GENERAL_UPSTREAM` when unlinked): it may still be published via its proper authorized lane but is not a strict-derived discovery. Track technical effect, user benefit (measured/unmeasured) and external PR disposition using **existing** evidence/outcome vocabulary, without claiming their equivalence or adding a new scorecard.

## Discovery exploration is not native-fit admission

**Contribution protocol v0.8.0 (prospective upgrade cohorts):** the [post-batch-39 opportunity-depth procedure](ASSESSMENT_CANDIDATE_BATCHES.md#post-batch-39-opportunity-depth-and-closure-contribution-protocol-v080) requires discriminating six-function post-source findings and a decisive native probe of the strongest supported-but-pending opportunity when executable, or an exact attempted step/blocker plus an attributable follow-up. `SCREENING_COMPLETE` does not imply `OPPORTUNITY_DECIDED` or validated feature absence. This is an Upstream contribution-selection and reporting requirement, **not** a Methodology/Profile redefinition, a new manifest schema or permission to bypass native-fit/runner gates. Historical batch 39 remains frozen.

The upgrade-batch [two-lane opportunity protocol](ASSESSMENT_CANDIDATE_BATCHES.md#opportunity-first-intake-and-validation-prospective-cohorts) separates **cheap first-party investigation** from **permission to implement and claim benefit**. Use Index-first preregistration for possible strict `ASSESSMENT_DERIVED` hypotheses; a first-party issue/PR/workflow lead selected before that preregistration is transparently source-first and cannot be promoted to derived origin. Both lanes still review six VSM functions and gather real source-native observations; the resulting technical work can be useful without qualifying as a derived discovery.

During exploration, `need=PENDING` or unknown maintainer demand is not proof of `need=FAIL` and not `need=PASS`. Research current existing product workflows, actual source code paths and tests, user-facing contracts, maintainer plans and possible deterministic counterexamples; record what was checked for each function. **No patch, external fork or benefit claim follows from this permission to investigate.** First establish original licensing and contributor policy. Before derivative implementation/technical admission, require all four independent fit gates to be `PASS`, the relevant rights/maintainer design process, and the existing independent deterministic native-runner controls for new strict-derived cases. A source-only feasibility note is not an independently executed result.

In particular, `NO_SUPPORTED_HYPOTHESIS` at the pre-source checkpoint means no prospective prediction *from the Index alone*; it does not mean source inspection found no possible improvement. A final `CLOSED_NO_CHANGE` must cite what existing capability, duplicate, scope incompatibility or falsification was actually observed. Otherwise preserve `BLOCKED_EVIDENCE` with a specific next check. The six-function count proves coverage **only when paired with six post-source scoped probes**, not completeness of the opportunity space. Keep all previous frozen cohorts unchanged.

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
3. **Native need/fit (independent evidence):** **first check current upstream license text, notices and planned derivative/redistribution compatibility before derivative code or fork preparation**; missing GitHub license metadata alone is inconclusive, but no actual applicable grant means no public derivative fork/patch. The read-only intake preflight supplies evidence, not automatic license clearance. Then inspect the current target default branch and its genuine contribution target (which can be a distinct `development` branch), first-party code, maintainer signal/issue/PR overlap, DCO/CLA/contributor rules, product scope and impact. Record `PASS`, `PENDING` or `FAIL` separately for **need, mechanism, counterfactual benefit, scope**. A VSM diagnosis or issue citation alone cannot make these pass.
**External dependency semantics: required `need` falsifier, before test design and implementation.** If a proposed product failure relies on how a third-party SDK, driver, framework, CLI or HTTP client handles a status/error/race, independently reproduce the *actual pinned/supported dependency API call* or verify its precise source path **before** accepting `need=PASS` or writing an injected-failure regression. Capture dependency/version, API and product call chain, exact observed exception or return, a negative control and the executable command or first-party source link. A fake transport may isolate an already verified error, but **a mock-only RED→GREEN cannot prove that the alleged error can reach real product code**, even if the surrounding product functions are genuine. Unverified behavior means `need=PENDING` / `BLOCKED_EVIDENCE` and **no external PR** on that premise; a disproven dependency assumption means `need=FAIL` / `CLOSED_NO_CHANGE` (screening), and any previously submitted PR is recorded with its own actual closed-unmerged lifecycle status. Preserve historical RED/GREEN logs, but explicitly withdraw unsupported product-need claims. A genuine-SDK/no-daemon probe can refute a claimed SDK exception, not prove the absence of every deployed race. See [KnowWork #4 correction](../pilots/knowwork-start-race-s2/CORRECTION_2026-11-14.md).

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
| `publication_feedback` | Fork/PR refs **only when they exist**, effective standing publication mandate and per-case gate evidence, maintainer disposition, further investigation |

### Classification example: HarnessDesk #1772

- [Pinned Index assessment](https://github.com/opensiro/vsm-harness-index/blob/13dab0d4f2954614f7f99a9fa044ad5b9a154490/assessments/ha/harnessdesk.md) includes **host/common tool projection** in the assessed system and describes operating S1/S2 agent work. It **does not identify** the second-host Unix-socket deletion bug as a VSM functional weakness.
- The concrete native defect comes from [HarnessDesk's first-party issue #1772](https://github.com/HarnessDesk/HarnessDesk/issues/1772) and current `tool-gateway.ts`, **not from an assessment diagnosis**. The [V2 patch](https://github.com/opensiro/upstream/blob/main/pilots/harnessdesk-1772/tool-gateway-ownership-fix-v2.patch) independently improves socket-owner safety.
- **Origin `ASSESSMENT_INFORMED`**. Actual targeted gateway regressions and [read-only pinned upstream `pnpm check:push` PASS](https://github.com/opensiro/upstream/actions/runs/39467673123) support *source validation*, not measured live/deployed product benefit, autonomous VSM ownership transfer, or a finished external contribution. The external `opensiro/fix-toolgateway-1772` branch and upstream PR remain absent; local policy remains `PROPOSED_NOT_ACTIVE`.
- Keep HarnessDesk #1772 as a legitimate **technical reliability pilot**; do not reclassify it as the new stronger assessment-derived experiment or erase its historical receipts. See [case-specific linkage note](../pilots/harnessdesk-1772/ASSESSMENT_LINKAGE_2026-10-20.md).

### Next case

Select through **fresh Index-first evidence** under [#56](https://github.com/opensiro/upstream/issues/56). A possible functional ownership hypothesis (such as an `S3=C(P)` human-current-control decision in a real harness) is only a **question to investigate**, not an automatically deficient grade, a selected target or an authorized contribution.
