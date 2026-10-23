# Evidence Bench — do not admit failed retrieval responses as evidence

**State:** OpenSiro internal source-pinned patch; assessment-linked native behavior improvement; deployed user benefit and external contribution NOT_MEASURED.

- Selected from [frozen Index-first candidate batch 11](https://github.com/opensiro/upstream/blob/main/data/assessment-candidate-batches/2026-10-23-11.json), row `evidence-bench-native-evidence-admission`. Canonical [Index Evidence Bench assessment](https://github.com/opensiro/vsm-harness-index/blob/main/assessments/ev/evidence-bench.md) concerns scientific evidence and independent gating. The exact status-field problem was independently reproduced in the first-party policy.
- First-party: [kstawiski/evidence-gated-scientific-agent@85b396a824dfad6ec0880cbe07d86d3e24920ae8](https://github.com/kstawiski/evidence-gated-scientific-agent/commit/85b396a824dfad6ec0880cbe07d86d3e24920ae8), `main` at check time. Apache-2.0 LICENSE, CONTRIBUTING welcomes narrow deterministic validator and policy fixes. No external PR/issue/fork.
- Patch: [retrieval-error-admission.patch](retrieval-error-admission.patch), SHA-256 `0974cdefa228cfdf37e1b750144e01c269c8f2dee6d9aa8ea01e86dd79b23646`, 2 first-party files.

## Falsifiable native finding

Original `ToolPolicy.after_tool` counted a retrieval with a nonempty `status: error` and no `error` key as successful. It recorded a purported URL from the failed response and could donate this counter to later scientific citation linting. With a fixed negative `query-docs` result carrying `status: error`, a concrete URL in the error message, and no network/tool invocation:

- BEFORE: `successful_calls == 1` and the error-message URL was recorded. New negative test **RED**.
- AFTER: `successful_calls == 0`, URLs/tools/artifacts all empty; ledger records `reported_error: ERROR`. Positive successful response still counts and records the real URL.
- `tests/test_policy.py`: **16 PASS** in Python 3.12 with minimal pytest+pydantic dependencies.
- Clean pinned original checkout + test-only injection reproduces RED; exact production patch gives 16 PASS.
- Adjacent `tests/test_linting.py` cannot be claimed PASS in minimal env because full first-party dependency closure was not installed (missing httpx during collection). No live tests, model calls, or external search were run.

**Scope:** recognize explicit error-like string status values `error`, `failure`, `failed`, `timeout`, `timed_out`, `canceled`, `cancelled`, `policy_denied`. Do not synthesize success/failure from absent status or no response content. This addresses result classification, not remote source authenticity or efficacy of scientific model judgments.

Read-only [CI native replay](../../.github/workflows/evidence-bench-retrieval-admission.yml) freezes the first-party source and exact patch hash, runs expected baseline RED then patched policy suite.

No S5 mandate covers external publication of this new Improvement. It is NOT an external PR, merged upstream patch, product impact result, or Index regrade.
