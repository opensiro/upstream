# Upstream operations and automation

Use [UPSTREAMING.md](../UPSTREAMING.md) for data ownership and permission boundaries. The implementation and schedules below are **local observations**, never automatic external publication authority.

## Work and integration

1. Bootstrap from [Organization START_HERE](https://github.com/opensiro/vsm-oss-organization/blob/main/START_HERE.md), follow the owner map and the exact task/PR.
2. Inspect the source SHA, license and native test contract; reserve/collision-check a source only under the actual [batch policy](ASSESSMENT_SOURCE_RESERVATIONS.md).
3. Retain source-pinned patch/test receipts in Upstream; use a reviewable internal PR only for material evidence or registry changes. Do **not** open an internal PR just to hold a future external PR description.
4. Where a [trusted stage grant](CONTINUOUS_WORKING_FORK_PIPELINE.md) is effective, prepare and validate the actual code/tests in the matching `opensiro-contributions/<target>` fork's `opensiro/...` branch. Otherwise preserve the precise permission blocker; do not replace a missing fork/branch write with a documentation-only "publication" wave.
5. Prepare the final external title/body from the tested fork diff and target-native PR form, verify the [current standing external publication mandate](STANDING_EXTERNAL_PR_PUBLICATION.md) and all native gates without requesting a new per-PR approval, publish only when permitted, and record the GitHub readback in the local registry/watchlist.
6. Validate local ledgers and generated views. CI passing does not imply external acceptance or an S5 grant. Keep internal merge, fork preparation, external PR submission, repair, and eventual fork archival distinct.

## External native CI placement

For a short **which Action does what** view and the historical cleanup queue,
start with [GitHub Actions ownership](ACTIONS.md). The dated
[Actions audit](../reports/2026-11-11-actions-audit.md) reconciles GitHub's
registered-workflow list with the files on `main`; registered workflows
from an open PR are not safe to disable without checking that PR.
The [run-volume audit](../reports/2026-11-11-actions-run-volume.md)
explains why cumulative run counts are not operating cost and records the
retirement of the duplicate fork-lifecycle test workflow; the unfiltered
`repository-integrity` job remains responsible for the full suite.

Use [native CI placement](NATIVE_CI_EXECUTION.md) for assessment-derived and ordinary source-native patches. The `.github/workflows/` files here are for Upstream's own validation, read-only observation and explicitly gated operations, **not** a new workflow per outside project. First-party before/after tests run in an authorized `opensiro-contributions` working fork or separately controlled deterministic runner; retain independently attributable logs, source/test/patch pins and outcome receipts here. Never infer permission to create a fork or publish a PR from the existence of a test workflow.

Project-specific legacy workflows are migration candidates, not automatically deletable: preserve their runs, active triggers and evidence before moving or retiring them. In particular, [merged PR #174](https://github.com/opensiro/upstream/pull/174) has a completed Runloop CI pilot, but its project-specific workflow was **not** merged to `main`. Its source-pinned historical run is not a reason to reintroduce the workflow. The [2026-11-11 audit](../reports/2026-11-11-actions-audit.md) records the subsequently disabled obsolete registration.

## Offline verification

```bash
python3 -m unittest discover -s tests -v
python3 scripts/upstream_status.py --check-generated
python3 scripts/harness_status.py --check
python3 scripts/pr_maintenance_watch.py --validate-only
python3 scripts/resolved_pr_acceptance.py --validate-only
python3 scripts/corrective_publication_queue.py validate
python3 scripts/portfolio_reconcile.py --validate-only
python3 scripts/verified_external_outcomes.py --validate-only
```

The unfiltered [repository-integrity workflow](../.github/workflows/repository-integrity.yml) runs offline tests on every internal PR and on pushes to `main`. It **is required** on protected `main` after the staged [Organization #305](https://github.com/opensiro/vsm-oss-organization/issues/305#issuecomment-6808962191) rollout: GitHub admin readback binds the context to GitHub Actions app `15368`, `strict=false`, and a deliberately failing non-Draft [PR #245](https://github.com/opensiro/upstream/pull/245) was blocked. No extra reviewer or weakening of existing conversation-resolution protection was introduced.

## External observation (read-only)

| Job or command | Cadence / trigger | Effect |
| --- | --- | --- |
| [PR maintenance](../.github/workflows/pr-maintenance.yml) | Hourly and manual | Read external PR reviews/CI; update only this repo's bounded issue #125 inbox |
| [Resolved PR acceptance](RESOLVED_PR_ACCEPTANCE.md) | Alongside maintenance | Observe the separate 18-target cohort and update its own bot-owned summary in #125 |
| [Portfolio reconciliation](../.github/workflows/portfolio-reconciliation.yml) | Daily and manual | GET exact watched, historical and registered PRs; write the run summary **and a 90-day JSON artifact**; no issue edit, Git commit or external write |
| [Verified external outcome evidence + joined PR report](../.github/workflows/verified-external-outcomes.yml) | Daily and manual | Recheck third-party merges/native CI, then join the current portfolio to independently accepted results in one source-linked summary and JSON artifact; no deployed-benefit KPI; read-only |
| [Status freshness](../.github/workflows/upstream-status-freshness.yml) | Daily | Verify stored lifecycle against live PRs; fail on drift, no auto-change |
| [Lifecycle proposal](../.github/workflows/upstream-status-proposal.yml) | Daily read-only; explicit manual Draft PR option | GET the same pinned PRs; if the lifecycle changed, upload an exact-scope patch. An internal Draft PR is created **only** on an explicit `workflow_dispatch.create_draft_pr=true`; no scheduled repository write |
| `python3 scripts/portfolio_reconcile.py --report --joined` | Operator run with `GITHUB_TOKEN` | One deduplicated PR/assessment/native-evidence view; unverified accepted count until the workflow's live accepted-source export is supplied |
| `python3 scripts/verified_external_outcomes.py --report` | Operator run with `GITHUB_TOKEN` | Separately screen verified outcome **candidates**; semantic/replacement chains remain reviewable |

The portfolio union uses existing source-owned publication receipts, existing manifests and the casebook/registry, not an inferred GitHub author-search corpus. New source-backed published PRs join the daily live observation without editing the official bounded hourly watcher. The live reconciler is not permitted to change the official watcher or conclude why a human closed a PR. For an observed drift, create a reviewed change to the relevant receipt; do not silently modify the primary ledgers on a timer.

The per-run JSON artifact includes an observation timestamp, all exact PR URLs with
their separate cohort memberships and a `cohort_sha256` identity fingerprint.
See [portfolio history](PORTFOLIO_HISTORY.md) for retention, comparability and
the important distinction between observed PR merging and verified adoption.
The two-stage accepted-source exporter independently rechecks first-party GitHub merge, source-delta and native CI evidence. Its `accepted_count` is a bounded merged-change result, not proof of deployed benefit. [Organization PR #322](https://github.com/opensiro/vsm-oss-organization/pull/322) is **merged** as `da377c16375793e6912db56996094e58d8dccfb2`; the Organization collector consumes only fresh source-verified exports while preserving unclaimed states and unknown historical baselines.

The [public Upstream PR status page](https://opensiro.com/upstream-portfolio.html)
is a separately deployed, source-dated consumer managed by
[`opensiro/opensiro.com`](https://github.com/opensiro/opensiro.com/blob/main/docs/UPSTREAM_PORTFOLIO_SYNC.md).
It does not own Upstream cohorts or turn PR merging into verified adoption.
See [the explicit verified-outcome gate](VERIFIED_EXTERNAL_OUTCOMES.md) for
the separate evidence statuses and the remaining Organization collector gate.

To refresh the existing **pinned casebook and registry PR receipts**, use:

```bash
python3 scripts/upstream_status.py --check-live
# After source-backed drift review only:
python3 scripts/upstream_status.py --refresh
python3 scripts/upstream_status.py --render
python3 scripts/upstream_status.py --check-generated
```

The optional refresh writes local files and must be reviewed in a PR. The daily live check does **not** automatically refresh on failure.

To generate a source-backed, **local-only** patch when the lifecycle actually
changed, run `python3 scripts/upstream_status.py --propose-if-drift` and inspect
the resulting Git diff. If no lifecycle state changed, the command leaves all
files untouched, including observation timestamps. Unknown PR states, source
errors and pinned-identity changes fail without writing a successful patch.
The [guarded workflow](../.github/workflows/upstream-status-proposal.yml) runs
this preparation daily and retains a 30-day patch artifact. Only an explicit
human workflow dispatch with the `create_draft_pr` input can open/update the
single **internal** bot Draft PR; this also depends on GitHub Actions PR-create
permissions being enabled. Draft PR generation is not branch-protection or CI
bypass. `GITHUB_TOKEN`-created PRs may not trigger standard PR checks; their
reviewer must run/verify required tests and source receipts before any merge.

## Scaling without crossing the publication gate

| Layer | Current/proposed state | Safe next step |
| --- | --- | --- |
| Data model and navigation | Standardized local contract; existing multiple ledgers remain distinct | Audit every new source/metric against ownership table |
| Reconciliation sensing | Automatic 18-PR watcher and broader read-only union; bounded 90-day observation artifacts | Verify first live artifact and add regression cases before expanding manifests |
| Verified external outcomes | 37-intervention owner-verifier corpus at the 2026-11-11 live checkpoint; deterministic acceptance rechecks first-party merges/native CI; 2 accepted merged changes, measured benefit **not claimed** | Keep observing live and retain ambiguous cases; Organization collector admission is a distinct CI/protection-gated change, not an Upstream exporter assertion |
| Lifecycle status correction | Daily read-only patch proposals; opt-in internal Draft PR only | Verify first live patch, configure explicit Actions PR permission if needed, require human merge; scheduled auto-PR activation remains a separate decision |
| Cross-batch source coordination | Optional, dormant Git compare-and-swap prototype under [#144](https://github.com/opensiro/upstream/issues/144) | Integrate only with an explicit collision policy and reviewed activation |
| Connected external fork/patch/PR executor | [Time-bounded preparation mandate](STANDING_PREPARATION_AUTONOMY.md) and [standing publication mandate](STANDING_EXTERNAL_PR_PUBLICATION.md) separately authorize qualifying fork/patch preparation and external PR submission without repeated owner approvals; executor capabilities and live provider verification remain case-specific | Verify both current-main policies and actor/provider permissions at each authorized stage; require source-native CI, destination rules, the final PR readback and an attributable receipt; neither mandate grants third-party merge rights |
| Automatic external PR merge, irreversible closure, fork archive | **Not authorized** | Individual attributable human decision and destination-repo rules |

This is a migration path beyond a pilot's manually maintained reports, **not** a claim of autonomous S3/S3* operation. More throughput does not relax license, source-identity, provenance or publication checks.

## Branch and PR hygiene

- GitHub currently has automatic branch deletion **after future merges**, and `main` reports as protected. Exact protection requirements may require an administrator readback.
- [The dated 2026-11-07 branch inventory](../reports/2026-11-07-internal-pr-branch-inventory.md) is historical, not a current count. [#150](https://github.com/opensiro/upstream/issues/150) owns live PR disposition; do not delete retained evidence branches by age or name.
- Before any deletion verify the precise ref/SHA, no open PR targeting or using it, any closed-PR evidence-retention decision, and branch protection. [#130](https://github.com/opensiro/upstream/issues/130) owns the prior cleanup receipt.
- The 2026-11-07 [closure-attribution report](../reports/2026-11-07-external-pr-closure-attribution.md) was integrated via [PR #152](https://github.com/opensiro/upstream/pull/152); the reconciler reports source events, not a substitute for reviewed human motive attribution.
