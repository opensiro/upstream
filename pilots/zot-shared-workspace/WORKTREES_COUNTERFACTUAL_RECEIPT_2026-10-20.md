# Zot native WriteTool: manual Git worktrees vs shared RepoRoot — executed receipt

**Date:** 2026-10-20.
**Experiment owner:** [Upstream #56](https://github.com/opensiro/upstream/issues/56).
**Reviewable internal change:** [Upstream PR #62](https://github.com/opensiro/upstream/pull/62).
**External Zot state:** UNMODIFIED — no Zot fork, external branch, issue, PR or maintainer response.
**Index origin:** [Zot S2 interference finding at immutable Index 5393b698](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/zo/zot.md).
**Zot source:** [patriceckhart/zot@c62d1c549d52cd33390968ffa50667cb79609152](https://github.com/patriceckhart/zot/commit/c62d1c549d52cd33390968ffa50667cb79609152).

## Verified execution

- GitHub Actions [run #39482685537](https://github.com/opensiro/upstream/actions/runs/39482685537), [native-worktrees job #118835016453](https://github.com/opensiro/upstream/actions/runs/39482685537/job/118835016453): **SUCCESS**.
- The exact Zot SHA was checked before injecting exactly one experimental test file into a disposable checkout; GitHub credentials were not persisted and permissions were contents:read.
- Go 1.25.0. Actual command: go test -race ./packages/agent/tools -run '^TestAssessmentNativeWriteManualWorktreeCounterfactual$' -count=1 -v -timeout=4m — **PASS**.
- Full affected package tests: go test ./packages/agent/swarm ./packages/agent/tools -count=1 -timeout=3m — **PASS**.
- Fixture: [experimental_manual_worktrees_counterfactual_test.go](experimental_manual_worktrees_counterfactual_test.go); [frozen protocol](WORKTREES_COUNTERFACTUAL_PROTOCOL_2026-10-20.md).

Exact selected log:
~~~text
=== RUN   TestAssessmentNativeWriteManualWorktreeCounterfactual
control: native_tools_success=2, updates_preserved_in_common_file=1, lost_updates=1, native_conflict_feedback=none
manual worktrees: native_tools_success=2, branches_preserved=2, shared_overwrites=0, merge_conflict=1, automatic_reconciliation=false
--- PASS: TestAssessmentNativeWriteManualWorktreeCounterfactual (0.06s)
PASS
ok github.com/patriceckhart/zot/packages/agent/tools 1.071s
~~~

## Measured comparison — same Zot tool and worker design

| Observable | Same RepoRoot | Separate user-managed Git worktrees |
| --- | --- | --- |
| Native Zot WriteTool actions successful | 2 | 2 |
| Intended independent changes preserved in working artifacts | 1/2 | 2/2 |
| Silent overwrite within a common file | 1 | 0 |
| Git branches holding alternative edits | Not exercised | 2 |
| Git merge explicitly reports conflict | Not exercised | 1 |
| Automatic conflict reconciliation by Zot | None | None |

Both cases use native first-party Zot Swarm + WriteTool with synthetic runners reading before writing in a deterministic schedule. In separate worktrees, distinct roots were supplied by the test/human, **not created by Zot**. The test then explicitly committed each edit and demonstrated a Git merge conflict, which still requires human/agent intervention.

## Product interpretation and limitations

1. This directly supports a **zero-Zot-code manual containment option**: independent Git worktrees retain both conflicting edits instead of silently overwriting a single common file. The conflict moves to branch integration where it is explicit, **not solved automatically**.
2. The primary baseline danger (silent same-file overwrites) remains in Zot's intentionally shared-RepoRoot default. The previous ScopedSpawner is still invalid for task/turn-scoped or tool-enforced protection. No improvement to a distributed Zot binary has occurred.
3. User setup cost, worktree orchestration across CLI modes, cleanup, merging, resumption, real-model task performance, actual user incidence and maintainer demand were **not measured**. No productivity, safety guarantee or general S2 closure follows from this limited test.
4. The fixture does not cover native EditTool/BashTool operations, symlink aliases or cross-process malicious writes in this worktree counterfactual. Existing separate [tool/turn tests](NATIVE_TOOL_TURN_BOUNDARY_RECEIPT_2026-10-20.md) remain decisive for the voluntary wrapper's limitations.

## Go/no-go

- Assessment-to-functional-mechanism hypothesis: **SUPPORTED** at frozen source, not automatically a product request.
- Native need for a new built-in Zot feature: **PENDING / BLOCKED_EVIDENCE** — no verified maintainer request or evidence that manual worktrees are unacceptable for Zot's lightweight contract.
- Minimal native change and user-visible before/after improvement: **NOT IMPLEMENTED / NOT DEMONSTRATED**.
- Tested alternative: **MANUAL_WORKTREE_CONTAINMENT_SUPPORTED** for deterministic native WriteTool scenario.
- External contribution / maintainer feedback: **NOT STARTED**; no permission is inferred.
- Decision: **NO_GO on building a native Zot file-claims manager now**. Advance Index-first screening of another harness; keep Zot design draft unpublished pending an explicit external publication decision. Do not update Index grade or Organization S1 admission.
