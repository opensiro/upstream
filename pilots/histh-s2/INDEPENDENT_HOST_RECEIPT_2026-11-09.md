# Histh S2 — independent native runner receipt (2026-11-09 UTC)

**Claim boundary:** one narrowly verified first-party tool-batching correctness change. Executed in a **separate dev-alpha-2 server-side CLI workspace** (origin `server`), not this chatbot's scratch runtime. This is a deterministic native test run, not a live LLM/agent/provider/Browser quality test, upstream maintainer CI or deployed proof.

## Immutable inputs

- Upstream source repository: [`ayandexyz/Honey-I-Shrunk-the-Harness`](https://github.com/ayandexyz/Honey-I-Shrunk-the-Harness/tree/1ac18ffb723f107391b82a34bfa9dc06abf0123a), exact `git rev-parse HEAD = 1ac18ffb723f107391b82a34bfa9dc06abf0123a`.
- Pre-current-source prediction: [Upstream checkpoint `95d9306537e0cdf6877942215a53ff679f561b7b`](https://github.com/opensiro/upstream/commit/95d9306537e0cdf6877942215a53ff679f561b7b), based on Index S2=C review ref `f2aff641e55c2e6bb8c55a8fb82b67bdf2addd1a`.
- Native regression: [`native-regression.patch`](native-regression.patch), SHA-256 `72132dfb27481bab69492f4ded16bf1091c6db2267126010f3965bcd368825b1`.
- Native fix: [`native-fix.patch`](native-fix.patch), SHA-256 `74658928fc6b240990e23cfdf57cb0e75f8b65a78516b1ad4cc617b6bee46fe7`.
- Both patch hashes produced by separate host `sha256sum` after fetching files from [frozen Upstream commit `151cc55`](https://github.com/opensiro/upstream/commit/151cc557390d6ed9bdafaa0784dd29defc6fd926). `git apply --check` passed before each patch application.
- Runtime: Linux x86_64, portable Node.js `v22.19.0`, `pnpm@10.0.0`, installed source workspaces with Playwright browser download skipped and dependency install scripts disabled.

## Matched first-party native execution

1. **Baseline RED** — apply *only* `native-regression.patch` to exact upstream source. Run `corepack pnpm exec tsx --test apps/core/src/tools/batching.test.ts`. Runner session `a3e8dc74-d9fe-4063-85f9-18be716d9961`, exit **1**. **9 tests, 8 PASS, 1 FAIL.** The newly preregistered implicit-mode case expected two sequential tasks, but source-native `planToolBatches` returned `[{start:0,end:2,parallel:true}]`; `ERR_ASSERTION`. This is a real first-party planner regression, not a mock that bypasses the mechanism.
2. **After GREEN** — apply `native-fix.patch` on the same pinned checkout, retaining identical regression. Rerun the **same** command. Runner session `81d4ec1c-c43b-4b80-8bf4-f43dde471bd8`, exit **0**. **9 tests, 9 PASS, 0 FAIL**, including explicit read-only parallel control and writing-agent sequential control.
3. **Typecheck** — `corepack pnpm --filter @thisisayande/freecode-core check-types` initially exited 2 because this clean `--ignore-scripts` install had not built first-party `@thisisayande/freecode-shared` declarations (session `d2d6d929-607d-4aa8-bbe0-0c1ac77c5d7d`; 14 TS2307 missing-module declarations). After the repo-documented `corepack pnpm --filter @thisisayande/freecode-shared build`, the same core `check-types` passed exit **0** (session `4039f67c-71d8-469e-b8fc-fcc1e61401a3`). No application-source edit was needed for this setup issue.
4. **Diff hygiene** — native runner `git diff --check` exit **0**, source HEAD unchanged, only `apps/core/src/tools/agent.ts` and `apps/core/src/tools/batching.test.ts` modified (session `ab2bcf76-60a7-40e2-9697-92eb720f5e1a`).

All command/session IDs refer to the connector's actual separately executed monitored sessions; the public receipt summarizes their result, but the session log service is not publicly mirrored here. No full all-package suite, live model eval, release, external PR CI, or deployed throughput/safety outcome is claimed.

## Interpretation

**Supported:** the actual native planner previously admitted two implicit custom build-role calls as parallel; the scoped change serializes ambiguous calls and keeps explicitly read-only calls parallel. Bounded `ASSESSMENT_DERIVED` mechanism benefit with native RED→GREEN and clean typecheck.

**Not supported or performed:** new autonomous S2 ownership, Index regrade, measured end-to-end model outcomes, production performance, approval from the target maintainer, third-party publication, or fulfillment of the target's optional/required A/B model-evaluation policy. Preserve these as separate future gates; do not run forbidden live model/Browser/provider trials to fill them.
