# Zot manual Git worktrees — counterfactual protocol

**Owner:** OpenSiro Upstream [#56](https://github.com/opensiro/upstream/issues/56).
**Date:** 2026-10-20.
**Status:** RESEARCH-ONLY / PRE-CI HYPOTHESIS (not a run receipt).
**Canonical origin:** [Index Zot assessment at 5393b698](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/zo/zot.md).
**Current tested source:** [Zot c62d1c549d52cd33390968ffa50667cb79609152](https://github.com/patriceckhart/zot/commit/c62d1c549d52cd33390968ffa50667cb79609152).
**Fixture:** [native WriteTool + Swarm test](experimental_manual_worktrees_counterfactual_test.go).
**Runner:** [credential-free source-pinned Actions](../../.github/workflows/zot-manual-worktrees-counterfactual.yml), Go 1.25.0.

## Research question

Zot intentionally runs child Swarms in one writable RepoRoot. The Index assessment identifies plausible cross-worker edit interference. The [baseline](BASELINE_RECEIPT_2026-10-20.md) reproduced a lost update with synthetic workers. The [native tool/turn boundary tests](NATIVE_TOOL_TURN_BOUNDARY_RECEIPT_2026-10-20.md) falsified the optional declaration wrapper as a native protection mechanism.

Before introducing claims, agents, locks or tool enforcement, test whether **ordinary user-managed Git worktrees** already offer sufficient source containment in this same scenario. This is an alternative, **not a new feature**, and does not improve Zot itself.

## Matched workload, specified before CI

- One file starts as original + newline. Two synthetic workers run actual Zot Swarm and WriteTool.Execute, with genuine NewSandbox; no models, credentials or external repository writes.
- Both workers read an original preimage, then write incompatible changes in deterministic order, A followed by B.
- Control: two independent Swarms share RepoRoot. Expected: both workers done, 1 of 2 intended updates preserved in the common working file, no native collision feedback.
- Counterfactual: the same Swarms and tools operate in two Git worktrees created and owned **manually** by the test, each with a distinct RepoRoot. Expected: 2 of 2 branch/file artifacts preserved, no common workspace overwrite.
- Attempt to merge independently committed branches into the original repo. Expect a visible Git conflict for overlapping edits; branch preservation is **not** automatic successful reconciliation.
- Measure native tool statuses, preserved updates, number of branches, base-worktree mutation and merge-conflict state.
- The adversarial scheduling is intentionally deterministic, not evidence of real-user incidence or improvements in agent model quality.

| Measure | Shared-root control (expected) | Manual worktrees (expected) |
| --- | --- | --- |
| Native WriteTool successful calls | 2 | 2 |
| Independently preserved edits | 1/2 | 2/2 |
| Native Zot conflict feedback | None | None |
| Git merge conflict | Not attempted | Explicit, requiring resolution |
| Automatic coordination or new Zot capability | None | None |
| User-managed setup burden | None | Nonzero |

**These are hypotheses, not completed results.** CI must run the actual code injected into the immutable Zot checkout, including the race detector and the full affected native package suites. Unexpected results must be recorded, not hidden.

## Independent product-native fit review

- Zot [swarm.go](https://github.com/patriceckhart/zot/blob/c62d1c549d52cd33390968ffa50667cb79609152/packages/agent/swarm/swarm.go) explicitly advertises no worktrees or per-agent isolation and suggests using normal Git tooling for separate branches.
- Zot [CONTRIBUTING.md](https://github.com/patriceckhart/zot/blob/c62d1c549d52cd33390968ffa50667cb79609152/CONTRIBUTING.md) values a lightweight single binary and requests design feedback for multi-package or public API changes.
- On 2026-10-20, bounded searches of Zot issues and PRs for worktree, same file, overwrite, swarm, and conflict found several swarm issues but no verified request for automatic per-file arbitration. Search absence does not prove no user need.
- The earlier scoped wrapper can be bypassed by other native tool instances; bash and external processes are not covered. Native tool enforcement would carry substantially greater implementation and compatibility cost.

| Native-fit gate | Current verdict | Reason |
| --- | --- | --- |
| Assessment origin | SUPPORTED hypothesis | S2 conflict mechanism explicitly observed in included Index assessment |
| New built-in feature need | PENDING | Synthetic collision alone does not establish product demand |
| Shared-root write behavior | OBSERVED | Controlled native source tests, no Zot patch |
| Counterfactual alternate solution | PENDING TEST | Git worktrees may preserve branches while shifting merge burden to user |
| Zot-native new-feature scope | BLOCKED_EVIDENCE | Deliberately shared cwd; independent design feedback not yet obtained |

## Go/no-go

If worktrees preserve both branch artifacts and conflict at merge, record **no-code containment** with a clearly unresolved integration burden. Do not describe that as a Zot improvement, automated S2 conflict resolution, a successful user task, or a changed Index grade.

Without verified native demand or maintainer feedback, do **not** build a native scope manager, change Zot, create a fork, or publish external issues/PRs. Continue an independent Index-first screening for a stronger product-fit candidate. If this hypothesis fails, retain the negative evidence and inspect the failing mechanism.
