# Conversation-approved contribution execution — authorization boundary (design only)

> **Status: NON-EXECUTABLE DESIGN.** This document is a source-first contract,
> not a credential, workflow, executor, consent record, approved manifest,
> or authorization to operate. No write-capable batch runner is deployed.
> [Issue #6](https://github.com/opensiro/upstream/issues/6) owns activation.
> [Organization #274](https://github.com/opensiro/vsm-oss-organization/issues/274)
> separately owns any change to OpenSiro's S1 organizational boundary.

## Goal

An operator can inspect a bounded list of **specific improvements to external
OSS systems** in any compatible chat/agent client, then issue **one explicit
decision** covering an exact subset of candidates and stages. A suitably
authorized executor may eventually perform *only* those actions. Repeated
per-fork GitHub reviewer clicks and an OpenSiro-managed hosted runtime are
not requirements.

The delivered [local preview](BATCH_PROPOSALS.md) supports up to 10 candidates,
each with the target subsystem, observed problem, planned change, expected
(unverified) benefit, validation and a claimed public evidence URL.
`--select` chooses proposal IDs; `--scope` can narrow each selected
candidate's proposed stages. This renderer does **not** communicate with
GitHub, verify ownership, or record approval.

## Hard separation of three objects

1. **Draft proposal.** Immutable-revision candidate content; status
   `proposal_only`; `proposal_sha256` identifies the canonical draft. No
   operator approval fields or write grant.
2. **Selected proposal scope.** Set of selected IDs and each exact allowed
   stage, identified by `selection_scope_sha256`. This hash is not a
   signature and does **not** prove operator authorization; a blocked
   candidate can still be selected *for discussion*.
3. **Actual execution authorization (NOT IMPLEMENTED).** An explicit,
   current, attributable operator decision covering the exact proposal
   revision, selected item/stage envelope and action-specific destinations.
   A proposed authorization stored or reproduced by an agent is still
   untrusted unless the actual executor has an independent reason to trust
   the decision.

Neither a user-facing `approved_by` string, GitHub issue link,
`selection_scope_sha256`, model output nor GitHub App credential alone
proves that the human authorized a specific batch.

## Two possible execution adapters; neither deployed

### A. Same-session connected agent (preferred first scope)

- User sees the exact contribution proposals and chooses entries/stages in
  their authenticated conversation.
- An actual connected agent applies those **current-session instructions**
  only through operations its connected provider already authorizes.
  Connector credentials prove service permissions, **not** permission to
  assume unspecified operator intent.
- Before each write, the agent compares its action, target, source revision,
  candidate ID and stage with the selected envelope and the consent scope.
  If the connector lacks an action, a claim is stale, or authority cannot be
  established, **stop**, do not silently switch to a broad PAT or headless
  workflow.
- A confirmation or execution receipt is not an independent cryptographic
  transcript signature. Do not claim such a proof exists.

### B. Deferred / headless runner (separately gated)

- A scheduled job cannot verify the real operator solely from agent-authored
  chat content, an `approved_by` JSON key, a public issue, or a git commit.
- Before a runner gains any write credential, it must have a genuinely
  verifiable channel for the exact approval and revocation, plus
  independently enforced protected workflow/manifest scope. If the channel
  is unavailable, **no headless write path may execute**.
- A future protected GitHub Actions environment may hold a narrowly scoped
  credential. Merely naming an environment in YAML is not enforcement, and
  GitHub Required reviewers are **not** the conversational operator UX.
- Never revive the old manual `execute=true` route disabled by
  [PR #8](https://github.com/opensiro/upstream/pull/8).

## Stage-specific permissions: no implicit escalation

| Stage | Narrow permissible result (future) | Independent prerequisite |
| --- | --- | --- |
| `create_public_fork` | Create/verify one public, correctly parented fork in `opensiro-contributions` with the specified source and name | Approved exact item+stage; source, license and forking checks |
| `prepare_contribution` | Scoped implementation in an authorized working repository/branch, with source-linked tests | Explicit stage approval; verified existing allowed workspace/branch, whether or not the fork stage was selected |
| `submit_external_pr` | Publish one PR to the intended external upstream repository from the verified contribution branch | Explicit stage approval; exact base/head/target and upstream contributor requirements checked |

A proposal may contain all three stages; selecting **only the fork**
must not permit preparation, pushing or external PR publication.
Selecting `submit_external_pr` alone does **not** implicitly grant
`create_public_fork` or `prepare_contribution`; any existing branch and
submission prerequisites must independently be verified. The upstream
maintainer alone controls external acceptance and merge.

**Not in this envelope:** repository deletion/transfer/archiving,
organization membership and permissions, maintainer contact beyond an
explicitly approved PR, S5 scope decisions, Methodology/Index classification
changes, or automatic maintenance-state transitions.

## Before any write

1. Confirm that the operator really selected the exact ID/stage set;
   preserve the source proposal revision and stage-bound scope identity.
2. Reject any selected blocker, unsupported stage, unreviewed source,
   forking restriction, unresolved license, unverified identity or
   ambiguous destination. A valid SPDX identifier alone is **not** legal
   compatibility approval.
3. Re-check the target repository, branch and intended operation against
   current public upstream instructions/issue and exact source evidence.
4. Check every selected entry for a valid authorization and actionable
   prerequisites **before the first write**, so a known invalid item
   does not cause avoidable partial execution.
5. Do not infer authority from a successful dry-run or a GH token.
   Unsupported actions or approval drift require **new operator decision**.

Preflight is best-effort against remote drift, not atomicity: multiple GitHub
writes cannot be assumed to roll back together. If state changes after
preflight, fail at the item/stage gate rather than broaden or substitute
permissions.

## Receipts and failure semantics (future)

Each attempted stage requires a **real** receipt bound to candidate ID,
source/destination, stage, proposal revision, scoped decision reference,
actual timestamp, observable GitHub refs and explicit result. Separate
`PREFLIGHT_PASS` and `PROPOSAL_PREVIEW` from real outcomes such as
`CREATED_VERIFIED`, `EXISTS_VERIFIED`, `PENDING_VERIFICATION`,
`BLOCKED`, `FAILED`, and independently verified upstream `submitted`
/ `merged`.

An accepted asynchronous fork request is not a verified fork. An existing
correctly parented fork is not an accepted upstream PR. A merged PR is not
proof of measured system improvement or product-native fit.
Partial failures, canceled batches, retries or stale approval must never
silently expand the selected scope; record a bounded terminal state and
return to the operator. Update `registry.yaml` only from verified facts.

## Minimum independent validation before an executor is merged

- [ ] A real operator authorization source is identified and validated
  **end-to-end**, not supplied by the same untrusted agent JSON.
- [ ] Approved/denied/expired/revoked/changed-scope cases reject writes
  before any credential is used.
- [ ] Per-candidate scope narrowing is enforced at every stage, including
  blocked or unselected entries and any mismatch between proposal digest,
  stage set, source, fork name, PR target or working branch.
- [ ] No route exists around the executor's allowlist via legacy CLI,
  workflow dispatch, personal PAT, optional branch, or helper API.
- [ ] Stage-specific native source/target checks, asynchronous verification,
  collision handling, idempotence and partial-failure receipts are tested.
- [ ] Negative tests confirm that fork approval cannot push code, submit a
  third-party PR, archive a repo, or escalate organization rights.
- [ ] Batch-specific tests are committed, run by exact-head CI and inspected.
  Existing single-fork test CI is not batch-authorization evidence.
- [ ] Protected `main`/workflow/environment/manifest boundaries and the
  least-privilege credential are verified *before* introducing any secret.
- [ ] Real operator-approved pilot is bounded and documented separately.
  **Demonstration batch #001 is not a pilot or an approval.**

No implementation or permission change is made merely by accepting this
design. If the selected chat client does not expose the needed GitHub
operations, stop at the read-only proposal and select a verified,
appropriately authorized adapter later.
