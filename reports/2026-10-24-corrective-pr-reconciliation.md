# Corrective external PR publication — live reconciliation (2026-10-24)

**Owner:** [Upstream #56](https://github.com/opensiro/upstream/issues/56). **Bounded mandate:** `CORRECTIVE-PUBLISH-2026-10-23-01` in [publication contract](../docs/CORRECTIVE_PR_PUBLICATION.md). **Type:** readback and record reconciliation; no new external PRs, branches, merges or simulated agent tests were created by this inventory.

At the time of live inspection, the frozen 34-case publication ledger still said **34 `QUEUED`** despite seven external Corrective PRs actually being published. Each of the following was confirmed as **OPEN, not Draft**, authored by authenticated contributor `xLagerFeuer`, with a **public direct fork** under `opensiro-contributions` and a matching upstream parent. These seven exact PR URLs were already in the hourly maintenance manifest.

| Frozen candidate | External upstream PR | Public direct fork | Observed head SHA |
| --- | --- | --- | --- |
| `oblivion-agent-tool-loop` | [Oblivion-agent #1](https://github.com/Rohith-s-hub/Oblivion-agent/pull/1) | `opensiro-contributions/Oblivion-agent` | `1967f1df19f80cd34d4a4b70756ae1589e075c8c` |
| `politik-transaction-denial-return` | [politik #33](https://github.com/cordfuse/politik/pull/33) | `opensiro-contributions/politik` | `23570ac446c5e84d20fd8794c9b578e8245c3a43` |
| `agent-loop-numeric-verifier-grounding` | [agent-loop #1](https://github.com/Onipounds/agent-loop/pull/1) | `opensiro-contributions/agent-loop` | `c0135171cb38e74a70108b6b8b6afde57e9d223e` |
| `discoveryrsi-campaign-history-integrity` | [DiscoveryRSI #2](https://github.com/Gen-Verse/DiscoveryRSI/pull/2) | `opensiro-contributions/DiscoveryRSI` | `03122c3c081fe2e386e3b6e7a250515f82b1ac15` |
| `matterloop-taskgraph-checkpoint-recovery` | [matterloop #11](https://github.com/huleidada/matterloop/pull/11) | `opensiro-contributions/matterloop` | `c8dfad22d368e439172293e8bcc50af486d385bb` |
| `recuris-metaagent-gate-schema` | [Recuris #2](https://github.com/Gen-Verse/Recuris/pull/2) | `opensiro-contributions/Recuris` | `1445a8bf45825a8b5b8e687c236253b810e244d0` |
| `pi-loop-worktree-publication-integrity` | [pi-loop-studio-orchestra #1](https://github.com/LEO001020/pi-loop-studio-orchestra/pull/1) | `opensiro-contributions/pi-loop-studio-orchestra` | `58308a41f631013b0e6783fb71886dfbd4cfedbd` |

Exact observed base SHA, contributor attribution and first-party native-test handoff for every case are in the [ledger](../data/corrective-publication/2026-10-23-01.json). The pinned assessment batch source files remain unchanged.

## Accounting after reconciliation

- Authorized scope: **34** cases, exactly the same original candidate IDs and order.
- Confirmed `SUBMITTED`: **7**, all with external PR evidence. Their state was OPEN/Ready for review at readback; that state is not a promise of future acceptance.
- Remaining `QUEUED`: **27**; no discovered author-owned external PR under the 34 source repositories at this readback. Do not treat these as published.
- Submissions inside hourly review watcher: **7 / 7**. The other existing watchlist entries concern improvement/connector/legacy work and are not silently classified as Corrective submissions.
- Next queued case (2026-10-24): `raven-stale-edit-ledger`, subject to live upstream/policy/native preflight before any publication.

## Permanent drift guard

`python3 scripts/corrective_publication_queue.py validate` now fails closed whenever a recorded `SUBMITTED` or `MERGED` Corrective PR is not registered in the [hourly maintenance watchlist](../data/pr-maintenance/targets.json). The [maintenance workflow](../.github/workflows/pr-maintenance.yml) runs this guard and native offline tests on relevant PRs and each schedule/dispatch. Future submission records and target registration must land in one reviewable change; removing a closed target without archival migration is not justified by the mere closure.

**Important separation:** Existing external StarNet [PR #56](https://github.com/androoAGI/starnet/pull/56) was closed unmerged after the upstream maintainer independently shipped the functionality in v0.13.2. It is **not** one of these 34 Corrective cases and must not change this count; its lifecycle remains in the maintenance watchlist for audit.
