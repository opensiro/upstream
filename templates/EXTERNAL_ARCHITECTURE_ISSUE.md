# Proposal: [specific native capability] for [PROJECT] — Opensiro VSM architecture review

<!--
DRAFT — NOT PUBLISHED.
This is an ORIGINAL-MAINTAINER-FACING Issue, distinct from the internal fork-local
Roadmap. Replace all placeholders with original-native, source-pinned evidence.
Verify original repo contribution/issue rules and deduplicate live Issues/PRs.
Do not create an external Issue, PR or comment without separate exact
current-conversation approval of destination, action and complete public text.
If an existing original Issue covers the same question, prefer contributing there
after the same consent gate rather than creating a duplicate.
-->

## Proposal in the project's own terms

We propose an **optional** [specific capability/integration] in [PROJECT] so that
[developer/operator] can [concrete decision or task] using [existing native mechanism].

**What exists today:** [first-party code/doc link, supported deployment mode and actual behavior].
**What may be missing:** [specific decision/feedback constructor or integration, not just a low VSM grade].
**Closest existing project-native solution:** [existing way to achieve the same outcome; why a different constructor might help].
**Existing discussion:** [verified original Issue/PR links and status, or NONE FOUND WITH SEARCH SCOPE].

We prefer reusing existing first-party work where it provides required C links.
Existing code may be temporary or permanent; we do not assume which.
The maintainers alone decide product fit, adoption, replacement or rejection.

## How we reached this proposal — Opensiro VSM assessment

Opensiro uses a public, reproducible **Viable System Model (VSM) harness assessment**.
We examine organizational *functions and decision ownership* at a stated system boundary,
not the presence of six named components. This is a methodology for generating and
challenging design hypotheses, **not a product-quality, safety or maturity score**.

**Historical assessment:** [accepted Opensiro Index assessment permalink] ·
[Index commit SHA] · [assessment blob SHA] · reviewed [YYYY-MM-DD] ·
original `review_ref`: [40-character commit] · Profile [version] ·
Skills Methodology [version].

**Boundary:** [system-in-focus, recursion, supported first-party runtime/deployment modes].
**Current original HEAD:** [pinned commit URL, observed date] — checked separately
from the historical assessment. Where the source has changed, label the historical
vector as historical; never silently assert it is the current classification.

| Key | Organizational function, in plain language | Historical state | Evidence or limitation |
| --- | --- | --- | --- |
| **S1 · Operations** | Units/agents doing the actual work | [accepted value] | [specific assessment/source pointer] |
| **S2 · Coordination** | Preventing conflicts and interference between operational units | [accepted value] | [specific pointer] |
| **S3 · Current management** | Managing present resources, priorities and commitments across operations | [accepted value] | [specific pointer] |
| **S3* · Independent audit** | Independently checking operational reality and returning corrective feedback | [accepted value] | [specific pointer] |
| **S4 · Future adaptation** | Examining external/future change and bringing adaptation options back into present decisions | [accepted value] | [specific pointer] |
| **S5 · Identity and policy** | Resolving system identity, ultimate policy and authority questions | [accepted value] | [specific pointer] |

**How to read the states (Opensiro Skills notation, not VSM theory):**

- **`A`** — an autonomous agent closes the relevant organizational decision/feedback loop in a supported first-party mode
- **`C`** — a first-party, function-specific construction path exists; a developer must compose the autonomous actor, authority or closure
- **`P`** — a supported parent-governed mode closes S3, S4 or S5 without established first-party A/C autonomy
- **`A(P)` / `C(P)`** — an independently evidenced parent-governed mode exists alongside A or C (S3/S4/S5 only)
- **`—`** — within the assessed boundary, no material first-party function path was evidenced after a bounded absence review; **not** proof it cannot be built or must be built
- **`?`** — evidence insufficient to establish either a positive function path or a defensible bounded absence

The states describe **ownership and supported construction modes, not ranks**:
`A` is not a universally better version of `C`, and a missing local S4 or S5
does not automatically imply a defect. Parent governance or deliberate non-construction
may be appropriate to this project's goals. We welcome corrections to our interpretation.

## Why this particular construction?

**Whole-repository prioritization:** [briefly explain why this one function was
selected after reviewing S1/S2/S3/S3*/S4/S5, and relevant maintainer preferences
only if expressly documented; otherwise NOT_STATED].

**Construction hypothesis:** [accepted historical `Sx=[state] → Sx=C`, one
function only]. This is a **proposed future constructor**, not a change to the
accepted assessment or a claim that the feature is already shipped.

**Native building blocks:** [existing code/API, original Issue/PR decisions].
**Minimal proposed addition:** [what first-party decision/feedback interface,
authorization, feedback or integration would make the selected function
developer-composable]. A generic utility or VSM label alone is not sufficient.

**Scope exclusions:** [deliberately out-of-scope functions, optional modes or
parent-owned authority, with original project evidence if available; otherwise
NOT VERIFIED]. No expectation to implement all six VSM functions locally.

## Proposed approach and validation

1. [Minimum integration with current code/Issue/PR; name first-party entry point]
2. [Actor's lawful alternative decisions, actual resulting effect and feedback]
3. [Targeted positive, unauthorized/missing-owner and compatibility tests;
   none claimed executed unless linked]

**Hypothesized benefit:** [plausible operator or developer outcome, not invented demand].
**How to falsify:** [native baseline already suffices; missing function-specific decision
owner or feedback; violated parent rights; unacceptable complexity].
**Cost status:** NOT_MEASURED. **Cost reduction remains a hypothesis** until
the same native task's implementation, integration, review, test and maintenance
costs are compared.

## Feedback requested

- Does this proposal fit the project's actual architecture and priorities?
- Is a simpler first-party path, or an existing Issue/PR, a better place to work?
- Is any element of our six-function mapping incorrect or intentionally out of scope?
- Would you prefer a smaller patch, a design discussion, or no new mechanism?

The maintainers determine their architecture and contribution process.
This is **not** a request to adopt VSM, a mandatory autonomy upgrade, or
a claim of missing policy/security machinery.

## Three independent ways to participate

- **Improve this harness:** contribute to the focused native construction or related original Issues/PRs only if the maintainers want it and the project contribution route allows it.
- **Challenge or improve the open specification:** point out incorrect VSM function mapping, parent ownership or intentional exclusions; methodological feedback belongs to the Opensiro Profile/Skills sources.
- **Explore a domain-specific fork:** test a different operating boundary in a legally permitted experimental fork without asking the original project to adopt VSM.

## Research attribution and AI disclosure

[Opensiro Upstream](https://github.com/opensiro/upstream) ·
[VSM Profile (function definitions)](https://github.com/opensiro/vsm-harness-profile/blob/main/PROFILE.md) ·
[VSM Skills (assessment states)](https://github.com/opensiro/vsm-harness-skills/blob/main/skills/assess-vsm-harness/references/autonomy-states.md) ·
[VSM Index (accepted assessments)](https://github.com/opensiro/vsm-harness-index)

**AI involvement:** This proposal and evidence map were prepared with AI assistance.
No independent human validation, original-maintainer endorsement, implemented C
constructor, accepted new Index grade or measured cost improvement is implied.
