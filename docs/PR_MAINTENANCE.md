# Upstream PR Maintenance — bounded review-and-repair work cell

**Owning issue:** [opensiro/upstream #125](https://github.com/opensiro/upstream/issues/125). Related empirical upstream improvement [#56](https://github.com/opensiro/upstream/issues/56).

**Current organizational boundary:** This is an **adjacent Upstream-local S1-like operating pilot**, **NOT** a fourth operational S1 admitted into the bounded OpenSiro VSM OSS organization. Admission remains proposed at [Organization #274](https://github.com/opensiro/vsm-oss-organization/issues/274) and requires its own attributable S5 decision, contract update, and evidence. A cron job, a GitHub App, or a bot is not itself an S1 or an autonomy-grade assertion.

## Operational purpose and decisions

**Durable local outcome:** an external PR's maintainer feedback is noticed, classified, and resolved with a justified native-tested correction, clear response, documented no-change, or escalated issue; upstream acceptance/merge decisions remain exclusively with upstream maintainers.

**Local environment:** the explicit public PR target list in [targets.json](../data/pr-maintenance/targets.json), external GitHub review and status events, external contribution policies, current source revisions and permitted fork branches.

**Current delegated envelope of the read-only monitor:**
- Observe and compare public PR state, head/base, mergeability (`mergeable=false` and `mergeable_state=dirty`), first-party/inline comments (including edited existing comments), reviews including `CHANGES_REQUESTED`, check runs and commit status.
- Classify human feedback and failing CI as `ACTION_REQUIRED`; notify only the [OpenSiro inbox #125](https://github.com/opensiro/upstream/issues/125). `APPROVED`, `MERGED`, `CLOSED_UNMERGED`, head/status transitions are information for subsequent reporting, not invitations to merge.
- Keep an idempotent checkpoint (compressed JSON) as a **single GitHub Actions bot comment** on this issue. An actionable digest has a stable issue-comment marker to prevent duplicate alerts if checkpoint writing failed. First scan establishes a baseline; historical comments do **not** become artificial new events.
- Schedule **hourly (minute 13, UTC)** on `main`; also accept manual `workflow_dispatch`. The [first default-branch run](https://github.com/opensiro/upstream/actions/runs/40103888527) succeeded and initialized the checkpoint. Job summary and issue comments link the original external PRs.

**Constrained S1-like maintenance work (human/agent in later execution):**
Use the [event triage and closure packet](PR_MAINTENANCE_TRIAGE.md) to bind an actual source event to its admission, source/authority checks and native-test/return receipts.

1. On `ACTION_REQUIRED`, independently read *current* upstream code, reviewer request, exact PR diff, source and CI failures.
2. Admit only if the requested fix remains within the original reviewed PR scope, source rights, contributor requirements and the operator's actual bounded decision envelope; otherwise `ESCALATED`.
3. Reproduce the defect and repair on an **authorized** contribution fork branch. Validate with **native deterministic tests only**, no LLM or live agent runs; update the existing PR **only when an operative write mandate covers that update**.
4. Return exact head, tests, external response or reason for no-change. Reobserve upstream replies. A reviewer comment does **not** create new permission; submitting a new external PR, CLA/DCO attestation, merge, scope expansion, or modified VSM grade is **NOT authorized by this watcher**.

This is a construction/operating contract. The read-only detector and alert transport do **not** by themselves prove that an autonomous S1 operator has closed an actual maintainer request. Positive classification requires decision-right/owner and closure evidence under the owning VSM Profile and Methodology.

## Technical architecture

`.github/workflows/pr-maintenance.yml` has two jobs. The `verify` job has **read-only contents** permission and executes on PRs, manual dispatch, and schedule; the conditional `watch` job runs **only** on schedule/dispatch after verification, with `contents:read` and `issues:write`. No token is passed to PR-submitted code on the verification route. Write operations are hardcoded to this repository's issue #125 and its checkpoint comment; there is no external GitHub POST/PATCH, no code push or PR/issue modification outside this inbox.

The watcher uses Python standard library only and authenticates using the GitHub Actions token. Each observation is a live **GET** from the GitHub repository that owns it; API errors, missing identities, unknown states and truncated pagination **fail closed**. Third-party message **bodies are deliberately not stored, executed, or trusted as instructions**: only event IDs, author, status and GitHub URLs are used. Humans/agents inspect the exact review on the external source before repairing.

Current targets are 14 explicitly verified public external PRs for contributor `xLagerFeuer`, including Headcount #47 (missed by one GitHub search result but directly confirmed OPEN), closed-unmerged StarNet #56, Draft Workflow One #173, and Draft [Reef/Polyp #19](https://github.com/Coral-Bricks-AI/reef/pull/19). This list is a versioned scope snapshot and is **not** dynamically widened by an unreviewed search result. Adding/removing targets requires a reviewable manifest change and explicit checkpoint-migration handling. Closed/merged PRs remain in the snapshot to preserve lifecycle evidence until a deliberate archival change.

**Checkpoint migration for #173 and Reef #19:** The watcher explicitly allows only these two reviewed additive URLs. Workflow One #173 was already baselined into the existing bot-owned 13-PR checkpoint. Reef #19 adds one snapshot on the next authorized scan, preserving the previous 13 observations. Both new arrivals receive a `NEW_TRACKED_PR` informational event instead of backfilled historic review/CI alerts; subsequent real transitions are tracked normally. An unapproved URL or removal still fails closed without inbox writes. A `--probe-only` live scan checks the migration without modifying the checkpoint; a scheduled/dispatch run following merge can persist the 14-PR checkpoint.

`python3 scripts/pr_maintenance_watch.py --validate-only` validates the manifest without network or write operations.

`python3 -m unittest discover -s tests -p test_pr_maintenance_watch.py -v` tests no-repeat notices, genuine review/CI changes, old comment suppression, callback routing and fail-closed behavior without calling GitHub.

## Caveats and activation

- The implementation was merged in [PR #126](https://github.com/opensiro/upstream/pull/126) and activated on `main`. The manual default-branch run succeeded; check [current Actions runs](https://github.com/opensiro/upstream/actions/workflows/pr-maintenance.yml) for subsequent hourly execution, rather than inferring each run from the schedule declaration.
- New or edited human review comments are actionable signals, not necessarily proven defects or authorized instructions. Inspect the actual updated source comment before triage; deleted comments and missed intermediate edit versions are not reconstructed by polling.
- A **newly confirmed** GitHub merge conflict raises `MERGE_CONFLICT`. `mergeable=null` means computation is pending, and branch protection/check failures are not necessarily conflicts. The last settled conflict state is kept separately through transient unknown responses; observed API fields are unchanged. Preexisting conflicts are **not** backfilled as new when adding mergeability fields to the checkpoint. Inspect the actual PR before rebasing; the target base need not be `main`.
- Example manual triage: [StarNet PR #56](../reports/2026-10-24-starnet-pr56-maintenance.md) was already `dirty`, but the maintainer had independently released the requested tool; the external PR was later closed unmerged by OpenSiro with an explicit reason. This is a justified *no-patch* local result, not an OpenSiro merge.
- GitHub scheduled workflows may run late or be skipped under platform load; `hourly` describes configuration, not guaranteed latency.
- Monitoring is not the same as event ownership. Maintainer review requests must be independently triaged and closed through an authorized operator.
- The existing daily portfolio lifecycle freshness check is still authoritative for its historical experimental cohort; this watcher does not overwrite it or mutate the frozen 34-case Corrective ledger.
- If GitHub issues are locked, Actions token cannot write to #125, or checkpoint state is ambiguous, the watcher must fail and alert via failing Actions, **not** silently reset its cursor.
