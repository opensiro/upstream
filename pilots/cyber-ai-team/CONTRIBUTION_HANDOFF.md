# Cyber AI Team — nonfinite or negative policy-envelope numbers admitted

**Stage:** `AWAITING_EXTERNAL`. Bounded source-only patch and tests; no external fork, upstream PR, business action or live agent/service run.

- **Frozen source:** `Hyper-AI-Lab/cyber-ai-team@525401e40f34863cc7f4d3b053d437ce7709912f` (MIT), included `S1=A` Index `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`. The assessment places the first-party owner policy/action envelope at this boundary; exact numeric admission failures came from source inspection, not an autonomy-score inference.
- **Need — PASS:** `ActionPolicyService.normalize_envelope` accepted `NaN`/infinite confidence or financial amounts, negative financial exposure and negative recipient counts. Numeric comparisons in `_hard_gate_reasons` do not reliably bound `NaN` (e.g., `nan < threshold` is false); a nonfinite value can therefore skip part of the policy guard.
- **Mechanism — PASS:** Fail input normalization on nonfinite or out-of-range confidence, nonfinite/negative exposure amounts or negative recipient counts, while preserving valid finite inputs and existing gate thresholds.
- **Counterfactual — PASS (bounded):** Five native `unittest` cases exercise the *exact first-party function body extracted from its source Python AST*, with one valid control and four malformed-number groups (five failed subcases). Before: **1 PASS / 4 FAIL** with two failed confidence subcases. After: **5 PASS / 0 FAIL**.
- **Scope — PASS:** `backend/src/cyber_team/operations/action_policy.py` and one test. AST extraction avoids loading unrelated ORM/OPA/provider imports; it does not replace or mock the first-party function body. No DB, Redis, OPA, ERPNext, Temporal, LLM, model-response simulation or external side effects.

## Verification

| Command | Result |
| --- | --- |
| `python3 -m unittest -q backend.tests.test_native_action_policy_envelope_unittest` before | 1 PASS / 4 FAIL (5 malformed subcases) |
| Same command after | 5 PASS / 0 FAIL |
| `python3 -m py_compile ...`; `git diff --check`; `git apply --reverse --check` | PASS |
| Full backend integration, live OPA/DB or model execution | **Not run / not claimed** |

**Exact tested patch:** [nonfinite-policy-envelopes.patch](nonfinite-policy-envelopes.patch), SHA256 `6beaf41f846357c27b36c1f825409f9a0b385d31544ec9ee0e590f59b035b773` (exact byte match to pinned checkout diff).

**Limits:** Proves correctness of Python normalization only, not end-to-end deployment hardening, policy-decision accuracy with OPA or any agent capability. External upstream submission stays human-owned. Generic `continue` advances to OniRoute.
