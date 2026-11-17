# [PROJECT] — capability integration roadmap for [operator outcome]

<!--
Opensiro working-fork GitHub Issue template, v2 (source-neutral).
Replace all bracketed placeholders and remove these instructions before publication.
For opensiro-contributions/<fork> only, NOT the original maintainer repository.
Source-native case evidence belongs at opensiro/meta:.opensiro/issues/<case-id>/.
A public fork GitHub Issue requires its own exact current-conversation approval.
-->

**Status:** PLAN_ONLY / [NEEDS_EVIDENCE | DECISION_READY | NO_USEFUL_CHANGE]
**Working fork:** [verified opensiro-contributions/<fork> URL]
**Case artifacts:** [.opensiro/issues/<case-id>/ on opensiro/meta]

## 1. Goal

Opensiro is investigating whether reusable organizational specifications informed by the Viable System Model (VSM) can **standardize and reduce the total cost of developing AI-agent harnesses**. Cost reduction and improved outcomes are hypotheses, not proven results. No project is required to adopt VSM or implement six new subsystems.

**User/operator outcome:** [Name the actor, task and measurable benefit over the simplest project-native alternative.]

**Roadmap design objective:** for useful VSM functions that lack a **confirmed `C` or `A`** construction/ownership path at the declared boundary, find the **smallest source-native, evidence-backed set of changes sufficient to offer a real `C` constructor**. This is a target for analysis, not a promised implementation or assessment grade. Already-confirmed `A`/`A(P)` functions are **not mandatory `C` targets**; `C`/`C(P)` already meet the constructor objective. A legitimate `P` authority remains legitimate and may be the intentional end state. An unresolved `?` must be investigated before declaring a gap.

## 2. Evidence baseline

- **Original repository / current default HEAD:** [owner/repo at immutable commit SHA; observed date].
- **Accepted Index assessment:** [immutable assessment file/blob SHA, `review_ref`, review date, Profile and Skills versions]. This is a **historical source-relative observation**, never an automatic current grade.
- **Freshness:** [days since successful Index semantic review; recommend Index-owned re-assessment if over 30 days or current changes materially affect the mapping; otherwise mark provisional unknowns].
- **Working fork and owner state:** [verified parent, opensiro/meta HEAD, current ACTIVE/PAUSE/STOP and ALLOW control; unknown => no write].
- **System in focus:** [operating boundary and supported first-party mode; excluded recursion, uninstalled plugins and private services].
- **License / contributor permissions:** [verified policy links, CLA, AI disclosure, allowed contribution route; note blockers].

## 3. Existing work and remaining gaps

Map **shipped** code separately from **open/unmerged** PRs, Issues, experiments and external governance. Inspect relevant original source and competing PR heads/diffs; a historical low grade or proposal title does not prove a missing current capability.

| VSM function / user need | Shipped first-party path and source link | Existing original Issues/PRs and live statuses | Concrete residual operator outcome |
| --- | --- | --- | --- |
| [Sx / actor → task] | [source and behavior] | [URL, OPEN/MERGED and PR head/diff if applicable] | [gap or already achieved] |
| [second relevant need, or remove row] | [link] | [link or none found] | [gap / none] |

**Best original-native alternative:** [Existing feature or documented manual/small-change workflow; say if it is already sufficient.]

## 4. VSM capability targets and prioritized development plan

**Target matrix (required):** list the relevant VSM functions, including **excluded already-autonomous functions** when they matter to the proposal. Do not infer `C` from `A`—the two are distinct ownership arrangements. We only exclude `A` from *mandatory C engineering work*.

| Function | Accepted historical state | Current first-party evidence / uncertainty | Construction target | Minimum set of source-native changes | Sufficiency / verification status |
| --- | --- | --- | --- | --- | --- |
| [Sx without verified C or A] | [— / ? / P] | [actual source evidence] | [`C` when materially useful; otherwise no change with reason] | [existing Issue/PR + exact missing first-party ports and integration] | [NEEDS_EVIDENCE / CONTRACT_READY; never VERIFIED_C merely from a plan] |
| [Sx already at A / A(P) / C / C(P)] | [actual state] | [actual source evidence] | [No mandatory C target] | [none; constraints/dependencies only if relevant] | [existing assessment remains historical] |

**Prioritization rule (research priority, not an autonomy-grade ladder):**
- **P0 — useful C sufficiency target(s):** prioritize a *material, verifiable operator outcome* with the smallest defensible missing construction path, strongest reuse of source-native Issues/PRs, and reasonable implementation/integration cost. If no eligible target is justified, say `NEEDS_EVIDENCE` or `NO_USEFUL_CHANGE` instead of fabricating one.
- **P1 — necessary enabling work:** dependencies, compatible integrations, authority enforcement and tests **required for P0 closure**; some prerequisites execute before the P0 deliverable. Name their issue/PR links and owners. P1 can also identify separately justified native work, but it is not an obligatory extra function target.
- **P2 — optional improvements:** independent parent modes `C(P)`/`A(P)` (where applicable and separately proven), refinements and cost optimizations. Neither `C → C(P) → A(P)` nor `A → C` is a mandatory progression.

