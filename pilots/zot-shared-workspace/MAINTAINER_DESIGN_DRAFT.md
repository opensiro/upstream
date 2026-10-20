# Proposed Zot maintainer design discussion — not published

**Status: TEXT ONLY / HUMAN PUBLICATION REQUIRED.** This is not a GitHub issue, PR, external maintainer contact, permission to modify Zot, or claim that Zot contains an unacknowledged software bug.

**Target:** [patriceckhart/zot](https://github.com/patriceckhart/zot). Intended location: a design-feedback discussion/feature issue, *only if a human chooses to send it*. Read current [CONTRIBUTING.md](https://github.com/patriceckhart/zot/blob/main/CONTRIBUTING.md) and check duplicate issues before publication.

## Suggested title

Would an opt-in write-conflict diagnostic for shared-workspace swarm agents fit Zot?

## Suggested message

Zot's README and `packages/agent/swarm/swarm.go` explicitly document that parallel `/swarm` workers run inside the host's `RepoRoot` and may write the same files. I understand that this is an intentional lightweight/shared-cwd design, not necessarily a bug.

I was investigating concurrent-worker interaction and created a small source-only baseline against `c62d1c5`. Two injected `Swarm` runners read the same original file, then independently write incompatible changes in a fixed order. Both finish `done`, while the second overwrites the first update. It doesn't use models or private data; the test just establishes one possible shared-workspace interference schedule:

- Expected writes: 2
- Preserved writes: 1
- Native conflict notification in the test case: none observed

[Reproduction and precise limits](https://github.com/opensiro/upstream/blob/research/assessment-derived-zot-baseline-20261020/pilots/zot-shared-workspace/BASELINE_RECEIPT_2026-10-20.md).

Would you consider **some narrowly scoped, optional diagnostic/admission path** for workflows with known overlapping writable paths? I would not want to change Zot's default shared working directory behavior, silently serialize all workers, or add a manager/long-running service. Potential user-visible alternatives might be an explicit warning when a second write-capable worker targets the same declared file scope, or an opt-in shared-write collision check with a clear refusal/return path. A Git worktree is also a valid documented manual workaround today.

Before preparing a patch, it would help to know (1) whether the limitation is one maintainers would like Zot itself to address, (2) which existing API/extension seam would be preferred for an optional safeguard, and (3) which compatibility and behavior constraints a regression test should preserve.

I haven't created a Zot fork branch or upstream implementation PR for this proposal.

## Scope constraints and after-case if supported

The baseline is **synthetic**. Do not imply widespread user harm or a VSM-grade issue. If product-native demand and design fit are confirmed:

1. Preserve the default `shared RepoRoot` behavior and existing CLI flags when the feature is off.
2. Implement the narrowest optional path the maintainer considers acceptable; avoid a new scheduler or generalized isolation subsystem unless necessary.
3. Use the same deterministic two-writer schedule as baseline. The behavior criterion is either two safely preserved updates or an explicit, attributable conflict rejection **without falsely reporting two clean successes**.
4. Separately test non-overlapping workers still run concurrently, scope constraints, cancellation and restart/recovery.
5. Run Zot's native Go tests including the race detector, record actual before/after and failure cases, and only then consider a permissioned contribution branch.

This document is **not** a request for permission to publish the discussion automatically. The underlying Index-first research record is [Upstream #56](https://github.com/opensiro/upstream/issues/56).
