# Batch 40 — source-native functional depth: scientific-search interface and incident memory provenance

**Date:** 2026-11-14 (UTC). **Owner:** [Upstream #56](https://github.com/opensiro/upstream/issues/56) / [batch-40 PR #303](https://github.com/opensiro/upstream/pull/303). **Protocol:** v0.8.0; **cohort route:** `EXPLICIT_REVISIT` of the *same* ten frozen batch-39 harnesses at `8a5ebb36058140e2b84ae4fb1b0751c9b0be7d89`. No new Index source discovery, regrading, or source-disjointness claim. This is **source-first, original-repository evidence** discovered within the revisit, not a strict `ASSESSMENT_DERIVED` intervention.

The [original report](2026-11-14-upgrade40-explicit-deep-revisit.md), [first native-depth follow-up](2026-11-14-upgrade40-native-depth-followup.md) and [verified SDK matrix](2026-11-14-upgrade40-locked-sdk-source-native-followup.md) remain unchanged except for navigation links. The two experiments below are additional *functional interface/decision* checks, rather than cosmetic fixes or more boilerplate S1–S5 rows.

## srchd — a real scientific-search SDK path, but a **different output contract**

**Product source:** [`dust-tt/srchd@4b5ffb44`](https://github.com/dust-tt/srchd/tree/4b5ffb44bdc6bb1d2181d746ec951dd30f89ed08). The official lockfile resolves `@mendable/firecrawl@4.35.0`. [Issue #204](https://github.com/dust-tt/srchd/issues/204) asks about scientific/broad searches (PubMed, bioRxiv **and patents**) and selectable Linkup; a contributor already owns [PR #203](https://github.com/dust-tt/srchd/pull/203). Maintainer discussion also considers `dust-tt/browse`; do not duplicate the author's feature.

**New source-native experiment:** [reproducer](repro/2026-11-14-upgrade40-srchd-research-sdk-contract.py) obtains the *actual npm-distributed* Firecrawl 4.35.0 SDK, verifies its official SHA-512 package integrity, extracts the **verbatim** `ResearchClient` code and executes it with Node's isolated VM and a recording fake `http.get`. The fake HTTP only supplies deterministic fixtures: it does **not** call a provider, run a web search, contact a live literature index, use credentials or measure relevance. [Machine receipt](evidence/2026-11-14-upgrade40-srchd-research-sdk-contract.json) includes the exact original segment SHA-256 and paths.

| Control | Actual first-party SDK behavior under fake HTTP |
| --- | --- |
| `research.searchPapers(query, {k:5,authors:[A,B],from:...})` | **PASS**: routes to `/v2/search/research/papers` with preserved query, `k`, repeated author params, date, SDK origin |
| Empty query and non-positive `k` | **PASS**: rejected before any HTTP call |
| `research.getPaper('pmid:12345678',{query,k})` | **PASS**: routes to a namespaced paper-id detail endpoint, with encoded identifier |
| `research.similarPapers('pmid:12345678',{intent,k})` | **PASS**: routes to a related-paper endpoint |

**Native interface result:** this SDK feature is **already present**; the earlier claim of a missing *provider* capability cannot be silently reinterpreted as a claim that no paper-index interface exists. `SearchPapersResponse.results` uses a `PaperResult` with `paperId`, `primaryId` (e.g. `pmid:12345678`), `title`, `abstract` and score. A direct HTTP `url` field is **not required** by that published type. A response that is valid for the paper SDK therefore **cannot safely be treated as the current WebClient's link-based search result without an explicit, verified identifier-to-link mapping**. The fixture intentionally returns a valid paper record with *no* `url`.

**Product limitation:** a PubMed/bioRxiv paper index does **not** satisfy the patent-search portion of #204; it cannot replace the general web provider contract outright. The vendor-advertised index size/relevance is a vendor claim, *not* an independently measured OpenSiro result. Feature shape, fallback behavior, paper citation formatting, output contract and product ownership would need maintainer discussion.

**Gate disposition:** `need=PENDING` (the maintainer has not requested an *additional paper-tool*, as distinct from Linkup), `mechanism=PASS` (verbatim SDK code), `counterfactual=PENDING` (no matched live scientific query results or quality benchmark), `scope=PENDING` (patent coverage, browse migration, maintainer design). **No implementation admission.**

## Akmatori — preserve three distinct things: incident, claim, confirmation

**Product source:** [`akmatori/akmatori@be62d926`](https://github.com/akmatori/akmatori/tree/be62d926fe6d92dceb5cf12e9a95cb587433cdf1). [Maintainer issue #67](https://github.com/akmatori/akmatori/issues/67) explicitly lists **cross-incident corroboration** and **automatic verification from action logs/operator outcome** as separate *not-yet-selected* follow-ups. Its current [`applyExtractedMemory`](https://github.com/akmatori/akmatori/blob/be62d926fe6d92dceb5cf12e9a95cb587433cdf1/internal/services/memory_extraction_apply.go) writes per-incident agent memories and protects operator-owned memories, while [`ApplyAgentMemoryEvidence`](https://github.com/akmatori/akmatori/blob/be62d926fe6d92dceb5cf12e9a95cb587433cdf1/internal/services/memory_evidence.go) refuses agent-produced `confirmed` grades and downgrades causal claims.

**New source-native experiment:** [research-only Go test](repro/2026-11-14-upgrade40-akmatori-independent-claims_test.go) was inserted into a **disposable pinned checkout**, not the original repository, and run using original `usageTestDB` (GORM + SQLite), first-party `applyExtractedMemory` and `ApplyAgentMemoryEvidence`. [Machine receipt](evidence/2026-11-14-upgrade40-akmatori-independent-claims.json) captures the successful real Go invocation alongside the prior [usage-not-corrob test](repro/2026-11-14-upgrade40-akmatori-memory-revisit_test.go). Two targeted research tests **PASS**.

| Scenario | Native result |
| --- | --- |
| Operator-confirmed memory owns the original name | **PASS**: subsequent agent memories do not overwrite it |
| Incidents A and B independently report the same causal claim under the same requested name | **PASS**: two separate agent-owned `unverified` records, uniquely suffixed |
| Incident C reports a contradicting causal claim | **PASS**: third separate `unverified` memory; no implied contradiction reconciliation |
| Incident B extraction runs again | **PASS**: the *same incident's* record is updated, not duplicated as a new independent corroboration |
| Previously tested multiple citations from two incidents | **PASS**: `UseCount=3` is not the number of independent confirmations and does not change trust grade |

**Decision:** the system already preserves source identity and protects operator authority. It **does not** merge same-claim incident records or adjudicate contradictory claims; this is consistent with the maintainer's explicitly deferred #67 design, not evidence of a regression. A future *read-only suggestion* for corroboration would need semantic claim keys, independent incident-level evidence, contradiction handling, explicit operator or outcome rights, and a defensible negative-control fixture. Do not introduce a numerical auto-confirm threshold from reuse or identical text.

**Gate disposition:** `need=PASS` for the stated **later** issue; `mechanism=PASS` for the current native persistence boundary; `counterfactual=PENDING` for measurable benefit of a new corroboration interface; `scope=PENDING` for selected semantics/owner. **No implementation admission.**

## Research next actions and stop boundaries

For srchd, seek a maintainer-accepted decision on **additional scientific-research tool vs provider choice**, and a small fixed-query evaluation covering PubMed, bioRxiv, patents and document retrieval. Before claiming a benefit, provide citations, normalized result and link semantics, matched provider quality/cost/time results and a separate negative coverage control. The native SDK function-only test is not a live benchmark.

For Akmatori, require an agreed user-facing distinction between `corroborated elsewhere`, `contradicted elsewhere` and `confirmed by operator`; then test two independent incidents, one same-incident rerun, and one contradictory source using first-party extractor-owned fixtures. A text-equal claim alone does not prove independent evidence, and a correlation of outcomes is not causality.

**No four-fit-gate PASS, independently executed matched before/after *product improvement*, implementation in any upstream source, external PR or completed assessment-derived causal claim**. Master batch 40 remains `SCREENING_COMPLETE / OPPORTUNITY_RESEARCH_PENDING / NO_ADMITTED_PATCH`.
