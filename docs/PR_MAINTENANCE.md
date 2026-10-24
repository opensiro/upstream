# Upstream PR Maintenance — bounded review-and-repair work cell

**Owning issue:** [opensiro/upstream #125](https://github.com/opensiro/upstream/issues/125). Related empirical upstream improvement [#56](https://github.com/opensiro/upstream/issues/56).

**Current organizational boundary:** This is an **adjacent Upstream-local S1-like operating pilot**, **NOT** a fourth operational S1 admitted into the bounded OpenSiro VSM OSS organization. Admission remains proposed at [Organization #274](https://github.com/opensiro/vsm-oss-organization/issues/274) and requires its own attributable S5 decision, contract update, and evidence. A cron job, a GitHub App, or a bot is not itself an S1 or an autonomy-grade assertion.

## Operational purpose and decisions

**Durable local outcome:** an external PR's maintainer feedback is noticed, classified, and resolved with a justified native-tested correction, clear response, documented no-change, or escalated issue; upstream acceptance/merge decisions remain exclusively with upstream maintainers.

**Local environment:** the explicit public PR target list in [targets.json](../data/pr-maintenance/targets.json), external GitHub review and status events, external contribution policies, current source revisions and permitted fork branches.

**Current delegated envelope of the read-only monitor:**
- Observe and compare public PR state, head/base, first-party/inline comments, reviews including `CHANGES_REQUESTED`, check runs and commit status.
- Classify human feedback and failing CI as `ACTION_REQUIRED`; notify only the [OpenSiro inbox #125](https://github.com/opensiro/upstream/issues/125). `APPROVED`, `MERGED`, `CLOSED_UNMERGED`, head/status transitions are information for subsequent reporting, not invitations to merge.
- Keep an idempotent checkpoint (compressed JSON) as a **single GitHub Actions bot comment** on this issue. An actionable digest has a stable issue-comment marker to prevent duplicate alerts if checkpoint writing failed. First scan establishes a baseline; historical comments do **not** become artificial new events.
- Schedule **hourly (minute 13, UTC)** after the workflow is merged onto `main`. Also accept manual `workflow_dispatch`. Job summary and issue comments link the original external PRs.

**Constrained S1-like maintenance work (human/agent in later execution):**
1. On `ACTION_REQUIRED`, independently read *current* upstream code, reviewer request, exact PR diff, source and CI failures.
2. Admit only if the requested fix remains within the original reviewed PR scope, source rights, contributor requirements and the operator's actual bounded decision envelope; otherwise `ESCALATED`.
3. Reproduce the defect and repair on an **authorized** contribution fork branch. Validate with **native deterministic tests only**, no LLM or live agent runs; update the existing PR **only when an operative write mandate covers that update**.
4. Return exact head, tests, external response or reason for no-change. Reobserve upstream replies. A reviewer comment does **not** create new permission; submitting a new external PR, CLA/DCO attestation, merge, scope expansion, or modified VSM grade is **NOT authorized by this watcher**.

This is a construction/operating contract. The read-only detector and alert transport do **not** by themselves prove that an autonomous S1 operator has closed an actual maintainer request. Positive classification requires decision-right/owner and closure evidence under the owning VSM Profile and Methodology.

## Technical architecture

`.github/workflows/pr-maintenance.yml` has two jobs. The `verify` job has **read-only contents** permission and executes on PRs, manual dispatch, and schedule; the conditional `watch` job runs **only** on schedule/dispatch after verification, with `contents:read` and `issues:write`. No token is passed to PR-submitted code on the verification route. Write operations are hardcoded to this repository's issue #125 and its checkpoint comment; there is no external GitHub POST/PATCH, no code push or PR/issue modification outside this inbox.

The watcher uses Python standard library only and authenticates using the GitHub Actions token. Each observation is a live **GET** from the GitHub repository that owns it; API errors, missing identities, unknown states and truncated pagination **fail closed**. Third-party message **bodies are deliberately not stored, executed, or trusted as instructions**: only event IDs, author, status and GitHub URLs are used. Humans/agents inspect the exact review on the external source before repairing.

Current targets are 13 explicitly verified public external PRs for contributor `xLagerFeuer`, including Headcount #47 (missed by one GitHub search result but directly confirmed OPEN), closed-unmerged StarNet #56, and new Draft Workflow One #173. This list is a versioned scope snapshot and is **not** dynamically widened by an unreviewed search result. Adding/removing targets requires a reviewable manifest change and explicit checkpoint-migration handling. Closed/merged PRs remain in the snapshot to preserve lifecycle evidence until a deliberate archival change.

**Checkpoint migration for #173:** The reviewed watcher code explicitly admits only the additive Workflow One #173 URL into an existing 12-PR checkpoint. All 12 prior snapshots remain intact; #173 starts from its first observed baseline (`NEW_TRACKED_PR`, informational only), so past comments and checks are not replayed as new maintainer requests. Its later real transitions are tracked normally. Any unapproved new target or any removed target still fails closed without inbox writes. The PR-branch live `--probe-only` check exercises this migration without modifying the bot checkpoint; first scheduled/dispatch run after merge persists the 13-PR checkpoint.

`python3 scripts/pr_maintenance_watch.py --validate-only` validates the manifest without network or write operations.

`python3 -m unittest discover -s tests -p test_pr_maintenance_watch.py -v` tests no-repeat notices, genuine review/CI changes, old comment suppression, callback routing and fail-closed behavior without calling GitHub.

## Caveats and activation

- This implementation is **not active on a schedule until merged** into the default branch and Actions is enabled. A successful PR-branch test is not a live monitor.
- GitHub scheduled workflows may run late or be skipped under platform load; `hourly` describes configuration, not guaranteed latency.
- Monitoring is not the same as event ownership. Maintainer review requests must be independently triaged and closed through an authorized operator.
- The existing daily portfolio lifecycle freshness check is still authoritative for its historical experimental cohort; this watcher does not overwrite it or mutate the frozen 34-case Corrective ledger.
- If GitHub issues are locked, Actions token cannot write to #125, or checkpoint state is ambiguous, the watcher must fail and alert via failing Actions, **not** silently reset its cursor.
