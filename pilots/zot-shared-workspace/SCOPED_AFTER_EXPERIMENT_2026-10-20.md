# Zot — source-only optional declared-file admission prototype

**Status: EXPERIMENTAL / NOT IN ZOT / NOT A PRODUCT FIX.** Owning [Upstream #56](https://github.com/opensiro/upstream/issues/56). Source selected by canonical [Index `5393b698...`](https://github.com/opensiro/vsm-harness-index/commit/5393b698bfdfa4ca14d97a79238234eca20694e5), assessment `assessments/zo/zot.md`, reviewed `2a19df15...`. Fresh independently inspected Zot [`main@c62d1c549d52cd33390968ffa50667cb79609152`](https://github.com/patriceckhart/zot/commit/c62d1c549d52cd33390968ffa50667cb79609152).

## Experiment question

Does an **explicit opt-in, exact-file write-scope admission contract** on the first-party Zot `Swarm.SpawnReq` lifecycle avoid the previously measured silent-lost-edit scenario **without serializing two disjoint workers**?

This is one small **operational conflict/feedback mechanism**, not a general S2=A transformation, whole-team S3 manager or right to modify upstream. It's motivated by the **specific S2 boundary** in the assessment: multiple genuine concurrent S1 workers share one writable `RepoRoot` and have no conflict-specific return into work allocation.

## Source-only additive mechanism

Two Go files are injected **only in a disposable GitHub Actions checkout** of the same pinned upstream source:

- [`experimental_scoped_spawn.go`](experimental_scoped_spawn.go): a wrapper `ScopedSpawner` with `SpawnDeclared(ctx, req, []exactRelativeFilePaths)`. It atomically rejects a second declaration of the same file while the first native `Swarm` worker is alive. It holds claims until the **actual native terminal lifecycle callback** (including `Stop`/cancellation); no global lock while different worker tasks are running.
- [`experimental_scoped_spawn_test.go`](experimental_scoped_spawn_test.go): after-case with the **same initial file** and independent synthetic Zot runners as [the baseline](assessment_shared_workspace_baseline_test.go), one conflict rejected explicitly and subsequently retried after the first completes, plus simultaneous disjoint-file worker test, cancellation-release and invalid-scope negative cases.
- [`zot-scoped-admission-after.yml`](../../.github/workflows/zot-scoped-admission-after.yml): same public Zot SHA, Go 1.25.0, genuine Zot package, identical original baseline fixture; invokes `go test -race` with the before/after tests and a full `go test ./packages/agent/swarm`. `contents: read` only, no persisted credential and **no external fork/upstream writes**.

This patch is deliberately **not installed into the Zot CLI/TUI**, not selected by any existing user option, not imposed on other ways to spawn agents, and not a guarantee that tools obey declarations. It is a proof-of-mechanism behind an explicit wrapper, not a deliverable user-facing Zot safeguard.

## Matched observations and limits

| Metric | Baseline before (measured) | Scoped prototype after |
| --- | --- | --- |
| Concurrent workers claiming same `shared.txt` | Both start and read original | Second caller gets explicit overlap refusal *before worker starts* |
| After user-visible explicit retry once first worker finishes | Not present in baseline; second writer overwrites from stale snapshot | Expected both updates preserved because second worker starts from fresh source |
| Feedback | Both original workers `done`, no conflict return | Expected `ErrDeclaredWriteConflict` and no false second acceptance |
| Declared non-overlapping worker scopes | Unrestricted concurrency | Must continue concurrently, independently checked |
| Cancellation/restart | No scope claims in upstream baseline | Must release only when worker's native terminal callback runs |
| Safety and limits | Unsynchronized writes can lose edits | **No sandbox:** agents can modify undeclared paths; symlinks/aliases not safely resolved; scoped wrapper applies only to callers choosing it; process-local coordination only. |

**No post-change values are claimed until actual CI output is inspected.** A test that rejects one worker is not equivalent to both workers completing uninterrupted. Throughput/fairness and real model-driven agent interaction have **not** been measured. The possible native product value requires feedback that an opt-in workflow fits the lightweight shared-root design.

### Admission gates still pending

- **Need:** no independently verified affected user/maintainer request to alter shared-folder swarm behavior.
- **Mechanism:** source-only scoped admission, if tests pass, would establish only **declared-path** collision avoidance, not general safety for arbitrary coding edits.
- **Counterfactual value:** compare benefit vs manual user-managed worktrees and exposed shared-file intent.
- **Scope:** maintainer fit, UX integration, restart/persistence, Windows/macOS path semantics, aliases and symlinks, independent host processes, actual tool-enforced adherence all need review.

**Do not publish to Zot or open a contribution fork** on the strength of this source-only experiment. The [human-owned design inquiry](MAINTAINER_DESIGN_DRAFT.md) is not published. If the product does not want opt-in declared-file coordination, retain the negative finding. No Index regrade or Organization S1 admission follows from a benchmark.
