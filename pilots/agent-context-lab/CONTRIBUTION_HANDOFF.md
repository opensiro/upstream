# agent-context-lab — default-FAIL evidence contract must fail closed

**Stage:** `AWAITING_EXTERNAL`. This is an internal evidence packet only; no external fork, issue, commit, PR, or merge.

- **Source:** `Qin-sor/agent-context-lab@372ecc514d48d8e1e5f92d672a9c2b16f4826b5d`, pinned from the included `S1=A` Index assessment at `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`, not `ASSESSMENT_DERIVED`. The assessment identifies the default-FAIL verifier and workspace controls; the concrete malformed-evidence acceptance paths were found by this native source screen.
- **Need — PASS:** `DefaultFailVerifier([]).verify(None).passed` returned `True` with no configured evidence. A single `Evidence.check` returning `("False", "...")` or `(1, "...")` also passed because the verifier relied on Python truthiness instead of a literal positive `True`. Both are false acceptance of insufficient or invalid script evidence.
- **Mechanism — PASS:** fail with a category C missing-process-evidence record if no checks are configured, and treat `ok is not True` as unsuccessful, preserving existing exception rejection and true/false boolean behavior. No agent, model, prompt, workspace-tool or policy bypass code changed.
- **Counterfactual — PASS (bounded):** six new direct `unittest` cases exercise the real shipped `harness.verifier` implementation without `run_task`, `MockLLM`, or provider access: **3 PASS / 3 RED before**, **6 PASS / 0 FAIL after**. The fix is bounded to the verifier API's evidence interpretation.
- **Scope — PASS:** one conditional and an empty-check-list gate in `harness/verifier.py`, plus `test_verifier_contract_unittest.py`; local external source remains uncommitted and unpushed.

## Native checks and limitations

| Check | Result |
| --- | --- |
| `python3 -m unittest -v test_verifier_contract_unittest` before patch | **3 PASS / 3 RED** |
| Same direct script tests after patch | **6 PASS / 0 FAIL** |
| `python3 -m compileall -q harness test_verifier_contract_unittest.py` | PASS |
| `git diff --check` | PASS |
| `git apply --reverse --check` against pinned source | PASS |
| Shipped `python3 test_verifier.py` | **Intentionally not run:** calls `run_task` with `MockLLM`; out of scope under the explicit script-only rule |
| Full application task suite, live LLM agent, provider, benchmark | **Not run / not claimed** |

**Patch:** [default-fail-evidence-contract.patch](default-fail-evidence-contract.patch), SHA256 `3444a7fbbd453a3023cf5fc0e10571ca0a671e723f1f035f1baee98ebd74917a`, exactly matching the tested first-party local Git diff. Reverse-apply check passed.

**Adversarial review:** The strict `True` requirement intentionally rejects legacy truthy nonbool checks, so adoption should inspect any third-party evidence check integrations before merging. A configured check returning literal `True` still does not independently prove correctness of that check's implementation. This change is not a general proof of verifier soundness, symlink safety, or operational autonomy.

**Continuation:** External publication remains human-owned. Generic `continue` skips this `AWAITING_EXTERNAL` row and advances to `discoveryrsi-campaign-history-integrity`.
