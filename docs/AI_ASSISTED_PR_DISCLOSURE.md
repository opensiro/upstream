# AI-assisted external PR disclosure

**Owner:** Upstream Contributions. **Effective for:** newly submitted and
maintained third-party PRs prepared by the OpenSiro AI-agent contribution
workflow. The target repository's own current PR template and contributor
requirements remain primary.

## Proposal ownership

For a prepared contribution with a verified `opensiro-contributions/<target>`
working branch, store the **exact prospective external title/body** in one
fork-local PR to that fork's own default branch. Compose it using the original
target's latest PR template and this disclosure; re-read the final fork-local
text and diff before requesting human publication approval. After a real
third-party PR is submitted, its own title/body become authoritative for
maintainer-facing discussion. Upstream keeps only proposal/publication links,
verified SHAs and decision/readback evidence, not a parallel editable PR-body
file. See [fork-local proposal contract](CONTINUOUS_WORKING_FORK_PIPELINE.md#fork-local-pr-proposal-contract).

## Required publication text

Append the [versioned disclosure template](../templates/EXTERNAL_PR_DISCLOSURE.md)
to the PR body **after** the original project's required sections and
checkboxes. Fill each `{{ASSESSMENT_*}}` field from the **current canonical
Index record** for the target, not from guesses, the PR creation date, or a
batch freeze date:

- `ASSESSMENT_PATH`: repository-relative `assessments/.../*.md` file in
  `opensiro/vsm-harness-index`, used for a live `main` link and a pinned link.
- `ASSESSMENT_INDEX_SHA`: immutable Index commit containing the record **used
  to formulate this PR**; verify that the file and metadata exist at that ref.
- `ASSESSMENT_DATE`: that assessment's `reviewed_at` date in `YYYY-MM-DD`.
- `ASSESSMENT_REVIEW_REF`: the assessment's `review_ref` (40-character source
  commit); the date is about this reviewed source, not the later PR.

The current Index URL lets a maintainer's AI agent inspect an updated
assessment; the pinned URL and source SHA let it reconstruct the actual basis
of this contribution. If current and pinned records differ, identify this as
potentially stale evidence and re-evaluate rather than silently presenting a
new assessment as the source of the original change. Do not replace, omit,
reorder or falsely check the target project's PR template. Preserve the real
test results, skipped checks, license/CLA/DCO conditions and limitations.
The disclosure is additive and is not a substitute for independent validation.

### Historical Corrective cohort (retrospective descriptions only)

The already-published, finite 2026-10-23 Corrective cohort was governed by
[`CORRECTIVE-PUBLISH-2026-10-23-01`](CORRECTIVE_PR_PUBLICATION.md).
Its owner mandate permitted publication at the **batch level**, without a
separate human publication approval for each qualifying PR. The later
per-PR human publication gate must **not** be described as having applied to
those historical submissions.

For an existing external PR demonstrably belonging to that exact cohort,
append the [historical disclosure](../templates/EXTERNAL_PR_DISCLOSURE_LEGACY_CORRECTIVE.md)
to its original body, using a verified matching canonical Index record,
`reviewed_at`, `review_ref`, and immutable assessment snapshot. This is a
description-only, retrospective transparency update, **not** a new publication
mandate, a technical review, or a change to the original approval evidence.
If provenance is missing, ambiguous, or the PR is outside that finite cohort,
do not apply this template or invent an assessment.

**Newly published PRs**, including any historical packet that would be
reopened for publication, still require the v2 current-policy disclosure and
the current per-PR publication approval. The `upstream_pr_handoff.py` preflight
must continue to reject the historical template for a new PR; the exception
applies solely to already-published descriptions.

An external PR published under the **current v2 policy** must explain three
separate facts:

1. **Technical work and provenance:** an AI-agent workflow, informed by the
   linked, dated and revision-pinned VSM assessment,
   prepared the analysis and change. An assessment suggests a candidate
   improvement; it is not proof that the patch works or changes a VSM grade.
2. **Current human involvement:** the owner is temporarily approving each
   external publication while checking the pipeline for bugs. This release
   approval is not a claim of manual technical review or a correctness
   certification. Do not write “fully autonomous” or “no human involvement”
   about a PR published under this gate.
3. **Risk and authority:** agent-generated work can be wrong. Third-party
   maintainers retain review and merge authority; no upstream acceptance,
   adoption or benefit follows from opening a PR.

The read-only `scripts/upstream_pr_handoff.py` preflight requires the complete
v2 disclosure with syntactically valid, internally consistent current/pinned
links, date and source SHA in its bounded reviewed body before contacting
GitHub. This structural check does **not** independently fetch or confirm the
assessment's content: preparers must verify the record and `reviewed_at` from
the authoritative Index first. Publication
must still satisfy the exact human approval gate and independent credential,
license, branch, target-template and native-test requirements. A post-hoc
disclosure edit to an already published PR changes only the description,
never the code, approval record or downstream outcome.

## Future fully autonomous mode — not yet operative

The intended end state is one autonomous assessment → hypothesis → native
test → patch → publication → observation pipeline. A future disclosure may
truthfully say “published without per-PR human approval” **only after** the
owning S5 authority has expressly delegated that decision, the executor and
recovery controls are operational, and the dated PR evidence proves the
autonomous action. That future mode needs a separately reviewed version of
this template and its preflight contract. This document itself grants no
publication autonomy and removes no present approval requirement.
