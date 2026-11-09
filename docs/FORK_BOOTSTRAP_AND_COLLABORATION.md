# Shared working forks: supervised bootstrap and cross-plugin contribution

**Status: REVIEWABLE DESIGN / READ-ONLY PROPOSAL; NO BULK FORK WRITES ACTIVE.**
**Owner:** [Upstream #28](https://github.com/opensiro/upstream/issues/28)
under the [#6 protected executor boundary](https://github.com/opensiro/upstream/issues/6).
**Destination:** public GitHub organization `opensiro-contributions`.
**External PR publication:** an explicit human decision for **each exact PR**.

## Why bootstrap once

An organization fork is a durable shared GitHub repository. Once created and
independently verified, all future interventions for that source should reuse
it rather than creating a fresh fork for each agent, plugin or batch. The code
and PR history live in GitHub; the OpenSiro [working-fork registry](../data/contribution-workspaces/registry.json)
owns the source-to-fork identity and the Upstream repo preserves source-native
patch/test evidence. No contributor's individual chat or plugin is the source
of truth for another contributor's work.

The [generated bootstrap proposal](../data/contribution-workspaces/fork-bootstrap-proposal.json)
consumes the frozen first-100 snapshot **and all previously worked sources**.
It may propose an unoccupied destination name, but it never reserves that
name, attests GitHub state, or authorizes creating a fork. Historical forks
are *reuse/recheck* cases. Closed-without-change, insufficient-evidence and
historical PR-only cases stay visible without being forced into a new fork.
Unresolved license cases are held. Adding a source to this proposal is **not**
approval to fork it or evidence that its code needs fixing.

## Human-supervised initial bootstrap

1. **Prepare:** run `python3 scripts/contribution_workspaces.py check` and
   `python3 scripts/fork_bootstrap_manifest.py check`; inspect the resulting
   catalog, holds, name proposals and groups of at most ten eligible sources.
   Each group's `selection_sha256` binds its exact proposed source→destination
   pairs, operation, destination organization and inventory digest. This hash
   is **not a signature or authorization**.
2. **Review every selected source:** obtain fresh GitHub source identity,
   public-fork eligibility, license and source policy; check *actual* org
   destination absence or matching `parent.full_name`, default and required
   nondefault branches, exact SHA, existing PRs and prior interventions.
   Names constructed as `source-owner--repo` resolve only a **local basename
   ambiguity**; actual GitHub occupancy and parent must still be checked.
   A changed source, policy, destination or selection means stop/reselect.
3. **Approve a specific batch:** the legitimate human operator approves the
   exact source/destination/stage scope through an independently authenticated
   control, not via a model-authored `approved_by`, a digest, an unsigned issue
   comment or a generic `continue`. A trusted one-use, expiring, revocable
   **create_public_fork** permit must bind the executor/actor and reviewed
   batch identity. A batch grant cannot authorize `prepare_contribution` or
   a third-party PR. The local proposal has **no such grant**.
4. **Execute through the controlled host:** `dev-alpha-2` has a registered SSH
   gateway to a VM with GitHub CLI; using it as the actual write transport is
   viable only after the [#6/#28](https://github.com/opensiro/upstream/issues/6)
   host-identity/rights and one-use permit checks are effectively connected.
   The exact host actor and organization rights must be reattested at write
   time. The executor creates or reuses one direct public fork per approved
   item. It must stop on ambiguous partial outcomes, 403/404, conflicts,
   changed refs and policy failures; **no blind retry or overwrite**.
5. **Read back:** independently fetch each destination's public `fork` flag,
   `parent.full_name`, source identity, preserved required branches, actual
   repository URL and write actor permissions. Record partial and negative
   outcomes separately in a dated provider receipt. Reconcile the source/fork
   registry in a reviewable internal PR. An exact fork receipt does not prove
   a subsequent patch or CI result.

The source proposal can be processed as a succession of small human-observed
batches. It is **not** a plan to run one unbounded shell command against all
sources. There is no automatic requirement to create a fork for negative or
historical-only cases.

## Continuous contributions after bootstrap

| Actor | Supported path | Permission boundary |
| --- | --- | --- |
| OpenSiro agent or plugin with an effective fork-write grant | Update a dedicated working branch with exact source and fork SHA checks; retain native CI and readback | A new exact `prepare_contribution` stage decision; never infer it from the bootstrap grant |
| External contributor without organization write rights | Use their own branch/fork in the compatible GitHub fork network, then propose an **internal PR targeting `opensiro-contributions/<name>`** | Normal GitHub author identity and repository PR/CI/review settings; **no shared OpenSiro SSH credentials** |
| OpenSiro maintainer with actual merge rights | Review and integrate the internal PR into the organization's selected working branch | Existing branch protection and required CI; internal approval is not external publication approval |
| Human owner of publication | Review the exact files, upstream-native tests, source base, licensing/CLA/DCO and proposed title/body; explicitly release **that** external PR | Separate human decision for each external PR; external maintainers own acceptance/merge |

An internal PR into an OpenSiro-owned fork and a PR **from** that fork **to**
the third-party parent are different operations. Neither a prior contributor
approval nor a successful internal CI run grants external publication rights.
The `upstream auto` and `upstream upgrade batch` commands may produce and
update internal handoffs, but cannot silently publish to external projects.

For multiple plugins working concurrently, use the same source identity and
one reviewed branch/PR per intervention. The Upstream registry and GitHub
source/fork/branch IDs are shared, not opaque plugin session IDs. Coordinate
colliding work by source/branch reservations and GitHub PR conflict checks;
avoid direct pushes to a shared default branch. Plugin accounts retain their
own independent GitHub access and must never borrow the maintainer's token.

## Offline commands and integration

```bash
python3 scripts/contribution_workspaces.py status
python3 scripts/fork_bootstrap_manifest.py status
python3 scripts/fork_bootstrap_manifest.py sync
python3 scripts/fork_bootstrap_manifest.py check
```

Both `sync` commands are deterministic local generation only. The `check`
commands run in the always-on internal repository-integrity CI job. If a
screen, added source or pilot changes the registry, the bootstrap proposal
must be regenerated **in the same internal PR**. Previously reviewed or
executed batch signatures do not silently carry over to a changed proposal.

### Explicitly not provided by this change

- No new registered SSH device, PAT, GitHub App, service account, workflow
  environment, trust bridge or active `dev-alpha-2` autonomy policy.
- No trusted `create_public_fork` or `prepare_contribution` permit issuer.
- No remote fork creation, fork branch update, internal PR, external PR,
  external comment or protected-branch merge.
- No claim that local name proposals are available on GitHub or that all
  catalogued sources are currently eligible for forking.

Activation is a separate reviewed authority + host connection task under
[#6](https://github.com/opensiro/upstream/issues/6) / [#28](https://github.com/opensiro/upstream/issues/28).
