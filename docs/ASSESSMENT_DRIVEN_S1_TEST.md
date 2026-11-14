# Assessment-driven S1 Upstream Contributions test

**Status:** source-first, read-only contract for the **assessment-derived test within the admitted Upstream S1 domain**. This does **not** activate an independent executor, assign an `S1=A` grade, widen publication rights or authorize GitHub writes.

## Purpose and command ownership

The existing [Organization Control Plane](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/AGENT_CONTROL_PLANE.md)
routes `test S1 function: upstream contributions` here. This particular test
asks whether OpenSiro can turn **findings from canonical VSM assessments of AI
harnesses into independently useful, upstream-native OSS contributions**, with
honest provenance, engineering validation and feedback.

This is deliberately **not** the generic `contribute to other harnesses`
discovery flow. The broad Upstream portfolio, ordinary GitHub-issue-driven
contributions and existing casebook remain valid separate work; they must
**not** be counted as passing this narrower assessment-driven S1 test.
[Organization #274](https://github.com/opensiro/vsm-oss-organization/issues/274)
has admitted Upstream as the bounded fourth operational S1 domain; that decision does not prove this specific assessment-derived experiment or activate additional external rights.

## Read-only first quality-census launch (2026-11-13)

The source-owning [hypothesis quality census](../scripts/assessment_hypothesis_quality.py)
can be run on the most recent eight frozen five-source batches without
creating a new status ledger, scheduled workflow, discovery/selection mandate,
or claim about deployed product impact:

```bash
python3 scripts/assessment_hypothesis_quality.py --last 8
python3 scripts/assessment_hypothesis_quality.py --last 8 \
  --output-json /tmp/upstream-quality.json --json
```

First baseline: [batches 27–34](../reports/2026-11-13-assessment-hypothesis-quality-baseline.md).
The script validates frozen manifests and source-backed publication receipts,
counts selection outcomes, and distinguishes recorded `ASSESSMENT_DERIVED`
origins from technical/maintainer success. It only confirms existence of
preregistration packets, **not** their commit chronology, independent native
runner proof, live external PR state, Organization acceptance, or measured user
benefit. Those remain separate, explicitly unclaimed gates under #56.

## Functional improvement evidence

Use the [assessment-to-improvement protocol](ASSESSMENT_TO_IMPROVEMENT.md)
for the stronger evidence claim. An assessment-related contribution is not
necessarily an assessment-derived diagnosis.

**Required test method:** follow its [pre-registered hypothesis and separate execution](ASSESSMENT_TO_IMPROVEMENT.md#pre-registered-hypothesis-and-separate-native-execution--2026-11-08-refinement) and [native scripted tests only](ASSESSMENT_TO_IMPROVEMENT.md#mandatory-validation-boundary--native-scripted-tests-only) rules. For new strict-derived claims, the assessment-motivated hypothesis must be checkpointed before fresh target-code/issue inspection; a separate deterministic CI/runner must execute pinned, matched first-party before/after checks and preserve attributable logs. The chatbot may design and review these checks but not directly run them as their validator. **No live LLM-agent runs, model API tests or Browser agent-quality sessions are required or authorized as part of this experiment.** Do not make them a technical completion gate or a condition for permissioned upstream submission.

- `ASSESSMENT_DERIVED`: an observed functional finding, discovered from
  canonical Index first, motivates a falsifiable upstream-native improvement.
- `ASSESSMENT_INFORMED`: assessment establishes subsystem relevance,
  while a separate issue/code investigation identifies the concrete defect.
- `GENERAL_UPSTREAM`: no demonstrated functional-finding linkage.
- `INSUFFICIENT`: a required provenance or linkage item cannot be verified.

Keep this origin class separate from execution status and from the observed
product-effect verdict. For a strong derived case, require a documented
pre-change behavior and safety criterion, a matched post-change evaluation
and an explicit benefit/no-benefit/inconclusive result. Passing CI validates
the check, not a changed product capability. Do not invent a functional
deficit from a grade or retroactively attach an Index finding to an already
chosen issue.

The existing [HarnessDesk #1772](../pilots/harnessdesk-1772/ASSESSMENT_LINKAGE_2026-10-20.md)
pilot is `ASSESSMENT_INFORMED`. A new Index-first functional-gap experiment
is tracked in [Upstream #56](https://github.com/opensiro/upstream/issues/56).

The [upgrade-batch selection contract](ASSESSMENT_CANDIDATE_BATCHES.md#control-plane-command-upstream-upgrade-batch) now **prefers independently needed minor/major native capabilities** across S1–S5, while accepting a well-substantiated **bug-fix fallback** when no suitable feature exists. Under [capability-first research v0.9.0](CAPABILITY_FIRST_RESEARCH.md), a **new user task and measurable native result** must be articulated before extending reliability research. A demonstrated repair does not alone complete a VSM-derived new-capability cycle. The existing `ASSESSMENT_DERIVED` / `ASSESSMENT_INFORMED` distinction, four native-fit gates, separate runner and actual product-effect verdicts remain authoritative; this is not a new S1 test, command or metric. For new Index cohorts with non-A S1, use the prospective v2 manifest without changing frozen v1 assessments.

## Ordered assessment-to-contribution intake

For repeated operator `continue`/`продолжай` instructions inside #56, use the
[frozen candidate-batch continuation protocol](ASSESSMENT_CANDIDATE_BATCHES.md):
finish the furthest legitimately available per-candidate step, record any
external permission handoff, **advance to the next screening row**, and roll
over to a new full batch only after the current cohort is resolved. A prepared
external PR packet is not a reason to idle or repeat native tests. These
read-only selection semantics do not grant GitHub rights and do not replace
the strict single-candidate origin/fit/admission gates below.

1. **Discover in Index first.** Refresh [canonical Index](https://github.com/opensiro/vsm-harness-index)
   on its current default branch, then inspect candidate records and the
   underlying assessment files. Record an exact, immutable Index commit SHA,
   assessment path/URL, assessed source repository/revision, relevant
   S1–S5 function/ownership finding and supporting assessment evidence.
   **Do not start from a favourite fork, the Upstream registry, a previous
   chat or a convenient open external issue.** Historical Index assessment
   pins remain evidence for what was assessed, not evidence of today's code.
2. **Derive and checkpoint an explicit hypothesis, not a grade repair.** Before fresh target-code/issue inspection, record a dated, attributable prediction, null/falsifier and assessment evidence. Describe the
   behavior/coordination mechanism the harness might benefit from and which
   assessment finding motivated it. `S3=—`, `S4=P` or any other grade
   is **not** itself a bug, product requirement, missing feature or reason to
   improve the score. The target's system-in-focus is the external harness;
   keep its technical value independent from changing Index classifications.
3. **Independently validate the upstream-native opportunity.** Read the
   harness's **current** default-branch revision, relevant implementation,
   `CONTRIBUTING`, licensing/CLA, existing issues/PRs and overlap. Require a
   source-backed need or demonstrated technical shortfall (a maintainer
   request is helpful but not the only form of primary evidence), a concrete
   native mechanism, counterfactual value without VSM labels, and fit with
   current scope. Record `PASS`, `PENDING` or `FAIL` separately for
   **need**, **mechanism**, **counterfactual value** and **scope**; do not
   silently promote an unsupported fit claim to `PASS`.
4. **Admit only a qualified assessment-linked candidate.** Trace the chain
   `Index assessment @ SHA → harness/finding → current upstream evidence
   → bounded improvement/test → expected unverified benefit`. A proposal
   with no matching Index assessment, no falsifiable engineering benefit,
   changed upstream identity or unresolved negative fit gate is
   `NO_ELIGIBLE_ASSESSMENT_CANDIDATE` / `BLOCKED_EVIDENCE`, not permission
   to swap in a random GitHub issue. If no candidates qualify, stop the
   discovery test with a truthful negative result.
5. **Propose, select and prepare.** For a qualified candidate, use the
   existing [proposal-only preview](BATCH_PROPOSALS.md) and the
   [one-stage Control Plane handoff](CONTROL_PLANE_HANDOFF.md). The canonical
   `proposal.evidence_url` should point to independently checked upstream
   primary evidence; preserve the separate Index assessment provenance in
   the test report. Current draft manifests do not encode or cryptographically
   verify the Index link: this is a **test prerequisite enforced by source
   inspection and reporting**, not a new claim that the existing JSON
   validator enforces it. Selection/hash means preview only.
6. **Exercise stages only under their own rights.** Record whether a real
   `create_public_fork`, `prepare_contribution`, or `submit_external_pr`
   took place, by whom and with which exact source/destination GitHub refs.
   An existing fork does **not** prove new fork creation. The connected
   trusted-host preparation now supports *bounded* source-native two-file
   patches under [standing preparation P1](STANDING_PREPARATION_AUTONOMY.md).
   Its opaque one-use decisions still require a trusted current-session
   stage decision, exact current-main policy, actor/source/fork checks and
   fresh commit readback. Separate
   [standing publication P1](STANDING_EXTERNAL_PR_PUBLICATION.md) authorizes
   qualified third-party PRs without per-PR owner prompts. Neither mandate
   follows from this assessment test, permits unreviewed arbitrary patches,
   waives legal attestations or grants external merge rights.
7. **Validate via a separate deterministic runner and return feedback.** Capture implemented diff and independently executed native tests
   (or `BLOCKED_INDEPENDENT_EXECUTION`), run URL, source/test pins, commands, logs, readback, partial/failed
   operations, owner interventions, external PR/review outcome where it
   exists, and how the outcome informs a later candidate. A green mock CI,
   proposal preview, issue link or PR in OpenSiro is **not** a validated
   upstream contribution. External maintainers own acceptance and merge.
   Preserve Index grades and historical assessment sources; any new
   assessment/reassessment is separately owned by Index/Skills.

## Working fork execution under the current P1 envelope

A qualified Index-derived candidate uses an authentic public direct fork in
**`opensiro-contributions`**, not a personal or coincidentally named fork.
The [working-fork pipeline](CONTINUOUS_WORKING_FORK_PIPELINE.md), [fork route](OPENSIRO_CONTRIBUTIONS_FORK_ROUTE.md)
and [Upstream #28](https://github.com/opensiro/upstream/issues/28)
own stage capability, exact authority and provider readback. The connected
GitHub integration cannot generally create forks; the separately authenticated
`dev-alpha-2` trusted-host route has demonstrated bounded source-native
preparation, including [Revka's two-file fork-local PR #1](https://github.com/opensiro-contributions/Revka/pull/1).
This does **not** imply arbitrary patch support or authorize retries after an
unknown write. Verify current source/fork base SHA, direct parent, branch,
native tests and trusted stage decision for *each* operation. Nondefault
source branches such as HarnessDesk `development` must not be replaced with
an unrelated fork `main`. Qualified external publication follows separate
standing P1 checks; CLA/DCO, security-policy and maintainer gates remain.

## Offline Index-origin consistency gate (implemented)

The read-only [`assessment_origin_preflight.py`](../scripts/assessment_origin_preflight.py)
checks one **already checked-out, exact-HEAD local Index git object** against one
existing Upstream `proposal_only` candidate. It requires an included
canonical-shaped assessment in the correct shard, a full 40-hex `review_ref`,
the six literal function states, and **matching proposed upstream repository**.
It reads assessment bytes from `git show <index-sha>:<path>` rather than
uncommitted workspace files. It rejects absent/mismatched candidates, missing
origin or blocked proposals; it never calls GitHub or mutates a repo.

```bash
python3 scripts/assessment_origin_preflight.py \\
  --index-root /path/to/local/vsm-harness-index \\
  --index-sha <40-hex-index-commit-sha> \\
  --assessment-path assessments/xx/harness-id.md \\
  --manifest /path/to/upstream-YYYYMMDD-slug.json \\
  --candidate exact-candidate-id
```

Output `LOCAL_INDEX_ORIGIN_PRECHECK_ONLY` carries the exact assessment hash,
Index/object identity, target match and unsigned proposal digest. It
**always** returns `NOT_APPROVED_NO_GITHUB_WRITES`,
`execution_available=false`, `native_fit=UNVERIFIED` and
`canonical_index_source=UNVERIFIED` (under the corresponding explicit
result-field names). A synthetic local checkout can pass its consistency
checks; **a trusted agent must independently verify the supplied Index SHA/path
against live canonical GitHub**, current upstream source, real native
need/fit, licences, duplicate PRs and its actual stage-specific grant.

This is an incremental executable **provenance-consistency prerequisite**, not
cryptographic remote attestation, admission, automatic candidate discovery,
or connected-host authorization. It does not change the generic batch schema
or replace the per-stage Upstream #6 gates.

## Composed assessment-driven Control Plane packet (offline)

After the local Index-object preflight, use
[`assessment_driven_handoff.py`](../scripts/assessment_driven_handoff.py) to
bind **one exact accepted assessment identity to one Upstream proposal and
one `prepare_contribution` test-file plan**. The composition calls the
existing Index-origin preflight and `control_plane_handoff.py`, checks their
candidate/upstream/proposal digests agree and emits one
`ASSESSMENT_DRIVEN_HANDOFF_PREVIEW_ONLY` packet. It exposes no `--execute`
flag and never writes to GitHub.

```bash
python3 scripts/assessment_driven_handoff.py \\
  --index-root /path/to/local/vsm-harness-index \\
  --index-sha <40-hex-index-commit-sha> \\
  --assessment-path assessments/xx/harness-id.md \\
  --manifest /path/to/upstream-YYYYMMDD-slug.json \\
  --candidate exact-candidate-id \\
  --working-repo contributor/existing-fork \\
  --base-branch main --base-sha <40-hex-fork-base-sha> \\
  --new-branch opensiro/test-candidate \\
  --file-path tests/test_candidate.py \\
  --content-file /path/to/test_candidate.py
```

This removes **accidental loss of the Index origin** across two local
preview stages; it does not authenticate the local checkout against public
GitHub, establish real product-native fit, guarantee fork identity or grant
current-session operator consent. The output always lists these still-open
gates, with `execution_available=false`. The existing
`connected_stage_adapter.py` remains separately gated and is **not**
invoked by this command.

## Minimum test receipt

A human-readable or machine-readable report must contain at least:

| Field | Required observation |
| --- | --- |
| `index_assessment` | Index assessment path/URL **and** immutable Index SHA; assessed harness upstream/revision; finding, function/ownership and source evidence |
| `origin_strength` | `ASSESSMENT_DERIVED / ASSESSMENT_INFORMED / GENERAL_UPSTREAM / INSUFFICIENT`, with a dated prospective hypothesis checkpoint, selection-order and causal evidence rather than just a related assessment URL |
| `before_after_effect` | Reproducible pre-change behavior, relevant benefit/safety metric, matched after-change test and `BENEFIT_SUPPORTED / NO_BENEFIT_OBSERVED / INCONCLUSIVE`, with independent runner run/artifact + code/test refs, or explicit untested blocker |
| `fresh_upstream` | Upstream owner/repository, current default-branch SHA, current relevant code/issue/PR URLs and policy/licence check |
| `hypothesis` | Assessment-motivated problem, concrete upstream-native mechanism, expected benefit and falsifier/test |
| `native_fit` | Separate need/mechanism/counterfactual/scope `PASS/PENDING/FAIL` with actual source links |
| `proposal` | Bounded Upstream candidate/manifest ID, selected stages, blockers and preview receipts, **not** approval |
| `authority` | Who actually selected, authorized and performed each allowed stage; unsupported operations and missing grants |
| `execution` | `SOURCE_PREPARED / OBSERVED / EXERCISED / CLOSED / BLOCKED / UNKNOWN`, exact GitHub refs, tested bytes/diff, CI/tests and honest recovery |
| `feedback` | Review/acceptance/rejection or pending outcome, next-work consequence and attribution/uncertainty |

Return `PARTIAL` or `INSUFFICIENT` whenever an end-to-end loop or decisive
owner is unproven. A test with no eligible assessment-derived candidate is a
valid bounded **negative discovery result**, not a completed contribution.
These labels are test observations, **not** a canonical `S1=A/C/C(P)` grade.

## Boundaries and negative examples

- **Do not pass:** start from Cognee because a fork already exists, then
  reverse-engineer an Index justification for an unrelated issue. A Cognee
  assessment can qualify only if its actual finding motivates the particular
  native change and all fit gates are separately supported.
- **Do not pass:** identify a low VSM grade and add a generic manager/reviewer
  merely to increase that grade.
- **Do not pass:** reuse an assessment-shaped historical PR or an existing
  fork as proof of a fresh automated `create_public_fork` stage.
- **Do not pass:** use a synthetic candidate, `approved_by` field, unsigned
  digest or `authorize=True` mock as a real operator decision.
- **Preserve:** generic external OSS discovery, the portfolio/casebook,
  separate local Upstream mandate authority, manual external PR publication,
  existing stage-specific permission gates and the bounded S5 admission.

**Sources of truth:** Index owns assessments; Profile/Skills own semantics and
assessment method; Upstream owns contribution proposal/implementation/outcomes;
Organization owns Control Plane routing and any future S5 boundary decision.
No standing runtime, additional S1 domain, or second Control Plane is required.
