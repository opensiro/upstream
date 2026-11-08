# Resolved Upstream PR Acceptance — operational lifecycle metric

**Owner:** Upstream Contributions S1 (`opensiro/upstream`). **Task/handoff:** [#137](https://github.com/opensiro/upstream/issues/137). **Live reporting inbox:** [#125](https://github.com/opensiro/upstream/issues/125). **Denominator source:** [`data/pr-maintenance/targets.json`](../data/pr-maintenance/targets.json), a reviewed explicit PR cohort.

This measures **external PR integration among PRs that have received a terminal GitHub disposition**. It does not measure the technical correctness of the idea, product-native fit, deployed user benefit, causal VSM impact, reviewer approval, or an autonomy grade. The [Organization S1 domain contract](https://github.com/opensiro/vsm-oss-organization/blob/main/contracts/s1/domain-contracts.md) delegates truthful lifecycle recording to Upstream; [Organization #274](https://github.com/opensiro/vsm-oss-organization/issues/274) did not transfer external maintainer merge rights.

## Formula and cohort

```text
Resolved Upstream PR Acceptance Rate = MERGED / (MERGED + CLOSED_UNMERGED)
```

If there are no resolved cases, the value is `N/A`, not 0% or 100%. Every display includes the numerator, denominator, total watched, pending and unverifiable counts, and observation timestamp. This is a **resolved-only conditional rate**, not a final outcome prediction for all submitted PRs. In particular, the 18 monitored PRs are not the eight historical intervention-fit cases or the 34-case finite Corrective publication queue; do not add cohort counts or success numerators across these overlapping ledgers.

| Primary GitHub outcome | Treatment | Interpretation |
| --- | --- | --- |
| `state=closed`, `merged_at` set | `MERGED` — numerator and denominator | This specific contributor PR was accepted/integrated |
| `state=closed`, `merged_at=null` | `CLOSED_UNMERGED` — denominator | This specific PR was not merged; it need not mean the idea was refuted (e.g. StarNet's independently implemented feature) |
| `state=open`, `merged_at=null` | `OPEN` — excluded | Not yet resolved, no negative verdict |
| Exact PR returns 404 | `UNVERIFIABLE` — excluded, named | Current source is inaccessible; do not infer open, closed or rejected |
| Other errors, malformed/contradictory fields, mismatched identity | Fail closed | No percentage is published from an incomplete untrusted snapshot |

The target set changes **only** through a reviewed watchlist change, with the existing #125 checkpoint migration controls. Every rate is conditional on that exact cohort; changes in its membership can change the metric independently of a maintainer's decision. Do not compare across revisions without recording which cohort each date used.

### Closure is not rejection or absent product impact

For exact `CLOSED_UNMERGED` PRs, GitHub PR state supplies the lifecycle numerator/denominator; **issue `closed` events** supply the closure actor; PR discussion, replacement links and first-party commits may separately support the reason or downstream outcome. These are different fields of evidence. An author can close an already-merged replacement's original, or close a proposed patch after its idea was implemented independently. Neither makes that original PR `MERGED`, and neither alone establishes a maintainer rejection. Likewise, a self-closure without an explanatory comment does not establish a motive.

The [2026-11-07 dated portfolio/closure reconciliation](../reports/2026-11-07-external-pr-closure-attribution.md) cross-checks all four known closed-without-merge PRs against exact GitHub events and distinguishes the **18 watched PRs**, **25 distinct PR URLs** and **24 represented interventions**. Its broader, manually interpreted figures are **not** substituted for the reviewed 18-target operational acceptance report or a new automated adoption metric.

## Implementation and persistence

The stdlib-only [`scripts/resolved_pr_acceptance.py`](../scripts/resolved_pr_acceptance.py) reads **all 18** GitHub PRs directly using the existing watcher GitHub transport and validates each returned URL and PR number. Every 404 is explicitly classified as unavailable and excluded from the acceptance denominator. This remains independent of the stricter review/CI **event watcher**: the latter checks its single reviewed Headcount #47 `verify_404_only` exception, reports **17 fully observed / 1 unavailable**, and fails closed on any other missing source. Neither route can silently reinterpret an unavailable PR as a rejection. Acceptance reporting never changes the event watcher's checkpoint or deduplication.

```bash
python3 scripts/resolved_pr_acceptance.py --validate-only
GITHUB_TOKEN=... python3 scripts/resolved_pr_acceptance.py --report
```

The latter is a GET-only operator report. On scheduled/manual default-branch runs, the existing [PR Maintenance Actions workflow](../.github/workflows/pr-maintenance.yml) runs a separate acceptance job **after offline verification**. `--update-inbox` may create or update only one `github-actions[bot]` summary comment inside [Upstream #125](https://github.com/opensiro/upstream/issues/125). The comment is idempotent per state/day and keeps a source timestamp and links for every monitored outcome; it does not edit third-party PRs, post external comments, or modify the historical casebook. A workflow/CI PASS does not by itself prove a successful live summary write: verify the exact bot comment and Actions run after merge.

Existing [#125 lifecycle/feedback alerts](https://github.com/opensiro/upstream/issues/125) provide the transition history. The rolling metric comment is a **current snapshot**, not an immutable time-series database. For a longitudinal study, preserve separately reviewed dated receipts with exact cohort revisions rather than treating the edited comment as an audit archive.

## Dated starting observation, not a constant

On **2026-11-05**, an independent direct GitHub readback of the 18 tracked URLs observed **4 merged** ([Agent Fleet #43](https://github.com/chankov/agent-fleet/pull/43), [Citadel #366](https://github.com/SethGammon/Citadel/pull/366), [DSH #173](https://github.com/chumingjun/dsh-harness-one/pull/173), [DiscoveryRSI #2](https://github.com/Gen-Verse/DiscoveryRSI/pull/2)), **1 closed unmerged** ([StarNet #56](https://github.com/androoAGI/starnet/pull/56)), **12 open**, and **1 unavailable** ([Headcount #47](https://github.com/cbrock84/headcount/pull/47), 404). Thus the dated resolved-only rate was **4/5 = 80%**, with a very small resolved sample. The current live comment, not this paragraph, controls any newer count. No technical rejection of StarNet's underlying idea is inferred.

## Recovery and authority

Future work begins at [Organization `START_HERE.md`](https://github.com/opensiro/vsm-oss-organization/blob/main/START_HERE.md) → `docs/ECOSYSTEM.md` → Upstream current `main` → [#137](https://github.com/opensiro/upstream/issues/137) → [#125](https://github.com/opensiro/upstream/issues/125) → the current target manifest and exact external PR sources. Upstream owns this lifecycle metric; Organization owns the separate experimental intervention-fit observations. No current count should be reconstructed from chat memory or treated as a permanent Project fact.
