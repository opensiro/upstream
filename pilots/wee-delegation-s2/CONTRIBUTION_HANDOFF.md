# Wee-Orchestrator S2 — remove temporary delegation identity on dispatch failure

**Batch:** [Upstream upgrade 23](../../data/assessment-candidate-batches/2026-11-10-23.json), [#56](https://github.com/opensiro/upstream/issues/56). **Status:** internal `ASSESSMENT_DERIVED / AWAITING_EXTERNAL`; external publication **not executed**.

## Prospective prediction and verified mechanism

- [Included Wee assessment](https://github.com/opensiro/vsm-harness-index/blob/46219bf103b0b122d86abc3ca70ae3d8bc820e2c/assessments/we/wee-orchestrator.md): S1=A/S2=C, exact assessed first-party source [`4f34d573`](https://github.com/leprachuan/Wee-Orchestrator/tree/4f34d5737910098c79f2ee42d0f3f383cfca830f). The [S2 hypothesis](https://github.com/opensiro/upstream/commit/02b24e372aa5f6158e6c37623626e17bc104b181) was committed before fresh source inspection.
- [`SessionManager._execute_with_context`](https://github.com/leprachuan/Wee-Orchestrator/blob/4f34d5737910098c79f2ee42d0f3f383cfca830f/agent_manager.py) retains a unique ephemeral `delegation_...` session map entry until *after* `_dispatch_single_runtime` returns. If dispatch raises, cleanup is skipped; normal-case tests do not cover this exception.
- [Fix](native-fix.patch): wrap dispatch in `try/finally` and keep the existing best-effort cleanup only for ephemeral identities. [Regression](native-regression.patch): native `SessionManager` test injecting a failing delegated runtime, requiring the temp key to be absent and the caller's agent untouched.

## Native-fit assessment

| Gate | Result | Bounds |
| --- | --- | --- |
| `need` | **PASS** | Exact first-party test demonstrated a retained `delegation_<uuid>` key on dispatch failure. |
| `mechanism` | **PASS** | Move existing removal into the exception-safe `finally` path; preserve original caller. |
| `counterfactual` | **PASS** | Separate runner matched baseline **11/12** then patched **12/12**. |
| `scope` | **PASS** | Two-file GPL-3.0 source/test patch; no model/provider/browser/external PR. |

See [independent host receipt](INDEPENDENT_HOST_RECEIPT_2026-11-10.md) for source/patch hashes, session identity and pytest results. The cleanup remains best-effort when storage itself fails; this change only handles failures from the runtime dispatch path.

## External boundary

No upstream fork, publication or maintainer agreement is claimed. The separate [Upstream #6](https://github.com/opensiro/upstream/issues/6) publication gate must be satisfied before a new third-party PR. Recheck the then-current target, GPL-3.0 terms and contribution guidelines; the full native suite was not executed. This correctness fix does not automatically raise Index S2=C.
