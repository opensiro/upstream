# Cognee Community — OpenSiro contribution

- **Upstream:** [topoteretes/cognee-community](https://github.com/topoteretes/cognee-community)
- **Working fork:** [opensiro/cognee-community](https://github.com/opensiro/cognee-community)
- **Focused review candidate:** [feat/opensiro-vsm-source-review](https://github.com/opensiro/cognee-community/tree/feat/opensiro-vsm-source-review), [commit d176484](https://github.com/opensiro/cognee-community/commit/d176484e85da55c84450d67040cb4a2d096353c7) — **B20 Python 3.11 clean wheel install / pip check / 32 unit tests / real three-record ingestion / independent audit PASS** ([GitHub Actions run #1](https://github.com/opensiro/cognee-community/actions/runs/38942238109))
- **Full research branch:** [feat/opensiro-vsm-source](https://github.com/opensiro/cognee-community/tree/feat/opensiro-vsm-source), [commit 74e4321](https://github.com/opensiro/cognee-community/commit/74e43217e08411951f0c68cfbf2e9c78ab6227d4) — B13 533/533 included corpus; B14–B16 real SIGKILL cases
- **Contribution:** canonical VSM assessment source connector
- **Upstream status:** **not submitted** (no issue assignment or upstream PR)
- **Fork lifecycle:** **active**

## Review scope decision (B17)

A **separate branch based on the untouched upstream-synchronized main** contains **one source-first connector** with these shipping modules: pinned canonical source reader, native Cognee graph/lexical projection, required single-host stage-attempt claim (created before any Cognee write), and independent read-only source/provenance/grade audit. It contains a minimal CLI, local example, tests and packaging. The Cognee 1.6.4 integration was rerun against a clean three-assessment local dataset: **3/3 documents, 69 nodes, 48 edges, 18/18 literal grades, correct source refs and persisted stage marker; new-process independent audit PASS**. **32/32 unit tests**, Ruff lint/format and Apache-2.0 licensed wheel build PASS. B18 additionally verified that a missing dataset is rejected without creating a new one, and that an existing dataset still passes native independent audit. The review commits are DCO-signed off with the same GitHub name and noreply email as their commit authors. No upstream CI or maintainer review claimed.

Full B10–B16 experiments, manual destructive SIGKILL scripts, and the B11 atomic active-generation/pointer implementation **remain exclusively on the original research branch**. The review candidate does not ship activation infrastructure, automatic sync, distributed fencing, test-only fault injection, or any hosted runtime. This distinction avoids confusing OpenSiro research evidence with a Cognee-ready production platform. Contribution status stays `preparing` and `upstream_pr: null`.

## Compatibility, licensing and DCO review (B18)

Reviewed against [Cognee Community contributing instructions](https://github.com/topoteretes/cognee-community/blob/main/CONTRIBUTING.md) and [PR template](https://github.com/topoteretes/cognee-community/blob/main/.github/pull_request_template.md): package layout/README/example/tests present, review branch originates at `main`, and the B18 base review commit's DCO sign-off matches its GitHub author identity. Both Cognee Community and OpenSiro Index declare **Apache-2.0**; the standalone connector wheel includes its own Apache-2.0 license text and SPDX expression. Original evidence remains linked/attributed, not relicensed.

**Real B18 finding/fix:** Cognee's `resolve_authorized_user_dataset` creates missing datasets, so independent audit previously risked creating a dataset. The review connector now requires a **pre-existing dataset owned by Cognee's default user** for audit. Real separate-process test: nonexistent dataset rejected, total dataset count unchanged **1 → 1**; previously imported 3 assessments still independently audited **PASS**, 18/18 literal grades. Invalid selections also fail before SDK access. This limits audit to default-user-owned local datasets, not arbitrary shared access grants. B18 passed **29/29 unit tests**, Ruff check/format and wheel metadata/license inclusion checks.

Remaining publication gates: no real upstream CI result; pinned Cognee SDK **1.6.4** is the only tested version; maintainer acceptance/issue assignment (if applicable to the event) remains unverified, and **no upstream PR** has been opened.

## Installed wheel and Cognee API contract (B19)

The review branch now includes [`tests/test_sdk_contract.py`](https://github.com/opensiro/cognee-community/blob/feat/opensiro-vsm-source-review/packages/connector/opensiro-vsm/tests/test_sdk_contract.py), which checks the specific Cognee 1.6.4 native graph/provenance, Cypher/BM25 and dataset lookup interfaces relied on by the connector. **32/32 unit tests**, root Ruff check/format, and wheel build PASS. A separate **Python 3.12 virtual environment** installed the wheel without fetching dependencies, explicitly reusing the Cognee 1.6.4 / DLT 1.30.0 dependencies from the existing dev-alpha environment. Wheel-origin imports and SDK API checks PASS; pinned Index source validation recovered **533 included, 45 excluded, 12 proposed**; real wheel-origin local import and separate-process independent audit passed for **3 documents / 69 graph nodes / 48 edges / 18 exact function values**, native source refs and durable attempt marker. 

**B19-specific limitation, closed by B20:** dev-alpha itself had no Python 3.11 interpreter, so B19 could not establish runtime compatibility. The later **B20 GitHub-hosted Python 3.11 clean run successfully resolved and installed every declared dependency**, passing pip check, native ingestion and independent audit. B19 and B20 remain separate receipts; neither proves other Python versions, future dependency upgrades or cross-backend production behavior.

## Clean Python 3.11 wheel, dependency resolution and native audit (B20)

The OpenSiro fork now has a **read-only GitHub Actions workflow** [`.github/workflows/opensiro-vsm-py311.yml`](https://github.com/opensiro/cognee-community/blob/feat/opensiro-vsm-source-review/.github/workflows/opensiro-vsm-py311.yml) that runs only on the focused review branch (or explicit manual dispatch), without pull requests or upstream changes. It provisions **real Python 3.11** on a GitHub-hosted Ubuntu runner, builds the connector wheel, creates a **new Python 3.11 virtual environment**, installs the wheel and *all* declared dependencies from package indexes without using existing Cognee installations, and verifies `pip check` (**no broken requirements**). This is a substantially stronger dependency/packaging check than B19's inherited Python 3.12 libraries.

[**B20 run #1 (2026-10-16), completed SUCCESS**](https://github.com/opensiro/cognee-community/actions/runs/38942238109) at review branch commit [`d176484`](https://github.com/opensiro/cognee-community/commit/d176484e85da55c84450d67040cb4a2d096353c7): installed **Cognee 1.6.4 / DLT 1.30.0 / OpenSiro connector 0.1.0**, **32/32 unit tests PASS**, pinned Index source validation **533 included, 45 excluded, 12 proposed**, native **3/3** source documents imported from the wheel on CPU, and independent fresh-process audit **PASS** for **69 nodes / 48 edges / 18 exact VSM grade values**, source provenance and a persisted stage-attempt marker. GitHub job and all steps concluded `success`; this is not just an unexecuted CI configuration.

This closes the **Python 3.11 clean dependency resolution and local native validation gate**. Remaining limitations are unchanged: Cognee 1.6.4 is still the only version tested; the full **533-record** audit was established separately by B13 on Python 3.12, *not* by B20's three-record CI run; there is no Cognee upstream CI, maintainer approval, vector/semantic validation, distributed coordination or production recovery certification. No PR, issue or comment has been created in Cognee upstream.

## Why this contribution

Provide a source-first import which reads the OpenSiro Index without modifying it and writes to a fresh local Cognee dataset: six literal S1–S5 function grades, distinct source and upstream review revisions, stable identity, source-level provenance, exact structured queries, and optional section-level lexical search. It should reuse Cognee's native ingestion, typed graph, and provenance APIs rather than duplicate a generic GitHub connector.

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

## Partially committed DLT load-job SIGKILL (B16)

The [B16 report](https://github.com/opensiro/cognee-community/blob/feat/opensiro-vsm-source/packages/connector/opensiro-vsm/docs/validation-b16.md) documents a real process kill **after the first of three independent SQLite DLT load jobs committed**. A second read-only connection observed **1/3** committed DLT source rows before SIGKILL and the supervisor observed the same **1/3** after child exit **−9**. Main Cognee `Data` and graph were still **0/0**, showing that a committed DLT staging job need not mean Cognee source admission completed. The pre-Cognee durable attempt marker rejected reuse of the failed dataset; a **new** 3-record dataset independently passed audit (**69 nodes, 48 edges, 18 exact grades**) and CAS activation; a fresh process reopened it as PASS. This deliberately uses **three test-only DLT resources** to produce separately committed jobs and **does not prove partial commit inside one SQL transaction**, distributed consistency, or native DLT auto-resume. Status remains `preparing` and there is no upstream PR.

## Workflow

1. Prepare and test all code **inside the OpenSiro fork** on a feature branch. Keep the fork's `main` aligned with upstream.
2. Match the Cognee Community package conventions (package, tests, example, documentation) and validate DCO requirements.
3. Obtain any contest-specific maintainer issue assignment/approval **before submitting**.
4. When a PR exists, add its verified URL to `registry.yaml`. Never mark it merged until upstream confirms acceptance.
5. Keep maintaining the fork only while necessary. If support ends, document outcomes and archive publicly rather than delete history.

No PR, issue or comment has been created in Cognee upstream as part of establishing this registry.
