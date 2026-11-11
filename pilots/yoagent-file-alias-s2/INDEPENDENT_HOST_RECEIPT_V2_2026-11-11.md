# yoagent S2 — V2 source-native revision receipt (2026-11-11 UTC)

**Identity:** `yologdev/yoagent@f1495e7f5746445a269ec6a9d14fa8ac346b359d`, assessment at `opensiro/vsm-harness-index@8cd38ff31b5b75c6f603624bbbed5072822c5aec`, reviewed 2026-11-10. The 2026-11-10 original [independent receipt](INDEPENDENT_HOST_RECEIPT_2026-11-10.md) and the frozen preregistered hypothesis remain unchanged.

**Reason for supersession:** The original `native-fix.patch` keyed an existing regular file solely by Unix (device,inode). That closes the hard-link alias race but weakens same-path serialization if an atomic replacement changes the inode while the original guard is still held. The new bounded V2 keeps the resolved-path mutex **and**, where present, the inode mutex, acquired in a fixed order. It adds a deterministic held-path/rename regression and a release-note entry. This concern was found during prepublication review, not proven as a deployed incident; the new rename regression was not run against V1.

**Selected patch:** [native-fix-v2.patch](native-fix-v2.patch), SHA-256 `6ea4f61da5e84d2302dafbe67923c5cdee4c0dd5467e37bcac35e0f8dbb80295`; 6,573 bytes, exactly `src/tools/file.rs` and `CHANGELOG.md`. Includes production fix and both in-file regression tests; therefore no separate V2 test patch. The older `native-fix.patch` SHA-256 `a4646350abef97cb76cf4f8bc7506cfe31f961b37a5896e5e61ddb2d50d20c94` is **superseded, not publishable**.

## Actual checks on V2

- Verified target and public direct fork `main` both at the assessed `f1495e7...` source SHA (2026-11-11).
- `git apply --check` V2 patch against an independently cloned pristine source at that SHA: **PASS**.
- `git diff --check` and `cargo fmt -- --check` with Rust 1.91.1: **PASS**; formatter session `f60bc9a8-10d0-412b-9dae-5add14808b73`.
- Native `cargo test --lib file_mutex -- --nocapture`: **1/1 PASS** (hard-link alias), session `5b65f903-2367-41f3-8d85-944b708e5f0d`.
- Full V2 `cargo test --lib`: **593/593 PASS**, session `a5935bc2-c524-48e5-852a-4b36e942ada9`, container `rust:1.91`; includes the new atomic replacement regression and original cancellation control.
- `cargo test --all-features`: **NOT COMPLETED**. The transient container on the shared VM exhausted filesystem capacity while building; that run was stopped without a result. Only its own temporary Rust build outputs were removed to restore free disk. It must run on fork-native CI or another capacity-appropriate host.
- Full `cargo clippy --all-targets --all-features`, MSRV Rust 1.86, Windows, macOS, wasm and end-to-end model/provider runs: **not performed** for V2. Do not check these as completed.

The deterministic earlier source-native RED on the path-only original code and V1 GREEN remain in the 2026-11-10 receipt; they do **not** prove the new rename regression was run RED against V1. V2 has only the above green verification. There is no claim of external publication, acceptance, product improvement in deployment, or automatic VSM-grade change.

## Preparation/publication gates

The selected V2 SHA is recorded in batch 24's mutable technical-handoff fields while leaving its preregistered hypothesis and historical receipt unchanged. The standing owner preparation and distinct publication mandates, current native contributor requirements, public fork permissions, exactly matched source and patch, and fork-local PR contract still apply. Target native CI must supply the missing broader coverage before claiming readiness for external publication.
