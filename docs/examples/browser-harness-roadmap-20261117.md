# Browser Harness — source-pinned architecture-first roadmap pilot

**Snapshot:** 2026-11-17. **Status:** `DRAFT — NOT PUBLISHED`. Read-only, non-authoritative example for the [OpenSiro roadmap procedure](../CAPABILITY_ROADMAP.md); all GitHub statuses below can change. **This does not modify the original project, fork, accepted Index, or Profile.**

## Identity and pins

- Original repository: browser-use/browser-harness
- Original HEAD: bc274a297d893e94ee05b4901898809651876a2d
- Observed at: 2026-11-17
- Accepted Index assessment: https://github.com/opensiro/vsm-harness-index/blob/d7d07e2f6db17d8ca9bc6c9c6c6d07892c611e1d/assessments/br/browser-harness.md
- Accepted assessment blob SHA: 7522febc97e2eff75e78ad781cec9ac64f480a94
- Accepted review ref: afbcc381b963040c19627d788e40c7e7663171ee
- Accepted reviewed at: 2026-09-18
- System in focus: shipped Browser Harness CLI, browser daemon, CDP/tab helpers, skill and MCP mode, with external agent actors; **not** Browser Use's separate maintainer organization or host product
- Assessment vector: `A C — — — —` (historical accepted Index, **not** a current-ref reassessment)
- Proposed Index re-review: [PR #3219](https://github.com/opensiro/vsm-harness-index/pull/3219), **open/unmerged at observation**, result `reassessed-unchanged` is **not canonical**.
- Profile reference: [Profile 0.2.4](https://github.com/opensiro/vsm-harness-profile/blob/main/PROFILE.md) (current semantic reference, not a retroactive source review)
- Skills reference: [Methodology 0.3.8](https://github.com/opensiro/vsm-harness-skills/blob/main/skills/assess-vsm-harness/references/autonomy-states.md)

## Rights and authority

- [MIT license](https://github.com/browser-use/browser-harness/blob/bc274a297d893e94ee05b4901898809651876a2d/LICENSE) permits copying/modifying subject to retained notice; third-party site terms and imported examples remain separate constraints.
- [CONTRIBUTING.md](https://github.com/browser-use/browser-harness/blob/bc274a297d893e94ee05b4901898809651876a2d/CONTRIBUTING.md) says focused improvements/PRs welcome and uncertain ideas may be proposed via issue. CLA/AI-specific attestations are **NOT VERIFIED** by this document, not presumed waived.
- Matching [fork](https://github.com/opensiro-contributions/browser-harness) and [fork metadata](https://github.com/opensiro-contributions/browser-harness/blob/opensiro/meta/.opensiro/state.json) were observed with `owner_control=ALLOW` and `attention=ACTIVE`; these are **not** a blanket approval to publish public issues, comments, fork PRs or external PRs. The fork may have advanced since this snapshot.
- External-publication route: separate exact owner approval for the concrete destination, full issue body/diff and action is **NOT GRANTED** by this pilot.

## Existing work / overlap

| Function hypothesis | Observed source | State at snapshot | What is established / not established |
| --- | --- | --- | --- |
| S1 task outcome safety | [fork PR #2](https://github.com/opensiro-contributions/browser-harness/pull/2) | OPEN fork-local proposal; head `0be45c484fe3a7a721bad48f37dc288ca9ee0fbc` | Guards non-idempotent action intent in a separate proposal; does not establish S3/S5 |
| S2 tab coordination | [issue #998](https://github.com/browser-use/browser-harness/issues/998) + [PR #1034](https://github.com/browser-use/browser-harness/pull/1034) | issue OPEN; original PR OPEN/unmerged; head `4056c5aece6e4a83ea999d60e42482b84f9eed7b` | Task-owned reconnection proposal, **not** shipped general whole-system S3 control |
| S3 resource/attachment control hypothesis | [issue #895](https://github.com/browser-use/browser-harness/issues/895) and [issue #901](https://github.com/browser-use/browser-harness/issues/901) | both issues OPEN | Browser preference and caller-owned health/metadata are real asks, **not** proof of an existing S3 constructor |
| S3* verification | [video-review path](https://github.com/browser-use/browser-harness/blob/bc274a297d893e94ee05b4901898809651876a2d/src/browser_harness/video_render.py) | SHIPPED artifact checks | Renderer review is not independent organizational audit judgment returning to S3 |
| S4 domain feedback hypothesis | [issue #934](https://github.com/browser-use/browser-harness/issues/934) and [merged PR #976](https://github.com/browser-use/browser-harness/pull/976) | issue OPEN, PR MERGED | Maintainer-curated skill policy at developer recursion; not a demonstrated prospective runtime S4 loop |
| S5 policy ownership | [CONTRIBUTING](https://github.com/browser-use/browser-harness/blob/bc274a297d893e94ee05b4901898809651876a2d/CONTRIBUTING.md) and [PR #976](https://github.com/browser-use/browser-harness/pull/976) | developer-level maintainer decisions | Does not establish runtime S5, S5=P or new identity-level use case |
| S1 domain skills discoverability | [fork PR #1](https://github.com/opensiro-contributions/browser-harness/pull/1) | OPEN fork-local proposal; head `13c404281b89003c3675d64a903cdc98b2139a96` | Optional export proposal; independent feature, not a general VSM solution |

**Overlap boundary:** linked issues/PRs indicate active ideas; this snapshot inspected **PR metadata summaries and pinned first-party paths**, not every competing diff under matching native runtime tests. Function overlap and user-level impact therefore remain **UNVERIFIED** where stated. No third-party contributor branch can be edited without rights.

## Function ownership

- S1 browser actions: external task agent chooses navigation/interaction through first-party helpers; actual browser observations return to its next task action.
- S2: simultaneous external agents sharing one local daemon can interfere through tab switching; existing first-party skill prescribes serialization or isolated browser lane; host composes the coordinating actor.
- Candidate S3: **not established**. Host/operator may choose browsers and agent commitments, but source issue #895/#901 and a tab API do not demonstrate a whole-system allocator/decision owner with returned controls across tasks.
- S3*: video review checks media/source artifacts; no independent S3 corrective channel evidenced.
- S4: maintainer decisions on domain skills occur at another recursion; no first-party prospective options that return to S3 evidenced.
- S5: ordinary consent/preferences and maintainer PR policy are **not** a shipped identity/ultimate-policy decision and return loop; no inferred S5=P.

## Capability priority

**Candidate first user need (requires maintainer confirmation):** An operator running *multiple browser tasks* wants to inspect current task-owned lanes and commitments, choose a constrained shared-browser allocation, and obtain reliable subsequent-task feedback demonstrating that the choice applied, without mutating a user's unrelated tabs.

- Baseline: existing first-party helpers and skill instructions support manual host-side serialization/isolation and tab targeting.
- Current alternatives: reuse [tab reconnection proposal #1034](https://github.com/browser-use/browser-harness/pull/1034) if accepted; or implement a simple host-side scheduler without new harness APIs.
- **S3=C is only a speculative target**, not an established current grade, not a mandate, and not an admission to implement a resource governor. Further source-native demand and competing-PR diff/behavior checks are needed. S2=C is already historically assessed.
- Stage P0: obtain maintainers' assessment of actual multi-agent task/resource-control need and overlap; if none, **NO_USEFUL_CHANGE**.
- Stage P1: if qualified, expose a minimal function-specific current-state/commitment/decision/feedback constructor and a *real* host assembly example; before/after native success, unauthorized ownership and compatibility checks.
- Stage P2 optional: independently proven parent-governed S3 current-control mode (`C(P)` or `P` if appropriate), with a legitimate decision owner and return to operations.
- Stage P3 optional: autonomous plus parent mode only if desired, with separate decisive-owner evidence for `A(P)`; no forced full autonomy.

## Implementation options

1. **Plan only first:** reorganize #895, #901, #998 and #1034 by current native user outcomes, distinguish overlap and choose no-code/integration or actual S3 constructor only if maintainers agree. This is not permission to edit those PRs.
2. **If qualified, small product PR:** a minimal host-composable shared-resource decision/feedback interface; keep S2 tab correctness work separate; each actual implementation follows full `upstream upgrade` tests, classification, fork-local review/publication gates.
3. **Native counterfactual:** compare a minimal external host scheduler using existing APIs against the proposed constructor under the same two-agent browser lane collision scenario. If new API does not improve a real task, omit it.

## Specification and domain alternatives

- Profile feedback: if the case reveals a real ambiguity in function-specific ownership/recursion/closure, propose evidence and counterexamples to [VSM Profile](https://github.com/opensiro/vsm-harness-profile) as a **separate normative review**, not a mandatory original project dependency.
- Skills feedback: if construction evidence / parent-mode calibration is ambiguous, send a separately scoped proposal to [VSM Skills](https://github.com/opensiro/vsm-harness-skills).
- Optional domain experiment: only with independent permission, explore an explicitly bounded **multi-tenant browser-work** fork; compare the smallest native scheduler to a VSM-informed constructor. This fork has **NOT BEEN CREATED** by this roadmap.

## Cost experiment

- Matched task: two external agents competing for one mutable browser lane while preserving each agent's tab ownership.
- Native baseline: simple host-side serialization and explicit isolated browser setup.
- Hypothetical variant: a verified first-party, composable current-control constructor with owner/feedback/closure.
- Costs to measure: engineering hours, integration/review/test effort, regressions and maintenance; task success and isolation correctness.
- Cost status: NOT_MEASURED
- No quantified developer saving, quality superiority, new VSM grade or maintainer endorsement is claimed.

## Delivery and publication

- Result: PLAN_ONLY
- External issue: DRAFT — NOT PUBLISHED
- Internal roadmap example: a dated, **non-authoritative snapshot**, not a durable fork event or original issue.
- External maintainer communication, original PR, public fork-local review PR, domain fork publication and normative Profile/Skills PR: **NONE CREATED** by this pilot.
