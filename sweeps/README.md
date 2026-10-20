# Complete Index function sweep — explicit review receipts (DRAFT)

This is a **coverage/selection receipt store**, not a second assessment index or a list of required feature implementations. The proposed operating rule: **every current Index assessment with `status: included` receives a bounded review of all six function slots (S1, S2, S3, S3*, S4, S5), independently of its positive/negative autonomy labels.** A review can produce **zero, one, or many** independent improvement candidate hypotheses, with an explicit reason for zero.

The authoritative factual corpus stays in [Index](https://github.com/opensiro/vsm-harness-index); Profile/Skills define function semantics. These files are Upstream's **own hypothesis-screening receipts**, not Index edits or reassessments.

## Coverage contract

- `scripts/sweep_index_assessments.py` reads an **exact locally pinned Index git HEAD**, enumerates all `assessments/**/*.md` tracked at that commit, and counts only `status: included` as the complete-work denominator. `excluded-no-agentic-vsm` and `proposed` remain visible but **not admitted by this process**.
- All six Index function sections must exist for included records. The scanner uses historically compatible **minimal required** frontmatter validation so older legitimate extra fields do not silently remove systems.
- Every included system starts **UNREVIEWED** until its Upstream receipt records separate, evidence-backed decisions for the six functions. Missing records are **not** equivalent to `REVIEWED_ZERO`. A receipt pinned to an old Index commit becomes stale when the queue is re-derived at a new commit and must be rechecked, not automatically rebased.
- Each function slot records `UNREVIEWED`, `REVIEWED_ZERO`, `HYPOTHESES_RECORDED` or `BLOCKED_EVIDENCE`. `REVIEWED_ZERO` means **no supported product-change hypothesis from the bounded review**, not proof that the upstream has no defects. `BLOCKED_EVIDENCE` **does not count as completed**. A hypothesis must link one or more actual [candidate cards](../candidates/README.md) with the exact Index origin/target; card provenance retains `ASSESSMENT_DERIVED` vs `ASSESSMENT_INFORMED`.
- A system is counted **fully screened** only when all **six** slots have `REVIEWED_ZERO` or `HYPOTHESES_RECORDED`, including at least 40 characters of substantive individual reasoning. This is a **declared research review only**, not independently verified native product fit; a separate product investigation remains required.
- The script fails closed on duplicated/unknown JSON fields, missing/inconsistent Index refs, orphaned or mismatched receipts/candidates, absent function sections, wrong git HEAD or invalid status. It cannot create candidate cards, mark native fit verified, choose proposals or grant GitHub writes.
- Multiple independent hypotheses per function/harness are permitted. One candidate linked across functions remains **one intervention**, not multiple successes. `GENERAL_UPSTREAM` candidates from product-first discovery are not retroactively assessment-derived.

## First reproducible substantive batch

After the one-system AgentBox seed receipt, [Batch 001](../reports/2026-10-21-index-sweep-batch-001.md) reviews the next **five assessments in deterministic path order**: A-Evolve, Abhed, acc, Active Graph, ActWeave. These are **bounded, Index-function-by-function reviews**, not full live-native regressions. Only the A-Evolve card resulted in a new hypothesis, classified `ASSESSMENT_INFORMED` from an independently reported issue. Not counting a candidate for the other systems is an explicit negative research decision, not a blanket claim of no defects.

## Run

```bash
# Read-only: use an already checked-out public Index at exact HEAD.
python3 scripts/sweep_index_assessments.py \\
  --index-root /path/to/vsm-harness-index \\
  --index-sha "$(git -C /path/to/vsm-harness-index rev-parse HEAD)" \\
  --reviews-root sweeps --candidate-root candidates \\
  --limit 15

# Machine-readable outstanding worklist (all included systems, not keyword hits).
python3 scripts/sweep_index_assessments.py \\
  --index-root /path/to/vsm-harness-index \\
  --index-sha "$(git -C /path/to/vsm-harness-index rev-parse HEAD)" \\
  --reviews-root sweeps --candidate-root candidates \\
  --offset 0 --limit 25 --format json
```

The worklist is sorted by assessment path for deterministic, paginated processing. The index root must be pinned by a trusted operator to the **actual public** Index commit; local Git object identity alone does not attest which GitHub repository the checkout came from. Avoid generating 615 `REVIEWED_ZERO` receipts without real function-by-function reading.

## Per-system review workflow

1. Read the system boundary, current Index assessment and all six source-pinned function sections; **do not infer a fix solely from `—` / `?`**. `S3*` is a distinct slot, not silently folded into S3.
2. For each function, name the actual organizational relation/decision owner, a plausible product-native pain or missing mechanism (or the absence of a defensible hypothesis), and what would **falsify** the proposed intervention. Record an explicit outcome and rationale.
3. If a concrete intervention hypothesis survives, create **one independent candidate card per meaningful product behavior change**; link its ID in the relevant function slot. Candidate cards then undergo separate current-upstream demand/mechanism/counterfactual/scope validation, reproduction and before/after experiments.
4. A zero-hypothesis review is a **valid outcome**. Do not fabricate code/PR work or rank by low VSM grades.
5. A reviewed coverage record is a read-only research declaration. Changes to Index, assessments, Control Plane S1 admission, fork permissions and third-party PR publication remain outside it.

[AgentBox example](agentbox.json) demonstrates a bounded six-function receipt with one assessment-derived S2 hypothesis. No entry is an automatic admission or evidence of changed VSM grades.
