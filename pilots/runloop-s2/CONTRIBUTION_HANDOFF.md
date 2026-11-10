# Runloop — idempotent reservation finalization (S2)

**Internal technical packet only.** [Upstream #56](https://github.com/opensiro/upstream/issues/56), [batch 14](../../data/assessment-candidate-batches/2026-11-08-14-SUMMARY.md), [Draft PR #174](https://github.com/opensiro/upstream/pull/174). No fork/branch/external PR has been created for this case; no authorization to publish one is inferred.

## Why this is assessment-derived

The canonical [Runloop Index assessment](https://github.com/opensiro/vsm-harness-index/blob/8ef26789403d7cf682e67dcc7985a0317a76bb00/assessments/ru/runloop.md) observes **S2=C**: deterministic, owner-shared token-budget reservation and settlement under a database lock, with no autonomous allocation owner. Before fresh Runloop source inspection, immutable [checkpoint `60b5eff`](https://github.com/opensiro/upstream/blob/60b5eff942e23e9932f6f37ff118e59b453fbe5a/data/assessment-candidate-batches/2026-11-08-14-HYPOTHESES.md) specifically predicted a double-credit or stranded-budget retry/release path. It did not predict an autonomy grade increase.

First-party [MIT source `main@1d68208`](https://github.com/murilo-bassan/durable-agent-runtime/blob/1d68208d017d27d1b21805753b51a3872c888a52/runtime/budget.py) confirms the need: each call to `settle()` inserts an entire refund plus actual use, and `release()` can append another refund for the same reservation. With budget `1000`, reservation `600` and usage `250`, repeat finalization must still leave `750` available. The original ledger did not associate finalization rows with the particular reservation; same run ID can legitimately have multiple separate reservations.

## Exact patch, test and scope

| Artifact | Role | SHA256 |
| --- | --- | --- |
| [`idempotent-budget-finalization.patch`](idempotent-budget-finalization.patch) | `runtime/budget.py` and forward migration `runtime/migrations/0003_budget_finalization_idempotency.sql`; one terminal release per reservation ID, settlement insertion atomic with first release | `b6e06c18de6917ea6dac1503b92dd3c24283b497111596da8ed7988e75e3d333` |
| [`test_budget_finalization.py`](test_budget_finalization.py) | Three native Postgres fixture tests: duplicate settlement, release after settlement, independent reservations with the same run ID | `8b500a4ce56a14212f2b6ce5e1506ef0e5422231e74f509a95e0bc1bc70759fe` |
| [`independent-runner-recipe.yml`](independent-runner-recipe.yml) | Archived, non-active original GitHub Actions test recipe for independently rerunning on a permissioned fork/runner | Historical exact-run attribution below |

The patch assumes Runloop's existing migration order and Postgres `ON CONFLICT` support. It uses a partial unique index on `reservation_id` for ledger rows whose kind is `released`; historical entries without a reservation ID remain unaffected. This patch fixes repeated finalization only; it does not redesign token pricing, scheduling, cancellations or autonomous control.

## Independent deterministic before/after

- Executor: GitHub Actions job [`before-after` in run #42493920695](https://github.com/opensiro/upstream/actions/runs/42493920695), 2026-11-08 UTC, **SUCCESS**, head commit `6b9b9afcfeb56edd32d1f5590cb80ec5a55f3eed`.
- Environment: Ubuntu hosted runner, Python 3.11.18, PostgreSQL 16 Alpine service; target checked out at immutable `1d68208d017d27d1b21805753b51a3872c888a52`; native dependencies from first-party `requirements-dev.txt`.
- Before: add the three tests to the **unmodified** source, invoke `python -m pytest -q tests/test_upgrade_budget_finalization.py`. Baseline `FF.`: duplicate `settle` returns remaining **1100** (`750` expected), `release` after `settle` returns **1350** (`750` expected); independent-reservations control passes.
- After: `git apply --check` and apply archived patch, then `python -m pytest -q tests/test_budget_prompts.py tests/test_upgrade_budget_finalization.py`; **8 dots / 8 passing assertions**, including five original source budget tests. `git diff --check` succeeds. Logs and file SHA256 checks were recorded by the independent runner; no live model or browser agent executed.

**Outcome:** `ASSESSMENT_DERIVED`, native need/mechanism/counterfactual/scope **PASS**, `BOUNDED_NATIVE_CORRECTNESS_ONLY`, stage `AWAITING_EXTERNAL`, external action `NOT_EXECUTED`. These are bounded first-party code-path results, not production/user/maintainer observations or a VSM autonomy grade change.

## Reproduction and delivery boundary

The completed Upstream Actions run is a **historical pinned receipt**. Its one-off workflow must not be added to `upstream/main`; this recipe is archived as a non-active pilot file. A separate [2026-11-08 zhdanov host-runner receipt](INDEPENDENT_HOST_RECEIPT_2026-11-08.md) now records an authorized one-shot deterministic rerun (expected 2 native baseline failures, 8/8 after PASS, monitor exit 0) and the on-demand reproduction route via the already-connected host. Future native replays require current host permission, exact source/packet pins and new attributable receipts; an authorized `opensiro-contributions` working fork is an alternative, not an assumed stage grant. Repository-integrity CI in Upstream does not substitute for native evidence.

Before an external Draft PR: recheck current default and intended contribution branch, license/DCO/CLA requirements, overlapping patches, branch/fork stage permission and independently reproduced regression. Upstream [#6](https://github.com/opensiro/upstream/issues/6) remains the disconnected general executor gate; the finite Corrective mandate does not apply. Publication and any third-party maintainer decision require their own evidence. Do not open an external PR or claim a completed end-to-end research cycle from this packet.
