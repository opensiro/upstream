# CodeAct S2 — independent first-request kernel admission receipt (2026-11-09 UTC)

**Result:** bounded first-party Tornado kernel allocation **RED → GREEN** on a separate `dev-alpha-2` SSH host runner. This proves one deterministic session-admission correctness effect, **not** deployed reliability, real Docker/Kubernetes isolation, live agent quality, maintainer acceptance or S2 autonomy change.

## Source and immutable inputs

- Canonical Index: [`codeact`, S1=A/S2=C, exact Index `46219bf`](https://github.com/opensiro/vsm-harness-index/blob/46219bf103b0b122d86abc3ca70ae3d8bc820e2c/assessments/co/codeact.md); assessed and current first-party `xingyaoww/code-act@d607f56c9cfe9e8632ebaf65dcaf2b4b7fe1c6f8` (same default-branch head at screening).
- Hypothesis predicted **before** fresh code inspection: [Upstream commit `441d7675`](https://github.com/opensiro/upstream/commit/441d7675fa42499db6d528f9dbef0bf718a9a503), frozen in batch 22. The later `91e316bc` correction changed only another source's review-ref transcription.
- First-party path: [`scripts/chat/code_execution/api.py`](https://github.com/xingyaoww/code-act/blob/d607f56c9cfe9e8632ebaf65dcaf2b4b7fe1c6f8/scripts/chat/code_execution/api.py), actual `ExecuteHandler.post`; backend gateway/kernel constructors are stubbed by the test to avoid Docker and agent/model execution.
- [Native regression patch](native-regression.patch) SHA-256 `9265f2da99a4edba0d690bb152d894157f51ede0a94978b716c3be2adc78adf6`.
- [Native production fix patch](native-fix.patch) SHA-256 `11afa4ea02e7c1107a8e1e77ca7333951dfa627e251c3057b6fb854633c99430`.
- Both patches downloaded by **exact Upstream commit** [`ac1bb234`](https://github.com/opensiro/upstream/commit/ac1bb2345d5be31be3570ffc9635e9e01b6f3c20) and independently SHA-256 verified. [Pinned runner script](run-native.sh) at [`f20a8751`](https://github.com/opensiro/upstream/commit/f20a8751992f258a283fcdcd1cc7bd0b10d1412c), SHA-256 `bccba89d92a3c9c74f166e9749098ddf1a610328a46c51033a552f81275b36b0` matched independently on the host.

## Distinct runner identity and environment

- `dev-alpha-2` device: `Zhdanov's Siro VM (vsmforge)`, SSH device ID `8493ff56-7ee6-4d0a-afe1-d2cdebc3456a`; a **separately executed, monitored server command**, not a test in the chatbot's local scratch interpreter.
- Session: `7c40d6d9-65a4-454e-b0ca-6d6e2b1668ac` (`opensiro-b22-codeact-native-redgreen`), 2026-11-09 16:55:27–16:55:50 UTC, final exit `0`, 59 retained monitoring lines.
- Execution and logs retained at `/tmp/opensiro-b22-codeact-OaTygDzt` on the host (`baseline.log`, `after.log`, exact patch copies). Host logs are connector-session evidence and are **not** publicly mirrored at a durable URL; treat retention as host-dependent.
- Linux, Python 3.12.3, isolated venv `tornado==6.5.2`; exact source clone HEAD asserted; no model/Browser, real Docker daemon, live Jupyter kernel, Kubernetes or provider request.

## Matched native source-path observations

1. **Baseline (regression patch only):** `python -m unittest discover -s scripts/chat/code_execution -p test_api_concurrency.py -v` exited **1**; **2 tests, 1 PASS, 1 FAIL**. Two concurrent HTTP POSTs with the same previously unseen `convid` both entered first-kernel initialization; first-party `ExecuteHandler.post` created **two distinct gateways**. Exact assertion: `2 != 1 : concurrent first requests must not create two gateways`. Independent different-conversation parallelism control PASS.
2. **After (same regression, plus production patch):** the **identical command** exited **0**; **2 tests, 2 PASS**. Coalesced same-conversation creation into one awaited in-flight task; independent conversation initialization remained parallel. The fix also closes the gateway after failed initialization and shields a peer's setup from an HTTP waiter cancellation, but those error cases were **not separately measured** in this run.
3. **Additional hygiene:** `python -m compileall -q` on `api.py` and regression file PASS; `git diff --check` PASS; only original native `api.py` and new `test_api_concurrency.py` changed in the first-party checkout. Patches were applied with `git apply --check` and actual `git apply`.

## Claim boundary and continuation

The before/after was executed by a distinct deterministic host against the first-party handler. The backend is deliberately stubbed; the test does not prove Docker name collision behavior, full native suite success, cross-process coordination, an end-to-end deployed service result or a change in VSM decision ownership. The four native-fit gates for this *bounded same-conversation first-start* issue pass. The case can be `ASSESSMENT_DERIVED / AWAITING_EXTERNAL` as an **internal technical handoff** only. Upstream #6 retains the separate fork/branch/external-PR stage gate.
