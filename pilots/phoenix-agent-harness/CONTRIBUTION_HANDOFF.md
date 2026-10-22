# Phoenix Agent Harness — preserve day-rate events for the full day window

**Status:** bounded, native source-only technical packet, `ASSESSMENT_INFORMED` / `AWAITING_EXTERNAL`. No external fork, issue, PR, provider or agent execution. External publication remains human-owned.

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

**Result: 2 PASS / 2 FAIL → 4 PASS / 0 FAIL.** `git apply --reverse --check` on the patched source: PASS. The external repository's dependency-heavy Vitest suite was not executed and is not claimed to pass.

## Scoped correction

- Diff: [`day-rate-event-retention.patch`](day-rate-event-retention.patch).
- SHA256: `3a2ed73ff19fce5146cea112918f34d5b4767c8ed0ba2f09b8a1aa56ee0553c8`.
- The retention horizon in `recordEvent()` is corrected from one hour to the longest first-party supported window, 24 hours. Minute/hour checks continue to filter by their own windows; unrelated provider and agent code is unchanged.
- GitHub PR search for a matching retention fix found no exact candidate in the inspected results; this is not a guarantee of no overlap. Confirm against current upstream before publication.

## Pending handoff

Only an authorized human/fork owner may ask for assignment if required, run full upstream CI with installed dependencies and publish the patch. Current work completes the bounded technical step but does not count as external contribution or proof of LLM safety.
