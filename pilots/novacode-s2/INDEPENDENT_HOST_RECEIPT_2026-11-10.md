# NovaCode S2 — separate native runner receipt (2026-11-10 UTC)

**Result:** bounded first-party pytest regression reproduced a teammate worktree cwd escape on the original source, then passed with a scoped fix. **RED 8/9 → GREEN 9/9**; this is a deterministic local source-path result, not deployed agent or tool-write verification.

## Pinned inputs

- Assessment: [NovaCode Index S1=A/S2=C](https://github.com/opensiro/vsm-harness-index/blob/46219bf103b0b122d86abc3ca70ae3d8bc820e2c/assessments/no/novacode.md).
- Preregistered S2 hypothesis: [Upstream commit `02b24e37`](https://github.com/opensiro/upstream/commit/02b24e372aa5f6158e6c37623626e17bc104b181), committed before first-party code inspection.
- First-party source: [`gczhuang-cmd/NovaCode@34a2d555a530120fd6241f7065d49390e52f3573`](https://github.com/gczhuang-cmd/NovaCode/tree/34a2d555a530120fd6241f7065d49390e52f3573); runner checked full Git SHA against the clone HEAD.
- [Production fix](native-fix.patch), SHA-256 `e77dd63490a71d269aac0f43e86cb1e3f69116c41f3636910a4625adb264274c`.
- [Regression-only patch](native-regression.patch), SHA-256 `23685106d4e851c733932106e6454b01425625e436600d3aef73ebec5d8db2c6`.
- Runner obtained both patches from the `research/upstream-upgrade-batch-23-20261110` branch after the final patch-context correction; the displayed digests are the exact independently observed bytes. Retain this receipt with the patches for replay. The branch was mutable at runtime; SHA-256 pins the payloads.

## Separate executor

- **Machine:** `dev-alpha-2` registered Zhdanov's Siro VM, SSH device `8493ff56-7ee6-4d0a-afe1-d2cdebc3456a`, not the chatbot's working shell.
- **Monitored session:** `fa81ce8f-dfdc-4046-8194-3df5e5437271`; 2026-11-10 14:19:21–14:19:29 UTC; completed with **exit 0**, 67 output lines.
- **Working checkout:** `/tmp/opensiro-b23-nova.eIGTUq/novacode`; branch-packet checkout `/tmp/opensiro-b23-nova.eIGTUq/upstream` (temporary, no durability promise).
- **Tools:** Linux, Python 3.12.3, pytest 7.4.4, git 2.43.0, repository source loaded with `PYTHONPATH=src`. Neither a model nor a browser nor real teammate tool-write was invoked.

## Matched source-native replay

1. Verify the exact source Git SHA, verify both patch digests, apply regression-only patch by `git apply --check` followed by `git apply`.
2. `PYTHONPATH=src python3 -m pytest -q tests/test_team_backend.py` → **exit 1**: `8 passed, 1 failed`, new `test_inprocess_spawn_inherits_worktree_cwd_without_leaking` failed because the child observed `parent/probe.txt` instead of `worker/probe.txt`.
3. Apply production fix patch by `git apply --check` then `git apply`; rerun the **identical** pytest command → **exit 0**: `9 passed, 1 warning` (host pytest did not recognize `asyncio_mode` config option).
4. `git diff --check` → PASS; session output ended `INDEPENDENT_MATCHED_RED_GREEN=PASS`.

Only `src/novacode/team/backend/inprocess.py` and `tests/test_team_backend.py` are affected. The instrumented fake task manager observes the first-party launch boundary and task context; the test is not a live filesystem write or proof of inter-process serialization. No third-party PR or S2 grade change was performed.
