# Kit #222 — partial subagent configuration should not lock out the agent

**Owning native problem:** [speakeasy-api/kit #222](https://github.com/speakeasy-api/kit/issues/222). Public `main@8f9f08a2b2088381f1cb106dcb9129378f8f0b4e` (2026-10-21), exact source and direct `Config::load` path inspected. **Only the internal OpenSiro pilot is written; no source changes, working fork or PR in Kit.**

## Selected target and source

The existing `SubagentConfig { harness: String, harnesses: ... }` requires the `harness` TOML field. A nested `[subagent.harnesses."acp.claude".models]` without it causes `Config::load` to return `InvalidData`, even when the main Kit session does not use a subagent. This is directly consistent with the user's first-party issue reproduction.

Origin is **ASSESSMENT_INFORMED**: [canonical Kit assessment](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ki/kit.md) documents first-party Kit operating boundaries but **did not diagnose this startup defect**. Treat this as issue-driven native engineering, not an Index S2 finding or grade repair.

## Offline hypothesis and distinct patch artifacts

- [Regression-only native patch](kit-222-regression-only.patch) contains source-local Rust tests and **no product logic**; checks the issue's exact TOML form, control default selection, preserved config bytes and invalid nested model-policy types.
- [Separate minimal source patch](kit-222-safe-default.patch) makes `SubagentConfig.harness` optional at deserialize time and **only when missing**, logs a field-specific warning (without secrets), uses the existing built-in default harness rather than selecting any external ACP backend, and does not apply the incomplete per-harness model overrides. Normal explicitly selected subagents and invalid nested policy types retain their existing validation.
- [Actual source-pinned Linux Actions](../../.github/workflows/kit-222-offline.yml) replays both stages against the **same cloned upstream SHA** using `cargo test --no-default-features --bin kit --locked`. It requires baseline fail **for the exact new test's missing-harness runtime assertion**, not a compiler/download failure, before it applies the production patch and requires native post-change tests to pass. Old config/harness tests and upstream formatting are additional gates.

**First-party design boundary:** this fallback is **a proposal**, not a maintainer-approved policy. It must not bypass malformed essential config, auto-select arbitrary third-party harnesses, or disable existing credential/permission checks. A real maintained solution may choose a different warning/disable contract. No paid LLM API or model inference is required.

## Status and acceptance

- Index origin: `ASSESSMENT_INFORMED / SCREENING`.
- **Actual native baseline: VERIFIED RED** — [first source-pinned run #39656287282](https://github.com/opensiro/upstream/actions/runs/39656287282) reproduced the **specific runtime failure** `missing field \`harness\`` under `subagent`, not a compile failure.
- **After: VERIFIED GREEN on focused source tests** — the two new tests PASS, three existing explicit policy/config tests PASS, `cargo fmt --all -- --check` PASS in the **same** run, without a provider, model or external Kit network calls. The warning for the incomplete optional configuration was actually printed in the test log.
- **Patch evidence:** regression-only SHA256 `34463579de4609cab159b6e2d90d4a737bd5a2c96147a6cec0354d5798a61901`; source-fix SHA256 `951952eef85d5d6e78c763fcbc30a28d620246af3a8991175780a1f89c814659`. Both independently replayed via `git apply` against pinned source on a read-only VM.
- **Next added engineering gate:** broad `cargo test --no-default-features --locked` plus strict all-targets headless Clippy; `NOT_VERIFIED` until the follow-up CI finishes. Source change and both patch digests remain frozen.
- Native fit: first-party demand `PASS`; mechanism/scope/counterfactual `PENDING` pending native results and maintainer preference.
- External fork / Kit PR / product release: `NONE`.
- No changes to Index, Organization control, permissions or authority.

The runner checks a **headless** Kit binary, not the whole original `mise` CI, macOS TUI or model-backed ACP scenario. A CI green check is necessary engineering evidence but not a claim of externally shipped improvement.
