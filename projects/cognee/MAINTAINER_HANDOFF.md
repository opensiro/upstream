# Cognee Community — proposed OpenSiro VSM source connector

> **OpenSiro-owned preparation only.** This document is not a request filed with Cognee, a Cognee approval, an upstream PR, or a Mergetober entry. Do not submit it automatically.

**Status (2026-10-16):** `preparing`. **Upstream issue:** none. **Upstream PR:** none. **Maintainer assignment:** none.

## One coherent contribution

A version-pinned, read-only **source** connector for the [OpenSiro VSM Harness Index](https://github.com/opensiro/vsm-harness-index). It imports canonically *included* assessment Markdown into a **new local Cognee dataset**, storing six literal S1–S5 grades, original source provenance, and assessment-scoped evidence as native typed graph data. Optional lexical chunks enable Cognee's own BM25 section search. It does not try to implement a generic GitHub connector or replace Cognee's ingestion/graph APIs.

- **Code to review:** [`opensiro/cognee-community:feat/opensiro-vsm-source-review`](https://github.com/opensiro/cognee-community/tree/feat/opensiro-vsm-source-review).
- **Pinned implementation:** [`d176484`](https://github.com/opensiro/cognee-community/commit/d176484e85da55c84450d67040cb4a2d096353c7).
- **Package:** [`packages/connector/opensiro-vsm/`](https://github.com/opensiro/cognee-community/tree/feat/opensiro-vsm-source-review/packages/connector/opensiro-vsm).
- **Independent research and fault evidence (not proposed for merging):** [`feat/opensiro-vsm-source`](https://github.com/opensiro/cognee-community/tree/feat/opensiro-vsm-source); [Index #1598](https://github.com/opensiro/vsm-harness-index/issues/1598).
- **GitHub Actions Python 3.11 verification:** [successful B20 run](https://github.com/opensiro/cognee-community/actions/runs/38942238109).

### Shipping surface

1. `source.py`: pinned Index Git tree, admission catalog, exact assessment identity and literal six-function grades. No writes to the Index.
2. `native.py`: existing Cognee 1.6.4 DLT ingestion + graph-only typed `VSMHarness`, `VSMAssessment`, `VSMFunction`, and assessment-level `VSMEvidence` nodes; optional six-section `DocumentChunk` projection.
3. `attempt.py`: exclusive, fsynced **single-host** staging claim created before any Cognee write, preventing unsafe same-dataset retry after failure.
4. `audit.py`: independent existing-dataset-only source/grade/provenance audit; never creates an absent audit target.
5. Package metadata, Apache-2.0 license, README, CLI, example, focused tests, and a fork-only Python 3.11 CI workflow.

### Tested — without implying acceptance

| Evidence | Actual observation |
| --- | --- |
| B20, GitHub-hosted Python 3.11 | Wheel builds; clean venv resolves dependencies; `pip check` PASS; Cognee 1.6.4 / DLT 1.30.0 |
| B20 SDK and source unit tests | **32/32 PASS** |
| B20 real installed-wheel import | **3/3** assessments, **69** nodes, **48** edges, **18/18** literal grades; independent new-process audit, source references and stage marker PASS |
| B20 read-only pinned source validation | 533 included / 45 excluded / 12 proposed; **not** a 533-record Python 3.11 import |
| B13, separate research branch under Python 3.12 | **533/533** full initial import, **11,201** nodes / **7,470** edges / **3,198/3,198** exact grades and audited provenance |
| B14–B16, research only | Specific real `SIGKILL` boundaries independently rejected; fresh-dataset recovery verified. These are **bounded** experiments, not product recovery certification. |

### Explicit non-goals / qualifications

- No real-time GitHub API sync, authentication, scheduled updates, in-place dataset overwrite, delete/GC, hosted OpenSiro control plane, LLM/embeddings, or semantic/vector retrieval.
- Only **Cognee 1.6.4** is tested; internal graph/provenance APIs may change.
- The stage claim and activation practices are **single-host**; no multi-writer/distributed transaction guarantees.
- `audit_dataset` currently accepts **existing local datasets owned by Cognee's default user**, not arbitrary shared-tenant datasets.
- Package code is Apache-2.0; assessment origins and links are attributed, not relicensed.

## Maintainer scope inquiry — draft, NOT sent

**Suggested title:** Proposal: pinned OpenSiro VSM assessment source connector for Cognee Community

> Hi Cognee maintainers,
>
> I'd like to propose a source-specific connector for the public OpenSiro VSM Harness Index under `packages/connector/opensiro-vsm/`.
>
> It reads canonically included assessment Markdown from a pinned Git revision (no credentials or API polling), then uses Cognee's existing DLT and typed graph APIs to represent the six literal VSM function grades, assessment-level source evidence, and document provenance. Optional Cognee-native section-level BM25 search is available. The connector imports to a fresh local dataset only; it does not add a generic GitHub connector or an operational control plane.
>
> A working implementation and local tests were prepared in an **OpenSiro fork before any maintainer assignment**: [review branch](https://github.com/opensiro/cognee-community/tree/feat/opensiro-vsm-source-review). Its Python 3.11 clean-wheel CI is [green](https://github.com/opensiro/cognee-community/actions/runs/38942238109). I'd appreciate your feedback on whether this source-specific connector fits Cognee Community's scope and package/API conventions **as an ordinary OSS contribution**.
>
> I have **not** opened an upstream PR or claimed a Mergetober assignment. I can adjust the scope if this would be useful.

## Proposed pull-request description — draft, NOT submitted

**Suggested title:** `feat(connector): add pinned OpenSiro VSM assessment source`

### Description

Adds one source-specific Cognee Community package, `packages/connector/opensiro-vsm/`, for loading admitted public OpenSiro Index assessments from a pinned Git revision into an isolated fresh Cognee dataset.

Uses existing Cognee ingestion and graph interfaces to preserve six exact S1–S5 grades, assessment-level evidence and source provenance. Provides an optional section-level lexical projection, read-only independent admission audit, and single-host durable stage-attempt fencing. Includes README, executable example, focused tests, Apache-2.0 licensing and Python 3.11 clean-install CI.

**Testing:** Python 3.11 wheel + dependency resolution + `pip check` PASS; **32/32** tests; 3-assessment native ingestion and independent new-process audit PASS ([CI run](https://github.com/opensiro/cognee-community/actions/runs/38942238109)). A full **533-assessment** initial import was separately verified on Python 3.12 from the larger OpenSiro research branch. No assertion of full-corpus Python 3.11 verification or maintainer acceptance.

**Limitations:** Cognee 1.6.4 only, fresh-only local datasets, no scheduled sync/LLM/vector search, no automatic DLT recovery or distributed safety claims. Review this as a small connector, not a platform.

### DCO Affirmation

I affirm that all code in every commit of this pull request conforms to the terms of the Topoteretes Developer Certificate of Origin.

## Publication / governance checklist

- [x] Review branch is based on fork `main`, and fork `main` matches upstream `main` at checked SHA.
- [x] README, package, runnable example, tests, Apache license, and DCO-signed commits.
- [x] Cognee 1.6.4 Python 3.11 dependency installation + real smoke / audit in OpenSiro CI.
- [ ] Maintainer confirms that this specific connector is useful and the chosen internal Cognee API usage is acceptable.
- [ ] User explicitly authorizes **any** communication or PR in Cognee upstream.
- [ ] Before opening a PR, refresh from current upstream `main` and rerun tests.
- [ ] For a **Mergetober** entry specifically: organizer's eligibility determination is required; the original work **preceded any assignment** and must not be passed off as post-assignment work. A separate public real-use blog is required by the contest rules. Do not assume this existing work qualifies.

Sources for contest-only conditions: [Mergetober rules](https://www.wemakedevs.org/hackathons/mergetober/rules) and [resources](https://www.wemakedevs.org/hackathons/mergetober/resources). General OSS guidance: [Cognee Community CONTRIBUTING](https://github.com/topoteretes/cognee-community/blob/main/CONTRIBUTING.md) and [PR template](https://github.com/topoteretes/cognee-community/blob/main/.github/pull_request_template.md).

**Decision:** No upstream writes until explicitly authorized; no invented assignment, review, or contest eligibility.