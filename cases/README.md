# Product-native fit — external intervention cases

**Portfolio check:** 2026-10-17. **Fit classification source:** [Organization's experimental `upstream-intervention-fit` ledger](https://github.com/opensiro/vsm-oss-organization/tree/main/experiments/upstream-intervention-fit), last snapshot `as_of: 2026-10-12`. These are different timestamps. This index records links and publicly observed outcomes; it does **not** perform a new independent fit reassessment or continuously monitor upstream.

## Question

Would an OpenSiro-shaped contribution be useful to the upstream project **even if its VSM assessment and grade were never mentioned**? The four separate gates are a demonstrated upstream need, an upstream-native mechanism, independent counterfactual value, and fit with current upstream scope. All four must pass for `pass`; an evidence gap is `pending`, not a success. An upstream merge is not sufficient for fit by itself.

| Intervention | Original PR | Upstream code / PR outcome checked 2026-10-17 | Experimental fit (ledger 2026-10-12) |
| --- | --- | --- | --- |
| [Marveen skill adaptation](marveen.md) | [#1516](https://github.com/Szotasz/marveen/pull/1516) | Merged 2026-09-30 | **pass** |
| [Henterprise delegation and reviews](henterprise.md) | [#1](https://github.com/humbertobellor/henterprise/pull/1) | Original closed; replacement [#3](https://github.com/humbertobellor/henterprise/pull/3) merged 2026-10-08, source commits preserved | **pending** |
| [Shep agent coordination](shep.md#933-agent-coordination) | [#933](https://github.com/shep-ai/shep/pull/933) | Open; commitlint message fixed, new-head CI awaiting approval; review pending | **pending** |
| [Shep ESM startup fix](shep.md#934-esm-worker-startup) | [#934](https://github.com/shep-ai/shep/pull/934) | Open; commitlint message fixed, new-head CI awaiting approval | **pass** |
| [StarNet station snapshot](starnet.md) | [#56](https://github.com/androoAGI/starnet/pull/56) | PR open; equivalent capability independently implemented by maintainer in [`dc9633b`](https://github.com/androoAGI/starnet/commit/dc9633bb05434e236509583cd1b226140f8d3f67) with idea credit | **pass** |
| [Headcount plugin security review](headcount.md) | [#47](https://github.com/cbrock84/headcount/pull/47) | Open; upstream need and scope not confirmed | **pending** |
| [Scion independent-review platform skill](scion.md) | [#2047](https://github.com/GoogleCloudPlatform/scion/pull/2047) | Closed without merge; maintainer prefers solution-level asset, not core | **fail** |
| [oh-my-agent durable policy governance](oh-my-agent.md) | [#819](https://github.com/first-fluke/oh-my-agent/pull/819) | Closed without merge; no source-backed native upstream need established | **fail** |

**Do not add PR counts:** eight **interventions**, not nine PRs. Henterprise's original #1 and its maintainer's replacement #3 are one accepted intervention, with distinct author and merger roles. StarNet #56 is **not** a merged PR and the maintainer's code must not be misattributed as the contributor's own commit.

The experimental snapshot reports **3 pass / 2 fail / 3 pending**, i.e. `3 / (3+2) = 60%` of completed *fit reviews*. This is **not** an upstream merge rate or a contributor productivity score; consult the [live source snapshot](https://github.com/opensiro/vsm-oss-organization/blob/main/experiments/upstream-intervention-fit/snapshot.json) before quoting it later.

## Ownership boundary

- Canonical fit observations, four-gate evidence, attribution and original/replacement chain: [Organization observations](https://github.com/opensiro/vsm-oss-organization/blob/main/experiments/upstream-intervention-fit/observations.json).
- This repository: accessible **portfolio profiles**, evidence links and public outcomes only.
- External maintainers: upstream code, accept/reject decisions, issue/PR/CI and scope.
- [Cognee Community](../projects/cognee/README.md) is a **separate, currently preparing OpenSiro-owned fork contribution**, not part of this completed experimental cohort.
- These cases use publicly verified [`xLagerFeuer` forks](https://github.com/xLagerFeuer); they are **not** presented as seven `opensiro/*` forks, and no fork-archive or maintainership decision is inferred.

If the experiment's classifications change, update them in the **Organization ledger first**, then synchronize this presentation; never silently upgrade a fit gate on the strength of a merge.
