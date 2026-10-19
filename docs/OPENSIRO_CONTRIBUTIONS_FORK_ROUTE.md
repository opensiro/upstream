# OpenSiro Contributions — fork creation via the existing Control Plane

**Owner:** `opensiro/upstream` · **Task:** [Upstream #28](https://github.com/opensiro/upstream/issues/28) (focused executor/first-fork blocker), parent [Upstream #6](https://github.com/opensiro/upstream/issues/6) · **Status:** `BLOCKED_EXECUTOR / BLOCKED_AUTHORIZATION` · **Not a live fork-creation tool or effective grant.**

## Principle

For assessment-driven Upstream Contributions, the normal working-fork
destination is **`opensiro-contributions/<fork-name>`**. Do **not** tell the
operator to create a fork in their personal account by default. A separate
personal-contributor fork can be used only when independently selected and
authorized for that specific contributor/work; it is not a workaround that
counts as the prescribed `opensiro-contributions` fork test.

The **existing Organization Control Plane** presents the action. The
**Upstream** repository owns intake, the exact fork stage and returned
evidence. This does not create another Control Plane, GitHub App, background
runner, scheduled bot, standing permission or admitted fourth S1 domain.

```text
Index assessment (canonical pinned SHA/path)
  → independently qualified native upstream improvement
  → blocked/preview-only Upstream proposal
  → verified fork-capable connected GitHub actor + destination rights
  → attributable exact-stage operator decision
  → one provider-native fork creation
  → exact new public fork / parent / branch / permissions readback
  → separate authorized prepare_contribution stage
  → complete unpublished contribution package
  → human-owned external PR publication (only if later chosen)
```

## Two supported execution designs, neither activated

**The existing REST fork client is a real source-prepared fork transport.**
[Merged PR #5](https://github.com/opensiro/upstream/pull/5) added
[`scripts/create_fork.py`](../scripts/create_fork.py), which implements
GitHub REST `POST /repos/{source}/forks`. [Merged PR #8](https://github.com/opensiro/upstream/pull/8)
intentionally disabled the old write-capable manual workflow because its
authorization boundary was incomplete. This is an **inactive execution route**,
not evidence that writing a fork requires a custom MCP plugin.

For safe activation the owner may independently review either a **protected,
batch-only GitHub Actions/REST executor** reusing this client or a **native
ChatGPT-connected fork provider** running the source-only adapter. The
native ChatGPT method is **not mandatory** if the separate trusted executor
can verify exact, attributable Control Plane batch authorization before
the write. Conversely, the old `--execute` command, an unguarded
`workflow_dispatch` or an unverified token is **not** the batch executor.

The [transport recovery design](AUTOMATIC_FORK_EXECUTOR_RECOVERY.md)
records current source evidence, GitHub App installation observations,
provider-permission checks, exact approval-to-executor bridge and
branch-aware acceptance criteria. **No path is activated until the
verifier and its actual rights are independently demonstrated.**

## Current tool boundary

- [Merged source PR #30](https://github.com/opensiro/upstream/pull/30)
  ports the historical Draft #18 fork adapter to current `main` with
  explicit branch/SHA validation and mock tests. It is **source-prepared**:
  neither trusted host `authorize(intent)` nor native
  `github.create_public_fork(...)` is live-connected.
- The currently available ChatGPT GitHub connector can create branches/files
  and internal PRs in authorized repositories, but does not expose a native
  create-fork action. **This blocks the connector-adapter route only, not a
  separately verified protected REST executor.** Its organization app
  installation and repository listing cannot by themselves prove fork-create
  permissions or the operator's exact authorization.
- Deployed [`fork-lifecycle.yml`](../.github/workflows/fork-lifecycle.yml)
  is **preview-only** and must remain that way. The old token-based
  `create_fork.py --execute`, PAT, an invented `approved_by` field or a
  headless workflow are **not** acceptable substitute execution paths.
- `BLOCKED_CAPABILITY` is a valid negative preflight for the native
  connector route; `BLOCKED_EXECUTOR / BLOCKED_AUTHORIZATION` is the
  appropriate overall state until **either** independently authorized
  executor path exists. Neither status is a request for an improvised
  personal fork. Preserve the qualified proposal and stop before any
  external mutation.

## Prepared branch-aware adapter (not live)

[`connected_fork_adapter.py`](../scripts/connected_fork_adapter.py) has an
offline-tested `create_public_fork` source contract with exact
`working_branch`, `working_branch_sha` and `default_branch_only`
inputs. It asks a trusted provider for the current source branch SHA
**before and after** current-session authorization; the fork result is
`CREATED_VERIFIED` only if the same required branch and SHA are
observed in the new working fork along with identity, parent, visibility
and push rights.

For HarnessDesk `development`, the operator-bound copy strategy must
be `default_branch_only=False`. This only works if the native provider
actually supports a corresponding **all-branch** fork operation. The
connector currently exposes **no native create-fork method**, and
the host-provided trusted `authorize(intent)` port is absent. The
implementation therefore remains **source-prepared**, not
activated; a passing offline fake-provider test grants nothing.

## Branch-aware fork acceptance

Do not conflate successful `create_public_fork` with readiness to modify the
correct upstream branch. For the first
[HarnessDesk #1772 candidate](../pilots/harnessdesk-1772/README.md), the
external repository's default branch is `main`, but its contribution path
uses `development` per
[`CONTRIBUTING.md`](https://github.com/HarnessDesk/HarnessDesk/blob/development/CONTRIBUTING.md).
Historical Draft #18 hard-coded `default_branch_only=True`. The
[current source adapter](../scripts/connected_fork_adapter.py) instead
binds `working_branch`, `working_branch_sha` and the explicit copy mode,
rejecting default-only copying for a nondefault target such as `development`.
The native GitHub fork method remains unavailable.

Before attempting an actual fork, resolve **in the exact stage contract and
bound operator intent** how the target working branch will exist. A
provider-native all-branches fork may be appropriate if supported and
specifically authorized; alternatively prove a separately permissible and
implemented method for materializing the target branch from the exact public
upstream ref. **Do not automatically assume GitHub fork network objects make
an uncreated branch writable**, use the release `main` instead of
`development`, or assert success from a 202 response.

For a `CREATED_VERIFIED` result intended to feed `prepare_contribution`,
read back all of: exact name, `fork=true`, expected `parent.full_name`,
public visibility, authenticated actor with push rights, and the selected
contribution branch at an independently refreshed acceptable revision.
If any source/permission/branch invariant is unverified, record
`PENDING_VERIFICATION` or `BLOCKED`; **do not** advance to preparation.

## First real, bounded action

Use the existing
[`pilots/harnessdesk-1772/`](../pilots/harnessdesk-1772/) packet only after
independently refreshing Index source/current upstream `development`, issue
#1772 status, overlapping PRs, licensing and contributor conditions.
The currently committed manifest has intentional blockers and **must not**
be silently treated as approved. Once every source/policy blocker is
resolved, revise the proposal and recompute its exact digest.

The connected host must then establish **all** of:

1. Native fork method actually exposed and permissible for authenticated
   actor and `opensiro-contributions` organization; missing method ⇒
   `BLOCKED_CAPABILITY`.
2. Exact already reviewed `create_public_fork` action, selected candidate,
   fork name, source/destination, branch-copy strategy, scope/digest and
   current-session attributable authorization; generic `continue`, the
   presence of tools, previously merged PRs or an assistant-generated issue
   are not approval.
3. Absent destination or explicit collision classification, fresh source
   rights/licensing/policy and second provider preflight immediately before
   the write.
4. Exactly one provider call, then independent readback (including the
   working-branch invariant), recording asynchronous/partial outcomes
   without unsafe automatic retry.
5. A **separate** exact authorization to create a contribution branch or
   test file. Creating a fork never permits external PR publication.

This is **local Upstream/fork-owner operational authority**, not an implicit
Organization S5 decision. [Organization #274](https://github.com/opensiro/vsm-oss-organization/issues/274)
remains `PROPOSED / NOT ADMITTED`; no `S1=A/C/C(P)` follows from this
readiness route.

## Implementation / review checkpoint

[Issue #28](https://github.com/opensiro/upstream/issues/28) owns the provider
and first-real-fork criteria. Branch-aware source was merged via
[PR #30](https://github.com/opensiro/upstream/pull/30). Require an actual
host-provided fork operation and separately authenticated, exact-stage
authorization before live activation; passing mocked tests alone is not a grant. Return a concrete readback receipt to
[Upstream #6](https://github.com/opensiro/upstream/issues/6) if an eligible
fork action ever executes.
