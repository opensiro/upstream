# AgentBox S2 — bounded Phase 4 manager advisory prototype

**Research-only OpenSiro implementation (2026-10-22)**, [Upstream #61](https://github.com/opensiro/upstream/issues/61) under [experiment #56](https://github.com/opensiro/upstream/issues/56). Origin hypothesis: `ASSESSMENT_DERIVED`; **native user benefit and first-party acceptance remain unproven**. This does **not** change `madarco/agentbox` or enable its autonomous manager.

**Frozen public source:** [AgentBox `main@605ee75d`](https://github.com/madarco/agentbox/commit/605ee75d63319003c188bc532d4e5b2ba36a51d6); canonical [Index AgentBox assessment](https://github.com/opensiro/vsm-harness-index/blob/main/assessments/ag/agentbox.md) notes that inter-box file conflict avoidance is manual. Existing native baselines: [CLI source #64](https://github.com/opensiro/upstream/pull/64) and [task-store #65](https://github.com/opensiro/upstream/pull/65); do not rebrand these as actual file-write collisions.

## One bounded proposed mechanism

[`module.ts`](module.ts) is a **new pure advisory function**, importable in the native AgentBox CLI (not wired into the dispatch path), using the existing `HubApiTask` shape. It consumes explicit per-task intended file or directory scopes, does **not** extract them from task titles, and produces: overlapping task groups, separate groups for unrelated files, `review` for unknown/malformed intent or already-running tasks, and `deferred` for unfinished dependencies. No task mutation, provisioning, host access, GitHub API write, memory expansion, lock or permission changes. No new task-store contract.

Safety bounds: lexical paths **are not verified realpath scope**; aliases, symlinks, case-folding, stale read snapshots, unlisted in-progress tasks, and global workspace controls are unhandled. Reject traversal, absolute/drive paths, undocumented wildcard patterns, unknown or duplicate task identifiers. `groups` are **recommendations, never automatically authorized launches**. All plans require revalidation and user/maintainer design decisions before use. Not an OS isolation mechanism.

[`module.test.ts`](module.test.ts) contains independently falsifiable native Vitest scenarios: same-file and nested tree interference, disjoint parallel docs, distinct-project boundaries, unknown and invalid scope fail-closed, unfinished dependencies, already allocated tasks, and pure no-mutation behavior. [Actions workflow](../../../.github/workflows/agentbox-s2-manager-advisory.yml) performs an **immutable upstream checkout**, injects exactly two untracked files into a disposable CI runner, performs original `pnpm build`, runs native Vitest, TypeScript type checking and ESLint. No Docker, real model API, worker operations, true before/after file conflict or external repo write.

## Acceptance, measurement and exit criteria

- Earlier **BEFORE**: real AgentBox CLI preflight recognizes valid task IDs, does not inspect overlapping file intents (stubbed Hub API, no boxes).
- Proposed **AFTER for planner module only**: a pair of payment tasks grouped, disjoint docs task separated, ambiguous scopes held for human review, dependent tasks deferred; measure real native test results before claiming even this function works.
- **Not measured**: actual agents/boxes prevented from damaging user files, reduced developer time, true S2 return loop, running manager integration, maintainer acceptance, review quality, grade uplift, or shipped software.

This prototype is deliberately **smaller than AgentBox Phase 4**. If maintainers prefer instruction-only grouping or wholly manual dispatch, this code can be dropped; the baseline stays valid. First-party [CONTRIBUTING](https://github.com/madarco/agentbox/blob/main/CONTRIBUTING.md) asks for an issue before a feature larger than a bugfix. An [external inquiry draft](../AGENTBOX_DESIGN_INQUIRY_DRAFT.md) exists but is not published. No fork, external PR, source mutation, autonomous S1 action or VSM reassessment is authorized by this work.
