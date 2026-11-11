# GitHub Actions run volume — 2026-11-11

**Owner:** `opensiro/upstream`. **Evidence:** public GitHub Actions REST
`GET /repos/opensiro/upstream/actions/runs`, with exact created-date filters.
Source observation around 2026-11-11 16:12 UTC; figures are snapshots, not
live KPIs and not a billable-minute total.

## Is 1,477 runs a problem?

**No, not on the evidence of the count alone.** The API returned **1,477
total workflow runs** at the observation time. This is cumulative run history,
not concurrently running jobs or a fee. Standard GitHub-hosted runners on a
public repository are free ([GitHub billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions));
larger runners and artifact storage have different rules. GitHub's default
retention of logs/artifacts/run records is 90 days, with configurable public
retention of 1–90 days ([settings](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)).
Do **not** purge historical native RED/GREEN runs merely to lower this counter:
they are source-pinned technical evidence and may outlive the downloadable
log artifact. Preserve concise durable receipts and immutable run URLs.

## Where recent runs came from

For the eight calendar dates **2026-11-04 through 2026-11-11** (including
partial 11 November), GitHub returned **484 runs** in the first observation:

| Workflow name | Runs |
| --- | ---: |
| Repository integrity (all PRs) | 204 |
| Fork lifecycle tests | 117 |
| Upstream portfolio PR freshness (read-only) | 76 |
| External PR review maintenance (hourly inbox) | 39 |
| External outcome evidence verification (read-only) | 29 |
| External PR portfolio reconciliation (read-only) | 13 |
| Upstream lifecycle change proposal (guarded) | 3 |
| Runloop independent native pilot | 2 |
| HarnessDesk current-source native gate | 1 |

Event split: **315 `pull_request`**, **114 `push`**, **46 `schedule`** and
**9 `workflow_dispatch`**. Thus **429 of 484 (88.6%)** were triggered by
repository activity, not a fixed schedule. An individual PR may legitimately
run multiple checks and repeated commits generate more runs.

The first two rows account for **321 of 484 runs (66.3%)**. A fresh follow-up
observation counted **118** fork-lifecycle test runs in the same window, of
which **77 were PR-triggered and 41 push-triggered**; counts can increase even
during the audit. The workflow ran the same command
`python3 -m unittest discover -s tests -v` as
[`repository-integrity.yml`](../.github/workflows/repository-integrity.yml).
The latter already executes the full suite without path filters on every PR
and push to `main`, plus data freshness checks. GitHub's main branch had no
required-status-check protection configured, and no repository rulesets were
returned in the readback; therefore this redundant workflow can be retired
without removing a unique test or an enforced check.

## Optimization decision

1. Retire `test-fork-lifecycle.yml` from `main` and from the control-workflow
   allowlist. This reduces future duplicate CI executions; **do not delete
   the historical run records**. The complete test suite remains mandatory
   inside `repository-integrity.yml`.
2. Keep the other seven control workflows separated by purpose and
   permission boundary. A read-only status observer should not be merged into
   a write-capable maintenance workflow just to reduce file count.
3. Migrate 15 legacy source-native workflows only after pinned equivalence
   and receipt preservation under [#214](https://github.com/opensiro/upstream/issues/214).
4. Re-measure run volume in a later fixed-length window rather than comparing
   the cumulative total before/after and treating history as waste.

The other [Actions audit](2026-11-11-actions-audit.md) records current-main
workflow ownership and the two already-disabled branch-only registrations.
Neither audit authorizes deleting native run evidence or reducing retention.
