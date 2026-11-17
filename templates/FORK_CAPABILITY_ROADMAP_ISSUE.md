# [PROJECT] — capability roadmap for [user/operator outcome]

<!-- Fork Issue template. Fill brackets with verified evidence and remove this note.
Copy to opensiro-contributions/<fork> only after exact public-Issue approval.
Case-specific research belongs on the fork's opensiro/meta branch, not Upstream.
This is NOT the external maintainer issue template. -->

## Why this Issue exists

OpenSiro is testing whether reusable organizational specifications and a VSM-informed methodology can **standardize and reduce the cost of developing AI-agent harnesses**. This is a research hypothesis, **not** a proven cost reduction or a request to implement every VSM function.

**User outcome we want to improve:** [Who needs to do what, and what currently prevents or complicates it?]

## Source and evidence

- **Original repository / observed HEAD:** [owner/repo, immutable SHA link, date].
- **Working fork and issue-local case:** [fork URL] · [`.opensiro/issues/<case-id>/` at `opensiro/meta`].
- **Index baseline:** [pinned accepted assessment URL, assessment source SHA, review date, Profile/Skills versions]. The Index grade is historical, not a claim about current main. [Freshness/reassessment uncertainty if material.]
- **System boundary:** [whose operation is being evaluated; excluded recursion/integrations].
- **Contribution constraints:** [verified license, contributor/CLA/AI terms, fork owner control; unknowns marked as unknown].

## What already exists?

Map only relevant shipped behavior and original Issues/PRs. A proposed/open PR is **not** a shipped feature.

| User need / VSM function (if relevant) | Current implementation | Existing Issue/PR and verified status | Remaining gap |
| --- | --- | --- | --- |
| [Actor and task] | [Code/docs link] | [Issue/PR link, open/merged and head SHA] | [Concrete unserved user outcome, or none] |
| [Second relevant need, or remove] | [Link] | [Link/status] | [Gap/none] |

**Simplest original-native alternative:** [Existing feature, manual workflow or small project-native change]. Prefer this if it solves the same task.

## Proposed priorities

Do not propose a feature merely because an Index grade is low. First reuse, integrate or extend existing original work.

- **P0:** [Smallest useful new capability; actor → trigger/disturbance → authorized decision/action → observable result and later feedback]. [Which existing Issue/PR it extends.]
- **P1 (optional):** [Dependent improvement and why it is lower priority], or **none**.
- **Optional later stages:** [C → C(P) → A(P) only when the relevant function and independent evidence allow them; otherwise none]. **No mandatory grade progression.**

**If proposing a C-level constructor:** link a separate case-local acceptance contract for the function-specific first-party entry point, developer-composable autonomous actor, authority boundary, options/state, enforcement, subsequent-operation feedback, reachability and positive/negative native tests. A draft or generic plugin is not a delivered `C`; `P` may be the legitimate endpoint.

## How would we know it helps?

- **New action / counterfactual:** [What can a user or agent do that they could not meaningfully do before?]
- **Positive case:** [Actor, input, expected outcome, first-party observable evidence].
- **Negative case:** [Missing permission / incompatible option / refusal / failure and safe outcome].
- **Dependencies and conflicts:** [Original decisions, maintainers, other PRs, licensing, compatibility].
- **No-change condition:** [Evidence that the existing solution is sufficient, or the proposed value cannot be demonstrated].

## Independent next steps

Select **one**, not all three:

1. **Project-native integration:** organize existing Issues/PRs; propose a small useful source change *only through a separately authorized Upstream Upgrade*.
2. **Methodology feedback:** submit a separate, evidence-backed Profile or Skills proposal if the research finds a real specification gap.
3. **Scoped experiment:** test a legally permissible domain-specific fork, without obligating original maintainers.

**Cost experiment:** compare the *same user task* using the simplest native approach and the VSM-informed one. Measure implementation, integration, testing/review, maintenance and result quality. **Status: `NOT_MEASURED`** until observed.

## Decision / handoff

**State:** `PLAN_ONLY` — [`NEEDS_EVIDENCE` / `DECISION_READY` / `NO_USEFUL_CHANGE`] (report labels only, not metadata enums).  
**Open question:** [What decision or evidence is needed next?]

Store detailed research, roadmap, construction contracts and external-Issue draft under the verified fork's `.opensiro/issues/<case-id>/`. This Issue is for **OpenSiro's fork-local discussion**, not an external request. Before contacting the original repository, dedupe existing original Issues; a new external Issue needs **separate exact approval** and is newly created, **not a cross-owner transfer**. No automatic implementation, product PR, Index regrade or internal Issue closure.

**AI disclosure:** Draft and evidence synthesis prepared with AI assistance; no human review, shipped result or measured cost saving is claimed unless independently evidenced.
