# Upstream #58 — DeepSeek Harness, source-first v0.18 rerun and evidence-driven reconsideration (2026-11-19)

**Internal coordination status only.** Original fresh source-first v0.18 assessment reached **NO_GO / NO_USEFUL_CHANGE** for a broad baked-in goal verifier; after its decision, a further public-source check found **original user demand plus a working-repository proof-of-concept requiring a patched GoalService seam**. The same fork case was reconsidered and now records a **narrow scoped GO / NEEDS_EVIDENCE** for an optional, original-native Goal completion pre-commit guard port. This follow-up is **not a second independent fresh-context run**.

| Field | Current verified scope |
| --- | --- |
| Original | [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) |
| Original master pinned | [`2e39e70496aa02986ca6a820c5d497e816b69d7e`](https://github.com/deepseek-ai/deepseek-harness/commit/2e39e70496aa02986ca6a820c5d497e816b69d7e) |
| Historical included Index | [DeepSeek Harness assessment](https://github.com/opensiro/vsm-harness-index/blob/c2e43bf4750841277b3e58d8ba80314121734764/assessments/de/deepseek-harness.md) · blob `257a55619d474d8a86a49de6dffa93a4426d7b62` · reviewed 2026-09-18 from `ddefc45fbc7f8e46dd73185e68295696d1297887` · Profile 0.2.2 / Methodology 0.3.1 |
| Historical six-function vector | S1=A · S2=A · S3=A(P) · S3*=— · S4=— · S5=—; **unchanged** |
| Owner control | ACTIVE / ALLOW on opensiro/meta; fork parent verified |
| Target proposal | **S3*=— → S3*=C**, opt-in original-native `GoalTransitionGuard`-like port + independent composed reviewer |
| Proposal-stage decision | **GO** for bounded proof of the minimal port; **not** a code contribution or C-grade claim |
| Research disposition | **NEEDS_EVIDENCE** · direct original task/replay, port viability, benefit vs plugin must be tested |
| Original source testing / cost | **NOT_RUN / NOT_MEASURED**; external plugin authors' test results are not OpenSiro test results |
| Fork Human / AI / Receipt | **PERSISTED** atomically in [metadata commit `d8dca0f239891eacffc02f95556fa461fee0814e`](https://github.com/opensiro-contributions/deepseek-harness/commit/d8dca0f239891eacffc02f95556fa461fee0814e); upstream validator **PASS** on remote readback (structural only) |
| Historical first-pass outcome | [NO_GO / NO_USEFUL_CHANGE](https://github.com/opensiro-contributions/deepseek-harness/blob/39bc69e4149528ab89deb60a6ed03f81739b0178/.opensiro/issues/independent-goal-verification-20261119/roadmap.md) retained in Git ancestry |
| External original/public fork publications | **NOT PUBLISHED**; current original policy rejects external PRs |
| Product / Index change | **NOT STARTED / UNCHANGED** |

## Canonical current fork record

- [Human Issue draft](https://github.com/opensiro-contributions/deepseek-harness/blob/d8dca0f239891eacffc02f95556fa461fee0814e/.opensiro/issues/independent-goal-verification-20261119/issue.md)
- [AI constructor sufficiency](https://github.com/opensiro-contributions/deepseek-harness/blob/d8dca0f239891eacffc02f95556fa461fee0814e/.opensiro/issues/independent-goal-verification-20261119/constructor-sufficiency.md)
- [Canonical roadmap receipt](https://github.com/opensiro-contributions/deepseek-harness/blob/d8dca0f239891eacffc02f95556fa461fee0814e/.opensiro/issues/independent-goal-verification-20261119/roadmap.md)
- [Case README and chronology](https://github.com/opensiro-contributions/deepseek-harness/blob/d8dca0f239891eacffc02f95556fa461fee0814e/.opensiro/issues/independent-goal-verification-20261119/README.md)
- [Cohort issue #58](https://github.com/opensiro/upstream/issues/58)

## Primary evidence and smallest distinct construction

**Original native Track A.** [GoalService.complete at pinned HEAD](https://github.com/deepseek-ai/deepseek-harness/blob/2e39e70496aa02986ca6a820c5d497e816b69d7e/packages/goal/goal/src/index.ts) reaches `commitSnapshot` and appends `goal/change` before `goal/changed` is emitted. Goal revision and phase guards exist, but a passive event handler cannot veto already durable completion. Goal tool/round driver allow the model to end goals, Ralph receives worker self-reports, and Auto Review authorises pending tools, not final results. S1, S2 and S3 have meaningful existing owner paths; S4/S5 are not targeted.

**Observed user need.** [Original Discussion #10471](https://github.com/deepseek-ai/deepseek-harness/discussions/10471) reports two model-authorised premature `update_goal complete` actions and repeated creation of new goals for the same work, and specifically proposes a verifier-owned completion decision. This is user testimony, **not an OpenSiro reproduction or original maintainer approval**.

**Cheaper Track A comparator.** [bpc-oss/dsh-verification](https://github.com/bpc-oss/dsh-verification) claims an evidence/permit-bound opt-in reviewer; it uses a [vendor-patching script](https://github.com/bpc-oss/dsh-verification/blob/main/scripts/patch-vendored-goal.cjs) to add a synchronous pre-commit `GoalTransitionGuard`, and [tests](https://github.com/bpc-oss/dsh-verification/blob/main/packages/dsh-verification/test/seam-e2e.test.ts) describe direct `ctx.goals.complete` rejection without permit, plus permit attribution and no-guard compatibility. The tests are **source-read, not executed**; compatibility with the frozen original HEAD is **UNKNOWN**, and default `advisory` is not enforce.

**Minimal Track B.** Investigate a **typed optional GoalService pre-commit guarded completion extension seam**, without duplicating the goal store or bundling a mandatory verifier. A separately configured legitimate reviewer receives evidence independent of worker narration, certifies/rejects/holds, ensures denial precedes durable `complete`, records attributable permit/rejection, and sends actionable feedback to later *authorised* goal work. Parent pause/revocation and replay consistency still control. A native hook alone does **not** satisfy S3*=C.

**Falsifier and next bounded test.** Against original `2e39e70496aa02986ca6a820c5d497e816b69d7e`, compare A0 deterministic tests/human acceptance, A1 vendor-patched external verifier, B1 supported optional port on the same true/false-completion tasks. Test direct-service bypass, stale revision, absent reviewer, post-restart proof, original advisory compatibility and lawful corrective round. If an unpatched supported plugin already covers every completion path or A0/A1 achieves equal outcome at lower cost, revert the optional native-port proposal to **NO_GO**. No benchmark or implementation is claimed.

## Original Issues, PRs and publication policy — resolved API interpretation

Original [public repository metadata](https://api.github.com/repos/deepseek-ai/deepseek-harness) explicitly reports `has_pull_requests=false`, `has_issues=false`, `has_discussions=true`. The [PR tab](https://github.com/deepseek-ai/deepseek-harness/pulls) displays restricted creation and 0 open / 0 closed. Public pull REST listing and direct pull details returning 404 are **consistent with the PR feature being disabled**; neither prove a complete historical PR archive. The `/pull/8736` URL redirects to [Discussion #8736 about task notifications](https://github.com/deepseek-ai/deepseek-harness/discussions/8736); it was **not PR #8736** and must not be used as PR evidence. Original first-party [CONTRIBUTING.md](https://github.com/deepseek-ai/deepseek-harness/blob/2e39e70496aa02986ca6a820c5d497e816b69d7e/CONTRIBUTING.md) explicitly declines external PRs and asks for Discussions or plugins.

**Rights boundary:** No original-facing issue, comment, review, PR or Discussion; no public working-fork Issue/PR; no product code change and no Index regrade. A later external interaction requires separate current-conversation consent and actual maintainer/contributor rights. Current file is source-linked coordination only.
