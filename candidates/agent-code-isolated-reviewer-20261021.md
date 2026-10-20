---
candidate_id: IMPR-AGENT-CODE-ISOLATED-REVIEW-20261021
state: SCREENING
origin_class: ASSESSMENT_DERIVED
target_repo: avala-ai/agent-code
index_sha: 5393b698bfdfa4ca14d97a79238234eca20694e5
assessment_path: assessments/ag/agent-code.md
review_ref: 2734ab5f18939b20c774b39c4406788383e35255
source_sha: 82e0edfa7372c256d893d0854f954d9099254f88
fit_need: PASS
fit_mechanism: PENDING
fit_value: PENDING
fit_scope: PENDING
---

# IMPR-AGENT-CODE-ISOLATED-REVIEW-20261021 — independent coding-result review

**State:** `SCREENING`; **no proposal or code change**.

## Origin and precise observed function gap

A deterministic, Index-first sweep read [agent-code's frozen assessment](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ag/agent-code.md) before checking current upstream issues. It specifically says **S3*=—** because the ordinary coding agent and an optional standalone security-scan result do **not** form an independently owned, source-observing claim-review loop with return into corrective work. This points directly to a *separate, source-inspecting reviewer under the agent coding task*, not to a generic grade-repair or an entirely new S3 controller.

The independent product-native need is already articulated in existing [upstream issue #524](https://github.com/avala-ai/agent-code/issues/524): a fresh-context reviewer with repo tools, target-specific scope, rubric and structured findings that can inform the implementation task. **This issue predates the screen, is upstream-authored evidence, and was not created by OpenSiro.** Link classification is `ASSESSMENT_DERIVED` **at the research hypothesis level only**, not a proven functional upgrade, independent S3* autonomy claim, or completed intervention.

## Fresh product source and narrowing

The target's currently inspected `main@82e0edfa7372c256d893d0854f954d9099254f88` has **already progressed** since the issue's original one-line `/review` report:
- [`crates/cli/src/commands/mod.rs`](https://github.com/avala-ai/agent-code/blob/82e0edfa7372c256d893d0854f954d9099254f88/crates/cli/src/commands/mod.rs) now parses targets, resolves the selected diff and returns `CommandResult::Prompt(format!("{}\\n\\n{}", review::RUBRIC, resolved.prompt))`.
- [`crates/lib/src/review/mod.rs`](https://github.com/avala-ai/agent-code/blob/82e0edfa7372c256d893d0854f954d9099254f88/crates/lib/src/review/mod.rs) contains a review rubric and target infrastructure; the [current changelog](https://github.com/avala-ai/agent-code/blob/82e0edfa7372c256d893d0854f954d9099254f88/CHANGELOG.md) credits #529 for these.
- Therefore **do not propose adding a rubric or target selector again**. The open question is whether the review actually receives **separate context + bounded read-only execution and a labelled structured return**, rather than just a new prompt in the original `QueryEngine` state.

## Proposed smallest useful mechanism

Investigate reusing the existing subagent/task lifecycle for a first-class `Review` task that loads the selected diff in **fresh context**, uses constrained read-only repository tools, and returns structured findings to the parent. Explicitly compare against current review commands and open PRs before claiming this mechanism is missing. A deliberately limited reviewer must not silently obtain approval/write rights.

## Four native fit gates

| Gate | State | Why |
| --- | --- | --- |
| Need | `PASS` | Specific Index S3* claim-gap and native developer issue #524 |
| Mechanism | `PENDING` | First-party rubric/target work already shipped, but exact isolated child-review path and interface need fresh tests |
| Counterfactual benefit | `PENDING` | No paired tests showing genuinely independent findings vs same-context review |
| Scope | `PENDING` | Existing task framework, approvals, current in-flight maintainer implementation and supported UI contract need confirmation |

**Baseline:** source-inspected only, **not** current-binary or model-blinded review trial. **After:** `NOT_IMPLEMENTED / NOT_MEASURED`. Potential product benefit: fewer self-confirming reviews and actionable result packets; do not assert it without measured correctness. **Next step:** inspect current review/task call path, read maintainers' PR discussions and run a deterministic isolated-vs-shared reviewer contract test. Maintainer retains design authority. No external writes or product improvement counted.


**First product-native code-slice checkpoint (2026-10-21):** [Internal Draft PR #69](https://github.com/opensiro/upstream/pull/69) prepares a [source-pinned Rust patch](https://github.com/opensiro/upstream/blob/pilot/agent-code-524-review-subagent-20261021/pilots/agent-code-524/reviewer-subagent-first-slice.patch) adding a built-in `review` type to the existing `AgentTool` subprocess path, with the repository rubric, `read_only=true`, `Plan` mode, a bounded tool list and native definition/child-command tests. This is a **partial native implementation**, not a completed solution to issue #524. It does **not** reroute the current parent-session `/review`, parse structured findings, deliver parent feedback, or prove true system-instruction replacement, no-network sandbox, or measurable review value. The shared existing permissions-overlay helper can fall back on a write failure and disk agent definitions can override built-in types; these are hardening blockers before promotion.

**Source replay:** original `main@82e0edfa7372c256d893d0854f954d9099254f88`; patch SHA-256 `0dfd319e31548af89b751af703f391ba46d57e4dc3846b91fe7b88a3e56d569d`; `git apply --check` and `cargo fmt --all -- --check` PASS on a separate clean checkout. Native Rust unit tests were being compiled with a locally installed toolchain at this checkpoint; **no success is asserted before the test runner completes**. All candidate fit gates other than need remain `PENDING` and state stays `SCREENING`.
