# AI-assisted external PR disclosure

**Owner:** Upstream Contributions. **Effective for:** newly submitted and
maintained third-party PRs prepared by the OpenSiro AI-agent contribution
workflow. The target repository's own current PR template and contributor
requirements remain primary.

## Required publication text

Append the exact [versioned disclosure](../templates/EXTERNAL_PR_DISCLOSURE.md)
to the PR body **after** the original project's required sections and
checkboxes. Do not replace, omit, reorder or falsely check that project's
template. Preserve the real test results, skipped checks, license/CLA/DCO
conditions and limitations. The disclosure is additive and is not a substitute
for independent native validation.

The external PR body must explain three separate facts:

1. **Technical work:** an AI-agent workflow, informed by VSM assessment,
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

The read-only `scripts/upstream_pr_handoff.py` preflight requires this exact
disclosure in its bounded reviewed body before contacting GitHub. Publication
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
