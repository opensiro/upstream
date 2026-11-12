# Revka: selected native DAG validator packet (2026-11-12)

## Immutable source and bytes

- Source: `KumihoIO/Revka@a1acd826502e12a6c2f3d147e488a7d2982c480b` (verified current `main`, 2026-11-12).
- Direct public fork: `opensiro-contributions/Revka` at the same `main` SHA (provider REST readback).
- Historical case: `revka-workflow-validation-contract`, frozen `data/assessment-candidate-batches/2026-10-23-10.json`; no mutation to frozen batch.
- Selected two-file patch: `pilots/revka/workflow-deep-dag-validation.patch`, SHA-256 `61c63244a659849c4c25adee79eb1d6abc4ee859eff906069284579365fb82e5`.
- Local `git apply --check`: PASS on source `main` at the exact source SHA.

## Native, offline red/green

A fresh isolated Python 3.12 virtual environment installed `pydantic 2.14.3`, `pytest 9.2.0`, `pytest-asyncio`, and `pyyaml`. With the selected patch applied, revert only the production validator to source `main` to test baseline; restore the patched validator for after-tests. The new regression test file is held identical in both comparisons.

- Baseline: `PYTHONPATH=operator-mcp python -m unittest discover -s operator-mcp/tests -p test_workflow_validator_deep_dag_native.py -v` -> **3 PASS / 1 ERROR**, `RecursionError` on valid descending 1200-step DAG.
- Patched: same command -> **4 PASS / 0 ERROR** (deep DAG, ordinary chain, cycle rejection, two-root join).
- Adjacent source-native suite: `PYTHONPATH=operator-mcp python -m pytest -q operator-mcp/tests/test_workflow_validator*` -> **17 passed**.
- `git diff --check`: PASS. No workflow, agent, model, provider, MCP, network or tool execution was run by tests.
- Full Rust `cargo fmt`, `cargo clippy`, `cargo test`, and full cross-component CI: **not run**; never claim a complete target CI pass.

## Authority and delivery boundary

This selects source-verified local patch bytes for prospective `prepare_contribution` under the separate effective standing preparation mandate. The selection **is not a grant, a legal declaration, external publication or third-party acceptance**. Target `docs/contributing/cla.md` defines PR submission as agreement to copyright and patent terms, originality and employer-rights representations. The owner has **not provided separate contributor-person assent** through the effective OpenSiro mandate, so `submit_external_pr` remains **LEGAL_ATTESTATION_REQUIRED**, notwithstanding the CLA requiring no extra individual signature. No external PR is claimed. Maintain source checks, target PR form, AI disclosure, CI and nonduplicate validation before any future third-party submission.

Classification remains **ASSESSMENT_INFORMED** (not a completed assessment-derived effect).
