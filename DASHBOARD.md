# Upstream contributions — Dashboard

> **Experimental snapshot: 2026-10-12** · Portfolio case review: **2026-10-17** · **Not live telemetry.**
> Based on the [Organization-owned experimental snapshot](https://github.com/opensiro/vsm-oss-organization/blob/main/experiments/upstream-intervention-fit/snapshot.json), not independent metrics invented in this portfolio.

### Outcomes at a glance

| Interventions | Upstream projects | Merged interventions | Still open | Closed without merge |
| :---: | :---: | :---: | :---: | :---: |
| **8** | **7** | **2** | **4** | **2** |

### Product-native fit

| Fit rate on completed reviews | Pass | Pending | Fail |
| :---: | :---: | :---: | :---: |
| **60% (3/5)** | **3** | **3** | **2** |

**What the 60% represents:** 3 interventions satisfy all four gates (upstream need, upstream-native mechanism, counterfactual value, scope compatibility) among 5 *completed* fit reviews. 3 pending interventions are excluded from the rate denominator. **Not a PR acceptance rate, productivity score, or VSM grade.**

### Intervention outcomes

```text
Merged           ██   2
Open             ████ 4
Closed unmerged  ██   2
```

### Fit-review distribution

```text
Pass      ███  3
Pending   ███  3
Fail      ██   2
```

### Evidence-linked interventions

| Intervention / case evidence | Upstream PR | Outcome | Product-native fit |
| --- | --- | --- | --- |
| [Headcount — Installable security reviewer](cases/headcount.md) | [PR #47](https://github.com/cbrock84/headcount/pull/47) | Open | **Pending** |
| [Henterprise — Hermes delegation & independent review](cases/henterprise.md) | [Original #1 → landed #3](https://github.com/humbertobellor/henterprise/pull/3) | Merged | **Pending** |
| [Marveen — Owner-gated skill adoption](cases/marveen.md) | [PR #1516](https://github.com/Szotasz/marveen/pull/1516) | Merged | **Pass** |
| [oh-my-agent — Durable organization policy](cases/oh-my-agent.md) | [PR #819](https://github.com/first-fluke/oh-my-agent/pull/819) | Closed unmerged | **Fail** |
| [Scion — Independent-review platform skill](cases/scion.md) | [PR #2047](https://github.com/GoogleCloudPlatform/scion/pull/2047) | Closed unmerged | **Fail** |
| [Shep — Agent-owned workcell coordination](cases/shep.md) | [PR #933](https://github.com/shep-ai/shep/pull/933) | Open | **Pending** |
| [Shep — ESM worker startup hotfix](cases/shep.md) | [PR #934](https://github.com/shep-ai/shep/pull/934) | Open | **Pass** |
| [StarNet — Lead station-status tool](cases/starnet.md) | [PR #56](https://github.com/androoAGI/starnet/pull/56) | Open (idea adopted) | **Pass** |

**Interpretation matters.** Henterprise's original #1 closed without merge, but replacement #3 merged with the source contributor's commits preserved: **one merged intervention**. StarNet's maintainer implemented the idea independently and explicitly credited its origin; contributor PR #56 **did not merge**. Both Shep PRs remain open with new-head CI awaiting maintainer workflow authorization. The [Cognee connector](projects/cognee/README.md) is **preparing**, not submitted upstream, and is outside this eight-case experimental cohort.

### Explore and verify

- [Interactive HTML dashboard source](docs/index.html) — self-contained browser page, ready for GitHub Pages **if Pages is configured separately**. GitHub's repository file viewer does not execute HTML.
- [Product-native fit casebook](https://github.com/opensiro/upstream/blob/main/cases/README.md) — primary public PRs, reviews and contextual evidence.
- [Canonical experimental snapshot](https://github.com/opensiro/vsm-oss-organization/blob/main/experiments/upstream-intervention-fit/snapshot.json) · [Metric contract](https://github.com/opensiro/vsm-oss-organization/tree/main/experiments/upstream-intervention-fit) · [Pinned non-authoritative dashboard input](data/upstream-fit-snapshot.json).
- To refresh: verify upstream evidence, update the **Organization-owned ledger** first, then explicitly update this snapshot and regenerate the dashboard. No automatically inferred merge or fit-status changes.

_Experimental, dated values. External maintainers retain decision authority; no upstream endorsement is implied._
