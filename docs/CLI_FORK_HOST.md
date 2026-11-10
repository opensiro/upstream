# GitHub CLI fork execution — credential-owning VM/host

**Status:** Host-backed CLI route documented; credential availability and authority
for an actual fork remain **unverified** in the OpenSiro Upstream execution
contract. This document does not activate a writer.  
**Owner:** [Upstream #28](https://github.com/opensiro/upstream/issues/28)
under [#6](https://github.com/opensiro/upstream/issues/6).

## Execution topology

```text
OpenSiro OSS Control Plane: selected candidate + exact stage/scope
  → trusted authorization / replay-protected batch grant
  → existing credential-owning VM or host (OS user / service / container)
  → locally available GitHub CLI (gh) or authenticated GitHub REST client
  → fork in opensiro-contributions
  → independent parent, public-visibility, push-right and branch-SHA readback
```

Here **VM/host means the actual environment that runs the GitHub request and
holds or can legitimately access its credential**, not a particular
orchestration application. The same host may support multiple invocation
interfaces; those interfaces do not confer additional GitHub privileges.

A PAT may already be installed on a VM/host in a GitHub CLI credential store,
a Git credential helper, an OS secret manager, a service environment, or a
container-specific identity. **Absence of `GH_TOKEN` or `GITHUB_TOKEN` in
one shell, or `gh auth status` failure for one OS account, is not proof that
no PAT exists elsewhere on that machine.** Equally, an operator report that
a PAT exists is not proof that the actual execution user can use it or that
it can create a repository in `opensiro-contributions`.

Do not copy, print, export into chat, persist in the source tree, or expose
the PAT in logs, command-line arguments, workflow dispatch inputs, CI
artifacts or PRs. Do not change a credential helper or reauthorize a
different principal merely because an earlier diagnostic shell was
unauthenticated.

## Executable, non-secret VM/host readiness probe

The upstream repository now includes
[`scripts/cli_host_readiness.py`](../scripts/cli_host_readiness.py), a
**read-only** standalone diagnostic intended to run on the **actual OS
account/container that would issue the fork request**:

```bash
python3 scripts/cli_host_readiness.py \
  --source HarnessDesk/HarnessDesk \
  --working-branch development
```

The probe checks only whether the local `gh` binary is present,
`gh auth status` succeeds **for this account**, `gh api user` identifies a
GitHub principal, and an explicit **GET** can retrieve the working branch SHA.
It also reports only the **presence** of `~/.git-credentials`, configuration of
the global Git credential helper, and presence of supported token environment
variables. It never runs `git credential fill`, reads credential-file
contents, prints a token, changes `gh auth`, posts to GitHub or creates a fork.
Subprocess stderr and raw `gh auth status` output are suppressed.

- `BLOCKED_GH_CLI_AUTH` means **only** that `gh` is not authenticated under
  that execution identity. It does not mean the host has no PAT.
- `CLI_READ_READY_NOT_AUTHORIZED` means **only** that identity and the public
  source branch are readable from the local CLI session. It does not prove
  organization repo creation or Control Plane batch authorization.
- A configured Git credential helper and store may authorize **Git**, but
  should not be silently exported into `gh` or exposed to a chat/CI log.
  Resolve the correct authenticated execution context separately.

## Non-secret CLI discovery — on the actual execution account

Run these from the **same VM/host, OS identity and environment** intended for
the fork stage. They are read-only and do not disclose a token value.

```bash
command -v gh
gh auth status --hostname github.com
gh api user --jq .login
gh api --method GET repos/HarnessDesk/HarnessDesk/branches/development --jq .commit.sha
```

Interpret outcomes narrowly:

- `command -v gh`: the binary is installed in that shell only.
- `gh auth status`: CLI-authenticated account(s) for **that OS user / environment**.
- `gh api user`: the identity available to the current GitHub CLI session
  (for an ordinary user PAT); an app installation token requires a different
  principal check.
- `gh api ... branches/development`: observed source SHA, **not** a
  destination creation grant.

If the credential is only available in another protected service/container
context, **check that context without moving or revealing it**. Prefer
diagnostics that return redacted presence, identity and effective permission
observations, not raw secret material. Git operations via a credential
helper do not necessarily authenticate `gh api` in the same shell.

## Fork write preconditions — distinct from credential presence

The existing [batch fork source gate](BATCH_FORK_HOST_GATE.md) must still
establish all of the following **at execution time**:

1. A real, authenticated operator/parent decision for **this exact batch
   and only the `create_public_fork` stage**, bound to candidate IDs,
   source, `opensiro-contributions`, source SHA, intended fork name,
   `default_branch_only` choice, manifest/scope digests and execution actor.
   The grant must be short-lived, one-use, revocable and replay-resistant.
2. The **actual credential-bearing OS identity** has the necessary
   GitHub fork-creation and destination-organization permissions; public
   GET success and the existence of a PAT do not establish this.
   Verify source policy and the applicable token restrictions independently.
3. For a nondefault integration branch such as `development`, request an
   all-branches fork and independently read back the exact branch SHA,
   actual source parent, visibility and push rights after the write.
4. One bounded fork POST per authorized item, truthful receipts and
   fail-closed stop after a failed, ambiguous or pending write. Never
   silently retry or submit an external upstream PR.

The [GitHub REST fork port](REST_FORK_PORT.md) contains the source-side
operation adapter but no actual authenticated CLI/host integration.
The [public preflight CLI](FORK_PUBLIC_PREFLIGHT.md) deliberately uses
anonymous GETs and remains uncredentialed. Neither proves a valid
permission or an operator decision.

## Updated one-off credential evidence

A dated live test on this existing host confirmed that `gh` could authenticate
as `xLagerFeuer` and **actually create** a public, correctly parented,
branch-preserving `HarnessDesk` fork in `opensiro-contributions`. This
supersedes the earlier dated `robot` unauthenticated observation **for the
tested CLI context only**. It is not a validated source-wide standing mandate
or a verified fork into the *different* organization `opensiro`.

[Organization fork and external upstream PR procedure](ORGANIZATION_FORK_UPSTREAM_PR.md)
now documents both org destinations and an independently read-only PR
handoff for a future pushed contribution branch. The latter cannot publish.

## Current boundary and next step

- An existing VM/host is a **candidate execution environment**, not a
  confirmed credential/permission capability.
- A PAT is **reported as already provisioned**; its storage location,
  applicable OS identity, exact scopes and destination rights have **not
  been independently verified** in Upstream's evidence.
- Do not create another bot, GitHub App or host by default. First inspect
  the already provisioned environment via non-secret checks.
- If a suitable credential and verifiable batch authorization cannot be
  established, report `BLOCKED_CREDENTIAL_CONTEXT`,
  `BLOCKED_PROVIDER_PERMISSIONS` or `BLOCKED_AUTHORIZATION` as
  appropriate and stop without writing.

No live fork, external PR publication or S1 autonomy/admission follows
from documenting this execution route.
