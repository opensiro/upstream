# Upstream operations and automation

Use [UPSTREAMING.md](../UPSTREAMING.md) for data ownership and permission boundaries. The implementation and schedules below are **local observations**, never automatic external publication authority.

## Work and integration

1. Bootstrap from [Organization START_HERE](https://github.com/opensiro/vsm-oss-organization/blob/main/START_HERE.md), follow the owner map and the exact task/PR.
2. Inspect the source SHA, license and native test contract; reserve/collision-check a source only under the actual [batch policy](ASSESSMENT_SOURCE_RESERVATIONS.md).
3. Prepare a minimal patch and native before/after tests in a reviewable OpenSiro PR.
4. Validate local ledgers and generated views. CI passing does not imply external acceptance or an S5 grant.
5. Separate the reviewable internal merge, external PR submission, PR repair, and eventual fork archival as distinct decision points.

## Offline verification

```bash
python3 -m unittest discover -s tests -v
python3 scripts/upstream_status.py --check-generated
python3 scripts/harness_status.py --check
python3 scripts/pr_maintenance_watch.py --validate-only
python3 scripts/resolved_pr_acceptance.py --validate-only
python3 scripts/corrective_publication_queue.py validate
python3 scripts/portfolio_reconcile.py --validate-only
```

The unfiltered [repository-integrity workflow](../.github/workflows/repository-integrity.yml) runs offline tests on every internal PR and on pushes to `main`. It does **not** itself prove that GitHub branch protection requires that check; that administrator-controlled setting is tracked separately by [Organization #305](https://github.com/opensiro/vsm-oss-organization/issues/305).

## External observation (read-only)

| Job or command | Cadence / trigger | Effect |
| --- | --- | --- |
| [PR maintenance](../.github/workflows/pr-maintenance.yml) | Hourly and manual | Read external PR reviews/CI; update only this repo's bounded issue #125 inbox |
| [Resolved PR acceptance](RESOLVED_PR_ACCEPTANCE.md) | Alongside maintenance | Observe the separate 18-target cohort and update its own bot-owned summary in #125 |
| [Portfolio reconciliation](../.github/workflows/portfolio-reconciliation.yml) | Daily and manual | GET exact watched, historical and registered PRs; write **only** the workflow run summary; no issue edit, Git commit or external write |
| [Status freshness](../.github/workflows/upstream-status-freshness.yml) | Daily | Verify stored lifecycle against live PRs; fail on drift, no auto-change |
| `python3 scripts/portfolio_reconcile.py --report` | Operator run with `GITHUB_TOKEN` | Report exact PR lifecycle, final closing actor (if evidenced) and cohort-separated counts |

The portfolio union uses existing manifests, not an inferred GitHub author-search corpus. The live reconciler is not permitted to change the official 18-target watcher or conclude why a human closed a PR. For an observed drift, create a reviewed change to the relevant receipt; do not silently modify the primary ledgers on a timer.

To refresh the existing **pinned casebook and registry PR receipts**, use:

```bash
python3 scripts/upstream_status.py --check-live
# After source-backed drift review only:
python3 scripts/upstream_status.py --refresh
python3 scripts/upstream_status.py --render
python3 scripts/upstream_status.py --check-generated
```

The optional refresh writes local files and must be reviewed in a PR. The daily live check does **not** automatically refresh on failure.

## Scaling without crossing the publication gate

| Layer | Current/proposed state | Safe next step |
| --- | --- | --- |
| Data model and navigation | Standardized local contract; existing multiple ledgers remain distinct | Audit every new source/metric against ownership table |
| Reconciliation sensing | Automatic 18-PR watcher and broader read-only union; dated casebook receipts | Verify live summaries and add regression cases before expanding manifests |
| Cross-batch source coordination | Optional, dormant Git compare-and-swap prototype under [#144](https://github.com/opensiro/upstream/issues/144) | Integrate only with an explicit collision policy and reviewed activation |
| Connected external fork/patch/PR executor | Code prepared, general stage grant **inactive** under [#6](https://github.com/opensiro/upstream/issues/6) | Separate S5 exact-stage mandate and real host/provider rights test |
| Automatic external PR merge, irreversible closure, fork archive | **Not authorized** | Individual attributable human decision and destination-repo rules |

This is a migration path beyond a pilot's manually maintained reports, **not** a claim of autonomous S3/S3* operation. More throughput does not relax license, source-identity, provenance or publication checks.

## Branch and PR hygiene

- GitHub currently has automatic branch deletion **after future merges**, and `main` reports as protected. Exact protection requirements may require an administrator readback.
- The [pre-refactor inventory from 2026-11-07](../reports/2026-11-07-internal-pr-branch-inventory.md) matched **21 open PRs + 6 retained closed-unmerged PR branches + protected main**. Opening this refactor PR #153 adds another head, so these are **not live counts**. [#150](https://github.com/opensiro/upstream/issues/150) is the review queue; do not delete a retained branch based on age or naming alone.
- Before any deletion verify the precise ref/SHA, no open PR targeting or using it, any closed-PR evidence-retention decision, and branch protection. [#130](https://github.com/opensiro/upstream/issues/130) owns the prior cleanup receipt.
- The 2026-11-07 [closure-attribution PR #152](https://github.com/opensiro/upstream/pull/152) is a reviewable dated report; the reconciler reports source events, not a substitute for human motive attribution.
