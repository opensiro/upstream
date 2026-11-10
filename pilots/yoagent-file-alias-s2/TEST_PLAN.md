# yoagent S2 hard-link alias — first-party native regression plan

- **Origin checkpoint:** batch 24 [prospective hypothesis commit](https://github.com/opensiro/upstream/commit/b4fcedc797cb8094897c56764cf85ab33e980472) before first-party inspection.
- **Index:** [canonical assessment](https://github.com/opensiro/vsm-harness-index/blob/8cd38ff31b5b75c6f603624bbbed5072822c5aec/assessments/yo/yoagent.md), S2=C process-wide file-tool lock over paths, reviewed `yologdev/yoagent@f1495e7f5746445a269ec6a9d14fa8ac346b359d`.
- **Current product source:** `main@f1495e7f5746445a269ec6a9d14fa8ac346b359d` (same as assessed ref, read back 2026-11-10 UTC); MIT; [CONTRIBUTING.md](https://github.com/yologdev/yoagent/blob/f1495e7f5746445a269ec6a9d14fa8ac346b359d/CONTRIBUTING.md) requires Rust >=1.86, cargo fmt/clippy/test/doc; no relevant open PR or issue identified by title scan.
- **Native path:** [`PathSandbox::check`](https://github.com/yologdev/yoagent/blob/f1495e7f5746445a269ec6a9d14fa8ac346b359d/src/tools/sandbox.rs) resolves symlinks but returns path strings; [`hold_file`](https://github.com/yologdev/yoagent/blob/f1495e7f5746445a269ec6a9d14fa8ac346b359d/src/tools/file.rs) keys the process-global map by `PathBuf`. POSIX hard links to the same regular file have different canonical path strings while sharing an inode. Read/Write/Edit all acquire this guard. This is a real source-level hypothesis, **not yet a first-party observed failure**.
- **Scoped target:** only regular existing file aliases through two hard links in a single process and the supplied file tools. External processes, arbitrary shells, same-inode content replacement and Windows alias handling remain outside the tested claim.

## Prespecified deterministic workload

1. From exact unmodified source SHA, add one `#[cfg(unix)]` native Rust `#[tokio::test]`: in a temporary directory write `a.txt`, create a hard link `b.txt`, resolve both with the genuine `PathSandbox::check`. Hold `a`'s guard while trying to acquire `b` with a short bounded timeout. **Required BEFORE RED:** alias lock acquisition incorrectly completes before guard release; test fails. Confirm no real model, provider, shell command execution or user workspace mutation.
2. Bounded proposed change: choose a shared `(device,inode)` mutex key for an **existing regular Unix file**, with the previous resolved path key as fallback for not-yet-created/unsupported files and on non-Unix platforms. Keep the cancellation semantics and weak map cleanup unchanged.
3. On the same separate deterministic runner, apply production patch and rerun the **same test**. **Required AFTER GREEN:** alias acquisition is blocked until the first guard is dropped; unrelated inode guard can proceed; original cancellation test still passes. Run bounded first-party `cargo test` plus cargo fmt/clippy as environment permits, report failures rather than assume PASS.
4. Persist source SHA, exact runner identity/environment, test patch hash, source patch hash, commands, observed RED/GREEN, regressions, timeout and confounders. No claimed benefit without this receipt. Any upstream-ready submission needs target policy recheck and a separate human publication decision.

## Decision gates before execution

- `need`: PENDING until source-native failure (hard links are supported OS regular files, but maintainer intent and impact remain separate).
- `mechanism`: PASS static source evidence of `PathBuf`-keyed guard across real built-in file tools.
- `counterfactual`: PENDING until matched test demonstrates preserved isolation without regressions.
- `scope`: PENDING until native runner and maintainer compatibility for a Unix-only path are checked.
- **Expected null:** no failing native test, unsupported multi-link use, or unsafe portability impact → `CLOSED_NO_CHANGE` / `BLOCKED_EVIDENCE`, no patch claim.
