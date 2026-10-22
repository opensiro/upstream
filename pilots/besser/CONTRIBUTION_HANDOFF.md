# BESSER — automatic transitions should be exclusive in both registration orders

**Stage:** `AWAITING_EXTERNAL`. Tested first-party native patch. No external fork/issue/PR, LLM model, NLP intent classifier, state-body execution or provider call.

- **Frozen source:** `BESSER-PEARL/BESSER-Agentic-Framework@da46d4e2f0ae477704f7cc1108f1f6ec5209530e` (MIT license), included `S1=A` Index `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`. The Index identifies state/transition control; the exact registration-order asymmetry was discovered by inspecting `baf/core/transition/transition_builder.py` and the documented `State.go_to()` invariant.
- **Need — PASS:** `TransitionBuilder.go_to()` rejects a second transition after any auto transition, but the opposite order (`event` or `condition` then `auto`) is accepted. An auto transition is documented as exclusive, so declaration order must not change the validity of the same transition set.
- **Mechanism — PASS:** Reject registration of a new auto transition if the source already has *any* transition, preserving the existing rejection when an auto transition is already present and standard single transition registrations.
- **Counterfactual — PASS:** Seven native `unittest` cases compile unchanged first-party `Transition`, `TransitionBuilder` and exception classes against fixed lightweight state registry records. **5 PASS / 2 FAIL** before; **7 PASS / 0 FAIL** after. No running `Agent`, model, state body, NLP configuration, or event stream was created.
- **Scope — PASS:** Only `baf/core/transition/transition_builder.py` plus one native regression script. We test the first-party transition declaration contract, not an inference or interactive agent benchmark. Full upstream agent suite was not run.

## Verification

| Command | Result |
| --- | --- |
| `python3 -m unittest discover -s baf/test/components -p test_native_transition_admission_unittest.py -v` before | 5 PASS / 2 FAIL |
| Same native command after | 7 PASS / 0 FAIL |
| `python3 -m py_compile ...`, `git diff --check`, `git apply --reverse --check` | PASS |
| Agent behavior, model, provider, upstream PR/merge | **Not run / not claimed** |

**Exact tested patch:** [auto-transition-registration-order.patch](auto-transition-registration-order.patch), SHA256 `206efdecf219f4f1b1344516bf245756f6ef626dfd330287cb45ac066b2bf691`.

**Limits:** This enforces a declaration-time consistency rule only. It does not establish agent behavior under any given event ordering, nor acceptance by the external maintainer. External publication is human-owned. Generic `continue` advances to BabyAI.
