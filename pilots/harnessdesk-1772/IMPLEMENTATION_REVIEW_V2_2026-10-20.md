# HarnessDesk #1772 — security/lifecycle review V2 (2026-10-20)

**Status:** V2 PATCH COMPILED AND TESTED ON CURRENT UPSTREAM SOURCE; **NO EXTERNAL FORK WRITE** / **NO THIRD-PARTY PR**.

**Owner:** [OpenSiro Upstream #6](https://github.com/opensiro/upstream/issues/6), [#28](https://github.com/opensiro/upstream/issues/28).  
**External issue:** [HarnessDesk/HarnessDesk #1772](https://github.com/HarnessDesk/HarnessDesk/issues/1772).  
**Baseline source:** `HarnessDesk/HarnessDesk development@97b13afc819ab7c1a0f8cd20630a428a34c2d47a` — observed live on 2026-10-20.  
**Prepared artifact:** [`tool-gateway-ownership-fix-v2.patch`](tool-gateway-ownership-fix-v2.patch), SHA-256 **`12b5c7e55a6f730fb9a2465ca30dd47321690c87c0d887e7b8c9d6990ec186e7`**.

## What changed from V1, and why

**V1 is superseded and must not be applied to the fork.** A new independent adversarial review of the [previous patch](tool-gateway-ownership-fix.patch) found two untested safety failures:

1. A dead process ID in `tools.sock.owner` was taken as sufficient evidence to remove the socket, even if a *different live* Unix-socket server had since bound that pathname. A newly added regression created precisely this situation, and V1 failed (candidate incorrectly removed the listener).
2. Node's `net.Server.close()` unlinks the **original listening pathname**. After the original gateway's socket pathname was replaced by an unrelated live listener, V1's `stop()` still removed the replacement even though its explicit nonce check declined to unlink it. A second adversarial test reproduced this failure.

V2 fixes both:

- Every owner record is bound to a verified socket filesystem identity (`device:inode`). Reclaiming a dead owner's socket requires the recorded identity to **match the actual pathname**, not merely a dead PID. Missing/mismatched identity fails closed.
- The server binds an unpredictable temporary sibling socket, **hard-links it without overwrite** to `tools.sock`, then removes the temporary name. Node now associates automatic close cleanup with the temporary name, **not** the public pathname. The public pathname is removed only when the current owner nonce **and socket identity** still match.
- Publication occurs synchronously after `server.listen()` binds, so immediate clients do not see a transient `ENOENT`.
- Existing atomic PID/nonce owner lock and serialized stale recovery gate remain. Unknown, interrupted or conflicting recoveries fail closed; they do not silently delete another host's socket.

See [Node.js documented Unix-domain socket auto-unlink behavior](https://nodejs.org/api/net.html#ipc-support) and [macOS `link(2)` atomic no-overwrite contract](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/link.2.html). **Historical checkpoint:** original V2 tests ran only on Linux. A later macOS CI execution validated the pinned patch; see the cross-platform receipt below. Unusual filesystem paths, broader process-race stress and full application CI remain outside these gateway tests.

## Reproducible validation

A real isolated upstream checkout, using Node **22.19.0** and pnpm **10.4.1**, was used for the actual build/tests:

1. Confirmed upstream `development` evolved from the previous `4029e951...` to `97b13afc...`. The change list between these SHAs did not modify the targeted ToolGateway production/test files.
2. Constructed the V2 patch from a working diff at the old baseline; verified `git apply --check` on a separate **current** `development@97b13af...` worktree.
3. **Actually applied V2** to that current-source worktree. `pnpm install --offline --frozen-lockfile --ignore-scripts` succeeded; `pnpm run build:node` **PASS**.
4. Ran `node --test --test-timeout=120000 packages/server/dist/test/tool-gateway-ownership.test.js packages/server/dist/test/tool-gateway.test.js`: **17/17 PASS**, including regressions for cross-process `SIGKILL`, duplicate startup, failed-duplicate shutdown, stale-lock recovery, recovery-lock contention, a different live listener under a stale PID record, and a replaced live socket pathname during the former owner's `stop()`.
5. `git diff --check`: **PASS**.

The two new adversarial tests initially failed on V1 before the repair, with reproducible `Missing expected exception` and `ENOENT` symptoms respectively. This red→green sequence is independent of the original V1's earlier **15/15 PASS** subset: those tests had not covered the two regressions.

### Cross-platform validation — later 2026-10-20 receipt

[Upstream PR #43](https://github.com/opensiro/upstream/pull/43) merged at `00e9a1069da9d63c89558d243eda6bda3a46466d` a **credential-free, read-only** macOS validation workflow on pinned public `HarnessDesk/HarnessDesk@97b13afc819ab7c1a0f8cd20630a428a34c2d47a`. The workflow checks the exact V2 SHA-256 before applying the patch, installs frozen dependencies with scripts disabled, runs the genuine Node build, then executes both gateway suites on `macos-15`.

- [Exact PR-head macOS run #39351363635](https://github.com/opensiro/upstream/actions/runs/39351363635): build **PASS**, gateway **17/17 PASS**.
- [Post-merge `main` macOS run #39351513890](https://github.com/opensiro/upstream/actions/runs/39351513890): build **PASS**, gateway **17/17 PASS**.
- Additionally, the new Linux adversarial regression file completed five successive repeat runs without failures.

This verifies targeted Linux and macOS **socket behavior on the pinned source**, not end-to-end application operation, publication rights or a full upstream gate. The [machine-readable handoff](prepare-v2-handoff.json) is an earlier, deliberately non-authorizing evidence snapshot; its original “macOS unverified” field reflects the preparation time, superseded by these immutable later CI receipts.

### Unfinished checks

- The historical **full** `pnpm check:push` run at V1 was explicitly terminated during long UI typechecking. It was **not** a completed PASS, and it was not evidence of a patch-caused type error.
- A **full end-to-end macOS application run** and broader current upstream `pnpm check:push` / upstream CI remain unverified. The pinned macOS Node build + 17 gateway tests are now validated, but OpenSiro CI does **not** prove acceptance by the external upstream.
- The existing manifest is still `proposal_only`/`prepare_contribution` and contains unresolved authorization blockers. The existence of [the public working fork](https://github.com/opensiro-contributions/HarnessDesk) does **not** constitute a new authenticated grant to push a branch, nor permission to publish a third-party PR.

## Next bounded execution

First conduct an exact, operator-authenticated Control Plane decision for a **new `prepare_contribution` write**, referencing current upstream and fork base SHAs, proposed branch, V2 SHA-256 and intended files. On approval: apply only V2 to the fork's own contribution branch, re-run appropriate checks and CI, and generate a fresh GET-only [external PR handoff](../../scripts/upstream_pr_handoff.py). **The operator remains responsible for external PR publication.** Do not infer approval from `continue`, this file, a digest, an issue comment or the historical one-off fork creation.
