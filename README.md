# OpenSiro Upstream Contributions

**OpenSiro's public record of improvements to other open-source projects.** We trace a contribution from a reproducible problem and source-native fix through its external pull request, maintainer feedback and independently verified outcome. A prepared patch is not a merged contribution, and a merged PR is not automatically a demonstrated product benefit.

## I'm human

| I want to… | Go to |
| --- | --- |
| Understand the broader OpenSiro project | [Visual VSM map](https://opensiro.com/vsm.html) |
| See contributions and what happened to them | [Public portfolio](https://opensiro.com/upstream-portfolio.html) · [GitHub dashboard](DASHBOARD.md) · [Harness status](HARNESS_STATUS.md) |
| Inspect actual third-party PRs | [Citadel #366](https://github.com/SethGammon/Citadel/pull/366) · [Agent Fleet #43](https://github.com/chankov/agent-fleet/pull/43) · [PR observation and verification rules](docs/VERIFIED_EXTERNAL_OUTCOMES.md) |
| Review source-backed evidence | [Casebook](cases/README.md) · [Native test pilots](pilots/README.md) |
| Contribute or maintain this project | [CONTRIBUTING.md](CONTRIBUTING.md) · [UPSTREAMING.md](UPSTREAMING.md) |

The [dashboard](DASHBOARD.md) and [portfolio](https://opensiro.com/upstream-portfolio.html) are projections, not authority for a third-party PR's live state. Consult the exact GitHub PR for current disposition. Our [verified-outcomes process](docs/VERIFIED_EXTERNAL_OUTCOMES.md) distinguishes machine evidence candidates from accepted outcomes; **no Organization-wide external-outcomes KPI has been claimed yet**.

## I'm AI

**One route:** [OpenSiro START_HERE](https://github.com/opensiro/vsm-oss-organization/blob/main/START_HERE.md) → [ecosystem ownership](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/ECOSYSTEM.md) → [AGENTS.md](AGENTS.md) → [UPSTREAMING.md](UPSTREAMING.md) → **exact current issue/PR**. Use the [Organization TODO](https://github.com/opensiro/vsm-oss-organization/blob/main/TODO.md) only for selected shared work, not as a substitute for the owning issue. New or cross-domain tasks start with [CONTRIBUTOR_START](https://github.com/opensiro/vsm-oss-organization/blob/main/CONTRIBUTOR_START.md).

For the common operations:

| Work | Procedure |
| --- | --- |
| Screen five sources and select a testable improvement | [Assessment candidate batches](docs/ASSESSMENT_CANDIDATE_BATCHES.md) |
| Prepare source code, native tests, and the fork-local PR | [Working-fork pipeline](docs/CONTINUOUS_WORKING_FORK_PIPELINE.md) |
| Publish a qualifying external PR | [Standing publication policy](docs/STANDING_EXTERNAL_PR_PUBLICATION.md) |
| Observe feedback, states, and outcomes | [PR maintenance](docs/PR_MAINTENANCE.md) · [Verified outcomes](docs/VERIFIED_EXTERNAL_OUTCOMES.md) |
| Operate this repository's own Actions | [Actions map](docs/ACTIONS.md) · [Operations](docs/OPERATIONS.md) |

**Where work belongs:** actual patches, tests, and proposed external PR bodies belong in the matching `opensiro-contributions/<target>` fork. This repository holds governance, historical test evidence, registries, observations and derived dashboards. [Source-of-truth contract](UPSTREAMING.md#source-of-truth-separation). Index owns canonical VSM assessments; Skills owns their methodology; Profile owns VSM semantics.

An **Index assessment** can lead to the strict [assessment-derived S1 test](docs/ASSESSMENT_DRIVEN_S1_TEST.md); the separate [generic OSS preview](docs/BATCH_PROPOSALS.md) does not prove an assessment-derived fix. The historical [OSM delegation design](docs/OSM_DELEGATION_DESIGN.md) does **not** grant host execution rights; see [automatic fork executor recovery](docs/AUTOMATIC_FORK_EXECUTOR_RECOVERY.md) for the specific technical gate.

Effective [standing preparation](docs/STANDING_PREPARATION_AUTONOMY.md) and [publication](docs/STANDING_EXTERNAL_PR_PUBLICATION.md) mandates remove repetitive owner prompts for qualifying operations. They do **not** supply missing host credentials, waive source-native CI, target contribution policies, legal attestations or third-party merge authority. Check current policies and permissions before writing. [Executor gate #6](https://github.com/opensiro/upstream/issues/6).

## Validate locally

```sh
python3 -m unittest discover -s tests -v
python3 scripts/upstream_status.py --check-generated
python3 scripts/harness_status.py --check
python3 scripts/portfolio_reconcile.py --validate-only
python3 scripts/verified_external_outcomes.py --validate-only
```

The unfiltered [repository-integrity workflow](.github/workflows/repository-integrity.yml) runs unit tests and generated-inventory checks on every PR. Third-party source-native CI belongs in working forks; [migration #214](https://github.com/opensiro/upstream/issues/214) has completed **placement**, not universal native parity.

**Legal boundary:** no repository-wide root LICENSE has been adopted. [Standards #130](https://github.com/opensiro/upstream/issues/130) and [license draft PR #1](https://github.com/opensiro/upstream/pull/1) require the actual rightsholders' decision; do not relicense third-party code or original prose by inference.
