# OpenSiro assessment-derived replay — Kram S2

## Pre-change frozen plan (2026-10-22)

- Run type: `FRESH_INDEX_FIRST`; index corpus sampled with FNV-1a32 over `index SHA:path`, first 24 paths.
- Independence qualification: `POTENTIALLY_CONTAMINATED` because prior case metadata existed in session context; no prior candidate list was used in the sampling or selection procedure.
- Index commit: `99bfde6da32c4ef2fccce396b3e3938fc959a91f`.
- Assessment path: `assessments/kr/kram.md`, `status: included`, `review_ref: 5f18406709f432dbdb2d6b09da6f140385516366`.
- Selection lock: 2026-10-22T14:29:19Z, before reading Kram current code/issues/PRs and Upstream case receipts.
- Selected function: S2 coordination; Index finding: parallel independently model-directed child task runs share the same workspace, but no first-party collision sensing/resolution/return was established.
- Native hypothesis: concurrent `edit_file` operations against disjoint substrings of the *same file* can lose an edit because each executes `ReadFile -> replacement -> WriteFile` without inter-call arbitration. A narrowly scoped same-file atomicity guard could preserve both edits without centralizing separate-file operations.
- Counterexample: if delegated tasks truly never touch the same path, there is no coordination benefit; a guard might introduce unneeded contention.
- Current external source: `codexmark/kram`, default branch `master`, exact SHA `5f18406709f432dbdb2d6b09da6f140385516366` (matches pinned assessment).
- Adjacent engineering owner: `opensiro/upstream`; not an admitted Organization S1 domain. External GitHub writes not authorized by this replay.

## Frozen before/after evaluation (before intervention)

1. Workload: concurrent calls through Kram's actual shipped `edit_file` Go tool to change separate unique `ALPHA=old` and `BETA=old` markers in one UTF-8 file with 1 MiB of neutral padding, using a synchronized start and 50 trials on each source state. Both change requests represent locally independent edits with shared file-path interference.
2. Control: the same operations against two separate files, 50 trials; both modifications should succeed, demonstrating that broad serialization is not required.
3. Safety: two competing edits of the *same* unique marker must not both silently succeed when one has made the expected old text disappear; the second must observe the changed state or produce an explicit conflict/not-found response.
4. Primary metric: `both_edits_preserved / 50` and `lost_updates / 50` on same-path trials. Threshold for the changed mechanism: all 50 trials preserve both unique edits, none succeeds with a silent lost update. Match workload, runtime, and environment across source states.
5. Null/falsifier: baseline already preserves both consistently, changed behavior shows no meaningful difference, regressions to separate-file progress, or dominant failures. Do not infer real-model task benefit from package-level tests alone.
6. Limits: no model-provider backed subagent task run, real-user workflow, multi-process concurrency, cross-tool `bash`/`write_file` collision, third-party maintainer acceptance, or deployed effect is attested by this focused replay.
7. Regression: Go race test for the focused tool/package; run native repository verification where dependencies and environment permit. Rollback: discard only the local prototype branch, no remote mutation.

## Source-first upstream-native inspection (after selection lock)

