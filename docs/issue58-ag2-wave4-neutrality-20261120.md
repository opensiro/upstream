# Upstream #58 — AG2 Wave 4 post-release v0.18.0 neutrality rerun

**As of 2026-11-20: DONE · REVIEWED · STRUCTURALLY VALIDATED · FORK-LOCAL PERSISTED · EXTERNAL NOT PUBLISHED.**

## Decision

- Original: [ag2ai/ag2](https://github.com/ag2ai/ag2) default `main@6d2dd8bab8af873ea29ed759cfacb572466d925e`.
- Existing stable case ID: `task-board-coordination-20261118` on matching verified [opensiro-contributions/ag2](https://github.com/opensiro-contributions/ag2).
- Protocol: [published Upstream v0.18.0 @28ea2cc](https://github.com/opensiro/upstream/commit/28ea2cce06b517bc4550dceddb00210b1e0dc85c).
- Accepted Index: [included AG2 @dadcf25](https://github.com/opensiro/vsm-harness-index/blob/dadcf25d6e7ffcbdb298e476a249b8be187c53b4/assessments/ag/ag2.md) blob `cc442691abb833236f48f30206580bb17c258f5c`, reviewed at `3211bb19832049e7abe1a5742b6d177274bff723` (2026-09-18), Profile 0.2.2 / Methodology 0.3.1.
- Historical vector unchanged: **S1=A · S2=C · S3=— · S3*=— · S4=— · S5=—**.
- **Proposal-stage: GO** for historical **`S3=— -> S3=C`**; research **NEEDS_EVIDENCE**, scenario **HYPOTHETICAL**, native tests **NOT_RUN**, cost **NOT_MEASURED**; no shipped C or new Index grade.

## Fresh source-first independent order and evidence

1. Selected the Wave 4 AG2 row after checking #58 comments, original/fork identities and current accepted Index, and immediately published the [IN_PROGRESS claim](https://github.com/opensiro/upstream/issues/58#issuecomment-7042743786).
2. Before accessing historical fork-local rationale, inspected pinned original `README.md`, `ag2/agent.py`, `ag2/task.py`, `ag2/network/hub/core.py`, HubArbiter, `TaskMirror`, `AgentClient`, discussion/workflow channel adapters, docs, contributor terms, test roots, [original Issue #3679](https://github.com/ag2ai/ag2/issues/3679) (OPEN), merged [#3576](https://github.com/ag2ai/ag2/pull/3576), [#2775](https://github.com/ag2ai/ag2/pull/2775), [#3128](https://github.com/ag2ai/ag2/pull/3128), and open [#3466](https://github.com/ag2ai/ag2/pull/3466) @81aef1444d0e55ae242591b6b4fae2e43b294599. Screened S1/S2/S3/S3*/S4/S5, network recursion and parent authority; documented Track A vs Track B and falsifier.
3. Sealed the [fresh independent verdict BEFORE historical comparison](https://github.com/opensiro/upstream/issues/58#issuecomment-7042841496), then read 2026-11-19 historical case and compared same S3 full-network current-manager evaluation object. Its old **NO_GO / NO_USEFUL_CHANGE** was based on unproven additional operator benefit relative to host targeted routing and #3679; v0.18.0 assesses constructibility before desirability. New **GO / NEEDS_EVIDENCE**, not an asserted product need or endorsement. Narrow single-next-wake adapter alone is still **not** an S3=C function.
4. New **P0**: optional developer-composable AG2 Network-level S3 current-control manager: whole-workload priority/capacity snapshot, lawful assign/defer/hold/reprioritize choice, revisioned atomic targeted dispatch of S1 work, TaskMirror returned terminal/correction changing the next S3 decision. **P1**: first-party authority and task ownership, local/remote idempotence, feedback, crash/retry, matched native #3679/static workflow comparator tests. **P2**: NONE.
5. Post-decision case sync on verified fork `ACTIVE/ALLOW` (preflight and write), validator `python3 scripts/validate_capability_roadmap.py <case-dir>` **PASS (structural only)**. Six GitHub remote blob SHA readbacks **MATCH (6/6)**. No conflicting same-case Wave 4 owner/commit observed in repeated concurrency checks.

## Authoritative fork receipt

**[Frozen fork commit 6f4448c9237814ef3ec4f1342a6535e434c232d8](https://github.com/opensiro-contributions/ag2/commit/6f4448c9237814ef3ec4f1342a6535e434c232d8)** on `opensiro/meta` (parent historical `f33ff627c9d9b405c914ec78e63fc28d04f96282`).

- [Human issue.md](https://github.com/opensiro-contributions/ag2/blob/6f4448c9237814ef3ec4f1342a6535e434c232d8/.opensiro/issues/task-board-coordination-20261118/issue.md) · [AI constructor-sufficiency.md](https://github.com/opensiro-contributions/ag2/blob/6f4448c9237814ef3ec4f1342a6535e434c232d8/.opensiro/issues/task-board-coordination-20261118/constructor-sufficiency.md) · [canonical roadmap.md](https://github.com/opensiro-contributions/ag2/blob/6f4448c9237814ef3ec4f1342a6535e434c232d8/.opensiro/issues/task-board-coordination-20261118/roadmap.md) · [README](https://github.com/opensiro-contributions/ag2/blob/6f4448c9237814ef3ec4f1342a6535e434c232d8/.opensiro/issues/task-board-coordination-20261118/README.md).
- Append-only [Wave 4 event](https://github.com/opensiro-contributions/ag2/blob/6f4448c9237814ef3ec4f1342a6535e434c232d8/.opensiro/events/20261120T151216Z--ag2-wave4-neutrality-rerun.json), updated [owner state](https://github.com/opensiro-contributions/ag2/blob/6f4448c9237814ef3ec4f1342a6535e434c232d8/.opensiro/state.json) `ACTIVE/ALLOW`.

**Completion dimensions:** REVIEWED=YES; STRUCTURAL_VALIDATOR=PASS; REMOTE_SHA_READBACK=6/6_MATCH; FORK_PERSISTED=YES; INTERNAL_STATUS_PR=OPEN_FOR_REVIEW; FORK_GITHUB_ISSUE=NOT_PUBLISHED; THIRD_PARTY_ISSUE_PR_COMMENT=NOT_PUBLISHED; PRODUCT_IMPLEMENTATION=NONE; NATIVE_TESTS=NOT_RUN; INDEX_GRADE=UNCHANGED.

**Next permissible action:** internal review and, later, separately authorized native empirical validation or explicit owner approval of exact public Issue text. Product adoption and original policy remain exclusively with AG2 maintainers. This record does not grant external publication or a new VSM grade.
