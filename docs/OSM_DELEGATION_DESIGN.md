# OSM autonomy-transfer design for Upstream Contributions

**Status: PROPOSED DESIGN ONLY — not a standing grant, S1 admission, host integration, or authority to mutate GitHub.**

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

**Fork creation is distinct from local preparation.** Draft [Upstream PR #18](https://github.com/opensiro/upstream/pull/18) proposes a source-only fork-stage adapter, but the present connected GitHub tools do not expose native `create_public_fork`. An already-existing fork is not evidence that a new fork was created.

## Activation transaction required before any standing local-write mandate

A prospective S5 decision on a new organizational boundary/delegation model must be **attributable** and separate from drafting or discussing this design. Any later effective operational grant must record:

1. legitimate issuer and a verifiable issuer/owner act, and the **exact recipient/agent execution identity**;
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
| Legitimate boundary/mandate issuer | Organization's currently declared S5 parent; **no attributable #274 admission/delegation decision yet** |
| Recipient | Agent-operated Upstream contribution role; **actual authenticated execution identity not identified** |
| Working repository allowlist | **Unset**: discoverable/writable forks are *not* automatically enrolled |
| Locally delegated discretion, after activation | Candidate investigation and bounded fix selection; own-branch creation, code/tests/docs changes, local recovery and verification; full **unpublished** external PR package |
| Disallowed operations | Submission of external PRs, unsolicited external maintainer contact, DCO/CLA assertions without attributable contributor attestation, protected/default-branch merges, destructive fork actions, permission expansion, S5 scope changes, Index/Skills canonical authority |
| Tool enforcement | **Not connected** for standing grants: stage scope, actor/repository/branch allowlist, live permission/revocation checks and readback must be implemented and evidenced first |
| Effective time, expiry, revocation | **Unset**; no perpetual grant or default approval |
| Decision proof and downstream acknowledgment | **Absent**; issuer evidence and applied recipient/host acknowledgment required before operation |
| Autonomy grade | **Not assessed**; future run evidence cannot be replaced with this proposal |

### P1 activation and acceptance conditions

- **Governance first.** Resolve the actual #274 S5 boundary decision independently (admit or keep adjacent). Do not silently assume admission from a positive technical trial. If a local standing mandate is then proposed, the legitimate owner must separately issue an attributable, versioned, revocable delegation within the chosen boundary, identify the real recipient actor and permitted source/fork scope, and supply its return target.
- **Host enforcement first.** The existing Control Plane must prove it can map a real connected agent execution identity and an operative mandate to GitHub write operations; check the exact grant before *every* write, repeat remote preflight at the action boundary, and reject grant expiry/revocation, wrong fork, default-branch/PR writes, branch drift and permission changes. Do not replace this with `authorize=True` or a document-derived approval.
- **Bounded first run.** Choose one real upstream-native issue, validate duplication/licensing/CLA and an explicitly allowed working fork. Within an effective P1 grant, the agent chooses and implements a testable patch, autonomously fixes ordinary test failures, and assembles the **unpublished** PR diff/title/body plus source and validation receipts. Do not require fresh human confirmation for each routine delegated step.
- **Negative and partial-path evidence.** Demonstrate that no grant means no write; forbidden repository/path, missing native operation, expired/revoked grant, modified base, policy conflict or external PR submission all fail closed. Preserve partial GitHub mutations and require a new decision before any unsafe retry.
- **Human publication handoff.** The operator receives the complete validated PR package and personally chooses whether/when to publish it on the external upstream. Record the human as the publication decision owner; the external maintainer independently owns review, acceptance and merge.
- **Observed return.** Capture who selected the candidate and fix, who authored the patch, validation/results, interventions, closure (`CLOSED_CHANGE` / `CLOSED_NO_CHANGE` / `ESCALATED` / `NON_ADMITTED` where appropriate), upstream disposition and the effect on later work. Keep the actual VSM autonomy assessment separate.

**P1 is blocked today.** The user-requested *direction* of progressively transferring routine contribution work does not, by itself, attest an effective actor-specific standing write mandate or bypass the currently binding stage-specific gate in Upstream #6. No external PR is authorized by this proposal.

## Owner-controlled evolution path

1. Review this target envelope together with the Organization OSM construction and [S5 domain proposal #274](https://github.com/opensiro/vsm-oss-organization/issues/274); do not treat review as selecting admission option A.
2. Obtain a separately attributable parent/issuer decision **if** the proposal changes S5-reserved delegation/boundary. Record the scope, grant, return targets, and subsequent application at the owning source; preserve existing safeguards until effective.
3. Extend the existing Upstream adapter **only for actually delegated local stages**, retaining a provider-enforced actor identity, checks before/after the decision, permission/policy/branch verification, narrow write scopes, real readback, failure/partial-recovery stop, and tests.
4. Exercise genuine bounded candidate work and preserve who owned each decision and closure; do not count fake/mock tests as autonomous operation.
5. Keep external PR publication **manual** until a distinct future issuer decision changes that specific right. Record the upstream maintainer's external disposition separately.

**OSM rule:** transfer the **decision right**, not merely the click, when legitimate authority and evidence permit. After transfer, avoid per-step permissions for locally delegated variety; before transfer, do not invent the permission.
