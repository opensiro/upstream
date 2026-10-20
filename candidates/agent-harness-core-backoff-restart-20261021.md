---
candidate_id: IMPR-AGENT-HARNESS-CORE-BACKOFF-20261021
state: SCREENING
origin_class: ASSESSMENT_INFORMED
target_repo: phenomenoner/agent-harness-core
index_sha: 5393b698bfdfa4ca14d97a79238234eca20694e5
assessment_path: assessments/ag/agent-harness-core.md
review_ref: 1e247e064061e4427f4b78e8afd8671e6e7f06f0
source_sha: 1e247e064061e4427f4b78e8afd8671e6e7f06f0
fit_need: PASS
fit_mechanism: PENDING
fit_value: PENDING
fit_scope: PENDING
---

# IMPR-AGENT-HARNESS-CORE-BACKOFF-20261021 — direct-owner restart state compatibility

**Origin:** `ASSESSMENT_INFORMED`, not a VSM S2/S3 diagnosis. The [frozen Index assessment](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ag/agent-harness-core.md) maps an actual durable, mixed workload coordination and master/child current-control architecture. It **does not** describe a restart deadlock or serialized state spelling defect. The independently discovered native [issue #22](https://github.com/phenomenoner/agent-harness-core/issues/22) reports the concrete restart failure on release v0.13.1 at the exact currently inspected commit `1e247e064061e4427f4b78e8afd8671e6e7f06f0`.

## Native failure

The issue provides a real direct-owner restart receipt: stopped Scheduled Task, master import 7/9 valid, 2 blockers and repeated successor master exits. `SupervisorChildActualState::Backoff` serializes `backoff`, but [`supervisor_master.rs`](https://github.com/phenomenoner/agent-harness-core/blob/1e247e064061e4427f4b78e8afd8671e6e7f06f0/crates/agent-harness-core/src/supervisor_master.rs) importer explicitly lists `restart-backoff`. Product impact is bounded service restart downtime, **not** evidence of automatic S3 upgrade.

A narrow potential remedy would align typed producer/importer states and permit a **provenance-bound**, PID-free backward-compatible `backoff` import, while preserving fail-closed identity checks and adding bounded graceful-stop sequencing. Do **not** simply accept all unknown states.

| Native gate | Verdict | Evidence |
| --- | --- | --- |
| Need | `PASS` | Observed first-party restart issue #22, exact current source vocabulary |
| Mechanism | `PENDING` | Typed state round-trip and graceful-stop policy need local Windows validation |
| Counterfactual benefit | `PENDING` | No current Windows restart replay nor before/after measured |
| Scope | `PENDING` | Windows Scheduled Task owner, PID identity/reuse, persisted schema migration and maintainers' policy need approval |

**Next falsifier:** attempt an isolated state round-trip, then guarded Windows T3 restart with one backoff child; prove every state import and exactly one ready owner/9 children. Current link only reviews incident and source. No external patch, PR, fork, permission or grade edit; state `SCREENING`, not `QUALIFIED`.
