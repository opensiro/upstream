# One-harness Upgrade: fork-local PR review and current AI disclosure

**Owner:** [opensiro/upstream](../PROTOCOL.md) · **Operating version:** current `PROTOCOL.md` on default branch. This is an **Unreleased** clarification, not a separate SemVer release or a new scheduler. Historical [upstream-old fork-local proposal](https://github.com/opensiro/upstream-old/blob/main/docs/CONTINUOUS_WORKING_FORK_PIPELINE.md#fork-local-pr-proposal-contract) and [v3 AI disclosure](https://github.com/opensiro/upstream-old/blob/main/templates/EXTERNAL_PR_DISCLOSURE_V3.md) remain intact as dated evidence, but the historical v3 *standing-publication/no-human-approval* statement does **not** describe the currently effective publication gate.

## What the human reviews

`upstream upgrade` chooses exactly **one original harness** and works on multiple technical hypotheses **within that harness** as needed. It implements/test-validates one real new capability or exits honestly with a source-local blocker/no-change. A failed hypothesis or local CLA/PAUSE is not permission to move to another original in that same invocation.

A real code proposal is prepared on a product branch in the matching correctly parented public `opensiro-contributions/<fork>` repository, **never** in `opensiro/upstream` or `opensiro-promotion`. It must not include `.opensiro/`, generated PR-body files, cloned evidence logs or unrelated changes. OpenSiro-only work state/events live on the fork's independent `opensiro/meta` branch.

The review surface is **one PR in that same fork, targeting the fork's source-matched default branch**. Its title/body are the exact prospective *third-party* PR presentation, preserving the third-party project's actual PR template and adding the current AI-assisted disclosure below. **Never merge** the fork-local PR to fork `main`: it is a human-visible proposal and may remain open or later be closed unmerged. The original third-party source owns any later external PR's status.

### Stages and authority

1. Independently verify source and license/contributor policy, source default SHA, the matching fork's `fork=true`, `parent.full_name`, product head/base SHAs, source-native need and baseline, tests, prior PRs and fork owner controls. A root GitHub license badge alone is not eligibility.
2. Implement/test on an authorized product branch, with a pinned diff and native before/after, negative/compatibility evidence. A source-local `DORMANT/PAUSE/STOP`, CLA/DCO, maintainer agreement or missing runner remains a blocker rather than a cross-harness rescan.
3. Compose the complete source-template-compatible external PR title/body **on the fork-local PR proposal**, including accurate disclosure, actual `reviewed_at` and source pins where an Index assessment exists. Use the same branch/commit for the reviewed external proposal. Preserve original author's mandatory checkboxes, contribution policy and project-specific disclosures.
4. Before **creating or updating a public fork-local PR**, show its exact destination, public title/body and verified code diff and obtain [exact current-conversation consent](https://github.com/opensiro/upstream/blob/main/PROTOCOL.md#external-publication-consent) for that public action. The fork-local PR is public and can be seen outside OpenSiro. Existing authorization for code branch edits **does not** itself approve this public posting. If the approval is absent, present a **read-only compare link**, source SHA, complete proposed body and `AWAITING_FORK_LOCAL_PR_APPROVAL`; do not manufacture a PR URL.
5. After authorized posting, independently read back the actual fork-local PR URL, head SHA, target branch, diff, title/body, open/draft state and CI. Show **that actual PR link to the human**, together with the exact proposed external destination/action and remaining conditions. Do not call it `READY_FOR_HUMAN_PR_APPROVAL` unless actual code/native checks and the review handoff are ready.
6. A separately approved and freshly verified **third-party PR** uses the reviewed product branch, source-native title/body, current disclosure and first-party PR readback. The fork-local review PR is not merged into the contributor fork's default branch by this step. Any public edit to an already published external PR is also a separate exact-action consent gate. No internal PR or historical standing mandate grants external publication consent.

## AI-assisted disclosure — current review-gated form

Use the following *additive* disclosure after the target repository's required PR sections. Historical v3 fields remain useful for evidence, but its text saying the PR was published *without separate human approval* is stale under the effective 2026-11-15 gate. This form intentionally does **not** claim independent human code review or assessment causality that cannot be proven.

```markdown
<!-- opensiro-ai-assessment-disclosure:review-gated -->
## AI-assisted contribution disclosure

**AI involvement:** This contribution's technical analysis, implementation, and reported tests were prepared with AI assistance through the Opensiro Upstream Contributions workflow. The reported native checks and code diff are available for independent verification; AI-generated changes may be incomplete or incorrect. No independent human technical review or correctness certification is claimed unless separately evidenced.

**Original source request:** <exact original issue/need URL>
**Improvement origin:** <ASSESSMENT_DERIVED | ASSESSMENT_INFORMED | GENERAL_UPSTREAM | INSUFFICIENT> — <brief, source-cited explanation>

**VSM assessment (when verified):** [Current record](https://github.com/opensiro/vsm-harness-index/blob/main/<ASSESSMENT_PATH>) · [Pinned record](https://github.com/opensiro/vsm-harness-index/blob/<ASSESSMENT_INDEX_SHA>/<ASSESSMENT_PATH>)
**Assessment date:** <YYYY-MM-DD from reviewed_at>
**Assessed source revision:** `<40-character review_ref>`
**Assessment relationship:** <context only | demonstrably prior pinned prediction used to formulate this improvement>
**Native validation:** <commands, exact results, limitations>

**Human/publication status:** <For an unpublished proposal: "This text is staged for owner review; no external PR has been submitted by this proposal." | For an already public PR: truthful statement of what is verifiably known, with NO retrospective claim of approval>
**Authority:** External maintainers alone decide whether to review, accept or merge the contribution. A linked VSM assessment does not certify this patch or prove a VSM grade improvement.
```

### Verification and non-claims

- Where the record exists, fetch **the canonical current Index assessment**, its immutable Index SHA and exact `reviewed_at` / `review_ref`; check the pinned file really exists at that SHA. Do not use a batch date, today or the external PR creation date as the assessment date.
- The **Index current record can predate the PR without causing its idea**. Label `GENERAL_UPSTREAM` / `ASSESSMENT_INFORMED` when the need came from the original source and the earlier assessment supplied only context. Use `ASSESSMENT_DERIVED` only with independently documented *pre-source* Index-first hypothesis chronology.
- For no verified matching Index record, write `No verified matching general VSM assessment` and omit fabricated assessment URLs, `reviewed_at` or source SHAs. Other independently pinned domain/source evidence may still motivate a feature; do not invent canonical Index coverage.
- Distinguish **AI-assisted coding**, native test claims, human publication approval and **independent human code review**. These are four different facts; do not claim a human technically reviewed the code just because they authorized an outward PR.
- Where an external PR was already posted, do not state that review was pending **before** publication or retroactively say it had exact owner approval if there is no supporting first-party evidence. A corrective description update remains a separately consent-gated outward edit.
- Do not copy the [historical v3 standing-mandate sentence](https://github.com/opensiro/upstream-old/blob/main/templates/EXTERNAL_PR_DISCLOSURE_V3.md) into newly prepared review-gated contributions. Keep historical published text and attestations unchanged until a specifically approved public edit.

### Known example needing correction, not an authorized edit

[browser-use/browser-harness PR #1034](https://github.com/browser-use/browser-harness/pull/1034) currently uses a generic `## AI assistance` paragraph. The [canonical Browser Harness assessment](https://github.com/opensiro/vsm-harness-index/blob/main/assessments/br/browser-harness.md) has `reviewed_at: 2026-09-18` and `review_ref: afbcc381b963040c19627d788e40c7e7663171ee`, and it can be pinned at [Index commit 854c6e5](https://github.com/opensiro/vsm-harness-index/blob/854c6e5441709b014c01f803c23311fdf366a354/assessments/br/browser-harness.md). **That alone does not establish an assessment-derived origin or retrospectively authorize its already-published PR.** This document prepares a corrected format; it does not edit that external PR.
