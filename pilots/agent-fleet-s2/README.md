# Agent Fleet S2 — atomic recovery of the native writer lease

**State:** reviewed OpenSiro-internal patch; external delivery NONE; user benefit NOT_MEASURED.

- **Origin:** frozen assessment candidate batch 11 (`agent-fleet-native-lease-contract`), selected from [Index Agent Fleet assessment](https://github.com/opensiro/vsm-harness-index/blob/main/assessments/ag/agent-fleet-chankov.md) at recorded Index SHA 396a54bb690f8ec7ce966bf9b00b241b30036307. S2=C is bounded to native writer lease for effectful poll merges, not universal hub coordination.
- **First-party source:** [chankov/agent-fleet@1d846daf52e4b71948cf31448058454db5633241](https://github.com/chankov/agent-fleet/commit/1d846daf52e4b71948cf31448058454db5633241); default main at check time 2026-10-23.
- **License:** first-party MIT LICENSE verified. CONTRIBUTING says search duplicates and avoid edits to vendored skills; this is not a vendored skill change. Search of existing issues/PRs found no exact stale-lease double-owner fix; dated search is not a guarantee of no future duplicate.
- **Patch:** [stale-lease-atomic-recovery.patch](stale-lease-atomic-recovery.patch). SHA-256 `702d91ef293cd9db94abc775035bf981b7aecd659cf01fbb7b4c16cf71db40e4`. Four source/test files.

## Falsifiable native failure

The first-party `acquireWriterLease` uses exclusive `wx` creation, but an existing dead-owner lease follows the read / unlink / replace path without serializing two contenders. Two native Node 22 processes both observe the original stale lock and may each unlink/recreate it, **both returning CLAIMED**.

[Regression worker and test](stale-lease-atomic-recovery.patch) use a fixed dead pid and synchronized snapshot barrier, without Pi, agents, model calls or external network. During measurement the new owner is kept alive with a fixed native owner-pid surrogate to distinguish a stale recovery collision from a legitimate successive acquisition.

| Verification | Pinned original | Patched |
| --- | --- | --- |
| Simultaneous recovery of one stale lease | 1 failure (both CLAIMED) | PASS (one CLAIMED; one LEASE_HELD) |
| Existing first-party lease tests | 2 PASS | 2 PASS |
| Exact patch against clean original checkout | not applicable | git apply PASS, test red to green |
| Repeated matched scripted tests | not applicable | 3 repeats, 3/3 checks each PASS |

The patch serializes acquisition, stale recovery and release with a local atomic guard directory. An abandoned guard is deliberately **fail-closed** after a bounded wait. The guard does not prove coordination across unrelated/uncooperative processes or networked filesystems, and does not protect other file writes. A permanently abandoned guard requires explicit operator cleanup after checking actual ownership; do not silently steal it.

The new two-process test and the existing writer-lease test are wired into the first-party native `test:fast` suite. A [read-only CI replay](../../.github/workflows/agent-fleet-s2-native-replay.yml) injects tests on the frozen original then applies the actual production patch and reruns native tests. The CI outcome must be read from GitHub, not predicted from this document.

## Attribution / external publication

**Assessment-derived selection and native correctness effect**, not proof of autonomous S2, increased VSM grade, user productivity or third-party adoption. Only the existing bounded 34-Case Corrective mandate permits external PRs without separate S5 action; **Agent Fleet is an ungranted Improvement and was not published externally**.
