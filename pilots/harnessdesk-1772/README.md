# HarnessDesk #1772 — assessment-driven S1 candidate (blocked; unpublished)

> **Later current-source revalidation — 2026-10-20:** The
> [new immutable prepare packet](prepare-v2-20261020-24aa8d7.json)
> records external source `development@24aa8d7`, exact V2 pre/postimage
> digests, local Linux Node build + **17/17 gateway PASS**.
> Public fork base remains `4029e951`; no grant, external branch or PR.
> The earlier macOS receipts below apply to **97b13afc**, and the new
> `24aa8d7` macOS pin is a separate validation run.
>
> **Cross-platform V2 validation — 2026-10-20:** Genuine pinned-source
> macOS Node build and **17/17 gateway tests PASS** in both
> [PR CI](https://github.com/opensiro/upstream/actions/runs/39351363635)
> and [post-merge CI](https://github.com/opensiro/upstream/actions/runs/39351513890).
> Original Linux gateway tests also PASS. See the
> [validation report](IMPLEMENTATION_REVIEW_V2_2026-10-20.md).
> **The full upstream `check:push` and an exact host write grant remain
> unverified**; the fork is unchanged.
>
> **Exact V2 stage handoff — 2026-10-20:** [Machine-readable
> prepare-stage packet](prepare-v2-handoff.json) and
> [readable execution boundary](PREPARE_V2_HANDOFF.md) now bind the
> updated `development@97b13afc`, verified public fork at
> `development@4029e951`, nonexistent proposed branch and exact V2
> patch SHA-256. **NOT AUTHORIZED**: the existing connected adapter
> handles only one new test file, not this two-file production patch.
>
> **Latest V2 review — 2026-10-20:** The [original production
> patch](tool-gateway-ownership-fix.patch) has **two reproduced safety defects**
> and **MUST NOT be applied or sent upstream**. See the
> [new V2 patch](tool-gateway-ownership-fix-v2.patch) and
> [red→green adversarial review](IMPLEMENTATION_REVIEW_V2_2026-10-20.md).
> V2 was built and tested in the **current** source
> `development@97b13afc819ab7c1a0f8cd20630a428a34c2d47a`;
> **17/17** targeted tests PASS. No V2 patch has been pushed to the
> public fork; the pilot has no authenticated prepare-stage grant.
>
> **Historical V1 2026-10-20 implementation checkpoint:** The old status below is a **dated
> 2026-10-19 historical pilot snapshot**. An actual public
> [`opensiro-contributions/HarnessDesk`](https://github.com/opensiro-contributions/HarnessDesk)
> fork has since been created and verified, and a
> [source-only production fix plus real Node regression tests](IMPLEMENTATION_VALIDATION_2026-10-20.md)
> have now been compiled/tested against upstream `development@4029e951`
> (**15/15 relevant tests PASS**). The
> [patch](tool-gateway-ownership-fix.patch) is reviewable, **but has not
> been written to the fork**, and no external upstream PR has been opened.
> The old manifest remains blocked and publication remains human-owned.
>
**Date:** 2026-10-19  
**Pilot status:** `SOURCE_QUALIFIED / PREPARED_PREVIEW / BLOCKED_EXTERNAL_STAGE`  
**External writes:** none. **No external PR, fork, branch, or maintainer comment** was created.

## Origin (Index first)

- Canonical Index repository: [`opensiro/vsm-harness-index@13dab0d4f2954614f7f99a9fa044ad5b9a154490`](https://github.com/opensiro/vsm-harness-index/commit/13dab0d4f2954614f7f99a9fa044ad5b9a154490).
- Concrete included assessment: [`assessments/ha/harnessdesk.md`](https://github.com/opensiro/vsm-harness-index/blob/13dab0d4f2954614f7f99a9fa044ad5b9a154490/assessments/ha/harnessdesk.md) — `review_ref=24add77185eebe321b0aa0b578933acf4a8e05d3`, `S1=A`, `S2=A`, `S3=C(P)`, `S3*=A`, `S4=—`, `S5=—`.
- Assessment finding, not a desired grade promotion: HarnessDesk's real user-facing purpose is to regulate distinct agent cells' shared work, tool access, task/file interference and current Room execution. Its report explicitly includes the host process and common tool projection within the system-in-focus. A broken socket under a still-running first host undermines that native capability; preserving the tool bridge is useful even if OpenSiro VSM did not exist.
- This is a **separately performed, bounded follow-on intake**, not a retroactive justification for the earlier generic Cognee case. Other Index sample candidates were reviewed before this candidate was selected.

## Independently verified upstream-native need

- Current upstream source: [`HarnessDesk/HarnessDesk`](https://github.com/HarnessDesk/HarnessDesk), working integration branch [`development@aeb939a6709ae23c9f1ff5948fbd2151572aee58`](https://github.com/HarnessDesk/HarnessDesk/commit/aeb939a6709ae23c9f1ff5948fbd2151572aee58) observed 2026-10-19. Default `main` is the release branch; [`CONTRIBUTING.md`](https://github.com/HarnessDesk/HarnessDesk/blob/development/CONTRIBUTING.md) prescribes reviewed changes to `development`.
- First-party observed issue: [#1772](https://github.com/HarnessDesk/HarnessDesk/issues/1772), **open** when checked; the maintainer's report describes a second host on the same `HARNESSDESK_HOME` stealing `run/tools.sock`. No relevant open fixing PR was found in the current open PR inventory; recheck again before any external write.
- Source confirmation: [`packages/server/src/tool-gateway.ts`](https://github.com/HarnessDesk/HarnessDesk/blob/aeb939a6709ae23c9f1ff5948fbd2151572aee58/packages/server/src/tool-gateway.ts) currently calls `rmSync(this.socketPath, { force: true })` in `ToolGateway.start()` before `listen`, and `ToolGateway.stop()` also unlinks the socket without tracking which instance owns the pathname.
- Integration confirmation: [`packages/server/src/bootstrap.ts`](https://github.com/HarnessDesk/HarnessDesk/blob/aeb939a6709ae23c9f1ff5948fbd2151572aee58/packages/server/src/bootstrap.ts) starts the ToolGateway during host construction, before a duplicate headless host attempts its own HTTP listen. This is consistent with the issue's actual failure sequence.
- Test layout: [`packages/server/test/tool-gateway.test.ts`](https://github.com/HarnessDesk/HarnessDesk/blob/aeb939a6709ae23c9f1ff5948fbd2151572aee58/packages/server/test/tool-gateway.test.ts) — singular `test/` directory. OpenSiro's bounded prepare-stage adapter now accepts this path after internal PR #26.
- License: upstream repository declares **MIT**. A DCO/CLA requirement was not found in the inspected contribution entry, but eligibility must be independently confirmed before publication.

## Native-fit gates (pilot judgments only)

| Gate | Status | Rationale |
| --- | --- | --- |
| Need | `PASS` | #1772 contains explicit user-visible steps and actual impact |
| Mechanism | `PASS_FOR_ROOT_CAUSE` | Current `start()` unlinks socket unconditionally; duplicate host can rebound before HTTP port failure |
| Counterfactual value | `PASS` | Keeping the first host's tools alive when a duplicate starts is a normal product reliability improvement; not a VSM score repair |
| Current scope | `PASS` | Node server ToolGateway and host bootstrap are active first-party distribution paths; tests already cover server gateway |
| Patch correctness / upstream CI | `UNVERIFIED` | No production patch applied or full HarnessDesk test suite run |
| Existing PR duplication | `NOT_FOUND_IN_CURRENT_OPEN_PR_SAMPLE` | One unrelated open Dependabot PR observed; negative search is not proof of future absence |

## Draft material (not installed in the target)

- [`upstream-20261019-harnessdesk-1772.json`](upstream-20261019-harnessdesk-1772.json): a strict blocked `proposal_only` record with issue evidence and future `prepare_contribution` stage. Explicit blockers are intentional. This **cannot** be selected by `assessment_origin_preflight.py` or used for a write without resolving them and recording a revised digest.
- [`tool-gateway-second-host.test.ts`](tool-gateway-second-host.test.ts): **unexecuted proposed regression test** whose intended location is `packages/server/test/tool-gateway-second-host.test.ts`; it checks a second gateway cannot take over or unlink a live first gateway's path and that failed duplicate cleanup leaves the primary gateway reachable. The existing implementation is expected to fail this new test; it is **not proof** the corresponding fix works.
- Implementation direction: enforce single-live-owner startup before unlink/listen, and make `stop()` unlink only a socket genuinely owned by that gateway. Handle a stale crashed-host socket separately. Prefer an explicitly tested lifecycle design; **do not simply remove the unconditional unlink** (would break stale-socket restarts), use a static in-process flag (would not protect different processes), or suppress errors.
- Target base is `development`; `aeb939a` is the observed SHA, **not** a guaranteed current fork base. Recheck current SHA, fork ancestry, policy, test path and tests at any real preparation action.

## Authority / exact stop

Upstream [#6](https://github.com/opensiro/upstream/issues/6) and [Control Plane handoff](../../docs/CONTROL_PLANE_HANDOFF.md) remain authoritative. Local source inspection, a VSM assessment and an issue **never authorize external GitHub writes**.

A matching **writable fork** of `HarnessDesk/HarnessDesk` was not found under the investigated `opensiro` and `opensiro-contributions` namespaces. The intended working-fork destination is **`opensiro-contributions/HarnessDesk`**, subject to name availability and authenticated organization creation rights. The connected GitHub tool currently does not offer `create_public_fork`. The correct next engineering step is the [provider capability/authorization route](../../docs/OPENSIRO_CONTRIBUTIONS_FORK_ROUTE.md), tracked under [Upstream #28](https://github.com/opensiro/upstream/issues/28)—**not** a default request for the operator to create a personal fork. The draft fork adapter currently copies only the default branch (`main`), while HarnessDesk requires `development`; verify that exact branch exists and is usable in any eventual fork. No identity/approval envelope for an exact working repository, SHA, branch, path and file-content digest has been obtained. **Stop at that gate**; never relabel a new independent repository as a fork, substitute a PAT, or publish an external PR.

Before a real external write: (1) obtain an authorized matching fork or a supported fork creation action; (2) independently re-check fresh upstream `development`, policy and PR overlap; (3) reproduce #1772 and implement/test a production fix plus regression; (4) revise the blocked proposal with exact unblocked scope only after evidence permits; (5) generate a bound `assessment_driven_handoff.py` packet with exact content digest; (6) request a trusted **exact-action** operator decision. External PR submission remains human-owned even after a prepared package. This report does not decide Organization S5 #274 or establish `S1=A`.

**No closure of external implementation is claimed.** This candidate is actionable for next research/engineering, but its external stage is deliberately `BLOCKED`.
