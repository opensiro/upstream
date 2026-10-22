# Reins — empty-principal RLS boundary mismatch across language implementations

**Stage:** `AWAITING_EXTERNAL`. Native code/test patch prepared internally; no fork, issue, commit, PR or merge has been made against the external Reins repository.

- **Frozen assessment:** `shamspias/reins@69d5ae7e3f2336366e7567b7a476e7c71608f226` in the canonical included `S1=A` Index revision `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`, not `ASSESSMENT_DERIVED`. The VSM record identifies capability and invocation policy as a relevant code-owned S1 surface. This exact Python RLS bug arose from direct examination of source and Go/TypeScript counterparts.
- **Need — PASS:** Python's `scope_violation()` rejects a scoped action only when `principal is None`; therefore an empty-string principal is accepted for `scope="orders"`. Conversely it rejects missing identity for `scope=""`, although both first-party Go and TypeScript regard empty scope as unscoped and empty principal as unauthenticated. This is a deterministic cross-language permission-contract mismatch.
- **Mechanism — PASS:** treat empty/None scope as unscoped (`if not capability.scope`) and absent/empty principal as unauthenticated (`if context is None or not context.principal`). Preserve the existing error, API and the ability of nonempty scope plus nonempty principal to pass. Do not change access classification, approval callbacks, model loop or scope filtering performed by a capability.
- **Counterfactual — PASS (bounded):** four direct Python `unittest` cases on genuine pinned source: before **2 PASS / 2 RED**, after **4 PASS / 0 FAIL**. The two controls cover normal authenticated scoped use and unauthenticated nonempty scope. The two RED cases cover an empty principal with real scope and empty scope with no principal.
- **Scope — PASS:** two conditional expressions in `packages/python/src/reins/rls.py`, plus a standalone standard-library regression test at `packages/python/tests/test_rls_contract_unittest.py`. No other source change.

## Reproducible native checks

| Check | Result |
| --- | --- |
| `PYTHONPATH=packages/python/src python3 -m unittest discover -s packages/python/tests -p test_rls_contract_unittest.py -v` on pinned baseline | **2 PASS / 2 RED** |
| Same test command after patch | **4 PASS / 0 FAIL** |
| `python3 -m compileall -q` on two changed source/test files | PASS |
| `git diff --check` | PASS |
| `git apply --reverse --check` against patched pinned checkout | PASS |
| First-party pytest test suites, JS/Go tests, integration and agent/provider execution | **Not run / not claimed**; pytest and Go are unavailable on this execution host |

**Exact patch:** [empty-principal-rls-contract.patch](empty-principal-rls-contract.patch), SHA256 `5c886ce7577531f67ac38545ece54e8575fa1d6fe12d4ef231212402d3698eaf`, identical to the tested diff from the frozen Reins checkout. No modifications to the external remote were made.

**Boundaries:** The guard only checks whether a principal identifier is nonempty; it does **not** authenticate it or enforce capability-specific row predicates. The upstream maintainer should run normal pytest plus cross-language conformance/CI before accepting any change. External publication is human-owned; ordinary `continue` immediately advances to CubeLoop instead of waiting for the external PR.
