# Recuris — fail closed on invalid or unpaired held-out data

**Stage:** `AWAITING_EXTERNAL`. Source-bound native Python patch only. No external fork, issue, PR, model run or provider call.

- **Frozen source:** `Gen-Verse/Recuris@7d3745ab787b1206ccd981cb1511100476097266`; included `S1=A` Index assessment `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`. The assessment identifies the first-party meta-agent gate controlling whether a memory revision is admitted. The concrete invalid-input defect was derived from reading `src/recuris/metaagent/gates.py`, not from a model efficacy assessment.
- **Need — PASS:** `held_out_paired_gate()` previously admitted `+inf` and scores greater than its documented `[0,1]` range as significant improvements. It also intersected the baseline and candidate keys, silently dropping unmatched held-out items, and raised `StatisticsError` for an empty per-seed series instead of rejecting the evaluation.
- **Mechanism — PASS:** validate finite, unit-interval numeric seed scores and nonempty per-item sequences in both matrices, require identical compared item sets, and return a negative `Verdict` for invalid/unpaired data before computing deltas or bootstrap bounds. Valid inputs follow the existing statistical decision path unchanged.
- **Counterfactual — PASS (bounded):** on frozen genuine source, six standard-library unittest cases produced **2 PASS / 3 FAIL / 1 ERROR** before the change and **6 PASS / 0 FAIL / 0 ERROR** after. The four initially nonpassing cases cover infinity, out-of-range reward, unpaired item coverage and empty series; the two passing controls cover legitimate improvement and no improvement.
- **Scope — PASS:** one Python function and one standalone Python unittest script. No benchmark worker, optimizer loop, LLM agent, live model or data-provider integration executed.

## Verification

| Check | Result |
| --- | --- |
| `PYTHONPATH=src python3 -m unittest discover -s tests -p native_heldout_gate_unittest.py -q` before | 2 PASS / 3 FAIL / 1 ERROR |
| Same command after | 6 PASS / 0 FAIL / 0 ERROR |
| `python3 -m compileall -q src/recuris/metaagent/gates.py tests/native_heldout_gate_unittest.py` | PASS |
| `git diff --check`; `git apply --reverse --check` on patched pinned checkout | PASS |
| Full Recuris benchmark/evolution/LLM evaluation | **Not run / not claimed** |

**Exact tested patch:** [invalid-heldout-data-guard.patch](invalid-heldout-data-guard.patch), SHA256 `1f129fac0e579bc33ab2b678325b5e1d0e6230e4887f47ae48d0a3049f3e9edc`. This SHA matches the complete local first-party diff byte-for-byte.

**Limits:** Demonstrates fail-closed treatment of invalid scores for one function; does not establish that all possible data corruption paths are blocked or that the meta-agent improves its tasks. External publication remains human-owned. Generic `continue` must advance to the next frozen nonduplicate candidate batch.
