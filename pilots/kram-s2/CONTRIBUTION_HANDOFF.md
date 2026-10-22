# Kram S2 — prepared upstream contribution (no external write)

**State:** `ACTION_PREPARED_NOT_AUTHORIZED`, 2026-10-22. **Owner:** `opensiro/upstream` issue [#56](https://github.com/opensiro/upstream/issues/56). This packet is a reviewable proposal, **not** an operator grant, contributor fork, pushed branch, opened third-party PR or maintainer decision.

## Source and first-party fit

- **Selected from Index first:** [Kram assessment at `99bfde6`](https://github.com/opensiro/vsm-harness-index/blob/99bfde6da32c4ef2fccce396b3e3938fc959a91f/assessments/kr/kram.md), S2 shared-workspace coordination; selection was **potentially contaminated** by previously viewed project context, as recorded in the [frozen replay](REPLAY_RECEIPT_2026-10-22.md).
- **External source:** [`codexmark/kram` `master@5f184067`](https://github.com/codexmark/kram/commit/5f18406709f432dbdb2d6b09da6f140385516366). This was still its latest `master` commit in a read-only GitHub check on 2026-10-22; it must be refreshed at execution time.
- **Policy:** [first-party `CONTRIBUTING.md`](https://github.com/codexmark/kram/blob/5f18406709f432dbdb2d6b09da6f140385516366/CONTRIBUTING.md) welcomes focused reproducible reliability fixes, targets **`master`**, asks for `./scripts/verify.sh` and a PR explaining runtime impact and limits. No issue-first requirement for this exact bug was found. Relevant pre-existing [PR #95](https://github.com/codexmark/kram/pull/95) adds a user-facing proposed diff preview for edit/write approval, **not** a lock around committed `edit_file` writes; this correctness fix does not claim to make preview-and-commit one atomic transaction.
- **Overlap:** read-only searches for exact same-file lost-update/synchronization issues or PRs revealed no matching fix on 2026-10-22; this is a dated negative search, not a proof that no future conflict exists.

## Exact proposed change

| Invariant | Prepared value |
| --- | --- |
| Baseline | `codexmark/kram` `master@5f18406709f432dbdb2d6b09da6f140385516366` |
| Working fork (proposed only) | `opensiro-contributions/kram` — **existence, parent and rights unverified** |
| New branch (proposed only) | `opensiro/fix-kram-concurrent-edit-loss` — **absence unverified** |
| Patch | [`s2-edit-file-atomicity-v2.patch`](s2-edit-file-atomicity-v2.patch) |
| SHA-256 | `c8877dda2405f6d18d5c0693c3620115c8b57907248b4f6c3d42007dec0d030b` |
| Change set | `edit_file.go` plus `s2_replay_test.go`, `s2_delegate_replay_test.go`; **3 files, 262 insertions, no deletions** |
| Policy | **Native deterministic scripts only; no LLM-agent/Browser/model-provider testing** |
| External execution | **None** — no fork, branch, issue, PR, maintainer contact or merge performed |

The change introduces a short-lived per-resolved-path lock around the actual native `edit_file` read/replace/write sequence. It prevents **same-registry concurrent `edit_file` calls** from silently losing disjoint edits to a shared file, while independently addressed files remain concurrent. It does not serialize separate registries/processes, `write_file`, shell commands or every possible path alias/filesystem race.

## Evidence sufficient for the scoped technical gate

| Native source test | Original | Patched |
| --- | --- | --- |
| Same-file disjoint-marker lost update | **50/50** | **0/50** |
| Through `Registry.Execute("delegate_task")` with a fixed-action script fixture | **29/30** | **0/30** |
| Distinct-file independent control | **50/50 preserved** | **50/50 preserved** |

- [Original pinned CI replay](https://github.com/opensiro/upstream/actions/runs/39826632281) and [policy PR replay](https://github.com/opensiro/upstream/actions/runs/39829252198): expected BEFORE failure, patched AFTER and native/race suite **PASS**; first-party `scripts/verify.sh` **PASS** on Linux; PowerShell parser check skipped (`pwsh` unavailable).
- Patch digest and source base are independently checked in [contract tests](../../tests/test_kram_s2_replay_contract.py). `git apply --cached --check` against the clean baseline index passed on 2026-10-22 (local workspace also contains untracked replay test fixtures; a normal `git apply --check` there would collide with them).
- This proves the bounded native mechanism, **not** deployed user benefit, provider-selected task efficacy, S2 autonomy regrade or external acceptance. The absence of live LLM-agent tests is the **agreed method**, not a missing technical gate; see [PR #76](https://github.com/opensiro/upstream/pull/76).

## Draft third-party PR — copy after an authorized branch exists

**Proposed title:** `fix(tools): prevent lost concurrent edit_file updates`

**What changed**

`edit_file` now serializes read/replace/write for the same resolved path within one shared registry. The lock is acquired after path validation and released after the write; separate paths do not share a lock, and idle lock entries are removed. Added native Go tests for same-file disjoint changes, conflicting replacements, independent files and `delegate_task` registry dispatch.

**Why**

Previously, two concurrent calls could read the same original file, both report success, and the later write silently erase the other call's independent edit. With the pinned baseline, a deterministic scripted concurrent replay lost a distinct update in all 50 trials. The proposed patch preserved both in all 50 equivalent trials. A second registry-dispatch test observed 29/30 baseline losses versus 0/30 after.

**Runtime impact**

- [x] Tools / permissions — `edit_file` correctness when native tool calls overlap on one path
- No change to the tool schema, delegation prompt, model/provider, permission policy or unrelated mutating tools

**Verification**

- [x] `./scripts/verify.sh` (Linux, pinned source, read-only temporary CI checkout)
- [x] Go native targeted tests including `-race`, baseline-vs-patch scripted replay
- [x] Linux build and Go Windows/Android cross-build checks as part of the first-party script
- Manual/real-agent acceptance: not run or required by the scoped deterministic technical protocol

**Platforms actually exercised**

- Linux amd64 for script execution and Go race tests; Windows amd64/Android arm64 **cross-built only**, not natively run; optional PowerShell parser unavailable

**User-visible behavior**

Concurrent native `edit_file` operations on separate substrings of the same file no longer silently lose an update in the tested shared-registry scenario; incompatible edits can report that the expected old text is missing after another edit.

**Known limitations**

Locks are per `editFile` tool instance, not cross-process or cross-tool; this is not an atomic commit of every file write or of the human diff preview. No deployed-user frequency, model-selected task benefit or cross-platform native run was measured.

## Execution and authority — explicit stops

1. A future executor must **refresh** current Kram `master`, policies, conflicts and the selected fork's parent/visibility/branch/permission state. A changed baseline requires a new patch-compatibility and test receipt, never an automatic push of stale bytes.
2. The owner must separately authorize a concrete `create_public_fork` action if needed, then a distinct `prepare_contribution` action bound to the actual actor, exact repository/ref, branch/path set and patch digest under [Upstream #6](https://github.com/opensiro/upstream/issues/6). Merely saying "continue" or having a connected PAT **does not** issue the grant.
3. An authorized host may then prepare the narrowly scoped branch and return a verified readback **without publishing a PR**. The final third-party PR creation remains human-owned and is not included in this packet.
4. Until those gates, status stays **`ACTION_PREPARED_NOT_AUTHORIZED`**; external delivery is `NONE`, and this pilot must not be counted as upstream acceptance or VSM regrade.

Machine-readable snapshot: [`contribution-handoff-2026-10-22.json`](contribution-handoff-2026-10-22.json).
