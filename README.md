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

## Fork lifecycle automation

[Conversation-first batch approval design](docs/CHAT_BATCH_APPROVAL.md) is the selected **provider-agnostic conversational interface**: propose a bounded contribution batch in any compatible agent chat, accept only the owner's selected items, record the decision, and execute only that exact authorized set. GitHub is the executor, not the approval interface. No ChatGPT-specific runtime or service is required.

Every proposed contribution includes a **concrete system improvement card**: target component, observed problem, planned change, expected benefit, verification method and public evidence. The plan is visible before selection and becomes part of the frozen batch scope; predicted benefits are not reported as verified outcomes. See [contribution proposal fields](docs/CHAT_BATCH_APPROVAL.md#required-contribution-proposal--what-the-system-would-gain).

The former single-fork workflow is now **preview-only on `main`** after [safety PR #8](https://github.com/opensiro/upstream/pull/8). It no longer offers `execute=true`, a privileged `create` job or a token reference. The [historical lifecycle handoff](docs/FORK_LIFECYCLE.md) is not an activation procedure. The [batch proposal and read-only validator](docs/CHAT_BATCH_APPROVAL.md) remain **Draft in PR #7**; no trusted batch-only executor or committed batch-specific CI exists. Do **not** provision `UPSTREAM_FORK_TOKEN`. Track remaining gates in [activation issue #6](https://github.com/opensiro/upstream/issues/6). Neither the design nor code authorizes external PR submission or changes the VSM OSS system boundary.

## Contributions

For a new project, add a record to `registry.yaml` and a short `projects/<slug>/README.md`. See [CONTRIBUTING.md](CONTRIBUTING.md).

This registry is maintained independently from Cognee's own repositories. Draft work in OpenSiro forks must not be represented as an upstream PR or merge.
