# HarnessDesk #1772 native CI migration — 2026-11-11

**Both source-native workflows retired — matching-fork parity PASS.**
Current-source Linux/macOS and older-source macOS ran successfully in
the correct fork, with exact pinned sources and original recipes archived.

## Frozen provenance

- Original [HarnessDesk/HarnessDesk](https://github.com/HarnessDesk/HarnessDesk);
  matching fork [opensiro-contributions/HarnessDesk](https://github.com/opensiro-contributions/HarnessDesk).
- Source pinned on both OS jobs: `81d5e34e0e8e3d7e0945bc680695940b41ab852f`.
- Fork evidence branch [`opensiro/ci-harnessdesk-v2-parity-20261111`](https://github.com/opensiro-contributions/HarnessDesk/tree/opensiro/ci-harnessdesk-v2-parity-20261111)
  at [`92583f632215d1b1891619e4d0430462bcbaf20d`](https://github.com/opensiro-contributions/HarnessDesk/commit/92583f632215d1b1891619e4d0430462bcbaf20d).
- Immutable OpenSiro fixture checkout: `e6433483c14cd12f9c2682d172c70406013936e5`.
  Patch SHA256 `12b5c7e55a6f730fb9a2465ca30dd47321690c87c0d887e7b8c9d6990ec186e7`;
  gateway postimage `a130ca1fdf78519fa055a12502c35f7b937ebe8caff084975aa8a927a08faa3f`;
  test postimage `f8fed230521978811efc3dd5bd32d8c284505201ecee41bf909bb93b3b163b9f`.
- Original YAML archived **byte-for-byte**:
  [`historical-upstream-current-source.yml`](historical-upstream-current-source.yml).
  Original Git blob: `80975f761651a2691da355047d9bd524c02d155a`.

## Source-native jobs

| Gate | Historical | Matching fork | Result |
| --- | --- | --- | --- |
| macOS 15 gateway original/V2 tests | [42879924218](https://github.com/opensiro/upstream/actions/runs/42879924218) | [43075481763 attempt 2](https://github.com/opensiro-contributions/HarnessDesk/actions/runs/43075481763/attempts/2) | **PASS**: actual allocated macOS runner, exact source/patch, Node 22.19.0, pnpm 10.4.1, build + regression tests |
| Linux complete `pnpm check:push` | [42879924218](https://github.com/opensiro/upstream/actions/runs/42879924218) | [43075481763 attempt 2](https://github.com/opensiro-contributions/HarnessDesk/actions/runs/43075481763/attempts/2) | **PASS**: actual Linux runner, pinned source/patch, full native suite |

Fork checks use identical native OS/runtime/test commands, but branch-only
triggers and credential-free pinned checkouts of the matching fork source and
OpenSiro evidence. Original [attempt 1](https://github.com/opensiro-contributions/HarnessDesk/actions/runs/43075481763/attempts/1)
failed only because GitHub could not allocate a macOS runner; Linux passed.
That failed attempt is retained as infrastructure evidence.

## Older-source macOS parity

`development@24aa8d7fdeee47f03f787cc77f40978948bf8141` is tested in the
archived [`historical-upstream-macos.yml`](historical-upstream-macos.yml)
(original Git blob `e5e233d13b0158f07bd9addb28297eb38db8f8cb`).
The [pinned integrity test](../../tests/test_harnessdesk_v2_current_pin.py)
now reads the byte-identical archived recipe. Matching-fork
[run 43075481835 attempt 2](https://github.com/opensiro-contributions/HarnessDesk/actions/runs/43075481835/attempts/2)
**PASS** on an actually allocated macOS runner: source
`24aa8d7fdeee47f03f787cc77f40978948bf8141`, patch SHA, Node 22.19.0,
pnpm 10.4.1, native build and gateway regressions. Its failed
first attempt is preserved as a runner-capacity failure, not a code defect.

This is frozen source-level evidence, not shipped benefit, external PR
acceptance, Index reassessment, or VSM grade change.
