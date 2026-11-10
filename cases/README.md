# Deprecated Product-native fit — historical intervention casebook

**DEPRECATED (2026-11-07):** the Product-native fit ratio and four-gate grades are frozen historical research, not active performance metrics. **Contextual case review:** 2026-10-17. **Legacy fit source:** [Organization's archived `upstream-intervention-fit` ledger](https://github.com/opensiro/vsm-oss-organization/tree/main/experiments/upstream-intervention-fit), pinned snapshot `as_of: 2026-10-12`. **External PR states** below come from [separately verified receipts](../data/upstream-lifecycle.json), not from historical fit. Neither source is live telemetry.

## Question

Would an OpenSiro-shaped contribution be useful to the upstream project **even if its VSM assessment and grade were never mentioned**? The four separate gates are a demonstrated upstream need, an upstream-native mechanism, independent counterfactual value, and fit with current upstream scope. All four must pass for `pass`; an evidence gap is `pending`, not a success. An upstream merge is not sufficient for fit by itself.

| Intervention | Original and landing PR | Observed external PR outcome | Experimental fit (ledger 2026-10-12) |
| --- | --- | --- | --- |
<!-- BEGIN GENERATED:casebook -->
| [Headcount — Installable security reviewer](headcount.md) | [Original PR](https://github.com/cbrock84/headcount/pull/47) | Unverifiable | **pending** |
| [Henterprise — Hermes delegation & independent review](henterprise.md) | [Original PR](https://github.com/humbertobellor/henterprise/pull/1) → [replacement](https://github.com/humbertobellor/henterprise/pull/3) | Merged | **pending** |
| [Marveen — Owner-gated skill adoption](marveen.md) | [Original PR](https://github.com/Szotasz/marveen/pull/1516) | Merged | **pass** |
| [oh-my-agent — Durable organization policy](oh-my-agent.md) | [Original PR](https://github.com/first-fluke/oh-my-agent/pull/819) | Closed unmerged | **fail** |
| [Scion — Independent-review platform skill](scion.md) | [Original PR](https://github.com/GoogleCloudPlatform/scion/pull/2047) | Closed unmerged | **fail** |
| [Shep — Agent-owned workcell coordination](shep.md#933-agent-coordination) | [Original PR](https://github.com/shep-ai/shep/pull/933) | Merged | **pending** |
| [Shep — ESM worker startup hotfix](shep.md#934-esm-worker-startup) | [Original PR](https://github.com/shep-ai/shep/pull/934) | Merged | **pass** |
| [StarNet — Lead station-status tool](starnet.md) | [Original PR](https://github.com/androoAGI/starnet/pull/56) | Closed unmerged | **pass** |
<!-- END GENERATED:casebook -->

**Do not add PR counts:** eight **interventions**, not nine PRs. Henterprise's original #1 and its maintainer's replacement #3 are one accepted intervention, with distinct author and merger roles. StarNet #56 is **not** a merged PR and the maintainer's code must not be misattributed as the contributor's own commit.

For attributable closure actors and the distinction between voluntary supersession, independently implemented functionality and a maintainer's scope refusal, see the [dated 2026-11-07 external PR closure reconciliation](../reports/2026-11-07-external-pr-closure-attribution.md). It does not change this frozen eight-case experiment or its fit labels.

The frozen snapshot historically reported **3 pass / 2 fail / 3 pending**, or `3 / (3+2) = 60%` of completed fit reviews. **This retired value must not be reported as a current KPI**, upstream acceptance rate or contributor productivity score. Its [frozen source snapshot](https://github.com/opensiro/vsm-oss-organization/blob/main/experiments/upstream-intervention-fit/snapshot.json) remains for reproducibility.

## Ownership boundary

- Canonical fit observations, four-gate evidence, attribution and original/replacement chain: [Organization observations](https://github.com/opensiro/vsm-oss-organization/blob/main/experiments/upstream-intervention-fit/observations.json).
- This repository: accessible **portfolio profiles**, evidence links and public outcomes only.
- External maintainers: upstream code, accept/reject decisions, issue/PR/CI and scope.
- [Cognee Community](../projects/cognee/README.md) is a **separate OpenSiro-owned fork contribution** in [`registry.yaml`](../registry.yaml), not part of this eight-case experimental cohort.
- These cases use publicly verified [`xLagerFeuer` forks](https://github.com/xLagerFeuer); they are **not** presented as seven `opensiro/*` forks, and no fork-archive or maintainership decision is inferred.

**Do not reopen or extend the deprecated fit scoring.** New contributions are recorded in Upstream-owned operational ledgers; current external PR lifecycle comes from exact GitHub source readback. Historical gate labels remain here only to preserve the original audit trail.
