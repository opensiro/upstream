# Batch 40 — locked SDK compatibility and Sailry native-blocker follow-up

**Date:** 2026-11-14 UTC. **Owner:** Upstream [#56](https://github.com/opensiro/upstream/issues/56) / batch-40 [PR #303](https://github.com/opensiro/upstream/pull/303). **Contribution protocol:** SemVer v0.8.0. **Cohort:** explicit revisit of the same ten batch-39 sources, not an independent source-disjoint discovery. Frozen batch-39 ref `8a5ebb36058140e2b84ae4fb1b0751c9b0be7d89` is untouched. **Status:** `OPPORTUNITY_RESEARCH_PENDING`; `NO_ADMITTED_PATCH`.

This follow-up is additive to the [main batch-40 report](2026-11-14-upgrade40-explicit-deep-revisit.md), [first native-depth record](2026-11-14-upgrade40-native-depth-followup.md) and [round-3 falsifiers](evidence/2026-11-14-upgrade40-falsifiers-round3.json). It addresses a specific evidence gap rather than repeating all 60 historic function rows.

## 1. srchd — verified Firecrawl SDK version-contract incompatibility

**Current source-of-truth:** [`dust-tt/srchd@4b5ffb4`](https://github.com/dust-tt/srchd/tree/4b5ffb44bdc6bb1d2181d746ec951dd30f89ed08), [current `package.json`](https://github.com/dust-tt/srchd/blob/4b5ffb44bdc6bb1d2181d746ec951dd30f89ed08/package.json) and [`package-lock.json`](https://github.com/dust-tt/srchd/blob/4b5ffb44bdc6bb1d2181d746ec951dd30f89ed08/package-lock.json) declare `@mendable/firecrawl: ^4.35.0` and **resolve `4.35.0`**. The current [`web.ts`](https://github.com/dust-tt/srchd/blob/4b5ffb44bdc6bb1d2181d746ec951dd30f89ed08/src/tools/web.ts) consumes `firecrawl.scrape(...).markdown` and `firecrawl.search(...).web`.

**Existing contributor:** [PR #203](https://github.com/dust-tt/srchd/pull/203) by `Tketa`, closed voluntarily as premature, uses [`web-providers.ts` pinned `9f183fde`](https://github.com/Tketa/srchd/blob/9f183fde801a21ca925b13c7a5e2149d86093654/src/tools/web-providers.ts) and the historical `@mendable/firecrawl: ^1.21.1` dependency. This contribution is **not** owned by OpenSiro. It has not been rejected by the maintainer; [issue #204](https://github.com/dust-tt/srchd/issues/204) contains support for a shared interface and one file per provider.

### Executed pinned type-compatibility matrix

The [reproducible script](repro/2026-11-14-upgrade40-srchd-pinned-sdk-type-matrix.py) downloaded the **exact author source at pinned SHA**, verified its SHA-256, downloaded published `@mendable/firecrawl@1.21.1`, `@mendable/firecrawl@4.35.0`, and TypeScript 5.9.3 directly from npm, verified each **official SHA-512 package integrity**, and compiled the **unchanged** author source under strict TypeScript against each official SDK declaration.

| SDK contract | Expected from historic author code | Native TypeScript result |
| --- | --- | --- |
| `@mendable/firecrawl@1.21.1` | Historical contributor baseline | **1 type error**: `TS2322`, optional search-result URL cannot fill required `string` |
| `@mendable/firecrawl@4.35.0` | Current target lockfile | **6 type errors**: missing `success` and `error` on `Document`, missing `success`/`data`/`error` on `SearchData`, and one implicit-`any` result-map parameter |

**Important correction to a narrower mock test:** SDK 4.35.0 **does expose** `scrapeUrl()`, as a deprecated compatibility alias for `scrape()`, so a missing-method `TypeError` is **not** established in the actual locked SDK. The decisive incompatibility is the **return-object contract**: the old contributor code assumes `{ success, markdown/error }` and `{ success, data/error }` while the locked SDK exposes `Document` and `SearchData.web`. This is supported by the actual published library declarations, not invented mock-only method availability. The [JSON receipt](evidence/2026-11-14-upgrade40-srchd-locked-firecrawl-type-contract.json) stores exact diagnostics and official npm integrity strings.

This settles the **technical mismatch of the old proposal with the current target lockfile**. It does **not** establish that Linkup is higher-quality, that the maintainer wants to revive the branch, or that OpenSiro may take over the author's work. An ordinary historical PR version mismatch is **source-first maintenance evidence**, not a retrospectively assessment-derived VSM finding.

### New alternate functional hypothesis: native scientific literature search

The checksum-verified `4.35.0` SDK also declares a separate `firecrawl.research.searchPapers(query, options)` interface with paper retrieval, metadata and citation-related operations, distinct from ordinary `firecrawl.search()`. Its vendor documentation describes indexed PubMed, bioRxiv, medRxiv and arXiv content; the stated corpus size is **vendor metadata, not independently verified OpenSiro performance evidence**. The current srchd `web.ts` exposes generic `fetch` and `search`, **not** this separate research-paper capability.

For the biomedical-scientific search need in [#204](https://github.com/dust-tt/srchd/issues/204), a smaller non-provider-switch alternative could be a **research-mode tool using the existing locked Firecrawl SDK**, rather than reintroducing another external provider. This is a **hypothesis, not an admitted implementation**: different search semantics, coverage and result presentation must be evaluated against the reporter's actual fixed-query needs. [`dust-tt/browse`](https://github.com/dust-tt/browse) also has a separate current Stagehand-based browsing implementation; the maintainer's discussion of migration to it must be checked before proposing a new srchd core API.

**Separate fit gates:**

| Candidate | need | mechanism | counterfactual | scope | Origin |
| --- | --- | --- | --- | --- | --- |
| Existing reporter's selectable Linkup provider | PASS (issue #204) | PASS (existing source + author's branch) | **PENDING** (matched biomedical search quality, fetch parity, cost/performance) | PASS for proposed interface shape, **ownership/architecture still unresolved** | Source-first, existing contributor |
| Alternative Firecrawl `research.searchPapers` MCP capability | **PENDING** (reporter asked for research results, not this exact feature) | PASS (locked SDK declaration) | **PENDING** (no native matched paper-search fixture / live result) | **PENDING** (maintainer direction, browse migration, tool-scope) | New source-first alternative; not Index-first S4 |
| Compatibility of old PR #203 with current target | TECHNICAL MISMATCH **confirmed** | PASS (pinned type matrix) | Source-compatibility counterexample reproduced, **not a product-benefit PASS** | Existing author's responsibility | Bug/compatibility observation |

**Next decisive research:** a first-party fixed question set from the reporter (PubMed, bioRxiv, patents and source retrieval), equal search limits/time budgets, consistent normalized result keys, quality/coverage/manual relevance checks and provider cost; clarify whether `browse` or the locked SDK's paper index is the accepted product owner. Without a live provider fixture or a maintainer decision there is no four-PASS product improvement and no new external PR.

## 2. Sailry — precise reproducible locked Rust dependency blocker

The original [Sailry source `eaad1b7`](https://github.com/sailry/sailry-harness/tree/eaad1b7f18e448c8c4e9e9286e19560c8a351ae1) instructs coordinators to assign disjoint file ownership but supplies no machine-readable `owned_files` parameter in its native `spawn_agent` schema; separate worktrees are already supported. This schema boundary was proven in the prior [round-3 source test](repro/2026-11-14-upgrade40-sailry-spawn-schema-probe.py), **not** by running a native Rust two-child collision.

The initial Rust 1.98.0 `cargo test --locked -p sailry-node-runtime --test agent delegation` on an isolated, unmodified pinned checkout fetched many Git dependencies and submodules but was terminated before test execution after prolonged dependency bootstrap. A subsequent **actual offline retry** against the same source returned **exit 101 in 1.02s**, explicitly because the locked dependency `sqlx` at `https://github.com/sailry/sqlx.git?rev=747f74eb23aaea1f545ab08ab9c2d12f6628abed` was not checked out in the Cargo cache. The exact [native failure receipt](evidence/2026-11-14-upgrade40-sailry-locked-offline-failure.json) preserves command, source pin and stderr.

**Fit unchanged:** `need=PENDING / mechanism=PASS (existing delegation/worktree) / counterfactual=PENDING / scope=PENDING`. Neither a feature gap nor an unsafe runtime collision is proven. Next test requires full locked Rust dependency resolution followed by original two-child overlapping/disjoint file fixture in a disposable worktree, not a static schema assertion. No patch is admitted.

## Net conclusion

This follow-up resolves one previously ambiguous compatibility fact and one precise runner dependency blocker without claiming a completed product-opportunity assessment. The current SDK **does** have a deprecated `scrapeUrl` alias; **return-shape incompatibility** is the actual confirmed finding. A *possible* scientific-search enhancement may be achievable using the already locked SDK, but feature demand, third-party authorship, side effects, native effectiveness and maintainer design remain unresolved.

**No third-party changes, no external PR, no source re-reservation, no Index/Profile/Skills changes, and no independently measured before/after product gain.** Preserve `OPPORTUNITY_RESEARCH_PENDING` and the original four-PASS admission rule.

### Cold-start reproduction check

After publication of the reproducer, the exact script file retrieved from this PR was executed again with a **fresh empty temporary workspace** and a supplied Node 22 binary, with no previously cached author source, SDK archives or TypeScript compiler. It fetched and verified the historical author-source SHA-256, downloaded and verified all three official npm package SHA-512 integrity records, and independently reproduced **one TS error against Firecrawl 1.21.1 versus six against the locked 4.35.0 declarations**. Command exit **0**; the program's asserted negative control and confirmed return-type findings held. This is a fresh executable *type-contract* reproduction, **not** an independent human reviewer, source-native complete srchd build, or measured search-quality improvement.
