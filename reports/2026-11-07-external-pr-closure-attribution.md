# External PR closure attribution and portfolio reconciliation — 2026-11-07 UTC

**Scope:** read-only, dated reconciliation of the public external PR identities already recorded by `opensiro/upstream`. **Local source:** `main@99ac0597ff01568a0e8bde78558e7966fb8ef1c4`. **External readback:** 2026-11-07 UTC, using exact GitHub PR resources and issue-event histories. This is not a continuously updated metric, a new intervention-fit classification, or authorization to change any external PR.

## Where each claim belongs

| Question | Authoritative input | Output / boundary |
| --- | --- | --- |
| Current external PR state | Exact third-party GitHub PR | `MERGED`, `CLOSED_UNMERGED`, `OPEN`, or `UNVERIFIABLE`; do not infer closure intent from state |
| Actor who closed a PR | Exact third-party GitHub issue `closed` event | Closure attribution, distinct from PR author's identity or maintainer feedback |
| Experimental product-native fit | [Organization experiment](https://github.com/opensiro/vsm-oss-organization/tree/main/experiments/upstream-intervention-fit) | Frozen four-gate judgment; not revised by this report |
| Original/replacement chain and independently landed idea | `data/upstream-lifecycle.json`, casebook and primary PR/commit/issue evidence | One intervention may have two PRs; maintainer-written implementation does not merge contributor commits |
| Operational resolved-PR acceptance | `data/pr-maintenance/targets.json`, [inbox #125](https://github.com/opensiro/upstream/issues/125), [`docs/RESOLVED_PR_ACCEPTANCE.md`](../docs/RESOLVED_PR_ACCEPTANCE.md) | Its exact **18-target** denominator is unchanged |

Do not edit generated `DASHBOARD.md`, `docs/index.html`, `cases/README.md` generated rows, or `HARNESS_STATUS.md` to impose this dated interpretation. Their existing builders own those projections. The separately published 34-case Corrective ledger is not a third, additive set of contributions.

## Exact four closed-without-merge PRs

All four GitHub PR resources returned `closed` and `merged_at: null`. Closure **actors** were independently read from `/repos/{owner}/{repo}/issues/{number}/events`; a `closed` state alone does not identify who acted or why.

| PR | Final closure event | Verified interpretation |
| --- | --- | --- |
| [Henterprise #1](https://github.com/humbertobellor/henterprise/pull/1) | `xLagerFeuer`, 2026-10-11 21:10 UTC ([events](https://api.github.com/repos/humbertobellor/henterprise/issues/1/events)) | Contributor explicitly [closed the superseded original](https://github.com/humbertobellor/henterprise/pull/1#issuecomment-6113791152) **after** maintainer [replacement #3](https://github.com/humbertobellor/henterprise/pull/3) merged on 2026-10-08 with the six contributor commits preserved. **One successfully landed intervention**, not a rejected change plus a second success. |
| [StarNet #56](https://github.com/androoAGI/starnet/pull/56) | `xLagerFeuer`, 2026-10-24 15:33 UTC ([events](https://api.github.com/repos/androoAGI/starnet/issues/56/events)) | Contributor [closed as superseded](https://github.com/androoAGI/starnet/pull/56#issuecomment-6386069014) after maintainer independently shipped `station.status` in `v0.13.2`. The [maintainer-authored commit](https://github.com/androoAGI/starnet/commit/dc9633bb05434e236509583cd1b226140f8d3f67) credits the idea; **not a contributor PR merge**. An earlier close/reopen of the same PR does not replace the final event. |
| [oh-my-agent #819](https://github.com/first-fluke/oh-my-agent/pull/819) | `xLagerFeuer`, 2026-09-28 18:29 UTC ([events](https://api.github.com/repos/first-fluke/oh-my-agent/issues/819/events)) | Contributor self-closed. No closure-reason comment or maintainer rejection was found in its PR discussion; **do not invent the actor's motive**. Independently, Organization's later source-first fit review judged upstream need unsupported (`fail`). |
| [Scion #2047](https://github.com/GoogleCloudPlatform/scion/pull/2047) | Maintainer `ptone`, 2026-09-28 23:13 UTC ([events](https://api.github.com/repos/GoogleCloudPlatform/scion/issues/2047/events)) | Maintainer [explained](https://github.com/GoogleCloudPlatform/scion/pull/2047#issuecomment-5880411960) that independent review belongs in a Scion solution/template, **not Scion core**. This is a specific integration-scope rejection, not a verdict that independent review is useless. A separate CLA bot message was not the documented closure reason. |

Therefore **three of four** `CLOSED_UNMERGED` PRs were closed by the contributor. Exactly **one** was closed by an upstream maintainer. Neither the actor nor the `closed` event alone is a product-fit or code-acceptance classification.

## Reconciled portfolio denominators (dated, not live)

The union of the 18 explicitly watched PR URLs, the eight historical casebook interventions (nine original/replacement PR URLs), and the separately registered Cognee PR contains **25 unique exact external PR URLs**. StarNet and Headcount occur in both the watcher and casebook; Cognee is already in the watcher. Exact GitHub PR readback on 2026-11-07 gave:

| View | Merged | Closed unmerged | Open | Unverifiable | Correct interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| [18-target watcher](../data/pr-maintenance/targets.json) | 5 | 1 | 11 | 1 | Resolved-only PR rate **5/(5+1) = 83.3%**, the existing operational metric |
| All **25 unique PR URLs** | 9 | 4 | 11 | 1 | Resolved-only **PR merge rate 9/(9+4) = 69.2%**, for this larger dated union |

The four additional merged PR URLs outside the 18-target watcher are [Henterprise #3](https://github.com/humbertobellor/henterprise/pull/3), [Marveen #1516](https://github.com/Szotasz/marveen/pull/1516), [Shep #933](https://github.com/shep-ai/shep/pull/933), and [Shep #934](https://github.com/shep-ai/shep/pull/934). Henterprise #3 was opened by its maintainer using the contributor's preserved commits. [Headcount #47](https://github.com/cbrock84/headcount/pull/47) returned 404 and is **unverifiable**, never treated as rejected or open.

After collapsing Henterprise #1/#3 into **one intervention**, the same public portfolio can be described as **24 distinct externally represented interventions**: 9 landed via PR, 1 independently implemented idea (StarNet), 1 contributor-closed without verified adoption (oh-my-agent), 1 maintainer-declined core placement (Scion), 11 still open, 1 unverifiable.

An **illustrative adoption-inclusive resolved-intervention observation** is therefore `(9 landed PR interventions + 1 independently implemented idea) / (9 + 1 + 1 + 1 terminal interventions) = 10/12 = 83.3%`. **Do not name this `PR acceptance`, automatically emit it as the operational metric, or infer product-native fit, causal benefit, OpenSiro authorship of maintainer code, or final success for pending work.** It requires explicit event/identity interpretation and a reviewed frozen cohort; any future general metric needs its own methodology and refresh rules.

## Follow-up / no changes made

- Retain the 18-target watcher denominator and its existing live bot comment under [#125](https://github.com/opensiro/upstream/issues/125); this report does not change the target list, acceptance script or checkpoint.
- Preserve the casebook's eight experimental intervention identities and Organization-owned fit classifications.
- Re-run exact third-party PR and closing-event reads before quoting these broader counts on a later date; this report is not a replacement for a live scan.
- No external GitHub mutation, new contribution publication, PR closure, grade change or autonomy inference follows from this accounting.
