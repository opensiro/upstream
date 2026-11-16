# OpenSiro — external PR activity

![GitHub-style activity calendar](activity.svg)

**Snapshot:** 2026-11-16 12:00 UTC. **Scope:** the 60 verified `opensiro-contributions` fork-local metadata branches and their 61 independently identified improvements. First-party live PR status and review reads were checked for all 42 distinct linked original-repository PR URLs. This is a **dated, bounded view**, not a live GitHub widget or all historical OpenSiro research.

| External PR lifecycle | Count | Interpretation |
| --- | ---: | --- |
| **Published** | **42** | Distinct externally opened PR URLs linked by `.opensiro/contributions/*.json` |
| **Merged** | **11** | Original GitHub PR has a non-null `merged_at` |
| **Open** | **24** | Original GitHub PR remains open |
| **Closed without merge** | **7** | Closed PR with no `merged_at`; rejection, withdrawal, replacement and other reasons are not conflated |
| **Of those 7, with an APPROVED review** | **0** | Subset of closed-unmerged, using original GitHub review objects, not an extra PR-status bucket |

**These values are PR counts, not independent-improvement counts.** For example, Henterprise original/replacement PR #1 and #3 are two published PRs for one improvement. Shep #933 and #934 represent two independent improvements. An accepted merge is *not* evidence of deployed product benefit. A review marked `APPROVED` is also not a merge or proof of adoption.

## Reading one square

A square is one **UTC calendar day**, split into **three horizontal stripes**: **green** = PR published, **blue** = PR merged, **amber** = PR closed without merge. Each stripe becomes darker independently as its event count grows. Gray stripes mean zero for that category. This is not a blended score.

A **purple dot** appears on the closure day if any PR closed without merge has an explicit current `APPROVED` GitHub review. The approved count is a **subset of closed-unmerged**, not an extra event or a claim of deployed value. The current source-backed snapshot has **zero approved closures**, so no purple dots appear on historical squares yet. The SVG contains a detailed title for each date, but GitHub Markdown image renderers may not expose that tooltip; the audit table below preserves exact counts.

On **2026-10-24**, for example, a single square has **8 published**, **1 merged**, **1 closed unmerged**, **0 with APPROVED review**. Those are independent intensities on the same day; no event is moved to the metadata migration date.

## Daily event counts (UTC)

| Date | Published | Merged | Closed unmerged | With APPROVED review |
| --- | ---: | ---: | ---: | ---: |
| 2026-09-23 | 2 | 0 | 0 | 0 |
| 2026-09-28 | 3 | 0 | 2 | 0 |
| 2026-09-30 | 0 | 1 | 0 | 0 |
| 2026-10-08 | 1 | 1 | 0 | 0 |
| 2026-10-11 | 1 | 0 | 1 | 0 |
| 2026-10-12 | 1 | 0 | 0 | 0 |
| 2026-10-19 | 1 | 2 | 0 | 0 |
| 2026-10-23 | 7 | 0 | 0 | 0 |
| 2026-10-24 | 8 | 1 | 1 | 0 |
| 2026-10-25 | 0 | 1 | 0 | 0 |
| 2026-10-29 | 0 | 1 | 0 | 0 |
| 2026-10-30 | 0 | 1 | 0 | 0 |
| 2026-11-05 | 0 | 1 | 0 | 0 |
| 2026-11-10 | 7 | 2 | 0 | 0 |
| 2026-11-11 | 7 | 0 | 0 | 0 |
| 2026-11-12 | 2 | 0 | 1 | 0 |
| 2026-11-13 | 2 | 0 | 1 | 0 |
| 2026-11-14 | 0 | 0 | 1 | 0 |

## Refresh on demand — no background services

The existing read-only `scripts/aggregate.py` is the source for verified fork metadata, while the new one-shot `scripts/activity.py` independently reads each linked original PR and relevant review API, deduplicates URLs, validates source identity, and renders the dated SVG/report:

```bash
GH_TOKEN=... python3 scripts/aggregate.py --no-prs --format json > /tmp/opensiro-portfolio.json
GH_TOKEN=... python3 scripts/activity.py --input /tmp/opensiro-portfolio.json \
  --svg docs/activity.svg --markdown docs/ACTIVITY.md
```

The second command **fails closed** if the input scan is partial/attention-filtered or if any original PR/review cannot be read. It does not quietly count API failures as zeros or update the chart with an incomplete total. The render is a static generated artifact: commit the refreshed files manually if desired. There is no cron, Action, daemon, second mutable ledger, web sync, migration restart or extra Organization KPI.

**Coverage limitations:** Only PR URLs actually linked from currently valid public `.opensiro/` metadata are included. The older historical registry, blocked/unmapped work, research-only prototypes, unlinked external PRs and ongoing PR lifecycle beyond the observation timestamp are not automatically counted. For reconciliation and provenance see [closed one-time migration issue #2](https://github.com/opensiro/upstream/issues/2) and [fork metadata contract](FORK_METADATA.md).
