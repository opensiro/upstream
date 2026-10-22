# HarnessDesk #1772 — unpublished external PR draft (V2)

**Status: DRAFT_TEXT_ONLY / NOT SUBMITTED / NO CONTRIBUTION BRANCH.** This
document is a reviewable proposed PR title/body, not an external GitHub
pull request, a signed DCO assertion, or a stage authorization. The current
[local preparation mandate](../../policies/harnessdesk-1772-local-prepare.json)
is `PROPOSED_NOT_ACTIVE`.

## Intended external repository and branch

- Upstream: [HarnessDesk/HarnessDesk](https://github.com/HarnessDesk/HarnessDesk)
- Report: [HarnessDesk #1772](https://github.com/HarnessDesk/HarnessDesk/issues/1772)
- Proposed PR base: `development`; observed source HEAD
  `81d5e34e0e8e3d7e0945bc680695940b41ab852f` (2026-10-20)
- Proposed PR head (does **not** exist): `opensiro-contributions:opensiro/fix-toolgateway-1772`.
  Fork `development` remains at `4029e95189c61485f934f158c6725ef6eeb7ef35`.
  Do not advance that branch or publish to upstream automatically.
- Reviewed patch: [V2 exact two-file diff](tool-gateway-ownership-fix-v2.patch),
  SHA-256 `12b5c7e55a6f730fb9a2465ca30dd47321690c87c0d887e7b8c9d6990ec186e7`.
  V1 is superseded by this safety review and must not be submitted.

## Proposed PR title

`fix: preserve ToolGateway socket ownership across duplicate hosts`

## Proposed PR description

### Problem

Opening two HarnessDesk hosts with the same home can allow the second host
to unlink and rebind `tools.sock` before its own HTTP startup fails. The
original host remains running, but new agent sessions lose access to its
ToolGateway. See #1772.

### Change

- Give the socket a per-process PID/nonce owner record; reject a duplicate
  live owner instead of deleting its socket.
- Use an exclusive recovery gate for dead-owner cleanup. A dead PID alone
  is not enough to delete an existing socket: require an exact recorded
  device/inode match; unknown ownership fails closed.
- Bind a temporary sibling Unix socket and hard-link it into the public
  pathname without overwrite. This prevents Node's automatic
  `net.Server.close()` cleanup from unlinking a different live listener
  that replaced the public pathname.
- Only the current owner may remove its own public socket and owner record
  during shutdown.
- Add regression tests for duplicate startup and `stop()` cleanup,
  terminated owner recovery, concurrent recovery, an unrelated live socket
  after a dead-owner record, and a replacement listener that must survive
  original-host shutdown.

### Files

- `packages/server/src/tool-gateway.ts` (existing file)
- `packages/server/test/tool-gateway-ownership.test.ts` (new file)

### Validation

- Previously validated on pinned public HarnessDesk sources with real
  Node build and **17/17 targeted gateway tests PASS** on Linux and
  macOS (source-specific receipts in OpenSiro's V2 review). These are
  **not** an assertion that the entire upstream suite passed at the
  newest `81d5e34...` source.
- Exact V2 preimage and both postimage SHA-256 hashes reverified against
  `81d5e34...`. The sparse checkout already contained the V2 patch;
  `git apply -R --check` and `git diff --check` passed.
- The upstream-mandated `pnpm check:push` at this exact source is
  tracked by [OpenSiro PR #55](https://github.com/opensiro/upstream/pull/55).
  **Update this section with the actual check conclusion before external publication.**
- Native macOS, complete CI and maintainer acceptance remain separate.

### Scope

The change addresses ToolGateway Unix-socket ownership and directly
related regression tests only. No new agent orchestration model, remote
service, VSM score change or cross-repository policy is proposed.

## Before human publication — mandatory checks

1. A legitimate local fork-owner grant must first be recorded and
   **actually applied** to the Upstream-local policy, or the fork branch
   must be prepared separately by its authorized human owner.
2. Verify live public source SHA, fork push rights, correct parent,
   `development`-targeting policy, branch absence, the patch digest, the
   exact two resulting file contents and absence of overlapping fixing PRs.
3. If a contributor branch is created under a permitted mandate, perform
   real post-write branch/commit/readback checks and the full required
   upstream gate. Record any failures without auto-retry of an ambiguous
   push.
4. Verify DCO/CLA/licensing contribution requirements and actual
   contributor authority. **Do not fabricate or automatically assert
   Signed-off-by or a personal compliance declaration.**
5. Produce the authenticated GET-only
   [external PR handoff](../../scripts/upstream_pr_handoff.py), binding
   the actual **new branch SHA** and current upstream base SHA. Its
   payload is not a publication instruction.
6. Publication to `HarnessDesk/HarnessDesk` is a separate
   **human operator decision**. Do not invoke `POST /pulls`,
   notify maintainers, or claim upstream acceptance before it happens.

**Owner/provenance:** [Upstream #6](https://github.com/opensiro/upstream/issues/6)
and [HarnessDesk #1772](https://github.com/HarnessDesk/HarnessDesk/issues/1772).
