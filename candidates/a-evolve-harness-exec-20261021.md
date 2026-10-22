---
candidate_id: IMPR-A-EVOLVE-HARNESS-EXEC-20261021
state: SCREENING
origin_class: ASSESSMENT_INFORMED
target_repo: A-EVO-Lab/a-evolve
index_sha: 5393b698bfdfa4ca14d97a79238234eca20694e5
assessment_path: assessments/a-/a-evolve.md
review_ref: 18ba996dac9843f2759b2cdf8a94022f58fbfeb9
source_sha: 18ba996dac9843f2759b2cdf8a94022f58fbfeb9
fit_need: PASS
fit_mechanism: PENDING
fit_value: PENDING
fit_scope: PENDING
---

# IMPR-A-EVOLVE-HARNESS-EXEC-20261021 — isolate execution of proposer-mutated harness

**Research state:** `SCREENING`. Origin is **ASSESSMENT_INFORMED**, not strictly `ASSESSMENT_DERIVED`. The [accepted Index assessment](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/a-/a-evolve.md) shows S4=A evolution of persistent workspaces, but does **not** identify `harness.py` module-scope execution or a bypass of the validation gate. The exact product problem came from first-party code and [pre-existing upstream issue #28](https://github.com/A-EVO-Lab/a-evolve/issues/28) discovered during this Index-first six-function sweep.

## Concrete native problem and current-source observations

[Issue #28](https://github.com/A-EVO-Lab/a-evolve/issues/28) documents a bounded, local-only reproduction where syntactically valid proposer-written workspace `harness.py` passes the candidate validator, then executes Python module-level code in the containing A-Evolve process when loaded. Its source-linked report is at an older commit; a fresh check of current target default `main@18ba996dac9843f2759b2cdf8a94022f58fbfeb9` confirms:

- [`agent_evolve/algorithms/meta_harness/engine.py`](https://github.com/A-EVO-Lab/a-evolve/blob/18ba996dac9843f2759b2cdf8a94022f58fbfeb9/agent_evolve/algorithms/meta_harness/engine.py) `MetaHarnessEngine._validate_candidate` checks `harness.py` and tool files with `compile(..., "exec")` only. That establishes syntax, not runtime provenance, import-time effects or capability constraints.
- The same engine invokes its proposer through the Claude Code CLI with `--dangerously-skip-permissions`, `cwd=workspace_root`. This is a developer-chosen execution mode, not evidence of a remote exploit.
- [`agent_evolve/protocol/base_agent.py`](https://github.com/A-EVO-Lab/a-evolve/blob/18ba996dac9843f2759b2cdf8a94022f58fbfeb9/agent_evolve/protocol/base_agent.py) `_load_harness` calls `spec.loader.exec_module(module)`, executing module-level Python in the loader's process.

**Native effect of interest:** prevent untrusted/evolved `harness.py` from gaining unintended privileges of the evaluator/parent process while preserving the intended user-authorized hook functionality. This is conditional local hardening. Do not call it a demonstrated remote attack or a proven prompt-injection exploit.

## Proposed bounded intervention and falsifier

Candidate **mechanism to evaluate**, not yet a patch: define an explicit trust contract for dynamically loaded workspace hooks. Compare strict rejection of unauthorised module-level operations versus process isolation for candidate evaluation, with structured hook outputs and no silent direct import into a privileged evaluator. The least intrusive viable fix depends on native maintainer requirements, runtime environment, import semantics and performance.

**Falsifier:** existing documented modes may explicitly treat mutated `harness.py` as fully trusted arbitrary Python, in which case an isolation retrofit may not align with the product contract. A `compile()`/AST-only restriction is **not** equivalent to safe sandboxing. An isolation patch is not acceptable if it breaks legitimate tools/hooks or claims security without a real capability boundary.

## Four native fit gates

| Native gate | Declared status | Support |
| --- | --- | --- |
| Need | `PASS` | Specific open upstream issue #28 with minimal canary reproduction; current first-party code retains the reported validation-vs-execution path |
| Mechanism | `PENDING` | Sandboxing/trust model and correct API boundary not decided or implemented |
| Counterfactual benefit | `PENDING` | Reproduction on current commit and before/after adversarial + legitimate-hook tests not yet run |
| Scope | `PENDING` | Maintainer acceptance, intended trusted-code contract, perf/UX and overlapping upstream PRs need fresh review |

## Measurements, status, next gate

- **Baseline:** first-party issue has a demonstrated canary at its own pinned commit; I inspected current `main` code but **did not reproduce the scenario on the current binary/environment**.
- **After:** `NOT_IMPLEMENTED`; effect `INCONCLUSIVE`. A successful test must demonstrate a concrete capability containment property while retaining supported evolution workflows.
- **Candidate vs contribution:** no OpenSiro external issue, fork, patch, or PR created. The existing upstream issue belongs to its original author.
- **Next falsifiable check:** isolated current-source harness-loading reproduction, current-mode trust policy and regression test matrix; escalate to an external maintainer design question before attempting a disruptive sandboxing patch. The native maintainer retains design authority.

This may be useful regardless of whether the target adds S3/S3* or changes any Index grade. It **must not** be counted as strict Index-derived S4 diagnosis in [Upstream #56](https://github.com/opensiro/upstream/issues/56).
