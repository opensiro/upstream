# Zot scoped-admission prototype — executed after-case receipt (2026-10-20)

**Status:** SOURCE-ONLY EXPERIMENT CONFIRMED / NOT A SHIPPED PRODUCT IMPROVEMENT.
**Owning issue:** [Upstream #56](https://github.com/opensiro/upstream/issues/56).
**Experimental PR:** [Upstream #59](https://github.com/opensiro/upstream/pull/59).
**Canonical assessment provenance:** [Index `main@5393b698bfdfa4ca14d97a79238234eca20694e5`](https://github.com/opensiro/vsm-harness-index/commit/5393b698bfdfa4ca14d97a79238234eca20694e5), `assessments/zo/zot.md`, reviewed source `2a19df15ba8278dd6a92240ab6c2ae267c3cf6c3`.
**Exact experiment source:** Zot `main@c62d1c549d52cd33390968ffa50667cb79609152` (identical for baseline and after). Real Zot `packages/agent/swarm` package with injected source/test files only in disposable CI worktree.

## Actual executions (GitHub-hosted runner, Go 1.25.0, no fork/upstream writes)

[Exact-head workflow #39476648135](https://github.com/opensiro/upstream/actions/runs/39476648135/job/118814214146): **SUCCESS**. `go test -race ./packages/agent/swarm -run '^TestAssessment(SharedWorkspaceLostUpdateBaseline|Scoped.*)$' -count=1 -v -timeout=3m` passed; native package `go test ./packages/agent/swarm -count=1 -timeout=3m` passed. Separate original [baseline workflow](https://github.com/opensiro/upstream/actions/runs/39476648257) and [OpenSiro Python workflow](https://github.com/opensiro/upstream/actions/runs/39476648307) both **SUCCESS**.

**Verbatim observed metrics from the same-run Go logs:**

```text
TestAssessmentSharedWorkspaceLostUpdateBaseline:
  workers_reported_done=2, worker_updates_intended=2,
  final_updates_preserved=1, lost_updates=1,
  native_conflict_feedback=not_observed
  PASS
TestAssessmentScopedConflictThenExplicitRetry:
  intended_updates=2, preserved_updates=2, lost_updates=0,
  explicit_scope_rejections=1, external_tool_writes_monitored=false
  PASS
TestAssessmentScopedDisjointStillConcurrent:
  disjoint_declared_scopes_start_concurrently=true
  PASS
TestAssessmentScopedClaimsReleasedAfterCancel: PASS
TestAssessmentScopedRejectsInvalidOrUnboundedDeclarations: PASS
```

| Observable | Baseline genuine Zot Swarm (before) | Experimental opt-in declared-file wrapper (after) |
| --- | --- | --- |
| Same source preimage read concurrently by two synthetic workers | Both start and write from stale copy | First starts, second attempt is **refused before worker creation** |
| Intended A/B edits preserved after explicit caller retry | 1/2; silent A overwrite | 2/2; after B explicitly retries once A finishes and reads new source |
| Conflict signal | None in baseline, both report `done` | One `ErrDeclaredWriteConflict` surfaced to the caller |
| Declared disjoint A/B work | Baseline has no claims | Both run concurrently; proven with barrier |
| Release when first worker stopped | Not applicable | Claim released at actual native terminal lifecycle callback; tested |
| Race detection | In-scope matched source tests | Go race detector PASS for both measured cases |

### Interpretation / essential caveats

The experiment **supports a bounded mechanism hypothesis**: if the caller already knows and accurately declares exact files to be modified, an in-process opt-in claim gate can avoid this specific simultaneous stale-write schedule *without blocking independent declared files*. Rejection changes the workload: **B does not complete concurrently**; it must retry and possibly replan. We are not comparing identical throughput or cost. Real LLM agents and real Zot edit tools were not used; only first-party Zot spawn/status lifecycle with deterministic synthetic runners. This is a proof of mechanism, not evidence of a successful real product improvement.

Important uncovered integration gaps:
- Native Zot `execRunner` runs a **long-lived session accepting further user turns**. This simple wrapper releases claims at process terminal callback, **not individual task-turn end**. In production a claim could persist for the entire background-agent lifetime, blocking later unrelated claims of the same path. Production integration would need first-party turn-scoped ownership and authoritative writer control.
- Zot workers can edit paths outside their declarations; the wrapper neither monitors tool calls nor enforces a sandbox/write transaction.
- Exact string paths are not complete aliases; symlinks, case sensitivity, directories, out-of-process workers, crash/restart, and shared process state are not safely resolved. Its sanitization is not a security boundary.
- No current Zot maintainer agreement/user demand establishes that this alternative fits the intentionally documented **shared working directory** behavior. The Zot `CONTRIBUTING.md` prefers design discussion before multi-package/public-API changes.

### Four native-fit gates / decision

- **Mechanism:** `PASS_SOURCE_ONLY` for synthetic exact-file admission plus explicit feedback in native Zot `Swarm`.
- **Need:** `PENDING`, neither a reported user incident nor maintainer request for such opt-in protection established.
- **Counterfactual product value:** `PENDING`, the gain is constrained and requires verified scope declarations and manual retry.
- **Compatibility / scope:** `PENDING`, long-lived sessions and file-write enforcement are material blockers to promoting this wrapper to production.

**Outcome:** `PROOF_OF_MECHANISM_SUPPORTED / DEPLOYED_PRODUCT_BENEFIT_INCONCLUSIVE`, source-only, `BLOCKED_EVIDENCE` for promotion into upstream implementation. **No** claimed S2 autonomy grade change, external fork code change, Zot issue/comment, Zot PR, or human publication action. Refrain from writing a production patch until design feedback establishes a compatible and desired enforcement scope.

Human-readable [unpublished design discussion](MAINTAINER_DESIGN_DRAFT.md) remains available for an operator who decides to contact Zot maintainers. The primary method contract is [ASSESSMENT_TO_IMPROVEMENT.md](../../docs/ASSESSMENT_TO_IMPROVEMENT.md).
