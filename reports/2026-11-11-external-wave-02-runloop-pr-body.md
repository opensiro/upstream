# Proposed external PR: murilo-bassan/durable-agent-runtime

**State:** internal exact-title/body proposal only; do **not** publish without current-source checks, an effective fork/branch stage grant and an individual human approval of this exact title/body. Code and native tests have **not** been pushed to a fork. This heading and note are not part of the PR body.

**Proposed title:** `fix: finalize token budget reservations idempotently`

## Proposed PR body (copy verbatim only after the gates above)

## Summary

- Associate token-ledger finalization with the actual reservation ledger ID, not just a run ID, since one run may legitimately reserve multiple times.
- Release a reservation at most once using a partial unique index and `ON CONFLICT DO NOTHING`, while making a first `settle()` write its release and usage in a single transaction.
- Add a forward SQL migration for `reservation_id` and three Postgres regression tests covering duplicate settlement, release-after-settlement and independent reservations within one run.

## Why

Repeated calls to `settle()` or `release()` previously credited the reservation more than once. For a 1,000-token budget with a 600-token reservation and actual usage of 250, retries must leave **750**, not 1,100 or 1,350. This patch focuses on retry safety; it does not change token pricing or scheduling.

## Validation

- Historical source-native Postgres CI on target `main@1d68208d017d27d1b21805753b51a3872c888a52`: 2 newly added regression tests failed before the fix; **8 relevant tests passed** after the fix (3 new tests and 5 existing controls). [Independent run](https://github.com/opensiro/upstream/actions/runs/42493920695).
- Current publication preflight confirmed the target source SHA is unchanged, but **did not rerun migration/deployment or the full repository test suite**. Maintainer review of the forward migration and database compatibility remains important.
- [Reproduction and exact patch handoff](https://github.com/opensiro/upstream/blob/main/pilots/runloop-s2/CONTRIBUTION_HANDOFF.md).

<!-- opensiro-ai-assessment-disclosure:v2 -->
## AI-assisted contribution disclosure

**VSM assessment:** [Current record](https://github.com/opensiro/vsm-harness-index/blob/main/assessments/ru/runloop.md) · [Snapshot used for this PR](https://github.com/opensiro/vsm-harness-index/blob/8ef26789403d7cf682e67dcc7985a0317a76bb00/assessments/ru/runloop.md)

**Assessment date:** 2026-11-05 (`reviewed_at`) · **Assessed source revision:** `1d68208d017d27d1b21805753b51a3872c888a52`

This PR was prepared by the [OpenSiro Upstream Contributions](https://github.com/opensiro/upstream) AI-agent workflow, informed by the VSM assessment linked above. Technical analysis, code changes and reported checks were agent-driven; no independent human code review is claimed. For now, a human approves publication while monitoring the pipeline for errors. That approval is **not** a technical correctness guarantee. Fully autonomous publication is a future goal, **not** the status of this PR. AI-generated changes may be incomplete or incorrect; please review the diff and evidence independently.

The assessment describes the assessed source revision on the stated date; it is not a guarantee about this PR or later upstream code. Maintainers and their agents can compare the current record with the snapshot and reassess if the source or evidence has changed.
