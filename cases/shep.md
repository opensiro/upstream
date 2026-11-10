# Shep — two distinct interventions

- **Upstream:** [shep-ai/shep](https://github.com/shep-ai/shep)
- **Contributor fork:** [xLagerFeuer/shep](https://github.com/xLagerFeuer/shep)
- **PR lifecycle (verified 2026-10-22):** [#933](https://github.com/shep-ai/shep/pull/933) and [#934](https://github.com/shep-ai/shep/pull/934) both **merged on 2026-10-19**. The CI/review paragraphs below document their earlier 2026-10-17 pre-merge state; see the [dated machine-readable receipt](../data/upstream-lifecycle.json) for the current recorded outcome.
- These are **two product interventions**, not two rebases of one patch: coordination is an opt-in feature; ESM worker startup is an independent existing bug.

## #933: Agent coordination

**Fit (experimental ledger 2026-10-12): pending.** Shep already provides isolated feature workcells, dependency/blocking controls and rebase/resume. The gap is deciding whether overlapping committed Git paths require a dependency, without a human deciding every time. The patch makes a bounded `defer/continue` choice and reuses `ReparentFeatureUseCase`, refreshed Git evidence, existing stop/block gates, feature flags and a visible persisted decision trail.

At the **2026-10-17 pre-merge review**, the [upstream reviewer ran the real built CLI](https://github.com/shep-ai/shep/pull/933#pullrequestreview-5488007885), confirmed the bounded flow, and requested security, settings, and user-visible state changes; those fixes were carried into the PR. On previous head `00c9b4f`, [CI/CD succeeded](https://github.com/shep-ai/shep/actions/runs/38271174322) while [PR Check failed](https://github.com/shep-ai/shep/actions/runs/38271430473) on the commit footer. The message was repaired without changing the code tree or parent in head [`d49450e`](https://github.com/xLagerFeuer/shep/commit/d49450e8f3b239abd6a6571bf9b14ccdc0185cb9). New-head [PR Check](https://github.com/shep-ai/shep/actions/runs/39054133043) and [CI/CD](https://github.com/shep-ai/shep/actions/runs/39054121165) then reported **`action_required`**, pending upstream workflow approval. The `CHANGES_REQUESTED` review had not yet been resolved in this earlier case note. [Public update/request](https://github.com/shep-ai/shep/pull/933#issuecomment-6237687884). The subsequent merge is recorded above, independently from fit classification.

**Gate result:** upstream need pass; native mechanism pass; counterfactual value pass; scope compatibility **unknown** pending final upstream scope/merge decision.

## #934: ESM worker startup

**Fit (experimental ledger 2026-10-12): pass.** The built ESM feature-worker crashed when startup code referenced CommonJS-only `__dirname`, a bug [reproduced by the upstream reviewer](https://github.com/shep-ai/shep/pull/933#pullrequestreview-5488007885). The standalone hotfix derives the location from `import.meta.url` and adds a regression guard without depending on #933's coordination feature. The [upstream source fix](https://github.com/shep-ai/shep/commit/c9eb38374788298d0363d862cb72f75ea07e46a4) is credited to its original upstream contributors.

At the earlier 2026-10-17 check, on previous head `6fd504a`, [CI/CD succeeded](https://github.com/shep-ai/shep/actions/runs/38271032693) while [PR Check failed](https://github.com/shep-ai/shep/actions/runs/38271032718) on a long commit-body line. The message was repaired without changing the code tree or parent in head [`012f2d4`](https://github.com/xLagerFeuer/shep/commit/012f2d4b5594ae2f10a8bcd6b1bc0c4bbab1a1ea). New-head [PR Check](https://github.com/shep-ai/shep/actions/runs/39053910123) and [CI/CD](https://github.com/shep-ai/shep/actions/runs/39053910191) then reported **`action_required`**. [Public update/request](https://github.com/shep-ai/shep/pull/934#issuecomment-6237687336). The later external merge is confirmed separately above; it is not inferred from previous CI or fit review.

**Gate result:** upstream need pass; native mechanism pass; counterfactual value pass; scope compatibility pass.

See [Organization-owned fit observations](https://github.com/opensiro/vsm-oss-organization/blob/main/experiments/upstream-intervention-fit/observations.json). Do not confuse upstream reviewers' fix commits, authorship or tests on different refs with tests performed on the contributor's own head.
