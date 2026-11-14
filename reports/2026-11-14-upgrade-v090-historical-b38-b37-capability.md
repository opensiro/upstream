# Historical upgrade research continuation — batches 38 → 37 under v0.9.0

**Owner:** [Upstream #56](https://github.com/opensiro/upstream/issues/56). **Research date:** 2026-11-14 UTC. **Mode:** `upstream batch upgrade`, expressly reusing historical sources; **not** a newly numbered cohort, source reservation, Index reassessment or protocol change.

**Canonical bootstrap:** [START_HERE](https://github.com/opensiro/vsm-oss-organization/blob/main/START_HERE.md) → [ECOSYSTEM](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/ECOSYSTEM.md) → [Upstream main](https://github.com/opensiro/upstream/tree/main) → #56. `VERSION` and `CHANGELOG.md` both identify **0.9.0**; [capability-first contract](https://github.com/opensiro/upstream/blob/main/docs/CAPABILITY_FIRST_RESEARCH.md) governs this *new* continuation, not retrospective reclassification of frozen evidence.

**Frozen provenance:** [batch 38 manifest/hypotheses/summary](https://github.com/opensiro/upstream/tree/4edaae79a0757c42ab5ac792b135ff4fb9fafa82/data/assessment-candidate-batches), [batch 38 Index](https://github.com/opensiro/vsm-harness-index/tree/75bb11fb29027ed579e4d24016a815b3d95c710c/assessments), [batch 37 frozen summary](https://github.com/opensiro/upstream/blob/main/data/assessment-candidate-batches/2026-11-13-37-SUMMARY.md), [batch 38 earlier native follow-up](https://github.com/opensiro/upstream/issues/56#issuecomment-6881586032). The original pre-source claims and their chronology are unchanged. This report is *additive source-first research*. The existing [batch 37 revisit #304](https://github.com/opensiro/upstream/pull/304) and [batch 40 investigation #303](https://github.com/opensiro/upstream/pull/303) remain independently owned and were not edited.

## Batch 38 — HappyHands S4: task-aware selection of admitted experience cases

**Actor / new capability:** a designer/operator starts a new scoped repair for *renewal*; the planner retrieves relevant, independently admitted historical cases **before the 20-case cutoff** and includes the case references in its plan. Existing alternative: same-project, evidence-current admitted cases are sorted lexically by content hash and the first 20 are selected, irrespective of task.

**First-party demand and mechanism:** [`docs/experience-cases.md`](https://github.com/ShuaiMXu/happyhands/blob/04e75765fa92e662dd6158d2920fd72e06ff25fe/docs/experience-cases.md) explicitly lists *task-aware ranking* as remaining work. [`packages/harness-core/experience-cases.js`](https://github.com/ShuaiMXu/happyhands/blob/04e75765fa92e662dd6158d2920fd72e06ff25fe/packages/harness-core/experience-cases.js) performs provenance/currentness/QA safeguards, then `caseId` ordering and `.slice(0,20)`. Both `savePlan` paths call `experienceCaseBrief(run)`, and the run spec has `project.task` context. This is a **new selection workflow**, not a claim that a buggy existing approval/QA control should be loosened. Relevant VSM relation: S4's controlled use of historical experience in later plans; the Index S4 state is **?**, not evidence by itself that task ranking is needed.

**Fresh execution, original HEAD:** `ShuaiMXu/happyhands@04e75765fa92e662dd6158d2920fd72e06ff25fe` (its public `main` at readback). MIT LICENSE checked. Node 22.16.0; original pinned `pnpm` lockfile installed. Source-native first-party case test: **5/5 PASS**. [Standalone reproducible script](repro/2026-11-14-b38-happyhands-task-selection.mjs) imports and **executes the original, unmodified** `collectExperienceCase`, `admitExperienceCase`, `listExperienceCases`, `relatedExperienceCases`, `experienceCaseBrief`, and `verifyExperienceCaseBrief` functions.

The script creates **21 synthetic, explicit `regressed` admissions** in same-project sibling runs, with current synthetic before/after evidence. Since this is an adverse-example retrieval fixture, no real approved QA or human judgment is claimed. It assigns the single `renewal` tag to the *last* case by hashed ID; the other 20 get `billing`. The original native retrieval returns **20 billing / 0 renewal** for both renewal and billing task contexts, and its digest verifies. A distinct foreign-project control returns zero. The separate **research-only comparator**, operating on the same already-admitted cases, ranks bounded literal task/tag token matches and chooses 20: **1/1 renewal** appears for the renewal task, **0/1** for the billing task, and the no-match fallback matches the original `caseId` order. This is a deterministic **candidate selection value proxy, not integrated product behavior**, visual-design improvement or quality-of-recommendation claim. No source files were modified.

**Native reproduction:**
```sh
git clone https://github.com/ShuaiMXu/happyhands.git /tmp/happyhands
git -C /tmp/happyhands checkout 04e75765fa92e662dd6158d2920fd72e06ff25fe
cd /tmp/happyhands
corepack pnpm install --frozen-lockfile --ignore-scripts
node --import ./tests/helpers/isolated-git.mjs --test tests/experience-cases.test.mjs
cd -
HAPPYHANDS_ROOT=/tmp/happyhands node reports/repro/2026-11-14-b38-happyhands-task-selection.mjs
```

**Gates:** `need=PASS` for the first-party requested missing task-aware selection and source-native cutoff loss; `mechanism=PASS` for original selection path; `counterfactual=PASS` **only for the deterministic bounded selection proxy** (not downstream plan/user quality); `scope=PENDING` until the original maintainer accepts the task-descriptor matching, tie rule, tag language and negative/adverse-case policy. Classification: **source-first prospective MINOR_FEATURE, not strictly ASSESSMENT_DERIVED**. **`BLOCKED_EVIDENCE` for implementation admission**; next owner: HappyHands maintainer/design contract. Narrow next decision: confirm whether `run.spec.project.task` literal admitted-tag ranking is a valid first cut, and whether regression warnings retain priority. A native integrated source patch and independently matched after-run must follow, not precede, the four-PASS decision. No fork or original PR was created.

## Batch 38 — CodeDen S3: avoid duplicate per-item Factory spend capability

**Actor / capability:** Factory operator sees a work item's attributed cost and sets an optional per-item spend cap. This is genuine [first-party demand #325](https://github.com/leonvanzyl/codeden/issues/325), **not** an invented missing need. However original-project [PR #352](https://github.com/leonvanzyl/codeden/pull/352) is now **CLOSED/MERGED**, and issue #325 is **CLOSED**. The original developer's implementation includes session attribution, cost views and cap behavior, rather than an OpenSiro-authored submission. [PR #351](https://github.com/leonvanzyl/codeden/pull/351) also merged separately for transcript pagination. Batch 38's earlier readback had already exercised the open #352's **29/29** native suites; those tests are **prior evidence**, not a new run or proof of downstream adoption. The PR's mid-session cap behavior differs from #325's between-turn acceptance text, so do not assert perfect requirement parity merely because it merged.

**Disposition for an OpenSiro duplicate:** **`CLOSED_NO_CHANGE`**, reason: the source owner implemented and merged the same capability before an OpenSiro implementation was warranted. This closes only *our duplicate opportunity*, not a claim that users no longer need per-item costs. No fork, patch, external PR, or attribution claim.

## Batch 38 — LumaK S2: independently observed concurrency hazard; product contract pending

The preceding [source-native controlled schedules](https://github.com/opensiro/upstream/issues/56#issuecomment-6881586032) at `kuLm1Fs/lumak-ts@ef1d2ddb16630e537c205fadb11031ba7bae6131` establish two same-file editors both reading before writing and one edit lost, whereas whole-operation ordering retained both and disjoint file edits remained parallel. The planned feature would offer *declared editor effect scopes, safe overlap coordination before stale reads and preserved disjoint parallelism*. Existing alternative is unscoped parallel `delegate`; source currently lacks a target-native declared scope contract. A write-only mutex is a falsified solution.

**Gates carried forward from the earlier original native receipt:** `need=PASS` for reproduced hazard, `mechanism=PASS`, `counterfactual=PASS` for the operation-ordering fixture, `scope=PENDING` for compatibility of custom/unknown tools and user-visible scope policy. Product value and novelty remain unadmitted without first-party decision: this may be a reliability correction rather than a separate new capability. **`BLOCKED_EVIDENCE`** for implementation; next owner: original maintainer/design authority. No fresh native test was claimed by this section.

## Batch 37 — HelixHarness: Cursor host support, feature not speculative

[First-party issue #11](https://github.com/didi/helixharness/issues/11) explicitly asks about Cursor; the project author replies that it is not yet adapted and support is planned. Current public [README](https://github.com/didi/helixharness/blob/main/README.md) states the end-to-end support boundary **Codex / Claude Code**. Current source search also references `.cursor/mcp.json` as a **MasterGo credential location**, which is *not* proof of Propose/Apply/Archive Cursor host integration.

**Actor / requested capability:** Cursor user initializes a project and completes Propose → Apply → Archive under Cursor without losing knowledge, permission and hook evidence; current first-party alternative is a supported Codex/Claude host. **`SOURCE_FIRST MINOR_FEATURE`**, with maintainer demand `PASS`, but end-to-end host compatibility, source-native workflow comparison, accepted adapter surface, controls and scope remain **PENDING**. **`BLOCKED_EVIDENCE`**; next owner: HelixHarness maintainer/design, existing issue #11. No new issue, fork, patch or duplicate external PR.

## Cross-case decision register

| Historical case | Research verdict | Separate external delivery | Next owner/check |
| --- | --- | --- | --- |
| Batch 38 HappyHands S4, task-aware case ranking | `BLOCKED_EVIDENCE` after reproduced native deficiency and research-only comparative proxy | NOT_EXECUTED | Original maintainer: approve deterministic tags/task scope; then native patch/independent after |
| Batch 38 CodeDen S3, per-item Factory spend | **`CLOSED_NO_CHANGE`** for duplicate OpenSiro proposal | NOT_EXECUTED; source author's #352 MERGED | No duplicate; observe actual maintainer corrections separately |
| Batch 38 LumaK S2, scoped parallel editing | `BLOCKED_EVIDENCE` for scope/policy despite native prior collision witness | NOT_EXECUTED | Original maintainer: overlapping/unknown editor contract |
| Batch 37 HelixHarness Cursor | `BLOCKED_EVIDENCE` for host workflow contract and native proof | NOT_EXECUTED | Original maintainer #11: support design plus Codex/Claude controls |

**Boundary:** Historical six-function Index coverage remains in each original frozen screening. These are targeted capability-first research decisions, not new 60-function screenings, regrades, change to `VERSION`/`CHANGELOG`, S5 powers or a full strict-derived benefit cycle. `BLOCKED_EVIDENCE` is **not** a claim that the user need is absent. No target-native external PR can be admitted before four complete fit gates, permissions, source policy, licensed fork/patch handoff and independently validated after-effect.
