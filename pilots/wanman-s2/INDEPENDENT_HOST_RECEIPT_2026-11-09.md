# Wanman S2 admission — independent native runner receipt (2026-11-09 UTC)

**Outcome:** bounded source-native correctness benefit confirmed: one failure and one control pass on the untouched product implementation with the identical new native regression test, then both pass with the proposed fix. The existing task-pool/supervisor suite and TypeScript typecheck pass after. No deployed benefit, VSM regrade, third-party submission or external maintainer acceptance is implied.

## Origin and exact source

- Index: [`opensiro/vsm-harness-index@46219bf`](https://github.com/opensiro/vsm-harness-index/commit/46219bf103b0b122d86abc3ca70ae3d8bc820e2c), `assessments/wa/wanman.md`, `chekusu/wanman@d3a8138de6c21981a4f1449a7b3f201e724c55c9`, S2=C.
- Pre-current-source hypothesis committed first: [`97273405215b8652073ddba5cfd222233c321328`](https://github.com/opensiro/upstream/blob/97273405215b8652073ddba5cfd222233c321328/data/assessment-candidate-batches/2026-11-09-18-HYPOTHESES.md). Predicted simultaneous overlapping RPC tasks could both pass non-atomic admission, while disjoint scopes should remain valid. The later investigation found the exact first-party `checkConflict` → `await create` gap in `packages/runtime/src/supervisor.ts` and SQLite `TaskPool`.
- External source ref: [`chekusu/wanman@d3a8138`](https://github.com/chekusu/wanman/tree/d3a8138de6c21981a4f1449a7b3f201e724c55c9), Apache-2.0. The source was clean at the pinned ref before applying the test patch.
- First-party entry: original `packages/runtime/src/__tests__/supervisor.test.ts`, original Vitest harness invoking `Supervisor.handleRpcAsync(TASK_CREATE)` with the real SQLite-backed `TaskPool`; no copied or simulated product implementation.
- Identical before/after test diff: [`native-regression.patch`](native-regression.patch), SHA256 `0fe4f64675c1bfd1c91720e80767ba7a9bf1b06727b8b3b625ab8a6a4da99f07`. Test adds overlapping two-call admission and a disjoint two-call control to the existing first-party suite.
- Production diff, applied **only after the RED run**: [`native-fix.patch`](native-fix.patch), SHA256 `4b61fca8bf5d7cd9f0db12d0b47dc00295468ad6362cbfcc1294bca2a3bd73b4`.

## Distinct deterministic host, environment and commands

- Runner: configured `dev-alpha-2` SSH tool executing on verified **Zhdanov** VM (`device_id=8493ff56-7ee6-4d0a-afe1-d2cdebc3456a`), distinct from the chatbot's local workspace. Host ran the target native tests inside Docker; the chatbot submitted jobs and inspected independent session outputs, **never ran native before/after validation in its own process**.
- Disposable host path (may expire): `/tmp/opensiro-wanman-b18-nG1E8gkL/source`, local clone at exact source commit; evidence clone `/tmp/opensiro-wanman-b18-nG1E8gkL/evidence`. Host runner has no third-party repository write authorization. No persistent service was installed.
- Image: `node:22-bookworm-slim`, digest `node@sha256:5ec23b7c622b00547753bc6ffd78085dd868a68aeb41c8e0a1418f033e13d96d`.
- Node `v22.23.4`, Corepack pnpm `9.15.0`, Vitest `4.1.4`; `corepack pnpm install --frozen-lockfile` completed on the exact source (independent install session `e337c0a5-3ecf-427e-94be-aaf79d5a33ad`, exit `0`, `Done in 11.3s`).

On host, with an isolated source checkout at the pinned baseline:

```sh
git -C /tmp/opensiro-wanman-b18-nG1E8gkL/source apply /tmp/opensiro-wanman-b18-nG1E8gkL/evidence/pilots/wanman-s2/native-regression.patch
docker run --rm -v /tmp/opensiro-wanman-b18-nG1E8gkL/source:/work -w /work node:22-bookworm-slim sh -c 'corepack enable && corepack pnpm --filter @wanman/runtime exec vitest run src/__tests__/supervisor.test.ts -t "simultaneous tasks"'
```

Runner before session `0578ac78-f4b4-4e82-b892-04566ec006f8`, exit `1`:

```text
FAIL admits at most one of two simultaneous tasks with an overlapping scope
AssertionError: expected [ …(2) ] to have a length of 1 but got 2
PASS admits two simultaneous tasks with disjoint scopes
Test Files 1 failed (1)
Tests 1 failed | 1 passed | 39 skipped (41)
```

Then the separate host applied the exact production patch, without replacing or changing the regression test:

```sh
git -C /tmp/opensiro-wanman-b18-nG1E8gkL/source apply /tmp/opensiro-wanman-b18-nG1E8gkL/evidence/pilots/wanman-s2/native-fix.patch
docker run --rm -v /tmp/opensiro-wanman-b18-nG1E8gkL/source:/work -w /work node:22-bookworm-slim sh -c 'corepack enable && corepack pnpm --filter @wanman/runtime exec vitest run src/__tests__/supervisor.test.ts -t "simultaneous tasks"'
```

Runner after session `e842fd76-3081-4daa-8126-cd4a4aa606e4`, exit `0`:

```text
Test Files 1 passed (1)
Tests 2 passed | 39 skipped (41)
```

Additional native controls on the **patched** exact source, independently executed on the same host:

```sh
docker run --rm -v /tmp/opensiro-wanman-b18-nG1E8gkL/source:/work -w /work node:22-bookworm-slim sh -c 'corepack enable && corepack pnpm --filter @wanman/runtime exec vitest run src/__tests__/supervisor.test.ts src/__tests__/task-pool.test.ts'
docker run --rm -v /tmp/opensiro-wanman-b18-nG1E8gkL/source:/work -w /work node:22-bookworm-slim sh -c 'corepack enable && corepack pnpm --filter @wanman/runtime typecheck'
```

- Native control session `fc22791a-9645-4c1a-8f34-b9beea8b90e4`, exit `0`: `task-pool.test.ts` **27 passed**, `supervisor.test.ts` **41 passed**, **68 passed / 0 failed** overall.
- Typecheck session `0246fdf2-20be-4f76-b66e-2dfec12241fe`, exit `0`: `@wanman/runtime` → `tsc --noEmit`, PASS.
- Host pinned-source readback and patch hashes: session `c68de6dc-6a5b-45ef-8830-abf997d4de63`, exit `0`; final `git diff --check` and image digest readback: session `41fd92e9-2970-4a8b-8d81-329a5ab93ae6`, exit `0`.

**Log retention:** remote monitoring sessions are tool-owned and may expire; the exact session IDs above name the attributable runs, while this checked-in receipt preserves the command, image/source/test/production patch identifiers and observed RED/GREEN outputs. Re-execution uses the archived patch files and the exact public source commit, not a permanently running host. Dependencies and upstream code could change outside these pins.

## Bounded interpretation and next step

- **need / mechanism / counterfactual / scope:** all PASS for the two-RPC overlapping-scope invariant. The test shows a real duplicate admission before the patch and correct exclusion afterward, while disjoint jobs remain admitted. The fix uses `TaskPool.createIfUnconflicted` with a SQLite `IMMEDIATE` transaction around both the active-scope query and insertion; the existing `create` and `checkConflict` entry points remain available.
- No LLM agent, model provider, Browser workflow, benchmark or external task was executed. The test establishes admission correctness under these specified inputs, not systemwide concurrency throughput, deployment benefit or absence of unrelated races.
- External fork, branch, PR and maintainer feedback remain **NOT_EXECUTED** pending a separate effective grant under [Upstream #6](https://github.com/opensiro/upstream/issues/6). Internal Upstream packet review may proceed without that external grant.
