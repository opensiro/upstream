# Upstream contributions — Dashboard

> **External PR sources checked:** 2026-11-05T17:36:18+00:00 · **Archived intervention cohort:** 2026-10-12.
> Lifecycle is a dated public GitHub observation. The former Product-native fit KPI is **deprecated** and is not recalculated or displayed as an active result.

The separate [Resolved Upstream PR Acceptance metric](docs/RESOLVED_PR_ACCEPTANCE.md) follows the 18-PR maintenance cohort with a source-dated [#125 inbox report](https://github.com/opensiro/upstream/issues/125); it excludes pending/unverifiable PRs.

### Upstream intervention outcomes (observed)

| Interventions | Projects | Merged | Open | Closed unmerged | Unverifiable |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **8** | **7** | **4** | **0** | **3** | **1** |

An unavailable PR is **not** an open PR or a rejection. Its last known outcome remains historical evidence, not a current assertion.

### Evidence-linked interventions

| Intervention / case | Original upstream PR | Current outcome |
| --- | --- | --- |
| [Headcount — Installable security reviewer](cases/headcount.md) | [Original PR](https://github.com/cbrock84/headcount/pull/47) | Unverifiable |
| [Henterprise — Hermes delegation & independent review](cases/henterprise.md) | [Original PR](https://github.com/humbertobellor/henterprise/pull/1) → [replacement](https://github.com/humbertobellor/henterprise/pull/3) | Merged |
| [Marveen — Owner-gated skill adoption](cases/marveen.md) | [Original PR](https://github.com/Szotasz/marveen/pull/1516) | Merged |
| [oh-my-agent — Durable organization policy](cases/oh-my-agent.md) | [Original PR](https://github.com/first-fluke/oh-my-agent/pull/819) | Closed unmerged |
| [Scion — Independent-review platform skill](cases/scion.md) | [Original PR](https://github.com/GoogleCloudPlatform/scion/pull/2047) | Closed unmerged |
| [Shep — Agent-owned workcell coordination](cases/shep.md#933-agent-coordination) | [Original PR](https://github.com/shep-ai/shep/pull/933) | Merged |
| [Shep — ESM worker startup hotfix](cases/shep.md#934-esm-worker-startup) | [Original PR](https://github.com/shep-ai/shep/pull/934) | Merged |
| [StarNet — Lead station-status tool](cases/starnet.md) | [Original PR](https://github.com/androoAGI/starnet/pull/56) | Closed unmerged |

### Separately tracked OpenSiro-owned fork contributions

These are **outside** the archived eight-intervention casebook cohort.

| Registry project | Upstream PR | Verified PR state |
| --- | --- | --- |
| [cognee-community](registry.yaml) | [PR](https://github.com/topoteretes/cognee-community/pull/434) | Open |

Registry PR verification: 2026-11-05T17:36:18+00:00. Updates to `registry.yaml` remain separately reviewed.

**Attribution:** Henterprise original #1 and merged replacement #3 count as **one intervention**. StarNet maintainer's independent implementation is **not** counted as a contributor PR merge. GitHub PR lifecycle alone does not prove a functional VSM S2 improvement.

### Provenance and refresh

- Deprecated historical Product-native fit experiment: [Organization archive](https://github.com/opensiro/vsm-oss-organization/tree/main/experiments/upstream-intervention-fit), pinned here as [`data/upstream-fit-snapshot.json`](data/upstream-fit-snapshot.json) (`as_of` 2026-10-12); **not an active KPI**.
- PR observations: [`data/upstream-lifecycle.json`](data/upstream-lifecycle.json), checked 2026-11-05T17:36:18+00:00; unavailable sources are explicitly marked. They do **not** imply that GitHub statuses are live at viewing time.
- [Public casebook](cases/README.md) provides contextual evidence. [`registry.yaml`](registry.yaml) submission PR states are verified separately and excluded from the experimental cohort.
- Refresh: `python3 scripts/upstream_status.py --refresh` then `--render`; test with `--check-generated` and `--check-live`. External PR checks are read-only; publication is a reviewed PR.

_External maintainers retain decision authority; no upstream endorsement is implied._
