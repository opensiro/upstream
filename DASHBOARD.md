# Upstream contributions — Dashboard

> **External PR states verified:** 2026-10-22T16:03:07+00:00 · **Experimental fit snapshot:** 2026-10-12.
> Lifecycle is a dated public GitHub observation; fit and attribution belong to the Organization experiment.

### Upstream intervention outcomes (observed)

| Interventions | Projects | Merged | Open | Closed unmerged |
| :---: | :---: | :---: | :---: | :---: |
| **8** | **7** | **4** | **2** | **2** |

### Product-native fit (separate historical experiment)

| Fit rate of completed reviews | Pass | Pending | Fail |
| :---: | :---: | :---: | :---: |
| **60% (3/5)** | **3** | **3** | **2** |

Four product-native fit gates are assessed in the [Organization-owned experiment](https://github.com/opensiro/vsm-oss-organization/tree/main/experiments/upstream-intervention-fit). This is **not** a PR acceptance rate, VSM grade, or automatically reassessed on a merge.

### Evidence-linked interventions

| Intervention / case | Original upstream PR | Current outcome | Experimental fit |
| --- | --- | --- | --- |
| [Headcount — Installable security reviewer](cases/headcount.md) | [Original PR](https://github.com/cbrock84/headcount/pull/47) | Open | **Pending** |
| [Henterprise — Hermes delegation & independent review](cases/henterprise.md) | [Original PR](https://github.com/humbertobellor/henterprise/pull/1) → [replacement](https://github.com/humbertobellor/henterprise/pull/3) | Merged | **Pending** |
| [Marveen — Owner-gated skill adoption](cases/marveen.md) | [Original PR](https://github.com/Szotasz/marveen/pull/1516) | Merged | **Pass** |
| [oh-my-agent — Durable organization policy](cases/oh-my-agent.md) | [Original PR](https://github.com/first-fluke/oh-my-agent/pull/819) | Closed unmerged | **Fail** |
| [Scion — Independent-review platform skill](cases/scion.md) | [Original PR](https://github.com/GoogleCloudPlatform/scion/pull/2047) | Closed unmerged | **Fail** |
| [Shep — Agent-owned workcell coordination](cases/shep.md#933-agent-coordination) | [Original PR](https://github.com/shep-ai/shep/pull/933) | Merged | **Pending** |
| [Shep — ESM worker startup hotfix](cases/shep.md#934-esm-worker-startup) | [Original PR](https://github.com/shep-ai/shep/pull/934) | Merged | **Pass** |
| [StarNet — Lead station-status tool](cases/starnet.md) | [Original PR](https://github.com/androoAGI/starnet/pull/56) | Open | **Pass** |

### Separately tracked OpenSiro-owned fork contributions

These are **outside** the eight-intervention experimental fit cohort.

| Registry project | Upstream PR | Verified PR state |
| --- | --- | --- |
| [cognee-community](registry.yaml) | [PR](https://github.com/topoteretes/cognee-community/pull/434) | Open |

Registry PR verification: 2026-10-22T16:47:43Z. Updates to `registry.yaml` remain separately reviewed.

**Attribution:** Henterprise original #1 and merged replacement #3 count as **one intervention**. StarNet maintainer's independent implementation is **not** counted as a contributor PR merge. GitHub PR lifecycle alone does not prove a functional VSM S2 improvement.

### Provenance and refresh

- Historical fit snapshot: [Organization ledger](https://github.com/opensiro/vsm-oss-organization/blob/main/experiments/upstream-intervention-fit/snapshot.json), pinned here as [`data/upstream-fit-snapshot.json`](data/upstream-fit-snapshot.json) (`as_of` 2026-10-12).
- PR observations: [`data/upstream-lifecycle.json`](data/upstream-lifecycle.json), last verified 2026-10-22T16:03:07+00:00. They do **not** imply that GitHub statuses are live at viewing time.
- [Public casebook](cases/README.md) provides contextual evidence. [`registry.yaml`](registry.yaml) submission PR states are verified separately and excluded from the experimental cohort.
- Refresh: `python3 scripts/upstream_status.py --refresh` then `--render`; test with `--check-generated` and `--check-live`. External PR checks are read-only; publication is a reviewed PR.

_External maintainers retain decision authority; no upstream endorsement is implied._
