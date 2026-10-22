# Zaly — bounded source screening (batch 03, row 2)

**Disposition:** CLOSED_NO_CHANGE. No accepted source patch, external PR or model-agent run.

- Frozen assessment: `assessments/za/zaly.md` at Index `396a54bb690f8ec7ce966bf9b00b241b30036307`; source `folke/zaly@a568c033de6418e5a24193f41ae8335ce0ddb2b2`.
- On 2026-10-22 the current `main` resolved to `efee7a370316886e6387de56e5119133c3095e4b`. Source-history inspection shows first-party commit [`abff49c`](https://github.com/folke/zaly/commit/abff49c) explicitly removed edit/write freshness checks, while [`842d394`](https://github.com/folke/zaly/commit/842d394) revised the edit argument contract. Current `edit.ts` no longer calls the pinned revision's `assertFresh`.
- Because the evaluated snapshot and current product have different explicit freshness contracts, a stale-write fix inferred only from the Index snapshot would be a backwards-looking intervention without a current agreed need. The old source's preflight and multi-edit uniqueness checks were inspected, but no current defect or native RED was established.
- The repository's declared runner is Bun (`bun >=1.2`); Bun is absent from this environment. No port/reimplementation or agent-model run was used to create a substitute test. Bounded GitHub issue/PR search for edit freshness did not return a matching candidate.

| Fit gate | Status | Reason |
| --- | --- | --- |
| Need | FAIL | Current product deliberately changed the screened contract |
| Mechanism | PASS | Assessed and present source revisions compared |
| Counterfactual | FAIL | No proven current regression or RED fixture |
| Scope | PENDING | No agreed code-change locus |

**Continuation:** Advance to Freebuff. Preserve both immutable reviewed SHA and current source revision in the receipt.
