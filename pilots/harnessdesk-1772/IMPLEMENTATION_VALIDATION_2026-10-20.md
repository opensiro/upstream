# HarnessDesk #1772 — local implementation and regression validation (V1 historical)

> **SUPERSEDED / DO NOT APPLY V1:** Independent adversarial review uncovered
> socket-identity takeover and unrelated-listener deletion on `stop()`.
> The original 15/15 PASS covered only the earlier test subset. The safe
> successor is [V2](IMPLEMENTATION_REVIEW_V2_2026-10-20.md), whose
> [revised patch](tool-gateway-ownership-fix-v2.patch) has been
> compiled/tested on current upstream source with 17/17 targeted PASS.
> V1 is retained solely as historical evidence.


**Status:** SOURCE PATCH PREPARED; production fix has been compiled and locally
tested against the real external repository; **not installed in the
organization fork** and **no external PR**.  
**Owner:** [Upstream #6](https://github.com/opensiro/upstream/issues/6)
and [Upstream #28](https://github.com/opensiro/upstream/issues/28).  
**External issue:** [HarnessDesk/HarnessDesk#1772](https://github.com/HarnessDesk/HarnessDesk/issues/1772).

## Fresh source and overlap observation

- Used the current upstream `HarnessDesk/HarnessDesk` integration branch
  `development` at **`4029e95189c61485f934f158c6725ef6eeb7ef35`**,
  fetched from GitHub on 2026-10-20 (not the obsolete SHA in the original
  2026-10-19 proposal).
- The issue remains **open**. The sampled current open upstream PR inventory
  contained no titles matching `socket`, `gateway` or `second host`;
  this is not a guarantee against later overlap.
- The org-owned public fork
  [opensiro-contributions/HarnessDesk](https://github.com/opensiro-contributions/HarnessDesk)
  already exists, its direct parent is correct, and its `development`
  branch was previously verified at the exact source SHA. This was created
  by a **one-off** authenticated host CLI request, not the automated batch
  pipeline.

## Actual candidate implementation

The [local patch](tool-gateway-ownership-fix.patch) targets exactly:

1. `packages/server/src/tool-gateway.ts` — replaces unconditional
   `rmSync(tools.sock)` on startup with a cross-process exclusive
   `tools.sock.owner` lock, containing the process PID and a random
   owner nonce. Live owner or unknown owner is **fail-closed**; neither the
   first host's socket nor its owner file is removed.
2. Adds `tools.sock.owner.recovery` as an **exclusive recovery gate**, so
   simultaneous post-crash reclaimers cannot both race to remove a socket.
   Dead-PID recovery can discard stale owner+socket and bind a new listener;
   an orphaned *recovery* lock is deliberately fail-closed for manual
   diagnosis instead of blindly taking over an ambiguous socket.
3. `stop()` checks the exact owner nonce before unlinking the socket/owner
   file. Calling `stop()` on a rejected duplicate does **nothing** to the
   first live host.
4. `packages/server/test/tool-gateway-ownership.test.ts` — regression
   covering duplicate startup, cleanup after refusal, stale lock recovery,
   ambiguous/unowned socket refusal, recovery-gate contention and a real
   independent Node child host terminated by `SIGKILL`, followed by
   verified live recovery.

This is a bounded production proposal, **not** an upstream-accepted patch or
a system-wide VSM grade change. Review the lock protocol for platform and
concurrent-recovery edge cases before any external publication.

## Executed validation — isolated nonprivileged development workspace

Ran in a fresh shallow-then-unshallowed checkout of the genuine upstream
`development` branch, without using the credential-bearing fork host as
a heavyweight build worker:

- Environment: Node **22.19.0**, pnpm **10.4.1**.
- `pnpm install --frozen-lockfile --ignore-scripts`: dependencies
  installed; the shell wrapper's final `PIPESTATUS` expression was not
  portable to `sh`, so do not count that wrapper's exit as the install
  result. The build consumed the resolved dependencies successfully.
- `pnpm run build:node`: **PASS**, TypeScript project compilation and
  generated Node artifacts succeeded.
- `node --test --test-timeout=120000
  packages/server/dist/test/tool-gateway-ownership.test.js
  packages/server/dist/test/tool-gateway.test.js`: **15/15 PASS**,
  including the real cross-process SIGKILL case and existing gateway API
  tests.
- `git diff --check`: **PASS**; the patch was generated from the tracked
  production diff plus the new regression test, against the pinned source
  branch.
- `pnpm check:push`: use the separate gate receipt only after verifying
  completion. The initial attempt failed due an incomplete shallow
  `origin/main` merge base. Full Git ancestry was then fetched and the
  gate was rerun; selected browser/native suites may remain CI-only.

## Authority and next stage

The existing [pilot manifest](upstream-20261019-harnessdesk-1772.json)
is `proposal_only`, lists `prepare_contribution`, and retains explicit
blockers. The real fork clears a former infrastructure limitation, but
**does not turn the manifest into an approved exact-stage write request**.
The CLI evidence also does not grant permission for a standing automated
upstream publication.

To turn this source patch into a working branch **after a separately
authenticated exact prepare-stage decision**, first revalidate the
current upstream `development` SHA and the existing fork base/branch,
review the patch and required tests, then apply only this patch to a new
`opensiro/*` branch. Run the project's required `pnpm check:push` and
any affected CI. External upstream PR creation remains **human-owned**;
the [GET-only PR handoff](../../scripts/upstream_pr_handoff.py) can prepare
its precise draft REST request after a real pushed contribution branch
exists, but cannot publish it.

No external branch, commit, upstream PR, maintainer comment, S1 admission
or new autonomy grade is claimed by this report.
