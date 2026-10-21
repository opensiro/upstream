# Agent-code #524 — consolidated independent reviewer and child permission contract

**Internal OpenSiro handoff · Draft PR #69 · 2026-10-21.**

**Canonical upstream source:** [`avala-ai/agent-code/main@82e0edfa7372c256d893d0854f954d9099254f88`](https://github.com/avala-ai/agent-code/commit/82e0edfa7372c256d893d0854f954d9099254f88), existing [issue #524](https://github.com/avala-ai/agent-code/issues/524). **Index lineage:** [`vsm-harness-index/main@5393b698bfdfa4ca14d97a79238234eca20694e5`](https://github.com/opensiro/vsm-harness-index/commit/5393b698bfdfa4ca14d97a79238234eca20694e5), `assessments/ag/agent-code.md`, `review_ref=2734ab5f18939b20c774b39c4406788383e35255`. The Index records no independent S3* review and issue #524 independently describes the product need.

**Source artifact:** [consolidated eight-file native patch](reviewer-subagent-first-slice.patch), SHA-256 `58a70a40beafcceef1f76161f869f4fe2366272d8a82ea9fe9b48fcf530235e1` (57,663 bytes). The source patch was created from the exact pinned target plus the previously reviewed mandatory-child-overlay protection, combined with the later isolated review and result gate. It **applies successfully on an independent pristine checkout**; `git diff --check` PASS.

## Changes

- `/review` preserves current target resolution/rubric but produces a distinct `ReviewTask`, **not** a parent-session model prompt. Modern TUI launches a typed `review` child process via existing `AgentTool`/`TaskManager`; the builtin definition cannot be overridden by project disk profiles.
- Constrained overlay creation **fails closed** in both foreground/background parent launch paths. A child marked as requiring an overlay **refuses to run** if the argument is missing or the file cannot be read, parsed or enforced. The non-subagent interactive compatibility policy remains separate.
- Typed `ReviewOutput` JSON has bounded priority/confidence/location validation. The TUI only displays bounded, labelled, *unverified model findings* on successful parse; it never treats raw task stdout as trusted new parent instructions.
- The child `review` role now **replaces** the default system message with a dedicated reviewer system prompt, including the rubric, JSON output contract and strictly scoped documentation of read-only tools. The general coding-agent persona, response style, user memory and additional directories are not injected as reviewer system instructions. The reviewer task remains a separate user message; both the AgentTool and coordinator reviewer child paths tag their role so the child selects this system message. An explicit pure role-routing test checks replacement and main-agent isolation.
- Completion propagation is gated to task IDs started by this TUI and their initial conversation epoch. Late output after a resume or session switch is discarded; malformed/oversized/non-JSON raw output remains available through `/tasks`.
- **Reviewer memory isolation:** the child-side CLI avoids main-agent background memory consolidation for `AgentKind::Subagent`, even when the extract-memories setting is enabled. This prevents an unrelated memory-maintenance model call and reuse of ambient user memory during the fresh-context reviewer task. Main-agent consolidation remains enabled when configured. Three new unit cases cover main-enabled, subagent-enabled and main-disabled behavior.

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

**Current eight-file JSONL-enabled native patch — PASS at exact pinned upstream:** The reviewer child now receives `--output-format json` (other agent types retain their existing output mode). `parse_review_jsonl` consumes the existing agent-code `JsonStreamSink` event envelope: it accepts `text_delta` from the last completed assistant turn, ignores thinking and tool-result content, requires a successful `session_end`, then validates the typed findings; malformed, incomplete, failed, unstructured, or truncated streams do **not** become accepted review artifacts. The TUI calls the event parser rather than trying to parse the entire process stdout as a single JSON object.

**Previously measured selected tests** (all five filters on the prior JSONL slice PASSED; the current full-library/full-CLI runs on the eight-file patch supersede those counts):

| Test | PASS |
| --- | ---: |
| `cargo test -p agent-code-lib review:: --lib --locked` | **19/19** |
| `cargo test -p agent-code-lib services::coordinator::coordinator_tests --lib --locked` | **37/37** |
| `cargo test -p agent-code-lib tools::agent::tests --lib --locked` | **15/15** |
| `cargo test -p agent-code --bin agent subagent_overlay_loading_tests --locked` | **2/2** |
| `cargo test -p agent-code --bin agent ui::modern::run::tests --locked` | **108/108** |
| **Total** | **181/181 PASS, zero failures** |

The JSONL regression initially failed on a malformed **test fixture**, not a production parser defect; corrected the fixture and reran the tests green. A distinct frozen-checkout worktree accepts the earlier 55,920-byte JSONL patch; `git apply --check`, `git diff --check`, `cargo fmt --all -- --check`, and byte comparison of the patch against the tested implementation all **PASS**. Tested using Rust 1.97 plus an isolated Zig C/linker toolchain.

**Current exact eight-file reviewer/memory-isolation patch (the artifact linked above):** `cargo test -p agent-code-lib --lib --locked --quiet` **1761/1761 PASS** (8.70 seconds) and `cargo test -p agent-code --bin agent --locked --quiet` **1022/1022 PASS** (4.74 seconds), including **3/3 new memory-role regression tests**. Thus **2783/2783 complete unit tests** across the two principal targets PASS. These counts supersede, and overlap, the older 181 focused tests; never sum them as independent coverage. `cargo fmt --all -- --check`, `git diff --check`, exact local-patch byte comparison and frozen-source patch replay **PASS**. The patch SHA256 was reverified immediately before publication.

**Measured change (deterministic policy, not a provider-backed outcome):** prior source passed the general `features.extract_memories` condition to the child lifecycle; after patch the same Boolean gate requires `AgentKind::Main`. Subagents therefore cannot trigger that specific memory consolidation path when configured, and the main agent's behavior is preserved. The test is an isolated role-policy assertion; neither a live memory leak nor an LLM review-quality improvement has been demonstrated.

**Scope caveat:** JSONL handling is still tested on synthetic event streams derived from first-party `JsonStreamSink`. Actual review output with a configured model remains to be checked. Full upstream CI, clippy and provider-backed comparison remain absent. The active Index `main` may advance; this experiment intentionally retains the frozen assessment pin for provenance and does not regrade it.

## Remaining acceptance boundaries

- No real model-backed independent review, blinded same-task comparison, or measured software-quality improvement. `ASSESSMENT_DERIVED` remains a **research selection category**; candidate stays `SCREENING`.
- Reviewer instructions now replace the general coding-agent base system message; the user turn contains only the task. The child produces JSONL and the route reconstructs the last completed turn, but real model-generated JSON may still be invalid; that degrades safely to `/tasks` rather than inventing findings.
- A Plan-mode Bash classifier and tool-level permissions are not an OS-level sandbox. No hostile filesystem/subprocess/network egress test has demonstrated complete containment.
- Results are operator-visible in the TUI, but not injected as a bounded model-visible parent action that would close an automatic S3 correction loop.
- Full **two-target unit tests are complete**, but full-workspace/cross-platform matrix, clippy, real host/provider tests and maintainer acceptance remain incomplete. The internal GitHub workflow validates the OpenSiro handoff, not third-party upstream acceptance.

**Authority:** only internal OpenSiro Draft PR #69 is written. No third-party code, contribution fork, external issue/PR, VSM grade, organization S1 admission or delegated permission changed. The human operator retains publication authority.
