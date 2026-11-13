# Dated reports

This directory holds immutable-in-meaning, **source-dated observations**. A report can remain useful as evidence after counts, GitHub PR states or Organization scope change; it must never silently replace live source-of-truth readback.

- [2026-10-19 Index-origin S1 pilot](2026-10-19-index-origin-s1-pilot.md)
- [2026-10-24 Corrective PR reconciliation](2026-10-24-corrective-pr-reconciliation.md)
- [2026-10-24 StarNet PR maintenance](2026-10-24-starnet-pr56-maintenance.md)
- [2026-10-25 operational readiness](2026-10-25-upstream-operational-readiness.md)
- [2026-11-07 internal PR/branch inventory](2026-11-07-internal-pr-branch-inventory.md) — 21 open + 6 closed-unmerged heads **before** refactor PR #153
- [2026-11-07 closure attribution](2026-11-07-external-pr-closure-attribution.md) — reviewed as [PR #152](https://github.com/opensiro/upstream/pull/152)
- [2026-11-11 external publication wave 01](2026-11-11-external-publication-wave-01.md) — five selected source-first handoffs, explicit blockers and per-PR publication gate
- [2026-11-11 external publication wave 02](2026-11-11-external-publication-wave-02.md) — five additional handoffs, two proposed final PR descriptions, source drift and DCO gates
- [2026-11-11 external publication wave 03](2026-11-11-external-publication-wave-03.md) — five further handoffs, one proposed PR description, security/contributor/duplicate gates
- [2026-11-11 GitHub Actions cleanup audit](2026-11-11-actions-audit.md) — control vs legacy native workflows, registered-branch discrepancies and evidence-gated retirement plan
- [2026-11-13 first assessment-hypothesis quality census](2026-11-13-assessment-hypothesis-quality-baseline.md) — 8 frozen batches / 40 sources; negative screens, blockers, recorded derived hypotheses and dated publication receipts, without asserting native benefit or external adoption
- [2026-11-11 GitHub Actions run-volume audit](2026-11-11-actions-run-volume.md) — source-dated 1,477 cumulative runs, trigger breakdown and redundant fork-lifecycle CI removal

For a current read-only PR-lifecycle observation use `python3 scripts/portfolio_reconcile.py --report` with a suitable token, or [the daily workflow](../.github/workflows/portfolio-reconciliation.yml). Neither assigns product fit or closure motive.
