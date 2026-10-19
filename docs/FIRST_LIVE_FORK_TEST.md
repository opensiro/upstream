# First live fork-contribution test through the existing Control Plane

**Status: PLANNED / NOT AUTHORIZED / NOT EXECUTABLE WITH THE CURRENT CONNECTED GITHUB TOOLSET.**

Owner: [Upstream issue #6](https://github.com/opensiro/upstream/issues/6).
The operator-facing entry remains the [existing OpenSiro OSS Control Plane](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/AGENT_CONTROL_PLANE.md).
This test does **not** admit Upstream as a fourth operational S1 domain: that is the independent, [still-proposed S5 decision #274](https://github.com/opensiro/vsm-oss-organization/issues/274).

## What this test is for

Prove the actual **fork-to-contribution** workflow with an external OSS source, rather than just the ability to prepare a branch and file in a pre-existing fork:

1. **Discover and propose** a real, source-backed upstream improvement. Read the current upstream default branch, issue/reviewer evidence, contributor instructions, fork policy, license, existing forks and overlapping PRs. Publish a `proposal_only` candidate and stage choices, not an invented approval.
2. **Operator selects and authorizes a precise `create_public_fork` action.** Display the source, destination owner/name, proposed stage, proposal revision and selected-stage digest. The digest is an unsigned identifier, **not** consent. The trusted current-session execution boundary must independently bind an actual attributable decision to the action.
3. **Create and verify a genuinely new public fork** in the specifically authorized destination namespace (the design contract currently calls for `opensiro-contributions`). Confirm the fork's parent is the selected upstream, it is public, the connected actor has the required permission, and its actual URL/identity. A provider acceptance/202 response is not a verified fork. A collision or pre-existing fork is not proof that a new fork was created.
4. **Prepare the contribution in the verified fork**, if this *additional* stage has been explicitly authorized: choose a bounded branch, implement the upstream-native change/tests and validate against the upstream's requirements. Preserve base refs, commit identities, evidence and any contributor/DCO constraints; do not invent a sign-off.
5. **Submit an external upstream PR only after its own explicit authorization** and verification of exact upstream target, branch, diff and policy prerequisites. Track submitted/accepted/merged/declined independently.
6. **Return real receipts** to the operator and update the Upstream lifecycle registry only for verified facts, with explicit partial-failure and maintenance status.

A fork created without a patch is a **verified fork-stage result**, not an end-to-end contribution. A patch prepared in an old fork is a **prepare-stage result**, not a fork-creation test. Opening a PR is not an upstream merge.

## The first pilot: stage gates

| Gate | Pass evidence | Block / fail closed when |
| --- | --- | --- |
| Source and proposal | A real external project, native need, source/license/policy review, no unresolved duplicate/collision | License/CLA, source, owner, policy or improvement is ambiguous |
| Exact operator approval | Independently attributable *current-session* consent for the selected candidate and the exact `create_public_fork` destination/stage | Generic `continue`, draft selection, agent-authored `approved_by` or API credentials alone |
| Connected provider capability | Native authorized fork-creation action and minimal required rights, implemented through the existing Control Plane execution path | No `create_fork`/equivalent action available; do not substitute a personal PAT, manual `execute=true`, or an untrusted callback |
| Real GitHub fork | Provider write plus readback of exact fork parent, owner, name, public visibility and identity; distinguish created vs already existed | Async request not yet verified, conflict, wrong parent or permission problem |
| Optional preparation | Separately authorized branch/commit, targeted tests and readback in *that* fork | Only fork stage authorized, DCO/CLA unresolved, no trusted host binding |
| Optional external PR | Separately approved actual PR and verified upstream PR URL/status | No specific publication authorization or contributor requirements unsatisfied |
| Closure | Per-stage receipts, partial/blocked states, clean registry semantics | Assumed merge, inferred S1 grade, guessed completion, or lost provenance |

The pilot should be one **real new-fork candidate** first, not a synthetic demonstration manifest. Avoid creating throwaway forks solely to claim a green test; choose a genuine intervention with credible next steps. Before any real write, re-read the current source and connected capabilities and re-run the bounded preflight.

## Current implementation boundary and immediate blocker

- [Batch proposal preview](BATCH_PROPOSALS.md) supports `create_public_fork`, `prepare_contribution` and `submit_external_pr` as **proposal stages only**.
- [Control Plane handoff](CONTROL_PLANE_HANDOFF.md) and [connected-stage adapter](CONNECTED_STAGE_ADAPTER.md) currently implement only **one test-file preparation in an already-existing writable fork**, using an unconnected trusted-host authorization callback. This is a valid narrow engineering checkpoint, **not** the fork test.
- The connected GitHub toolset inspected for this planning checkpoint exposes branch/file/PR operations but **no fork-creation action**. Consequently **live `create_public_fork` is BLOCKED**. Do not revive the old unrestricted fork helper, provision a token, launch a headless runner or use a side channel to make the test appear completed.
- The prior [Cognee preparation receipt](https://github.com/opensiro/upstream/issues/6#issuecomment-6255490373) used the **already-existing** `opensiro/cognee-community` fork; it remains honest evidence for `prepare_contribution` only. Cognee is **not** a required component or special dependency of Upstream.
- No external repository mutation or upstream submission is authorized by creating or merging this documentation.

## Minimal engineering work before a live fork

1. Establish a provider-supported, least-privilege `create_public_fork` operation callable from the **same existing Control Plane** with an independently trusted consent gate. If unavailable, record `BLOCKED_CAPABILITY` and stop; do not develop a separate permanent bot or hosted service.
2. Commit negative tests for missing/mismatched/expired/revoked approval; wrong source/destination; existing fork with wrong parent; permission and visibility mismatch; asynchronous response without verified readback; partial failures; and prevention of implicit `prepare_contribution`/`submit_external_pr`.
3. Run exact-head tests and review the safety boundary. Only then present a fresh real candidate and **ask the operator to authorize the exact fork action**.
4. Once real fork creation and verification succeed, exercise subsequent stages with their *own* scoped approvals and test evidence. Preserve blocked and unsuccessful outcomes.

**Activation remains closed.** The observed read-only and mock checks are not a real fork, not an operator decision, and not end-to-end success.
