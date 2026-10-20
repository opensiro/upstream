# Improvement candidate intake — bounded Index-first S2 screen and Kit native opportunity

**Date:** 2026-10-21. **Owner:** [Upstream #56](https://github.com/opensiro/upstream/issues/56), in [Draft PR #67](https://github.com/opensiro/upstream/pull/67). **Status:** read-only research, no external GitHub write.
**Index snapshot:** `opensiro/vsm-harness-index/main@5393b698bfdfa4ca14d97a79238234eca20694e5`. The exact local Index checkout at that HEAD included **678** Markdown assessments, not a full newly executed assessment or exhaustive product ranking. This note is a **bounded screen**.

## Selection order and result

Search began from the Index's S2 functional evidence (missing or uncertain conflict/overlap controls), not a favorite upstream issue. Candidate summaries were inspected and current public target sources checked independently. In the examined set:

| Index target and assessed revision | Current third-party main inspected | Outcome |
| --- | --- | --- |
| [Crabot](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/cr/crabot.md) at `09324dba3036f9033bb8a7dc5b88cc62959db8a2` | [J-F-Liu/crabot@be0d954](https://github.com/J-F-Liu/crabot/commit/be0d954c6c72f129ba9cf570a29dd13da9edb590) | Assessment documents shared-workspace multi-session interference risk, but current README advertises overlapping-edit detection. No open upstream product request was found in the bounded issue check; **no proven new first-party need or product change selected** |
| [bash-agent](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ba/bash-agent.md) at `e0062d42f7016f40639a8e69070131d521194cc1` | [lloydzhou/bash-agent@94ab4c9](https://github.com/lloydzhou/bash-agent/commit/94ab4c9a4e4b726f4dd03a692180eb8f6a0670d8) | Parent/child FIFO reporting vs shared-file interference is a researchable S2 area. Reviewed open issues concern web UI/session management and core simplicity, not an accepted collision-resolution design. **PENDING native demand; no candidate admitted** |
| [Travis234](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/tr/travis234.md) at `97aff8b174fe95064b390f30da07093b33de3c0b` | [taikkyithar/travis234@97aff8b](https://github.com/taikkyithar/travis234/commit/97aff8b174fe95064b390f30da07093b33de3c0b) | README already explicitly requires disjoint child-file ownership; no open maintainer conflict feature request was found. **No assessed-native missing feature endorsed** |
| [Kit](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ki/kit.md) at `3fd1fd5fda269569ceba0c2dd884c988d31f53d0` | [speakeasy-api/kit@8f9f08a](https://github.com/speakeasy-api/kit/commit/8f9f08a2b2088381f1cb106dcb9129378f8f0b4e) | Index S2 describes per-child mutex/generation safeguards but no cross-child arbitration demand. Separately, [open first-party issue #222](https://github.com/speakeasy-api/kit/issues/222) gives a detailed startup-lockout reproduction from incomplete `subagent.harness`; present [source](https://github.com/speakeasy-api/kit/blob/8f9f08a2b2088381f1cb106dcb9129378f8f0b4e/src/main.rs) requires this field. Created a [distinct `ASSESSMENT_INFORMED` candidate](../candidates/kit-subagent-config-20261021.md), **not** derived S2 evidence |

The Index contains `visvoai` assessment at reviewed `25602903497dfeca8a4d7e654467ab046e32071c`, but the owner/repository name `VisvoAI/visvoai` could not be resolved via connected GitHub during this pass. **No current-native conclusion or candidate** may be inferred from the inaccessible repo. Existing earlier [AgentBox screen](../pilots/agentbox-s2/NATIVE_FIT_DECISION_AND_ALT_SCREEN_2026-10-20.md) separately evaluated Claw Code, KairoCode, AtomCode and Dendrophis; do not count them as freshly retested here.

## Provenance consistency check and actual effect boundary

A read-only local check used the actual Index checkout frozen at `5393b698` and its `git show <sha>:<assessment>` objects. It verified **4/4 existing candidate cards** against each included assessment's actual `repository` and `review_ref`:

- AgentBox overlap: [review ref](https://github.com/madarco/agentbox/commit/463a6a0a20176147f0b0dbfa8a261aba5e43cbd6)
- AgentBox dependency: **same** reviewed source; this separate hypothesis is `ASSESSMENT_INFORMED`, not falsely attributed as Index-diagnosed.
- Zot shared write: [review ref](https://github.com/patriceckhart/zot/commit/2a19df15ba8278dd6a92240ab6c2ae267c3cf6c3)
- Kit startup: [review ref](https://github.com/speakeasy-api/kit/commit/3fd1fd5fda269569ceba0c2dd884c988d31f53d0)

**Only identity/provenance syntax and actual pinned assessment objects were verified.** This does **not** prove the selection-order causal linkage for the Kit-specific defect, product benefit or native-fit status; the linked issue predates this pass, and the weakness is external to the Index S2 finding. It also does not make the untrusted local checkout a canonical live-source authorization mechanism.

## Decision

Four candidates are now independent research records; **none is `QUALIFIED`**. Kit `SCREENING` is based on a specific user-reported issue and current source observation, pending current-main reproduction, safe recovery semantics, regression evidence and author compatibility. AgentBox S2 remains the stronger assessment-derived but design-blocked parent experiment.

No third-party repo, user config, contributor fork, external issue/PR or canonical assessment was modified. The [read-only candidate inspector](../scripts/inspect_improvement_candidates.py) and [linker](../scripts/improvement_candidate_linkage.py) do not activate proposal stages or grant GitHub rights.
