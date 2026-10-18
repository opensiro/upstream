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
   destination fork name, license/source checks, contribution purpose,
   and any blocker. This is a proposal, not an action authorization.
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

### Batch approval does not silently authorize other actions

For the first implementation, the only executable operation is
`create_public_fork` into `opensiro-contributions`. Developing code,
opening an *external* upstream pull request, maintainer contact,
archive/delete, and permissions changes are **distinct decisions**.
An approved fork batch cannot expand itself into external submissions.

### Example — explanatory, not a real batch

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
