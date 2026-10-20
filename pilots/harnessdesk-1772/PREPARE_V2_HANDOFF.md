# HarnessDesk #1772 — exact V2 preparation handoff (not authorization)

**Updated pinned source evidence (later on 2026-10-20):** The prior
`prepare-v2-handoff.json` below is a frozen historical snapshot at
`97b13afc`; do not overwrite it. The new
[`prepare-v2-20261020-24aa8d7.json`](prepare-v2-20261020-24aa8d7.json)
pins actual source `development@24aa8d7fdeee47f03f787cc77f40978948bf8141`,
while the public fork `development` remains at `4029e951...`.
On the newest source, V2 exact patch SHA256
`12b5c7e55a6f730fb9a2465ca30dd47321690c87c0d887e7b8c9d6990ec186e7`
applies cleanly; frozen offline dependencies, Node build and gateway
**17/17 tests PASS** on Linux. The packet now includes exact source
preimage and both postimage SHA-256 digests. A separate credential-free
macOS CI run is selected for this newer immutable SHA; do not report it
as passed before a linked completion receipt. The current fork base
mismatch and missing **real one-use host grant** still block writes.
The read-only [provider attestor](../../scripts/cli_host_patch_attestor.py)
was successfully exercised on the real credential-owning VM as
`xLagerFeuer` with `permissions.push=true`, but is **not** an operator
stage authorization.

**2026-10-20, source-only.** See the machine-readable
[`prepare-v2-handoff.json`](prepare-v2-handoff.json) and
[tested V2 patch](tool-gateway-ownership-fix-v2.patch). This is a bounded
candidate **`prepare_contribution`** packet, not a new batch, grant,
approval, working branch, PR or organizational S1 status change.

## Current source and connected-account evidence

Authenticated read-only GitHub CLI on existing VM/host observed (source/fork state is dated; the later macOS validation runs **do not** authorize a write):

| Boundary | Observed |
| --- | --- |
| Executing GitHub identity | `xLagerFeuer` |
| External source | `HarnessDesk/HarnessDesk`, issue #1772 **open** |
| External source `development` | `97b13afc819ab7c1a0f8cd20630a428a34c2d47a` |
| Public working fork | `opensiro-contributions/HarnessDesk`, direct parent confirmed; actor `push=true` |
| Fork `development` | **`4029e95189c61485f934f158c6725ef6eeb7ef35`** (behind source) |
| Proposed branch | `opensiro/fix-toolgateway-1772` — **absent in authenticated GET** |
| Only permitted patch artifact | [V2](tool-gateway-ownership-fix-v2.patch), SHA-256 `12b5c7e55a6f730fb9a2465ca30dd47321690c87c0d887e7b8c9d6990ec186e7` |
| Local source validation | On *current source SHA*: Node build PASS; original+new gateway tests **17/17 PASS** |
| macOS / full upstream gate | **Pinned macOS Node build and gateway tests 17/17 PASS** ([PR run](https://github.com/opensiro/upstream/actions/runs/39351363635), [post-merge run](https://github.com/opensiro/upstream/actions/runs/39351513890)); **full `pnpm check:push` NOT COMPLETE** |

The GitHub API observations above are dated. Refresh exact actor, issue,
source branch, fork identity/parent/push rights, working-branch absence
and patch digest before any future write. Do not treat existing PAT
scopes or this packet as consent.

## Actual execution boundary

The existing [single-test-file adapter](../../scripts/connected_stage_adapter.py)
accepts only one new test file per exact `prepare_contribution` action. **V2
is a two-file patch modifying production code and adding a test file**.
The adapter does **not** implement this action, and no trusted host batch
grant is currently issued for it. It would be incorrect to create a
fake `authorize=lambda _: True`, quietly bypass the adapter using
`git push`, or promote the proposal digest into operator approval.

A future legitimate executor must:

1. Verify **exact** refreshed source+fork SHAs, approved contributor policy,
   owner, branch, V2 SHA-256 and two changed paths. Use `development` of
   the external source as the new contribution branch base; **do not**
   build on the fork's stale `development` without reconciling it.
2. Require a *genuine, attributable, one-use and revocable
   `prepare_contribution` grant* effective in the actual credential-owning
   VM/host. Grant binding includes the **actor**, source/fork,
   source SHA, destination branch, file paths and patch digest. Validate
   independently at execution time.
3. Only then create a new branch in the public fork, apply *only*
   that V2 patch, verify resulting diff and run affected tests and
   `pnpm check:push` / required upstream CI. Never overwrite another
   branch or retry an ambiguous push.
4. Reverify the pushed head/parent and generate a new
   [GET-only external PR handoff](../../scripts/upstream_pr_handoff.py).
   **Human retains the separate external PR publication decision**;
   the handoff does not call GitHub `POST /pulls`.

Source-only verification commands (no GitHub write):

```bash
sha256sum pilots/harnessdesk-1772/tool-gateway-ownership-fix-v2.patch
git -C /path/to/clean/HarnessDesk-development apply --check \
  /path/to/opensiro-upstream/pilots/harnessdesk-1772/tool-gateway-ownership-fix-v2.patch
```

**New source-only multi-file implementation:** The
[exact two-file stage core](../../scripts/connected_multifile_stage.py)
now exists, with [contract and negative tests](../../docs/CONNECTED_MULTIFILE_STAGE.md).
It keeps the original single-file adapter unchanged and **does not activate
a real authenticated host approval issuer or atomic GitHub patch port**.
A later **source-only, optional shared-commit mode** eliminates the need
to synchronize the fork's older `development` branch **if** the exact
current upstream SHA is independently present in the fork and the
fork branch is verified as its ancestor. This route requires a new
exact action binding `fork_observed_sha`, and does not rewrite this
historical proposal packet. The original proposal blockers and absent
authenticated one-use stage grant remain. This is
a later checkpoint than the original JSON snapshot; do not promote the
JSON packet to an authorization.

**Next missing implementation** is a separately reviewed exact
**multi-file, content-bound, host-authorized preparation port** (or an
equivalent trusted host executor), *not* another fork creation and not an
unprotected `gh api POST` in a preview workflow.

No external fork contribution branch or third-party PR was created here.
