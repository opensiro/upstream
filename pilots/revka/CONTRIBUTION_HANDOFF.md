# Revka — validate deep workflow DAGs without recursion overflow

**Current status (2026-11-12):** `FORK_LOCAL_OPEN` / `ASSESSMENT_INFORMED`; `LEGAL_ATTESTATION_REQUIRED` before any code submission to the original Revka project. Historical 2026-10-24/25 records are preserved below.

## Source and problem

- Frozen `included S1=A` assessment: `assessments/re/revka.md` in Index `396a54bb690f8ec7ce966bf9b00b241b30036307`, reviewed `2026-10-18`.
- Pinned upstream: `KumihoIO/Revka@a1acd826502e12a6c2f3d147e488a7d2982c480b`, first-party [operator-mcp workflow validator](https://github.com/KumihoIO/Revka/blob/a1acd826502e12a6c2f3d147e488a7d2982c480b/operator-mcp/operator_mcp/workflow/validator.py), `_check_cycles()` and `validate_workflow()`.
- The recursive DFS in the topological sort exceeded Python's recursion limit on a valid deep DAG when the workflow definition listed downstream steps before dependencies. At 1200 steps it raised `RecursionError` instead of returning the `ValidationResult` promised by its interface.

## Native before/after proof

```shell
PYTHONPATH=operator-mcp python3 -m unittest discover -s operator-mcp/tests -p test_workflow_validator_deep_dag_native.py -v
```

Pydantic constructed the actual `WorkflowDef` and `StepDef` objects, with static `StepType.NOTIFY` and synthetic dependency edges. **No workflow execution**, no agent, provider, MCP, model, simulator, shell tool or network operation.

| Test | Before | After |
| --- | --- | --- |
| 1200-step valid descending DAG | ERROR `RecursionError` | PASS, all 1200 steps |
| Four-step ordinary chain | PASS | PASS |
| Four-step dependency cycle rejected | PASS | PASS |
| Two roots and one join | PASS | PASS |

**Before: 3 PASS / 1 ERROR. After: 4 PASS / 0 ERROR.** Patch applied to the actual source tree; `git apply --reverse --check` and `git diff --check`: PASS. Wider upstream pytest tests cannot be attested here because the `pytest` module is unavailable in this environment; do not label that an upstream regression.

**2026-10-24 live replay:** cloned upstream `main` at the same pinned `a1acd826502e12a6c2f3d147e488a7d2982c480b` and reran the original first-party Python/Pydantic source: **3 PASS / 1 `RecursionError`** before, **4 PASS** after the exact narrow patch; no agent or workflow execution. The local Python environment lacks pytest, so no broader test-suite claim is made. GitHub issue and PR searches for a matching recursion-depth fix found no exact match; this is limited overlap evidence.

## Bounded correction

- [`workflow-deep-dag-validation.patch`](workflow-deep-dag-validation.patch), SHA256 `61c63244a659849c4c25adee79eb1d6abc4ee859eff906069284579365fb82e5`.
- Changes only `_check_cycles()` from recursive DFS to equivalent explicit-stack DFS. Preserves cycle rejection and dependencies-first order without increasing global recursion limits.
- Risk: altered graph-traversal implementation, despite bounded same-function scope. Maintainer should run native full graph tests with its Python CI dependencies. Rollback: reverse the patch.
- No matching recursion-depth PR found in narrow GitHub PR search; still check current issues and maintainers' contributor policy before independently authorized external publication.

## Contributor authority blocker — verified 2026-10-24

The actual first-party [Revka CLA](https://github.com/KumihoIO/Revka/blob/main/docs/contributing/cla.md) states that **submitting a PR or code patch constitutes agreement** to Kumiho Inc.'s copyright and patent license terms; an individual needs no separate signature. Revka is dual-licensed MIT/Apache-2.0 ([`LICENSE-MIT`](https://github.com/KumihoIO/Revka/blob/main/LICENSE-MIT), [`LICENSE-APACHE`](https://github.com/KumihoIO/Revka/blob/main/LICENSE-APACHE)); the problem is **not** a missing license.

The finite OpenSiro corrective-publication mandate expressly does **not** delegate contributor-specific CLA attestations or consent. Therefore the prepared local patch is **not authorized for external submission under the current mandate**, even though native tests pass. Leave its ledger row `QUEUED`; no fake `SUBMITTED` or PR URL. The legitimate contributor/owner can separately decide whether to accept the actual CLA terms, after which upstream PR template, privacy, risk, and native validation gates must still be completed. No CLA agreement has been asserted on the owner's behalf.

**2026-10-25 terminal queue review:** Confirmed [Revka CLA v1.0](https://github.com/KumihoIO/Revka/blob/main/docs/contributing/cla.md) still defines code/PR submission itself as acceptance of Kumiho Inc. copyright and patent licensing, with originality/employer warranties. **Ledger now `BLOCKED`** pending a separate personal contributor decision, superseding the 2026-10-24 `QUEUED` instruction above. The prior deterministic RED/GREEN is unchanged; no new tests, fork, PR or agreement was executed in this pass.

## Current fork-local preparation  2026-11-12

**Verified stage:** `FORK_LOCAL_OPEN` (technical preparation complete); **external publication: `LEGAL_ATTESTATION_REQUIRED`**.

- Exact current original source / direct public fork `main`: `KumihoIO/Revka@a1acd826502e12a6c2f3d147e488a7d2982c480b`.
- Prepared branch in `opensiro-contributions/Revka`: `opensiro/fix-validator-deep-dag`, commit [`75c7adfca75fb30075e75674eb1badc2f6b7c90a`](https://github.com/opensiro-contributions/Revka/commit/75c7adfca75fb30075e75674eb1badc2f6b7c90a). Independent GitHub readback verified one direct parent matching source `main` and exactly the two expected source/test files.
- **Open, non-Draft, fork-local PR:** [opensiro-contributions/Revka #1](https://github.com/opensiro-contributions/Revka/pull/1). Base = fork `main`, head = selected commit; **this is not an external PR to KumihoIO/Revka**. Its body reproduces the target template, source-native evidence, assessment provenance, AI declaration and legal gate.
- Native proof replayed on 2026-11-12 in isolated Python 3.12 environment: baseline 3 PASS / 1 `RecursionError`; patched 4/4 PASS; adjacent first-party workflow-validator tests **17/17 PASS**. The historical 2026-10-24 pytest-unavailable statement above applies only to that prior environment. Full Rust and cross-component CI remain unrun.
- The patch SHA256 is `61c63244a659849c4c25adee79eb1d6abc4ee859eff906069284579365fb82e5`; its additive selection and dated native receipt were merged via [Upstream #254](https://github.com/opensiro/upstream/pull/254). The trusted exact two-file adapter accepted native paths after [#255](https://github.com/opensiro/upstream/pull/255). A first preparation attempt returned `UNKNOWN_AFTER_WRITE`; the observed large-checkout failure was fixed via sparse read-only materialization in [#256](https://github.com/opensiro/upstream/pull/256). GitHub readback confirmed no branch after the first attempt; a fresh one-use preparation authorization on current main then returned `PREPARED_VERIFIED`.
- Authoritative stage readbacks and decision boundary: [Upstream #6](https://github.com/opensiro/upstream/issues/6#issuecomment-6827421403) and [#56](https://github.com/opensiro/upstream/issues/56#issuecomment-6827422477).
- **CLA remains separate**: the original project accepts an individual contributor's CLA through actual submission, including copyright/patent license and contributor-rights representations. OpenSiro's technical standing mandate does not authorize the AI to give personal assent. No external PR, CLA assent, original-project acceptance, product benefit or VSM-grade improvement is claimed.
