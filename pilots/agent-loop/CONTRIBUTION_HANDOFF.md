# agent-loop — scientific-notation numeric grounding

**Stage:** `AWAITING_EXTERNAL`. Internal evidence and native patch only: no external fork, issue, commit, PR, or merge.

- **Source:** `Onipounds/agent-loop@49525dc12a9861f71c99050de3b4a4b8b897e9fa`, pinned from the included `S1=A` Index assessment at `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`, not `ASSESSMENT_DERIVED`. The assessment exposes a tool-result numeric verification boundary; this notation bug was identified during the subsequent direct-source screen.
- **Need — PASS:** `extract_numbers("1e3")` incorrectly returned `[1.0, 3.0]`. Therefore `verify_grounding` rejected a valid scientific-notation answer whose tool result was `1000`, while **accepting** the unsupported claim `1e3` when unrelated tool results contained `1` and `3`. Leading-decimal `.5` also parsed as `5`.
- **Mechanism — PASS:** recognize each complete signed decimal/scientific-notation claim in the existing numeric parser. Preserve the existing identifier suppression for e.g. `pump-7` and `S7-1500`. No model calls or security-control changes.
- **Counterfactual — PASS (bounded):** first-party Python source exercised with four additional `unittest` regression cases: before patch **1 PASS / 3 RED**; after patch **4 PASS / 0 FAIL**. The cases include the false-positive and false-negative grounding paths. No live LLM agent, provider, or mock-model performance experiment was executed.
- **Scope — PASS:** one regex and explanatory comment in `agent_loop/verify.py`, plus `tests/test_numeric_notation.py` as a native stdlib test. Local external source edits remain uncommitted and unpushed.

## Native checks and limitations

| Check | Result |
| --- | --- |
| `python3 -m unittest discover -s tests -p test_numeric_notation.py -v` before patch | **1 PASS / 3 RED** |
| Same test after patch | **4 PASS / 0 FAIL** |
| `python3 -m compileall -q agent_loop tests/test_numeric_notation.py` | PASS |
| `git diff --check` | PASS |
| `git apply --reverse --check` against modified pinned source | PASS |
| First-party `pytest tests/test_agent.py` | **Not run**: `pytest` not installed in the environment |
| Entire native suite, full CI, multi-version compatibility and model performance | **Not run / not claimed** |

**Patch:** [numeric-notation-grounding.patch](numeric-notation-grounding.patch). SHA256 `c95110e9a0c22f3c51b12143564b78514942aef1200898e015405931a6cea33c`, exactly equal to the real locally tested first-party Git diff. Reverse-apply check passed.

**Adversarial review:** This is a syntactic numeric-claim fix, not semantic proof of source attribution. The verifier still tolerates close-but-not-equal numbers and gathers values from the entire tool-result history. Neither those known trade-offs nor wider identifier, range, units, inf/nan and multiple-measurement cases are solved by this small patch. Maintainers should run their full pytest/CI matrix before considering adoption.

**Continuation:** External publication is human-owned. Generic `continue` skips this `AWAITING_EXTERNAL` row and proceeds to `agent-context-lab-default-fail-boundary` in the same fifth cohort.
