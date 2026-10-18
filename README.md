# OpenSiro — upstream contributions

This repository is the public **portfolio and lifecycle registry** for OpenSiro's contributions to third-party open-source projects.

It is **not** a monorepo of forks, a mirror of upstream code, a claim of upstream endorsement, or a new organizational control plane. Each working fork remains a separate GitHub repository.

## Public impact dashboard

**[Open the Upstream Dashboard →](DASHBOARD.md)** — readable on GitHub. It shows the eight experimental upstream interventions, outcomes, product-native fit (currently **60% of completed fit reviews**), primary PR evidence, and snapshot dates. For a standalone interactive, filterable browser view see [`docs/index.html`](docs/index.html) (HTML file; GitHub Pages publishing is not enabled by these files).

These are **dated experiment measurements, not live acceptance rates or productivity scores**. The [Organization-owned snapshot](https://github.com/opensiro/vsm-oss-organization/blob/main/experiments/upstream-intervention-fit/snapshot.json) is authoritative; the dashboard is a pinned public presentation.

## Current work

| External project | OpenSiro fork | Contribution | Upstream status | Fork lifecycle |
| --- | --- | --- | --- | --- |
| [Cognee Community](https://github.com/topoteretes/cognee-community) | [opensiro/cognee-community](https://github.com/opensiro/cognee-community) | [Canonical OpenSiro VSM assessment source](projects/cognee/README.md) | **Not submitted** | **Active** |

Machine-readable current state: [`registry.yaml`](registry.yaml). Research and testing evidence is linked in project profiles.

## Assessment-shaped external intervention cases

A separate [product-native fit casebook](cases/README.md) documents **eight** publicly evidenced interventions into other OSS harnesses that originated from or were shaped by OpenSiro assessment/research. It includes accepted, still-open, and unsuccessful work. Most are in **personal contributor forks**, not OpenSiro-owned forks, so their fork-maintenance state is **not** inferred or added to `registry.yaml`.

The [Organization experimental ledger](https://github.com/opensiro/vsm-oss-organization/tree/main/experiments/upstream-intervention-fit) remains the source of truth for the four fit gates, participant attribution and deduplication. The casebook is a linked portfolio view, **not** an upstream endorsement, an acceptance rate or a VSM grade claim.

## Two independent status dimensions

**Contribution outcome** tracks the result *at upstream*: `research`, `preparing`, `submitted`, `merged`, `closed`, or `not-accepted`. Only a verified upstream merge is marked `merged`.

**Fork lifecycle** tracks the OpenSiro repository itself: `active`, `maintained`, or `archived`. An archived fork does **not** imply that its upstream contribution was accepted.

Typical sequence: **Fork → Research → Implement → Submit → Upstream outcome → Maintain or archive**. Projects can stay `maintained` indefinitely.

## Archiving policy

Before archiving an inactive fork, verify that its planned PRs are resolved or intentionally closed, no known maintenance obligations remain, and this registry contains its final outcome and upstream links. Archive the **public GitHub fork**, retaining its history; do not silently delete it. A need for continued maintenance is reason to keep it active. A fork may be unarchived if maintenance resumes.

The archived state is an explicit decision, **not an automatic action triggered by merged PRs**.

## Conversation-first contribution proposals (read-only)

[Batch proposal preview](docs/BATCH_PROPOSALS.md) is a **provider-agnostic,
local-only** way to review up to ten possible contributions before an owner
approves anything. Every candidate states the target system's problem,
planned change, **expected (unverified) benefit**, validation and evidence.
It can display the operator's **proposed selection** in JSON or plain text.

```bash
python3 scripts/batch_proposals.py --manifest /path/to/upstream-YYYYMMDD-name.json --draft --select candidate-a,candidate-c --scope 'candidate-a=create_public_fork' --format text
```

The optional `--scope` can **reduce** the stages proposed for each
selected candidate; it cannot add a new action. Without it, a selected
candidate retains all proposed stages for preview. The result includes
`selection_scope_sha256` binding the exact per-candidate stage subset.

This command never contacts GitHub, creates forks, publishes external PRs
or records an approval. Selection and SHA-256 identifiers are **not**
authorization. See [the proposal schema and limitations](docs/BATCH_PROPOSALS.md).

## Fork lifecycle automation

The manually dispatched [fork lifecycle workflow](.github/workflows/fork-lifecycle.yml)
is **preview-only on `main`** after [PR #8](https://github.com/opensiro/upstream/pull/8).
It no longer offers an `execute` input, privileged create job or credential
reference. The old [fork lifecycle handoff](docs/FORK_LIFECYCLE.md) is historical
and **not** a deployment checklist.

[Activation issue #6](https://github.com/opensiro/upstream/issues/6)
tracks future execution. The [non-executable authorization and stage contract](docs/BATCH_EXECUTION_BOUNDARY.md)
specifies how a same-session connected agent or separately verified
headless runner could accept **one exact operator decision** without
conflating chat selection with GitHub permissions. The old
[Draft PR #7](https://github.com/opensiro/upstream/pull/7) is superseded
by the merged preview and is **not merge-ready**.

A narrowly limited [connected-stage preparation adapter](docs/CONNECTED_STAGE_ADAPTER.md)
now supplies **source-prepared, mock-tested** one-file test preparation in an
existing writable fork, gated by a trusted session authorization callback.
It is **not connected to a live host** and **not an approved contribution**;
no fork or external PR execution is enabled. It remains under Issue #6.

**Do not provision `UPSTREAM_FORK_TOKEN` or execute demonstration batch #001.**
Neither proposal preview nor fork planning grants external PR publication,
archiving or a new VSM OSS organizational boundary.

## Contributions

For a new project, add a record to `registry.yaml` and a short `projects/<slug>/README.md`. See [CONTRIBUTING.md](CONTRIBUTING.md).

This registry is maintained independently from Cognee's own repositories. Draft work in OpenSiro forks must not be represented as an upstream PR or merge.
