# Included Index → all-six-function improvement sweep: initial coverage checkpoint

**Date:** 2026-10-21. **Owner:** `opensiro/upstream` [#56](https://github.com/opensiro/upstream/issues/56). **Review artifact:** [Draft PR #67](https://github.com/opensiro/upstream/pull/67). This is a read-only **coverage baseline**, **not** a completed screening of every harness, native improvement trial, Index reassessment or proposal-stage admission.

## Authoritative input and machine method

The current public `opensiro/vsm-harness-index/main` was verified at `5393b698bfdfa4ca14d97a79238234eca20694e5`, and a local checkout with **exactly that Git HEAD** was traversed with [`scripts/sweep_index_assessments.py`](../scripts/sweep_index_assessments.py). The tool inspects **all tracked** `assessments/**/*.md` at that commit; it does not search for keywords or restrict to `S2=—`.

| Read-only inventory measure | Observed |
| --- | ---: |
| Total tracked assessment records | **678** |
| `status: included` (the review denominator) | **615** |
| `status: excluded-no-agentic-vsm` (not screened) | **50** |
| `status: proposed` (not screened) | **13** |
| Function slots per included system | **6** — S1, S2, S3, S3*, S4, S5 |
| Required function-specific screening decisions | **3,690** |
| Completed *declared* six-function reviews at checkpoint | **1 / 615** |
| Recorded *declared* function review decisions | **6 / 3,690** |
| Remaining included systems in worklist | **614** |
| Outstanding function review slots | **3,684** |

The initial six-function example is [AgentBox](../sweeps/agentbox.json): **one assessment-derived S2 overlap-planning hypothesis**, five explicitly reviewed slots where no **separate supported product-change hypothesis** was identified at this bounded reading. This DOES NOT mean AgentBox has no other defects, that native S2 benefit is established or that any autonomy grades changed. The separately discovered AgentBox `dependsOn` issue is `ASSESSMENT_INFORMED` and does not become an assessment-derived S2 result through this receipt.

## Why this approach is not keyword triage

The new worklist enumerates **615/615 included systems** at the pinned Index, including systems with positive functional states and sections that do not use search terms `conflict`, `collision`, etc. It **does not** automatically claim they have been individually read: only a substantive `sweeps/<harness_id>.json` record with all six function outcomes can advance that system's **declared coverage**. If a system is omitted, blocked or reviewed without a supported hypothesis, its state remains explicit; no artificial candidate/PR or native-fit success is generated.

For every new independent hypothesis, a separate [candidate card](../candidates/README.md) is required, followed by independently checked **need / mechanism / counterfactual value / scope** in the *current* target project. Product-native reproduction and before/after measurement remain separate from any coverage declaration.

## Verification and limitations

- The frozen local Index HEAD, assessment metadata, publication status and presence of all six section headings were checked for every included assessment; this **does not attest** current GitHub authenticity without a trusted external ref check, nor does presence of a section demonstrate that we have re-reviewed its content.
- Existing `assessment_origin_preflight.py` is intentionally **not modified**: it has a narrower exact-stage proposal contract and can reject older legitimate `last_checked_ref`-style historical fields; the read-only corpus sweep accepts extra unique scalar fields while validating the required identities and sections.
- This checkpoint represents **one manually reasoned six-function review plus 614 queued**, not 615 completed. It must be rerun as the Index evolves and old per-system receipts should fail closed on changed input SHA.
- No Index grades, outside repositories, approval state, contribution manifest, contributor fork, operator permission, or third-party upstream issue/PR changed.

Run the [documented sweep command](../sweeps/README.md) to see the next deterministic page of included systems and record one verified function-specific decision per slot. Full screening still requires human/agent source analysis for each system; **the scanner only guarantees that nothing is silently skipped**.
