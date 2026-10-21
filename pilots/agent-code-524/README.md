# Agent-code #524 — consolidated independent reviewer and child permission contract

**Internal OpenSiro handoff · Draft PR #69 · 2026-10-21.**

**Canonical upstream source:** [`avala-ai/agent-code/main@82e0edfa7372c256d893d0854f954d9099254f88`](https://github.com/avala-ai/agent-code/commit/82e0edfa7372c256d893d0854f954d9099254f88), existing [issue #524](https://github.com/avala-ai/agent-code/issues/524). **Index lineage:** [`vsm-harness-index/main@5393b698bfdfa4ca14d97a79238234eca20694e5`](https://github.com/opensiro/vsm-harness-index/commit/5393b698bfdfa4ca14d97a79238234eca20694e5), `assessments/ag/agent-code.md`, `review_ref=2734ab5f18939b20c774b39c4406788383e35255`. The Index records no independent S3* review and issue #524 independently describes the product need.

**Source artifact:** [consolidated seven-file native patch](reviewer-subagent-first-slice.patch), SHA-256 `be775b2e2830e0f4991e91013f7c0dd629e0da6e1ae870edb11b41950bff278c` (46,972 bytes). The source patch was created from the exact pinned target plus the previously reviewed mandatory-child-overlay protection, combined with the later isolated review and result gate. It **applies successfully on an independent pristine checkout**; `git diff --check` PASS.

## Changes

- `/review` preserves current target resolution/rubric but produces a distinct `ReviewTask`, **not** a parent-session model prompt. Modern TUI launches a typed `review` child process via existing `AgentTool`/`TaskManager`; the builtin definition cannot be overridden by project disk profiles.
- Constrained overlay creation **fails closed** in both foreground/background parent launch paths. A child marked as requiring an overlay **refuses to run** if the argument is missing or the file cannot be read, parsed or enforced. The non-subagent interactive compatibility policy remains separate.
- Typed `ReviewOutput` JSON has bounded priority/confidence/location validation. The TUI only displays bounded, labelled, *unverified model findings* on successful parse; it never treats raw task stdout as trusted new parent instructions.
- Completion propagation is gated to task IDs started by this TUI and their initial conversation epoch. Late output after a resume or session switch is discarded; malformed/oversized/non-JSON raw output remains available through `/tasks`.

## Reproducibility

```bash
git clone https://github.com/avala-ai/agent-code.git
cd agent-code
git checkout 82e0edfa7372c256d893d0854f954d9099254f88
git apply --check /path/to/reviewer-subagent-first-slice.patch
git apply /path/to/reviewer-subagent-first-slice.patch
cargo fmt --all -- --check
cargo test -p agent-code-lib review:: --lib --locked
cargo test -p agent-code-lib services::coordinator::coordinator_tests --lib --locked
cargo test -p agent-code-lib tools::agent::tests --lib --locked
cargo test -p agent-code --bin agent subagent_overlay_loading_tests --locked
cargo test -p agent-code --bin agent ui::modern::run::tests --locked
```

The VM required Rust 1.97 with an isolated Zig C/linker/archiver because system `cc/ar` were absent.

**Prior source-slice tests (not a combined-patch certification):** 17/17 review, 37/37 coordinator, 15/15 AgentTool, 108/108 modern TUI and 2/2 child-overlay parser. A previous live CLI smoke on five invalid required-overlay cases rejected all five before any model request.

**Combined seven-file test results — PASS on the actual reconciled source worktree:** `review::` **17/17**, `services::coordinator::coordinator_tests` **37/37**, `tools::agent::tests` **15/15**, `subagent_overlay_loading_tests` **2/2**, `ui::modern::run::tests` **108/108**. **Total 179/179 selected native tests PASS, zero failures** (five sequential Cargo test filters, final runner exit code 0). Clean patch replay on independent source checkout, `cargo fmt --all` and `git diff --check` also PASS. The exact published patch is byte-identical to the file exported from the tested merged source.

## Remaining acceptance boundaries

- No real model-backed independent review, blinded same-task comparison, or measured software-quality improvement. `ASSESSMENT_DERIVED` remains a **research selection category**; candidate stays `SCREENING`.
- The child reviewer rubric is prefixed to its one-shot prompt, not installed as a replacement base system message; actual model-generated stdout may not be a lone JSON object, so structured results can fail closed to `/tasks` rather than appear as validated findings.
- A Plan-mode Bash classifier and tool-level permissions are not an OS-level sandbox. No hostile filesystem/subprocess/network egress test has demonstrated complete containment.
- Results are operator-visible in the TUI, but not injected as a bounded model-visible parent action that would close an automatic S3 correction loop.
- Full upstream tests, matrix/clippy, real host/provider tests and maintainer acceptance are not complete. The internal GitHub workflow validates the OpenSiro handoff, not native third-party code behavior.

**Authority:** only internal OpenSiro Draft PR #69 is written. No third-party code, contribution fork, external issue/PR, VSM grade, organization S1 admission or delegated permission changed. The human operator retains publication authority.
