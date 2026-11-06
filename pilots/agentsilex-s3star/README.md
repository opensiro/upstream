# AgentSilex — offline recorded trajectory audit (Improvement pilot)

- **Experiment:** [OpenSiro/upstream #56](https://github.com/opensiro/upstream/issues/56)
- **Kind:** source-native Improvement / assessment-derived candidate, **not** completed external contribution.
- **Index-first hypothesis:** [`assessments/ag/agentsilex.md` at Index `c96243e0768d361ddc8389e3a29998f55ba76c16`](https://github.com/opensiro/vsm-harness-index/blob/c96243e0768d361ddc8389e3a29998f55ba76c16/assessments/ag/agentsilex.md), recognizing a composable S3* evaluator whose independent organizational access/closure comes from the host. Assessment scores are not the proposed feature or metric of success.
- **Exact first-party baseline:** [howl-anderson/agentsilex@`cd529f2838151fd8a4f0d6b7054a45d829b3f78d`](https://github.com/howl-anderson/agentsilex/tree/cd529f2838151fd8a4f0d6b7054a45d829b3f78d), identical to default main at intake.
- **License:** verified original MIT `LICENSE` before implementation.
- **Contributor policy:** root and `.github` checked; no `CONTRIBUTING.md` or issue-assignment prerequisite found. Only internal OpenSiro files were published, no external issue/fork/branch/PR or merge.
- **Duplication:** all 3 entries on the upstream issue channel and 2 PRs (open/closed) inspected; none covers offline recorded audit.

## Native functional difference

Previously `AgentEvaluator.evaluate(eval_set)` always created a `Runner` and executed the operational agent to reconstruct each response/trajectory. An auditor with saved evidence but no authority or credentials to invoke the production agent could not use the public evaluation logic; replay might generate different behavior.

The patch adds `AgentEvaluator(agent=None, evaluators=[...]).evaluate_recorded(golden_set, recorded_by_eval_id)`. The auditor can score separately supplied `DialogTurn` evidence against independent expected data using the existing metric implementations and aggregation, without running `Runner` or any operational agent. The new path validates all case identifiers, exact per-case turn counts, duplicate IDs/metric names, and nonempty criteria before scoring. Existing `evaluate` still uses the normal Runner path.

Select the first-party `ResponseMatchEvaluator(..., metric=SimilarityMetric.EXACT)` and/or `ToolTrajectoryEvaluator` for deterministic provider-free evaluation. An optional LLM-judge metric would, by its own definition, invoke inference and **was not used in this pilot**. Saved evidence is not authenticated, and separately callable audit is **not proof of organizational independence, S3* autonomy, or downstream corrective closure**.

## Reproducible before/after

Environment: Python 3.12, isolated .venv with the project's public `.[evaluation]` dependencies, pytest. No provider calls, model runs or LLM-performance comparison.

- **Before:** new deterministic offline-audit tests **6 FAIL** on pristine source: `AgentEvaluator` lacks `evaluate_recorded`.
- **After:** same tests expanded to 8; focused new tests **8 PASS / 0 FAIL**.
- **After broader allowed native set:** `pytest -q tests/test_recorded_evaluator.py tests/test_runner.py tests/test_utils.py tests/test_extract_function_schema.py` — **25 PASS / 0 FAIL**. Existing runner tests mock inference.
- **Existing suite limitation:** complete `pytest -q tests` has **12 failures** in MCP and observability integration. Exactly the same 12 test failures reproduce on a separate pristine baseline, using the same .venv; baseline code failures are not patch regressions. Never claim the entire test suite passes.
- Python compileall, `git diff --check`, and `git apply --check` against a pristine clone at the pinned SHA: PASS.

## Status and external gate

This is an OpenSiro-internal **technically validated source-only patch**. No external AgentSilex contribution was published. The owner's 34-Case Corrective mandate does not authorize publishing this newly proposed Improvement. Any external submission requires the applicable owner publication decision, first-party current-HEAD/policy refresh, tests/CI and maintainer review; no merge is authorized.

## Apply

From the pinned upstream checkout:

```sh
git apply --check recorded-audit.patch
git apply recorded-audit.patch
python -m pytest -q tests/test_recorded_evaluator.py
```
