# Runloop batch 14 — independent host rerun receipt (2026-11-08 UTC)

**Scope:** Source-only deterministic native execution for [Upstream #56](https://github.com/opensiro/upstream/issues/56) / [PR #174](https://github.com/opensiro/upstream/pull/174). This is **not** an external fork/branch/PR or a model-agent evaluation. The earlier, publicly inspectable [GitHub Actions #42493920695](https://github.com/opensiro/upstream/actions/runs/42493920695) remains the primary independent CI receipt.

## Executor and identity

- Execution boundary: authenticated `dev-alpha-2` SSH access to the operator-connected **zhdanov** VM. A transient **systemd user service** (`opensiro-b14-runloop-20261108-02.service`) performed the target tests; the chat assistant submitted the fixed job and read its result, but did not directly execute the Python target tests in its own runtime.
- Execution session: `ac603478-0e46-42cb-a771-0624220996d4`, 2026-11-08 UTC; completed at **18:56:05 UTC**, monitored exit code **0**. The first detached attempt was stopped when an SSH session ended because user linger was disabled; it produced **no test verdict** and is not counted. The second attempt held the authorized session open through completion.
- Host: Ubuntu 24.04.3 LTS, Docker 29.1.3. Isolated containers: PostgreSQL **16-alpine** and Python **3.11-slim**. Ephemeral Docker network/DB were removed on task exit. No always-on runner, scheduler or background agent was installed.
- Frozen source: `murilo-bassan/durable-agent-runtime@1d68208d017d27d1b21805753b51a3872c888a52`.
- Technical packet was checked out at internal PR head `f695ce0e0897202fb3c32db67fdee03a046d2b50` (at dispatch).
- Patch SHA-256: `b6e06c18de6917ea6dac1503b92dd3c24283b497111596da8ed7988e75e3d333`.
- Test SHA-256: `8b500a4ce56a14212f2b6ce5e1506ef0e5422231e74f509a95e0bc1bc70759fe`.

## Executed matched observations

1. The separate runner copied the exact test into `tests/test_upgrade_budget_finalization.py` on the **unmodified** first-party checkout. `python -m pytest -q tests/test_upgrade_budget_finalization.py` produced expected **2 failures** and **1 passing control**:
   - duplicate `settle()`: remaining **1100**, expected **750**;
   - `release()` after `settle()`: remaining **1350**, expected **750**.
   Both named native failures were checked explicitly before continuing.
2. The runner performed `git apply --check`, applied the exact archived patch to the same first-party checkout and ran `python -m pytest -q tests/test_budget_prompts.py tests/test_upgrade_budget_finalization.py` against the same isolated PostgreSQL service: **8/8 PASS**.
3. `git diff --check`: PASS. Final runner status: `RESULT=PASS`, service command exit **0**.

SHA-256 of the operator-host execution log: `f6f6691b519f109029f4977f57bb62afdfd750b20770ba39cf05150f4ca977d8`. Baseline test log: `2a3d4f5ac077fcafb874d9e2cc4157c5c25599c8a3c693abf15d32a5044cab53`. These host files are *not* publicly hosted immutable artifacts; the exact original GitHub Actions run above is the public CI evidence. This record preserves a second attributable executor result without overstating audit independence.

## Future reproducibility route

A source-only, **on-demand** native runner is now established on the already connected zhdanov host under its actual SSH/tool permissions; it requires no external contributor-fork stage and no OpenSiro permanent service. To repeat:

1. Establish current authorized host access and an isolated scratch checkout of this PR's [packet](CONTRIBUTION_HANDOFF.md) and the exact first-party source SHA above. Compare SHA-256 values before execution.
2. Dispatch the frozen [archived independent runner recipe](independent-runner-recipe.yml) as a distinct deterministic transient host job (or execute the equivalent native script in another actually authorized isolated CI runner). Use PostgreSQL 16 and Python 3.11; when Docker-networked, point `TEST_ADMIN_DATABASE_URL` and `TEST_DATABASE_URL` to the isolated `db:5432` service.
3. Preserve the runner identity, environment, commands, native before/after and control logs, completion status and artifact digests. Require both expected baseline failures and all eight after-patch successes. A failed or unauthenticated rerun cannot inherit this receipt.

This is an **execution route**, not a standing new S5 mandate or an assertion that future calls will have permission. If host permissions, source, dependencies or patch change, recheck before rerunning. Do **not** add a new project-specific workflow to `opensiro/upstream/main`; do **not** publish externally without the separate [Upstream #6](https://github.com/opensiro/upstream/issues/6) stage rights.

**Effect limit:** Bounded, source-pinned token-ledger correctness. No production/user benefit, third-party acceptance, autonomous S2 ownership transfer or Index regrade established.
