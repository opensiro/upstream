# Oh My Hermes S2 — separately executed native stale-lock recovery replay

**Recorded:** 2026-11-12 UTC. **Owner:** [Upstream #56](https://github.com/opensiro/upstream/issues/56), batch 27.
**Origin:** included S1=A/S2=C [Index assessment](https://github.com/opensiro/vsm-harness-index/blob/85ae995fc2551ac0a076609bce0300d075cac2d5/assessments/oh/oh-my-hermes.md) at exact `85ae995fc2551ac0a076609bce0300d075cac2d5`. [Prospective hypothesis](https://github.com/opensiro/upstream/commit/9e2c1e9695a82fcb853d05244ba8198dcd61dc1b) committed BEFORE original code/issues inspection. **Original** `witt3rd/oh-my-hermes@3b06e33ae67b202b342989b484f08143e65e250d` is also current `master` (MIT; no known conflicting stale-reclaim PR in bounded GitHub search).

## Actual source problem and first-party mechanism

Fresh lock creation uses `os.O_EXCL` and prevents ordinary dual acquisition; the precise predicted non-atomic gap is **stale recovery**, not initial creation. Two contenders can both read the same dead-holder PID. While B is delayed after reading the old PID, A deletes the stale path and atomically acquires the lock; B then unlinks A's **new live lock** based on its obsolete observation and itself returns `acquired=True`. That violates the native advisory lock's one-holder contract for two independently executing sessions.

The test runs genuine `plugins/omh/omh_state.py::state_lock_acquire` twice in separately named Python threads with deterministic event gates, isolated per-test `tmp_path`, and a patched PID-liveness predicate for exactly one synthetic dead PID. It does not create a live user lock or execute a model. The checked fix serializes **stale recovery only** through a sibling SQLite `BEGIN IMMEDIATE` interprocess transaction, *re-reads the live path under the guard* and removes it only if the current holder remains dead. Ordinary uncontended `O_EXCL` creation is unaffected. SQLite uses Python standard library; the sidecar is retained in the private state directory. This is a bounded correctness change, not proof of real-world failure rate or full multi-process race-freedom.

## Exact independent native results

**Executor:** authenticated, distinct dev-alpha-2 Linux VM (Zhdanov), source-pinned clean worktree at `/tmp/opensiro-omh-replay-b27-20261112`, Python 3.12.3 / pytest 7.4.4. The assistant prepared code and test design; the runner executed real first-party Python, not LLM-agent/virtual provider calls. Original project unchanged; all reproduction state under pytest's temporary paths.

| Stage | Exact command | Observed result |
| --- | --- | --- |
| Original source + **exact same regression patch** | `python3 -m pytest plugins/omh/tests/test_state.py -q -k concurrent_stale_reclaim --tb=short` | **RED: exit 1**, one failed test; source returns `acquired=True` for **both A and B**; all other 75 tests deselected |
| Original + regression + production patch | Same focused command | **GREEN: 1 PASS**, 75 deselected; exit 0 |
| Fully patched first-party suite | `cd plugins/omh && python3 -m pytest tests/ -q` | **195 PASS, 7 SKIP, 0 FAIL**; exit 0 |
| Syntax/diff | `python3 -m py_compile`, `git apply --check`, `git diff --check` | **PASS** |

- [Production patch](../pilots/omh-stale-lock-s2/native-fix.patch) SHA256 `3195879df9cca44921c4e8b859bd7fe0f996a923f4c006222afbfa94d6a8a1d2`.
- [Native first-party regression patch](../pilots/omh-stale-lock-s2/native-regression.patch) SHA256 `f345b09552108041fa5b66d9e959d9b5c17a3204a5d69a318fc163ee6c068791`.
- Patched source SHA256 `7b9651103d8546f8fc8398b7b495b2974c0bef98c9273f9216de35644af37cd4`; patched test SHA256 `bea6419613cb2c140eef5736a402e43fc79ce34c1d92c4ae5e73f37a4a9ed6a9`.
- Logs on the distinct host: `/tmp/opensiro-omh-replay-red-b27.log`, `/tmp/opensiro-omh-replay-green-b27.log`, `/tmp/opensiro-omh-replay-full-b27.log`; reproduced twice including the initial `/tmp/opensiro-omh-stale-red-20261112.log` and patched full suite.

## Native-fit gates and boundaries

- **Need=PASS:** the lock directly promises one active holder per `(mode, lock_key)`; two `acquired=True` results are observed in the original source.
- **Mechanism=PASS:** stale-file check–unlink–retry is not atomic even though normal `O_EXCL` creation is.
- **Counterfactual=PASS:** a second claimant now gets refusal, preventing dual-owner corruption without depending on any VSM terminology.
- **Scope=PASS:** two first-party files, no new dependency, no model runtime, no user data or protected code modification; original MIT source and CONTRIBUTING are consistent with a focused bug fix.
- **Not claimed:** a cross-process stress matrix (the matched test uses deterministic threads), a full deployed user workload, a VSM grade change, original maintainer acceptance, or a fork/external PR unless separate GitHub stage readback verifies those later.
