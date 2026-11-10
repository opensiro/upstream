# yoagent — independent source-native host receipt (2026-11-10 UTC)

**Cohort:** Upstream upgrade 24 / [#56](https://github.com/opensiro/upstream/issues/56). **Hypothesis checkpoint:** [b4fcedc](https://github.com/opensiro/upstream/commit/b4fcedc797cb8094897c56764cf85ab33e980472), before target-code inspection. **Index:** [assessment at 8cd38ff](https://github.com/opensiro/vsm-harness-index/blob/8cd38ff31b5b75c6f603624bbbed5072822c5aec/assessments/yo/yoagent.md), S2=C. **First-party product source:** `yologdev/yoagent@f1495e7f5746445a269ec6a9d14fa8ac346b359d`; actual default branch read back at the same SHA on 2026-11-10.

## Independent execution identity and inputs

- Execution surface: registered SSH device **dev-alpha-2 / Zhdanov's Siro VM**, distinct from the assessment chat runtime. Native compiler/test runner was a Docker `rust:1.91` container (actual Rust toolchain **1.91.1**) with project first-party Rust files; no live agent, LLM, model provider, browser, or user-facing harness session.
- Clean source worktree: `/home/robot/upstream-upgrade24-yoagent-source`, checked `git rev-parse HEAD` = `f1495e7f5746445a269ec6a9d14fa8ac346b359d`, unmodified before patch application. Separate runner worktree: `/home/robot/upstream-upgrade24-yoagent-runner`, originally same SHA.
- Archived [native regression](native-regression.patch) SHA-256: `ab7994de0c0dbc0ab583746f38340f916dbf817f2eb58911731054bc9412287b`.
- Archived [native source fix](native-fix.patch) SHA-256: `a4646350abef97cb76cf4f8bc7506cfe31f961b37a5896e5e61ddb2d50d20c94`.
- Both final formatted patch files were separately checked with `git apply --check` against the clean source SHA; `git diff --check` on the patched worktree passed. After an initial formatting-only diff, `cargo fmt` and `cargo fmt -- --check` exited 0 (session `4fdddd04-e695-4ccf-9a50-afd3fbb88b9e`). Formatting changed presentation, not patch logic. The matched RED/GREEN runs preceded formatting but used the same Rust source/test behavior.

## Matched native outcomes

| Stage | Exact first-party action | Independent session | Observed |
| --- | --- | --- | --- |
| Before | Apply **regression-only** patch to the pinned source; `cargo test --lib hard_link_aliases_share_the_same_file_mutex -- --nocapture` | `0945f13f-ad83-4b16-8282-a0876daeff85` | **RED** (exit 101): test panicked at `src/tools/file.rs:1271:9`, `a hard-link alias must wait on the same file mutex`. This confirms lock aliasing, not merely failed compilation. |
| After | Apply only bounded source-fix patch in the same source/testing environment; `cargo test --lib tools::file::tests -- --nocapture` | `80b2d155-049d-4779-aa29-bd6160971d73` | **GREEN** (exit 0): **2 passed / 0 failed**, including hard-link regression and existing cancellation test. |
| Expanded native | `cargo test --lib` | `602c89c8-5363-4b87-9dc6-d7dc9db24e14` | **GREEN** (exit 0): **592 passed / 0 failed / 0 ignored** (10.16 s). |
| Formatting | `rustup component add rustfmt && cargo fmt && cargo fmt -- --check` | `4fdddd04-e695-4ccf-9a50-afd3fbb88b9e` | **PASS** (exit 0). |
| Strict library lint | `rustup component add clippy && cargo clippy --lib -- -D warnings` | `88013141-0955-4962-926c-4396fda02d2b` | **PASS** (exit 0), toolchain Rust 1.91.1, no warnings. |

Docker invocation for native tests (with the same container mount/cached registry in both phases):

```sh
docker run --rm -e CARGO_BUILD_JOBS=4 \
  -v /home/robot/upstream-upgrade24-cargo-registry:/usr/local/cargo/registry \
  -v /home/robot/upstream-upgrade24-yoagent-runner:/work \
  -w /work rust:1.91 cargo test --lib tools::file::tests -- --nocapture
```

For RED use the same container and `cargo test --lib hard_link_aliases_share_the_same_file_mutex -- --nocapture`; for the expanded run replace the trailing cargo command by `cargo test --lib`. The original test first failed *after compilation*, so this is a genuine behavior-level before/after comparison.

## Environmental limits and nonclaims

- A first attempt with Rust **1.86** was blocked by current resolved `wiremock 0.6.5` (let-chains requiring a newer toolchain); `--locked` also failed because the checked-in lockfile required updating. Both substantive RED/GREEN runs therefore used Rust **1.91.1**, and Cargo's resolved local `Cargo.lock` changed during dependency resolution. **Minimum Rust 1.86 support is not attested** by this experiment.
- This reproducer concerns two **existing Unix regular-file hard links** accessed via the product's **in-process** file lock. It does not test cross-process locking, file rename/replacement races, Windows semantics, product-level tool sequences or deployed agents.
- The full result is **library tests**, not the entire first-party integration/CLI suite. No user outcome, benchmark, maintainer acceptance or VSM-grade uplift is claimed.
- Prepared internal patch only; **no third-party fork, branch or PR** and no external publication authorization inferred. A current-target and contribution-policy recheck remains necessary at the external gate.
