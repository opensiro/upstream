---
candidate_id: IMPR-AGENT-S-CLI-ACTION-20261021
state: PARKED
origin_class: ASSESSMENT_INFORMED
target_repo: simular-ai/Agent-S
index_sha: 5393b698bfdfa4ca14d97a79238234eca20694e5
assessment_path: assessments/ag/agent-s.md
review_ref: 3aa272d23d2994c7bbde1acbbe0ef8e8d06b8693
source_sha: 15776a8dc659658b1963816ea006f7af1978e595
fit_need: PASS
fit_mechanism: PENDING
fit_value: PENDING
fit_scope: FAIL
---

# IMPR-AGENT-S-CLI-ACTION-20261021 — distinguish terminal action signals from typed task text

**State:** `PARKED / ASSESSMENT_INFORMED`, blocker `BLOCKED_DUPLICATE_OPEN_PR`, **not an Index-diagnosed S1 defect**. The [Agent-S Index assessment](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ag/agent-s.md) identifies the shipped Agent S3 CLI with screenshot-driven actions and feedback, but does not specifically diagnose substring-based terminal action control.

## Product-native need

[Upstream issue #235](https://github.com/simular-ai/Agent-S/issues/235) reports that the shipping S3 CLI uses substring searches for `done`, `fail`, `next`, `wait` in the **entire generated Python code**, so normal user text such as “All done, thanks!” can be misinterpreted as a task completion rather than passed to `agent.type`. The reporter also documents a minimal OSWorldACI-derived code example and says a patch is being prepared. The existing [`gui_agents/s3/cli_app.py` at current source](https://github.com/simular-ai/Agent-S/blob/15776a8dc659658b1963816ea006f7af1978e595/gui_agents/s3/cli_app.py) still contains the specific `if "done" in code[0].lower() or "fail" in code[0].lower()`, `if "next" in ...`, `if "wait" in ...` branches before `exec(code[0])`. The same issue reports a similar older S2.5 CLI pattern, but this candidate concerns **the presently shipped Agent S3**.

## Falsifiable intervention hypothesis

Use the action's **typed terminal status** (`DONE`/`FAIL` as established by the existing OSWorldACI contract) instead of looking for keywords in arbitrary code/arguments. Preserve legitimate `type`, `open` and sleep action behavior; avoid reinterpreting model-generated executable text as a safe structured protocol without actual producer guarantees.

## Four native fit gates

| Native gate | Verdict | Evidence |
| --- | --- | --- |
| Need | `PASS` | First-party open issue #235 and current executable CLI substring branches |
| Mechanism | `PENDING` | Confirm exact status representation, S3/S2.5 differences and avoid overlap with reporter's planned patch |
| Counterfactual benefit | `PENDING` | No current-source baseline test with a generated typed code string and matched after test |
| Scope | `FAIL` | First-party [PR #236](https://github.com/simular-ai/Agent-S/pull/236) is open and implements exactly the typed-text vs terminal-action distinction for the S3 and S2.5 CLI paths. |

**2026-10-23 duplicate resolution:** first-party [PR #236](https://github.com/simular-ai/Agent-S/pull/236) is already OPEN against `main`, supplies exact terminal-action comparisons in both CLIs, and reports native regression tests. Do not send a competing fix or count that PR as OpenSiro authorship. `PARKED / BLOCKED_DUPLICATE_OPEN_PR`; no new source, tests, fork or external PR created by OpenSiro for this candidate. Upstream merge and deployed effect remain unverified.
