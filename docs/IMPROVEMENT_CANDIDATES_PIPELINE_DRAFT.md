# Improvement candidates — separate intake from upstream execution (DRAFT)

**Owner:** `opensiro/upstream`. **Design status:** proposal for review, **not an activated workflow**, new S1 domain, delegation, permission, or new Index methodology.
**Experiment:** [Upstream #56](https://github.com/opensiro/upstream/issues/56); [AgentBox #61](https://github.com/opensiro/upstream/issues/61).
**Existing source of truth:** [assessment-to-improvement](ASSESSMENT_TO_IMPROVEMENT.md), [assessment-driven S1 test](ASSESSMENT_DRIVEN_S1_TEST.md), [batch proposal preview](BATCH_PROPOSALS.md), [handoff](CONTROL_PLANE_HANDOFF.md). This document proposes a missing **object boundary**, not a replacement for those contracts.

## Problem

The existing test narrates a linear chain from one canonical VSM assessment through a single selected improvement and onward to an upstream contribution. In practice:

- **one assessment can motivate multiple incompatible improvement hypotheses** (e.g. AgentBox file-overlap planning and its independently discovered `dependsOn` status semantics);
- independent investigation may reject or park an idea after a useful source-native test (Zot), **without** creating a contribution;
- a product issue may be independently useful but **not strictly assessment-derived**;
- treating `batch_proposals.py` candidate rows as discovery records prematurely requires fork names and proposed GitHub write stages for hypotheses that should never reach execution.

Therefore introduce a **research-only, many-candidate intake** between Index and the existing contribution proposal lifecycle.

## Proposed pipeline

```text
Index: accepted general VSM assessment @ immutable Index commit
       | (read-only observation; never invent a missing-function bug)
       v
Upstream: improvement candidate intake [NEW]
       | one assessment → zero, one, or many independently named candidates
       | individual native need/fit, scope, baseline, blockers, negative outcomes
       | candidate may remain PARKED / REJECTED without a fork
       v
Upstream: qualified candidate selection (owner decision; still NO WRITE RIGHT)
       | only after four native-fit gates and provenance check
       v
Upstream: existing proposal-only batch / one-stage handoff [UNCHANGED]
       | scoped technical plan + separate exact-action authorization
       v
Contributor fork: bounded patch + matched native before/after [EXISTING ROUTE]
       | verified product effect; no grade assumptions
       v
External upstream issue/PR (separately authorized) → maintainer feedback
       |
       +--- feedback updates the originating candidate (not Index automatically)
```

**Implementation rule:** no new agent, service, database, automated sorter, GitHub fork or writing right. Candidate cards are linked Markdown research records under [`candidates/`](../candidates/README.md); live source/issue/release status remains authoritative in its owning repository. The canonical Index assessment **does not** store improvement candidates; Index is the fact source for the assessed system, Upstream owns hypotheses and contribution outcomes.

## Candidate identity and minimum fields

A candidate is a **one specific product behavior change hypothesis**, not a VSM label, upstream PR, GitHub fork or priority claim.

| Field | Required meaning |
| --- | --- |
| `candidate_id` | Stable Upstream-local ID, unchanged through screening; use a separate card for each substantially different intervention |
| `target_repo` | Actual third-party repo; retain the assessed `review_ref` and today's checked default source separately |
| `origin_class` | `ASSESSMENT_DERIVED`, `ASSESSMENT_INFORMED`, `GENERAL_UPSTREAM`, or `INSUFFICIENT` with real selection-order evidence; hypothetical class can remain `INSUFFICIENT` |
| `index_origin` | Immutable Index SHA + assessment path + precise S-function/finding and the selection-order receipt where applicable; no backfilled or invented linkage |
| `problem` | Actual user-relevant behavior/first-party roadmap or incident; distinguish observed code metadata from actual worker action |
| `hypothesis` | Exactly one proposed mechanism plus null outcome / competing explanation, expected non-VSM product benefit |
| `native_fit` | Separate **need / mechanism / counterfactual value / scope** verdicts `PASS / PENDING / FAIL`, sources, and any narrower qualified claim |
| `evidence` | Source SHA, verified baseline, duplicates, tests and confounders; links to canonical receipts rather than pasted status snapshots |
| `state` | Candidate research state independent of contribution state, fork lifecycle and external review |
| `next_gate` | One falsifiable next check, named decision owner, blocker, and no unearned permission |
| `downstream` | Exact proposal/case/PR refs **only after they exist**; no invented planned fork counted as a created fork |

### Candidate research states (proposed)

- `DISCOVERED` — an evidence-linked hypothesis exists; not yet qualified.
- `SCREENING` — current first-party need, duplicates and four fit gates being assessed.
- `BLOCKED_EVIDENCE` — decisive evidence or design semantics unavailable; **not executable**.
- `QUALIFIED` — all four fit gates have evidence-backed `PASS`; a before/after protocol and remaining boundaries are explicit. **Not authorized to write to external GitHub.**
- `SELECTED` — a qualified candidate was intentionally chosen for the existing contribution **proposal-only** handoff. Selection is not an exact-action grant.
- `PARKED` — low demand, stale opportunity, deliberate design boundary or competing implementation. Can resume after new evidence.
- `REJECTED` — disproven or incompatible hypothesis, preserving the negative result and sources.

`baseline_status` (`NOT_RUN/MEASURED`), `effect_verdict` (`NOT_TESTED/BENEFIT_SUPPORTED/NO_BENEFIT_OBSERVED/INCONCLUSIVE`) and `contribution_status` (existing repository `research/preparing/submitted/merged/closed/not-accepted`) are **separate dimensions**. Do not mark a candidate `QUALIFIED` just because CI passed; do not mark a PR `merged` because a candidate was selected.

## Gate contract: candidate → proposal is an explicit transition

Before generating a `batch_proposals.py` `proposal_only` row for the **assessment-driven** route, verify:

1. The recorded Index origin is genuinely first in the discovery chain, and the proposed change follows a **specific observed functional finding** (or classify `ASSESSMENT_INFORMED` and do not count as strict assessment-derived).
2. Fresh upstream code, maintainer/product evidence, overlapping PRs, licence/CLA/DCO and the actual development branch are checked.
3. Four native-fit gates each have `PASS`, not `PASS_ROADMAP` standing in for approval of an exact API design. A credible `BLOCKED_EVIDENCE` candidate stays in the pool.
4. There is a falsifiable protocol for real target behavior **before** and after, including a null/negative outcome and safety regressions.
5. A reviewer/operator records a selection rationale and links the stable `candidate_id` to one concrete proposal ID/digest; this **does not** authorize any fork/patch/PR.

The generic OSS upstream path remains independently available. Its user-chosen candidates do not retroactively become Index-derived by attaching an assessment link.

## One-to-many / lifecycle edge cases

- An assessment can yield **zero qualified candidates**; report a valid negative discovery result.
- Multiple candidates for one system remain separate until an explicit scoped decision to combine them; combining does not upgrade weaker provenance. Prefer small interventions.
- One candidate can have multiple experiments and negative receipts; preserve attempts instead of overwriting historical evidence.
- Rejected/parked candidates remain linkable and do not create empty `registry.yaml` fork entries. `registry.yaml` continues to represent **actual forks/contributions**, not the candidate backlog.
- If a new Index revision or first-party main commit changes the premise, recheck and record the replacement evidence without rewriting the frozen assessment.
- Successful candidate selection or external PR acceptance does **not** change S2/S3 grades or Organization S1 admission. A distinct Index reassessment is the only path to a new canonical assessment.

## Draft rollout and review questions

**This PR remains a DRAFT design, plus a small executable _offline, read-only_ integrity check.** [`inspect_improvement_candidates.py`](../scripts/inspect_improvement_candidates.py) and [its test suite](../tests/test_inspect_improvement_candidates.py) check stable IDs, pinned-reference syntax, state/fit declaration coherence, source/evidence-card structure and non-duplication; the [credential-free CI workflow](../.github/workflows/improvement-candidates.yml) executes them. They do **not** validate live source or user benefit, attest provenance/fit, select a candidate, create a proposal, or authenticate/authorize any action. `declared_fit_complete=true` is only locally asserted metadata.

Proposed adoption sequence: review this boundary → accept/adjust candidate state names → retain/retire initial research cards → separately review an explicit candidate-to-existing-proposal transition, with verified live evidence and operator decision, if/when a candidate qualifies → then amend the authoritative S1/proposal contracts in another reviewable change. No automatic sorter, execution gate or new agent is introduced.

Questions for review:
1. Should `QUALIFIED` require maintainer feedback **only when** the target design is not already established, rather than for every independently validated bug fix? (Proposed: yes, require acceptance of the actual behavior, not a ritual comment.)
2. Is the human/operator selection point placed correctly **after** candidate qualification and **before** any existing `proposal_only` draft?
3. Should improvements across several assessed harnesses be comparable by **native benefit/evidence** without collapsing them into VSM grades or automatic ranking? (Proposed: yes; no ranking algorithm yet.)

See initial [research-only candidate cards](../candidates/README.md) and the [unpublished AgentBox upstream issue draft](../pilots/agentbox-s2/AGENTBOX_DESIGN_INQUIRY_DRAFT.md).
