# Bounded local prepare mandate — HarnessDesk #1772 (proposal)

**Status: PROPOSED / NOT ACTIVE.** This is the simpler trust-based alternative to [Draft #52](https://github.com/opensiro/upstream/pull/52). It neither issues an operator decision nor activates a live external GitHub write. See [Upstream #6](https://github.com/opensiro/upstream/issues/6) and the parent [OSM delegation design](OSM_DELEGATION_DESIGN.md).

## Why this is smaller

Reuse the existing `gh` credentials on the existing VM and the already implemented authenticated GitHub read/patch port. Do **not** establish a new key hierarchy, signature authority, database, long-running service, or secondary Control Plane.

The **local fork owner** may eventually apply a **finite, revocable, standing mandate** that transfers *routine branch/commit preparation decisions* to the existing agent executor. The upstream PR publication decision stays human-owned. This adjacent Upstream-local pilot does **not** decide Organization [#274](https://github.com/opensiro/vsm-oss-organization/issues/274) or grade S1 autonomy.

## Narrow first-pilot envelope

[Proposed policy](../policies/harnessdesk-1772-local-prepare.json):

| Dimension | Fixed boundary |
| --- | --- |
| Local owner / GitHub actor | `xLagerFeuer` |
| Executor | existing agent on `zhdanov:robot` via authenticated `gh` |
| Source | `HarnessDesk/HarnessDesk`, issue [#1772](https://github.com/HarnessDesk/HarnessDesk/issues/1772) |
| Writable fork | **only** `opensiro-contributions/HarnessDesk` |
| Allowed action | `prepare_contribution` |
| Source and fork target | `development` pins, shared-commit mode |
| New ref | **only** `opensiro/fix-toolgateway-1772`, if absent |
| Changed paths | existing `packages/server/src/tool-gateway.ts` and new `packages/server/test/tool-gateway-ownership.test.ts` |
| Period proposed | 20 October through 10 November 2026 UTC (21 days; renew by owner decision) |
| External GitHub PR creation, review comments, maintainer contact, merge, fork default/development updates, forced writes | **Not delegated** |

Patch bytes, proposal selection, source/fork SHA, both postimages, GitHub actor, license and ancestry are rechecked by the existing two-file core/REST port before creating a non-overwriting branch reference. No per-action cryptographic signature or repeated operator prompt is required **after** activation. A failed/ambiguous GitHub write is not automatically retried; report actual refs and errors.

### Owner application — not done

- The applicable fork owner must separately choose this precise envelope and record an attributable decision in [Upstream #6](https://github.com/opensiro/upstream/issues/6), including the authorized agent host identity, time bound and human-owned external publication. The `owner_decision_url` must point to that real owner action. The assistant's generic `continue`, an agent-authored comment, a PAT, or a proposed file **is not this decision**.
- After that decision, an authorized owner applies `status: ACTIVE` with the actual decision link to **`opensiro/upstream` default branch `main`**; a subsequent `REVOKED`/expiry immediately denies later actions. Inactive policy values cannot be activated by `--run`, a manifest, local file edit or branch PR alone.
- `BoundedLocalPrepareHost` fetches the observed current `main` head and pinned policy over authenticated GitHub GET **twice** per decision, and the second pass checks for revocation/drift. It binds scope and actual provider actor. Running the stage under the current checked-in proposal returns **BLOCKED_NO_WRITE**.
- The new branch must be absent. The already implemented REST Git Data port only creates it via non-overwriting POST, never updates existing branch refs. All repository writes must use that bounded port, not the naked credential.

### Trust tradeoff (deliberate)

This is a *simple, trust-based* operational contract, **not** a hard sandbox against a compromised executor. The `robot` account with an unrestricted GitHub PAT can in principle call `gh` directly, ignoring a Python allowlist. Owner governance, audit receipts, PAT scope and limited destination repository rights mitigate but **do not eliminate** this possibility. Avoid describing this pilot as technically enforcing a boundary that exists only by voluntary code-path choice.

For stronger threat models, a separately protected token broker/signer would be required; that is deferred as disproportionate to this pilot.

### Existing-VM entry point (never a new service)

Run `python3 scripts/prepare_harnessdesk_local.py --check` for authenticated **GET-only** source/fork/policy preflight. The result reports source/fork SHA and the observed main-policy status without creating a branch.

Only **after** an independently attributable fork-owner decision and application of an ACTIVE policy to owner-repository `main`, run `python3 scripts/prepare_harnessdesk_local.py --prepare`. This re-GETs the current policy, invokes the existing two-file patch stage with actor attestation and exact-source validation, and creates only a new contributor-fork branch if permitted. With the currently proposed policy or missing GitHub main policy the result is `BLOCKED_NO_WRITE`; the command line flag never supplies authorization itself. No external PR is submitted.

### Acceptance and next work

1. Offline positive (test fixture ACTIVE) and negative (repository policy PROPOSED) behavior verified, including revocation, time limit, actor, source, fork, branch, paths, source/base hashes, GitHub main drift and provider re-preflight.
2. Recheck current source and fork; run required upstream `pnpm check:push` and focused regression coverage before any real push. Historical [V2 packet](../pilots/harnessdesk-1772/prepare-v2-20261020-81d5e34-shared.json) remains non-authorizing and must not be rewritten as if it were an accepted grant.
3. With a **real owner-applied** ACTIVE policy, execute the existing two-file writer on the named fork, inspect commit/branch and readback, and produce a complete **unpublished** upstream PR title/body with the tested diff. No external pull request POST.
4. Record a truthful decision/execution/validation/feedback receipt. Do not infer an autonomous S1 grade or Organization S5 admission from this proposal.

If the owner decision, effective default-branch policy, authenticated provider actor, source compatibility or relevant tests cannot be established, remain `BLOCKED_NO_WRITE`.
