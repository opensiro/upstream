# BabyAI — reject non-positive native training and validation counts

**Stage:** `SUBMITTED_DRAFT` on 2026-10-24. [Upstream Draft PR #128](https://github.com/mila-iqia/babyai/pull/128) from `xLagerFeuer` using the public `opensiro-contributions/babyai` fork; no environment episode or agent execution.

- **External publication readback:** base `65fb0cb6f816532a65014bf034a758244e2d5ae7`, head `ee9746d9ac7010126cbfedac5de174ee65d87b51`, exactly two files changed; OPEN / Draft, no upstream merge claimed.

- **Frozen source:** `mila-iqia/babyai@65fb0cb6f816532a65014bf034a758244e2d5ae7` (BSD-3-Clause license), included `S1=A` Index SHA `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`. The Index identifies task/evaluation infrastructure, and the exact script argument deficit was found in `babyai/arguments.py`, a separate deterministic input boundary from the model/environment evaluation in `babyai/evaluate.py`.
- **Need — PASS:** `ArgumentParser.parse_args()` accepted `--procs 0`, `--frames-per-proc -1` and `--val-episodes 0` despite downstream scripts expecting positive process/rollout/validation counts. Zero validation episodes makes the batch evaluator use `num_envs=0`, leading to invalid loop sizing rather than a clear CLI error.
- **Mechanism — PASS:** After `argparse` parses numeric values, validate these three strictly positive counts using the existing standard `ArgumentParser.error()` path. Preserve valid defaults, explicit positive values and existing seed handling.
- **Counterfactual — PASS:** Five genuine first-party Python parser tests with fixed `sys.argv` fixtures; **2 PASS / 3 FAIL** before, **5 PASS / 0 FAIL** after. No `Gym` environment, RL iteration, learned/model agent or inference was instantiated.
- **Scope — PASS:** `babyai/arguments.py` plus one standalone native `unittest` script. Model evaluation and downstream training remain untested; the claim concerns CLI admission only.

## Verification

| Command | Result |
| --- | --- |
| `python3 -m unittest discover -s tests -p test_native_argument_contract_unittest.py -v` before | 2 PASS / 3 FAIL |
| Same command after | 5 PASS / 0 FAIL |
| `python3 -m py_compile ...`, `git diff --check`, `git apply --reverse --check` | PASS |
| RL episodes, model/agent behavior, external PR/merge | **Not run / not claimed** |

**Exact source patch:** [native-training-argument-guard.patch](native-training-argument-guard.patch), SHA256 `e8ff3276e248490c535c3a6183935a385bd53e4e01a157918a1bac64cfd1f32e`.

**Limits:** The three validated counts are not a complete specification of all training flags. This is an input-schema guard, not a reported improvement in agent training performance. External maintainer review and merge remain human-owned; the technical candidate is complete.
