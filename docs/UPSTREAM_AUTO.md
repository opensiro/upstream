# Upstream Auto — bounded task arbitration (proposal / preview)

**Owning issue:** [Upstream #161](https://github.com/opensiro/upstream/issues/161).
**Current status:** protocol and read-only inspection only. This document does not
activate an unattended executor, a general task reservation service, or new
external GitHub write rights. A request for `upstream auto` must not claim that
parallel-safe execution is already implemented.

## Purpose and recursion

`upstream auto` is an Upstream Contributions **S1-local** operator route. Its
eventual purpose is to select and resume bounded work among existing Upstream
lanes when multiple agent sessions are active, without duplicating the work.

It is **not** the Organization global `TODO.md` scheduler, a new S3 commitment
owner, or the cross-domain S2 needed for [Organization M4 #6](https://github.com/opensiro/vsm-oss-organization/issues/6).
The Upstream-local coordination could qualify as a recursive S2 **only if**
separate operational S1 units, actual interference, coordination, returned
feedback, and attenuation are evidenced at that explicitly declared recursion.
Locks, queue state and a router alone never establish `S2=C` or `S2=A`.

## Command contract

| Command | Current behavior | Future admission condition |
| --- | --- | --- |
| `upstream auto status` | Read-only, live source-first preview of currently eligible, pending, reserved and blocked work; explain uncertainty. | Existing Upstream owner issues and authenticated first-party evidence. |
| `upstream auto` | Return `NOT_IMPLEMENTED_EXECUTOR` plus a bounded preview and exact missing gate. Do **not** start/reserve an arbitrary open issue. | A separately reviewed, tested task-claim protocol and bounded executor under #161. |
| `upstream auto resume` | Return `NOT_IMPLEMENTED_TASK_CLAIM` unless there is an independently verified existing owner-specific task reservation; then route to that *existing* owner workflow, subject to its gates. | Readback of an auditable claim and task-specific safe recovery. |

The eventual executor may dispatch these existing owner tasks, never substitute
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

## Read-only preview and selection proposal

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
5. Return an inspection receipt: `SOURCE_CUT`, `ELIGIBLE`, `BUSY`, `BLOCKED`,
   `SUGGESTED_NEXT`, `DECISION_OWNER`, and `MISSING_GATE`. If data are absent,
   use `NO_VERIFIED_ELIGIBLE_WORK` or `BLOCKED_VISIBILITY`.

This preview makes **no write**, takes no reservation and creates no new
Organization `NOW`/`NEXT` entry. Until the actual concurrent task-claim
protocol is accepted, it must not certify the suggested task as exclusively
allocated to this agent.

## Requirements before an executable `upstream auto`

- A versioned inventory and task identity for each eligible owner route,
  including source/PR refs and no double-count of multi-PR interventions.
- A task-specific atomic claim/admission or equivalent race-free serialization
  for **non-batch** work. Batch source-CAS is not a general lock.
- Auditable recovery from interrupted/stale work. No silent expiry, theft,
  branch rewrite or fabricated closure.
- Bounded execution (one admitted work unit per invocation), explicit retry
  limits, native validation and receipts to the owning issue/ledger.
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
