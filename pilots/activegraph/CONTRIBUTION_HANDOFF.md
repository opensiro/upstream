# Active Graph — stored event accepts JSON values outside object shape

**2026-10-25 publication review:** [CONTRIBUTING.md](https://github.com/yoheinakajima/activegraph/blob/main/CONTRIBUTING.md) limits unsolicited external code PRs to truly trivial changes that do not alter test expectations. Behavior changes require an issue, maintainer scope agreement and the explicit `status: ready-for-pr` label. This decoder change adds a new regression contract and is not trivial under that definition; no matching gate-approved issue was found. Apache-2.0 license is present, no DCO is required, but the maintainer's pre-approval gate controls. **BLOCKED**; no external PR, issue, fork or fresh test this pass. The older test receipt below is not a current CI result.

**Stage:** `AWAITING_EXTERNAL`. Exact-source native regression patch, no external fork/PR, behavior or model-agent execution.

- **Frozen source:** `yoheinakajima/activegraph@50d8405923b79e4e823a73a3045bb969436a872c` (Apache-2.0), included `S1=A` Index `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`. The Index credits its first-party event-sourced graph and replay. Direct source inspection showed `activegraph/store/serde.py::decode_payload` annotated a dict but returned any syntactically valid JSON value.
- **Need — PASS:** Stored `[]`, `null` and string JSON were decoded as successful event payloads despite the object-shaped event contract. Such data can fail much later during replay or behavior patch access, rather than being rejected at the storage boundary.
- **Mechanism — PASS:** After parsing JSON, reject any root value other than an object via the existing structured `CorruptedEventPayloadError`; nested lists inside a valid object remain allowed.
- **Counterfactual — PASS (bounded):** Five real-source Python `unittest` cases: object roundtrip, invalid syntax, and array/null/scalar roots. Baseline **2 PASS / 3 FAIL**, after **5 PASS / 0 FAIL**.
- **Scope — PASS:** only the genuine `activegraph/store/serde.py` decoder and one native unittest file. No model, recorded-model replay, behavior registration or live agent run. `pytest` not installed in the screening interpreter, so existing pytest suite remains **not run**, not a claim of success.

## Verification

| Command | Result |
| --- | --- |
| `python3 -m unittest -q tests.test_native_event_payload_object_unittest` before | 2 PASS / 3 FAIL |
| Same command after | 5 PASS / 0 FAIL |
| `python3 -m py_compile ...`; `git diff --check`; `git apply --reverse --check` | PASS |
| Existing `python3 -m pytest tests/test_serde.py -q` | Not run: `No module named pytest` |
| Live graph behavior, model or provider | Not run |

**Exact tested patch:** [nonobject-event-payload-rejection.patch](nonobject-event-payload-rejection.patch), SHA256 `6a6a3557e08fbd459a855674e1e6f5e85c3ab4e665c72b46c516edace7367af8`.

**Limits:** Proves rejection of non-object stored JSON payload roots, not full append-only storage corruption recovery, semantic conflict resolution or model task performance. External upstream submission is human-owned; generic `continue` advances to PyFlue.
