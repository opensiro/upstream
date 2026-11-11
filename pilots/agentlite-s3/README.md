# AgentLite — opt-in per-task delegation budget (source-only Improvement pilot)

- **Experiment:** [Upstream #56](https://github.com/opensiro/upstream/issues/56)
- **Type:** Improvement; Index-first `ASSESSMENT_DERIVED` hypothesis, **not a completed external contribution**.
- **Assessment source:** [canonical Index `assessments/ag/agentlite.md` at `c96243e0768d361ddc8389e3a29998f55ba76c16`](https://github.com/opensiro/vsm-harness-index/blob/c96243e0768d361ddc8389e3a29998f55ba76c16/assessments/ag/agentlite.md). S1 workers and manager dispatch are credited, but no first-party whole-system resource-control path (S3) is established. A missing grade is **not** a defect by itself.
- **First-party source baseline:** [SalesforceAIResearch/AgentLite@`b173239a652eea560e57c6fe46b0c0af7c4f3578`](https://github.com/SalesforceAIResearch/AgentLite/tree/b173239a652eea560e57c6fe46b0c0af7c4f3578), the same revision as current default main at intake.
- **License:** Apache-2.0, verified from `LICENSE.txt` before editing.
- **Contributor policy:** root `CONTRIBUTING.md` requires issue-first discussion and maintainer feedback before implementing proposed features upstream; any eventual submission also requires Salesforce CLA. No public proposal, fork, branch or PR was posted to that upstream project.
- **Duplicates:** first-party complete issue/PR collections checked (42 issue-channel entries incl. 25 PRs, 25 PR entries); no matching team-call quota feature discovered.

## Product-native hypothesis and functional change

The existing `ManagerAgent` limits its own loop to 20 turns but has no separate configurable ceiling on **child-agent calls** within one manager task. Cost-sensitive applications may want the caller to cap delegated operations independently of the model's choice of team member.

The proposed `max_team_calls_per_task` option accepts a non-negative integer or `None` (default). In the ordinary `ManagerAgent.execute` path it counts each attempted worker execution, returns an observable budget-exhaustion message before starting the next worker, leaves Finish/other manager actions usable, and resets the counter per task. Task counters are context-local, avoiding accidental sharing across nested or concurrent invocations. The default behavior remains unchanged.

This is **bounded call-count control**, not an end-to-end money/token saving, independent audit, proof of quality improvement or verified S3 autonomy upgrade. The quota does not bound worker latency, worker token usage, direct low-level `forward` calls outside ordinary `execute`, or decisions made by downstream services.

## Native before/after receipt

Environment: local Python 3.12; isolated .venv with `langchain==0.1.3`, `langchain-openai==0.0.5`, `openai==1.10.0`, `pydantic<3`, pytest. Deterministic `ScriptedLLM` outputs text strings only; **no real LLM-agent effectiveness experiments, inference, API call or real provider**.

- **Before** (new tests against pristine upstream `ManagerAgent.py`): **2 PASS, 2 FAIL**. The budget-one scenario invoked the worker twice; negative budgets were silently accepted.
- **After** (same tests with patch applied): **4 PASS, 0 FAIL**. Budget-one dispatches only the first worker and records a budget message; default calls both; quota resets for the next task; negative input rejected.
- Python compileall and `git diff --check`: PASS.
- `git apply --check` of the exact patch against a separate pristine clone at the baseline SHA: PASS.
- Broader `pytest tests` was **not a valid deterministic full-suite result**: the existing `tests/test_llm.py` attempts live provider invocation, prohibited by this pilot, and failed during its unrelated client initialization (`proxies` incompatibility) before any provider request. Do not run that file as part of this experiment.

## Publication state

The source change and tests are present as `max-team-calls-per-task.patch` in this **OpenSiro-internal** pilot only. A separate maintainer issue and feedback, current-source reconfirmation, applicable actor/CLA requirements, native CI, and a distinct external publication mandate are required for an upstream proposal/PR. This pilot is not evidence of maintainer acceptance or an external submission.

## Apply

From an unmodified source checkout at the pinned SHA:

```sh
git apply --check max-team-calls-per-task.patch
git apply max-team-calls-per-task.patch
python -m pytest -q tests/test_manager_delegation_budget.py
```
