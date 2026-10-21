# Agent-code #524 — consolidated independent reviewer and child permission contract

**Internal OpenSiro handoff · Draft PR #69 · 2026-10-21.**

**Canonical upstream source:** [`avala-ai/agent-code/main@82e0edfa7372c256d893d0854f954d9099254f88`](https://github.com/avala-ai/agent-code/commit/82e0edfa7372c256d893d0854f954d9099254f88), existing [issue #524](https://github.com/avala-ai/agent-code/issues/524). **Index lineage:** [`vsm-harness-index/main@5393b698bfdfa4ca14d97a79238234eca20694e5`](https://github.com/opensiro/vsm-harness-index/commit/5393b698bfdfa4ca14d97a79238234eca20694e5), `assessments/ag/agent-code.md`, `review_ref=2734ab5f18939b20c774b39c4406788383e35255`. The Index records no independent S3* review and issue #524 independently describes the product need.

**Source artifact:** [consolidated eight-file native patch](reviewer-subagent-first-slice.patch), SHA-256 `fc3c22f86b4a83b3fbe843b9f106f6e699f6ca556cd4d33d2733a43307056303` (55,920 bytes). The source patch was created from the exact pinned target plus the previously reviewed mandatory-child-overlay protection, combined with the later isolated review and result gate. It **applies successfully on an independent pristine checkout**; `git diff --check` PASS.

## Changes

- `/review` preserves current target resolution/rubric but produces a distinct `ReviewTask`, **not** a parent-session model prompt. Modern TUI launches a typed `review` child process via existing `AgentTool`/`TaskManager`; the builtin definition cannot be overridden by project disk profiles.
- Constrained overlay creation **fails closed** in both foreground/background parent launch paths. A child marked as requiring an overlay **refuses to run** if the argument is missing or the file cannot be read, parsed or enforced. The non-subagent interactive compatibility policy remains separate.
- Typed `ReviewOutput` JSON has bounded priority/confidence/location validation. The TUI only displays bounded, labelled, *unverified model findings* on successful parse; it never treats raw task stdout as trusted new parent instructions.
- The child `review` role now **replaces** the default system message with a dedicated reviewer system prompt, including the rubric, JSON output contract and strictly scoped documentation of read-only tools. The general coding-agent persona, response style, user memory and additional directories are not injected as reviewer system instructions. The reviewer task remains a separate user message; both the AgentTool and coordinator reviewer child paths tag their role so the child selects this system message. An explicit pure role-routing test checks replacement and main-agent isolation.
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

**Current seven-file JSONL-enabled native patch — PASS at exact pinned upstream:** The reviewer child now receives `--output-format json` (other agent types retain their existing output mode). `parse_review_jsonl` consumes the existing agent-code `JsonStreamSink` event envelope: it accepts `text_delta` from the last completed assistant turn, ignores thinking and tool-result content, requires a successful `session_end`, then validates the typed findings; malformed, incomplete, failed, unstructured, or truncated streams do **not** become accepted review artifacts. The TUI calls the event parser rather than trying to parse the entire process stdout as a single JSON object.

**Previously measured selected tests** (all five filters on the prior JSONL slice PASSED; the current full-library/full-CLI runs on the eight-file patch supersede those counts):

| Test | PASS |
| --- | ---: |
| `cargo test -p agent-code-lib review:: --lib --locked` | **19/19** |
| `cargo test -p agent-code-lib services::coordinator::coordinator_tests --lib --locked` | **37/37** |
| `cargo test -p agent-code-lib tools::agent::tests --lib --locked` | **15/15** |
| `cargo test -p agent-code --bin agent subagent_overlay_loading_tests --locked` | **2/2** |
| `cargo test -p agent-code --bin agent ui::modern::run::tests --locked` | **108/108** |
| **Total** | **181/181 PASS, zero failures** |

The JSONL regression initially failed on a malformed **test fixture**, not a production parser defect; corrected the fixture and reran the tests green. A distinct frozen-checkout worktree accepts the exact 55,920-byte patch; `git apply --check`, `git diff --check`, `cargo fmt --all -- --check`, and byte comparison of the patch against the tested implementation all **PASS**. Tested using Rust 1.97 plus an isolated Zig C/linker toolchain.

**Broader exact eight-file native results:** `cargo test -p agent-code-lib --lib --locked --quiet` **1761/1761 PASS** (10.98 seconds) and `cargo test -p agent-code --bin agent --locked --quiet` **1019/1019 PASS** (10.17 seconds), both on the current eight-file native checkout. **2780/2780 full unit tests across these two targets PASS**, in addition to the 181 narrower targeted filters (which overlap these suites and must not be added to the total). This is wider native validation than the original PR handoff, but does not include end-to-end configured provider runs, all workspace targets/platforms, clippy, or external maintainer CI.

**Scope caveat:** The JSONL handling is tested using synthetic event streams derived from the first-party `JsonStreamSink` schema; actual review output with a configured model remains to be checked. Full external upstream CI and provider-backed comparison are still absent. JSONL handling is tested using synthetic event streams derived from the existing first-party `JsonStreamSink` event schema; actual review output with a configured model remains to be checked.

## Remaining acceptance boundaries

- No real model-backed independent review, blinded same-task comparison, or measured software-quality improvement. `ASSESSMENT_DERIVED` remains a **research selection category**; candidate stays `SCREENING`.
- The child reviewer rubric is prefixed to its one-shot prompt, not installed as a replacement base system message; the child now produces JSONL and the route reconstructs last-turn text, but real model-generated JSON may still be invalid; that degrades safely to `/tasks` instead of inventing findings.
- A Plan-mode Bash classifier and tool-level permissions are not an OS-level sandbox. No hostile filesystem/subprocess/network egress test has demonstrated complete containment.
- Results are operator-visible in the TUI, but not injected as a bounded model-visible parent action that would close an automatic S3 correction loop.
- Full upstream tests, matrix/clippy, real host/provider tests and maintainer acceptance are not complete. The internal GitHub workflow validates the OpenSiro handoff, not native third-party code behavior.

**Authority:** only internal OpenSiro Draft PR #69 is written. No third-party code, contribution fork, external issue/PR, VSM grade, organization S1 admission or delegated permission changed. The human operator retains publication authority.
