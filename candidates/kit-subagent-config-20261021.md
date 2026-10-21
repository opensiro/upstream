---
candidate_id: IMPR-KIT-SUBAGENT-CONFIG-20261021
state: SCREENING
origin_class: ASSESSMENT_INFORMED
target_repo: speakeasy-api/kit
index_sha: 5393b698bfdfa4ca14d97a79238234eca20694e5
assessment_path: assessments/ki/kit.md
review_ref: 3fd1fd5fda269569ceba0c2dd884c988d31f53d0
source_sha: 8f9f08a2b2088381f1cb106dcb9129378f8f0b4e
fit_need: PASS
fit_mechanism: PASS
fit_value: PASS
fit_scope: PENDING
---

# IMPR-KIT-SUBAGENT-CONFIG-20261021 — native Kit startup recovery

**State:** `SCREENING / ASSESSMENT_INFORMED`, **not** `ASSESSMENT_DERIVED`, `QUALIFIED`, `SELECTED`, `UPSTREAM_MERGED` or Organization S1-admitted.

## Index and first-party source

The [Kit assessment pinned at Index 5393b698](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ki/kit.md) records Kit's supported optional subagent/ACP mechanisms at review ref `3fd1fd5f...`. It **does not identify the specific defect**. The actual user-facing need came from first-party [Kit issue #222](https://github.com/speakeasy-api/kit/issues/222), which remains **open** at this checkpoint.

Pinned target: [Kit `main@8f9f08a2`](https://github.com/speakeasy-api/kit/tree/8f9f08a2b2088381f1cb106dcb9129378f8f0b4e). In `src/main.rs`, `SubagentConfig.harness: String` makes nested `subagent.harnesses.*` fields without a parent `subagent.harness` fail `Config::load` with `InvalidData`. An optional child config can therefore prevent ordinary Kit command startup.

## Four native fit gates — evidence-specific

| Gate | Verdict | What was actually established |
| --- | --- | --- |
| Need | `PASS` | Native user report [#222](https://github.com/speakeasy-api/kit/issues/222), exact current source path and true baseline failure |
| Mechanism | `PASS` | Distinct regression-only and minimal product patches, reproducible clean application; proposed missing-field warning + built-in default + incomplete child-policy exclusion |
| Counterfactual local benefit | `PASS` **bounded** | Real original `kit sessions` binary **failed** with issue fixture; patched binary **succeeded** with actionable warning and unchanged config file; same immutable source, isolated HOME, no model/API |
| Scope / acceptability | `PENDING` | Upstream maintainer has **not** approved fallback/disable semantics; default-feature Linux compatibility PASS, but native macOS check, external PR and maintainer feedback remain open |

## Reproducible actual before/after result

[OpenSiro internal PR #70](https://github.com/opensiro/upstream/pull/70) is a **review-ready internal source-level proposal**, not the Kit upstream PR.

- [First red/green #39656287282](https://github.com/opensiro/upstream/actions/runs/39656287282) — `Config::load` test RED on original missing `harness` field, GREEN after source-only patch; invalid policy types still rejected; existing config tests and format PASS.
- [Complete headless native suite #39657240286](https://github.com/opensiro/upstream/actions/runs/39657240286) — all headless Rust tests and strict headless all-targets Clippy PASS (main library 1,329 passed, five ignored; other CLI/integration suites PASS).
- [Actual CLI #39658753131](https://github.com/opensiro/upstream/actions/runs/39658753131) and [final unchanged-source replay #39660969648](https://github.com/opensiro/upstream/actions/runs/39660969648) — original real headless `kit sessions` failed on exact synthetic issue TOML; patched real CLI succeeded with specific warning; original user config bytes preserved. Full headless suite, strict lint and format PASS.
- Unified upstream-style [native patch](https://github.com/opensiro/upstream/blob/pilot/kit-222-partial-subagent-config-20261021/pilots/kit-222/kit-222-upstream-combined.patch) SHA-256 `cc997c7ee350db49c4a4f03789da25a3a4a8760281fefcc178e3a71c6b972389`, verified on pinned pristine source with `git apply --check` and `git diff --check`. [Reproduction detail](https://github.com/opensiro/upstream/blob/pilot/kit-222-partial-subagent-config-20261021/pilots/kit-222/README.md) and [human-owned external PR packet](https://github.com/opensiro/upstream/blob/pilot/kit-222-partial-subagent-config-20261021/pilots/kit-222/UPSTREAM_PR_HANDOFF.md).

**Important bounds:** a measured deterministic **local CLI startup/recovery** effect is not a model-backed `kit acp` run, production review-quality/uptime metric, OS isolation proof, release, upstream merge or VSM-grade uplift. The proposed built-in default when the explicit field is absent is a **maintainer decision to accept or change**, not implicitly approved by tests. It must not select third-party harnesses or silently suppress malformed mandatory options.

## Next gate and ownership

[Normal Linux/default-feature compatibility run #39671040353](https://github.com/opensiro/upstream/actions/runs/39671040353) completed **SUCCESS**: `cargo clippy --all-features --all-targets -- -D warnings` and `cargo test --locked`, including **1,949 core library passed, zero failed, ten ignored**, plus native CLI/integration tests and Rustfmt. This is not just a `--no-default-features` smoke. [Headless source and before/after CLI run #39671039770](https://github.com/opensiro/upstream/actions/runs/39671039770) and [fork lifecycle run #39671039773](https://github.com/opensiro/upstream/actions/runs/39671039773) also completed **SUCCESS** at the exact reviewed PR source head. No original Rust patch changes.

The actual Kit issue was reported on macOS. Dedicated native [macOS config tests and local `kit sessions` CLI CI #39674571202](https://github.com/opensiro/upstream/actions/runs/39674571202) is running; **do not claim macOS PASS until complete**. This is not the original macOS Xcode/desktop CI.

For design contrast, existing original Kit `Command::Config::Set` invokes `kit::config_editor::set` directly without `Config::load_default`, so `kit config set subagent.harness acp.claude` offers a **manual repair route** even with malformed optional `[subagent]` config. The measured patch benefit is specifically **no manual repair before ordinary session startup**. Upstream maintainers must decide whether built-in default selection or complete disabling of incomplete subagent delegation is preferable. The product fit scope remains `PENDING` for that reason. Actual external PR, final maintainer review, original macOS Xcode/desktop matrix and downstream release are still absent.

No external fork, original Kit branch/PR, Index grade change, Organization authority or product release has been written. External PR remains human-owned and governed by separate stage-specific permission. Preserve this as an **ASSESSMENT_INFORMED** engineering case, not as the strict Index→functional-gap success sought by [OpenSiro experiment #56](https://github.com/opensiro/upstream/issues/56).
