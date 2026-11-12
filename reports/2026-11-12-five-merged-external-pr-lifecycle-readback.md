# Five external merged PRs - first-party lifecycle readback (2026-11-12)

**Owner:** OpenSiro Upstream Contributions, issues [#56](https://github.com/opensiro/upstream/issues/56) and [#125](https://github.com/opensiro/upstream/issues/125).

Five distinct third-party source repositories with already-published PRs. Authenticated GitHub REST GET on 2026-11-12 confirmed merge disposition, source-head fork, author, independent maintainer and exact changed-file sets. This is **not** five new submissions, accepted KPI, re-execution of native tests, or deployed product benefit.

## Source-owner merge evidence

| Source | PR | Merged UTC | Maintainer | Final source PR head | Merge commit |
|---|---|---|---|---|---|
| Gen-Verse/DiscoveryRSI | [#2](https://github.com/Gen-Verse/DiscoveryRSI/pull/2) | 2026-10-30T06:10:37Z | JianyuanZhong | `03122c3c081fe2e386e3b6e7a250515f82b1ac15` | `d9a3dfe138a87706ac4850e1fcc6b2d5b0ec3353` |
| chumingjun/dsh-harness-one | [#173](https://github.com/chumingjun/dsh-harness-one/pull/173) | 2026-10-29T08:17:44Z | chumingjun | `daa232cac3096e418e70c887079f8bdac4466a14` | `b0bf15853e3656cb0e5445d06215f66449d395ce` |
| cordfuse/politik | [#33](https://github.com/cordfuse/politik/pull/33) | 2026-11-05T19:01:23Z | steve-krisjanovs | `23570ac446c5e84d20fd8794c9b578e8245c3a43` | `da28ee8523186947f490554df18ad47f6994d24f` |
| ruslantrachuk/dark-factory | [#106](https://github.com/ruslantrachuk/dark-factory/pull/106) | 2026-11-10T16:44:55Z | ruslantrachuk | `bbcd33077bb94befe9599f6f62642caac1cfc885` | `36d788ad7df913d09f91c63be88155323a9f5ae8` |
| splashxmoon/friday | [#23](https://github.com/splashxmoon/friday/pull/23) | 2026-11-10T17:47:58Z | splashxmoon | `0b98947ee5077a08de485b22d13830bcaf9adf90` | `9cdbe26b6e4cb61f88c1fe6e9a6dda503a3b6cb6` |

## Technical provenance and remaining gates

### Gen-Verse/DiscoveryRSI

- **First-party state:** MERGED: https://github.com/Gen-Verse/DiscoveryRSI/pull/2; original PR author xLagerFeuer, head from `opensiro-contributions/DiscoveryRSI`. Merged by `JianyuanZhong` on 2026-10-30T06:10:37Z.
- **Actual changed paths (2):** `src/discovery_rsi/core.py`, `tests/test_replay_snapshot_unittest.py`. These agree with the archived local scope, but do not prove exact post-test patch identity.
- **Assessment origin:** `ASSESSMENT_INFORMED`. [Original native handoff](../pilots/discoveryrsi/CONTRIBUTION_HANDOFF.md) gives historical first-party counterfactuals: baseline 1/4, after 4/4; full project pytest not verified. Native tests **were not re-executed today**.
- **Disposition:** `EXTERNAL_MERGE_SOURCE_CONFIRMED; STRICT_NATIVE_OUTCOME_VERIFICATION_PENDING`. No independently accepted strict outcome, verified deployment, new VSM grade or measured end-user benefit is claimed.

### chumingjun/dsh-harness-one

- **First-party state:** MERGED: https://github.com/chumingjun/dsh-harness-one/pull/173; original PR author xLagerFeuer, head from `opensiro-contributions/dsh-harness-one`. Merged by `chumingjun` on 2026-10-29T08:17:44Z.
- **Actual changed paths (2):** `dsh-plugins/dsh-ccpg-orchestrator/lib/engine.js`, `dsh-plugins/dsh-ccpg-orchestrator/test/native-runid-isolation.test.mjs`. These agree with the archived local scope, but do not prove exact post-test patch identity.
- **Assessment origin:** `ASSESSMENT_INFORMED`. [Original native handoff](../pilots/workflow-one/CONTRIBUTION_HANDOFF.md) gives historical first-party counterfactuals: baseline 2/3, after 3/3; whole engine suite not run. Native tests **were not re-executed today**.
- **Disposition:** `EXTERNAL_MERGE_SOURCE_CONFIRMED; STRICT_NATIVE_OUTCOME_VERIFICATION_PENDING`. No independently accepted strict outcome, verified deployment, new VSM grade or measured end-user benefit is claimed.

### cordfuse/politik

- **First-party state:** MERGED: https://github.com/cordfuse/politik/pull/33; original PR author xLagerFeuer, head from `opensiro-contributions/politik`. Merged by `steve-krisjanovs` on 2026-11-05T19:01:23Z.
- **Actual changed paths (2):** `src/containment.ts`, `tests/containment.test.ts`. These agree with the archived local scope, but do not prove exact post-test patch identity.
- **Assessment origin:** `ASSESSMENT_INFORMED`. [Original native handoff](../pilots/politik/CONTRIBUTION_HANDOFF.md) gives historical first-party counterfactuals: baseline 16/17, after 17/17; original full suite had unrelated failure. Native tests **were not re-executed today**.
- **Disposition:** `EXTERNAL_MERGE_SOURCE_CONFIRMED; STRICT_NATIVE_OUTCOME_VERIFICATION_PENDING`. No independently accepted strict outcome, verified deployment, new VSM grade or measured end-user benefit is claimed.

### ruslantrachuk/dark-factory

- **First-party state:** MERGED: https://github.com/ruslantrachuk/dark-factory/pull/106; original PR author xLagerFeuer, head from `opensiro-contributions/dark-factory`. Merged by `ruslantrachuk` on 2026-11-10T16:44:55Z.
- **Actual changed paths (4):** `.github/workflows/test.yml`, `CONTRIBUTING.md`, `plugins/dark-factory/workflows/feature-core.js`, `tests/test_feature_core_disjointness.mjs`. These agree with the archived local scope, but do not prove exact post-test patch identity.
- **Assessment origin:** `ASSESSMENT_DERIVED`. [Original native handoff](../pilots/dark-factory-s2/CONTRIBUTION_HANDOFF.md) gives historical first-party counterfactuals: baseline 2/5, after 5/5; existing repository checks 36/36; full CI not run. Native tests **were not re-executed today**.
- **Disposition:** `EXTERNAL_MERGE_SOURCE_CONFIRMED; STRICT_NATIVE_OUTCOME_VERIFICATION_PENDING`. No independently accepted strict outcome, verified deployment, new VSM grade or measured end-user benefit is claimed.

### splashxmoon/friday

- **First-party state:** MERGED: https://github.com/splashxmoon/friday/pull/23; original PR author xLagerFeuer, head from `opensiro-contributions/friday`. Merged by `splashxmoon` on 2026-11-10T17:47:58Z.
- **Actual changed paths (2):** `src/agent-mesh.ts`, `test/file-custody-alias.test.ts`. These agree with the archived local scope, but do not prove exact post-test patch identity.
- **Assessment origin:** `ASSESSMENT_DERIVED`. [Original native handoff](../pilots/friday-s2/CONTRIBUTION_HANDOFF.md) gives historical first-party counterfactuals: baseline 0/2, after 2/2; targeted 12/12 and TS typecheck; broad suite not verified. Native tests **were not re-executed today**.
- **Disposition:** `EXTERNAL_MERGE_SOURCE_CONFIRMED; STRICT_NATIVE_OUTCOME_VERIFICATION_PENDING`. No independently accepted strict outcome, verified deployment, new VSM grade or measured end-user benefit is claimed.

## Metric boundary

- These five PRs were **already present** in the 33-PR maintenance watchlist; do not add five to its publication count.
- A GitHub merge, matched author/fork and exact path set prove the narrow source-side disposition, **not** that the final tested change is identical, all first-party CI gates passed or product benefit was measured.
- The existing strict automatic outcome fast path is bounded and requires fully revalidated immutable native CI/provenance. This report does not edit the accepted outcome file or widen the metric by inference.
- These five third-party source PRs were merged by their original maintainers; OpenSiro performed **no new external PR write** in this readback.
