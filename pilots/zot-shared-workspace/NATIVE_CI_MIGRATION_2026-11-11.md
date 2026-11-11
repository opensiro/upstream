# Zot four-case native CI migration — 2026-11-11

**Disposition:** `NATIVE_PARITY_PASS_FOUR_PINNED_EXPERIMENTS`. Four historical
Upstream source-native workflows were reproduced on the correctly parented
public Zot working fork. This preserves the original experiments, not a
product fix or new assessment.

## Immutable source and exact runner

| Evidence | Identity |
| --- | --- |
| First-party source | `patriceckhart/zot@c62d1c549d52cd33390968ffa50667cb79609152` |
| Working fork | [`opensiro-contributions/zot`](https://github.com/opensiro-contributions/zot), parent `patriceckhart/zot`; original source commit resolves inside fork |
| Fork `main` before evidence branch | `4b417b9dc48687318b9b1ef4806355c1d99e4180` — unchanged |
| Frozen OpenSiro fixture and original workflow revision | `opensiro/upstream@c0615edfdfa85a264b03751fd3eeb28d1aeeb6db` |
| Evidence branch | [`opensiro/ci-zot-native-parity-20261111`](https://github.com/opensiro-contributions/zot/tree/opensiro/ci-zot-native-parity-20261111) |
| Fork CI commit (only four workflows) | [`b70ce41b14955842ebd5c5b5263a5a63947a6f19`](https://github.com/opensiro-contributions/zot/commit/b70ce41b14955842ebd5c5b5263a5a63947a6f19) |
| Environment and permissions | GitHub-hosted `ubuntu-latest`, Go `1.25.0`, `contents: read`, both checkout steps `persist-credentials: false` |

The only orchestration differences from original Upstream YAML were a
dedicated fork-branch `push` trigger, an immutable Upstream research-fixture
checkout and a source checkout at the **same exact Zot commit via the
matching working fork**. All original first-party Go commands, fixture
injection paths and selected packages were retained. The four fork runs
were **success on attempt 1**:

| Case | Historical Upstream run | Fork-native run | Preserved observation |
| --- | --- | --- | --- |
| Shared-workspace baseline | [39482937427](https://github.com/opensiro/upstream/actions/runs/39482937427) | [43071812474](https://github.com/opensiro-contributions/zot/actions/runs/43071812474) | 2 intended, 1 preserved, one silent lost update; Go native test PASS |
| Opt-in scoped admission after-case | [39482937643](https://github.com/opensiro/upstream/actions/runs/39482937643) | [43071812481](https://github.com/opensiro-contributions/zot/actions/runs/43071812481) | Baseline 1/2; conditional after-case 2/2 with one explicit rejection/retry; race detector PASS |
| Tool and logical turn gaps | [39482937587](https://github.com/opensiro/upstream/actions/runs/39482937587) | [43071812486](https://github.com/opensiro-contributions/zot/actions/runs/43071812486) | Scope not released on logical turn end, native WriteTool/EditTool can modify claimed file outside wrapper; race detector PASS |
| Manual Git worktrees counterfactual | [39482937216](https://github.com/opensiro/upstream/actions/runs/39482937216) | [43071812698](https://github.com/opensiro-contributions/zot/actions/runs/43071812698) | Shared root preserves 1/2, manually separate worktrees preserve 2/2 and report merge conflict; race detector PASS |

The three race-detector workflows also passed the original complete affected
native `swarm`/`tools` Go package regressions. The baseline passed its exact
selected first-party Go test. Tests used deterministic synthetic workers,
not hosted LLM agents. A `PASS` in the negative tool/turn cases means the
original **limitation** was reproduced, not repaired.

## Research fixture SHA256 (source files all in this directory)

| File | SHA256 |
| --- | --- |
| [`assessment_shared_workspace_baseline_test.go`](assessment_shared_workspace_baseline_test.go) | `6b04e994cd265d38817c8dcf255e828b023eca1efe49157ec1d88d3a67c5e012` |
| [`experimental_manual_worktrees_counterfactual_test.go`](experimental_manual_worktrees_counterfactual_test.go) | `000538e2c2098ae7fcc13dd54c76c8d86287da9dc719f25a41aa36c3fce06585` |
| [`experimental_native_tools_bypass_test.go`](experimental_native_tools_bypass_test.go) | `ef161d1451247cd848626dcc4d5bfacdc1ca346c4aa88c7419c74aa61eb9fe2a` |
| [`experimental_scoped_spawn.go`](experimental_scoped_spawn.go) | `7c74a828d5e3f6c021d47f7b9413ea3304154a96a3f7b001ad1f028f4aec00e7` |
| [`experimental_scoped_spawn_test.go`](experimental_scoped_spawn_test.go) | `19bcca604a919235e92652cfcd72831fa7831e3f4c59a4a47577e6291319767b` |
| [`experimental_turn_boundary_gap_test.go`](experimental_turn_boundary_gap_test.go) | `90986858b004b7bcface93adb68e2545f385c6ade8397a0f811569598f14e3a7` |

## Lossless archived Upstream workflows

The original workflow files were moved **byte-for-byte** into this pilot
directory; their historical run links above and the pre-retirement
Upstream commit preserve attribution. Original Git blob SHAs:

| Original workflow | Archived recipe | Git blob SHA |
| --- | --- | --- |
| `zot-shared-workspace-baseline.yml` | [historical-upstream-shared-workspace-baseline.yml](historical-upstream-shared-workspace-baseline.yml) | `e0a182556fd83cdaca9db364e1a56fa1d9ee49ef` |
| `zot-scoped-admission-after.yml` | [historical-upstream-scoped-admission-after.yml](historical-upstream-scoped-admission-after.yml) | `c502bf9a4f522332ed99084f7013003cad39ef04` |
| `zot-native-tool-turn-boundaries.yml` | [historical-upstream-native-tool-turn-boundaries.yml](historical-upstream-native-tool-turn-boundaries.yml) | `0b0708a5accd39b5c217b8440728239da7a2c9a7` |
| `zot-manual-worktrees-counterfactual.yml` | [historical-upstream-manual-worktrees-counterfactual.yml](historical-upstream-manual-worktrees-counterfactual.yml) | `f0083b896a2cde348df2d03f64fa410c3b147260` |

GitHub run logs/artifacts may expire; the original dated receipts and this
durable migration note preserve the bounded results. The fork default branch,
original third-party source and Zot product files were not modified.
This is **source-only** evidence: no external Zot PR, maintainer acceptance,
shipped benefit, broad S2 safety claim, or Index VSM regrade. The opt-in
wrapper's task/turn and actual native writer limitations remain open;
future Zot revisions require fresh tests. See [Upstream #214](https://github.com/opensiro/upstream/issues/214).
