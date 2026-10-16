# Cognee Community — OpenSiro contribution

- **Upstream:** [topoteretes/cognee-community](https://github.com/topoteretes/cognee-community)
- **Working fork:** [opensiro/cognee-community](https://github.com/opensiro/cognee-community)
- **Local implementation branch:** [feat/opensiro-vsm-source](https://github.com/opensiro/cognee-community/tree/feat/opensiro-vsm-source)
- **Latest fork branch commit:** [46b1781](https://github.com/opensiro/cognee-community/commit/46b17818e8c22f38295eccae0747edefb4e6d692) — B13 full 533/533 PASS; B14 graph-stage SIGKILL PASS; B15 early DLT-stage SIGKILL & durable attempt guard PASS; 36 tests, Ruff and wheel build PASS
- **Contribution:** canonical VSM assessment source connector
- **Upstream status:** **not submitted** (no issue assignment or upstream PR)
- **Fork lifecycle:** **active**

## Why this contribution

Provide a source-first, read-only import of the accepted OpenSiro VSM harness assessments: six literal S1–S5 function grades, distinct source and upstream review revisions, stable identity, source-level provenance, exact structured queries, and optional section-level lexical search. It should reuse Cognee's native ingestion, typed graph, and provenance APIs rather than duplicate a generic GitHub connector.

## Evidence and current boundaries

- [Index research issue #1598](https://github.com/opensiro/vsm-harness-index/issues/1598) — full 533 accepted-record import, exact graph and provenance audits, B8/B9 query tests, B10 source package prototype, and B11 bounded generation switching.
- [Organization research issue #271](https://github.com/opensiro/vsm-oss-organization/issues/271) — upstream contribution strategy and scope decisions.

B10 demonstrated a CPU-only fresh import of all 533 accepted assessments into an isolated Cognee 1.6.4 dataset. B11 tested a smaller two-generation source update with independent audits and an atomic local selection pointer. These results do **not** establish production-grade interrupted Cognee ingestion recovery, distributed cutover, vector/semantic retrieval, or upstream acceptance.

## Full packaged validation (B13)

The fork's [B13 validation report](https://github.com/opensiro/cognee-community/blob/feat/opensiro-vsm-source/packages/connector/opensiro-vsm/docs/validation-b13.md) verifies **533/533** accepted assessments, **3,198 exact function facts**, **11,201 nodes and 7,470 edges**, and native source provenance. CPU-only retrieval returned expected names at rank 1 for four controlled queries. A controlled interruption produced an incomplete stage which was rejected on reopening; recovery used **another fresh dataset** before pointer publication. This B13 test alone does not establish hard process termination or production readiness; B14 below tests one exact SIGKILL checkpoint.

## Real SIGKILL checkpoint (B14)

The [B14 report](https://github.com/opensiro/cognee-community/blob/feat/opensiro-vsm-source/packages/connector/opensiro-vsm/docs/validation-b14.md) verifies **actual SIGKILL of a spawned import process** after the first complete graph record, independent read-back of a partial **26-node/19-edge** stage, audit rejection and nonempty-dataset retry refusal. A **new clean dataset** was independently audited (3 assessments, 69 nodes / 48 edges / 18 grades) and activated; a separate process reopened and re-audited it as PASS. The fork includes an opt-in disposable-store [manual reproducibility test](https://github.com/opensiro/cognee-community/blob/feat/opensiro-vsm-source/packages/connector/opensiro-vsm/tests/manual_sigkill_recovery.py) which repeated the experiment in another scratch folder. This **does not prove** power-loss recovery, arbitrary mid-transaction crashes, distributed backend consistency or production readiness.

## Precommit DLT SIGKILL and durable retry fence (B15)

The [B15 report](https://github.com/opensiro/cognee-community/blob/feat/opensiro-vsm-source/packages/connector/opensiro-vsm/docs/validation-b15.md) documents a second **real SIGKILL**, now after DLT received the first source item but **before** the Cognee database had committed any Data rows. This exposed a gap: the former nonempty-Data guard would not prevent reusing such an already-attempted dataset. The package now has an exclusive fsynced per-dataset **attempt marker** written before any Cognee operation. Reopen after SIGKILL found **0 source documents and 0 graph nodes**, independent audit rejected the incomplete version, and the new attempt guard rejected reuse even with zero rows. A new clean 3-document dataset independently passed graph audit (69 nodes, 48 edges, 18 literal grades), was activated, and passed fresh-process read-back. The opt-in manual test sequence was repeated in a second scratch folder, all four phases PASS. **This is a local per-process DLT iterator boundary, not an arbitrary mid-DLT commit or distributed crash recovery certification.**

## Workflow

1. Prepare and test all code **inside the OpenSiro fork** on a feature branch. Keep the fork's `main` aligned with upstream.
2. Match the Cognee Community package conventions (package, tests, example, documentation) and validate DCO requirements.
3. Obtain any contest-specific maintainer issue assignment/approval **before submitting**.
4. When a PR exists, add its verified URL to `registry.yaml`. Never mark it merged until upstream confirms acceptance.
5. Keep maintaining the fork only while necessary. If support ends, document outcomes and archive publicly rather than delete history.

No PR, issue or comment has been created in Cognee upstream as part of establishing this registry.
