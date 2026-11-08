# Phoenix Agent Harness — preserve day-rate events for the full day window

**Status:** `ASSESSMENT_INFORMED` / `SUBMITTED_READY_FOR_REVIEW`. Public upstream [Phoenix Agent Harness #1](https://github.com/Phoenixrr2113/agent-harness/pull/1) is **OPEN, `draft: false`**, authored by authenticated `xLagerFeuer` under the finite owner mandate. External review and merge are not implied.

## First-party evidence

- Canonical Index `included S1=A`: `assessments/ph/phoenix-agent-harness.md` pinned at `396a54bb690f8ec7ce966bf9b00b241b30036307`, reviewed `2026-10-18`.
- Frozen upstream: `Phoenixrr2113/agent-harness@0f67103affd30a3c778874b890dbd5801cdbd94f` (MIT).
- [Original rate limiter](https://github.com/Phoenixrr2113/agent-harness/blob/0f67103affd30a3c778874b890dbd5801cdbd94f/src/runtime/rate-limiter.ts): `recordEvent()` always prunes historical events after **one hour**, while `buildRateLimits()`/`checkRateLimit()` explicitly support `per_day` over **86,400,000 ms**. Each subsequent recorded request can therefore delete valid daily history, allowing calls beyond the configured daily cap.
- `src/core/types.ts` admits only positive configured request limits; this packet does not attempt to change that schema or the meaning of disabled settings.

## Native before/after, no model tests

Ran the **genuine TypeScript source** via the Node 24 built-in type stripper, with isolated temporary `rate-limits.json` stores and explicit timestamps. No copied/reimplemented rate helper, mock model, LLM, agent runtime, benchmark, HTTP call or model trial.

```shell
node --experimental-strip-types tests/rate-day-window-native.test.mjs
```

| Fixed-data case | Before | After |
| --- | --- | --- |
| Two day-key entries separated by two hours | FAIL (only one retained) | PASS |
| New minute-key event must preserve existing day-key history | FAIL (day count erased) | PASS |
| Hour window ignores older-than-hour history | PASS | PASS |
| Day window discards events older than 24h | PASS | PASS |

**Result: 2 PASS / 2 FAIL → 4 PASS / 0 FAIL.** `git apply --reverse --check` on the patched source: PASS. At live publication, two matching regression cases were also added to the existing upstream Vitest suite: `npm exec -- vitest run tests/rate-limiter.test.ts` **14/14 PASS**; `npm run lint` **PASS** (Node 24.22.1, dependencies installed with `npm ci --ignore-scripts`). The standalone `.mjs` reproduction file was local test evidence and **was not included in the external PR**; the actual external changed files are `src/runtime/rate-limiter.ts` and `tests/rate-limiter.test.ts`. Full suite not run.

## Scoped correction

- Diff: [`day-rate-event-retention.patch`](day-rate-event-retention.patch).
- SHA256 (original one-hour correction only): `3a2ed73ff19fce5146cea112918f34d5b4767c8ed0ba2f09b8a1aa56ee0553c8`.
- The retention horizon in `recordEvent()` is corrected from one hour to the longest first-party supported window, 24 hours. Minute/hour checks continue to filter by their own windows; unrelated provider and agent code is unchanged.
- GitHub PR search for a matching retention fix found no exact candidate in the inspected results; this is not a guarantee of no overlap. Confirm against current upstream before publication.

## External PR publication and next action

- **Upstream:** [Phoenixrr2113/agent-harness #1](https://github.com/Phoenixrr2113/agent-harness/pull/1); `state: open`, `draft: false`, actor `xLagerFeuer`, observed 2026-10-24.
- **Direct public fork:** `opensiro-contributions/agent-harness`, branch `opensiro/fix/day-rate-retention`; verified parent `Phoenixrr2113/agent-harness`.
- **Base SHA:** `0f67103affd30a3c778874b890dbd5801cdbd94f`. **Head SHA:** `85a88a40357bb4153662b1a527c0f0d3307f153d`.
- **Exact diff:** two files (runtime source and existing Vitest suite); no unrelated files, secrets, agents or providers.
- **Native checks:** 4/4 isolated after fix, 14/14 scoped upstream Vitest, TypeScript lint PASS. GitGuardian security check had passed on the first external PR readback; broader upstream CI, acceptance and merge are pending.
- **Maintenance:** exact PR URL is registered in the finite publication ledger and hourly review target list, with additive checkpoint migration.

## Independent re-review and amendment (2026-10-24)

- Review exposed a second pre-existing correctness gap: the global `MAX_EVENTS = 10000` persisted-event cap evicted valid `per_day` entries as minute/hour/day records accumulated together. Native reproduction used 3,500 calls = 10,500 events: **observed day count 3,334 instead of 3,500**, allowing a configured cap of 3,400 to be exceeded.
- A second native regression reproduced a single key overflowing 10,000 records while still-active events were silently lost; the checker incorrectly allowed an otherwise over-cap call. Both new regression tests were **RED** before amendment.
- Published a second commit `85a88a40357bb4153662b1a527c0f0d3307f153d` to the **same** upstream PR, retaining up to 10,000 events **per key** and recording per-key truncation timestamps. When a single key itself overflows, checks **fail closed** until its missing history expires; explicit clearing removes that marker.
- **After amendment:** first-party Vitest `tests/rate-limiter.test.ts` + `tests/guardrails.test.ts` **34/34 PASS**, `npm run lint` PASS, `npm run build` PASS, `git diff --check` PASS. Native script tests only; no LLM agents/models/benchmarks.
- PR body was synchronized through the already configured VM as authenticated `xLagerFeuer` after GitHub integration returned 403 for metadata updates; independent GitHub readback confirmed body, head and `draft: false`.
- Upstream CI run `40128022518` returned `action_required` (no completed first-party test jobs). Upstream maintainer review and CI execution remain pending. No merge was attempted. Previous installations may already have lost history; the amendment cannot reconstruct it retroactively.
- The original patch and SHA256 above are **first-correction receipts** only; the final published PR diff includes the additional store-overflow hardening and regressions. Avoid claiming they hash the amended combined diff.

No additional change to this external PR is planned without new first-party CI or maintainer feedback. Continue to the next eligible candidate in the finite queue; legal/security holds remain enforced.
