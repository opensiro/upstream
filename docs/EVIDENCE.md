# Evidence and verified outcomes

[← Home](../README.md) · [Case protocol](../PROTOCOL.md) · [Architecture](ARCHITECTURE.md)

An Upstream contribution is valuable when it investigates a real, source-backed improvement. Keep different evidence levels separate:

| Evidence | Proves | Does not prove |
| --- | --- | --- |
| Index assessment and VSM hypothesis | Why a mechanism is worth exploring | Missing product capability |
| Original source / maintainer need and pinned baseline | Reachable product task or a falsifiable prediction | Useful patch or deployed user value |
| Native before/after, with negative/compatibility control | Bounded behavior under tested conditions | General user adoption |
| Working fork code and native tests | A prepared, tested artifact at exact SHA | PR submission or acceptance |
| Public original-project PR | Proposal submitted | Merge or adoption |
| Independently checked external merged PR | Source change accepted/merged | Deployment, real user benefit or causal VSM improvement |
| Source-proven duplicate/no-change, closed-unmerged, unavailable evidence | Honest narrow disposition | Automatic rejection, productivity zero or universal impossibility |

## What one fork-local contribution should link

In `.opensiro/contributions/<stable-id>.json` and its event/evidence links, record the original target and exact source SHA; real user action and existing alternative; evidence/provenance chronology (strict **ASSESSMENT_DERIVED** requires a dated pinned Index-first prediction); native need/mechanism/counterfactual/scope; source-pinned before/after and negative control; exact [opensiro-contributions](https://github.com/opensiro-contributions) fork/branch/commit and its native test receipts; actual external PR and independent readback; and the next smallest action or reason for terminal closure. Upstream may hold a **minimal pre-fork intake issue**, but does not mirror complete operational records after verified fork metadata exists. If a field is unknown, say **unknown** instead of filling a fake passed gate.

Real code/tests and detailed OpenSiro history belong in the target fork, with `.opensiro/` stored **only** on its separate `opensiro/meta` branch; [the metadata contract](FORK_METADATA.md) is introduced under v0.13.0 and retained under v0.14.0. Original GitHub PR status remains first-party. Historical native scripts and source-ledgers remain [upstream-old](https://github.com/opensiro/upstream-old); there is no second copy of third-party product code in this new repo.

## Organization metric contract

The currently written Organization KPI for Upstream S1 is **`verified_external_outcomes`**, under [Organization METRICS.md](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/METRICS.md) and [metrics.yaml](https://github.com/opensiro/vsm-oss-organization/blob/main/metrics.yaml). It requires fresh independently revalidated accepted **merged changes**, with source identity, evidence and cohort digests. It is **not** the number of external PRs, a PR acceptance rate, number of batches, tests run or proof of deployed benefit.

**Migration status:** verified-outcome producer and its receipts still reside in [upstream-old's accepted outcome pipeline](https://github.com/opensiro/upstream-old/blob/main/docs/VERIFIED_EXTERNAL_OUTCOMES.md). This new Upstream has **no live accepted-export implementation** as of the v0.13.0 documentation cutover. The Organization must not pretend new `registry.yaml` or other source paths exist, nor reinterpret unavailable output as zero. Historical data remains historical; a fresh source contract and live revalidation must be implemented and checked before claiming new-repository KPI values. Do not double-count original/replacement PR chains. [Cutover details](MIGRATION.md).

A verified GitHub merge proves that merge; a product benefit requires separate source-native behavioral evidence. SemVer documents protocol obligations, not an independently proven effect.
