# KnowWork — independent native RED/GREEN receipt (2026-11-10)

## Frozen source and provenance

- Assessment: [KnowWork S2=C at frozen Index `da98a140`](https://github.com/opensiro/vsm-harness-index/blob/da98a140b1c6541f639c1dc4094bf2aeaacdb08d/assessments/kn/knowwork.md); assessed project ref `83c763e4fe2d63cd59e0344268afa94321d35585`.
- Pre-target-source hypothesis: [immutable batch-25 checkpoint `5ddeba9`](https://github.com/opensiro/upstream/commit/5ddeba928a62829d1951f3380d728920ff63ec01); first-party source inspected only after this checkpoint.
- Current first-party baseline: [`knowflow-ai/KnowWork@033b49240ec49c7b8d3b43f1783b9b4d89425b5e`](https://github.com/knowflow-ai/KnowWork/tree/033b49240ec49c7b8d3b43f1783b9b4d89425b5e), 2026-11-10; root `LICENSE` Apache-2.0.
- Exact affected code: [`server/src/knowwork_server/sandbox/containers.py`](https://github.com/knowflow-ai/KnowWork/blob/033b49240ec49c7b8d3b43f1783b9b4d89425b5e/server/src/knowwork_server/sandbox/containers.py), [native tests](https://github.com/knowflow-ai/KnowWork/blob/033b49240ec49c7b8d3b43f1783b9b4d89425b5e/server/tests/sandbox/test_lifecycle.py), and [FakeDocker](https://github.com/knowflow-ai/KnowWork/blob/033b49240ec49c7b8d3b43f1783b9b4d89425b5e/server/tests/sandbox/fake_docker.py).
- Archived independent reproducible artifacts: [test plan](TEST_PLAN.md), [regression patch](native-regression.patch), [candidate fix patch](native-fix.patch). Both cleanly apply independently to the frozen first-party source.
- SHA256 regression patch `30702f011b0487580fc9fd58e2253f5afacaabaf1d82344eef97765a13139192`; SHA256 fix patch `fcc24402da2b1dc7219fbed9098b3a893d54728620a6bc069f5a56f3bf6b60ca`.

## Deterministic execution on dev-alpha-2

The independent SSH runner used a separate clean clone at the pinned first-party commit and a second disposable worktree. Python 3.12, isolated venv with native project `pytest`/`docker`/`pydantic` dependencies; no model or real Docker daemon.

| Phase | Backend session | Observation |
|---|---|---|
| Existing native controls, pristine checkout | `08049ef5-2d7d-4632-bde2-c75f66518e7f` | Six relevant lifecycle checks PASS |
| Regression-only patch (before production fix) | `dceb81f0-2561-4b29-a45e-abe6f757c279` | **RED**: both `peer_start_race` variants FAIL with native `SandboxError` after simulated Docker API 304; newly-created path also removes the peer-started container |
| Same tests after bounded production patch | `7414d54d-b533-459f-8329-e72380074d41` | **GREEN 2/2**; full lifecycle test file also PASS |
| Expanded final test invocation | `7be843cc-5c20-45d9-b614-5815587ccef2` | **34 passed in 0.49s**, `compileall` PASS and `git diff --check` PASS |

Representative commands, executed within pinned source `server/`:
```bash
PYTHONPATH=src /home/robot/upstream-upgrade25-knowwork-venv/bin/python -m pytest --confcutdir=tests/sandbox -q tests/sandbox/test_lifecycle.py -k peer_start_race
PYTHONPATH=src /home/robot/upstream-upgrade25-knowwork-venv/bin/python -m pytest -o addopts='' --confcutdir=tests/sandbox -q tests/sandbox/test_lifecycle.py
```

`--confcutdir=tests/sandbox` deliberately excludes an unrelated parent `conftest.py` requiring a PostgreSQL `pgserver`; it does not bypass this module's fixture/test setup.

## Bounded interpretation

A process-local `SandboxKey` lock does not serialize separate business-server processes. In the tested interleaving, a peer starts the **same Docker container ID** between the local inspect/create and `start`; the losing process gets an already-started 304. Existing code propagates a false failure and, on create, can delete a running peer-owned sandbox. The candidate fix accepts a failed start only when fresh inspection of **that exact ID** says `running`; otherwise the original `SandboxError` and cleanup are retained.

This validates the source-native fake Docker state transition and regression behavior, **not** a real Docker multi-process deployment, production frequency, service reliability improvement, or real-world impact. No external PR was published, no maintainer acceptance claimed, and no new assessment grade was assigned.
