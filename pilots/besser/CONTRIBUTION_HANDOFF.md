# BESSER — automatic transitions should be exclusive in both registration orders

**Stage:** `SUBMITTED_READY_FOR_REVIEW` on 2026-10-24. [Upstream PR #205](https://github.com/BESSER-PEARL/BESSER-Agentic-Framework/pull/205) from `xLagerFeuer` via public `opensiro-contributions/BESSER-Agentic-Framework` fork. No LLM model, NLP intent classifier, state-body execution or provider call was run.

- **External publication readback:** current upstream base `548fc529c20da7f4342f2f60f847418f149e9340`, head `0f97ff5f1374381f1554be48eb33d339a282c8e0`, two files changed; OPEN / Ready for review, no merge claimed. Earlier pinned source remains a reproducible historic baseline; native tests also reproduced 5/7 → 7/7 against the newer upstream main.

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

**Limits:** This enforces a declaration-time consistency rule only. It does not establish agent behavior under any given event ordering, nor acceptance by the external maintainer. External review and merge remain human-owned. The next frozen candidate is BabyAI.
