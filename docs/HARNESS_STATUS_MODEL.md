# Harness / intervention / PR — cross-lane status projection

**Owner:** `opensiro/upstream` [#56](https://github.com/opensiro/upstream/issues/56). **Mode:** read-only local projection, no new authority, no upstream GitHub write, no lifecycle status mutation.

## What the four levels mean

| Level | Identity | Cardinality | Authority |
| --- | --- | --- | --- |
| Harness | GitHub upstream `owner/repo` (case-insensitive grouping) | One harness has many interventions | Upstream repository identity in the owning evidence |
| Intervention | Stable namespaced ID (`assessment:`, `portfolio:`, `registry:`, or monitor-only) | Several interventions can affect one VSM function, or one harness may need several different VSM functions | Source batch, publication ledger, casebook or registry |
| External PR | Exact public GitHub `owner/repo/pull/N` URL | One intervention can have an original and replacement PR; one PR can cover several interventions | Dated public source receipt; **not** a newly fetched live outcome |
| Batch | Frozen assessment cohort and index SHA | One batch contains five independently scoped interventions by current batch policy | `data/assessment-candidate-batches/*.json` |

There is deliberately **no harness-level `FIXED` status**. For example, one harness can have intervention A accepted upstream, intervention B blocked for evidence and intervention C prepared but unpublished. All three must remain visible.

## Data source precedence and reconciliation

1. **Technical screening** comes from immutable `data/assessment-candidate-batches/*.json` candidates. Historical `AWAITING_EXTERNAL` means native evidence or handoff was prepared in that cohort; it does **not** imply any third-party submission.
2. **External publication/acceptance** for overlapping assessment IDs comes from the separate finite `data/corrective-publication/2026-10-23-01.json` and `data/improvement-publication/2026-10-24-01.json` ledgers. A confirmed `MERGED_UPSTREAM` overlays the external dimension without rewriting the original batch stage; `SUBMITTED_UNVERIFIED_LIVE` explicitly does not assert a currently open PR.
3. **Experimental portfolio** case identities and source attribution come from the dated `data/upstream-fit-snapshot.json` plus verified `data/upstream-lifecycle.json`, `data/dashboard-cases.json` and linked `cases/` files. Fit is not a VSM function grade. Historical merged/open/closed/unverifiable states remain dated receipts.
4. **Registry** project identities and PRs come from `registry.yaml` and the same dated lifecycle receipt. An OpenSiro fork's maintenance lifecycle is not conflated with an external PR outcome.
5. **PR watcher** `data/pr-maintenance/targets.json` marks monitored URLs already known in the model. It creates a `monitor:` placeholder **only if** a watched PR has no existing intervention. Monitoring does not prove a fix or grant a publication right.

The [existing Portfolio Dashboard](../DASHBOARD.md) remains the eight-intervention historical presentation, with the original Product-native fit metric **deprecated** and preserved only in the frozen archive. The [new joined inventory](../HARNESS_STATUS.md) answers the different operational question: *what has happened to each individual improvement of each upstream harness?*

## Read-only operations

```bash
python3 scripts/harness_status.py --check
python3 scripts/harness_status.py --json
python3 scripts/harness_status.py --json --filter actionable
python3 scripts/harness_status.py --filter awaiting-external
python3 scripts/harness_status.py --filter blocked
python3 scripts/harness_status.py --filter merged
python3 scripts/harness_status.py --write
python3 -m unittest discover -s tests -p 'test_harness_status.py'
```

`--write` regenerates **only** `HARNESS_STATUS.md`; `--check` fails on drift. Filtered output is inspection-only; `--write` and `--check` refuse filtered input. The complete unit suite and the read-only upstream status freshness workflow check the projection.

### Control Plane routing suggestion

`upstream status` → bootstrap Organization → route to `opensiro/upstream` → run `python3 scripts/harness_status.py --check` and optionally `--json --filter actionable` → summarize harness/intervention/PR, evidence freshness and next action. It is distinct from `batch upstream` (scheduling/technical work), `test S1 function: upstream contributions` (construction test), and the bounded Corrective external publication lane.

All external writes remain separately governed by S5, licensing, review and GitHub permissions. The status projection **does not** create a new mandate or allow an external merge. The existing hourly bounded PR maintenance workflow senses changes only for its explicit targets; this projection is not a live crawler and should be regenerated after a source-ledger change.
