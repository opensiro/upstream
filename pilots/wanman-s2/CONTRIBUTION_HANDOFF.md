# Wanman — serialize competing task scope admission

**Status:** `ASSESSMENT_DERIVED / AWAITING_EXTERNAL` — internal, source-tested technical handoff only. Neither a patch to the original project nor an external PR has been published. Owner: [Upstream #56](https://github.com/opensiro/upstream/issues/56); external publication authority remains separately gated by [#6](https://github.com/opensiro/upstream/issues/6).

## Product-native issue

Wanman coordinates agent tasks with a shared task pool. In the assessed S2=C mechanism, task scope conflicts should prevent two jobs from writing the same paths. Current first-party [`Supervisor.handleRpcAsync(TASK_CREATE)`](https://github.com/chekusu/wanman/blob/d3a8138de6c21981a4f1449a7b3f201e724c55c9/packages/runtime/src/supervisor.ts) awaited `TaskPool.checkConflict()` and then awaited `TaskPool.create()` separately. Both functions read/write the same SQLite-backed tasks, but the two operations were not one admission transaction. Two concurrent overlapping RPCs could both observe no active task and be admitted.

**Assessment origin:** [Index source](https://github.com/opensiro/vsm-harness-index/blob/46219bf103b0b122d86abc3ca70ae3d8bc820e2c/assessments/wa/wanman.md), with [prospective pre-code hypothesis](https://github.com/opensiro/upstream/blob/97273405215b8652073ddba5cfd222233c321328/data/assessment-candidate-batches/2026-11-09-18-HYPOTHESES.md) committed *before* current source/issue inspection. The exact first-party source pinned for validation is `chekusu/wanman@d3a8138de6c21981a4f1449a7b3f201e724c55c9`, Apache-2.0.

## Proposed scoped change

| Artifact | Scope | SHA256 |
| --- | --- | --- |
| [`native-regression.patch`](native-regression.patch) | Adds two tests to existing `packages/runtime/src/__tests__/supervisor.test.ts` for competing overlapping/disjoint `TASK_CREATE` calls | `0fe4f64675c1bfd1c91720e80767ba7a9bf1b06727b8b3b625ab8a6a4da99f07` |
| [`native-fix.patch`](native-fix.patch) | Uses one SQLite `IMMEDIATE` transaction to check conflicting active scopes and insert the admitted task; makes Supervisor use that atomic API | `4b61fca8bf5d7cd9f0db12d0b47dc00295468ad6362cbfcc1294bca2a3bd73b4` |

The general task insertion API remains available to existing other callers. No agent scheduler, model invocation, shared task schema, authorization policy or external repository is changed by this internal packet.

## Independent first-party regression

The distinct Zhdanov runner executed genuine native Vitest against an exact source checkout in pinned Node 22 Docker. See the [full independent runner receipt](INDEPENDENT_HOST_RECEIPT_2026-11-09.md) for session IDs, commands, hashes, container digest and the preserved log excerpts.

| Test | Original source + identical regression | Original source + production fix + identical regression |
| --- | --- | --- |
| Concurrent overlapping scopes | **FAIL:** both admitted, expected one | **PASS:** one accepted, one rejected |
| Concurrent disjoint scopes | PASS: both admitted | PASS: both admitted |
| Existing + new supervisor/task pool tests | Not run on baseline as an entire suite | **68/68 PASS** |
| Runtime typecheck | Not run on baseline | PASS (`tsc --noEmit`) |

The native benefit is **bounded admission correctness**. It is not a VSM C→A grade change, autonomous system test, external adoption or deployed-user outcome.

## Maintainer handoff and publication boundary

1. Recheck source HEAD, project contribution policy, open overlapping PRs and current tests against the pinned baseline before an actual external contribution; never silently rebase the archived evidence.
2. On a permitted worktree/fork, apply `native-regression.patch` then `native-fix.patch` in this order. Run the project's existing `@wanman/runtime` Vitest suite and typecheck with its locked pnpm dependencies; assess whether the project prefers a different scope-admission API surface.
3. Request the separately effective external fork/branch/PR-stage grant, if still needed, before attempting external publication. **No external action has been executed by this batch.**

There is no S3* approval requirement inside this technical loop and no inference of external acceptance from the independent host receipt.
