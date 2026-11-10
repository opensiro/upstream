# OSM autonomy-transfer design for Upstream Contributions

**Status: PROPOSED DESIGN ONLY — not a standing grant, S1 admission, host integration, or authority to mutate GitHub.**

**Separate later owner decision (2026-10-23):** the [34-case Corrective publication mandate](CORRECTIVE_PR_PUBLICATION.md) is an explicitly finite exception to the earlier human-only external Draft PR policy. It **does not activate** the broad `UPSTREAM-OSM-P1` proposal below, make this design operational, add an Organization S1 domain, or grant external maintainer merge rights. Historic proposed-stage descriptions below are retained as the original prospective design, not a denial of the dated finite exception.

This design applies the [Organization OSM Roadmap](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/ROADMAP.md) to the *candidate* Upstream Contributions operating function. The [Organization Control Plane](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/AGENT_CONTROL_PLANE.md) remains the human-facing interface; this repository owns the contribution procedure. [Upstream #6](https://github.com/opensiro/upstream/issues/6) owns the executor; [Organization #274](https://github.com/opensiro/vsm-oss-organization/issues/274) is the **unmade S5** choice about admitting a fourth S1 domain. The current bounded S1 domains remain Index, Skills and Awesome.

## Function and operating goal

- **Environment:** third-party open-source repositories, maintainer issues and policies, source changes, test suites, forks, CI, reviews and outcomes.
- **Operational transformation:** source-evidenced external need → upstream-native proposed improvement → locally verified change → reviewable contribution package → observed upstream response.
- **Local variety:** issue selection, technical scope, implementation strategy, branches, code/test iteration, ordinary recovery, and transparent source/impact reporting.
- **Residual variety:** permission or license conflicts, organizational boundary/delegation change, unapproved public external publication, and maintainer acceptance. These leave local agent discretion.
- **Feedback:** preserve issue/source pins, local commits/tests, identity and human interventions, any future upstream PR and disposition; correct the next attempt from actual response.

An agent is not autonomous because GitHub's API can write. Conversely, requiring a new human vote on every routine technical step **after a valid local mandate exists** would keep those decisive S1 choices human-owned.

## Intended staged transfer (not yet authorized)

| Stage | Agent's proposed decision rights | Human or external right retained | Current execution evidence/gate |
| --- | --- | --- | --- |
| 0. Discover/propose | Identify an upstream-native issue, check overlap and contribution policy; recommend a bounded change | Scope/identity and external rules remain binding | Read-only preview available |
| 1. Local prepare | Select implementation, create branch/commits **only in enumerated authorized working forks**, implement/test/recover, produce a reviewable diff | S5 parent retains delegation-model/organization-boundary rights; no automatic authority over personal forks | Current `prepare_contribution` still requires exact-action authorization and a trusted provider-bound host; existing adapter can only create one test file |
| 2. Complete unpublished PR package | Review source and policy, add production fix/tests as allowed, collect evidence, prepare full PR title/body and diff, verify checks | **Operator owns publication of an external PR**; DCO/CLA sign-off must be attributed to a real eligible contributor | Proposed extension only, no general patch/commit/PR-packaging executor enabled |
| 3. External submission | After a separate future delegation, may eventually be considered for publication automation | **Manual operator action now**; no publication right currently granted | `submit_external_pr` out of scope for current adapter |
| 4. External disposition | Observe maintainer feedback and propose bounded revisions; keep truthful lifecycle evidence | External maintainer solely controls acceptance/merge; operator retains undelegated contact/rights | No acceptance inferred from a prepared branch, draft, PR creation or green CI |

**Fork creation is distinct from local preparation.** Merged [Upstream PR #30](https://github.com/opensiro/upstream/pull/30) provides the branch-aware, **source-only** fork-stage adapter (superseding historical Draft #18), but the connected GitHub tools still expose no native `create_public_fork` method and no trusted exact-stage host authorization. An already-existing fork is not evidence that a new fork was created.

## Activation transaction required before any standing local-write mandate

**Authority depends on system-in-focus.** While `opensiro/upstream` is **adjacent** to the bounded Organization, a local preparation mandate for its own authorized forks can be issued by an **attributable, legitimate Upstream repository/fork owner** within those actual rights. That **does not require** admitting a fourth Organization S1 domain. A change to the bounded Organization's scope or its higher-level delegation model, however, remains a separate **Organization S5** decision under [#274](https://github.com/opensiro/vsm-oss-organization/issues/274). Neither kind of decision follows from drafting or discussing this design. Any later effective operational grant must record:

1. the **specific applicable authority owner** (local Upstream/fork owner while adjacent, or S5-delegated owner if formally admitted), an attributable issuer act, and the **exact recipient/agent execution identity**;
2. named working repositories/namespaces, upstream policy/licensing constraints, permitted paths, branches, write stages and denied actions;
3. the local decision rights transferred vs higher/external decisions retained, and whether/how DCO and other contributor attestations can be made;
4. start/end or finite term, budget/operation limits, revocation/checkpoint mechanism, and live enforcement through the connected host/provider;
5. actual decision → execution → readback/validation → recovery/return receipts, including human intervention attribution and downstream effect.

Do not treat a GitHub push permission, assistant-written issue comment, generic chat confirmation, draft hash, passing CI or an `authorize=lambda _: True` callback as grant evidence. If identity, effective grant, current rights, provider operation, policy, or source preflight is missing, **stop at the existing exact-stage gate** and report the specific missing condition. No PAT, headless runner or second Control Plane is introduced by this design.

## P1 standing-mandate decision packet (unissued)

**Proposal identifier:** `UPSTREAM-OSM-P1`. **State:** `PROPOSED_NOT_GRANTED`. This is a reviewable proposal for **local contribution autonomy**, not an operator instruction, signed delegation, host identity, or executable credential. All unset fields below are **blocking** for activation.

| Decision field | Proposed value / current evidence |
| --- | --- |
| Organizational system-in-focus | Bounded OpenSiro VSM OSS group; Upstream is currently an **adjacent candidate**, not an admitted fourth S1 domain |
| Legitimate boundary/mandate issuer | **Adjacent Upstream local P1:** authorized owner of the particular Upstream-controlled working fork(s), with a separately attributable grant (**not issued**). **Organization S5:** reserves #274 admission and any bounded-Organization delegation-model change (**not decided**). These are different rights. |
| Recipient | Agent-operated Upstream contribution role; **actual authenticated execution identity not identified** |
| Working repository allowlist | **Unset**: discoverable/writable forks are *not* automatically enrolled |
| Locally delegated discretion, after activation | Candidate investigation and bounded fix selection; own-branch creation, code/tests/docs changes, local recovery and verification; full **unpublished** external PR package |
| Disallowed operations | Submission of external PRs, unsolicited external maintainer contact, DCO/CLA assertions without attributable contributor attestation, protected/default-branch merges, destructive fork actions, permission expansion, S5 scope changes, Index/Skills canonical authority |
| Tool enforcement | **Not connected** for standing grants: stage scope, actor/repository/branch allowlist, live permission/revocation checks and readback must be implemented and evidenced first |
| Effective time, expiry, revocation | **Unset**; no perpetual grant or default approval |
| Decision proof and downstream acknowledgment | **Absent**; issuer evidence and applied recipient/host acknowledgment required before operation |
| Autonomy grade | **Not assessed**; future run evidence cannot be replaced with this proposal |

### P1 activation and acceptance conditions

- **Classify the recursion and issuer first.** When Upstream remains adjacent, the **actual owner of each participating working fork** may issue a narrowly scoped local P1 mandate without first deciding Organization #274. This owner must demonstrably control the relevant repo/fork and the delegated operations. Formal admission of Upstream to the **bounded Organization** and changes to its higher-level S1/S5 delegation model still require a separate attributable S5 decision under #274; neither is implied by a local mandate. In either case the applicable issuer must record a versioned, revocable grant, identified recipient execution actor, permitted repos/stages, and return target.
- **Host enforcement first.** The existing Control Plane must prove it can map a real connected agent execution identity and an operative mandate to GitHub write operations; check the exact grant before *every* write, repeat remote preflight at the action boundary, and reject grant expiry/revocation, wrong fork, default-branch/PR writes, branch drift and permission changes. Do not replace this with `authorize=True` or a document-derived approval.
- **Bounded first run.** Choose one real upstream-native issue, validate duplication/licensing/CLA and an explicitly allowed working fork. Within an effective P1 grant, the agent chooses and implements a testable patch, autonomously fixes ordinary test failures, and assembles the **unpublished** PR diff/title/body plus source and validation receipts. Do not require fresh human confirmation for each routine delegated step.
- **Negative and partial-path evidence.** Demonstrate that no grant means no write; forbidden repository/path, missing native operation, expired/revoked grant, modified base, policy conflict or external PR submission all fail closed. Preserve partial GitHub mutations and require a new decision before any unsafe retry.
- **Human publication handoff.** The operator receives the complete validated PR package and personally chooses whether/when to publish it on the external upstream. Record the human as the publication decision owner; the external maintainer independently owns review, acceptance and merge.
- **Observed return.** Capture who selected the candidate and fix, who authored the patch, validation/results, interventions, closure (`CLOSED_CHANGE` / `CLOSED_NO_CHANGE` / `ESCALATED` / `NON_ADMITTED` where appropriate), upstream disposition and the effect on later work. Keep the actual VSM autonomy assessment separate.

**P1 is blocked today.** The user-requested *direction* of progressively transferring routine contribution work does not, by itself, attest an effective actor-specific standing write mandate or bypass the currently binding stage-specific gate in Upstream #6. No external PR is authorized by this proposal.

## Owner-controlled evolution path

1. Review this target envelope and **decide which system boundary owns the requested right**. Adjacent local Upstream fork preparation and Organization-wide S1 admission are independent decisions. Preserve [Organization #274](https://github.com/opensiro/vsm-oss-organization/issues/274) as a separate S5 question; do not treat review as selecting admission option A.
2. Obtain a separately attributable **authorized Upstream/fork-owner decision** for a local adjacent P1 grant, or an **S5 decision** if the proposed change alters the bounded Organization's identity, admission or higher-level delegation model. Record scope, owner, recipient, effective term, revocation, return targets, and application at their owning sources; preserve existing safeguards until effective.
3. Extend the existing Upstream adapter **only for actually delegated local stages**, retaining a provider-enforced actor identity, checks before/after the decision, permission/policy/branch verification, narrow write scopes, real readback, failure/partial-recovery stop, and tests.
4. Exercise genuine bounded candidate work and preserve who owned each decision and closure; do not count fake/mock tests as autonomous operation.
5. Keep external PR publication **manual** until a distinct future issuer decision changes that specific right. Record the upstream maintainer's external disposition separately.

**OSM rule:** transfer the **decision right**, not merely the click, when legitimate authority and evidence permit. After transfer, avoid per-step permissions for locally delegated variety; before transfer, do not invent the permission.
