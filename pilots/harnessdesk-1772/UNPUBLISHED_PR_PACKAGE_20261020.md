# HarnessDesk #1772 — unpublished upstream PR package (2026-10-20)

**Status: prepared locally, NOT a published third-party PR.** This is not a grant, an external submission, or a success claim. Owner: [Upstream #6](https://github.com/opensiro/upstream/issues/6). Working source: `HarnessDesk/HarnessDesk development@81d5e34e0e8e3d7e0945bc680695940b41ab852f`.

## Suggested upstream pull-request metadata (not submitted)

**Proposed title:** `fix(server): preserve tool gateway socket ownership across duplicate hosts`

**Target base:** `HarnessDesk/HarnessDesk:development`

**Working branch (not created):** `opensiro-contributions/HarnessDesk:opensiro/fix-toolgateway-1772`

**Suggested PR body:**

> ### Summary
>
> Fixes #1772. A second headless host reusing a running host's `HARNESSDESK_HOME` must never unlink the active `run/tools.sock` and leave new sessions unable to initialize their tool gateway.
>
> This patch adds an exclusive PID/nonce ownership lock with fail-closed recovery, records the actual Unix socket identity (device and inode), and publishes a temporary sibling socket by a non-overwriting hard link. A duplicate host refuses startup without changing the existing listener. Shutdown removes the public pathname only while the owner nonce and socket identity still match.
>
> ### Safety/regression coverage
>
> Adds `packages/server/test/tool-gateway-ownership.test.ts` to cover simultaneous and duplicate host startup, original server continuity, stale owner recovery, foreign live listener preservation, ownership replacement and shutdown races. The existing `tool-gateway.test.ts` suite runs alongside it.
>
> ### Testing
>
> - `git apply --check`, `git diff --check`, and exact pre/post-file SHA256 on pinned `development@81d5e34`: PASS in a credential-free local sparse checkout.
> - Earlier pinned macOS and Linux Node build and 17/17 gateway regression results are recorded in the OpenSiro implementation receipt; do not substitute them for this exact-source run.
> - **Current-source macOS and full `pnpm check:push`: PENDING / must be updated from real CI results.**
>
> ### Scope
>
> Exactly one production source file and one new package-local test. No changes to app UI, authentication, default branches, release infrastructure or upstream maintainer policies.

The text above is **only a proposed future body**. Before publication, update its testing section to actual source/diff CI results, review maintainer contribution rules and any contributor DCO/CLA representations, and decide externally under the reserved human publication right.

## Exact immutable artifact pins

| Item | Value |
| --- | --- |
| Issue | [HarnessDesk #1772](https://github.com/HarnessDesk/HarnessDesk/issues/1772) |
| Source commit | `81d5e34e0e8e3d7e0945bc680695940b41ab852f` |
| Fork observed development | `4029e95189c61485f934f158c6725ef6eeb7ef35` |
| Intended fork branch | `opensiro/fix-toolgateway-1772` |
| Patch | [V2 exact two-file patch](tool-gateway-ownership-fix-v2.patch) |
| Whole patch SHA-256 | `12b5c7e55a6f730fb9a2465ca30dd47321690c87c0d887e7b8c9d6990ec186e7` |
| Production preimage SHA-256 | `727b8a13c8bcbbd4786c2ab9f048c8ab931f28a45d02aa1701a2c4d1131096ee` |
| Production postimage SHA-256 | `a130ca1fdf78519fa055a12502c35f7b937ebe8caff084975aa8a927a08faa3f` |
| New test postimage SHA-256 | `f8fed230521978811efc3dd5bd32d8c284505201ecee41bf909bb93b3b163b9f` |

## Validation receipts and execution boundary

- Isolated sparse Git checkout fetched from public HarnessDesk at the exact commit. Actual `git apply --check`, `git apply`, and `git diff --check` were successful; actual postimage hashes matched this table exactly. This is **not** an executed Node test.
- [Current source no-write CI workflow](../../.github/workflows/harnessdesk-v2-current-source.yml) tests pinned macOS Node build, two gateway suites and separate Linux `pnpm check:push` after applying the exact patch. Outcomes belong to the actual GitHub Actions jobs, not this preparatory document.
- VM `zhdanov:robot` lacks Node/pnpm and has limited remaining disk; do not report a full local `check:push` run. Remote CI is the chosen validation runner.
- [Proposed finite mandate](../../policies/harnessdesk-1772-local-prepare.json) remains `PROPOSED_NOT_ACTIVE`. Do not create the fork branch or call the external `POST /pulls` before the separately effective owner mandate and publication decision respectively. [Historical prepare packet](prepare-v2-20261020-81d5e34-shared.json) remains non-authorizing.

## Completion checkpoints

1. Read back the exact-source CI jobs and record truthful PASS/FAIL/BLOCKED outcomes.
2. Resolve any source-based regression failures; if the patch changes, publish a new V3 pin and new tests instead of silently rewriting historical V2 receipts.
3. Obtain a separately attributable owner activation of the time-bounded **local fork** mandate. The Control Plane cannot infer activation from a generic `continue`.
4. Recheck current issue/source/fork/branch, then run the existing bounded `--prepare` route; verify one commit and branch plus exact file paths. Stop without retry on ambiguity.
5. Hand over this updated PR title/body/diff/test evidence to the human. The human alone submits the external upstream pull request.
