# GitHub Actions: ownership and cleanup

**Operator question:** Which workflow should I use, and why are there so many?

This is an **ownership map**, not a request to run every workflow. The live
GitHub Actions screen also includes some workflows registered from branches
that are **not** on `main`. For a source-dated count, exact names and run
receipts, see the [2026-11-11 audit](../reports/2026-11-11-actions-audit.md).

## Upstream-owned workflows (keep)

| Intent | Action on `main` | Effect |
| --- | --- | --- |
| Check repository data and documentation | [`repository-integrity.yml`](../.github/workflows/repository-integrity.yml) | PR/push/offline tests; does not validate an external harness's product behavior |
| Preview a fork lifecycle | [`fork-lifecycle.yml`](../.github/workflows/fork-lifecycle.yml) | Manual preview; **no fork write** |
| Watch external PR reviews and CI | [`pr-maintenance.yml`](../.github/workflows/pr-maintenance.yml) | Hourly/opt-in, bounded local issue-inbox updates |
| Collect external PR status evidence | [`portfolio-reconciliation.yml`](../.github/workflows/portfolio-reconciliation.yml) | Read-only portfolio reconciliation and retained run artifact |
| Screen externally verified outcome candidates | [`verified-external-outcomes.yml`](../.github/workflows/verified-external-outcomes.yml) | Candidate evidence only; no adoption-KPI claim |
| Detect stale local PR lifecycle data | [`upstream-status-freshness.yml`](../.github/workflows/upstream-status-freshness.yml) | Read-only drift check; no automatic change |
| Prepare a lifecycle drift correction | [`upstream-status-proposal.yml`](../.github/workflows/upstream-status-proposal.yml) | Read-only scheduled patch artifact; **internal Draft PR only by explicit manual input** |

The jobs above have different credentials, schedules, outputs and failure
contracts. In particular, do **not** merge write-capable inbox maintenance
into read-only external observers merely to reduce the workflow count.
See [operations](OPERATIONS.md) for commands and exact permissions.

The former `test-fork-lifecycle.yml` repeated the full `unittest discover`
suite already run on every PR and `main` push by `repository-integrity.yml`.
It was retired after verifying no required status-check dependency; the
historical GitHub runs remain accessible. No fork-lifecycle test was removed.

## Third-party native workflows (retirement queue)

`main` retains historical source-native CI for three projects. Agent Code,
Kram and Zot are fully migrated, while Kit's offline workflow has matching-fork
parity and its macOS-containing compatibility workflow still awaits a runner:

| Source | Legacy workflows | Working-fork migration |
| --- | ---: | --- |
| Agent Code | 0 | [Three Agent Code 524 native gates migrated to the matching fork](../pilots/agent-code-524/NATIVE_CI_MIGRATION_2026-11-11.md); original recipes archived |
| AgentBox | 1 | [Two pinned baselines migrated to fork-native CI](../pilots/agentbox-s2/NATIVE_CI_MIGRATION_2026-11-11.md); retain manager-advisory workflow for [open PR #71](https://github.com/opensiro/upstream/pull/71) |
| HarnessDesk | 2 | [Pinned matching-fork Linux `check:push` PASS](https://github.com/opensiro-contributions/HarnessDesk/actions/runs/43075481763); both macOS jobs [blocked before runner acquisition](https://github.com/opensiro/upstream/issues/214#issuecomment-6804460569). Preserve both historical YAML until macOS parity succeeds |
| Kit | 1 | [Pinned fork-native offline RED/GREEN PASS](../pilots/kit-222/NATIVE_CI_MIGRATION_2026-11-11.md); compatibility retained until macOS parity |
| Kram | 0 | [Pinned fork-native RED/GREEN PASS](../pilots/kram-s2/NATIVE_CI_MIGRATION_2026-11-11.md); original recipe archived |
| Zot | 0 | [Four pinned native cases migrated to the matching fork](../pilots/zot-shared-workspace/NATIVE_CI_MIGRATION_2026-11-11.md); original recipes archived |

**Do not run these by default, add new per-harness Actions here, or delete
them solely because they are old.** New source-native checks live in the
matching `opensiro-contributions/<target>` fork (or a distinct deterministic
runner) under [native CI placement](NATIVE_CI_EXECUTION.md). The current
automated guard is [`tests/test_native_ci_placement.py`](../tests/test_native_ci_placement.py).

An equivalent migration needs:

1. Source commit, exact patch/test hashes, native OS/runtime, historical run
   and artifact retention recorded in Upstream.
2. A real source-matched fork/runner run demonstrating equivalent native
   before/after behavior (including expected RED, controls and GREEN).
3. Updated references and pinned tests, followed by a **reviewed removal PR**
   for the replaced Upstream workflow. Removing YAML must not remove its
   durable evidence.

Track retirement in [Upstream #214](https://github.com/opensiro/upstream/issues/214).
The related [repository standards #130](https://github.com/opensiro/upstream/issues/130)
covers the broader repo cleanup. The existence of a generic `ci.yml` in a
working fork is **not** proof of equivalent pinned native coverage.

## Why GitHub's Actions tab may show more than `main`

GitHub can continue to list registered workflows from PR branches after their
workflow file is absent from `main`. A registered `active` status in the API
does **not** establish that the workflow is present or scheduled on `main`.
Investigate the workflow path, exact PR/head ref, existing runs and branch
retention before disabling or retiring it. Do not delete a workflow on an
open technical PR just to simplify the list.
