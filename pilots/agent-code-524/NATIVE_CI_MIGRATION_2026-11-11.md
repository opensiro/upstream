# Agent Code #524 source-native CI migration — 2026-11-11

**Disposition:** `NATIVE_PARITY_PASS_FROZEN_AGENT_CODE_524`. All three
historical native gates now have successful matching-fork receipts,
including the corrected three-job Linux/Windows audit. These are
deterministic source-level results, not a shipped product outcome.

## Frozen sources, forks and environment

| Identity | Verified value |
| --- | --- |
| Original first-party source | `avala-ai/agent-code@82e0edfa7372c256d893d0854f954d9099254f88` |
| Correct public working fork | [`opensiro-contributions/agent-code`](https://github.com/opensiro-contributions/agent-code), parent `avala-ai/agent-code`; fork `main` still equals original source SHA |
| Immutable Upstream patch / scripts | `opensiro/upstream@e6433483c14cd12f9c2682d172c70406013936e5` |
| Frozen eight-file source patch SHA256 | `58a70a40beafcceef1f76161f869f4fe2366272d8a82ea9fe9b48fcf530235e1` — [patch](reviewer-subagent-first-slice.patch) |
| Offline/delta evidence branch | [`opensiro/ci-agent-code-524-parity-20261111`](https://github.com/opensiro-contributions/agent-code/tree/opensiro/ci-agent-code-524-parity-20261111) @ [`5a41de5c539d623af5abde7cdf46bb5a57faa739`](https://github.com/opensiro-contributions/agent-code/commit/5a41de5c539d623af5abde7cdf46bb5a57faa739) |
| Corrected cross-platform audit-only branch | [`opensiro/ci-agent-code-524-audit-parity-20261111`](https://github.com/opensiro-contributions/agent-code/tree/opensiro/ci-agent-code-524-audit-parity-20261111) @ [`025bde4b89dd1cea0e818203e662f35968002075`](https://github.com/opensiro-contributions/agent-code/commit/025bde4b89dd1cea0e818203e662f35968002075) |
| Execution environment | GitHub-hosted `ubuntu-latest` and `windows-latest`, Rust toolchain `1.97`, `permissions: contents: read`, credential-free checkouts, exact Cargo lockfile; scripted offline, no real model |

Both offline workflows on the first branch retained the original source
patch verification, first-party tests, Clippy and CLI commands. Every native
checkout points at the exact source SHA **in the corresponding fork**, with
the Upstream handoff and scripts pinned to the immutable fixture revision.

| Gate | Historical Upstream run | Fork-native run | Evidence |
| --- | --- | --- | --- |
| Baseline-vs-patched CLI delta | [39649051245](https://github.com/opensiro/upstream/actions/runs/39649051245) | [43073752245](https://github.com/opensiro-contributions/agent-code/actions/runs/43073752245) | **SUCCESS attempt 1**; original child reused general coding role, patch uses distinct reviewer; missing/malformed mandatory child overlays: old accepted, patched rejects; original main-agent contract retained |
| Patched offline native tests | [39649051475](https://github.com/opensiro/upstream/actions/runs/39649051475) | [43073752502](https://github.com/opensiro-contributions/agent-code/actions/runs/43073752502) | **SUCCESS attempt 1**; 1,761 library and 1,022 CLI unit tests, format, scoped Clippy, patched build, actual offline CLI smoke, synthetic HTTP/mock-provider process smoke, Python evaluator checks |
| Linux/Windows upstream compatibility and baseline strict-Clippy attribution | [39649050989](https://github.com/opensiro/upstream/actions/runs/39649050989) | [43074382674](https://github.com/opensiro-contributions/agent-code/actions/runs/43074382674) | **SUCCESS attempt 1 on corrected audit-only branch**; Linux all-targets check/test, Windows all-targets test and Linux baseline/patched strict-Clippy diagnostic-location comparator PASS |

### Cross-platform audit checkout correction (bounded failed first attempt)

The first attempt on the three-workflow branch, [audit run 43073752362](https://github.com/opensiro-contributions/agent-code/actions/runs/43073752362),
was **FAILURE for orchestration**, not a source-native regression: its
Linux all-targets job had the correct frozen Upstream fixture checkout,
but the Windows and strict-Clippy jobs accidentally used the default fork
checkout for `path: opensiro`, so the handoff patch/scripts were absent.
Those two jobs stopped at fixture preparation **before their native gates**.

The correction is an isolated *audit-only* branch containing one workflow;
**each of its three jobs** now explicitly checks out
`opensiro/upstream@e6433483c14cd12f9c2682d172c70406013936e5` at
`path: opensiro` and first-party source
`opensiro-contributions/agent-code@82e0edfa7372c256d893d0854f954d9099254f88`
at `path: agent-code`. No source or patch bytes changed. This retains
the failed first attempt as evidence, instead of hiding or relabeling it.

The strict-Clippy gate is **diagnostic-location parity**, not a green
unqualified `-D warnings` result. The six historical untouched baseline
`clippy::unnecessary_cast` diagnostic locations remain; the fail-closed
comparator must reject additional locations on the patched source. In the
corrected [audit run 43074382674](https://github.com/opensiro-contributions/agent-code/actions/runs/43074382674),
the comparator observed the same six unique diagnostic locations on the
baseline and `NO_NEW_DIAGNOSTIC_LOCATIONS` on the patched source
(`PATCH_INTRODUCED_STRICT_CLIPPY_DIAGNOSTICS=0`). This **does not**
mean unqualified strict Clippy passes. The Windows
`cargo test --all-targets --locked` completed with zero failed tests;
its primary agent-code-lib suite reported 1,695 passing tests (17 ignored),
and other targets also passed. Linux all-targets check and test both passed.

## Frozen fixture and archive digests

| File | SHA256 / original Git blob |
| --- | --- |
| [`reviewer-subagent-first-slice.patch`](reviewer-subagent-first-slice.patch) | SHA256 `58a70a40beafcceef1f76161f869f4fe2366272d8a82ea9fe9b48fcf530235e1` |
| [`offline_cli_smoke.py`](offline_cli_smoke.py) | SHA256 `716e8ed18055ab741b230226efc23032d58a3d787c644fce47f73e88bb7098cf` |
| [`offline_delta_smoke.py`](offline_delta_smoke.py) | SHA256 `068a8446c06a8f1186e6f8118548e41d28d432934f38a24d3c46df686c349e71` |
| [`mock_provider_smoke.py`](mock_provider_smoke.py) | SHA256 `8a84f2bf0d2937a6ea23ae9c304ae27203c9cc122976a6591e3f60c95a6dea71` |
| [`verify_clippy_baseline.py`](verify_clippy_baseline.py) | SHA256 `6aa0db415fda830a4e3eab0ee04eeaaf8519ad851effdd514137f3b8a78c8e45` |
| [`test_verify_clippy_baseline.py`](test_verify_clippy_baseline.py) | SHA256 `e462be7af68da9e6ac53f6b3969dbd4378ca8ee6008b67ae6568bbf225b5a2bf` |
| [historical-upstream-offline-delta.yml](historical-upstream-offline-delta.yml) | Git blob `3503caeb3b0b0f44dc1678abd18fbb6321b2e26d` |
| [historical-upstream-offline.yml](historical-upstream-offline.yml) | Git blob `f4999e38836d55e7b860c002dd0a5f58359a75d0` |
| [historical-upstream-audit.yml](historical-upstream-audit.yml) | Git blob `eed1bf36c587dc64c3adbe3f78fd073f406c4357` |

All three historical YAML files were moved **byte-for-byte** from
`.github/workflows/` into this pilot. Old workflow registrations and
historical GitHub Actions runs were not manually deleted. GitHub logs
and artifacts may expire; the old dated pilot receipts and this migration
record preserve attribution and scoped results.

**Boundary:** script-level source and binary tests, not model-backed
reviewer quality, OS sandbox enforcement, external maintainer acceptance,
shipped product improvement, autonomous S3* independence or Index regrade.
No original source, working-fork `main`, or third-party PR was changed.