- Actual upstream: [codexmark/kram](https://github.com/codexmark/kram), public MIT, default `master`, SHA `5f18406709f432dbdb2d6b09da6f140385516366` at retrieval; reviewed Index revision is still current.
- [delegate_task](https://github.com/codexmark/kram/blob/5f18406709f432dbdb2d6b09da6f140385516366/internal/daemon/tools/delegate.go) concurrently invokes `Delegator.RunTask` (three workers by default); the daemon assembles a shared registry of project-root tools. Delegation prompt explicitly requests independent tasks and does not guarantee file-disjointness.
- [edit_file](https://github.com/codexmark/kram/blob/5f18406709f432dbdb2d6b09da6f140385516366/internal/daemon/tools/edit_file.go) uses a read/replace/write sequence without same-file synchronization. Even edits to different substrings of one shared file can silently overwrite each other.
- [CONTRIBUTING](https://github.com/codexmark/kram/blob/5f18406709f432dbdb2d6b09da6f140385516366/CONTRIBUTING.md) welcomes reproducible correctness bugs and focused changes, requires `./scripts/verify.sh` before a PR. No obligatory issue-first rule for this bugfix or project CLA found in read policy.
- Current GitHub issue/PR searches for `worktree`, `parallel write`, `delegate conflict`, `edit_file race`, `concurrent edit_file` and `lost update` found no exact duplicate. [Issue #31](https://github.com/codexmark/kram/issues/31) and [PR #43](https://github.com/codexmark/kram/pull/43) concern subagent visibility, not the selected file-interference defect.

### Four native-fit gates

| Gate | Result | Evidence and limitation |
| --- | --- | --- |
| `need` | **PASS** | Actual shipped `edit_file` silently loses a distinct update under a repeated concurrent real-tool workload. No user-reported incidence rate was measured. |
| `mechanism` | **PASS (bounded)** | Per-path critical section around the actual read/replace/write operation in the shared registry prevents this class of lost update. Does not lock other writers or processes. |
| `counterfactual_value` | **PASS (tool level)** | With VSM labels removed, preserving independent source edits and refusing to falsely acknowledge competing edits is useful correctness behavior. Real LLM workflow benefit **PENDING**. |
| `scope` | **PASS (local bugfix)** | Narrow built-in file-editor correctness fix, with no tool schema, prompts, permission policy or default delegation workflow change; maintainer's design/acceptance verdict **PENDING**. |

## Baseline — unmodified product code

Exact source commit: `5f18406709f432dbdb2d6b09da6f140385516366`, local clean tracked source. Experimental test added as an untracked file (does not change production behavior), Linux x86-64, official Go 1.26.6.

Command:

```bash
env GOCACHE=/tmp/kram-go-cache GOPATH=/tmp/kram-gopath \
  /tmp/kram-go1266/go/bin/go test ./internal/daemon/tools \
  -run 'TestS2(SameFileEditReplay|SeparateFilesControl|CompetingSameMarker)' \
  -count=1 -v
```

| Trial | Before (50 iterations) | Observable |
| --- | --- | --- |
| Two different-marker `edit_file` changes on one path | **0/50 preserved both; 50/50 silently lost one** | Both tool calls reported success while one expected substring was not updated |
| Two incompatible `edit_file` replacements of one marker | **50/50 double success** | Both tool calls reported success although one value could not survive |
| Two independent paths | **50/50 preserved both** | Disjoint control PASS |

Baseline test exit status **1** (expected RED). One earlier 50-trial run before the safety-case addition measured 1/50 preserved with two tool errors, confirming scheduling variability; the final frozen three-case baseline above is the matched reference.

## Local intervention and matched after

- Prototype source: temporary, isolated local clone `kram-prototype`, branch `experiment/s2-edit-file-atomicity` (NOT pushed).
- Reviewer patch (with supplementary delegated-route test): `kram_s2_edit_file_atomicity_v2.patch`, SHA-256 `c8877dda2405f6d18d5c0693c3620115c8b57907248b4f6c3d42007dec0d030b`. Earlier `kram_s2_edit_file_atomicity.patch` is preserved as the original two-file iteration and must not be confused with this current reviewer patch.
- Scope: three paths, `internal/daemon/tools/edit_file.go` and two new regression test files, `s2_replay_test.go` and `s2_delegate_replay_test.go`. Shared `editFile` instance holds ref-counted, per-real-file locks only during in-flight edits; distinct paths do not share the same lock.
- Source application: `git apply --check --cached` PASS against unchanged baseline index; `git diff --cached --check` PASS.
- Matched after trial: **50/50 same-path different-marker edits preserved**, **0/50 competing-marker double success**, **50/50 distinct paths preserved**, test PASS.
- Focused `go test -race` for the three cases PASS, same after metrics.
- Native `bash scripts/verify.sh` PASS: gofmt, `go vet ./...`, architectural boundary, all Go packages' race suite, every per-package coverage gate (overall 89.5%), host build, Windows amd64 cross-build, Android/Termux arm64 cross-build, shell installer behavior; PowerShell parser unavailable, so its optional parser check was skipped.

**Direct technical effect:** the package-level source behavioral defect is closed under the exact tested concurrent tool-call scenario. **Full product effect:** `INCONCLUSIVE / BENEFIT_NOT_MEASURED` for actual provider-driven multiagent tasks, real user frequency, performance tradeoffs, additional mutating tools, cross-process edits and operating-system edge cases. There is no claim of a changed Index S2 state.

### Supplemental delegated-route replay (performed after the frozen evaluation)

This was a **post-plan validation**, not part of the preregistered three-case frozen evaluation. To test the actual coordination call path, `TestS2DelegatedRegistryReplay` invokes `Registry.Execute("delegate_task", ...)` and installs a synthetic `Delegator` whose two synchronized `RunTask` callbacks each invoke the **same registry's** `Registry.Execute("edit_file", ...)`. Each writes one nonoverlapping marker in the same 1 MiB file. The real `delegate_task` fan-out and permission/registry dispatch execute unchanged; only the LLM's choice of child task calls is synthetic.

```bash
env GOCACHE=/tmp/kram-go-cache GOPATH=/tmp/kram-gopath \
  /tmp/kram-go1266/go/bin/go test ./internal/daemon/tools \
  -run '^TestS2DelegatedRegistryReplay$' -count=1 -v
```

| Actual registry/delegate path | Baseline source | Local changed source |
| --- | --- | --- |
| Both distinct file edits preserved | **1/30** | **30/30** |
| Lost update | **29/30** | **0/30** |
| Both child calls returned success despite lost update | **29/30** | **0/30** |
| Go test exit status | **FAIL** (expected RED) | **PASS** |

The case supports the shared-registry concurrency mechanism and is stronger than a direct tool-only unit test; it is **not** evidence that a provider-backed agent will actually select overlapping tasks, nor that the fix arbitrates across other write tools, independent registries, processes, or unmanaged shell commands.

Supplemental regression status: `go test -race ./internal/daemon/tools -run 'TestS2(SameFileEditReplay|SeparateFilesControl|CompetingSameMarker|DelegatedRegistryReplay)' -count=1 -v` **PASS**; native `scripts/verify.sh` rerun with permission to open localhost test sockets **PASS** (Go race/coverage gates, host/Windows/Android builds, installer checks; PowerShell parser skipped because `pwsh` is unavailable). Its first attempt in the restricted sandbox failed for environment reasons (`httptest: listen ... socket: operation not permitted`), not because of a source regression. The same script completed successfully when local test listeners were permitted.

Final reviewer manifest: base `5f18406709f432dbdb2d6b09da6f140385516366`, **3 files / 262 insertions / 0 deletions**; `git diff --cached --check` PASS and `git apply --check --cached kram_s2_edit_file_atomicity_v2.patch` against the unchanged baseline index PASS. Both the patch and this report are local-only. The patch has **not** been pushed to any GitHub repository.

## Permission and publication record

- S1 test contract is [read-only by default](https://github.com/opensiro/upstream/blob/main/docs/ASSESSMENT_DRIVEN_S1_TEST.md). Control Plane command itself does not authorize external GitHub actions.
- Connected GitHub permissions on `codexmark/kram`: `pull=true`, `push=false`; no new fork was created. There is no exact per-stage owner authorization for this target or working-fork receipt.
- Local clone, compilation and tests used only reversible scratch/temp operations. No third-party GitHub branch, issue, PR, maintainer contact or merge occurred; no OpenSiro-owned PR or ledger write was made.
- Organization [#274](https://github.com/opensiro/vsm-oss-organization/issues/274) remained `PROPOSED / NOT ADMITTED`; Upstream [#6](https://github.com/opensiro/upstream/issues/6) remains the separate execution/authorization gate.
- `origin_class=ASSESSMENT_DERIVED` on documented source-order and functional linkage, with independently-blind-session status `POTENTIALLY_CONTAMINATED`.
- `execution_stage=SOURCE_PREPARED / EXERCISED_LOCAL`; `effect_verdict=BENEFIT_SUPPORTED_TOOL_LEVEL / INCONCLUSIVE_PRODUCT_LEVEL`; `external_publication=NONE`; `maintainer_disposition=NOT_REQUESTED`.
- `authority_used`: public read and local scratch execution only. `human_interventions`: no issue/PR/design decisions by the operator during this replay; original user command supplied the task. No S5 grant or S1 autonomy grade inferred.
- Remaining stop: `BLOCKED_EXTERNAL_STAGE_AUTHORITY` and `PENDING_REAL_AGENT_PRODUCT_EFFECT`. Next eligible actions are first-party design feedback and exact-stage permissioned handoff, not an automatic external publication.

## Comparison after lock with prior method

Read [Upstream #56](https://github.com/opensiro/upstream/issues/56) and the [dated prior case receipt](https://github.com/opensiro/vsm-oss-organization/blob/docs/assessment-upstream-control-plane-replay-20261022/docs/reviews/2026-10-22-assessment-upstream-prior-case.md) only after the Kram selection lock.

| Feature | Prior issue-driven repair and AgentBox S2 research | New Kram replay |
| --- | --- | --- |
| Discovery origin | Issue-driven repairs were typically `ASSESSMENT_INFORMED`; prior AgentBox had Index S2 hypothesis | Index included assessment selected prospectively at immutable SHA |
| Mechanism | AgentBox advisory plan on intended scopes, opt-in, not wired into real workers | Native shipped `edit_file` path, in-memory critical section |
| Pre/post | Prior AgentBox measured task-plan outputs but not file collision | Real shipped file tool baseline **50/50 lost** → **0/50 lost** in matching focused replay |
| Remaining limitation | No real worker/box write benefit measured | No provider-backed agent work or end-to-end user benefit measured |
| External contribution | Prior AgentBox PR was OpenSiro-internal; no external upstream acceptance | No external PR, no current permission for GitHub mutation |

**Conclusion:** The prospectively selected functional finding yielded a reproducible, independently useful, narrowly repaired source-level problem. This advances the assessment-derived test past planning-only evidence, but is **not** a full successful external contribution or fully demonstrated S1 function. The final authority/real-product-feedback stages remain open.
