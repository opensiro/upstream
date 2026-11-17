# Capability Roadmap — architecture-first, plan-only

[Protocol](../PROTOCOL.md#architecture-first-upstream-roadmap-ownerrepo-plan-only) · [issue template](../templates/EXTERNAL_ARCHITECTURE_ISSUE.md)

## Purpose

This route tests whether reusable organizational specifications and source-native contributions reduce AI harness engineering effort. **VSM is a working reference hypothesis**, not a required implementation or confirmed cost advantage. The output is a **decision-ready plan**, potentially with zero code and no external publication.

The normative [Profile](https://github.com/opensiro/vsm-harness-profile/blob/main/PROFILE.md) owns function semantics; [Skills](https://github.com/opensiro/vsm-harness-skills) owns grade/methodology; [Index](https://github.com/opensiro/vsm-harness-index) owns accepted assessments. Upstream does not overwrite their authority.

## Procedure

1. **Source and authority pins:** Named original repository; exact current default HEAD; observation time; legal license/contributor/AI policy and autonomy preflight; accepted Index assessment URL *and file blob SHA*, historical review date/ref; explicitly label pending reassessments as unaccepted. Declare system-in-focus and excluded recursion. If a verified fork is relevant read original parent and `opensiro/meta` owner controls before writes.
   - **Assessment freshness advisory:** Compute age in calendar days at the observation date from the latest accepted successful Index semantic review (`reviewed_at`, or a later successfully supported `last_checked_at`; do not credit informal source inspection). If older than **30 days**, **recommend an Index-owned, source-pinned re-assessment before relying on the historical vector for architectural conclusions**. Materially changed current behavior can justify the recommendation sooner. Cite the exact canonical assessment, date, current source HEAD and any live reassessment issue/PR. This recommendation is **not** a periodic reassessment mandate, universal Index policy, automated queue write, grade change or roadmap block. If re-assessment is pending or not feasible, continue **plan-only with provisional claims**, old assessment explicitly historical, and source-native evidence controlling current functionality. An open or unmerged proposal is not accepted freshness.
2. **Native work census:** For relevant S1/S2/S3/S3*/S4/S5, inspect current shipped code; exact original issue and PR state/head/diff and maintainer decision; existing OpenSiro fork work; competing original alternatives. Distinguish `SHIPPED`, `OPEN_PR`, `ISSUE_ONLY`, `EXPERIMENT`, `EXTERNAL_GOVERNANCE` and `UNVERIFIED` as *report labels only*, not stored metadata enums.
3. **Function-specific residual gap:** Name real actor → trigger → decision/action → observable result; actual disturbance; decisive right and owner; enforcement/transport; feedback into subsequent operation. Write `current main → competing proposal → remaining task`, overlap/alternative, uncertainty. No conclusion from a low Index grade or an issue title alone.
4. **Composability-first option:** Favor supported first-party, function-specific constructors where maintainers need them; only a shipped/composable closure can establish `C` in a later Index assessment. A `C` **implementation target** must carry a source-native constructor/acceptance contract: precise user counterfactual, environmental/operational stimulus, function-specific first-party decision/feedback port (not generic hooks), an explicitly composable autonomous decision actor and authority boundary, proposed option/state lifecycle, closure into subsequent operation, exact tests including rejection/absence and compatibility, and proof of distribution reachability. Without those details call the case `NEEDS_EVIDENCE`, not an implementation-ready `C` roadmap. `C(P)` and `A(P)` are optional, independently demonstrated modes **only for S3/S4/S5**, not a mandated grade progression. `P` alone is a valid intentional goal; S1/S2/S3* have no published parent mode. Always prefer a simpler native design when appropriate.
5. **Independent maintainer choices:** (a) original-native code/PR work, with existing Upgrade gates and separate independent contribution record per real improvement; (b) normative semantic feedback to Profile or separate Skills method/assessment improvement; (c) permitted experimental domain fork with declared boundary. Neither a spec issue nor a fork creates original maintainer obligations.
6. **Matched cost experiment:** Predeclare equivalent native vs VSM-informed user tasks and measure total implementation, integration, review/test, maintenance/regression effort and output quality. Report `NOT_MEASURED` until data exist. Never claim proven cheaper or performance superiority from a diagram.
7. **Handoff:** Produce [Capability Roadmap Receipt](#capability-roadmap-receipt) and optional [external architecture issue](../templates/EXTERNAL_ARCHITECTURE_ISSUE.md) with exact source links; keep `DRAFT — NOT PUBLISHED` until separate current owner consent for the exact destination/full text/diff. Plan-only ends even with zero code, zero PR, or no qualified improvement.

## Explicit implementation follow-up (not part of PLAN_ONLY)

A bare `upstream roadmap OWNER/REPO` request stops at a source-linked proposal without product edits. When the owner **separately requests implementation of this roadmap/constructor contract, including a fork-local review PR**, it activates the already-defined [full-cycle Upgrade handoff](../PROTOCOL.md#roadmap--implementation-handoff-explicit-execution-intent) for that **same original**. The previous roadmap's `PLAN_ONLY` label describes the *past stage*, not a veto on new implementation intent.

A qualified `C` constructor is **not delivered** by the contract, code sample, fake completion tests or a generic plugin extension. Carry the smallest first-party path from disturbance and proposed options through real developer-composed decision owner, enforced authority, next-operation application and observation. Test the original-native capability delta and contract acceptance cases. Stage implementation/test code on the verified `opensiro-contributions` fork's product branch; keep schema-v2 evidence on `opensiro/meta` only. Prepare original-template PR diff and five-link handoff. A public fork-local PR itself still needs **separate exact current-conversation approval of its destination, action, full title/body and diff**; no blanket authorization is inferred from "implement". If that gate remains unapproved, report the tested branch plus `READY_FOR_FORK_LOCAL_PR_APPROVAL — NOT PUBLISHED` rather than falsely marking a PR complete. No external original publication or grade upgrade follows automatically.

If the native delta or a true S4/S3/etc decision/closure witness is not established, say `NO_MATERIAL_DELTA` or `IMPLEMENTATION_BLOCKED` with source-backed reasons, and do not add a fake first-party controller to fill a grade.

## Capability Roadmap Receipt

A compact, **read-only Markdown report** in chat, or a dated **non-authoritative example**. Do not create another issue/PR queue or a fork-local contribution ID just for a proposal. Required evidence sections:

| Section | Required contents |
| --- | --- |
| Identity | Original and HEAD SHA/date; boundary/recursion; pinned accepted Index assessment SHA, review date/ref and Profile/Skills refs; last successful review/check date, age in days and any proposed re-assessment link (provisional when pending) |
| Permission | License/contributor/CLA/AI policy, allowed paths and any actual fork owner state; no inferred write |
| Existing work | Original and fork issue/PR URLs, true open/merged status and head/diff evidence, shipped/proposed distinction |
| VSM witness | Function, disturbance, real decision/feedback owner/right, enabling first-party primitives and return-to-operation |
| Proposed capability | Actor/output and native alternative, meaningful constructor path, dependencies and small acceptance cases |
| Constructor target (when proposing `C`) | Function-specific first-party ports and distribution reachability; what a developer must compose (real autonomous decision actor/authority), option/state lifecycle, controlled return into future operation, negative cases and reproducible end-to-end acceptance. Explicitly distinguish proposed from shipped `C`. |
| Optional paths | Product-native code, Profile or Skills feedback, permitted domain-specific fork |
| Cost check | Paired native/VSM-informed task, all-in measures and observed values, else `NOT_MEASURED` |
| Delivery | `PLAN_ONLY`, `NEEDS_EVIDENCE` or `NO_USEFUL_CHANGE` as narrative outcomes only; external issue marked `DRAFT — NOT PUBLISHED` |

**Fail closed:** unknown source/ref/owner/diff or assessment freshness stays unverified. A >30-day historical assessment prompts a recommended re-review, not a hard stop, automatic Index write, or silent promotion of a pending reassessment. An Issue or open PR does not certify shipped capability, a planned `C` is not an Index `C`, and a maintained project policy is not automatic runtime S5.

For an implementation-oriented `C` target, see the [Paperclip S4=C proposed construction and acceptance contract](examples/paperclip-s4-constructor-acceptance-20261117.md) for a concrete (still plan-only) first-party interface/ownership/feedback design and falsifiable test matrix. The example demonstrates required specificity, not a changed Index grade or a mandatory VSM architecture.

## Optional structural receipt check

The source-native receipt stays **read-only documentation**, not a fork-local JSON state or an Index assessment. For a dated Markdown case note, run:

~~~sh
python3 scripts/validate_capability_roadmap.py docs/examples/browser-harness-roadmap-20261117.md
~~~

The validator checks presence of pinned SHA/date fields, required receipt sections, an evidence link and explicit non-publication/cost status. **It does not read live GitHub, verify legal permissions, prove VSM function closure or certify lower cost.** Exact current GitHub readback and semantic review remain mandatory before any subsequent action.

## Ownership and stages

- The roadmap is **not** an Index reassessment, normative Profile patch or second canonical ledger.
- Existing single-harness `upstream upgrade` remains the implementation route, with material capability-delta, native tests, v2 provenance, verified matching fork and separate exact public approvals.
- Fork-local `.opensiro/contributions/<id>.json` remains **one independently implemented improvement**, on the separate `opensiro/meta` branch; a roadmap may link existing records without manufacturing a new case.
- A public original issue, comment or PR is a separate external interaction and needs a complete exact approval in the current conversation. A plan-only route has **no automatic publication**.
