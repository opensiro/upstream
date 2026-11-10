# VTCode — native worktree reconciliation identity mismatch: source finding, test not yet executable

**Batch:** [2026-10-22-02](../../data/assessment-candidate-batches/2026-10-22-02.json), row 1/5.
**Stage:** BLOCKED_EVIDENCE. This is a source-derived hypothesis, **not** a validated product fix, source patch or external PR.

## Exact provenance and source finding

- Canonical [Index assessment](https://github.com/opensiro/vsm-harness-index/blob/396a54bb690f8ec7ce966bf9b00b241b30036307/assessments/vt/vtcode.md) reviewed vinhnx/VTCode at dc32271158bec3c37b81ad7bf57157a801307517 and explicitly records a likely worktree identity mismatch. This candidate was selected **from the assessment before searching upstream bugs**.
- Current main check: f654ee6f0e5d427507c10146043b9bc73e5f217c. The same path still appears in source as of 2026-10-22:
  1. [controller_spawn_run.rs](https://github.com/vinhnx/VTCode/blob/f654ee6f0e5d427507c10146043b9bc73e5f217c/crates/codegen/vtcode-core/src/subagents/controller_spawn_run.rs) creates worktree name by sanitized spec name plus launch UUID.
  2. [controller_child_loop.rs](https://github.com/vinhnx/VTCode/blob/f654ee6f0e5d427507c10146043b9bc73e5f217c/crates/codegen/vtcode-core/src/subagents/controller_child_loop.rs) passes only record.spec.name as the reconciliation worktree name, despite carrying the exact worktree_path.
  3. [reconciler.rs](https://github.com/vinhnx/VTCode/blob/f654ee6f0e5d427507c10146043b9bc73e5f217c/crates/codegen/vtcode-core/src/git/reconciler.rs) constructs branch loop/{worktree_name}, then checks for commits/diff/merge on that name and eventually removes the named worktree.
- Example inference: a generated branch loop/worker-{UUID} would be looked up as loop/worker. This is a **source-backed mismatch inference**, not a measured invocation result. No exact matching open issue/PR was found in a bounded GitHub search; check overlap again before publication.

## Fit status / missing independent evidence

- **need PENDING:** plausible native failure but no independently executed first-party worktree/reconcile regression.
- **mechanism PASS:** current source carries both name creation and name-derived git lookup paths.
- **counterfactual PENDING:** a fix reusing the worktree path basename is a candidate, but a real baseline/after test has not established that it merges correctly.
- **scope PASS:** narrow native worktree completion and one deterministic Rust test; no model or browser required.
- **origin INSUFFICIENT** pending native verification; it may become ASSESSMENT_DERIVED only if an actual source-first RED/GREEN contribution succeeds.

The current workspace has **neither cargo nor rustc**, so an execution of genuine first-party Rust code cannot be honestly reported here. No live LLM agents, external provider calls or synthesized stand-in implementation were used to replace it. Required next evidence: run first-party Rust reconciliation against a local disposable git repository with exact generated worktree name, assert mismatched-before and corrected-after native results, with cleanup/negative controls; then revisit source overlap and fit. Under the batch continuation rule, this unverified case is passed over to Zaino without discarding its source-derived hypothesis.
