# Upstream operational-readiness review — 2026-10-25

**Owner:** `opensiro/upstream`. **Status:** dated, source-backed transition review; not an external merge, autonomy assessment, S5 boundary decision, or general publication grant.

## Finding

OpenSiro Upstream has progressed from source-only contribution pilots to **real, bounded Corrective PR publication and a running read-only PR watcher**. It has **not** yet demonstrated a general autonomous contribution executor, autonomous repair/closure of external review requests, or the complete strict **Index-first assessment → functional weakness → measured product improvement → upstream feedback** chain. Keep this a sustained **adjacent engineering workstream** pending an independent Organization [#274](https://github.com/opensiro/vsm-oss-organization/issues/274) S5 decision.

## Reconstructable evidence

| Surface | Public owner/source | Verified boundary |
| --- | --- | --- |
| Organization | [START_HERE](https://github.com/opensiro/vsm-oss-organization/blob/main/START_HERE.md), [S1 domains](https://github.com/opensiro/vsm-oss-organization/blob/main/contracts/s1/domain-contracts.md), [#274](https://github.com/opensiro/vsm-oss-organization/issues/274) | Exactly **three** admitted operational domains; Upstream is **proposed, not admitted** |
| Corrective publication | [finite mandate](../docs/CORRECTIVE_PR_PUBLICATION.md), [ledger](../data/corrective-publication/2026-10-23-01.json), [PR #129](https://github.com/opensiro/upstream/pull/129) | **34 fixed cases: 13 SUBMITTED / 21 BLOCKED / 0 QUEUED** on the **unmerged PR branch**; no new external PR in the 2026-10-25 review |
| Default-branch drift | [main ledger](https://github.com/opensiro/upstream/blob/main/data/corrective-publication/2026-10-23-01.json) | At review time `main` still showed **8 SUBMITTED / 26 QUEUED**; not the branch's latest record |
| PR maintenance | [issue #125](https://github.com/opensiro/upstream/issues/125), [contract](../docs/PR_MAINTENANCE.md), [target list](../data/pr-maintenance/targets.json) | Read-only hourly watcher active on `main` with **13** targets; PR #129 proposes **18** and its checkpoint migration is not active before merge |
| Strict functional experiment | [#56](https://github.com/opensiro/upstream/issues/56), [functional effects](../docs/FUNCTIONAL_EFFECTS.md), [AgentBox #61](https://github.com/opensiro/upstream/issues/61) | Native code-level effects and hypotheses measured in bounded pilots; no completed strict assessment-derived upstream change or deployed-user benefit claim |
| General execution | [#6](https://github.com/opensiro/upstream/issues/6) | General connected contributor executor remains **inactive**; the 34-case mandate is not an indefinite publisher |
| Product-native fit | [Organization experimental ledger](https://github.com/opensiro/vsm-oss-organization/tree/main/experiments/upstream-intervention-fit) | Fit, attribution and its denominator are **Organization-owned**; neither PR count nor mergeability regrades VSM |

## Lane-by-lane status

| Lane | Demonstrated | Not demonstrated | Disposition |
| --- | --- | --- | --- |
| Portfolio / lifecycle | Source-linked registry, casebook and external outcomes | Live acceptance/productivity metric | Existing public maintenance |
| Corrective development / publication | Authentic source/test/fork/PR receipts for **13** bounded cases | All 34 published, generalized external publication authority, maintainer acceptance | Finite cohort **triaged/exhausted**, not all fixes delivered |
| External PR monitoring | Hourly sensing and issue-inbox deduplication on `main` | Self-directed code repair and accepted closure for a genuine new review request | Read-only operation active; repair loop still experimental |
| Strict functional improvement | Index-first native before/after experiments, including Kram | Complete derived-and-adopted functional improvement chain | Research continues |
| Organizational fourth S1 | [Proposal PR #275](https://github.com/opensiro/vsm-oss-organization/pull/275) and [decision #274](https://github.com/opensiro/vsm-oss-organization/issues/274) | Explicit S5 choice, applied scope change, autonomy witness | **PROPOSED / NOT ADMITTED** |

## External PR snapshot (2026-10-25)

The **18 PRs proposed** in the PR #129 watchlist were directly checked on GitHub: **16 OPEN / 1 MERGED / 1 CLOSED**, and no open PR was Draft. All **13 Corrective** submissions were **OPEN / Ready for review**; none had a `CHANGES_REQUESTED` review. Separately, [Agent Fleet #43](https://github.com/chankov/agent-fleet/pull/43) was merged after approval and [StarNet #56](https://github.com/androoAGI/starnet/pull/56) closed without merge. [BabyAI #128](https://github.com/mila-iqia/babyai/pull/128) requires review; [Phoenix #1](https://github.com/Phoenixrr2113/agent-harness/pull/1) had a passing GitGuardian check and informational bot comments. `BLOCKED`/`UNSTABLE` merge states alone are **not** evidence of code regressions. This is a dated snapshot, not a live dashboard.

The **21 blocked Corrective cases** are neither published repairs nor proven upstream refusals. Specific reasons and historical native-test limits live in each ledger row and its handoff. Reopening needs new admission and any required legal, security, maintainer or scope clearance; do not silently turn them into `SUBMITTED`/`MERGED`.

## Authority and recovery boundaries

- **Organization** owns the bounded S1 scope, role/authority contracts and parent S5 choice. Its `TODO.md` selects only in-scope organizational work; adjacent Upstream cannot be silently added as a fourth S1 task.
- **Upstream** owns its external contribution ledger, native receipts, maintenance watcher, functional effects and public portfolio. `main` is the ordinary source of truth; until PR #129 merges, a fresh session must inspect its **exact head branch** to recover the new 13/21 and 18-target snapshot.
- **External maintainers** own acceptance, issue assignment, CLA/DCO/security policies and merge. A reviewer comment does not create authority for a new write.
- **Index/Skills/Profile** retain assessment, methodology and semantic ownership. Product-native fit remains an independently evidenced claim, not a VSM grade or raw PR count.

## Sequential transition gates

1. **G1 — Git-native synchronization:** review/merge [PR #129](https://github.com/opensiro/upstream/pull/129) through ordinary integration authority. After **actual merge**, verify default-branch ledger **13/21/0**, watcher **18**, clean CI and a safe additive bot-checkpoint migration. Do not present PR-branch state as active on `main` prematurely.
2. **G2 — maintenance return:** close a genuine new maintainer request or CI regression with current source/policy, native RED/GREEN where needed, an authorized existing-PR update, and a recorded outcome or justified escalation/no-change. Monitoring by itself is not autonomous closure.
3. **G3 — strict #56 chain:** select a current canonical Index finding before product work, measure genuine native before/after, and seek independent upstream feedback. [AgentBox #61](https://github.com/opensiro/upstream/issues/61) still requires project-side design feedback before claiming fit. Never substitute Corrective count or live LLM benchmarks.
4. **G4 — Organization choice:** [#274](https://github.com/opensiro/vsm-oss-organization/issues/274) requires the legitimate S5 holder to choose `ADMIT_WITH_ENVELOPE` or `KEEP_ADJACENT`. Even if admitted, a distinct application PR and operational witness must precede any grade claim.

**Immediate posture:** continue the adjacent Upstream engineering/maintenance workstream under its present rights. Do not enlarge the exhausted finite 34, assume new external posting permission, or auto-contact maintainers. All in-scope product testing remains **native deterministic script/CLI/source testing only**; no live LLM-agent/model-provider trials.
