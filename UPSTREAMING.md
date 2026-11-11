# Upstream-local operating contract

**Owner:** `opensiro/upstream`, the admitted OpenSiro Upstream Contributions S1 domain. **Authority:** [Organization bootstrap](https://github.com/opensiro/vsm-oss-organization/blob/main/START_HERE.md) and [S1 domain contracts](https://github.com/opensiro/vsm-oss-organization/blob/main/contracts/s1/domain-contracts.md). This file describes local storage, life cycles and evidence; it creates no new S5 delegation or external publication right.

## Responsibilities

The domain manages evidence-backed upstream improvement proposals, pinned product-native patches and tests, local contribution and fork life cycles, submitted external PR maintenance, and source-linked portfolio reporting. It does not own VSM semantics, the general assessment method, canonical Index findings, Organization's **deprecated historical** intervention-fit classification or the authority to merge into a third-party project.

## Source-of-truth separation

| Subject | Authoritative source | Local materialization |
| --- | --- | --- |
| Canonical general harness assessments | [Index](https://github.com/opensiro/vsm-harness-index), [Skills methodology](https://github.com/opensiro/vsm-harness-skills) | Frozen assessment references in batches and pilot evidence |
| Deprecated four-gate intervention-fit judgments | [Organization historical experiment](https://github.com/opensiro/vsm-oss-organization/tree/main/experiments/upstream-intervention-fit) | Frozen `data/upstream-fit-snapshot.json` for casebook identity/audit; **no active fit KPI** |
| Source-native contribution implementation and exact unpublished PR proposal | Matching verified `opensiro-contributions/<target>` fork: `opensiro/...` code/test branch and fork-local PR to fork default branch | Only branch/head SHA, proposal PR URL, approval evidence and external publication receipts; never a duplicate prospective PR body |
| Current external PR status | Exact third-party GitHub PR | `data/upstream-lifecycle.json`; explicit `data/pr-maintenance/targets.json`; dated observations |
| PR closing actor | Final applicable GitHub issue `closed` event | Dated portfolio report; no automatic assertion about motive |
| OpenSiro-owned fork maintenance | Fork and owner-reviewed local decision | `registry.yaml`, `projects/<slug>/README.md` |
| Native functional effect | Pinned source test and before/after receipt | `pilots/`, `data/functional-effects.json` |
| Technical batch membership and disposition | Frozen local batch manifest and owning issue | `data/assessment-candidate-batches/`, generated Harness Status |
| Additive source → working-fork intentions and handoff pointers | 100-source priority snapshot + frozen technical batch manifests; live fork parent verified independently | Generated `data/contribution-workspaces/registry.json`; [continuous pipeline](docs/CONTINUOUS_WORKING_FORK_PIPELINE.md) |
| One-time supervised public-fork bootstrap and cross-plugin internal PR routing | Exact Upstream source identities, effective batch-stage grants, separate standing external-publication mandate | [Non-executable generated proposal](data/contribution-workspaces/fork-bootstrap-proposal.json), [protocol](docs/FORK_BOOTSTRAP_AND_COLLABORATION.md) |
| Authorized finite external-publication stages | Their exact publication mandate and ledger | `data/corrective-publication/`, `data/improvement-publication/` |
| Shared work selection, S1 boundary, S5 grants | [Organization TODO](https://github.com/opensiro/vsm-oss-organization/blob/main/TODO.md), domain contract and owner decisions | Repository-local issues and explicitly scoped handoffs |

Do not reconcile discrepancies by changing the wrong owner. A current PR readback may require updating an Upstream receipt, but it never silently updates the Organization fit snapshot.

## Native test execution boundary

The native test **packet and receipts** are Upstream-owned; the external harness's **CI execution** belongs in a stage-authorized `opensiro-contributions/<target>` working fork or a separately controlled deterministic runner. Use [the native CI placement contract](docs/NATIVE_CI_EXECUTION.md) before introducing any target-specific GitHub Actions file. The existence of an OpenSiro-owned fork or a validated patch never grants new fork, branch, PR or maintainer rights; [#6](https://github.com/opensiro/upstream/issues/6) remains the general executor gate.

## Contribution lifecycle

1. **Admit and pin a source:** verify project identity, revision, license and stage-specific rights. New standard `batch upstream` screening freezes five distinct Index-origin sources under [the batch contract](docs/ASSESSMENT_CANDIDATE_BATCHES.md); it is not the Index assessment publication queue.
2. **Diagnose and prepare:** reproduce a product-native problem with deterministic source-native tests. Keep screening, assessment-derived and assessment-informed origin labels separate ([protocol](docs/ASSESSMENT_TO_IMPROVEMENT.md)).
3. **Retain technical evidence in Upstream:** record the source SHA, patch/recipe, negative/positive native test receipt, scope and limitations; use an internal reviewable PR for a material evidence or registry change where appropriate. **Do not create a separate internal PR solely to store the title/body of a prospective third-party PR.** A technical packet is not itself the external delivery.
4. **Autonomously prepare the executable contribution in its working fork:** under the revocable [standing preparation mandate](docs/STANDING_PREPARATION_AUTONOMY.md) and [#6](https://github.com/opensiro/upstream/issues/6), no new owner prompt is needed per source, fork or commit in a qualifying five-repository wave. The host still verifies the current-main policy and internally issues an exact bound execution decision for every write. Verify the matching public parent, rights and base; put the actual code/tests on an `opensiro/...` branch in `opensiro-contributions/<target>`, run permitted native checks, and read back the final commit and diff. If the real host/provider capability is missing, record `WAITING_FOR_TRUSTED_EXECUTOR` rather than asking the owner to approve preparation again or manufacturing a stand-in Upstream PR.
5. **Prepare, validate and publish the source-local proposal:** after verifying the actual working diff, create a **fork-local PR** from its `opensiro/...` branch into the matching fork default branch. Its title/body are the one authoritative unpublished external-PR proposal, using the **target's current PR template and contributor rules** (headings, evidence, checkboxes, DCO/CLA, tests), followed by the [mandatory AI-assisted disclosure](docs/AI_ASSISTED_PR_DISCLOSURE.md). Never add a proposal file to the outgoing code branch, or mirror its full prose in Upstream. Under the [standing external-publication mandate](docs/STANDING_EXTERNAL_PR_PUBLICATION.md), **do not request additional per-PR owner approval**: instead verify the fork-local PR URL, exact title/body and unchanged source/fork head/base SHAs and all mandatory source-native gates before every POST. With effective publication rights, open the real third-party PR **Open · Ready for review** (`draft: false`), reserving Draft for a documented target-permitted condition. Read back the final PR; a fork-local PR by itself is not an external publication. See [fork-local proposal contract](docs/CONTINUOUS_WORKING_FORK_PIPELINE.md#fork-local-pr-proposal-contract) and [source-native PR gate](docs/ORGANIZATION_FORK_UPSTREAM_PR.md#source-native-pr-form-and-contributor-requirements).
6. **Maintain after publication:** after actual GitHub PR readback, update the reviewed Upstream ledger/watchlist, then monitor review, CI, new maintainer feedback and lifecycle changes through [PR maintenance](docs/PR_MAINTENANCE.md). Do not treat an opened PR as accepted.
7. **Resolve or archive:** record merged, closed-without-merge, open or unverifiable PR state. Attribution, product effect and intervention success require independent evidence. Fork archival is an explicit owner decision, not an effect of PR merge.

## Portfolio denominators

- **Watchlist PR view:** the reviewed explicit manifest at `data/pr-maintenance/targets.json`; official resolved-PR formula is `MERGED / (MERGED + CLOSED_UNMERGED)`. Open and unverifiable targets remain outside the denominator. This is not an experiment-fit rate.
- **Broad PR union:** deduplicate the watchlist with all original/replacement casebook PR URLs and registered external PR URLs. `scripts/portfolio_reconcile.py` computes a separate, live, **read-only** observation without editing the explicit watchlist.
- **Intervention view:** a replacement PR may complete an existing intervention; an independently implemented idea is not a contributor merge. No automatic adoption/fit score is inferred from the broader PR union.
- **Technical batches and publication queues:** these are separate scopes, not additional additive contributions to the same PR denominator.

Every report must identify the cohort, observation time, source and whether it counts **PR URLs**, distinct interventions, native behavior or Organization-reviewed fit. Historical percentages must not be relabeled as current production rates.

## Generated artifacts and checks

| Materialization | Owning implementation | Check |
| --- | --- | --- |
| `DASHBOARD.md`, `docs/index.html`, generated `cases/README.md` section | `scripts/upstream_status.py` | `--check-generated` |
| `HARNESS_STATUS.md` | `scripts/harness_status.py` | `--check` |
| Functional effects view | `scripts/functional_effects.py` | Its deterministic validation |
| Resolved-PR inbox summary | `scripts/resolved_pr_acceptance.py` | Explicit manifest and GitHub exact-PR readback |
| Broad portfolio observation | `scripts/portfolio_reconcile.py` | `--validate-only` offline, `--report` live; no repository writes |
| Verified external outcome evidence | `scripts/verified_external_outcomes.py` → `scripts/accepted_external_outcomes.py` | [Evidence contract](docs/VERIFIED_EXTERNAL_OUTCOMES.md), offline `--validate-only`, live candidate observation + independently rechecked merged-change acceptance export; Organization metric activation is a separate consumer gate and **not** proof of deployed benefit |
| Additive working-fork inventory | `scripts/contribution_workspaces.py` | `sync` with every internal technical-record change; `check` in unfiltered PR CI; not a fork-write grant |
| Historical experiment and pilot directory catalog | `scripts/pilot_catalog.py` | `sync` with any pilot file change; `check` in unfiltered PR CI; never a success/outcome inference |

Do not manually change generated rows. Refresh upstream PR receipts atomically after a verified state change and review the resulting diff. CI tests and reviewable PRs are the local integration path, not authority for third-party writes.

## Internal PRs and branches

An internal PR is either active integration work, research-only evidence, blocked design/authority work or explicitly superseded after review. Draft status, age, merge-conflict flags and passing CI are **not** enough to close or merge it. [Issue #150](https://github.com/opensiro/upstream/issues/150) governs disposition review; [#130](https://github.com/opensiro/upstream/issues/130) governs repository settings and branch retention.

`main` is protected; merged-PR branches were pruned after verified reconciliation on 2026-11-06. Six closed-unmerged internal PR branches were deliberately retained: #7, #17, #18, #52, #68 and #110. Any future deletion requires fresh SHA/PR/protection verification and an explicit decision. The current live branch count is not frozen in this contract.

## Non-activation and license guard

The connected fork/stage executor remains gated by an **active, authenticated standing preparation mandate** and real host/provider capabilities under [#6](https://github.com/opensiro/upstream/issues/6). This transfers the owner's routine preparation decisions, **not** GitHub credentials or proof that every writer is live. Optional Git compare-and-swap batch reservation under [#144](https://github.com/opensiro/upstream/issues/144) is source-prepared, not an active scheduler. The repository root does **not** currently contain an adopted LICENSE; [#130](https://github.com/opensiro/upstream/issues/130) and [PR #1](https://github.com/opensiro/upstream/pull/1) require a real copyright/owner disposition.

See [docs/OPERATIONS.md](docs/OPERATIONS.md) for commands, workflows and the bounded scale-up path.
