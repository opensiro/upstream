# Shared working forks: supervised bootstrap and cross-plugin contribution

**Status: OWNER-SUPERVISED ONE-OFF ROUTE DOCUMENTED; NO BULK FORK WRITES YET.**
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

### Simpler owner-operated route (not autonomous delegation)

The owner may direct a **specific, attended one-time fork-creation batch**
through their already-connected `dev-alpha-2` SSH session and authenticated
GitHub CLI. This follows the proven ad-hoc [HarnessDesk fork
checkpoint](https://github.com/opensiro/upstream/issues/28), not the inactive
automated Control Plane executor. It needs **no new permanent bot, standing
fork-creation policy, custom MCP plugin, GitHub Actions workflow or generic
autonomy permit issuer** when the owner directly selects each exact batch and
controls the operation. It is human-owned execution, **not** evidence that
Upstream has acquired autonomous fork-creation authority.

The conversation phrase `continue`, `оформи` or an agent-selected digest is
**not** sufficient to start a GitHub write. Before an attended run, show the
exact source/destination list, ensure the owner explicitly authorizes that
one list for creation, and recheck the live provider state under the actual
GitHub actor. The owner can observe the command output, stop the process and
choose the next batch; each executed action needs its own receipt. There is
no automatic background execution and no privilege transfer to other agents.

Use the read-only command printer to inspect one group:

```bash
python3 scripts/supervised_fork_plan.py status
python3 scripts/supervised_fork_plan.py show --batch bootstrap-001
```

It only **displays** `gh repo fork` examples, binding the proposed fork name
and destination. It has no `execute` command. After an exact owner decision,
the connected host runs the selected GitHub action in the observed session;
`--default-branch-only` is deliberately omitted so required nondefault
branches are not discarded. A displayed command is not independently proven
safe or approved, and remote checks must precede **every** write.

### Protected automated route — newer standing delegation

The historical one-use **human-granted** automated route below predates
the [2026-11-11 standing preparation mandate](STANDING_PREPARATION_AUTONOMY.md).
For five-source waves with eligible reviewed packets, the host now makes
bound one-use *execution* decisions automatically under a current-main
standing owner policy; it does not ask for a new human vote on each fork
or patch. The technical provider, fork, source and write controls still
apply, and `submit_external_pr` remains human-approved per PR.

Unattended/batch-agent execution using
[`batch_fork_executor.py`](../scripts/batch_fork_executor.py), an automated
Control Plane trigger, or permanent delegated fork-writing rights still
requires the independently authenticated, revocable one-use host grants in
[#6](https://github.com/opensiro/upstream/issues/6) and
[#28](https://github.com/opensiro/upstream/issues/28). The supervised human
route is **not** a substitute attestor that makes those automated paths live.

### Common preflight and readback

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
3. **Authorize a specific batch:** in the supervised route, the authenticated
   owner directly selects the exact list and attended operations; an arbitrary
   model-authored approval or previous one-off session does not authorize
   future lists. In the separate automated route, a trusted one-use,
   expiring, revocable **create_public_fork** permit must bind the actual
   executor/actor and reviewed batch identity. Neither route authorizes
   `prepare_contribution` or a third-party PR.
4. **Execute through the observed host:** `dev-alpha-2` has a registered SSH
   gateway to a VM with GitHub CLI. The exact authenticated actor and
   organization rights must be reattested at write time. For an explicit
   owner-directed supervised batch, run each exact command individually and
   display its result to the owner. Stop on ambiguous partial outcomes,
   403/404, conflicts, changed refs and policy failures; **no blind retry,
   overwrite or unattended continuation**. The protected automated route
   must additionally verify its host grant before writing.
5. **Read back:** independently fetch each destination's public `fork` flag,
   `parent.full_name`, source identity, preserved required branches, actual
   repository URL and write actor permissions. Record partial and negative
   outcomes separately in a dated provider receipt. Reconcile the source/fork
   registry in a reviewable internal PR. An exact fork receipt does not prove
   a subsequent patch or CI result.

The source proposal can be processed as a succession of small human-observed
batches without constructing a separate permanent executor. It is **not** a
plan to run one unbounded shell command against all sources. There is no
automatic requirement to create a fork for negative or historical-only cases.

## Continuous contributions after bootstrap

| Actor | Supported path | Permission boundary |
| --- | --- | --- |
| OpenSiro agent or plugin with an effective fork-write grant | Update a dedicated working branch with exact source and fork SHA checks; retain native CI and readback | A new exact `prepare_contribution` stage decision; never infer it from the bootstrap grant |
| External contributor without organization write rights | Use their own branch/fork in the compatible GitHub fork network, then propose an **internal PR targeting `opensiro-contributions/<name>`** | Normal GitHub author identity and repository PR/CI/review settings; **no shared OpenSiro SSH credentials** |
| OpenSiro maintainer with actual merge rights | Review and integrate the internal PR into the organization's selected working branch | Existing branch protection and required CI; internal approval is not external publication approval |
| Human owner of publication | Review the exact files, upstream-native tests, source base, licensing/CLA/DCO, **target's original PR template/contributor requirements** and the completed title/body; explicitly release **that** external PR | Separate human decision for each external PR; external maintainers own acceptance/merge |

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
python3 scripts/supervised_fork_plan.py show --batch bootstrap-001
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

Unattended automation remains a separate reviewed authority + host connection
task under [#6](https://github.com/opensiro/upstream/issues/6) /
[#28](https://github.com/opensiro/upstream/issues/28). An actual supervised
bootstrap still requires a **new exact owner instruction for the selected
batch** and live safety checks; this change itself grants neither.
