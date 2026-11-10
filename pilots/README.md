# Experimental evidence and technical pilots

This directory preserves the *experiments* behind OpenSiro's third-party
Upstream interventions: source-pinned hypotheses, negative screens, native
fixtures, patches, protocols, receipts, limitations and contributor handoffs.
It is **not** the live source workspace, a successful-intervention list or an
external PR publication queue.

## Navigate the historical work

- [**All preserved pilot directories, grouped by artifact**](CATALOG.md) —
  generated, clickable catalog of original paths and major evidence types.
- [**Experiment record contract**](EXPERIMENT_CONTRACT.md) — what counts as
  a protocol, result, limitation and delivery record; how new work is filed.
- [**Machine-readable pilot inventory**](catalog.json) — stable source for
  agents and CI; file inventory only, not positive-result grades.
- [**Frozen historical path baseline**](HISTORICAL_BASELINE.json) — immutable
  identity/path guard for the original pilot files, not an experiment result.
- [Assessment-to-improvement method](../docs/ASSESSMENT_TO_IMPROVEMENT.md)
  and [native functional effects](../docs/FUNCTIONAL_EFFECTS.md) — meaning and
  validation boundaries for individual claims.

Each original subdirectory remains in place to preserve frozen references.
Examples: the [Kram native replay](kram-s2/README.md),
[Zot counterfactual experiments](zot-shared-workspace/SCREENING_2026-10-20.md),
and [AgentBox manager study](agentbox-s2/SCREENING_AND_NATIVE_FIT_2026-10-20.md).

## Where new changes go

After a justified source-native technical fix, the intended live workspace is
the matching verified `opensiro-contributions` fork. This directory retains
the experiment packet and reproducibility evidence. The [continuous source →
fork pipeline](../docs/CONTINUOUS_WORKING_FORK_PIPELINE.md) documents the
current inactive executor boundary and **human-only external PR decision**.

For current intervention stages use [Harness Status](../HARNESS_STATUS.md),
the owning batch record and the exact external PR. A directory name or patch
file alone never establishes an outcome, VSM grade or upstream acceptance.
