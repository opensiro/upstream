# Kit #222 — external upstream PR packet (human-owned, not yet published)

**Native source:** [speakeasy-api/kit #222](https://github.com/speakeasy-api/kit/issues/222), `main@8f9f08a2b2088381f1cb106dcb9129378f8f0b4e`. Internal [OpenSiro PR #70](https://github.com/opensiro/upstream/pull/70) is open and ready for internal review; a reviewable engineering handoff, **not an external fork or PR**.

**Applyable native patch:** [kit-222-upstream-combined.patch](kit-222-upstream-combined.patch), SHA256 `cc997c7ee350db49c4a4f03789da25a3a4a8760281fefcc178e3a71c6b972389`. One upstream file `src/main.rs`: minimal production fix plus two colocated Rust regression tests. Independently generated from the verified separate test-only and source-only patches against the unchanged Kit commit, and applied cleanly in a fresh file checkout.

## Suggested PR title

`fix(config): recover from partial subagent harness settings`

## Suggested PR body

### Summary

Fixes #222. A partial optional `[subagent]` config with nested `subagent.harnesses.*` but no `subagent.harness` previously prevented even ordinary Kit commands from starting. Allow the incomplete optional config to deserialize, explicitly warn about the missing field, select only Kit's normal built-in harness by default, and ignore incomplete subagent-specific model policies. The user-owned TOML remains untouched. Explicit harness selection, unknown `subagent.names` rejection, and invalid nested policy types remain checked.

### Test plan

- [x] Source-pinned **real native regression RED before code change**: `Config::load` on exact issue fixture fails at `missing field `harness``.
- [x] **After code change**: two new tests pass; three existing subagent/config policy tests pass. [First native run #39656287282](https://github.com/opensiro/upstream/actions/runs/39656287282).
- [x] Complete `cargo test --no-default-features --locked` **PASS**, including 1,329 lib tests passing, five deliberately ignored, plus other native CLI/integration suites.
- [x] Strict `cargo clippy --no-default-features --all-targets --locked -- -D warnings` and `cargo fmt --all -- --check` **PASS** ([full receipt #39657240286](https://github.com/opensiro/upstream/actions/runs/39657240286)).
- [x] **Real CLI before/after** in temporary HOME, invoking headless `kit sessions`: original binary **blocked**, patched binary **succeeds with warning** and preserves config bytes, [run #39658753131](https://github.com/opensiro/upstream/actions/runs/39658753131). No model inference/API.
- [ ] First-party default-feature/all-features compatibility under [separate OpenSiro CI](https://github.com/opensiro/upstream/blob/pilot/kit-222-partial-subagent-config-20261021/.github/workflows/kit-222-compat.yml) — check its run before ticking this box. Kit's own `mise run lint`/CI, macOS matrix and external PR checks still require upstream submission or maintainer confirmation.
- [ ] Maintainer approval of chosen fallback/disable semantics; this is a proposed recovery policy, not an upstream agreement.

### Non-goals / safety

No silent ACP third-party selection, config rewrite, permission bypass, disabling of other malformed-config checks, model quality claim, production availability result, or VSM grade change. Source-driven `ASSESSMENT_INFORMED`, not a diagnosis directly established by Index.

## Exact reproduction for the authorized contributor

```sh
git clone https://github.com/speakeasy-api/kit.git
cd kit
git checkout 8f9f08a2b2088381f1cb106dcb9129378f8f0b4e
sha256sum /path/to/kit-222-upstream-combined.patch
git apply --check /path/to/kit-222-upstream-combined.patch
git apply /path/to/kit-222-upstream-combined.patch
git diff --check
cargo test --no-default-features --locked
cargo clippy --no-default-features --all-targets --locked -- -D warnings
cargo fmt --all -- --check
```

The actual external feature branch must be created in a **separately authorized contributor fork**, not on Kit's protected `main`. Refresh the current upstream SHA/deduplication and rerun CI when doing so. **Only the human operator decides and performs the external PR publication**, after internal review and any applicable write-stage grant. No model API required for this implementation's offline checks.
