# NanoCoder S2 — opt-in replay of the newest busy event

**Status: INTERNAL FEATURE PROTOTYPE; PRODUCT FIT PENDING.** This patch is *not* a repair of an unintended v1 bug: current first-party behavior deliberately drops events while a subscription has an in-flight worker.

- **Origin / ownership:** [OpenSiro #56](https://github.com/opensiro/upstream/issues/56), [canonical Index assessment](https://github.com/opensiro/vsm-harness-index/blob/21b0887f16bc12de22b0cecbcfcccb4862c90c83/assessments/na/nanocoder.md), S2=C. The assessment documents `BackpressureDispatcher`'s drop-on-busy relation. Earlier [OpenSiro PR #23](https://github.com/opensiro/upstream/pull/23) classified this general S2 space as needing further native and maintainer evidence; this native replay does **not** retroactively qualify that study.
- **First-party source:** [Nano-Collective/nanocoder@ef41e8a](https://github.com/Nano-Collective/nanocoder/commit/ef41e8aa0092e2c3e7b5932f480f920bcffb68da), MIT in [LICENSE.md](https://github.com/Nano-Collective/nanocoder/blob/main/LICENSE.md). [CONTRIBUTING](https://github.com/Nano-Collective/nanocoder/blob/main/CONTRIBUTING.md) directs unspecified features to issue/spec discussion. No external issue or discussion posted.
- **Patch:** [latest-busy-event-replay.patch](latest-busy-event-replay.patch), SHA-256 `39222202f3f8ed7cad8a252c856b122a7844e91518b179fd0dc9f8b97acaf5b1`. Three first-party files: `source/events/backpressure.ts`, `source/daemon/daemon.ts`, and a standalone `scripts/test-backpressure-replay.mjs` using Node 22's native TypeScript transform.

## Feature hypothesis, not a bug claim

An opt-in `replayLatestWhileBusy` flag on `BackpressureDispatcher` / programmatic `startDaemon` options retains **one newest event per in-flight subscription** and dispatches it serially after the current job succeeds. Intermediate pending events coalesce and invoke the existing `onDrop` telemetry callback. Default drop behavior remains unchanged; the daemon does not turn the flag on by default and no user-config option was added.

**Original source + same new native test:** expected RED on replay scenario, original calls `[a]` rather than `[a,c]`; default drop remains PASS.

**Patched source:** 6/6 native scenarios PASS: default drop, opt-in replay newest/coalescing, independence across subscriptions, disposal, failure fail-closed/recovery, and file debounce after a busy run. Node 22.19 syntax transform checks PASS. `git diff --check` PASS.

Read-only source-pinned [CI replay](../../.github/workflows/nanocoder-s2-native-replay.yml) replays the exact archived patch. A production daemon with real providers was not started; full package AVA/typecheck suite and user configuration/deployment integration are not claimed PASS. No LLM/model runs or provider calls.

## Gate boundary

This is an **ASSESSMENT_DERIVED_FEATURE_HYPOTHESIS / NEED_UNVERIFIED**, not a qualified strict assessment-derived success: a maintainer need, native operational benefit under supported config, performance/cost tradeoffs, and external acceptance remain unverified. The opt-in replay can create extra sequential work and does not resolve semantic conflicts. Before any external contribution, first obtain issue/spec discussion per first-party policy, recheck current head/duplicates and obtain the applicable S5 authority. The prior finite 34-case Corrective publication grant does not apply. External fork and PR: **NONE**.
