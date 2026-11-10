# OpenSiro Upstream Contributions

OpenSiro's public, evidence-backed record of contributions to **third-party open-source projects**: what was investigated, what was prepared or submitted, what maintainers did, and what remains unresolved.

This repository is a **contribution portfolio and operating system**, not a fork monorepo, upstream endorsement, VSM assessment index, or an independent authority to publish changes into other projects.

## I'm human

| I want to… | Start here |
| --- | --- |
| Explore the contribution portfolio | [public source-dated PR metrics](https://opensiro.com/upstream-portfolio.html) · [GitHub dashboard](DASHBOARD.md) · [cross-lane harness status](HARNESS_STATUS.md) |
| See OpenSiro-owned working forks | [registry.yaml](registry.yaml) · [project records](projects/) |
| Track the 100 priority targets and previously screened sources | [continuous working-fork pipeline](docs/CONTINUOUS_WORKING_FORK_PIPELINE.md) · [generated inventory](data/contribution-workspaces/registry.json) · [supervised fork bootstrap proposal](docs/FORK_BOOTSTRAP_AND_COLLABORATION.md) |
| Examine interventions and evidence | [casebook](cases/README.md) · [technical pilots](pilots/README.md) |
| Follow external pull requests | [PR maintenance](docs/PR_MAINTENANCE.md) · [resolved-PR metric](docs/RESOLVED_PR_ACCEPTANCE.md) · [verified external outcome evidence](docs/VERIFIED_EXTERNAL_OUTCOMES.md) |
| Propose or review a contribution | [CONTRIBUTING.md](CONTRIBUTING.md) · [Upstream operating contract](UPSTREAMING.md) |
| Understand architecture or automation | [Documentation map](docs/README.md) · [operations](docs/OPERATIONS.md) |

The dashboards are **dated, generated views**. The public website is a consumer of this repository's read-only PR observer, not the owner of a new adoption metric. For the latest merge, closure or review outcome, inspect the linked external GitHub PR. An unavailable PR is not automatically a rejection.

## I'm AI

Follow the current OpenSiro [START_HERE.md](https://github.com/opensiro/vsm-oss-organization/blob/main/START_HERE.md) → [ecosystem owner map](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/ECOSYSTEM.md) → the exact owning issue/PR. Read this repository's [AGENTS.md](AGENTS.md) and [UPSTREAMING.md](UPSTREAMING.md) before modifying any data or automation.

- **Already scheduled work:** [Organization TODO.md](https://github.com/opensiro/vsm-oss-organization/blob/main/TODO.md). An arbitrary open PR does not become the next scheduled task.
- **New, unclassified or cross-domain work:** [Organization contributor entry](https://github.com/opensiro/vsm-oss-organization/blob/main/CONTRIBUTOR_START.md).
- **Upstream-owned work:** the specific local issue/PR defines the evidence, frozen inputs, tests and authorization boundary. [PR portfolio triage #150](https://github.com/opensiro/upstream/issues/150) and [repository standards #130](https://github.com/opensiro/upstream/issues/130) are review queues, not instructions to merge, close or delete.

## What belongs here

| Surface | Responsibility | Source of truth |
| --- | --- | --- |
| `registry.yaml`, `projects/` | OpenSiro-owned forks, individual contribution status and fork maintenance | Reviewed local records corroborated by the external PR/fork |
| `data/assessment-candidate-batches/` | Pinned five-source technical screening batches and dispositions | Frozen batch manifests; [batch contract](docs/ASSESSMENT_CANDIDATE_BATCHES.md) |
| `pilots/`, `cases/` | Patches, native replay receipts and the historical eight-intervention experiment view | Pinned product-native evidence; [Organization fit experiment](https://github.com/opensiro/vsm-oss-organization/tree/main/experiments/upstream-intervention-fit) owns fit |
| `data/corrective-publication/`, `data/improvement-publication/` | Separate finite publication cohorts | Their own explicitly bounded grants and ledgers |
| `data/pr-maintenance/` | Explicitly reviewed external PR watchlist | Exact external PRs; [watcher](docs/PR_MAINTENANCE.md) |
| `scripts/`, `tests/`, `.github/workflows/` | Deterministic checks, read-only sensing and explicitly gated operations | Source code and CI; [operations](docs/OPERATIONS.md) |
| `DASHBOARD.md`, `HARNESS_STATUS.md`, `docs/index.html` | Generated portfolio projections | Their input ledgers and renderers, not manual edits |

See [UPSTREAMING.md](UPSTREAMING.md) for the full ownership and lifecycle rules. The Index owns canonical VSM harness assessments; [Skills](https://github.com/opensiro/vsm-harness-skills) owns assessment methodology; [Profile](https://github.com/opensiro/vsm-harness-profile) owns VSM semantics.

## Distinct evidence layers

1. **External PR lifecycle:** open, merged, closed without merge, or unverifiable. Verified at the exact external PR; closure is not necessarily maintainer rejection.
2. **Product-native technical effect:** reproduced and measured separately, using deterministic source-native tests—not live LLM or browser-agent quality trials. See [functional effects](docs/FUNCTIONAL_EFFECTS.md) and [assessment-to-improvement](docs/ASSESSMENT_TO_IMPROVEMENT.md).
3. **Verified external outcome:** externally accepted contribution with source-pinned native evidence and attributable first-party disposition. A [new read-only verifier](docs/VERIFIED_EXTERNAL_OUTCOMES.md) emits evidence **candidates**; Organization has **not** yet claimed its primary metric or inferred deployed benefit.
4. **Deprecated historical Product-native fit:** the original four-gate study is preserved under Organization for archival reproduction only; it is **not an active metric** and is not recomputed from merge counts. This does not remove source-native engineering diligence.

The operational [resolved-PR acceptance](docs/RESOLVED_PR_ACCEPTANCE.md) concerns its own **18 explicitly watched PRs**, with the formula `merged / (merged + closed_unmerged)`; pending and unverifiable PRs are excluded. A broader portfolio reconciliation must keep its different denominator and intervention identities explicit. The [2026-11-07 closure-attribution report](reports/2026-11-07-external-pr-closure-attribution.md) documents reviewed reasons, separate from machine-observed events.

An **Index assessment** can motivate the separate [assessment-driven S1 function test](docs/ASSESSMENT_DRIVEN_S1_TEST.md), which starts from pinned canonical evidence and asks whether a source-native change is worthwhile. This is distinct from the [generic OSS proposal preview](docs/BATCH_PROPOSALS.md), including ordinary issue-driven improvement work. Neither workflow grants external publication rights.

## Operating boundary

Upstream Contributions is the **fourth admitted S1 domain** within OpenSiro's public OSS boundary ([Organization #274](https://github.com/opensiro/vsm-oss-organization/issues/274)). That does **not** grant third-party repository write rights, automatic external PR publication/merge, independent S3/S3* authority, or a VSM autonomy grade.

Source preparation, offline native tests and GitHub read-only observation are distinct from privileged actions. The finite [Corrective publication mandate](docs/CORRECTIVE_PR_PUBLICATION.md) does not activate the general [fork executor](docs/AUTOMATIC_FORK_EXECUTOR_RECOVERY.md); [Issue #6](https://github.com/opensiro/upstream/issues/6) owns that separate gate. Never treat a selected batch, an approval text in a file or a successful unit test as an effective external write grant.

The proposed autonomy-transfer model at [docs/OSM_DELEGATION_DESIGN.md](docs/OSM_DELEGATION_DESIGN.md) is **design only**, not an issued standing mandate.

## Validate locally

```bash
python3 -m unittest discover -s tests -v
python3 scripts/upstream_status.py --check-generated
python3 scripts/harness_status.py --check
python3 scripts/pr_maintenance_watch.py --validate-only
python3 scripts/resolved_pr_acceptance.py --validate-only
python3 scripts/portfolio_reconcile.py --validate-only
python3 scripts/verified_external_outcomes.py --validate-only
```

External live checks and issue-inbox updates are **separate** opt-in or scheduled operations; see [operations](docs/OPERATIONS.md). Do not edit generated files by hand.

## Contribution and license policy

Use [CONTRIBUTING.md](CONTRIBUTING.md) for local records, [UPSTREAMING.md](UPSTREAMING.md) for source precedence and [repository standards #130](https://github.com/opensiro/upstream/issues/130) for the unresolved original-code/documentation license choice. **No root LICENSE has been adopted yet.** Do not infer permission to relicense third-party patches or original prose, and do not silently merge the proposed [license PR #1](https://github.com/opensiro/upstream/pull/1).
