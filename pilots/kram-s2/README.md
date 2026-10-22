# Kram S2 — pinned native concurrent-edit replay

**Status:** assessment-derived, local-source effect supported; real product/user benefit **not measured**. [Experiment #56](https://github.com/opensiro/upstream/issues/56).

The selection arose from [current canonical Index `assessments/kr/kram.md`](https://github.com/opensiro/vsm-harness-index/blob/99bfde6da32c4ef2fccce396b3e3938fc959a91f/assessments/kr/kram.md) at `99bfde6da32c4ef2fccce396b3e3938fc959a91f`. The first-party baseline is [`codexmark/kram@5f184067`](https://github.com/codexmark/kram/commit/5f18406709f432dbdb2d6b09da6f140385516366). The origin-order replay is recorded, though a fully blind selection cannot be guaranteed because other cases were visible in the session.

## Reproducible, bounded finding

- Unmodified native `edit_file`: simultaneous edits to separate unique markers of the **same path** silently lost one update in **50/50** local trials.
- The optional local per-file guard: **0/50** lost. Two incompatible edits of the same marker no longer both reported success; independent files passed **50/50**.
- Through native `Registry.Execute("delegate_task", ...)`, with a **synthetic** delegator choosing fixed edit calls: baseline **29/30** lost versus after **0/30**.
- Native Go race checks and the complete repository `scripts/verify.sh` passed locally (PowerShell parser check unavailable). The patch does not alter other mutating tools, separate registries/processes, provider-selected child tasks, or distributed coordination.

The [reviewed three-file patch](s2-edit-file-atomicity-v2.patch) has SHA-256 `c8877dda2405f6d18d5c0693c3620115c8b57907248b4f6c3d42007dec0d030b`. Full [preregistered method and local observations](REPLAY_RECEIPT_2026-10-22.md) include null hypotheses, validity limits and exact commands.

The [read-only CI replay](../../.github/workflows/kram-s2-native-replay.yml) checks out the first-party commit, injects **tests only** for BEFORE, asserts a reproducible original failure, applies just the production change for AFTER, and runs native/race/regression verification. The runner's temporary source checkout is discarded. It does not push to Kram.

For a future authorized contributor stage, see the [prepared Kram contribution handoff](CONTRIBUTION_HANDOFF.md) and [exact machine-readable packet](contribution-handoff-2026-10-22.json). They include the first-party PR text, immutable patch digest, target `master` and explicit **no external write** status; neither is an authorization.

## Stop conditions and next gates

1. **Technical — satisfied for the bounded mechanism:** the pinned native `edit_file` before/after script, scripted `delegate_task` registry dispatch, separate-file control, native Go/race regressions and read-only CI establish the measured correctness delta. **Do not test or require live LLM agents, model APIs or real-user workflows.** Only further deterministic native scripts are in scope if a source-level concern arises; general S2 autonomy and adoption remain unmeasured, not pending gates.
2. **Governance:** exact-stage OpenSiro Control Plane permission and maintainer review are required before any contribution branch or third-party issue/PR. Human owns external publication; maintainer owns acceptance.
3. **Reporting:** `NATIVE_TOOL_BEHAVIOR` and `product_benefit=NOT_MEASURED`, `external_delivery=NONE`. Do not combine with the separate eight-PR lifecycle portfolio or claim an Index grade change.
