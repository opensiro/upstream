# OpenSiro Upstream Contributions

OpenSiro's public, evidence-backed record of contributions to **third-party open-source projects**: what was investigated, what was prepared or submitted, what maintainers did, and what remains unresolved.

This repository is the **evidence and coordination layer**, not a fork monorepo, upstream endorsement, VSM assessment index, or independent authority to publish changes into other projects. Actual contribution code, target-native CI and unpublished external PR proposals live in the matching `opensiro-contributions` working fork.

## I'm AI

Follow the current OpenSiro [START_HERE.md](https://github.com/opensiro/vsm-oss-organization/blob/main/START_HERE.md) → [ecosystem owner map](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/ECOSYSTEM.md) → the exact owning issue/PR. Read this repository's [AGENTS.md](AGENTS.md) and [UPSTREAMING.md](UPSTREAMING.md) before modifying any data or automation.

- **Already scheduled work:** [Organization TODO.md](https://github.com/opensiro/vsm-oss-organization/blob/main/TODO.md). An arbitrary open PR does not become the next scheduled task.
- **New, unclassified or cross-domain work:** [Organization contributor entry](https://github.com/opensiro/vsm-oss-organization/blob/main/CONTRIBUTOR_START.md).
- **Upstream-owned work:** the specific local issue/PR defines the evidence, frozen inputs, tests and authorization boundary. [PR portfolio triage #150](https://github.com/opensiro/upstream/issues/150) and [repository standards #130](https://github.com/opensiro/upstream/issues/130) are review queues, not instructions to merge, close or delete.

| Intent | Current operational route |
| --- | --- |
| Find or prioritize an improvement | [Candidate batches](docs/ASSESSMENT_CANDIDATE_BATCHES.md) · [assessment → improvement](docs/ASSESSMENT_TO_IMPROVEMENT.md) |
| Prepare a patch, native tests and an unpublished PR proposal | [Five-source working-fork pipeline](docs/CONTINUOUS_WORKING_FORK_PIPELINE.md) · [standing preparation policy and limits](docs/STANDING_PREPARATION_AUTONOMY.md) · [native CI placement](docs/NATIVE_CI_EXECUTION.md) |
| Publish an external PR | [Standing publication mandate and non-waivable checks](docs/STANDING_EXTERNAL_PR_PUBLICATION.md) · [fork-local proposal contract](UPSTREAMING.md#contribution-lifecycle) · [AI disclosure](docs/AI_ASSISTED_PR_DISCLOSURE.md) |
| Observe PRs and outcomes | [PR maintenance](docs/PR_MAINTENANCE.md) · [verified outcomes](docs/VERIFIED_EXTERNAL_OUTCOMES.md) |
| Find the right GitHub Action | [Action ownership and migration map](docs/ACTIONS.md) |

Routine fork creation, patch preparation and qualifying external PR publication **do not require a fresh user approval for each step** under their distinct current standing mandates and an authenticated, capable execution host. An unavailable host capability or unmet native gate is a technical blocker, not a new human-approval request.

## I'm human

| I want to… | Start here |
| --- | --- |
| I don't understand any of this | [Show me the visual map](https://opensiro.com/vsm.html) — a direct, illustrated introduction to the VSM approach |
| Browse external contributions and outcomes | [Public portfolio](https://opensiro.com/upstream-portfolio.html) · [GitHub dashboard](DASHBOARD.md) · [harness status](HARNESS_STATUS.md) |
| See working forks and priority targets | [registry.yaml](registry.yaml) · [generated working-fork inventory](data/contribution-workspaces/registry.json) |
| Examine technical evidence | [Casebook](cases/README.md) · [pilots](pilots/README.md) |
| Contribute or review | [CONTRIBUTING.md](CONTRIBUTING.md) · [UPSTREAMING.md](UPSTREAMING.md) |
| Understand the infrastructure | [Documentation map](docs/README.md) · [Actions map](docs/ACTIONS.md) |

Dashboards are **dated generated views**; for the latest status, follow the exact external GitHub PR. The website consumes read-only observations and does not establish an adoption metric. An unavailable PR is not automatically a rejection.

## What belongs here

| Surface | Responsibility | Source of truth |
| --- | --- | --- |
| `registry.yaml`, `projects/` | OpenSiro-owned forks, individual contribution status and fork maintenance | Reviewed local records corroborated by the external PR/fork |
| `data/assessment-candidate-batches/` | Pinned five-source technical screening batches and dispositions | Frozen batch manifests; [batch contract](docs/ASSESSMENT_CANDIDATE_BATCHES.md) |
| `pilots/`, `cases/` | Historical patches, reproducible native replay packets and technical receipts; **not** the live outgoing contribution branch | Pinned product-native evidence; [Organization fit experiment](https://github.com/opensiro/vsm-oss-organization/tree/main/experiments/upstream-intervention-fit) owns historical fit |
| `data/corrective-publication/`, `data/improvement-publication/` | Separate finite publication cohorts | Their own explicitly bounded grants and ledgers |
| `data/pr-maintenance/` | Explicitly reviewed external PR watchlist | Exact external PRs; [watcher](docs/PR_MAINTENANCE.md) |
| `scripts/`, `tests/`, `.github/workflows/` | Upstream's own deterministic checks, sensing and gated operations; legacy per-harness workflows await retirement | [Actions ownership map](docs/ACTIONS.md) · [migration #214](https://github.com/opensiro/upstream/issues/214) |
| `DASHBOARD.md`, `HARNESS_STATUS.md`, `docs/index.html` | Generated portfolio projections | Their input ledgers and renderers, not manual edits |
| `opensiro-contributions/<target>` (separate repository) | Current source-native patch, tests, branch-specific CI and **one fork-local PR** containing the proposed external title/body | Verified working-fork branch, head SHA and fork-local PR; [UPSTREAMING.md](UPSTREAMING.md#source-of-truth-separation) |

See [UPSTREAMING.md](UPSTREAMING.md) for the full ownership and lifecycle rules. The Index owns canonical VSM harness assessments; [Skills](https://github.com/opensiro/vsm-harness-skills) owns assessment methodology; [Profile](https://github.com/opensiro/vsm-harness-profile) owns VSM semantics.

## Distinct evidence layers

1. **External PR lifecycle:** open, merged, closed without merge, or unverifiable. Verified at the exact external PR; closure is not necessarily maintainer rejection.
2. **Product-native technical effect:** reproduced and measured separately, using deterministic source-native tests—not live LLM or browser-agent quality trials. See [functional effects](docs/FUNCTIONAL_EFFECTS.md) and [assessment-to-improvement](docs/ASSESSMENT_TO_IMPROVEMENT.md).
3. **Verified external outcome:** externally accepted contribution with source-pinned native evidence and attributable first-party disposition. A [new read-only verifier](docs/VERIFIED_EXTERNAL_OUTCOMES.md) emits evidence **candidates**; Organization has **not** yet claimed its primary metric or inferred deployed benefit.
4. **Deprecated historical Product-native fit:** the original four-gate study is preserved under Organization for archival reproduction only; it is **not an active metric** and is not recomputed from merge counts. This does not remove source-native engineering diligence.

The operational [resolved-PR acceptance](docs/RESOLVED_PR_ACCEPTANCE.md) concerns its own **18 explicitly watched PRs**, with the formula `merged / (merged + closed_unmerged)`; pending and unverifiable PRs are excluded. A broader portfolio reconciliation must keep its different denominator and intervention identities explicit. The [2026-11-07 closure-attribution report](reports/2026-11-07-external-pr-closure-attribution.md) documents reviewed reasons, separate from machine-observed events.

An **Index assessment** can motivate the separate [assessment-driven S1 function test](docs/ASSESSMENT_DRIVEN_S1_TEST.md), which starts from pinned canonical evidence and asks whether a source-native change is worthwhile. This is distinct from the [generic OSS proposal preview](docs/BATCH_PROPOSALS.md), including ordinary issue-driven improvement work. Neither workflow grants external publication rights.

## Operating boundary

Upstream Contributions is the **fourth admitted S1 domain** within OpenSiro's public OSS boundary ([Organization #274](https://github.com/opensiro/vsm-oss-organization/issues/274)). S1 admission does **not** grant third-party repository write or merge rights, independent S3/S3* authority, or a VSM autonomy grade by itself. A separate, revocable owner mandate now permits **qualifying external PR submissions** after the specific checks below; it never grants third-party merge rights.

Source preparation, offline native tests and GitHub read-only observation are distinct from privileged actions. The finite [Corrective publication mandate](docs/CORRECTIVE_PR_PUBLICATION.md) does not activate the general [fork executor](docs/AUTOMATIC_FORK_EXECUTOR_RECOVERY.md); [Issue #6](https://github.com/opensiro/upstream/issues/6) owns that separate gate. Never treat a selected batch, an approval text in a file or a successful unit test as an effective external write grant.

The broader transfer model in [docs/OSM_DELEGATION_DESIGN.md](docs/OSM_DELEGATION_DESIGN.md) remains a design. **Separately**, the owner has issued a narrow, revocable [standing preparation mandate](docs/STANDING_PREPARATION_AUTONOMY.md), recorded in [policy](policies/standing-preparation-p1.json), and a distinct [standing external-PR publication mandate](docs/STANDING_EXTERNAL_PR_PUBLICATION.md), recorded in [policy](policies/standing-external-publication-p1.json), both bounded by [#6](https://github.com/opensiro/upstream/issues/6). These remove repeated routine owner prompts but do **not** grant unrestricted writes, waive third-party policy or prove that a connected executor can perform every stage.

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
