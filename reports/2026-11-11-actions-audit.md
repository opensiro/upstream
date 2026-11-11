# Upstream GitHub Actions inventory — 2026-11-11

**Scope:** public `opensiro/upstream` `main` at
`4fc443fdf87bb7d3c54cc96c9f57a8adc25a2c6d`, compared with the
GitHub Actions workflow registration API and recorded native run evidence.
This is a dated cleanup baseline, **not** a live workflow-status dashboard.

## Reconciliation

| Classification | Workflows | Disposition |
| --- | ---: | --- |
| Upstream-owned control files on `main` | 8 | Keep; distinct repository CI, fork preview, PR sensing and gated local operations |
| Historical per-source native CI files on `main` | 15 | Retirement-only; migration governed by [#214](https://github.com/opensiro/upstream/issues/214) |
| Additional workflow registrations in GitHub Actions absent from `main` | 9 | Inspect associated PR/head ref and evidence before disabling |
| **Total workflow files on `main`** | **23** | `find .github/workflows -maxdepth 1 -name '*.yml'` |
| **Total registered workflows exposed by GitHub API** | **32** | `gh api repos/opensiro/upstream/actions/workflows` |

An API `state=active` is a *registration state*, not evidence that a workflow
exists on `main` or runs on a current schedule. **The difference of nine is
not nine duplicate YAML files waiting to be deleted from `main`.**

## Keep: Upstream's own eight actions

| File | Purpose |
| --- | --- |
| `repository-integrity.yml` | Repository-wide checks on PRs and `main` |
| `test-fork-lifecycle.yml` | Fork-lifecycle code regression |
| `fork-lifecycle.yml` | Manual, read-only fork-lifecycle preview |
| `pr-maintenance.yml` | Hourly bounded external-PR/CI inbox updates |
| `portfolio-reconciliation.yml` | Portfolio PR state observation; run artifact |
| `verified-external-outcomes.yml` | Evidence-candidate observation, not accepted KPI |
| `upstream-status-freshness.yml` | External PR lifecycle drift detection |
| `upstream-status-proposal.yml` | Scheduled read-only drift patch; manually gated internal Draft PR |

See [action map](../docs/ACTIONS.md) for direct workflow links, user intents
and permission boundaries. Merging their schedules/permissions merely to
minimize count is not supported by this audit.

## Retire only after native equivalence: 15 legacy files on `main`

| Target | Legacy workflow path (under `.github/workflows/`) | Historical successful run ID | Migration gate |
| --- | --- | --- | --- |
| Agent Code | `agent-code-524-offline-delta.yml` | [39649051245](https://github.com/opensiro/upstream/actions/runs/39649051245) | Pinned offline delta vs fork-native reproduction |
| Agent Code | `agent-code-524-offline.yml` | [39649051475](https://github.com/opensiro/upstream/actions/runs/39649051475) | Pinned offline source verification |
| Agent Code | `agent-code-524-upstream-audit.yml` | [39649050989](https://github.com/opensiro/upstream/actions/runs/39649050989) | Third-party audit/replay parity |
| AgentBox | `agentbox-native-dependency-dispatch.yml` | [39683286749](https://github.com/opensiro/upstream/actions/runs/39683286749) | Dependency scheduling baseline |
| AgentBox | `agentbox-s2-manager-advisory.yml` | [39683286746](https://github.com/opensiro/upstream/actions/runs/39683286746) | Preserve related [open PR #71](https://github.com/opensiro/upstream/pull/71) |
| AgentBox | `agentbox-task-conflict-baseline.yml` | [39683286874](https://github.com/opensiro/upstream/actions/runs/39683286874) | Task-conflict baseline |
| HarnessDesk | `harnessdesk-v2-current-source.yml` | [42879924218](https://github.com/opensiro/upstream/actions/runs/42879924218) | Current-source check still ran on 2026-11-10 |
| HarnessDesk | `harnessdesk-v2-macos.yml` | [39437232817](https://github.com/opensiro/upstream/actions/runs/39437232817) | Pinned macOS test and [`test_harnessdesk_v2_current_pin.py`](../tests/test_harnessdesk_v2_current_pin.py) |
| Kit | `kit-222-compat.yml` | [39674571202](https://github.com/opensiro/upstream/actions/runs/39674571202) | Compatibility regression parity |
| Kit | `kit-222-offline.yml` | [39674571130](https://github.com/opensiro/upstream/actions/runs/39674571130) | Offline native regression parity |
| Kram | `kram-s2-native-replay.yml` | [39830836737](https://github.com/opensiro/upstream/actions/runs/39830836737) | **No equivalent working-fork workflow evidenced**; establish replacement runner |
| Zot | `zot-manual-worktrees-counterfactual.yml` | [39482937216](https://github.com/opensiro/upstream/actions/runs/39482937216) | Pinned worktrees counterfactual |
| Zot | `zot-native-tool-turn-boundaries.yml` | [39482937587](https://github.com/opensiro/upstream/actions/runs/39482937587) | Tool-turn boundary evidence |
| Zot | `zot-scoped-admission-after.yml` | [39482937643](https://github.com/opensiro/upstream/actions/runs/39482937643) | Admission after-case |
| Zot | `zot-shared-workspace-baseline.yml` | [39482937427](https://github.com/opensiro/upstream/actions/runs/39482937427) | Shared-workspace baseline |

The run IDs are **historical references**, not proof that a corresponding
workflow in `opensiro-contributions` covers the same source, patch, tests,
OS/runtime or baseline RED / AFTER GREEN. The [native placement rule](../docs/NATIVE_CI_EXECUTION.md)
and [#214](https://github.com/opensiro/upstream/issues/214) require a
source-pinned replacement receipt before each actual removal. Six matching
forks were observed; ordinary fork `ci.yml` files alone do not close the
parity gate. The Kram source fork had no equivalent workflow observed.

## Registered in GitHub but absent from `main`: nine entries

| Registered workflow path | Investigation before disabling |
| --- | --- |
| `agent-fleet-s2-native-replay.yml` | Check [PR #119](https://github.com/opensiro/upstream/pull/119) and its current head |
| `agentbox-s2-plan-prototype.yml` | Check AgentBox pilot PR history, current source and needed run retention |
| `assessment-upgrade-b14-runloop-native.yml` | Check historical [Runloop PR #174](https://github.com/opensiro/upstream/pull/174) and [pinned run](https://github.com/opensiro/upstream/actions/runs/42493920695) |
| `citadel-s2-native-replay.yml` | Check [PR #118](https://github.com/opensiro/upstream/pull/118) |
| `evidence-bench-retrieval-admission.yml` | Check [PR #120](https://github.com/opensiro/upstream/pull/120) |
| `fara-native-resume.yml` | Check [PR #121](https://github.com/opensiro/upstream/pull/121) |
| `harnessdesk-v2-current-full-gate.yml` | Check historical HarnessDesk branch and tests |
| `improvement-candidates.yml` | Check [PR #67](https://github.com/opensiro/upstream/pull/67) |
| `nanocoder-s2-native-replay.yml` | Check [PR #123](https://github.com/opensiro/upstream/pull/123) |

These are **not** additional workflow files on current `main`. Their
registration is retained as observed, and this audit performs no API
disable/delete operation on an open PR's CI. Future cleanup should first
match each registered ID to its exact branch and live PR disposition.

## Result and recommended sequence

1. **Now:** provide one operator-facing [Action map](../docs/ACTIONS.md) and
   correct the root README's stale standing-mandate and fork-proposal routing.
2. **Next:** for each six-source legacy group, preserve pinned receipts and
   verify first-party native replacement; remove only proven redundant YAML
   through a reviewable PR under [#214](https://github.com/opensiro/upstream/issues/214).
3. **Separately:** reconcile the nine API-only registrations against open PRs
   and protected evidence; disable only individually confirmed orphans.

**Initial documentation PR #218:** navigation and report only; no YAML
removed and no workflow state changed at that stage. Native equivalence for
the 15 legacy `main` files was not yet demonstrated, and no CI or publication
permissions were widened.

## Post-audit registered-workflow cleanup (2026-11-11)

After checking the exact associated PRs, current-main workflow paths and
historical run receipts, two **branch-only** registrations were disabled via
the GitHub Actions API. Neither workflow YAML exists on `main`, neither
related PR is open, and no run artifacts were deleted:

| Workflow ID | Path | Source PR / historical evidence | Verified API state |
| --- | --- | --- | --- |
| `411236102` | `assessment-upgrade-b14-runloop-native.yml` | [Merged #174](https://github.com/opensiro/upstream/pull/174) · [run 42493920695](https://github.com/opensiro/upstream/actions/runs/42493920695) | `disabled_manually` |
| `390833119` | `harnessdesk-v2-current-full-gate.yml` | [Merged #55](https://github.com/opensiro/upstream/pull/55) · [run 39467673123](https://github.com/opensiro/upstream/actions/runs/39467673123) | `disabled_manually` |

The **other seven** registered, absent-from-main workflow paths correspond
to open technical PRs (#71, #67, #119, #118, #120, #121, #123) and remain
enabled pending their PR disposition. The resulting registered workflow
states are **30 active + 2 manually disabled**; the number of workflow files
on `main` is still 23. This targeted API cleanup is reversible and did not
alter Git history, source-native receipts, workflow permissions or CI in
active PRs. The 15 legacy main-branch files remain subject to the separate
source-equivalence gate [#214](https://github.com/opensiro/upstream/issues/214).

## Subsequent control-workflow deduplication

The [run-volume audit](2026-11-11-actions-run-volume.md) found that the
separate `test-fork-lifecycle.yml` control workflow executed the same full
offline test suite as the unfiltered `repository-integrity.yml`. With no
unique test or required-status-check dependency, it was removed from the
control allowlist and `main` by a follow-up reviewable change. This brings
the control set from eight to **seven**, without affecting the 15
source-native legacy workflows or their migration gates. The 23-file count
above is the **initial dated baseline**, not the post-dedup count.

## First source-native migration: Kram

On 2026-11-11, the source-matched
[`opensiro-contributions/kram` pinned native runner](https://github.com/opensiro-contributions/kram/actions/runs/43059374414)
completed `success`. It reproduced the original S2 RED, the source-only
patched GREEN under the Go race detector and the complete first-party
`scripts/verify.sh`. The [durable migration receipt](../pilots/kram-s2/NATIVE_CI_MIGRATION_2026-11-11.md)
records source, patch, test digests, branch SHA, exact native counts, original
Upstream run and runner permissions. The old workflow is preserved byte-for-
byte as a pilot artifact and retired from `.github/workflows` by reviewable
PR. After that merge, **14** historical source-native workflows remain on
Upstream `main`; this does not close any other source's parity gate.

## Second source-native migration: Kit offline only

On 2026-11-11, the historical Kit #222 offline RED/GREEN workflow was
reproduced successfully in its correctly parented
[`opensiro-contributions/kit` fork](https://github.com/opensiro-contributions/kit),
using a dedicated branch and frozen source
`speakeasy-api/kit@8f9f08a2b2088381f1cb106dcb9129378f8f0b4e`.
The [native offline run](https://github.com/opensiro-contributions/kit/actions/runs/43064797099)
verified the expected RED, patched GREEN, 1329 passing library tests,
strict Clippy, formatting and real offline CLI recovery. The
[durable receipt](../pilots/kit-222/NATIVE_CI_MIGRATION_2026-11-11.md)
preserves exact source/patch/runner evidence. Its former Upstream YAML was
archived byte-for-byte and retired by a separate reviewable PR. After that
PR merges, **13** historical source-native workflows remain on `main`.

The separate [Linux/macOS compatibility run](https://github.com/opensiro-contributions/kit/actions/runs/43064796979)
passed its Linux native job, but GitHub failed to allocate a hosted macOS
runner on its first attempt. The original `kit-222-compat.yml` **remains on
Upstream `main`** until equivalent fork-native macOS coverage completes.
Neither engineering result proves Kit maintainer adoption, shipping or
current-source compatibility.
