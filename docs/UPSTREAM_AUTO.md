# Upstream Auto — bounded task arbitration

**Owning issue:** [Upstream #161](https://github.com/opensiro/upstream/issues/161).
**Current scope:** on-demand agent selection and a tested, opt-in **internal**
task reservation primitive. This is not a deployed unattended agent, a general
GitHub-write grant, or an autonomous external contributor. The task's owning
contract remains the executor for native actions.

## Purpose and recursion

`upstream auto` is an Upstream Contributions **S1-local** operator route. Its
purpose is to select and resume bounded work among existing Upstream
lanes when multiple agent sessions are active, without duplicating the work.

It is **not** the Organization global `TODO.md` scheduler, a new S3 commitment
owner, or the cross-domain S2 needed for [Organization M4 #6](https://github.com/opensiro/vsm-oss-organization/issues/6).
The Upstream-local coordination could qualify as a recursive S2 **only if**
separate operational S1 units, actual interference, coordination, returned
feedback, and attenuation are evidenced at that explicitly declared recursion.
Locks, queue state and a router alone never establish `S2=C` or `S2=A`.

## Command contract

| Command | Current behavior | Hard limit |
| --- | --- | --- |
| `upstream auto status` | An agent reads live Upstream owner evidence, prepares a short-lived worklist and runs the deterministic read-only selector against the current task-CAS ledger. | Returns a **preview**, not proof of admission or execution. |
| `upstream auto` | One bounded agent session: source-first S1 admission, live-worklist preview, optional atomic reservation, then one action in the already-owning task route followed by an attributable handoff/release. | If live task claims, tools or the exact task authority are absent, report `NOT_IMPLEMENTED_EXECUTOR` or the specific blocker; do not run work unreserved. |
| `upstream auto resume` | Re-read the declared actor's existing task claims, revalidate refs and continue one existing owner lane. | Missing/invalid claim returns `NOT_IMPLEMENTED_TASK_CLAIM` or `BLOCKED_RESERVATION_VISIBILITY`; no silent claim theft or release. |

The dispatcher may select these existing owner tasks, never substitute
its own authority or issue lifecycle:

| Lane | Current Upstream owner | Routing invariant |
| --- | --- | --- |
| Technical five-source cohorts | [#56](https://github.com/opensiro/upstream/issues/56), [#144](https://github.com/opensiro/upstream/issues/144) | Use pinned Index evidence, exactly five distinct sources, source-CAS claim where effective, and serial candidate execution. |
| Third-party PR feedback | [#125](https://github.com/opensiro/upstream/issues/125) | Inspect first-party external PR/CI/review events; no external replies without exact-stage authority. |
| Internal PR disposition | [#150](https://github.com/opensiro/upstream/issues/150) | Respect open/closed/retained branch decisions and current head/CI; no automatic merge or deletion. |
| External outcome evidence | [#159](https://github.com/opensiro/upstream/issues/159) | Machine candidate status is not a reviewer-accepted result or Organization KPI. |

An open issue is **not** automatically an admitted executable task. Each lane
must supply current actionable evidence and the required S1 admission rights.
No generic `auto` dispatch may override a frozen cohort, a live PR reviewer, a
separate publication mandate, or a task's own `STOP` and read-only restrictions.

## Read-only selection and balancing

1. Re-read Organization [START_HERE](https://github.com/opensiro/vsm-oss-organization/blob/main/START_HERE.md), the Upstream default branch and the exact owner issues above.
2. Distinguish `ACTIONABLE`, `AWAITING_EXTERNAL`, `BLOCKED_EVIDENCE`, `CLAIMED`,
   `STALE_CLAIM_UNRESOLVED`, and `UNKNOWN`. Never replace unavailable evidence
   with `ACTIONABLE`.
3. Normalize source identity, intervention ID and PR target before comparing
   work. Existing five-source CAS claims cover their **batch** domain; they
   do not prove exclusive ownership of PR-maintenance or outcome-review tasks.
4. Prefer genuine maintainer review/CI events and safely resumable work over
   speculative discovery; balance lane WIP, starvation and risk. Explain each
   suggested priority with time-of-check source refs, without promoting a
   deterministic score to agent-owned S2 discretion.
5. Record a short-lived, attributable JSON worklist containing `schema_version=1`,
   exact `upstream_main_sha`, `observed_at` and at most 100 task cards. Each
   card specifies `task_id`, `lane`, exact `owner_issue`, `resources`, direct
   first-party GitHub `evidence_url`, `queued_at`, task `observed_at`, `status`,
   `priority` (`P0`–`P3`), non-external `operation` and a pinned `head_sha` for
   PR targets. An **agent**, not the file, owns and documents the S1 admission
   judgment; arbitrary open issues and unverified source claims are excluded.
6. Run `python3 scripts/upstream_auto.py status --manifest /path/to/fresh-worklist.json`.
   The script reads the dedicated Git ledger, validates source-cut and task
   freshness (maximum 60 minutes), normalizes identities, filters busy/blocked
   tasks and lane WIP limits, then proposes a reproducible `selected` task.
   Return `NO_VERIFIED_ELIGIBLE_WORK` or `BLOCKED_RESERVATION_VISIBILITY`
   rather than guessing from incomplete GitHub visibility.

The selector sorts by explicit priority, age (bounded anti-starvation boost),
and work-class weight: urgent maintainer/CI feedback and existing outcomes
generally precede speculative new screening. WIP caps are `maintenance=2`,
`outcomes=2`, `portfolio=1`, `batch=1`. These are provisional workload
heuristics, **not** VSM S2 decisions by themselves. `status` makes **no write**,
takes no reservation and creates no new Organization `NOW`/`NEXT` entry.

## CAS claims, recovery, and bounded execution

The separate first-party Git branch `refs/heads/upstream-auto-task-reservations`
contains exactly `reservations.json` (append-only `CLAIM` / `RELEASE` events).
For a selected admitted task, an agent may run:

```bash
python3 scripts/upstream_auto.py claim --manifest /path/to/fresh-worklist.json --actor agent-session-1 --write-claim
python3 scripts/upstream_auto.py resume --actor agent-session-1
python3 scripts/upstream_auto.py release --claim-id <claim_id> --actor agent-session-1 --reason "Reviewed and recorded owner handoff" --evidence-url https://github.com/opensiro/upstream/issues/161 --write-release
```

The `--write-*` options are **explicit opt-in Git writes to this Upstream-owned
ledger only**, requiring a Git credential with effective rights. No external
fork, comment, PR, merge or third-party mutation is performed by the script.
The claim checks the live Upstream main SHA, owning issue state and PR head/
lifecycle where applicable, then commits a new Git tree against the fetched
ledger head. A **non-force** push is its compare-and-swap admission. Losing
a race yields `BLOCKED_CONCURRENT_RESERVATION` and requires a fresh read;
different unclaimed resources can proceed after re-planning.

The declared `--actor` is an audit label, **not cryptographic authentication**;
actual Git/provider permission remains a separate gate. A successful claim
only reserves the named local task. The agent must **revalidate current
source, owner permissions and task-specific tests before any work**, execute
at most one admitted action, record the actual owner result, and release with
an attributable reason. A release does not itself prove successful execution.
`resume` never silently reassigns a claim. Claims older than 24 hours are
reported as `STALE_CLAIM_UNRESOLVED` until auditable recovery; they are not
automatically stolen, expired or treated as completed.

The existing five-source batch source-CAS branch is **separate**. A batch
task must name one frozen batch and its five sources, and must have all five
already reserved by that batch in the source-CAS ledger before this generic
task claim is written. A generic task claim alone cannot admit a new cohort.
There is no proven atomic transaction **across both** Git-ledger branches;
source-overlapping cross-protocol work must be rechecked at the actual owner
gate and treated as blocked when its safe serialization cannot be proven.

If Git credentials, the task-ledger branch, live evidence or task-specific
rights are missing, the agent stops at the read-only preview or a precise
`BLOCKED_*` receipt. A ChatGPT/GitHub connector can carry equivalent Git
objects and a compare-and-swap ref update **only** if its own permissions and
expected-head protection are verified; the CLI does not create that authority.
An eligible connector-driven CAS uses this **same** event schema and strict
append-only replay, fetches the live ledger ref SHA and single-file tree,
creates the new ledger blob/tree/child commit, updates the same ref with an
`expected_sha` lease and **non-force** semantics, then performs authenticated
readback. A rejected lease means `BLOCKED_CONCURRENT_RESERVATION` and a fresh
re-plan; it never authorizes a force update or retry against an unseen head.

## Remaining boundaries and acceptance evidence

- A versioned inventory and task identity for each eligible owner route,
  including source/PR refs and no double-count of multi-PR interventions.
- A shared task-level atomic claim/admission is implemented for **Upstream Auto
  participants**. Batch source-CAS is still not a general lock; callers not
  using this task ledger remain outside its collision guarantee.
- Auditable recovery from interrupted/stale work. No silent expiry, theft,
  branch rewrite or fabricated closure.
- The agent, not this script, is the bounded executor (one admitted work unit
  per invocation). Native validation and receipts to the owning issue/ledger
  remain task-specific responsibilities and are not fabricated by a claim.
- Concurrent fixture tests: same-task collision, disjoint-task progress,
  missing visibility, stale claim, live PR head change, blocked grant,
  fairness/WIP and unchanged five-row batch order.
- A separate effective actor/permission/stage grant before external fork,
  branch, PR or comment creation. Third-party merge remains external.

## VSM assessment evidence boundary

An Upstream-local task distributor may strengthen evidence for **local**
coordination. Formal Organization `S2=A` under M4 additionally requires a
specific inter-domain disturbance among at least two **different admitted
S1 domains**, a decisive agent-owned coordination choice, an observable return
to both affected domains, and subsequent attenuation. Record counterexamples
and human decisions. Do not regrade an Index assessment, Organization milestone,
Upstream S1 ownership, or `verified_external_outcomes` based on this proposal.
