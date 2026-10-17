# Shep — two distinct interventions

- **Upstream:** [shep-ai/shep](https://github.com/shep-ai/shep)
- **Contributor fork:** [xLagerFeuer/shep](https://github.com/xLagerFeuer/shep)
- **Current upstream PRs:** [#933](https://github.com/shep-ai/shep/pull/933), [#934](https://github.com/shep-ai/shep/pull/934), both **open** at the 2026-10-17 check.
- These are **two product interventions**, not two rebases of one patch: coordination is an opt-in feature; ESM worker startup is an independent existing bug.

## #933: Agent coordination

**Fit (experimental ledger 2026-10-12): pending.** Shep already provides isolated feature workcells, dependency/blocking controls and rebase/resume. The gap is deciding whether overlapping committed Git paths require a dependency, without a human deciding every time. The patch makes a bounded `defer/continue` choice and reuses `ReparentFeatureUseCase`, refreshed Git evidence, existing stop/block gates, feature flags and a visible persisted decision trail.

The [upstream reviewer ran the real built CLI](https://github.com/shep-ai/shep/pull/933#pullrequestreview-5488007885), confirmed the bounded flow, and requested security, settings, and user-visible state changes; those fixes were carried into the PR but final acceptance is not established. On the pinned PR head `00c9b4f`, [CI/CD succeeded](https://github.com/shep-ai/shep/actions/runs/38271174322), while [PR Check failed](https://github.com/shep-ai/shep/actions/runs/38271430473) on a commit-footer line over 100 characters. The `CHANGES_REQUESTED` review still requires disposition.

**Gate result:** upstream need pass; native mechanism pass; counterfactual value pass; scope compatibility **unknown** pending final upstream scope/merge decision.

## #934: ESM worker startup

**Fit (experimental ledger 2026-10-12): pass, not merged.** The built ESM feature-worker crashed when startup code referenced CommonJS-only `__dirname`, a bug [reproduced by the upstream reviewer](https://github.com/shep-ai/shep/pull/933#pullrequestreview-5488007885). The standalone hotfix derives the location from `import.meta.url` and adds a regression guard without depending on #933's coordination feature. The [upstream source fix](https://github.com/shep-ai/shep/commit/c9eb38374788298d0363d862cb72f75ea07e46a4) is credited to its original upstream contributors.

On head `6fd504a`, [CI/CD succeeded](https://github.com/shep-ai/shep/actions/runs/38271032693) while [PR Check failed](https://github.com/shep-ai/shep/actions/runs/38271032718) for a commit-body line over 100 characters. Neither a passing code suite nor a `pass` fit review is an upstream merge.

**Gate result:** upstream need pass; native mechanism pass; counterfactual value pass; scope compatibility pass.

See [Organization-owned fit observations](https://github.com/opensiro/vsm-oss-organization/blob/main/experiments/upstream-intervention-fit/observations.json). Do not confuse upstream reviewers' fix commits, authorship or tests on different refs with tests performed on the contributor's own head.