**Ordered integration / dependencies:**

| Priority | User capability / deliverable | Reuse and missing change | Depends on | Decision owner, rights and measurable acceptance |
| --- | --- | --- | --- | --- |
| P0 | [candidate C construction and user outcome] | [native links + required delta] | [P1 prerequisites / none] | [first-party functional owner + positive and negative closure] |
| P1 | [required supporting integration] | [code/issues/PRs and gap] | [other constraints] | [compatibility/authority outcome] |
| P2 (optional) | [additional mode/optimization] | [smallest useful change] | [P0 proof where relevant] | [independent acceptance] |

**C sufficiency contract (required for each proposed C target):** link [case-local constructor-acceptance.md], specifying (1) a real VSM-specific disturbance and operator counterfactual, (2) first-party function-specific input/option/decision and durable state ports **rather than generic hooks**, (3) what a developer independently composes, including an **actual autonomous decision actor** and legitimate rights, (4) enforcement, fail-closed denials and future-operation feedback/closure, (5) supported distribution/mode reachability and (6) native end-to-end positive, negative, unauthorized and compatibility tests. State explicitly which existing PRs/Issues cover each element and which new changes are required.

**Sufficiency verdict:** [complete *design* coverage / missing evidence / disproved] with links for every dependency. **Design completeness is not shipping, and shipping is not an accepted Index `C` without separate Index review.** For `P` preserve legitimate parent authority; for `A(P)` exclude mandatory C work but retain constraints. `A`, `C`, `P` are ownership arrangements, not performance or maturity grades.

## 5. Acceptance, alternatives and stop conditions

| Gate | Evidence required | Negative / stop condition |
| --- | --- | --- |
| Existing-work and material-delta check | Current original HEAD plus exact competing Issue/PR evidence; new user action unavailable or materially better than native baseline | Native workaround or shipped solution already covers it => NO_USEFUL_CHANGE |
| Positive operator scenario | [actor → stimulus → legitimate autonomous/composed decision → enforced first-party result and next-operation receipt] | A notification/UI mock or standalone generic plugin cannot establish C |
| Negative/authority case | [non-delegated actor, stale/unknown input, incompatible configuration, unavailable owner => safe denial and observable feedback] | No enforced owner/feedback or bypassable protected decision => NEEDS_EVIDENCE / blocked |
| Constructor completeness | [ports, actual developer composition, authority, distribution and native tests from case contract] | A proposal/open PR is not shipped C; no automatic Index grade |
| Native alternative | [paired simple native task and comparable outcome] | Smaller project-native solution wins; do not build solely to fill a VSM grade |

## 6. Independent development paths

These are **independent choices**, not three compulsory tasks:
1. **Harness-native integration:** organize original Issues/PRs; if qualified and separately authorized, implement a narrow tested improvement via `upstream upgrade`.
2. **Methodology feedback:** bring evidence-backed semantic counterexamples to [VSM Profile](https://github.com/opensiro/vsm-harness-profile) or assessment-method concerns to [VSM Skills](https://github.com/opensiro/vsm-harness-skills).
3. **Scoped experiment:** compare a legally permitted domain fork with a simpler original-native approach; no maintainer adoption implied.

**Selected research path / next decision:** [choose independent branch(es), state what is blocked].

## 7. Value evaluation

**Matched task:** [the same operator input, permitted decisions and outcome with native/manual vs VSM-informed alternative].

**Measures:** end-to-end user result, implementation/integration time, review and negative-case tests, maintenance/regression burden, operational compatibility and failure modes. **Cost status: `NOT_MEASURED`** until independently observed. Never assert guaranteed cost savings from a proposed constructor.

## 8. Decision and handoff

**Result:** `PLAN_ONLY / [NEEDS_EVIDENCE | DECISION_READY | NO_USEFUL_CHANGE]` (report disposition only, not fork metadata enums).

**Priority decision:** [P0 nominated functions, excluded already-A/C functions, prerequisite order and sufficiency gaps].

**Next action:** [exact current-source investigation or a separately requested Upgrade]. This Issue is **Opensiro's fork-local discussion surface**, not an original maintainer request. Store detailed evidence, original Issue deduplication, constructor contract and any third-party draft in the verified fork's `.opensiro/issues/<case-id>/` on its separate `opensiro/meta` branch.

No public fork Issue, original Issue/comment/PR, product implementation, fork-local public review PR, delegated authority, automatic Index regrade or implicit cross-owner GitHub Issue transfer is authorized by this draft. **Each public publication requires its own exact current-conversation owner approval.** Existing original Issues must be reused rather than duplicated.

**AI disclosure:** Prepared with AI assistance. No independent human validation, shipped constructor, accepted grade change or measured cost saving is implied.
