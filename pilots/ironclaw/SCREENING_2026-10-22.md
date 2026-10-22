# IronClaw — scheduler/recovery screen closed without a duplicate fix

**Batch:** [2026-10-22-01](../../data/assessment-candidate-batches/2026-10-22-01.json), row 5/5.
**Disposition:** CLOSED_NO_CHANGE; no Rust patch, model-agent test or external GitHub write.

## Frozen finding and first-party overlap

- [Index assessment](https://github.com/opensiro/vsm-harness-index/blob/f2ea54a19770b21f88d70113fe8c60c72802e19e/assessments/ir/ironclaw.md) pins nearai/ironclaw at b0b999d96781516ee05e6ba961d6f3ead900da96. The current GitHub default-branch API still pointed at this commit when checked on 2026-10-22. The assessment observes bounded job concurrency and deterministic recovery as S2 coordination, not a confirmed defect.
- [First-party issue #6455](https://github.com/nearai/ironclaw/issues/6455) asks the assigned maintainer to reconcile legacy stuck-job self-repair with Reborn heartbeat, expired-lease recovery, bounded reclaims and terminal reporting, adding only missing caller-level tests. It explicitly prohibits a second recovery scheduler.
- [First-party PR #6458](https://github.com/nearai/ironclaw/pull/6458) directly covers the recovery/reconciliation need and remained **open/unmerged** at this check. Its native Rust scheduler, lease/crash and integration tests are maintainer claims, **not** independent OpenSiro results.
- [First-party runner contract](https://github.com/nearai/ironclaw/blob/b0b999d96781516ee05e6ba961d6f3ead900da96/docs/internal/reborn/contracts/turn-runner.md) already specifies expiry outcome/recovery semantics.

## Fit and disposition

- **need PASS:** a bounded maintainer-issued question exists.
- **mechanism PASS:** first-party contract and PR cover the genuine lease-recovery mechanism.
- **counterfactual FAIL:** no independent uncovered failing native case was established beyond the maintainer's existing work.
- **scope FAIL:** a competing repair would duplicate #6458 and risk violating the explicit no-second-scheduler boundary.
- **origin INSUFFICIENT** for a new OpenSiro intervention. No assessment-derived discovery and no executed product fix claimed.

Close this candidate screening, preserve the overlap, and roll over to the next **complete frozen Index-based cohort** as required by the Upstream batch practice. Revisit only for genuinely distinct new native evidence.
