# Wee-Orchestrator S2 — separate native runner receipt (2026-11-10 UTC)

**Result:** bounded first-party pytest demonstrated orphaned ephemeral delegation identity on the original source and verified cleanup after source-native fix. **RED 11/12 → GREEN 12/12**. No real LLM, delegated provider or live session network was exercised.

## Pinned inputs

- Assessment: [Wee-Orchestrator Index S1=A/S2=C](https://github.com/opensiro/vsm-harness-index/blob/46219bf103b0b122d86abc3ca70ae3d8bc820e2c/assessments/we/wee-orchestrator.md).
- Prediction first committed in [Upstream `02b24e37`](https://github.com/opensiro/upstream/commit/02b24e372aa5f6158e6c37623626e17bc104b181), before code inspection.
- First-party source: [`leprachuan/Wee-Orchestrator@4f34d5737910098c79f2ee42d0f3f383cfca830f`](https://github.com/leprachuan/Wee-Orchestrator/tree/4f34d5737910098c79f2ee42d0f3f383cfca830f); runner asserted full Git SHA equal to clone HEAD.
- [Production fix](native-fix.patch), SHA-256 `786384caf62ef03822e91629c7ff40f79c26a83880bafaf5f4ebc398ce59627b`.
- [Regression-only patch](native-regression.patch), SHA-256 `301485c5e6225e520c88007fbb34a945945167563682eff65c39e2bc1c6ca6b6`.
- Runner fetched the corrected patches from the then-current `research/upstream-upgrade-batch-23-20261110` branch. SHA-256 identifiers record exact executed contents; branch was mutable during packet construction.

## Separate executor

- **Machine:** `dev-alpha-2` registered Zhdanov's Siro VM, SSH device `8493ff56-7ee6-4d0a-afe1-d2cdebc3456a`, distinct from the chatbot's local scratch session.
- **Monitored session:** `f540ff69-d09f-4249-9b0a-37505e1e0d03`; 2026-11-10 14:19:20–14:19:30 UTC; completed with **exit 0**, 43 output lines.
- **Working checkout:** `/tmp/opensiro-b23-wee.3bwXSt/wee`, packet checkout `/tmp/opensiro-b23-wee.3bwXSt/upstream`; temporary host retention only.
- **Tools:** Linux, Python 3.12.3, pytest 7.4.4, git 2.43.0. `SessionManager._dispatch_single_runtime` was mocked to raise `RuntimeError`, not connected to a real agent/provider.

## Matched source-native replay

1. Assert source HEAD; SHA-256 both patches; `git apply --check` and apply regression-only patch.
2. `PYTHONPATH=src python3 -m pytest -q tests/test_delegation_session_isolation.py` → **exit 1**: `11 passed, 1 failed in 0.52s`. New `test_failed_delegation_cleans_up_ephemeral_identity` failed: a `delegation_<uuid>` key remained beside the original caller session.
3. `git apply --check` and apply production fix patch; rerun the **same** test file → **exit 0**: `12 passed in 0.47s`. It asserted caller `agent=orchestrator` remained intact.
4. `git diff --check` → PASS; independent session output ended `INDEPENDENT_MATCHED_RED_GREEN=PASS`.

Only `agent_manager.py` and `tests/test_delegation_session_isolation.py` changed in the target checkout. This test proves one exception-path cleanup effect, not complete cancellation semantics, durable storage failure handling, end-to-end provider reliability, maintainer adoption or S2 grade change.
