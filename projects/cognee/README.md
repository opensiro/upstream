# Cognee Community — OpenSiro contribution

- **Upstream:** [topoteretes/cognee-community](https://github.com/topoteretes/cognee-community)
- **Working fork:** [opensiro/cognee-community](https://github.com/opensiro/cognee-community)
- **Local implementation branch:** [feat/opensiro-vsm-source](https://github.com/opensiro/cognee-community/tree/feat/opensiro-vsm-source)
- **Latest fork branch commit:** [986fc29](https://github.com/opensiro/cognee-community/commit/986fc296c6dd7c75406dd9fbd616d5fcd528ea8f) — 27 local tests PASS, Ruff lint/format PASS, package wheel build PASS, Cognee native three-harness smoke PASS
- **Contribution:** canonical VSM assessment source connector
- **Upstream status:** **not submitted** (no issue assignment or upstream PR)
- **Fork lifecycle:** **active**

## Why this contribution

Provide a source-first, read-only import of the accepted OpenSiro VSM harness assessments: six literal S1–S5 function grades, distinct source and upstream review revisions, stable identity, source-level provenance, exact structured queries, and optional section-level lexical search. It should reuse Cognee's native ingestion, typed graph, and provenance APIs rather than duplicate a generic GitHub connector.

## Evidence and current boundaries

- [Index research issue #1598](https://github.com/opensiro/vsm-harness-index/issues/1598) — full 533 accepted-record import, exact graph and provenance audits, B8/B9 query tests, B10 source package prototype, and B11 bounded generation switching.
- [Organization research issue #271](https://github.com/opensiro/vsm-oss-organization/issues/271) — upstream contribution strategy and scope decisions.

B10 demonstrated a CPU-only fresh import of all 533 accepted assessments into an isolated Cognee 1.6.4 dataset. B11 tested a smaller two-generation source update with independent audits and an atomic local selection pointer. These results do **not** establish production-grade interrupted Cognee ingestion recovery, distributed cutover, vector/semantic retrieval, or upstream acceptance.

## Workflow

1. Prepare and test all code **inside the OpenSiro fork** on a feature branch. Keep the fork's `main` aligned with upstream.
2. Match the Cognee Community package conventions (package, tests, example, documentation) and validate DCO requirements.
3. Obtain any contest-specific maintainer issue assignment/approval **before submitting**.
4. When a PR exists, add its verified URL to `registry.yaml`. Never mark it merged until upstream confirms acceptance.
5. Keep maintaining the fork only while necessary. If support ends, document outcomes and archive publicly rather than delete history.

No PR, issue or comment has been created in Cognee upstream as part of establishing this registry.
