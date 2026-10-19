# Assessment-driven S1 Upstream Contributions test

**Status:** source-first, read-only test contract for the **candidate** Upstream S1
function. This is **not** an activated automation, an effective P1 mandate, a
fourth admitted Organization S1 domain or a permission to modify GitHub.

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
owns the still-unmade S5 choice about the formal fourth-domain scope,
currently `PROPOSED / NOT ADMITTED`. This document only defines the
observable test, not that policy decision.

## Ordered assessment-to-contribution intake

1. **Discover in Index first.** Refresh [canonical Index](https://github.com/opensiro/vsm-harness-index)
   on its current default branch, then inspect candidate records and the
   underlying assessment files. Record an exact, immutable Index commit SHA,
   assessment path/URL, assessed source repository/revision, relevant
   S1–S5 function/ownership finding and supporting assessment evidence.
   **Do not start from a favourite fork, the Upstream registry, a previous
   chat or a convenient open external issue.** Historical Index assessment
   pins remain evidence for what was assessed, not evidence of today's code.
2. **Derive an explicit hypothesis, not a grade repair.** Describe the
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
   preparation adapter supports only a narrow one-new-test-file stage and
   still requires separate exact-action, trusted current-session
   authorization. Fork creation and external PR publication are not silently
   enabled by this test or P1 source-only checks. Do not provision a PAT,
   bypass stage gates or manufacture a host grant.
7. **Validate and return feedback.** Capture implemented diff and tests
   actually run (or the precise stop condition), readback, partial/failed
   operations, owner interventions, external PR/review outcome where it
   exists, and how the outcome informs a later candidate. A green mock CI,
   proposal preview, issue link or PR in OpenSiro is **not** a validated
   upstream contribution. External maintainers own acceptance and merge.
   Preserve Index grades and historical assessment sources; any new
   assessment/reassessment is separately owned by Index/Skills.

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
  existing stage-specific permission gates and the unresolved S5 admission.

**Sources of truth:** Index owns assessments; Profile/Skills own semantics and
assessment method; Upstream owns contribution proposal/implementation/outcomes;
Organization owns Control Plane routing and any future S5 boundary decision.
No standing runtime, new S1 domain, or second Control Plane is required.
