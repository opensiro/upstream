# Revka — validate deep workflow DAGs without recursion overflow

**Status:** bounded native first-party validator patch, `ASSESSMENT_INFORMED` / `AWAITING_EXTERNAL`. External publication rights remain human-owned; no external issue, fork or PR was written.

## Source and problem

- Frozen `included S1=A` assessment: `assessments/re/revka.md` in Index `396a54bb690f8ec7ce966bf9b00b241b30036307`, reviewed `2026-10-18`.
- Pinned upstream: `KumihoIO/Revka@a1acd826502e12a6c2f3d147e488a7d2982c480b`, first-party [operator-mcp workflow validator](https://github.com/KumihoIO/Revka/blob/a1acd826502e12a6c2f3d147e488a7d2982c480b/operator-mcp/operator_mcp/workflow/validator.py), `_check_cycles()` and `validate_workflow()`.
- The recursive DFS in the topological sort exceeded Python's recursion limit on a valid deep DAG when the workflow definition listed downstream steps before dependencies. At 1200 steps it raised `RecursionError` instead of returning the `ValidationResult` promised by its interface.

## Native before/after proof

```shell
PYTHONPATH=operator-mcp python3 -m unittest discover -s operator-mcp/tests -p test_workflow_validator_deep_dag_native.py -v
```

Pydantic constructed the actual `WorkflowDef` and `StepDef` objects, with static `StepType.NOTIFY` and synthetic dependency edges. **No workflow execution**, no agent, provider, MCP, model, simulator, shell tool or network operation.

| Test | Before | After |
| --- | --- | --- |
| 1200-step valid descending DAG | ERROR `RecursionError` | PASS, all 1200 steps |
| Four-step ordinary chain | PASS | PASS |
| Four-step dependency cycle rejected | PASS | PASS |
| Two roots and one join | PASS | PASS |

**Before: 3 PASS / 1 ERROR. After: 4 PASS / 0 ERROR.** Patch applied to the actual source tree; `git apply --reverse --check` and `git diff --check`: PASS. Wider upstream pytest tests cannot be attested here because the `pytest` module is unavailable in this environment; do not label that an upstream regression.

## Bounded correction

- [`workflow-deep-dag-validation.patch`](workflow-deep-dag-validation.patch), SHA256 `61c63244a659849c4c25adee79eb1d6abc4ee859eff906069284579365fb82e5`.
- Changes only `_check_cycles()` from recursive DFS to equivalent explicit-stack DFS. Preserves cycle rejection and dependencies-first order without increasing global recursion limits.
- Risk: altered graph-traversal implementation, despite bounded same-function scope. Maintainer should run native full graph tests with its Python CI dependencies. Rollback: reverse the patch.
- No matching recursion-depth PR found in narrow GitHub PR search; still check current issues and maintainers' contributor policy before independently authorized external publication.
