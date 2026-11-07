# Initial external-outcomes readback — agent proposal (2026-11-07)

**Status:** dated, read-only **manual GitHub readback** and agent semantic-review proposal under [Upstream #159](https://github.com/opensiro/upstream/issues/159). **Not** the successful `observe` workflow artifact, an owner-accepted ledger, an independent S3* audit, or Organization's primary `verified_external_outcomes` stock. No external publication, merge, test rerun, or user benefit is asserted.

- Observation cutoff: **2026-11-07T14:59:36Z** (UTC, source readbacks collected immediately before this time).
- Upstream `main` source: [`1e021a2cfcac4312d7d8fcb26f0c1afffd1b0d0d`](https://github.com/opensiro/upstream/commit/1e021a2cfcac4312d7d8fcb26f0c1afffd1b0d0d) (local evidence-tree SHA matched GitHub main tree).
- Exact source `source_sha256`: `e32c7c4ee85d94a0b0245cd8ac869b1ed958614942905700a57db51febc51955`.
- Exact `portfolio_cohort_sha256`: `9ec745b1a73ce49ece1bea7b3c3ac844bb9bfe80bfe2dbc74c48a2819d472adf`.
- `python3 scripts/verified_external_outcomes.py --validate-only`: **PASS**, 24 interventions, 25 PR URLs, 21 unpublished blocked Corrective excluded.
- GitHub workflow: the available [PR validate run](https://github.com/opensiro/upstream/actions/runs/42382487478) passed; **no post-merge `observe` run or JSON artifact was found at the readback time**. The first real `observe` and schema/digest verification remain required before source-owned acceptance. The schedule is daily at 05:17 UTC; workflow dispatch is also configured but was not invoked by this review.

## Current first-party lifecycle (not the semantic KPI)

| PR-based intervention lifecycle | Count |
| --- | ---: |
| Merged externally, including one replacement chain | 9 |
| Open externally | 11 |
| Closed without merge (effective PR) | 3 |
| Unavailable/404 external PR | 1 |
| **Total distinct interventions** | **24** |

These observations are volatile. The 9 merged interventions are **not** 9 proven outcomes. The provisional evidence-gate grouping if the workflow receives exactly these inputs would be **2 fast-path `VERIFIED` candidates / 10 `PENDING_REVIEW` / 11 `INSUFFICIENT_EVIDENCE` / 1 `UNVERIFIABLE`**. This prediction is **not** an actual verifier result; the real JSON must be retained and compared before updating any accepted ledger. A machine `VERIFIED` result is still a candidate.

| Intervention ID | First-party PR evidence | Observed lifecycle | Proposed evidence gate |
| --- | --- | --- | --- |
| `casebook:headcount-47` | [pull#47](https://github.com/cbrock84/headcount/pull/47) | UNVERIFIABLE | `UNVERIFIABLE` |
| `casebook:henterprise-1` | [pull#1](https://github.com/humbertobellor/henterprise/pull/1) → [pull#3](https://github.com/humbertobellor/henterprise/pull/3) | MERGED | `PENDING_REVIEW` |
| `casebook:marveen-1516` | [pull#1516](https://github.com/Szotasz/marveen/pull/1516) | MERGED | `PENDING_REVIEW` |
| `casebook:oh-my-agent-819` | [pull#819](https://github.com/first-fluke/oh-my-agent/pull/819) | CLOSED_UNMERGED | `PENDING_REVIEW` |
| `casebook:scion-2047` | [pull#2047](https://github.com/GoogleCloudPlatform/scion/pull/2047) | CLOSED_UNMERGED | `PENDING_REVIEW` |
| `casebook:shep-933` | [pull#933](https://github.com/shep-ai/shep/pull/933) | MERGED | `PENDING_REVIEW` |
| `casebook:shep-934` | [pull#934](https://github.com/shep-ai/shep/pull/934) | MERGED | `PENDING_REVIEW` |
| `casebook:starnet-55` | [pull#56](https://github.com/androoAGI/starnet/pull/56) | CLOSED_UNMERGED | `PENDING_REVIEW` |
| `corrective:agent-loop-numeric-verifier-grounding` | [pull#1](https://github.com/Onipounds/agent-loop/pull/1) | OPEN | `INSUFFICIENT_EVIDENCE` |
| `corrective:babyai-task-evaluation-input-contract` | [pull#128](https://github.com/mila-iqia/babyai/pull/128) | OPEN | `INSUFFICIENT_EVIDENCE` |
| `corrective:besser-state-transition-validation` | [pull#205](https://github.com/BESSER-PEARL/BESSER-Agentic-Framework/pull/205) | OPEN | `INSUFFICIENT_EVIDENCE` |
| `corrective:discoveryrsi-campaign-history-integrity` | [pull#2](https://github.com/Gen-Verse/DiscoveryRSI/pull/2) | MERGED | `PENDING_REVIEW` |
| `corrective:dsh-harness-one-workflow-state` | [pull#173](https://github.com/chumingjun/dsh-harness-one/pull/173) | MERGED | `PENDING_REVIEW` |
| `corrective:matterloop-taskgraph-checkpoint-recovery` | [pull#11](https://github.com/huleidada/matterloop/pull/11) | OPEN | `INSUFFICIENT_EVIDENCE` |
| `corrective:oblivion-agent-tool-loop` | [pull#1](https://github.com/Rohith-s-hub/Oblivion-agent/pull/1) | OPEN | `INSUFFICIENT_EVIDENCE` |
| `corrective:phoenix-agent-harness-budget-admission` | [pull#1](https://github.com/Phoenixrr2113/agent-harness/pull/1) | OPEN | `INSUFFICIENT_EVIDENCE` |
| `corrective:pi-loop-worktree-publication-integrity` | [pull#1](https://github.com/LEO001020/pi-loop-studio-orchestra/pull/1) | OPEN | `INSUFFICIENT_EVIDENCE` |
| `corrective:politik-transaction-denial-return` | [pull#33](https://github.com/cordfuse/politik/pull/33) | MERGED | `PENDING_REVIEW` |
| `corrective:recuris-metaagent-gate-schema` | [pull#2](https://github.com/Gen-Verse/Recuris/pull/2) | OPEN | `INSUFFICIENT_EVIDENCE` |
| `corrective:reef-polyp-experiment-queue-contract` | [pull#19](https://github.com/Coral-Bricks-AI/reef/pull/19) | OPEN | `INSUFFICIENT_EVIDENCE` |
| `corrective:spartan-persistence-recovery-contract` | [pull#1](https://github.com/CorticalComputer/Spartan/pull/1) | OPEN | `INSUFFICIENT_EVIDENCE` |
| `improvement:agent-fleet-native-lease-contract` | [pull#43](https://github.com/chankov/agent-fleet/pull/43) | MERGED | candidate `VERIFIED`¹ |
| `improvement:citadel-native-claim-exclusivity` | [pull#366](https://github.com/SethGammon/Citadel/pull/366) | MERGED | candidate `VERIFIED`¹ |
| `registry:cognee-community` | [pull#434](https://github.com/topoteretes/cognee-community/pull/434) | OPEN | `INSUFFICIENT_EVIDENCE` |

¹ Improvement fast-path candidates were manually cross-checked against first-party receipts; full live `observe` has not been run.

## Bounded semantic conclusions and missing evidence

1. **Improvement — Citadel / Agent Fleet (two fast-path candidates).** [Citadel #366](https://github.com/SethGammon/Citadel/pull/366) was merged by SethGammon at `45727eb8f54d616686e51f049e7b11035af35e96`; PR head `3567a5b6c3db98b8bd48886be6ce8be35f9bbd3c` matches the publication ledger. The [source comparison](https://github.com/opensiro-contributions/Citadel/compare/f27529aa13071ad828f07aeb76f0415ae50d1371...3567a5b6c3db98b8bd48886be6ce8be35f9bbd3c) contains only `.github/workflows/hol-plugin-scanner.yml` (two commits, complete ahead-of-base compare). [Native CI run 40039135313](https://github.com/opensiro/upstream/actions/runs/40039135313) succeeded and links internal [PR #118](https://github.com/opensiro/upstream/pull/118). [Agent Fleet #43](https://github.com/chankov/agent-fleet/pull/43) was merged by chankov at `212bbf6e2f26addb24c448070f8c8ac404da376e`, exactly matching published/final head `9647f07e88384fd9360c4d98a0d2ba18f63606de`; [native CI run 40093167700](https://github.com/opensiro/upstream/actions/runs/40093167700) succeeded and links internal [PR #119](https://github.com/opensiro/upstream/pull/119). Both authors were `xLagerFeuer` on the `opensiro-contributions` forks and both merges were performed by first-party maintainers. These satisfy the *manual observed* fast-path conditions, pending actual `observe`.
2. **Corrective — three merged, still pending reviewer completion.** [Politik #33](https://github.com/cordfuse/politik/pull/33), [DiscoveryRSI #2](https://github.com/Gen-Verse/DiscoveryRSI/pull/2), and [dsh-harness-one #173](https://github.com/chumingjun/dsh-harness-one/pull/173) are merged by project maintainers and retain the contributor and head SHAs recorded in the Corrective ledger. But their only recorded `native_test_receipt` values use mutable `blob/main/pilots/.../CONTRIBUTION_HANDOFF.md` links, and the source ledger still says `SUBMITTED`. Each requires an immutable native receipt and reviewer-attributable completion record before acceptance; current first-party merge is insufficient. [DiscoveryRSI maintainer comment](https://github.com/Gen-Verse/DiscoveryRSI/pull/2#issuecomment-6516262977) and [dsh maintainer's qualified review](https://github.com/chumingjun/dsh-harness-one/pull/173#issuecomment-6491575751) support first-party disposition, not deployed product benefit.
3. **Henterprise — one replacement intervention.** Original [#1](https://github.com/humbertobellor/henterprise/pull/1) was closed without merge; owner-created replacement [#3](https://github.com/humbertobellor/henterprise/pull/3) merged at `193e8fdac0d17abf833ab68e5179b273a6084e4c`. [First-party review](https://github.com/humbertobellor/henterprise/pull/1#pullrequestreview-5452164769) and replacement body explicitly credit the initial six contributions; the [replacement commit list](https://github.com/humbertobellor/henterprise/pull/3/commits) retains six `xLagerFeuer` author identities and one maintainer fix. This is one **attributable replacement-chain candidate**, not two merges; full source-pinned native validity/accepted-ledger gate remains open.
4. **StarNet — independent implementation, not OpenSiro merge.** [Original #56](https://github.com/androoAGI/starnet/pull/56) is closed unmerged. [Issue #55 maintainer response](https://github.com/androoAGI/starnet/issues/55) says the maintainer independently shipped a `station.status` tool in v0.13.2 with acknowledgment; [closure comment](https://github.com/androoAGI/starnet/pull/56#issuecomment-6386069014) confirms different code authorship. Proposed verdict: **NOT_ATTRIBUTABLE as an OpenSiro code merge**; possible idea influence is a distinct non-merge observation, not a verified code outcome.
5. **Scion and Oh My Agent — do not infer motive from actor alone.** [Scion #2047](https://github.com/GoogleCloudPlatform/scion/pull/2047) was closed by ptone; [maintainer comment](https://github.com/GoogleCloudPlatform/scion/pull/2047#issuecomment-5880411960) explicitly states the proposal belongs outside Scion core, supporting a non-accepted core patch. [Oh My Agent #819](https://github.com/first-fluke/oh-my-agent/pull/819) was closed by contributor `xLagerFeuer` with no review explanation observed; keep closure motive **UNKNOWN**, not automatic rejection.
6. **Other historical merged PRs — source-pinned native-effect review outstanding.** [Marveen #1516](https://github.com/Szotasz/marveen/pull/1516) has a [maintainer merge-and-CI statement](https://github.com/Szotasz/marveen/pull/1516#issuecomment-5906554788) with requested hardening; [Shep #933](https://github.com/shep-ai/shep/pull/933) and [#934](https://github.com/shep-ai/shep/pull/934) were merged by arielshad, but #933 had substantial [maintainer corrections](https://github.com/shep-ai/shep/pull/933) and #934 had [CI rerun/approval questions](https://github.com/shep-ai/shep/pull/934#issuecomment-6237687336). These are external merges, **not yet owner-accepted semantic outcomes**. Treat each Shep PR as its existing distinct recorded intervention, subject to its own native receipt and effect boundary.
7. **Unverifiable source:** [headcount #47](https://github.com/cbrock84/headcount/pull/47) returned 404. Do not count as open, rejected, merged, or proven until public first-party access or an accepted alternate provenance chain is available.

## Acceptance handoff

- **Upstream S1:** preserve this review as an *agent-authored candidate dossier*, reconcile each affected native receipt, confirm exact completion/attribution, and propose a versioned accepted-ledger schema in a separate reviewable change under [#159](https://github.com/opensiro/upstream/issues/159). A human-owned or independent reviewer verdict must be attributed to that actual reviewer if used; this agent cannot issue its own S3* certificate.
- **Live sensing:** run/observe the first successful `observe` job, retain its 90-day JSON artifact, confirm `source_sha256` and cohort digest, and compare machine reasons with this provisional manual screen. Do not convert this document's provisional counts into a machine result.
- **Organization:** keep `verified_external_outcomes=unclaimed_semantic_evidence` and Product-native fit deprecated until the accepted Upstream ledger and separate Organization collector gate pass. The merged-PR acceptance percentage remains secondary lifecycle telemetry.
