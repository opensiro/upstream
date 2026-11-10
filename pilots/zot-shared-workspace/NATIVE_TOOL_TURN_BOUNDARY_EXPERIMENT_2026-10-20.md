# Zot — native writer and prompt-turn boundary falsification

**Status:** SOURCE-ONLY / PRELIMINARY; do not assert the expected negative test results until the linked CI passes. **Owning work:** [OpenSiro Upstream #56](https://github.com/opensiro/upstream/issues/56). **Experiment class:** independently selected Index S2 boundary, not a Zot product bug, implemented upstream PR or Index reassessment.

## Pinned source and origin

- [OpenSiro Index `5393b698bfdfa4ca14d97a79238234eca20694e5`](https://github.com/opensiro/vsm-harness-index/commit/5393b698bfdfa4ca14d97a79238234eca20694e5) → included [Zot assessment](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/zo/zot.md) → observed shared writable workspace among concurrently acting S1s without first-party collision attenuation.
- Independently verified currently pinned [Zot source `c62d1c549d52cd33390968ffa50667cb79609152`](https://github.com/patriceckhart/zot/commit/c62d1c549d52cd33390968ffa50667cb79609152), which explicitly advertises **shared cwd and optional multi-agent swarm**. This is a design constraint, not proof that Zot maintainers want serialization or isolation.
- Previous [baseline receipt](BASELINE_RECEIPT_2026-10-20.md): in a deterministic two-worker stale-write schedule, both source-backed workers report Done, and 1/2 intended updates survive.
- Previous [opt-in scoped admission proof](SCOPED_AFTER_RECEIPT_2026-10-20.md): known declared-file overlap is rejected, and after a caller retry 2/2 updates survive in a synthetic run. The wrapper is *not* installed in Zot CLI or tools.

## New independent question

Are **turn-scoped** ownership and **real Zot tool writes** actually covered by the earlier wrapper? The answer must be established from native Zot source and executed tests, not assumed from the earlier scoped-admission green CI.

### Native code ownership points

| Native point | Observed implementation | Implication |
| --- | --- | --- |
| `packages/agent/swarm/runner.go` | `notifyPromptTurnEnd` routes a `turn_end` with numeric `step` to `Agent.OnTurnEnd` without stopping the runner | A long-lived agent may complete a task while its process and process-duration claims continue |
| `packages/agent/tools/write.go` | `WriteTool.Execute` calls `os.WriteFile` after the ordinary sandbox path check | Does not check the experimental scoped-admission registry |
| `packages/agent/tools/edit.go` | `EditTool.Execute` plans from current contents, then calls `os.WriteFile` | Scope admission cannot enforce stale edit safety or block unclaimed writes |
| `packages/agent/tools/bash.go` | `BashTool.Execute` launches shell commands | Merely wrapping write/edit is not a general write-control boundary; arbitrary shell mutation remains unless separately addressed |
| `packages/agent/tools/swarm_spawn.go` | First-party auto-swarm spawns through `Swarm.SpawnReq` | Prior opt-in `ScopedSpawner` is not on the default automatic spawn path |
| `packages/agent/swarm/swarm.go` | Worker lifecycle `OnLifecycle` stop callback occurs only when `runner.Run` returns | Releasing scope only at process termination can over-retain claims beyond a logical task turn |

### Exact two controlled negative tests

- [`experimental_turn_boundary_gap_test.go`](experimental_turn_boundary_gap_test.go) is injected into **real Zot `packages/agent/swarm`**. A synthetic long-lived worker declares `shared.txt`; native `notifyPromptTurnEnd` dispatches its documented prompt-level completion and the callback fires. The worker remains alive. The earlier wrapper must still reject a new declared task on that file until the runner exits. This distinguishes **a completed task** from **an ended worker process**, without using any model.
- [`experimental_native_tools_bypass_test.go`](experimental_native_tools_bypass_test.go) is injected into **real Zot `packages/agent/tools`**. With one declared scope live and a second scoped declaration explicitly rejected, a second actual `Swarm` executes **real Zot `WriteTool.Execute` and `EditTool.Execute`** against the same shared temporary file. The test expects the direct native tools to modify the file anyway. The second Swarm is *outside* the optional wrapper, as is possible without wiring enforcement into the default runtime; this is a **test of coverage**, not a real malicious-agent bypass exploit.

The attached [credential-free CI workflow](../../.github/workflows/zot-native-tool-turn-boundaries.yml) checks out the same immutable Zot source, injects the research fixtures into disposable checkout packages, runs `go test -race` with the exact tests and the normal complete native `swarm` and `tools` package suites. The code under test is genuine Zot source; the worker behavior is deterministic and model-free.

### Interpretation boundary

Even if these tests pass, they document **failed coverage** of a source-only prototype, not a Zot vulnerability, incidence rate, real agent improvement, or an accepted native design. Do not claim the existing scoped-admission prototype is tool-enforced or task-turn-scoped. The successful prior 2/2 retry remains a valid *conditional* synthetic result, not a product success.

## Production-fit decision (hold)

A prospective legitimate upstream-native path would require (1) meaningful per-task/turn claim creation/release while an agent session stays alive; (2) authority to intercept all effective writes or detect external mutations; (3) closure that returns conflict feedback to affected continuing S1s; (4) cross-platform path/alias and crash safety; (5) keeping the intentionally lightweight shared-working-directory default and preserving normal disjoint concurrency. A write gate at `WriteTool`/`EditTool` alone is insufficient while `bash` can also mutate files, and an opt-in manager introduces UX surface that Zot may not want.

**Current acceptance status:** Need: `PENDING`; mechanic coverage: `NOT COMPLETE`; counterfactual product benefit: `PENDING`; compatibility/maintainer design: `PENDING`. Separate [unpublished design discussion draft](MAINTAINER_DESIGN_DRAFT.md) must not be mistaken for an issue raised to Zot. No external GitHub write or S2/S3 promotion is authorized.
