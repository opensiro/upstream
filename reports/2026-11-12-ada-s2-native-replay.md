# Ada S2: worker copy-back claims and git porcelain — native replay receipt

**Recorded:** 2026-11-12 UTC. **Owning issue:** [Upstream #56](https://github.com/opensiro/upstream/issues/56). **Frozen cohort:** [batch 33](../data/assessment-candidate-batches/2026-11-12-33.json). **Original:** [black141312/ada@20c3dd8813ce82fc82c2b243094ea239502e029f](https://github.com/black141312/ada/tree/20c3dd8813ce82fc82c2b243094ea239502e029f), MIT; current `main` matches the 2026-10-23 canonical [Index S1=A/S2=C assessment](https://github.com/opensiro/vsm-harness-index/blob/85ae995fc2551ac0a076609bce0300d075cac2d5/assessments/ad/ada.md).

## Pre-source origin and distinct mechanisms

The [pre-source checkpoint `996c731`](https://github.com/opensiro/upstream/commit/996c7311ab31fba0edca72d832b226bb349a34b1) was committed **before any current original source/policy inspection**. It predicted **stale reserved output paths after an isolated worker's failed copy-back** within the first-party parent `claimedPaths` S2 coordinator. This mechanism is **ASSESSMENT_DERIVED**, independent of whether the autonomy grade changes.

Actual first-party source revealed **another distinct bug** while building the regression: `worker.ts::git()` uses `.trim()` on `git status --porcelain -uall`. A tracked modification begins with a significant leading status-space; trimming it before `slice(3)` drops the *first character of the first pathname* (`target.txt` → `arget.txt`). This was a **source-discovered supplementary parsing defect**, **not** retrospectively claimed to be predicted by the VSM assessment. The same bounded production patch contains both repairs because correct path parsing is necessary to make the intended S2 reservation test meaningful.

The S2-specific reproduced failure *after correcting only that parser*: deleting a tracked file in an isolated worker should not reserve its unchanged parent path (deletions are intentionally not propagated); a failed `copyFileSync` after `claim(paths)` reserves an uninstalled path and blocks a later safe retry. Both cases are first-party product behavior, not invented VSM regrading.

## Replay, source artifacts and native controls

**Runner:** authenticated Linux `zhdanov` VM (dev-alpha-2), official Node.js `v24.22.3` downloaded to an isolated `/tmp` directory and SHA256-verified against the official Node distribution manifest, npm `11.19.1`. `npm ci --ignore-scripts --no-audit --no-fund` installed the original project dependency graph in the temporary checkout. Real project `src/client/worker.ts::runIsolatedWorker` creates real disposable Git worktrees and receives fake locally executed child CLI outputs; no LLM, provider, browser or account operations. All parent repositories and worker files are disposable test fixtures.

The **same exact test-first patch** was applied to a second clean worktree at original `20c3dd8813ce82fc82c2b243094ea239502e029f`:

| Run | Observed result |
| --- | --- |
| Original source + native regression patch, `node --test src/client/worker.test.ts` | **RED: exit 1, 0 PASS / 4 FAIL**; original Git porcelain path lost first character; uninstalled reservations failed |
| Original code with only parser fixed during hypothesis isolation | **1 PASS / 2 FAIL** across then-existing three tests; isolated claim-leak issue remains distinct |
| Original source + identical regression and production patches | **GREEN: exit 0, 4 PASS / 0 FAIL**; no detached worker claim leak; installed first-writer claim still rejects a second writer |
| Source branch `npm run typecheck` (`tsc --noEmit`) | **PASS, exit 0** |
| Source branch `npm run selfcheck` | **INCOMPLETE: timeout exit 124**; stopped after the `pinned ...` console trace, no `selfcheck OK` |
| **Unmodified original source** with the same dependency install/runtime, `npm run selfcheck` | **Also INCOMPLETE: timeout exit 124** at the same `pinned ...` trace. This documents a baseline/environment limitation, not a proved general upstream regression or a successful selfcheck |

Regression scenarios: (1) tracked-file deletion does **not** leave an unpropagated claim; (2) forced destination copy failure (`EISDIR`) releases only uninstalled claims, then retry succeeds; (3) tracked modification preserves exact full path; (4) successful installed path retains claim and denies a later overlapping writer. No external or live-agent end-to-end run is claimed.

**Exact reviewable source patches:**
- [Production code patch](../pilots/ada-s2/native-fix.patch), SHA256 `60d55e1aa9427c22e0080eeeab46e8a63ed36e104b69c897956dceb5925e4686`: `src/client/worker.ts` and `src/client/agent.ts`.
- [First-party native regression patch](../pilots/ada-s2/native-regression.patch), SHA256 `bf29b645900840a207a2606aa0d9dffb2d59a004c75449285804f2c7580b0dc3`: new `src/client/worker.test.ts`.
- After-patch SHA256: `src/client/agent.ts` = `2bfc292f7655982e20204ec584d6c9cba8ba39835a0050593153f034873bd17a`; `src/client/worker.ts` = `d3c64b03286add08546ecc7caf8fd70a637b8c275a62bc0111b3c6062eba3b3e`; `src/client/worker.test.ts` = `1bdbe30fc6dacc6c6728e28b37d92c0d00d74f01ca7d824249dd0aad6cbda9dd`.
- Host trace filenames: `/tmp/opensiro-ada-b33-native-red-v2.log`, `/tmp/opensiro-ada-b33-after-parser-only.log`, `/tmp/opensiro-ada-b33-replay-red.log`, `/tmp/opensiro-ada-b33-replay-green.log`, `/tmp/opensiro-ada-b33-typecheck-final.log`, `/tmp/opensiro-ada-b33-selfcheck-bounded.log`, `/tmp/opensiro-ada-b33-baseline-selfcheck.log`. These are **local executor logs**, not separately published immutable GitHub artifacts. The exact patches/tests are preserved in this PR.

## Four source-native fit gates and publication boundary

- **Need=PASS:** two original product-level behaviors observable in real first-party worktree/copy-back: stuck path ownership after failed/non-propagated output; first tracked-file status path mangled.
- **Mechanism=PASS:** synchronous `claimPaths` precedes `copyFileSync` and has no rollback, while `trim()` removes status-space before fixed-width porcelain parsing.
- **Counterfactual=PASS (bounded):** identical native tests fail on original and pass on patched source; successful writer's exclusive claim is preserved.
- **Scope=PASS for the three source/test files:** changes limited to built-in Git-worktree integration, no new dependency/provider behavior. The extra parser fix is explicitly *source-discovered*, not part of the original S2 prediction.

**Publication disposition: `BLOCKED_EVIDENCE` until first-party full `selfcheck` can be made green or the external maintainer explicitly accepts a bounded alternative.** The target `CONTRIBUTING.md` requires both `npm run typecheck` and `npm run selfcheck` before PR. We verified typecheck and matched native regression, but cannot truthfully claim complete selfcheck despite the equally observed baseline timeout. No working fork creation, branch push, fork-local or original external PR, maintainer acceptance, deployed effect, human review, or Index autonomy grade update is claimed. If the legal/source policy or default branch changes, re-run all gates before any external action.
