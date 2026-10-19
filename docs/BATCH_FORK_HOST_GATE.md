# Trusted-host batch fork orchestration — source prepared, inactive

**Owner:** [Upstream #28](https://github.com/opensiro/upstream/issues/28) under [#6](https://github.com/opensiro/upstream/issues/6).  
**State:** `SOURCE_PREPARED / MOCK_TESTED / LIVE_EXECUTOR_BLOCKED`.  
**Entry:** Existing Organization Control Plane; *not* an additional Control Plane, GitHub App, hosted worker or privileged Actions workflow.

## Added bounded core

[`scripts/batch_fork_executor.py`](../scripts/batch_fork_executor.py) composes
the existing `proposal_only` selection with the single-stage
[`connected_fork_adapter.py`](CONNECTED_FORK_ADAPTER.md).

It admits **1–10 selected candidates**, each with *exactly*
`create_public_fork`. Every candidate requires a concrete action specifying
fixed destination `opensiro-contributions`, fork name, working branch,
pinned 40-hex SHA and explicit all-branch/default-only fork choice.

Before requesting authorization, the core validates the entire batch,
all candidate proposal blockers, requested stage scopes, duplicate
destinations, live provider-source/branch checks, same connected actor and
repository-name matches. It binds all actions and proposal/scope hashes to
**one batch intent**.

The host is then required to issue a **genuinely authenticated one-batch
grant**. Each fork uses a separate host-enforced one-use *stage* decision under
that batch grant. Changed proposal, selected scopes, actions, source SHA,
actor or target blocks; a write/readback failure or pending outcome stops
further candidates. No automatic retry, publish, archive or registry update.

## REST provider port (source only)

[`scripts/rest_fork_port.py`](../scripts/rest_fork_port.py) implements
the required GitHub REST `repo`, `branch` and fork operation
interfaces with **host-injected authenticated request and permission
attestation**. It is **not** an exposed ChatGPT GitHub method or a
credential-bearing CLI; see [REST port contract](REST_FORK_PORT.md).
It does not close the trusted batch-grant/actor/permission gap.

## Host requirements (not implemented here)

The Python interface requires **two injected ports**:

- `github`: existing `repo`, `branch`, `fork_capability`,
  `create_public_fork`. Currently **no real connected fork provider**
  satisfying this interface is exposed through the GitHub connector.
- `host`: `verify_exact_batch(batch_intent)` and
  `authorize_exact_stage(grant, batch_intent, stage_intent)`.

The **real host** must authenticate the *actual operator* and executing
actor, verify a bounded issuer/recipient/expiry/nonce/revocation decision,
keep a replay-proof grant ledger, independently bind the exact batch and
stage, and provide an authorized fork-capable provider. Merely constructing
an object implementing these Python methods or returning `True` does
**not authenticate** anybody. The code and offline tests are not a substitute
for a trusted host boundary. Do not activate the module from untrusted
workflow inputs, forked PR code, a console, an issue comment, an unsigned
`approved_by` field or an unprotected runner.

A **protected Actions/REST** transport remains an alternative to native
ChatGPT connector exposure, per
[`AUTOMATIC_FORK_EXECUTOR_RECOVERY.md`](AUTOMATIC_FORK_EXECUTOR_RECOVERY.md).
The current module is provider-agnostic *source orchestration*, not the
production credential/approval bridge. The old
[`fork-lifecycle.yml`](../.github/workflows/fork-lifecycle.yml)
**must stay preview-only**; no legacy `--execute`/`UPSTREAM_FORK_TOKEN` route.

## Safety test contract

[`tests/test_batch_fork_executor.py`](../tests/test_batch_fork_executor.py)
provides offline fake-provider and fake-host coverage for: no provider,
no host, denied batch or per-stage approval, selected-only stages, blocked
candidate, duplicate destination, post-approval changed manifest/scope/action,
changed source SHA, missing nondefault branch, all-branches-only fork,
write failure, pending readback, no retry and a two-candidate grant.

**Mock green is NOT live success.** In particular, the existing
[HarnessDesk #1772](../pilots/harnessdesk-1772/README.md) proposal contains
`prepare_contribution` only and explicit blockers; it cannot be selected
into a new `create_public_fork` stage or executed with this core.
The source and proposal must be independently refreshed and separately
requalified when the real executor is ready.

## Remaining acceptance gates

1. Independently verify that an actual provider can fork a third-party public
   repository into `opensiro-contributions`, that its executing actor has
   scope-limited org creation permissions, and that the provider can copy
   the required nondefault branch.
2. Authenticate and bind **one real Control Plane operator batch decision**
   to an effective short-lived, revocable, replay-protected host grant.
   Unit-test stand-ins, proposal hashes or a generic `continue` do not count.
3. Implement and review a **protected runtime integration**. Prevent
   PR-branch code, manually supplied manifest or user workflow dispatch
   from activating privilege. Validate status/permissions and one-write
   receipts under an actually connected provider.
4. Execute a fresh, source-qualified pilot only after authorization and
   independently verify the new public fork, direct parent, push rights
   and `development` branch at pinned source SHA.

Until these exist, `BLOCKED_EXECUTOR / BLOCKED_AUTHORIZATION` remains
the truthful live status. This design neither admits a fourth S1 domain nor
authorizes an external PR, and it does not claim an autonomy grade.
