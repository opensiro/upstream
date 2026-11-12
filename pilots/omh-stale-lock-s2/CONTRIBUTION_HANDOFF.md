# Oh My Hermes — prevent two claimants during stale plan-lock reclamation

**Batch:** [Upstream #56](https://github.com/opensiro/upstream/issues/56), 2026-11-12 batch 27. **Current verified publication stage:** `EXTERNAL_OPEN_READY / ASSESSMENT_DERIVED` (no maintainer decision yet). The historical frozen screening manifest records the earlier `AWAITING_EXTERNAL` checkpoint; it is not rewritten.

**Public GitHub readbacks (2026-11-12):** [Original upstream PR #28](https://github.com/witt3rd/oh-my-hermes/pull/28) · [Matching fork-local proposal #1](https://github.com/opensiro-contributions/oh-my-hermes/pull/1) · [Contributor fork](https://github.com/opensiro-contributions/oh-my-hermes) · [exact working commit `6eced4f`](https://github.com/opensiro-contributions/oh-my-hermes/commit/6eced4fdad9ff4faa7daf0979021d870558e8d26). Open/Ready, one commit based on original `master@3b06e33`, the two native files only, fork-local and original PR bodies identical (SHA256 `142f0a0eae0162708b6727544696975b552e40e79c3a896340e94a5a7cfa569e`), checked first-party plugin suite **195 PASS / 7 SKIP** on the actual published fork branch. The external maintainer has not accepted or merged the change. Public submission was performed by the authenticated `xLagerFeuer` dev-alpha-2 host under the current owner standing publication mandate, after separate P1 fork/branch preparation.

## Native product contract

First-party [Oh My Hermes](https://github.com/witt3rd/oh-my-hermes/tree/3b06e33ae67b202b342989b484f08143e65e250d) is MIT licensed and currently uses that exact `master` revision. Ralph/Autopilot call `plugins/omh/omh_state.py::state_lock_acquire` to ensure only one live holder for the same keyed plan. The normal `os.O_EXCL` creation is atomic; the **stale-PID reclaimer** is not. Two contenders may read one dead-holder PID; while B is paused, A unlinks and acquires a new lock; B then unlinks A's **fresh** lock and also succeeds.

## Origin and evidence

- [Immutable Index assessment](https://github.com/opensiro/vsm-harness-index/blob/85ae995fc2551ac0a076609bce0300d075cac2d5/assessments/oh/oh-my-hermes.md) (S2=C; review 2026-10-27). Its S2 interference witness is per-plan mutual exclusion among separate instances.
- [Pre-code hypothesis checkpoint `9e2c1e9`](https://github.com/opensiro/upstream/commit/9e2c1e9695a82fcb853d05244ba8198dcd61dc1b), committed *before fresh source inspection*, predicted dual acquisition from a non-atomic check/record boundary. It was narrowed to the **stale recovery check–unlink sequence** after reading first-party source, not retrofitted from a third-party issue.
- [Distinct-host native RED/GREEN replay](../../reports/2026-11-12-omh-stale-lock-native-replay.md): original **1 FAIL** (A and B both `acquired=True`), patched **1 PASS**, full first-party Python plugin suite **195 PASS, 7 SKIP**.
- Exact source `3b06e33ae67b202b342989b484f08143e65e250d`; [production patch](native-fix.patch) SHA256 `3195879df9cca44921c4e8b859bd7fe0f996a923f4c006222afbfa94d6a8a1d2`; [native regression](native-regression.patch) SHA256 `f345b09552108041fa5b66d9e959d9b5c17a3204a5d69a318fc163ee6c068791`.

**Executable two-file packet for the connected stage:** [native-contribution.patch](native-contribution.patch), SHA256 `7510b3a3c6e0fc1e476490848f12cb5225101414e4f479a71031d843e3017e9e`. This includes the previously certified production and regression changes *unchanged*; additive selected-packets.json now selects the combined exact native pair for atomic creation of the working branch. Original individual patch hashes remain available above for independent review. The two-file host adapter accepts **only these exact OMH production/test paths**; it does not admit arbitrary plugin files.

## Fix and fit

Protect *only the rare stale reclaimer* using a sibling SQLite `BEGIN IMMEDIATE` transaction and re-check the current lock PID before removal; ordinary uncontended acquisition still uses the original no-DB `O_EXCL` path. The extra `.omh-lock-reclaim.sqlite3` file lives under the existing private state root; Python standard library, no dependencies or provider calls.

The first-party `CONTRIBUTING.md` accepts focused PRs; no separate contributor-person CLA or matching open stale-reclaimer PR observed in bounded fresh GitHub checks. Four fit gates `need/mechanism/counterfactual/scope=PASS` as bounded by the receipt. External fork/branch/PR still requires a **fresh authenticated stage**, exact source/fork SHA, reviewable technical packet selection, unchanged patch hashes, verified source policy, native CI and original maintainer acceptance decision.

This is source-level lock correctness under a deterministic test, **not** proof of a production incident, measured crossprocess performance, universal race-freedom, deployed benefit or a VSM autonomy regrade.
