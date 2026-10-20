# Zot — observed native tool and logical-turn boundary receipt

**Date:** 2026-10-20. **Owning experiment:** [OpenSiro Upstream #56](https://github.com/opensiro/upstream/issues/56). **Code artifact:** [Upstream PR #60](https://github.com/opensiro/upstream/pull/60). **External status:** SOURCE-ONLY; not installed or published to Zot, and not a user-facing safety improvement.

## Provenance and exact run

- Canonical Index first: [`opensiro/vsm-harness-index@5393b698bfdfa4ca14d97a79238234eca20694e5`](https://github.com/opensiro/vsm-harness-index/commit/5393b698bfdfa4ca14d97a79238234eca20694e5); assessment `assessments/zo/zot.md` flags **specific concurrent shared-workspace S1 interference**. The `S2=—` label itself is not a bug report.
- Native Zot source frozen at [`patriceckhart/zot@c62d1c549d52cd33390968ffa50667cb79609152`](https://github.com/patriceckhart/zot/commit/c62d1c549d52cd33390968ffa50667cb79609152), unchanged from the earlier [baseline](BASELINE_RECEIPT_2026-10-20.md) and [scoped-admission after-case](SCOPED_AFTER_RECEIPT_2026-10-20.md).
- Actual [GitHub Actions #39479028548](https://github.com/opensiro/upstream/actions/runs/39479028548/job/118822434911) **SUCCESS**. GitHub Ubuntu runner, Go 1.25.0, immutable public Zot source, read-only checkout and no persisted GitHub credentials. Experimental files injected solely into disposable checkout. `go test -race ./packages/agent/swarm ./packages/agent/tools` (two selected tests) **PASS**, full `go test ./packages/agent/swarm ./packages/agent/tools` **PASS**. OpenSiro 420/420 offline Python tests and `git diff --check` **PASS** on initial head. An initial runner attempt failed *before test execution* because the research fixture contained a malformed escaped Go newline; it was corrected and this is the subsequent green execution.
- [Turn-boundary fixture](experimental_turn_boundary_gap_test.go), [tool-boundary fixture](experimental_native_tools_bypass_test.go), [original voluntary gate](experimental_scoped_spawn.go), and [CI](../../.github/workflows/zot-native-tool-turn-boundaries.yml).

## Exact observed native test output

```text
=== RUN TestAssessmentLongLivedPromptTurnDoesNotReleaseScope
native_turn_end_callback_observed=true,
worker_still_running=true,
claim_released_at_task_end=false,
subsequent_declared_task_rejected=true,
claim_released_at_process_end=true
--- PASS: TestAssessmentLongLivedPromptTurnDoesNotReleaseScope

=== RUN TestAssessmentNativeWriteAndEditBypassDeclaredScope
declared_competitor_rejected=true,
unscoped_native_write_success=true,
unscoped_native_edit_success=true,
content_mutated_while_claim_active=true,
product_enforcement=false
--- PASS: TestAssessmentNativeWriteAndEditBypassDeclaredScope

ok github.com/patriceckhart/zot/packages/agent/swarm
ok github.com/patriceckhart/zot/packages/agent/tools
```

## Result and interpretation

1. **Task versus process (observed):** The first-party `notifyPromptTurnEnd` does invoke the registered `Agent.OnTurnEnd` callback from a supported prompt-level `turn_end` event. The synthetic runner remains active, and the prototype's declaration persists; another declared task is blocked **after the first logical task completed**. It becomes eligible only after **process termination**. This is not necessarily safe or ergonomic for long-lived Zot agents. The test uses a fake native `Runner`; real hosted providers are not invoked.
2. **Real WriteTool and EditTool (observed):** While the declaration is held and a second *declared* start was rejected, another, independently instantiated **actual Zot `Swarm`** running **native `WriteTool.Execute` followed by `EditTool.Execute`** successfully modifies the claimed temporary file. The test's second Swarm does not opt in to the experimental wrapper; it demonstrates the exact gap between voluntary admission and **actual tool enforcement**, not a bypass of a genuine global Zot security boundary.
3. **Bash and other write paths (source inspection only):** Zot `BashTool.Execute` can invoke shell commands; it is not covered by the wrapper. No additional tool/OS-isolation claims were tested or proven.
4. **Meaning for earlier 1/2 → 2/2 result:** The earlier conditional synthetic after-case remains valid **only when both runners are routed through the voluntary `ScopedSpawner`, declare paths truthfully, and explicitly retry**. It is not evidence of real-world Zot write safety or a functioning autonomous conflict-feedback loop.

## Go/no-go for a Zot-native contribution

**Evidence-supported:** shared-workspace conflict is possible; optional exact-file admission can reject one known conflicting start; the simple implementation is **not turn-scoped and not tool-enforced**. No vendor code, user scenario or maintainer acceptance was changed.

**Required for a usable native version (not yet implemented):**

- Task/turn identity and clean claim release on actual task-turn completion **not merely process exit**, including overlap with queued new turns and cancellation/restart.
- A bounded **shared decision/enforcement point** covering WriteTool/EditTool plus shell and other effective mutation routes, or an explicitly restricted opt-in mode with clear limitations. Tool wrappers alone cannot guarantee protection against `bash`.
- Explicit detection/refusal or coordination feedback returned to the particular S1s needing to retry/replan; avoid falsely reporting a silently overwritten update as successful.
- Path aliases, symlinks, directory scopes, external writers/processes, crash windows, Windows/macOS behavior and non-overlapping throughput must be evaluated before safety claims.
- Independent native **product need and fit with Zot's intentionally shared cwd / lightweight design**, preferably maintainer design feedback, as Zot's [CONTRIBUTING](https://github.com/patriceckhart/zot/blob/c62d1c549d52cd33390968ffa50667cb79609152/CONTRIBUTING.md) requests.

**Outcome:** `PRIOR_SCOPED_ADMISSION_INTEGRATION_INSUFFICIENT`, `OBSERVED_TOOL_AND_TURN_GAPS`, `EXTERNAL_PRODUCT_BENEFIT_INCONCLUSIVE`, `BLOCKED_EVIDENCE` for native implementation. The research's purpose is to distinguish viable improvement candidates from score-driven or synthetic PR generation, not to force an S2 grade upgrade. [Unpublished maintainer design draft](MAINTAINER_DESIGN_DRAFT.md) remains human-owned; no external issue/PR created.
