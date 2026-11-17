# Paperclip — architecture-first capability roadmap after Index re-assessment

**Snapshot:** 2026-11-17. **Result:** `PLAN_ONLY`. **External issue: DRAFT — NOT PUBLISHED**. This is an internal, dated, **non-authoritative Upstream example** governed by [Capability Roadmap](../CAPABILITY_ROADMAP.md), not a second Index assessment, delivery promise, maintainer request, or third-party communication.

## Identity and pins

- Original repository: paperclipai/paperclip
- Original HEAD: 904c01d1a3a16de817792432d5d5a24f6e4bde12
- Observed at: 2026-11-17
- Accepted Index assessment: https://github.com/opensiro/vsm-harness-index/blob/975a58814b767cfca414c152480f787bfe80944b/assessments/pa/paperclip.md
- Accepted assessment blob SHA: 238863a500491b7851fa90478ae64b2471acb219
- Accepted review ref: 7f9867895c4e7e9589b233a93aa9efceb0c992d0
- Accepted reviewed at: 2026-11-17
- Last successful assessment age: 0 calendar days at observation; **no 30-day freshness advisory**. The original default branch advanced five commits from the accepted review ref to the observed HEAD; those newer changes are **not part of the accepted Index assessment**, and their effect is not presumed.
- Accepted re-assessment lifecycle: [Index issue #3230](https://github.com/opensiro/vsm-harness-index/issues/3230), **CLOSED COMPLETED**; [Index PR #3235](https://github.com/opensiro/vsm-harness-index/pull/3235), **MERGED** at `975a58814b767cfca414c152480f787bfe80944b`; this source review changed the pin and evidence, not the six-function vector.
- System in focus: one supported **Paperclip company**, its first-party agent/runtime, goal, task, management, review and board-decision modes; not the Paperclip maintainers' development organization, a recursive manager subtree, non-installed provider/plugin actor, or private Cloud-only implementation.
- Assessment vector: **`S1=A S2=A S3=A(P) S3*=A S4=— S5=P`**, accepted and re-reviewed under [Profile 0.2.4](https://github.com/opensiro/vsm-harness-profile/blob/main/PROFILE.md) and [Methodology 0.3.8](https://github.com/opensiro/vsm-harness-skills/blob/main/skills/assess-vsm-harness/SKILL.md). This is a function-specific ownership observation, **not** a product-quality score or a reason to implement a missing VSM box.
- Original delta since accepted review: https://github.com/paperclipai/paperclip/compare/7f9867895c4e7e9589b233a93aa9efceb0c992d0...904c01d1a3a16de817792432d5d5a24f6e4bde12 ; five commits observed, no autonomous semantic reassessment at this newer head.

## Rights and authority

- Original source is [MIT-licensed](https://github.com/paperclipai/paperclip/blob/7f9867895c4e7e9589b233a93aa9efceb0c992d0/LICENSE). [Contributor rules](https://github.com/paperclipai/paperclip/blob/904c01d1a3a16de817792432d5d5a24f6e4bde12/CONTRIBUTING.md) require dedup, the source PR template, model-use disclosure, tests, and pre-coordination on Discord for larger core work; **no Discord contact was made**. CLA or human-attestation exemptions are **NOT VERIFIED** and are not assumed.
- [Matched fork](https://github.com/opensiro-contributions/paperclip) is verified to originate from `paperclipai/paperclip`; current [fork owner state](https://github.com/opensiro-contributions/paperclip/blob/opensiro/meta/.opensiro/state.json) was **ACTIVE / ALLOW** at 2026-11-17 15:11 UTC. This is not consent to publish a fork-local PR or contact Paperclip maintainers. Re-read controls before any future effectful step.
- External-publication approval for this receipt, any architecture issue, comment, fork-local public PR or external PR: **NOT GRANTED**. This receipt creates none.

## Existing work / overlap

| Function/need | Evidence | Observed status | Boundary |
| --- | --- | --- | --- |
| S4 model-release compatibility and upgrade choices | [Original issue #20848](https://github.com/paperclipai/paperclip/issues/20848) | **OPEN, issue only** | Proposes opt-in detection, capability-aware recommendation, authorization, canary/rollback; not shipped |
| S3/S4 adaptive subscription and CEO budget feedback | [Original issue #3406](https://github.com/paperclipai/paperclip/issues/3406) | **OPEN, issue only** | Current usage/threshold handling versus proposed future operating alternatives need separation |
| S3 scheduled resource admission | [Original issue #16504](https://github.com/paperclipai/paperclip/issues/16504) and [PR #13379](https://github.com/paperclipai/paperclip/pull/13379) | **Issue OPEN, PR OPEN / UNMERGED** (head `43b61148378cc045ff0eda5ad0f5b754c496b4be`) | Deferral under exhausted subscription is not itself prospective adaptation |
| AI account selection extension | [PR #14967](https://github.com/paperclipai/paperclip/pull/14967), [issue #16954](https://github.com/paperclipai/paperclip/issues/16954) | **PR MERGED**; **OSS reference router issue OPEN** | Host `ai.connections.route` is shipped; learned cooldown/Cloud policy not credited as a first-party S4 actor |
| S5 board decision-source identity | [Issue #18296](https://github.com/paperclipai/paperclip/issues/18296), [PR #17857](https://github.com/paperclipai/paperclip/pull/17857) | **Issue OPEN, PR OPEN / UNMERGED** (head `b6cd49d4b6926fae61a2c68a31ce7c659b69eaa6`) | Approval audit/source and budget control may be valuable, but generic approval is not a new S5 grade |
| S3* review-stage recovery | [PR #15265](https://github.com/paperclipai/paperclip/pull/15265) | **OPEN / UNMERGED** (head `28183072c57ef8f035a0851aed2e03f4df9b7f77`) | Existing optional distinct-reviewer mode is already `S3*=A`; don't duplicate it |
| Independent OpenSiro research | [S3/S4 resource research](https://github.com/opensiro-contributions/paperclip/blob/opensiro/meta/.opensiro/contributions/paperclip-s3-s4-adaptive-resource-feedback.json), [S5 decision source](https://github.com/opensiro-contributions/paperclip/blob/opensiro/meta/.opensiro/contributions/paperclip-s5-approval-decision-source.json), [S5 strategic authority](https://github.com/opensiro-contributions/paperclip/blob/opensiro/meta/.opensiro/contributions/paperclip-s5-strategy-approval-authority.json) | Existing separate fork-local **RESEARCH**, not shipped code or accepted Index evidence | Reuse these records, don't manufacture a fourth contribution simply for this roadmap |

**Dedup limit:** The list above is a dated census of related original issues/PR heads and fork-local records, not a claim that every competing diff/test has been exhaustively evaluated. Before any implementation, re-read exact current code and heads, assess native behavior and maintainer decisions; do not duplicate an accepted PR or prescribe a controller from the `S4=—` label.

## Function ownership

- **S1=A:** first-party report agents autonomously checkout and execute assigned work, return results and affect subsequent tasks via the Paperclip heartbeat contract.
- **S2=A:** CEO/managers choose allocation/dependency/unblocking outcomes among distinct report-agent units, while deterministic single checkout and blockers enforce the decision; status feeds back into later wakes.
- **S3=A(P):** model-driven managers own current company resource/priority intervention in one mode; board users independently retain effective override over budget, assignments and agent state in another. These are separate operational arrangements.
- **S3*=A:** an optional first-party execution policy assigns a distinct non-executor reviewer who judges the claim and returns approval or change request into next task state.
- **S4=—:** pinned first-party evals, saved skills, routines, optional memories and model connection routing don't demonstrate a distinct external/future sensing → adaptation options → authorized choice → modified operating capability loop. [Self-Organization and Automatic Organizational Learning](https://github.com/paperclipai/paperclip/blob/7f9867895c4e7e9589b233a93aa9efceb0c992d0/ROADMAP.md) remain planned; no invented grade for an issue/open PR/plugin.
- **S5=P:** first-party company board approves or rejects purpose/CEO strategy and its decision returns to executable work; the ultimate policy owner is legitimately human/parent. **P can be the final desired mode**, not a deficiency.

## Capability priority

**P0 — optional model-release adaptation closure, conditional on the actual native gap.** Hypothetical actor: operator responsible for a Paperclip company's future model portfolio. Disturbance: announced changes to model availability, API, price or capability. Candidate user outcome: receive a compatible, evidence-ranked option, approve or reject a future-run-only configuration update, optionally canary/rollback, and later observe whether the chosen setting was applied. Start from [existing issue #20848](https://github.com/paperclipai/paperclip/issues/20848); inspect product and PR overlap before offering new code. This is a **proposed S4-specific first-party constructor**, not current `S4=C`.

**P1 — current capacity-to-future policy feedback without duplicating quota admission.** Actor: CEO/board/operator managing several agents. A scheduled/subscription demand trend changes future run feasibility; the user needs alternatives with a real decision owner and verification on subsequent runs, not merely a reactive 429 handler. First compare shipped gateway resource management and [#3406](https://github.com/paperclipai/paperclip/issues/3406), [#16504](https://github.com/paperclipai/paperclip/issues/16504), [#13379](https://github.com/paperclipai/paperclip/pull/13379) and [#15791](https://github.com/paperclipai/paperclip/pull/15791). If a simpler native scheduling tweak closes the task, prefer it.

**P1 — reserved strategic approval-authority boundary, not a new S5 grade.** Actor: company board establishing legitimate authorities for CEO strategy changes. Hypothesis: per-company named principals/channels and enforcement provide a material new ability beyond approval provenance. Check whether the operator can designate who is entitled to approve a **strategy-level** decision and whether the resulting policy actually prevents unauthorized approval across supported entry points. Existing [fork RFC](https://github.com/opensiro-contributions/paperclip/blob/opensiro/meta/.opensiro/proposals/paperclip-s5-strategy-approval-authority.md) and [issue #18296](https://github.com/paperclipai/paperclip/issues/18296) already cover parts; avoid a duplicate issue. Routine execution approvals are not automatically S5.

**P2 — integration guardrails only.** Any new S3/S4 constructor must respect existing S2 single-owner/blocker semantics, S3* independent review and board S5 reserved decisions; do not require six additional subsystems or force `C → C(P) → A(P)`. The optional parent variants require independent first-party closure and separate Index review after shipping.

### P0 proposed S4 constructor — implementation-ready acceptance conditions

The specific **proposed first-party S4 constructor** is now written as a separate, reviewable [Paperclip S4=C construction and acceptance contract](paperclip-s4-constructor-acceptance-20261117.md). It is a **hypothesis and engineering target**, not a shipped feature or a changed Index grade. The contract pins the accepted evidence, explicit S4 decision/feedback owner, a five-port minimum design and ten falsifiable acceptance scenarios (`AC-01`–`AC-10`).

**Required minimum before calling a future implementation a candidate `C`:** a source-attributed external/future model-change signal → durable comparison of `hold` versus `candidate` against actual current S3 capability → first-party **S4-specific** decision port into which a developer can compose an autonomous evaluator/agent with bounded authority → authorized **future-run-only** configuration/capability revision → receipt from subsequent actual agent operation returning success or denial into S3. Include a working actor-composition example, unauthorized/unknown-compatibility/rollback negative tests, first-party reachability and existing-simpler-native comparison. A release notification, model catalog, optional generic plugin hook or human-only approval **fails** the autonomous constructor witness.

**Grade gate:** `C` requires subsequent first-party shipping and an independent source-pinned Index assessment under Skills; `P` remains a valid human-only S4 possibility if separately established. `C(P)` requires two independent mode witnesses and is not the target by default. Existing `S4=—` remains canonical.
**Preimplementation test of materiality:** for each candidate, state actor, exact currently impossible/awkward task, best native workaround, measurable output, right owner, enforcement, trace of decision to later execution, and overlap. If a shipped path already closes the task, report `NO_USEFUL_CHANGE` for that idea.

## Implementation options

1. **First, plan-only/source validation:** trace current Paperclip code and exact issue/PR head/diff for P0; use existing issue #20848 instead of posting a duplicate. A roadmap is complete without source changes.
2. **Small product-native change only if qualified:** opt-in notification, compatibility/decision witness and future-run-only application, preferably first-party plugin or extension route if technically sufficient and admissible; do not bypass board authority, security and existing review stages. Route any actual implementation through standard `upstream upgrade`, a single stable contribution ID per independently useful change, native tests, disclosure and public-publication approval.
3. **Simpler alternative first:** manual release notification + a documented operator config change or a small scheduled check, with no new VSM-specific API if it meets the same user need.
4. **No change:** a credible final disposition if existing code/PRs solve it or product demand is not supported.

## Specification and domain alternatives

- **Profile feedback:** if the evidence exposes a genuine ambiguity about outside-and-future feedback, owner boundary, parent mode or recursion, propose a separately governed semantic question to [Profile](https://github.com/opensiro/vsm-harness-profile); do not alter its semantics in Upstream.
- **Skills feedback:** if current source exposes an actual ambiguity about `C` evidence or negative-state adjudication, propose a separate method-calibration issue/PR to [Skills](https://github.com/opensiro/vsm-harness-skills); do not edit accepted Index grades directly.
- **Optional domain-specific fork:** only if lawful and operator-approved, isolate a model-portfolio adaptation experiment within the matched Paperclip fork; specify first-party vs added actor and compare a simpler native mode. No product-branch change or fork PR was created here.

## Cost experiment

- Matched task: an external model provider releases a materially changed model while a multi-agent Paperclip company needs to decide whether and how to upgrade its agents without affecting unauthorized live sessions.
- Native baseline: existing model configuration, operator research and manual change (or small native notification feature).
- VSM-informed variant: bounded function-specific external-signal/option/authorization/feedback constructor with the same supported input, operator, acceptance criteria and future-run execution semantics.
- Measure: total engineering hours, onboarding/integration, review/CI and native test effort, observed task completion/correct authority/rollback behavior, code surface and subsequent maintenance/regression cost; repeat on comparable tasks before making a cost claim.
- Cost status: NOT_MEASURED
- No demonstrated lower cost, productivity gain, added VSM grade, original maintainer endorsement or deployment benefit is claimed.

## Delivery and publication

- Result: PLAN_ONLY
- External issue: DRAFT — NOT PUBLISHED
- Accepted Index source: https://github.com/opensiro/vsm-harness-index/blob/975a58814b767cfca414c152480f787bfe80944b/assessments/pa/paperclip.md
- This is a dated **internal Upstream non-authoritative receipt**, with a new same-day accepted Index assessment rather than the old two-month assessment.
- New external original issue/comment/PR, public fork-local review PR, Discord message, source-code change, fork-local contribution record, Index grade change, Profile/Skills change, experiment result or cost claim: **NONE**.
- Only a separate exact current-conversation approval can authorize any later third-party public communication or fork review.
