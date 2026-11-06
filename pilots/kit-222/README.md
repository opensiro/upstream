# Kit #222 — partial subagent configuration should not lock out the agent

**Owning native problem:** [speakeasy-api/kit #222](https://github.com/speakeasy-api/kit/issues/222). Public `main@8f9f08a2b2088381f1cb106dcb9129378f8f0b4e` (2026-10-21), exact source and direct `Config::load` path inspected. **Internal OpenSiro PR #70 is open and ready for review; no source changes, working fork or PR in original Kit.**

## Selected target and source

The existing `SubagentConfig { harness: String, harnesses: ... }` requires the `harness` TOML field. A nested `[subagent.harnesses."acp.claude".models]` without it causes `Config::load` to return `InvalidData`, even when the main Kit session does not use a subagent. This is directly consistent with the user's first-party issue reproduction.

Origin is **ASSESSMENT_INFORMED**: [canonical Kit assessment](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ki/kit.md) documents first-party Kit operating boundaries but **did not diagnose this startup defect**. Treat this as issue-driven native engineering, not an Index S2 finding or grade repair.

## Offline hypothesis and distinct patch artifacts

- [Regression-only native patch](kit-222-regression-only.patch) contains source-local Rust tests and **no product logic**; checks the issue's exact TOML form, control default selection, preserved config bytes and invalid nested model-policy types.
- [Separate minimal source patch](kit-222-safe-default.patch) makes `SubagentConfig.harness` optional at deserialize time and **only when missing**, logs a field-specific warning (without secrets), uses the existing built-in default harness rather than selecting any external ACP backend, and does not apply the incomplete per-harness model overrides. Normal explicitly selected subagents and invalid nested policy types retain their existing validation.
- [Actual source-pinned Linux Actions](../../.github/workflows/kit-222-offline.yml) replays both stages against the **same cloned upstream SHA** using `cargo test --no-default-features --bin kit --locked`. It requires baseline fail **for the exact new test's missing-harness runtime assertion**, not a compiler/download failure, before it applies the production patch and requires native post-change tests to pass. Old config/harness tests and upstream formatting are additional gates.

**Second source-pinned native matrix:** [Actions run #39657240286](https://github.com/opensiro/upstream/actions/runs/39657240286) **SUCCESS** for the real regression RED → GREEN, the original config-control tests, complete `cargo test --no-default-features --locked` test suite, strict `cargo clippy --no-default-features --all-targets --locked -- -D warnings`, and Rust formatting. Main library summary: **1,329 PASS, five ignored**, plus separate CLI/integration tests PASS. This is the actual headless upstream crate test matrix (original Kit main also had a passing first-party CI); it is not a default-feature/all-features or macOS matrix.

**Actual native Kit CLI before/after:** [source-pinned Actions #39658753131](https://github.com/opensiro/upstream/actions/runs/39658753131) **SUCCESS** on the same original source and immutable source patch: the **original compiled `kit sessions --root <temp>` executable** returned nonzero with `missing field `harness``, while the **patched compiled executable** completed successfully, printed the actionable `missing `subagent.harness`` warning on stderr, and left the original synthetic TOML bytes unchanged. The HOME/session root were isolated in `RUNNER_TEMP`, with no actual model API or third-party service. The run independently reconfirmed the focused regression RED/GREEN, the complete `cargo test --no-default-features --locked` suite, strict all-targets headless Clippy and formatting. This is a real Kit CLI startup benefit for one local command, **not** real ACP inference or external release evidence.

**Complete single-patch source handoff:** [`kit-222-upstream-combined.patch`](kit-222-upstream-combined.patch), **SHA256 `cc997c7ee350db49c4a4f03789da25a3a4a8760281fefcc178e3a71c6b972389`**, combines the same regression and production hunks of the two independently tested patch files into one standard `git diff`. An authenticated read-only host replay checked the SHA256 and `git apply --check`/`git apply`/`git diff --check` from a new pristine `src/main.rs` at the pinned Kit commit and checked exact bytes against the local generated diff. The GitHub artifact is self-contained, **not** code submitted to Kit.

**First-party design boundary:** this fallback is **a proposal**, not a maintainer-approved policy. It must not bypass malformed essential config, auto-select arbitrary third-party harnesses, or disable existing credential/permission checks. A real maintained solution may choose a different warning/disable contract. No paid LLM API or model inference is required.

## Status and acceptance

- Index origin: `ASSESSMENT_INFORMED / SCREENING`.
- **Actual native baseline: VERIFIED RED** — [first source-pinned run #39656287282](https://github.com/opensiro/upstream/actions/runs/39656287282) reproduced the **specific runtime failure** `missing field `harness`` under `subagent`, not a compile failure.
- **After: VERIFIED GREEN on focused source tests** — the two new tests PASS, three existing explicit policy/config tests PASS, `cargo fmt --all -- --check` PASS in the **same** run, without a provider, model or external Kit network calls. The warning for the incomplete optional configuration was actually printed in the test log.
- **Patch evidence:** regression-only SHA256 `34463579de4609cab159b6e2d90d4a737bd5a2c96147a6cec0354d5798a61901`; source-fix SHA256 `951952eef85d5d6e78c763fcbc30a28d620246af3a8991175780a1f89c814659`. Both independently replayed via `git apply` against pinned source on a read-only VM.
- **Verified engineering acceptance:** full headless native suite, strict headless all-targets Clippy, formatting and actual CLI startup before/after **PASS** ([final pinned CI #39660969648](https://github.com/opensiro/upstream/actions/runs/39660969648)). Separate [original-feature compatibility workflow](https://github.com/opensiro/upstream/blob/pilot/kit-222-partial-subagent-config-20261021/.github/workflows/kit-222-compat.yml) checks default-feature Rust tests and strict all-features Clippy; do not claim these PASS until completed.
- Native fit: first-party demand `PASS`; mechanism/scope/counterfactual `PENDING` pending native results and maintainer preference.
- External fork / Kit PR / product release: `NONE`.
- No changes to Index, Organization control, permissions or authority.

The runner checks a **headless** Kit binary, not the whole original `mise` CI, macOS TUI or model-backed ACP scenario. A CI green check is necessary engineering evidence but not a claim of externally shipped improvement.
