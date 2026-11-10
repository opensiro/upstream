# S1 assessment-to-upstream pilot: first bounded Index-origin discovery

**Date:** 2026-10-19  
**Command:** `test S1 function: upstream contributions`  
**Run type:** source-first, read-only, *fresh candidate selection from the Index*  
**Result:** `PARTIAL / NO_ELIGIBLE_ASSESSMENT_CANDIDATE_IN_SAMPLED_SET`  
**Index exact source commit:** [`d701ec67c96e39de5971271f6158997337c6e524`](https://github.com/opensiro/vsm-harness-index/commit/d701ec67c96e39de5971271f6158997337c6e524)  
**Upstream contract:** [`ASSESSMENT_DRIVEN_S1_TEST.md`](../docs/ASSESSMENT_DRIVEN_S1_TEST.md)  
**Organization control route:** [`test S1 function: upstream contributions`](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/AGENT_CONTROL_PLANE.md)

## Procedure and selection boundary

1. Started at the canonical Index `main`, not at an Upstream portfolio, fork, external issue, or prior preferred project.
2. Read the Index repository's `README.md`, `data/catalog.psv`, `data/signatures.psv`, `TLDR.md`, and six pinned assessment records. The first bounded sample is drawn from the **newest-facing TLDR view** and consists of Harness², NanoCoder (HaoyuZhang0214), CodeAgent (Harvil1), Cloud Coding Agent Node, RainCode and MinAgent. This is a **bounded feasibility sample**, not a random or exhaustive ranking of 590 accepted assessments.
3. For five of those, checked current public upstream default branch/permissions and current primary code/README; for four checked current issue inventories (and Harness² PR overlap). Cloud Coding Agent Node has only the Index assessment checked here and **was not advanced through fresh upstream qualification**: it is excluded from the evaluated five, not silently counted as FAIL.
4. Compared observed behavior against actual assessment findings; applied **upstream-native need, mechanism, counterfactual value, scope and overlap** gates. A grade gap alone never qualifies.
5. Found no safely actionable, nonduplicative improvement with all gates established in this sample. Did **not** select an executable candidate or invoke `prepare_contribution`. No fork, external branch, external PR, external issue/comment, credential or standing authorization was created by this pilot.

## Source-pinned candidate matrix

The five evaluated assessments below exist at the Index snapshot `d701ec67`. `PASS/PENDING/FAIL` in the fit columns are **pilot judgments only**; they are not canonical VSM states or a replacement for the Organization experimental fit ledger. Current upstream revisions were read independently; their relationship to the historical assessment review ref is not assumed.

| Candidate | Assessment / function finding | Fresh upstream main (2026-10-19) | Upstream need / mechanism / value / scope | Admission disposition |
| --- | --- | --- | --- | --- |
| [Harness²](https://github.com/google-research/harness2) | [`assessments/ha/harness2.md`](https://github.com/opensiro/vsm-harness-index/blob/d701ec67c96e39de5971271f6158997337c6e524/assessments/ha/harness2.md): `S1=A`, `S4=A`; cross-task reflector/library is a real future-facing path | [`1cfe254e8d25b15f37048c3730134686abe60335`](https://github.com/google-research/harness2/commit/1cfe254e8d25b15f37048c3730134686abe60335) | `PASS/PASS/PASS/PASS` for consistency of reflection evidence; [existing PR #79](https://github.com/google-research/harness2/pull/79) fixes wrong reflection comparison base and already supplies regression tests | `BLOCKED_OVERLAP`. An OpenSiro duplicate would not be a useful upstream-native contribution; no external patch created |
| [NanoCoder](https://github.com/HaoyuZhang0214/NanoCoder) | [`assessments/na/nanocoder-haoyuzhang0214.md`](https://github.com/opensiro/vsm-harness-index/blob/d701ec67c96e39de5971271f6158997337c6e524/assessments/na/nanocoder-haoyuzhang0214.md): `S1=A`, `S2=—`; multiple child operations may share one `TodoWriteTool` | [`a54add8b6e3f2b6c47e374e3fc466906bbd1f1b8`](https://github.com/HaoyuZhang0214/NanoCoder/commit/a54add8b6e3f2b6c47e374e3fc466906bbd1f1b8) | `PENDING/PENDING/PENDING/PENDING`. Current [`todo.py`](https://github.com/HaoyuZhang0214/NanoCoder/blob/a54add8b6e3f2b6c47e374e3fc466906bbd1f1b8/nanocoder/tools/todo.py) deliberately replaces one **shared** checklist; [`agent.py`](https://github.com/HaoyuZhang0214/NanoCoder/blob/a54add8b6e3f2b6c47e374e3fc466906bbd1f1b8/nanocoder/tools/agent.py) passes shared tool instances to children. Overwrites are mechanically possible, but this is **documented intentional behavior**, not a demonstrated production defect or maintainer-endorsed feature gap. Issues are disabled at this repo; no overlap scan by issue search can establish demand | `BLOCKED_EVIDENCE`. Needs a source-native conflicting two-child reproduction and a backwards-compatible acceptance contract before proposing a change |
| [CodeAgent (Harvil1)](https://github.com/Harvil1/codeAgent) | [`assessments/co/codeagent-harvil1.md`](https://github.com/opensiro/vsm-harness-index/blob/d701ec67c96e39de5971271f6158997337c6e524/assessments/co/codeagent-harvil1.md): `S1=A`, `S2=C`, `S3=A`, `S3*=—` | [`e48780be52949dfcf17338025f6beab48ca01428`](https://github.com/Harvil1/codeAgent/commit/e48780be52949dfcf17338025f6beab48ca01428) | `FAIL/PENDING/PENDING/PENDING`. [Current README](https://github.com/Harvil1/codeAgent/blob/e48780be52949dfcf17338025f6beab48ca01428/README.md) already describes team isolation, approval and security mechanisms. No source-backed request for a new independent S3* function was found in the open issues (zero open items). Adding a reviewer just to improve `S3*` would be score chasing | `NOT_ADMITTED`: grade absence is not an upstream demand |
| [RainCode](https://github.com/Rainmemery/RainCode) | [`assessments/ra/raincode.md`](https://github.com/opensiro/vsm-harness-index/blob/d701ec67c96e39de5971271f6158997337c6e524/assessments/ra/raincode.md): `S1=A`, `S2=—`; child agents share working state while writes are serialized only within one batch | [`0e2800c0a63eea37f2a7b6cab06f74f8e176b262`](https://github.com/Rainmemery/RainCode/commit/0e2800c0a63eea37f2a7b6cab06f74f8e176b262) | `PENDING/PENDING/PENDING/PENDING`. The [subagent manager](https://github.com/Rainmemery/RainCode/blob/0e2800c0a63eea37f2a7b6cab06f74f8e176b262/packages/agent-core/src/subagent/manager.ts) permits child concurrency; [tool executor](https://github.com/Rainmemery/RainCode/blob/0e2800c0a63eea37f2a7b6cab06f74f8e176b262/packages/tools/src/executor.ts) serializes write calls per `runBatch`, not across children. This shows a potential conflict boundary, **not** a reproduced user-visible failure, test regression or accepted change scope; no open upstream issues observed | `BLOCKED_EVIDENCE`. Require narrow real cross-child conflict reproduction plus native fix and regression, not generic S2 implementation |
| [MinAgent](https://github.com/Nichonauta/MinAgent) | [`assessments/mi/minagent.md`](https://github.com/opensiro/vsm-harness-index/blob/d701ec67c96e39de5971271f6158997337c6e524/assessments/mi/minagent.md): `S1=A`, `S4=A`; `/init` persists model-authored AGENTS.md and reloads it | [`17f0bfa746d9355b7a3e54608d3410ce245b222b`](https://github.com/Nichonauta/MinAgent/commit/17f0bfa746d9355b7a3e54608d3410ce245b222b) | `FAIL/PENDING/PENDING/PENDING`. The [current README](https://github.com/Nichonauta/MinAgent/blob/17f0bfa746d9355b7a3e54608d3410ce245b222b/README.md) documents operating `/init`, project context reload and file-write verification. The one observed open issue (#1) is about a logo, not an actionable assessment-derived harness improvement | `NOT_ADMITTED`: existing S4 functionality is not an actionable gap |

### Additional sampled assessment (not fully qualified)

[Cloud Coding Agent Node](https://github.com/fred1433/cloud-coding-agent-node) was inspected in
[`assessments/cl/cloud-coding-agent-node.md`](https://github.com/opensiro/vsm-harness-index/blob/d701ec67c96e39de5971271f6158997337c6e524/assessments/cl/cloud-coding-agent-node.md)
at the same Index SHA. Its fresh current upstream primary sources were **not**
read for this pilot; it is `NOT_EVALUATED` and must not be counted as
an assessment-derived opportunity, rejection or completed gate.

## Execution and authority receipt

| Stage | Actual observation |
| --- | --- |
| `discover_from_index` | `EXERCISED`: current Index source read, six assessment paths/pins checked, five independently cross-checked with current upstream default-branch source |
| `native_fit` | `EXERCISED` for five candidates; no nonduplicative all-gates-pass candidate |
| `proposal_only` | `NOT_SELECTED`: no eligible candidate, no manifest preview asserted as an approval |
| `create_public_fork` | `NOT_EXECUTED`: connected connector does not expose native fork creation; no existing fork substituted as a witness |
| `prepare_contribution` | `NOT_EXECUTED`: no admitted candidate and no exact current-session operator authorization |
| `submit_external_pr` | `NOT_EXECUTED`: manual publication remains separately reserved |
| `upstream_outcome` | `UNKNOWN`: no new external submission, review or merge by this pilot |
| `VSM_autonomy_grade` | `NOT_ASSESSED`: no conclusion of `S1=A/C/C(P)` or S5 admission |

**Evidence limits:** This is a bounded **source inspection**, not an external
harness runtime execution, concurrency reproduction, blind independent
evaluation, comprehensive assessment-corpus scan or performance experiment.
The reported Index/S1 origin is real; the absence of an eligible **sampled**
candidate is not a global absence statement. No new source/assessment claims
were written into Index. No PR/issue/email was sent to the sampled upstream
maintainers.

## Return and next operational checkpoint

The newly merged contract is **usable as a fail-closed intake**: instead of
reverse-engineering a reason for an available fork, it refuses to open one
when the source-first assessment and independent native benefit are not both
shown. This particular bounded test **closes as an honest negative
discovery receipt**; the broader S1 function still has `PARTIAL` operational
proof under [Upstream #6](https://github.com/opensiro/upstream/issues/6).

A subsequent bounded source-first batch may sample different Index records
and must pin its own Index SHA and eligibility evidence. For NanoCoder and
RainCode, the next meaningful **read-only** evidence would be a reproducible
two-worker disturbance and proof the intended fix does not defeat existing
user workflows. If one passes all four fit gates and overlap checks, only then
generate the existing Upstream proposal-only manifest and exact action packet.
Live writes continue to require a separate authenticated exact-stage grant;
this report provides none.
