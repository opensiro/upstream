# AgentBox S2 baseline CI migration — 2026-11-11

**Disposition:** `NATIVE_PARITY_PASS_BASELINES_ONLY` for the two historical
source-native **baseline** workflows. The separate manager-advisory workflow
is still owned by the unresolved [Upstream PR #71](https://github.com/opensiro/upstream/pull/71)
and is intentionally retained. These source-only tests do not establish a
RED/GREEN product fix, real agent behavior, adoption or a VSM regrade.

## Immutable source and matched runner receipts

| Evidence | Identity |
| --- | --- |
| First-party source and matching fork `main` at migration | `madarco/agentbox@605ee75d63319003c188bc532d4e5b2ba36a51d6` |
| Frozen Upstream test fixtures | `opensiro/upstream@449ffd57c36d3ecb2a63197b23ac35319ea16fe7` |
| Matching public direct fork | [`opensiro-contributions/agentbox`](https://github.com/opensiro-contributions/agentbox), parent `madarco/agentbox` |
| Dedicated branch and workflow commit | [`opensiro/ci-agentbox-s2-baselines-20261111` @ `56d0835bceac2830bc9f2a0060e9da8bbf04c613`](https://github.com/opensiro-contributions/agentbox/commit/56d0835bceac2830bc9f2a0060e9da8bbf04c613) |
| Task-conflict baseline original run | [Upstream 39683286874](https://github.com/opensiro/upstream/actions/runs/39683286874) |
| Task-conflict baseline fork run | [43069016683 — success](https://github.com/opensiro-contributions/agentbox/actions/runs/43069016683) |
| Dependency-dispatch baseline original run | [Upstream 39683286749](https://github.com/opensiro/upstream/actions/runs/39683286749) |
| Dependency-dispatch baseline fork run | [43069017370 — success](https://github.com/opensiro-contributions/agentbox/actions/runs/43069017370) |
| Task-conflict native test SHA256 | `6bb0d9a79f0e67d3c8945dd72100cda454b6c9d701c8be655bff2b1e25427b4a` — [test](assessment_native_task_conflict_baseline.test.ts) |
| Dependency-dispatch native test SHA256 | `b55104dcc7110117ab7bbe37336aebfe59f5ca93352721c4c10fdc32ed47af87` — [test](assessment_native_dependency_dispatch_baseline.test.ts) |
| Historical task-conflict workflow blob | `558269d64f487326623e8a7920ba6ed294a55420` — [archived recipe](historical-upstream-task-conflict-baseline.yml) |
| Historical dependency workflow blob | `2a779f2d5ec1dffb61dd4c57fb677e5f60d092db` — [archived recipe](historical-upstream-native-dependency-dispatch.yml) |

## Executed native contract

Both matching-fork GitHub Actions ran source-pinned public checkouts with
`permissions: contents: read` and `persist-credentials: false`. The only
workflow changes relative to original Upstream YAML were a dedicated branch
`push` trigger, an explicit immutable `opensiro/upstream` checkout, and a
distinct display name. Node `22`, pnpm `9.15.0`, frozen source lockfile,
full workspace `pnpm build` and the original Vitest commands were unchanged.
The original workflows requested Ubuntu GitHub-hosted Linux (task conflict
`ubuntu-latest`, dependency dispatch `ubuntu-latest`).

| Case | First-party command | Observed fork-native outcome |
| --- | --- | --- |
| Task-conflict preflight | `pnpm --filter @madarco/agentbox exec vitest run test/zz_opensiro_task_conflict_baseline.test.ts` | **1 test PASS**, one test file; native pnpm build PASS |
| Dependency-dispatch baseline | `pnpm --filter @agentbox/relay exec vitest run test/zz_opensiro_dependency_dispatch_baseline.test.ts` | **1 test PASS**, one test file; native pnpm build PASS |

The two fixture files were copied **only** into disposable source checkout
paths (`apps/cli/test/` and `packages/relay/test/`). The original source
SHA was checked; both workflows asserted no tracked first-party product
source changes. The branch contains only two CI YAML files; the fork's
default branch and third-party original were not modified.

These cases measure the bounded source-native **baseline**, not a patch
effect. No source-only production change was introduced and there is no
AFTER product benefit to claim. The upstream manager-advisory prototype
under [PR #71](https://github.com/opensiro/upstream/pull/71) has a different
test/behavior surface and is **not** replaced by these two baseline runs.

## Archival and continuing limits

After successful fork-native parity, the two historical YAML recipes can
be moved byte-for-byte from `upstream/.github/workflows/` into this pilot
directory. Original filenames and Git contents stay reachable at the pinned
pre-migration commit:

- [task-conflict original YAML](https://github.com/opensiro/upstream/blob/449ffd57c36d3ecb2a63197b23ac35319ea16fe7/.github/workflows/agentbox-task-conflict-baseline.yml)
- [dependency-dispatch original YAML](https://github.com/opensiro/upstream/blob/449ffd57c36d3ecb2a63197b23ac35319ea16fe7/.github/workflows/agentbox-native-dependency-dispatch.yml)

Historical and replacement run URLs remain attributable, though GitHub
downloadable logs can expire. Future replays require checking fresh source
and evidence boundaries; this pinned historical test is not an evergreen
claim about later AgentBox releases. New harness-native CI belongs in the
matching working fork under [Upstream #214](https://github.com/opensiro/upstream/issues/214).

**Scope:** `external_delivery=NONE`; `product_benefit=NOT_MEASURED`;
`manager_advisory=RETAINED_OPEN_PR_71`.
