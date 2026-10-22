# Reef / Polyp — archive replay can falsely report an unpushed commit as published

**Stage:** `AWAITING_EXTERNAL`. A tested source-only patch packet; no external fork, issue, PR, remote network Git, database or model/agent run.

- **Frozen source:** `Coral-Bricks-AI/reef@33aefaa12d78891bf5ba70a0d96b070d471ecc78` (Apache-2.0), included `S1=A` Index `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`. The assessment places Polyp experiment-state, queue and archive protocol in the first-party boundary. This defect comes from direct source inspection of `polyp/queue/cbq.py::git_commit_push`, not from a model experiment.
- **Need — PASS:** On retry after local `git commit` succeeds but `git push` is interrupted, there are no new changes to commit. The function returned `True` immediately on `nothing to commit` without pushing, despite the previous archive commit still missing from `origin/main`. It could falsely report a durable archive export.
- **Mechanism — PASS:** Treat `nothing to commit` as a valid state for the existing push/retry loop, not as completed publication. Reject other commit failures instead of ignoring them. Preserve normal first-publish and already-synced idempotence.
- **Counterfactual — PASS (bounded):** three `unittest` cases use **real local Git binaries**, a temporary bare repository acting as `origin`, and a temporary working repository: pending-unpushed-commit retry, new file modification commit/push and already-synced no-op. Before patch **2 PASS / 1 FAIL** (remote SHA stale after claimed success), after **3 PASS / 0 FAIL**.
- **Scope — PASS:** the original queue script helper and one offline Python `unittest` file. No PostgreSQL server, GPU worker, model, provider, hosted project, or network Git remote.

## Verification

| Script | Result |
| --- | --- |
| `uv run --no-project --with 'psycopg[binary]' python3 -m unittest discover -s polyp/queue -p test_native_git_archive_retry_unittest.py -q` before | 2 PASS / 1 FAIL |
| Same command after | 3 PASS / 0 FAIL |
| `python3 -m compileall -q ...`; `git diff --check` | PASS |
| `git apply --reverse --check` on modified pinned checkout | PASS |
| Real Postgres/worker/model; real GitHub publication; upstream CI | **Not run / not claimed** |

**Exact tested patch:** [unpushed-archive-commit-retry.patch](unpushed-archive-commit-retry.patch), SHA256 `323710c9d0100010daaf034a37c479ce139d0ff7fca6883e4a47d92fea40a38e`. Exact byte match to modified source diff. `psycopg` was made available only to import the genuine queue module; `connect()` was never called.

**Limits:** Proves one replay failure mode of a local Git archive helper, not eventual success on unreliable real GitHub remote. It is unrelated to the effectiveness of model-generated experiment ideas. External upstream publication remains human-owned. Generic `continue` advances to SIFRA.
