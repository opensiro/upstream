# Citadel S2 — atomic scope-claim admission

Status: INTERNAL PATCH / NATIVE SOURCE EFFECT. Product benefit and third-party delivery NOT_MEASURED.

**Assessment origin:** [canonical Citadel Index](https://github.com/opensiro/vsm-harness-index/blob/main/assessments/ci/citadel.md) S2=C expressly records the non-atomic check/write race in the first-party scope-claim registry. Selection was made with prior case context; this is not a blind independent origin.

**External baseline:** [SethGammon/Citadel@63e538c](https://github.com/SethGammon/Citadel/commit/63e538c65a5e09384c464bff5892cf6e9f601949), main as read 2026-10-23. First-party MIT license and CONTRIBUTING.md verified. Related first-party [PR #355](https://github.com/SethGammon/Citadel/pull/355) fixed path normalization, not this cross-process check/write atomicity.

**Patch:** [atomic-claims.patch](atomic-claims.patch); SHA-256 90c0362e33c825e967f136b1b357e143a6f5647d003857c85a000fe0618fc772. Five first-party source/test files.

## Measured native behavior

Two independent Node 22 processes synchronized before calling the real claimScope function and paused after receiving a claims-directory snapshot.

| Scripted scenario | Original | Patched |
| --- | --- | --- |
| Simultaneous same-scope claim | BOTH CLAIMED (FAIL) | one CLAIMED / one SCOPE_OVERLAP (PASS) |
| Different scopes | Not needed for baseline | both CLAIMED (PASS) |
| Release and reacquire | Not needed for baseline | PASS |
| Abandoned transaction lock | No lock | CLAIM_BUSY, no claim persisted (PASS) |
| Single-process collision | Existing mechanism | PASS |
| Original coordination regression | Existing suite | PASS |
| Sweep with temporarily unavailable claim lock | not applicable | preserves stale instance for retry (PASS) |
| Unregister while claim lock is held | not applicable | fails closed; leaves instance/claim intact (PASS) |

The new first-party test script is scripts/test-coordination-claim-atomicity.js, included in the patch and integrated into scripts/test-all.js. Read-only CI workflow: [citadel-s2-native-replay.yml](../../.github/workflows/citadel-s2-native-replay.yml).

The lock directory is an atomic local-filesystem coordination primitive. It serializes first-party claim creation and release, including cleanup of stale instances; it waits a bounded period and fails closed if abandoned, never steals the lock. This is not general shared-file write safety, authorization, a remote/filesystem-distributed guarantee, or user-visible model effectiveness. Only native scripts ran; no live model or LLM agents.

## Upstream cross-platform gate

Citadel's own contribution policy tests Node 22/24 on Ubuntu, macOS and Windows. The [source-pinned native CI workflow](../../.github/workflows/citadel-s2-native-replay.yml) now replays the specific **BOTH CLAIMED** baseline failure and the exact patched source on a **3 OS × 2 Node** matrix. It verifies the specific before-failure signature so an unrelated crash cannot count as expected RED, while the full first-party `npm test` remains separately required on Ubuntu/Node 22.

The first Windows matrix attempt stopped at SHA validation before running native tests: Git checkout had converted the archived diff from LF to CRLF. The replay workflow now normalizes the diff bytes back to canonical LF, checks the immutable checksum, and resets the pinned Citadel checkout under `core.autocrlf=false` on Windows before applying it. This is CI portability handling, **not** a change to the claimed native defect or a Windows product-fix. The expanded matrix must be read back from the actual current GitHub Actions run before cross-platform PASS can be claimed; the earlier one-run Ubuntu receipt alone does not establish Windows/macOS support. No LLM or agent-quality tests are used.

## Publication boundary

OpenSiro S5 finite Corrective mandate does NOT authorize external publication of this Improvement. No external fork or PR was created. Refresh license, contributor policies, duplicate PRs and head before any authorized delivery. Full suite and remote CI statuses are recorded separately; don't interpret the patch as accepted upstream or as a VSM-grade change.

The v2 patch also routes `unregisterInstance()` through the same serialized claim release, and changes stale-instance sweep to **release the claim before removing its instance record**; a temporarily busy or abandoned lock therefore cannot erase the retry handle. These are source-native safety regressions, not product deployment claims.
