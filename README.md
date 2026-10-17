# OpenSiro — upstream contributions

This repository is the public **portfolio and lifecycle registry** for OpenSiro's contributions to third-party open-source projects.

It is **not** a monorepo of forks, a mirror of upstream code, a claim of upstream endorsement, or a new organizational control plane. Each working fork remains a separate GitHub repository.

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

## Contributions

For a new project, add a record to `registry.yaml` and a short `projects/<slug>/README.md`. See [CONTRIBUTING.md](CONTRIBUTING.md).

This registry is maintained independently from Cognee's own repositories. Draft work in OpenSiro forks must not be represented as an upstream PR or merge.
