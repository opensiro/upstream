---
candidate_id: IMPR-AGENCY-SWARM-TRACE-ENDPOINT-20261021
state: SCREENING
origin_class: ASSESSMENT_INFORMED
target_repo: VRSEN/agency-swarm
index_sha: 5393b698bfdfa4ca14d97a79238234eca20694e5
assessment_path: assessments/ag/agency-swarm.md
review_ref: 853d37b9b243edc5dfe2ff2d2d4658aa8ec9a750
source_sha: a86d657e12b693be64a8dcb8ead560a7b9a4ef01
fit_need: PASS
fit_mechanism: PENDING
fit_value: PENDING
fit_scope: PENDING
---

# IMPR-AGENCY-SWARM-TRACE-ENDPOINT-20261021 — prevent unexpected trace egress with overridden model endpoint

**State:** `SCREENING`, `ASSESSMENT_INFORMED`, **NOT** assessed S2/S3*/S5 defect. The Index [Agency Swarm assessment](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ag/agency-swarm.md) maps model/tool-running S1 and optional supporting tracing/guardrail infrastructure but does **not** identify trace transmission to a different provider. The concrete product problem comes from independent [open upstream issue #828](https://github.com/VRSEN/agency-swarm/issues/828), encountered in a source-first sweep, and is **not** retroactively attributed to the Index.

## Native behavior and impact

With `OPENAI_BASE_URL` or agent `base_url` overridden for local/model proxy use, issue #828 reports model calls reaching the configured endpoint but trace spans still being sent to `api.openai.com` using `OPENAI_API_KEY`. Root cause is reported in the downstream `openai-agents` dependency's hardcoded `BackendSpanExporter`; an upstream SDK report exists separately. The first-party code search found explicit `OPENAI_BASE_URL` checks in Agency Swarm provider/hosted-tool adapters and `OPENAI_AGENTS_DISABLE_TRACING` in selected tests, but **no comprehensive native tracing egress audit or current-version runtime reproduction has been executed**.

The native risk is unintended egress of trace metadata and confusing credentials/401 when users intend a local provider; this does **not** demonstrate exfiltration of prompts in the absence of captured outbound packets.

## One falsifiable improvement hypothesis

For an explicitly overridden non-default model endpoint, default SDK platform tracing **off** unless the user intentionally opts into it; preserve documented OpenAI tracing opt-in and make the behavior observable in tests. Alternatively route exporter to an explicitly selected trace collector if the SDK supports it. Do not silently change model endpoints, disable all telemetry unconditionally or assume environment override implies user consent to remote tracing.

## Four native fit gates

| Native gate | Verdict | Evidence |
| --- | --- | --- |
| Need | `PASS` | Reproducible symptom and user-facing impact described by first-party issue #828 |
| Mechanism | `PENDING` | Precedence of env override, per-agent base URL and explicit trace opt-in not proven |
| Counterfactual benefit | `PENDING` | No isolated HTTP egress assertion before/after on current SDK |
| Scope | `PENDING` | Dependency's tracing ownership, compatibility and existing upstream SDK fix must be checked |

**Baseline:** reported issue, current source only partly corroborating, `NOT_RUN` for actual egress. **After:** `NOT_IMPLEMENTED / INCONCLUSIVE`. **Next gate:** isolated fake endpoint and mocked HTTP tracing exporter; assert no requests to unexpected hosts except intentional opt-in, while preserving normal configured tracing. No third-party issue/PR/fork or code was created.
