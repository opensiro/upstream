# Conversation-approved contribution batches (provider-agnostic UX contract)

> **Status: design only — NOT implemented and NOT authorized to execute.**
> Tracks [Upstream #6](https://github.com/opensiro/upstream/issues/6).
> The merged single-fork workflow is **not** a batch authorization gate.
> Do **not** provision `UPSTREAM_FORK_TOKEN` until an executor that rejects
> unapproved requests is implemented, tested, and merged.

## Operator experience (conversation-first, client-agnostic)

The approval interface is any conversational agent or chat client: ChatGPT, Claude,
a custom bot, or another compatible frontend. No particular model, provider,
application, or hosted runtime is required. GitHub stores the approved batch
and performs only authorized operations; the conversation is the operator UX.

1. The agent prepares a **bounded contribution batch**, normally up to
   ten candidates. Each row includes upstream URL, intended operation,
   destination fork name, license/source checks, a **concrete change proposal**,
   and any blocker. Each candidate must explain the observed upstream problem,
   targeted system component, planned change, expected system improvement,
   and how the change would be validated. Evidence links must accompany
   the proposal. This is a proposal, not an action authorization.
2. The owner sees the batch in their chosen conversation client and can **approve all, approve
   selected entries, ask for changes, or reject**. The chat response
   must refer to the concrete batch/version and allowed operations.
3. The agent publishes the **exact approved subset** and an approval
   receipt to the public Upstream repository. The receipt records
   the user-facing decision text, operator identity assertion, UTC
   timestamp, exact approved items and their canonical digest. The
   machine-readable `approval_medium` is `agent_chat` regardless of client;
   a provider name is optional provenance and never an authorization gate.
   Never present this as a GitHub-verified cryptographic signature:
   the agent-controlled GitHub connection alone cannot independently
   attest who approved the batch in any conversational client.
4. The executor accepts **only a registered approved batch** from
   a protected `main` branch, not an arbitrary `source` with
   `execute=true`. It verifies the permitted operations and exact
   item set *before* using its fork-creation credential.
5. Each item gets a separate verifiable result: `CREATED_VERIFIED`,
   `EXISTS_VERIFIED`, `BLOCKED`, or `PENDING_VERIFICATION`.
   Partial failure never authorizes extra items or implicit retries.
   Results and GitHub run URLs are returned through the originating conversation/client and linked from
   the public issue/receipt.
6. `registry.yaml` and project profiles are changed **only from
   verified repositories and recorded contribution scope**, not from
   approvals or API 202 responses.

## Required contribution proposal — what the system would gain

Every candidate row must carry a **specific, evidence-linked plan**, not just
a repository name, a VSM letter, or a generic "improve orchestration" claim.
The chat UI shows the following human-readable fields:

| Field | Operator question | What it should contain |
| --- | --- | --- |
| `system_component` | Where? | The upstream-owned component, workflow, API, documentation or contributor process being changed |
| `problem` | Why? | The current limitation and the observed evidence supporting it |
| `planned_change` | What exactly will change? | Concrete files, behaviors or integration path to modify; scoped enough for upstream review |
| `expected_improvement` | What gets better? | An explicitly **expected**, not measured, downstream system-level benefit |
| `validation` | How will we know? | Planned tests, regression cases, benchmark or observable acceptance conditions |
| `evidence_url` | What supports the proposal? | A public upstream source, issue, maintainer discussion or other relevant evidence URL |

For an assessment-informed suggestion, an agent **may** additionally describe
which Profile-defined VSM function the change appears to touch (e.g., a
task-level S1 capability or an S2 coordination path) and link the actual
general VSM assessment. This is explanatory context, **not** a new grade, a
maturity score, an assertion of autonomy, or proof that the improvement works.
Absence of an assessment must not block an otherwise viable native upstream
contribution.

**Authority distinction:** selecting an entry with action
`create_public_fork` approves only creation of the named fork under the
stated proposal. It does **not** approve implementation, commit/push of a
proposed patch, submission of an external PR, or archiving. Those require
their own explicitly scoped approvals, even if the same candidate card
explains the longer-term contribution plan.

When an agent revises any substantive part of the proposed problem, plan,
expected improvement or validation, it must issue a new batch version and
obtain fresh approval. The frozen approved manifest includes the exact
`proposal` object in its SHA-256 digest; it must not be silently rewritten.

### How to derive improvement plans from assessed systems

Public VSM Index assessments and strong practices from other OSS systems
can be **discovery signals** for candidate changes. A concrete contribution
proposal must still be grounded in the **target upstream's** own code,
maintainer expectations, integration surface and tests:

```text
Source observations / optional VSM assessment
          ↓
Identify a concrete upstream-native problem
          ↓
Propose a bounded change to the target system
          ↓
State expected (not established) improvement
          ↓
Specify tests, compatibility checks, and public evidence
          ↓
Human selection → scoped batch authorization
          ↓
Later: separately verified implementation/upstream outcome
```

A transferable best practice observed in another system is **not proof**
that copying it is appropriate or will improve this target. The proposal
should state what needs adapting to the target architecture and identify
regression risks when material. It should also distinguish:

- **Target-system benefit**: what the upstream project itself is expected
  to gain. This is the primary criterion for a proposed contribution.
- **Reusable insight for OpenSiro**: a pattern OpenSiro might later adopt
  in its own work, if relevant. This is secondary research context, not
  a justification for a patch the upstream does not need.

Do not manufacture assessment evidence or change Index ownership labels
because a contribution proposal sounds promising. Only actual upstream
validation and maintainer outcomes can support completed-result claims.

### Example candidate card — illustration, not an executable approval

**Repository:** `example/repo-a` (illustrative)
**Proposed authorized action:** Create public fork
**Target:** Task handoff component
**Problem:** Failed handoffs may leave a task without a clear accountable owner;
verify with a pinned source reference before proposing upstream work
**Planned change:** Add explicit handoff state and a focused regression test
**Expected improvement:** Fewer ambiguous task ownership transitions; a
hypothesis to evaluate, not a measured result
**Validation:** Run the project's task-handoff test suite and a before/after
regression case for interrupted handoffs
**Evidence:** The real card must link to a public source; no synthetic
`example/` link is acceptable as evidence

This illustration does not endorse or assess any actual project and is **not**
the demonstration batch #001 previously shown in chat.

### Batch approval does not silently authorize other actions

For the first implementation, the only executable operation is
`create_public_fork` into `opensiro-contributions`. Developing code,
opening an *external* upstream pull request, maintainer contact,
archive/delete, and permissions changes are **distinct decisions**.
An approved fork batch cannot expand itself into external submissions.

### Batch selection example — explanatory, not a real batch

```text
Batch: upstream-2026-001 (draft v1)
#  Repository         Action               Checks
1  example/repo-a     Create public fork   License reviewed
2  example/repo-b     Create public fork   License unclear → blocked

Choices:
  Approve eligible entries
  Approve selected entries (e.g. 1)
  Revise batch
  Reject batch
```

On selection, the bot reports precisely what will be created and
what is excluded; a changed item or new action requires **new
chat approval** for a new batch/version.

## Historical OpenSiro illustration — Henterprise (not a new batch)

The existing [Henterprise casebook entry](../cases/henterprise.md) shows why
candidate cards must separate proposed value from verified outcomes:

- **Target system:** Henterprise's Hermes delegation and independent review path.
- **Proposed change:** Cross-department accept/revise/reject responses,
  task-scoped commitment ledger, fixed-reference reviewer children,
  blocking-finding return and focused re-review, implemented with the
  project's existing `delegate_task` skills rather than a new runtime.
- **Expected improvement:** Clearer task-level coordination and review
  accountability. This is a *plausible benefit*, not a measured capability gain.
- **Outcome evidence:** The original [PR #1](https://github.com/humbertobellor/henterprise/pull/1)
  closed; the maintainer's replacement [PR #3](https://github.com/humbertobellor/henterprise/pull/3)
  merged on 2026-10-08.
- **Do not overclaim:** Product-native fit remains **pending** in the
  referenced experimental ledger. A merge is not proof of the independent
  counterfactual upstream need, and maintainer-added code is not attributed
  to the original contributor.

This is an **already recorded historical intervention**, not a new
candidate, real batch approval, authorization to reopen a PR, or evidence
of improved VSM grades. Actual future candidates still require specific
upstream evidence and a validation plan before presentation.

## GitHub remains an executor, not the approval interface

- A GitHub Actions environment may still store a **separate scoped
  secret** and restrict deployments to protected `main`, without
  requesting per-fork or per-batch GitHub **Required reviewers**.
- Protect `main` and workflow edits. Enforce the batch allowlist
  **inside the executor** before granting it the secret.
- Keep least-privilege fork credentials separate from any conversational
  agent connector. No admin/delete/archive permissions.
- The approval recording mechanism is a **workflow authorization
  policy**, not an independent authentication provider. GitHub
  credentials and branch protection are the actual enforcement
  boundary. If tamper-resistant owner attribution beyond agent
  assertions is required, it needs an independent attestation
  mechanism; do not claim it exists.
- Do not permit a direct single-fork execute path to bypass the
  approved-batch gate. Keep the current `execute=true` workflow
  **unprovisioned** until it is removed or made read-only.

## Minimal acceptance tests before enabling secrets

- Without an approved batch, no fork-creation POST occurs.
- An unapproved project, modified fork name, changed action, expired
  approval, or replay not matching the original batch is rejected.
- Only explicitly selected entries are executed; blocked entries are
  skipped, not silently approved.
- Wrong parent or occupied destination fails closed.
- Per-item results and partial failures do not mutate approval scope.
- No PR submission, repository archive, or automatic attribution of
  external acceptance is possible with this credential.
- Protected-branch and environment restrictions are verified
  on GitHub **before** adding the token.

## Provider-neutral approval metadata

The proposed approved-manifest schema attaches a `proposal` object to each
item with exactly the six fields above. The field is **descriptive and
authorization-scoped metadata**, not an instruction to execute a patch.
The batch digest covers that text and all selected entries; the proposal
remains stable after approval. The executor can validate scope without
pretending to verify the truth of a promised improvement.



Use `approval_medium: agent_chat` for conversational approval from any
provider. Preserve `approved_by` as a *declared* operator identity, and
`approval_ref` as the OpenSiro audit-record link; neither is an authenticated
identity proof by itself. Agent/platform names can be recorded as optional
observational provenance outside the authorization-critical allowlist.
Do not add a ChatGPT/Claude-specific field or rely on a client brand for
permission decisions. The batch executor currently remains **inactive**.

## Scope

This is a user-interface and operational execution design within
the independent `opensiro/upstream` portfolio. It does not adopt
Upstream as the fourth S1 domain. The boundary decision in
[Organization #274](https://github.com/opensiro/vsm-oss-organization/issues/274)
remains explicitly separate and proposed.
