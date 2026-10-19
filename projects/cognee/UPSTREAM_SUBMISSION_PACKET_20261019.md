# Cognee Community — B23 manual submission packet

Status: **READY_FOR_MANUAL_UPSTREAM_CONTACT** (2026-10-19). This is OpenSiro-owned preparation only. **No external Cognee issue or PR has been created, and no maintainer has approved or assigned this work.**

## Candidate and scope

- Upstream target: [topoteretes/cognee-community](https://github.com/topoteretes/cognee-community), current main at preparation-time SHA **472e9484e6b610e4e0b193ae526439e3aad407a0**.
- Submission candidate: [opensiro/cognee-community — submission/opensiro-vsm-source-ready-20261019](https://github.com/opensiro/cognee-community/tree/submission/opensiro-vsm-source-ready-20261019), HEAD **8ec814d146e4cca9dd1c3ee6fb71123f94aebec5**.
- Exactly **three DCO-signed commits**, directly descended from upstream main, **17 changed files** entirely within packages/connector/opensiro-vsm. GitHub commit authors and sign-off identity match.
- Historical OpenSiro Draft review: [PR #1](https://github.com/opensiro/cognee-community/pull/1). [B22 source/provenance and observed failure report](https://github.com/opensiro/cognee-community/blob/fix/opensiro-vsm-shards-dev-flow-20261019/packages/connector/opensiro-vsm/docs/review-validation-20261019.md) is intentionally **not part of the upstream code diff**.
- The only differences between validated review-branch package blobs and candidate package blobs are the public-facing README (now refreshed with B23 clean Python 3.11 receipts) and the absence of that OpenSiro-only report. The executable code and tests are unchanged.
- No added bot, service, generic GitHub connector, runtime control plane or OpenSiro-only GitHub Actions workflow in the proposed 17-file diff.

## What it contributes

A bounded, source-first OpenSiro VSM Index connector using native Cognee 1.6.4 ingestion, typed graph and provenance. It reads canonical pinned Markdown, validates included membership and exact six literal S1–S5 function grades, preserves original Markdown hashes and reviewed upstream Git revisions, and optionally enables six-section native BM25 lexical search. A developer-facing read-only search-and-inspect example links native results back to pinned complete assessment Markdown and upstream source trees. Fresh local datasets use a single-host write-attempt marker; an independent audit checks exact graph/provenance and never creates missing datasets.

Limits: local fresh-only dataset, existing default-user ownership for read-only audit, graph-only plus six-section lexical search (NOT full-body/semantic search); no vector embeddings, model inference, hosted service, automatic update, distributed fencing or quality ranking. Usage in example harnesses is an engineering demonstration, not proof of superior gameplay or coding performance.

## Verification completed before asking for upstream submission

- [**GitHub-hosted clean Python 3.11 CI PASS**](https://github.com/opensiro/cognee-community/actions/runs/39292809116) on source/test-equivalent OpenSiro review branch: wheel build, full fresh dependency resolution, pip check, **43/43 tests**, pinned sharded Index validation **583 included / 48 excluded / 12 proposed**, **3/3** Cognee-native imported documents, **60 nodes / 39 edges / 18 exact literal grades**, fresh-process independent audit, **10** lexical hits and pinned Ascension full-source inspection, and absent dataset fail-closed negative.
- [**Ruff CI PASS**](https://github.com/opensiro/cognee-community/actions/runs/39292366309); additionally the exact candidate branch was independently cloned and passed full repository Ruff check/format (376 files), 43 tests and pinned source validation on Python 3.12/Cognee 1.6.4.
- Research-only older B13 tested 533-document full import on a different pinned Index; do not conflate it with this 3-document Python 3.11 import. No full-corpus Python 3.11 ingestion, comparative search study or broader production claims.

Public usage evidence:
- [Flash API harness construction](https://github.com/opensiro/harness-build-example-flash-api)
- [Game harness construction / Iteration 2](https://github.com/opensiro/harness-build-example-game-development)
- [Reusable Cognee-first SKILL.md](https://github.com/opensiro/vsm-harness-skills/blob/main/skills/build-harness-cognee-first/SKILL.md)

## Ready-to-send ordinary OSS maintainer inquiry — NOT SENT

**Title: Proposal: pinned OpenSiro VSM Index source connector for Cognee Community**

Hi Cognee maintainers,

I would like to propose one source-specific connector for the public OpenSiro VSM Harness Index, under packages/connector/opensiro-vsm. It uses Cognee's existing ingestion, typed graph, provenance and section-level BM25 search interfaces to make canonically included assessments available alongside six literal autonomy labels, source evidence and exact upstream Git revisions.

The prepared [candidate branch](https://github.com/opensiro/cognee-community/tree/submission/opensiro-vsm-source-ready-20261019) is based on the current Cognee Community main and has three DCO-signed commits. A [clean Python 3.11 installed-wheel CI run](https://github.com/opensiro/cognee-community/actions/runs/39292809116) passed unit tests, a real three-document Cognee import, an independent audit and native lexical search with pinned source inspection.

This is intentionally a local, fresh-only source connector, not a generic GitHub adapter or service. Lexical indexing currently covers the six VSM function sections, not the full assessment body. We have used the discovery workflow in public [Flash API](https://github.com/opensiro/harness-build-example-flash-api) and [Game Development](https://github.com/opensiro/harness-build-example-game-development) construction examples.

Would this fit Cognee Community's ordinary OSS contribution scope and conventions? The work was started before any maintainer assignment, and I am not claiming Mergetober eligibility or any prize. I have not opened a contribution PR upstream.

## Ready-to-send Cognee Community PR draft — NOT SUBMITTED

**Title: feat(connector): add pinned OpenSiro VSM assessment source**

### Description

Add a single Apache-2.0 source connector package at packages/connector/opensiro-vsm for pinned, read-only Git source ingestion of admitted [OpenSiro VSM assessments](https://github.com/opensiro/vsm-harness-index) into a fresh local Cognee dataset. Includes exact literal function values, versioned provenance, typed graph, independent source/grade audit, durable single-host attempt fencing, optional section-level lexical retrieval and a search-to-pinned-source inspection example. Supports strict historical flat and current sharded paths.

### Testing

[Clean Python 3.11 CI PASS](https://github.com/opensiro/cognee-community/actions/runs/39292809116): wheel, dependencies, pip check, 43 tests, pinned 583-record admitted source validation, real three-document import with 60 nodes/39 edges/18 exact grades, independent audit, native lexical search and negative missing-dataset test. [Ruff CI PASS](https://github.com/opensiro/cognee-community/actions/runs/39292366309) and independent full-candidate lint/test/source checks.

### Limitations

Cognee SDK 1.6.4, single-host fresh-only local datasets, function-section lexical search only, no embeddings, automatic updates, hosted service or guaranteed distributed recovery. No performance or contest eligibility claims.

### DCO Affirmation

I affirm that all code in every commit of this pull request conforms to the terms of the Topoteretes Developer Certificate of Origin.

## DCO precedents and contributor responsibility (2026-10-20)

The pinned [Cognee Community CONTRIBUTING.md](https://github.com/topoteretes/cognee-community/blob/472e9484e6b610e4e0b193ae526439e3aad407a0/CONTRIBUTING.md) requires per-commit sign-off and the PR description affirmation. A spot check of **10 merged** Cognee Community PRs found that enforcement is not universal: [#304](https://github.com/topoteretes/cognee-community/pull/304) had 5/5 signed commits and a PR DCO affirmation; [#370](https://github.com/topoteretes/cognee-community/pull/370) had 1/1 signed and an affirmation; [#191](https://github.com/topoteretes/cognee-community/pull/191) merged with an affirmation but 0/36 sign-offs; and [#224](https://github.com/topoteretes/cognee-community/pull/224) / [#210](https://github.com/topoteretes/cognee-community/pull/210) merged despite lacking both the affirmation and sign-off, with AI-assisted authorship acknowledged in their PR descriptions. These are observations, **not a DCO policy waiver**. There is no additional published separate personal-AI attestation requirement. The OpenSiro candidate satisfies the written template requirements: all three commits have matching sign-offs. A contributor publishing the PR must still ensure the DCO assertion about distribution rights is truthful.

## Manual boundary

Only the user may authorize contacting maintainers or submitting the external Cognee issue / PR. Before submission, recheck upstream main HEAD and accept/resolve any newer upstream changes. No external action or Mergetober eligibility is claimed by the preparation.
