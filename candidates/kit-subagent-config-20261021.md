---
candidate_id: IMPR-KIT-SUBAGENT-CONFIG-20261021
state: SCREENING
origin_class: ASSESSMENT_INFORMED
target_repo: speakeasy-api/kit
index_sha: 5393b698bfdfa4ca14d97a79238234eca20694e5
assessment_path: assessments/ki/kit.md
review_ref: 3fd1fd5fda269569ceba0c2dd884c988d31f53d0
source_sha: 8f9f08a2b2088381f1cb106dcb9129378f8f0b4e
fit_need: PASS
fit_mechanism: PENDING
fit_value: PENDING
fit_scope: PENDING
---

# IMPR-KIT-SUBAGENT-CONFIG-20261021 — recover from partial subagent configuration

**Candidate state:** `SCREENING`; not qualified, approved, implemented, or published.
**Origin class:** `ASSESSMENT_INFORMED`, **NOT** `ASSESSMENT_DERIVED`.
**Target:** [speakeasy-api/kit](https://github.com/speakeasy-api/kit); current default `main@8f9f08a2b2088381f1cb106dcb9129378f8f0b4e` inspected 2026-10-21.
**Canonical Index:** [Kit included assessment at immutable Index 5393b698](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ki/kit.md), assessed `3fd1fd5fda269569ceba0c2dd884c988d31f53d0`. The assessment covers a supported first-party optional subagent/ACP subsystem; it **does not find** this config-startup bug, nor classify it as a specific S2 gap. This card's screening **began from Index before reviewing this issue**, but the exact native defect comes from independent first-party issue/code evidence, not from the assessment.

## Native product need (not a VSM grade repair)

[Open Kit issue #222](https://github.com/speakeasy-api/kit/issues/222), filed 2026-09-14, describes a user whose partial `~/.kit/config.toml` config contains nested `[subagent.harnesses."acp.claude".models]` data but no `subagent.harness`. It reports `kit acp` exiting before startup because config deserialization requires the missing field. This can lock users out of the agent until they manually repair the config. The issue includes a minimal reproduction and asks for safe fallback/actionable warning.

Current first-party [`src/main.rs@8f9f08a2`](https://github.com/speakeasy-api/kit/blob/8f9f08a2b2088381f1cb106dcb9129378f8f0b4e/src/main.rs) still declares:

```rust
#[derive(Debug, Deserialize)]
struct SubagentConfig {
    harness: String,
    #[serde(default)]
    harnesses: BTreeMap<String, kit::SubagentHarnessPolicy>,
}
```

The required `harness` field is **consistent with the reported failure**; the current full `kit acp` command has **NOT** been executed in a controlled environment for this card, so regression is not yet independently demonstrated on the current binary. The issue remains open; no matching fix PR was verified in this bounded check. Recheck duplicate fixes/branches before doing implementation.

## One bounded intervention hypothesis and falsifier

**Hypothesis:** treat a present-but-partial optional subagent configuration as a recoverable configuration error: keep the main agent startable, disable only the misconfigured subagent path, and emit an actionable warning that names the missing `subagent.harness` field. Do not silently choose another child backend or expose a new execution/permission path.

**Falsifier/risks:** a broad deserialization fallback could hide malformed essential config, silently change model/harness selection, or break intentionally strict CLI policy. The intended fallback policy, error surface and refusal behavior need maintainers' agreement or unequivocal documented first-party requirement. Do not simply make `harness` optional and silently pick an arbitrary value.

## Four native fit gates

| Gate | Verdict | Native evidence |
| --- | --- | --- |
| Need | `PASS` | Detailed [first-party open issue #222](https://github.com/speakeasy-api/kit/issues/222) with a concrete reproducible report; current source remains structurally compatible with the missing-field error |
| Mechanism | `PENDING` | Safe, narrow startup recovery and warning behavior not yet implemented or verified |
| Counterfactual benefit | `PENDING` | No matched fresh-main before/after startup test, regression test or preservation-of-config behavior yet |
| Scope | `PENDING` | Contribution tests/policy, current PR/branch overlaps and acceptable recovery semantics need final confirmation |

## Test/effect vs contribution

- **Baseline:** `ISSUE_REPRODUCTION_DOCUMENTED`, current source inspected; **not** `CURRENT_MAIN_EXECUTED`. Re-run the exact supplied TOML fixture with `kit acp` inside a temporary isolated `HOME`, capture stderr/exit status, and confirm no credential or real session side effects.
- **After:** `NOT_IMPLEMENTED` / `NOT_MEASURED`.
- **Safety checks:** correct missing-field warning; independent ordinary sessions remain usable; no implicit subagent start or unapproved backend selection; malformed mandatory settings still fail as appropriate.
- **Product effect:** `INCONCLUSIVE`. A real repaired startup regression, not changed VSM status, would define success.
- **Upstream fork/patch/issue/PR:** no action taken by OpenSiro for this candidate. Existing external Kit #222 predates this work and is not an OpenSiro contribution.
- **Next gate / decision owner:** local, current-main source-native reproduction and inspection of Kit's contribution/running commands under its first-party `AGENTS.md`; if reproduced, confirm compatible recovery semantics before a scoped patch. The external maintainer retains implementation/merge authority.

This candidate **does not** count toward [strict assessment-derived experiment #56](https://github.com/opensiro/upstream/issues/56) as a newly discovered S2 deficit. It belongs in the separate improvement pool precisely so an independently useful issue can be pursued without corrupting Index-to-mechanism attribution.
