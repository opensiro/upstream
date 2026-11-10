# Data and provenance

These directories are **distinct ledgers**, not one additive contribution table.

| Path | Owns |
| --- | --- |
| `assessment-candidate-batches/` | Frozen five-source screening manifests and summary receipts |
| `corrective-publication/` | Finite Corrective publication cohort and stage results |
| `improvement-publication/` | Separately mandated Improvement publications |
| `pr-maintenance/targets.json` | Explicit 18-PR operational watcher cohort; do not silently widen |
| `upstream-lifecycle.json` | Source-dated external PR observations for the historical casebook and registry |
| `upstream-fit-snapshot.json` | Pinned **copy** of Organization-owned historical fit experiment |
| `functional-effects.json` | Native before/after evidence, not external adoption |
| `dashboard-cases.json` | Casebook presentation metadata |

`registry.yaml` at repository root independently covers OpenSiro-owned working forks and submitted contributions.

The new [portfolio reconciler](../scripts/portfolio_reconcile.py) deduplicates exact URLs across the 18-target watchlist, casebook original/replacement PRs and registry submissions **in memory**. It publishes no new mutable canonical ledger. This prevents a second, manually diverging roster.

For precedence, cohort definitions, required provenance and safe mutation boundaries see [UPSTREAMING.md](../UPSTREAMING.md). To refresh generated views see [operations](../docs/OPERATIONS.md).
