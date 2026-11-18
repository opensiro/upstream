# Capability Roadmap — architecture-first, plan-only

[Protocol](../PROTOCOL.md#architecture-first-upstream-roadmap-ownerrepo-plan-only) · [fork-local roadmap Issue template](../templates/FORK_CAPABILITY_ROADMAP_ISSUE.md) · [external architecture Issue template](../templates/EXTERNAL_ARCHITECTURE_ISSUE.md)

## Purpose

This route tests whether reusable organizational specifications and source-native contributions reduce AI harness engineering effort. **VSM is a working reference hypothesis**, not a required implementation or confirmed cost advantage. The output is a **decision-ready plan**, potentially with zero code and no external publication.

The normative [Profile](https://github.com/opensiro/vsm-harness-profile/blob/main/PROFILE.md) owns function semantics; [Skills](https://github.com/opensiro/vsm-harness-skills) owns grade/methodology; [Index](https://github.com/opensiro/vsm-harness-index) owns accepted assessments. Upstream does not overwrite their authority.

## Two-level case presentation: Human first, AI second

**Reusable artifacts:** [Human Issue template](../templates/FORK_CAPABILITY_ROADMAP_ISSUE.md) and [AI/developer technical contract template](../templates/ROADMAP_AI_CONSTRUCTOR_CONTRACT.md). Fill these with source-native evidence in the same fork-local case folder.

**The human-facing Issue is the entry point**, not the condensed tail of the technical design. Its first substantive content MUST follow this order:

1. **Why Opensiro:** Opensiro tests whether VSM-informed reusable specifications and source-native integrations can **standardize and lower the engineering cost of AI-agent harnesses**. Cost reduction is an unmeasured hypothesis; maintainers are not obliged to adopt VSM.
2. **Central accepted Index assessment:** a prominent complete **`S1/S2/S3/S3*/S4/S5`** vector and compact **six-function table** showing ownership state, meaning and assessment consequence, linked to the accepted assessment, `review_ref`, date, Profile/Skills versions. This is the **historical starting point** of reasoning, not proposed after-state. Never invent missing states; use explicit `?`/`UNVERIFIED` when absent.
3. **Human decision:** operator outcome and counterfactual, original-native alternatives/Issues/PRs, prioritized target vs dependencies vs optional work (`P0/P1/P2`), materiality, stop and no-publication gates, direct link to the AI companion.

Keep this a **short human decision surface**. Do not put the full constructor API specification, source map, multi-step implementation recipe or extended test matrix inline. Put these in **one case-local linked AI/developer contract**, preserving the exact same starting assessment/priority claims. That companion MUST own first-party code/pinned refs, current shipped-vs-proposed gap map, five-link function-specific sufficiency as appropriate, authority and ownership, `S3↔S4` interface when relevant, verifiable native tests including negatives, evidence gaps and implementation stop rules. **Two files are two audiences, not two public Issues**. Cross-link both; use the current approved fork issue template as Human reference.

An optional one-sentence status header is metadata, not the beginning of the substantive presentation. Do not lead with a proposed feature, technology name, a raw vector **without first explaining Opensiro**, or a wall of API details before the central assessment.

## Default target and work priority

**Target-first roadmap:** for relevant VSM functions without a confirmed `C`/`C(P)` or `A`/`A(P)` first-party path, investigate the **minimum source-native set of existing and proposed changes sufficient for a meaningful `C` constructor**. Use accepted Index grades only as dated evidence; inspect current source and resolve `?` before concluding a function is missing. Already-`A`/`A(P)` functions **do not need C engineering work** for this roadmap, even though `A` does not logically imply a reusable `C` interface. Already-`C`/`C(P)` functions also do not need another constructor. Parent-governed `P` is legitimate, and may be retained as the final mode when an autonomous constructor adds no user value or violates reserved authority.

**P0** is the best evidence-backed, useful function-specific *C sufficiency target*, backed by the combination of actual first-party primitives, original Issues/PRs and necessary missing changes. **P1** covers **prerequisites** for that target, including integration, authorization and tests; these dependencies may have to execute before P0 can be delivered. **P2** is independently valuable but optional: a separately evidenced `C(P)`/`A(P)` mode, refinements or optimizations. Priority is based on material user benefit, composability feasibility, reuse of existing work, dependencies and measured-or-hypothesized effort—not the lowest historical grade or a supposed `A > C > P` maturity scale.

A plan **MUST show the accepted historical state → observed source-native current state → C construction target or justified exclusion → minimum necessary integration set → sufficiency evidence/acceptance** for each relevant function. It is not sufficient to list P0/P1 ideas without specifying why the complete set could later support `C`. For any qualified C target, link a function-specific first-party constructor and positive/negative acceptance contract. A plan does not assert a shipped C; if there is no defensible useful target, `NEEDS_EVIDENCE` or `NO_USEFUL_CHANGE` is a successful **explicit** plan-only outcome. There is no compulsory implementation, new grade or maintainer adoption.

## Issue-local artifact storage and conditional original Issue

`upstream roadmap` remains `PLAN_ONLY`. An explicitly requested persistent case belongs under the verified fork's `opensiro/meta:.opensiro/issues/<case-id>/` after checking the parent repository, meta HEAD and owner control. Store case-level `roadmap.md`, `constructor-acceptance.md`, external Issue drafts and technical receipts there, **not** in central Upstream. For Opensiro discussion, use the [generic fork roadmap Issue template](../templates/FORK_CAPABILITY_ROADMAP_ISSUE.md), populated with current source-native evidence. A public fork GitHub Issue for discussing/reviewing that case requires a separate exact approval of its full title/body; a case folder alone is not a GitHub Issue. The [external architecture template](../templates/EXTERNAL_ARCHITECTURE_ISSUE.md) is a distinct maintainer-facing artifact and does not become public automatically.

Follow the [fork Issue → case evidence → original Issue route](../PROTOCOL.md#fork-github-issue--local-case--external-issue-separate-publication). Before any original Issue, dedupe the live original issue/PR set; link an existing original issue if it covers the outcome. For a new maintainer issue, request a **separate exact publication approval**, create a standalone original-native issue and read back its actual URL; store/cross-link it in the fork case. This is not GitHub native transfer across separate owners, nor automatic closure of the fork Issue. No grade change, product code implementation or public PR is implied by case publication.

**Approved two-level case example:** [Paperclip human Issue v2](https://github.com/opensiro-contributions/paperclip/blob/opensiro/meta/.opensiro/issues/capability-roadmap-issue-pilots-20261118/issue-v2.md) and [AI/developer constructor contract](https://github.com/opensiro-contributions/paperclip/blob/opensiro/meta/.opensiro/issues/capability-roadmap-issue-pilots-20261118/constructor-sufficiency-v2.md), with the accepted Index state as their shared central starting point. These are plan-only fork files, not published GitHub Issues or a current-revision grade.

**Migrated case exemplars:** [Paperclip S4 roadmap](https://github.com/opensiro-contributions/paperclip/blob/opensiro/meta/.opensiro/issues/model-release-adaptation-20261117/roadmap.md) and [acceptance contract](https://github.com/opensiro-contributions/paperclip/blob/opensiro/meta/.opensiro/issues/model-release-adaptation-20261117/constructor-acceptance.md); [Browser Harness S3 roadmap](https://github.com/opensiro-contributions/browser-harness/blob/opensiro/meta/.opensiro/issues/browser-resource-control-20261117/roadmap.md).

## Procedure

1. **Source and authority pins:** Named original repository; exact current default HEAD; observation time; legal license/contributor/AI policy and autonomy preflight; accepted Index assessment URL *and file blob SHA*, historical review date/ref; explicitly label pending reassessments as unaccepted. Declare system-in-focus and excluded recursion. If a verified fork is relevant read original parent and `opensiro/meta` owner controls before writes.
   - **Assessment freshness advisory:** Compute age in calendar days at the observation date from the latest accepted successful Index semantic review (`reviewed_at`, or a later successfully supported `last_checked_at`; do not credit informal source inspection). If older than **30 days**, **recommend an Index-owned, source-pinned re-assessment before relying on the historical vector for architectural conclusions**. Materially changed current behavior can justify the recommendation sooner. Cite the exact canonical assessment, date, current source HEAD and any live reassessment issue/PR. This recommendation is **not** a periodic reassessment mandate, universal Index policy, automated queue write, grade change or roadmap block. If re-assessment is pending or not feasible, continue **plan-only with provisional claims**, old assessment explicitly historical, and source-native evidence controlling current functionality. An open or unmerged proposal is not accepted freshness.
2. **Native work census:** For relevant S1/S2/S3/S3*/S4/S5, inspect current shipped code; exact original issue and PR state/head/diff and maintainer decision; existing OpenSiro fork work; competing original alternatives. Distinguish `SHIPPED`, `OPEN_PR`, `ISSUE_ONLY`, `EXPERIMENT`, `EXTERNAL_GOVERNANCE` and `UNVERIFIED` as *report labels only*, not stored metadata enums.
3. **Function-specific residual gap:** Name real actor → trigger → decision/action → observable result; actual disturbance; decisive right and owner; enforcement/transport; feedback into subsequent operation. Write `current main → competing proposal → remaining task`, overlap/alternative, uncertainty. No conclusion from a low Index grade or an issue title alone.
4. **C-construction target, completeness and priority:** Apply the [default target and P0/P1/P2 order](#default-target-and-work-priority) to functions lacking confirmed `C` or `A`. A qualified C implementation target **requires** source-native evidence of the exact user counterfactual, environmental/operational stimulus, first-party function-specific decision/feedback port, independently developer-composable autonomous decision actor and authority boundary, options/state lifecycle, enforcement, return-to-operation receipt, distribution reachability, and positive/negative/compatibility acceptance tests. Identify existing PR/Issue coverage vs remaining edits **and why their combined behavior would be sufficient**. Without those, call it `NEEDS_EVIDENCE`, never implementation-ready `C`. `C(P)`/`A(P)` are optional independent modes only for S3/S4/S5, not mandatory stages; a legitimate `P` can remain final. No shipped or grade assertions from plans. Prefer simpler native mechanisms whenever they meet the operator need.
5. **Independent maintainer choices:** (a) original-native code/PR work, with existing Upgrade gates and separate independent contribution record per real improvement; (b) normative semantic feedback to Profile or separate Skills method/assessment improvement; (c) permitted experimental domain fork with declared boundary. Neither a spec issue nor a fork creates original maintainer obligations.
6. **Matched cost experiment:** Predeclare equivalent native vs VSM-informed user tasks and measure total implementation, integration, review/test, maintenance/regression effort and output quality. Report `NOT_MEASURED` until data exist. Never claim proven cheaper or performance superiority from a diagram.
7. **Handoff:** Produce [Capability Roadmap Receipt](#capability-roadmap-receipt) and optional [external architecture issue](../templates/EXTERNAL_ARCHITECTURE_ISSUE.md) with exact source links; keep `DRAFT — NOT PUBLISHED` until separate current owner consent for the exact destination/full text/diff. Plan-only ends even with zero code, zero PR, or no qualified improvement.

## Explicit implementation follow-up (not part of PLAN_ONLY)

A bare `upstream roadmap OWNER/REPO` request stops at a source-linked proposal without product edits. When the owner **separately requests implementation of this roadmap/constructor contract, including a fork-local review PR**, it activates the already-defined [full-cycle Upgrade handoff](../PROTOCOL.md#roadmap--implementation-handoff-explicit-execution-intent) for that **same original**. The previous roadmap's `PLAN_ONLY` label describes the *past stage*, not a veto on new implementation intent.

A qualified `C` constructor is **not delivered** by the contract, code sample, fake completion tests or a generic plugin extension. Carry the smallest first-party path from disturbance and proposed options through real developer-composed decision owner, enforced authority, next-operation application and observation. Test the original-native capability delta and contract acceptance cases. Stage implementation/test code on the verified `opensiro-contributions` fork's product branch; keep schema-v2 evidence on `opensiro/meta` only. Prepare original-template PR diff and five-link handoff. A public fork-local PR itself still needs **separate exact current-conversation approval of its destination, action, full title/body and diff**; no blanket authorization is inferred from "implement". If that gate remains unapproved, report the tested branch plus `READY_FOR_FORK_LOCAL_PR_APPROVAL — NOT PUBLISHED` rather than falsely marking a PR complete. No external original publication or grade upgrade follows automatically.

If the native delta or a true S4/S3/etc decision/closure witness is not established, say `NO_MATERIAL_DELTA` or `IMPLEMENTATION_BLOCKED` with source-backed reasons, and do not add a fake first-party controller to fill a grade.

## Capability Roadmap Receipt

A compact **plan-only Markdown report** in chat, or a dated **case record in the verified fork's `.opensiro/issues/<case-id>/`** when persistent storage is requested and authorized. Do not create an Upstream queue or an implementation contribution ID merely for the proposal. Required evidence sections:

| Section | Required contents |
| --- | --- |
| Identity | Original and HEAD SHA/date; boundary/recursion; pinned accepted Index assessment SHA, review date/ref and Profile/Skills refs; last successful review/check date, age in days and any proposed re-assessment link (provisional when pending) |
| Human-first presentation | Why Opensiro → complete central accepted six-system VSM baseline (historical grades/meaning/provenance) → prioritized human decision and explicit link to separate AI/developer construction contract; no bulky technical appendix embedded in the Issue |
| AI companion | Linked case-local source-to-constructor evidence, current shipped/proposed gaps, owner and authority/feedback chain, native acceptance/negative tests; mirrors the human baseline and priorities |
| Permission | License/contributor/CLA/AI policy, allowed paths and any actual fork owner state; no inferred write |
| Existing work | Original and fork issue/PR URLs, true open/merged status and head/diff evidence, shipped/proposed distinction |
| VSM witness | Function, disturbance, real decision/feedback owner/right, enabling first-party primitives and return-to-operation |
| Proposed capability | Actor/output and native alternative, meaningful constructor path, dependencies and small acceptance cases |
| Target matrix and work priority | Relevant functions: accepted historical state, current source witness, `C` target or justified exclusion (already `A`/`A(P)` or `C`/`C(P)`), P0 capability, P1 necessary dependencies, P2 optional modes, and why the proposed *full change set* is sufficient for the C target or explicitly blocked |
| Constructor sufficiency (for each qualified `C` target) | Function-specific first-party ports and distribution reachability; what a developer must compose (real autonomous decision actor/authority), option/state lifecycle, controlled return into future operation, negative cases and reproducible end-to-end acceptance. Explicitly distinguish proposed from shipped `C`. |
| Optional paths | Product-native code, Profile or Skills feedback, permitted domain-specific fork |
| Cost check | Paired native/VSM-informed task, all-in measures and observed values, else `NOT_MEASURED` |
| Delivery | `PLAN_ONLY`, `NEEDS_EVIDENCE` or `NO_USEFUL_CHANGE` as narrative outcomes only; external issue marked `DRAFT — NOT PUBLISHED` |

**Fail closed:** unknown source/ref/owner/diff or assessment freshness stays unverified. A >30-day historical assessment prompts a recommended re-review, not a hard stop, automatic Index write, or silent promotion of a pending reassessment. An Issue or open PR does not certify shipped capability, a planned `C` is not an Index `C`, and a maintained project policy is not automatic runtime S5.

For an implementation-oriented `C` target, see the [Paperclip S4=C proposed construction and acceptance contract](https://github.com/opensiro-contributions/paperclip/blob/opensiro/meta/.opensiro/issues/model-release-adaptation-20261117/constructor-acceptance.md) for a concrete (still plan-only) first-party interface/ownership/feedback design and falsifiable test matrix. The example demonstrates required specificity, not a changed Index grade or a mandatory VSM architecture.

## Optional structural receipt check

The source-native receipt remains **PLAN_ONLY evidence in the fork metadata worktree**, not an implementation contribution, a public Issue, a fork-local review PR or Index assessment. For a dated Markdown case note, run:

~~~sh
python3 scripts/validate_capability_roadmap.py /path/to/fork-meta/.opensiro/issues/<case-id>/roadmap.md
~~~

The validator checks presence of pinned SHA/date fields, required receipt sections, an evidence link and explicit non-publication/cost status. **It does not read live GitHub, verify legal permissions, prove VSM function closure or certify lower cost.** Exact current GitHub readback and semantic review remain mandatory before any subsequent action.

## Ownership and stages

- The roadmap is **not** an Index reassessment, normative Profile patch or second canonical ledger.
- Existing single-harness `upstream upgrade` remains the implementation route, with material capability-delta, native tests, v2 provenance, verified matching fork and separate exact public approvals.
- Fork-local `.opensiro/contributions/<id>.json` remains **one independently implemented improvement**, on the separate `opensiro/meta` branch; a roadmap may link existing records without manufacturing a new case.
- A public original issue, comment or PR is a separate external interaction and needs a complete exact approval in the current conversation. A plan-only route has **no automatic publication**.
