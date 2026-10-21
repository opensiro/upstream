# Agent-code #524 — independent reviewer task, structured result gate, fail-closed overlay

**Status (2026-10-21):** `NATIVE_PATCH_PREPARED / 177_SELECTED_TESTS_PASS / EXTERNAL_NOT_SUBMITTED`. This is an internal OpenSiro engineering handoff **against the third-party product's source**, not a completed upstream contribution or an accepted change in VSM grade.

## Sources and origin

- Target: [`avala-ai/agent-code` issue #524](https://github.com/avala-ai/agent-code/issues/524). Original and currently inspected upstream `main@82e0edfa7372c256d893d0854f954d9099254f88`.
- [Current canonical Index](https://github.com/opensiro/vsm-harness-index/commit/5393b698bfdfa4ca14d97a79238234eca20694e5), [assessment](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ag/agent-code.md) `review_ref=2734ab5f18939b20c774b39c4406788383e35255`: no independent, source-inspecting S3* review/corrective loop at that frozen boundary.
- [Improvement Candidate](https://github.com/opensiro/upstream/blob/design/improvement-candidates-intake-20261020/candidates/agent-code-isolated-reviewer-20261021.md): `ASSESSMENT_DERIVED` at hypothesis selection, `SCREENING` with benefit/operational-scope gates still pending.
- [Six-file native source patch](reviewer-subagent-first-slice.patch): SHA256 **`50c7b579987af896e2f946e489860a62a6f46237c25dc7c498f5a826213479b5`** (39,404 bytes). Source-pinned against the exact target commit, applying cleanly on a separate pristine worktree.

## Native code change

1. A builtin `review` AgentRegistry profile reuses the upstream `review::RUBRIC`, with fresh-process invocation, `Plan` mode, 20-turn cap, only repo-read/Bash tools and excluded editing, network-search and delegation tools. Interactive `/review` now resolves its existing target into **`CommandResult::ReviewTask` rather than a parent `Prompt`**; modern TUI launches the child with existing `TaskManager` / `AgentTool`, without serializing the parent's conversation history. Its output can be inspected with `/tasks`.
2. Shared permissions overlay creation changed from warning-and-inherited-permission fallback to **fail-closed `Result`**. If a constrained overlay cannot be written, foreground/background AgentTool and coordinator direct/team calls abort launch. Unconstrained profiles do not need a new overlay. An injected failing writer verifies the negative path.
3. A strict, typed review JSON contract contains findings, verdict, confidence, priority and code line ranges. `parse_review_output` rejects freeform responses and malformed records. The reviewer prompt requests only the JSON schema.
4. TUI remembers review task IDs started in the current conversation **with an epoch fence**. It polls for their completion, asynchronously reads no more than 128 KiB of output and displays a bounded, explicitly **unverified model finding** summary only for valid JSON. On invalid/truncated/non-JSON output it displays an explanation and directs the user to `/tasks` rather than injecting raw model chatter as parent instructions. Results belonging to an old resumed conversation are ignored.

## What was actually tested

The following tests ran on the same third-party source with the current exact patch applied:

| Test scope | Result |
| --- | --- |
| `cargo test -p agent-code-lib review:: --lib --locked` | **17/17 PASS** including 3 new strict JSON parser cases |
| `cargo test -p agent-code-lib services::coordinator::coordinator_tests --lib --locked` | **37/37 PASS**, including injected overlay write-error and builtin reviewer policy |
| `cargo test -p agent-code-lib tools::agent::tests --lib --locked` | **15/15 PASS**, including separate process, bounded permissions and command construction |
| `cargo test -p agent-code --bin agent ui::modern::run::tests --locked` | **108/108 PASS**, including no-parent-turn and bounded labelled results |
| **Total selected native tests** | **177/177 PASS** |

Verified `git diff --check`, `git apply --check` and successful application on a separate clean worktree at `82e0edfa`. Validation host uses Rust 1.97 with a locally bootstrapped Zig C/linker/archive wrapper because no stock compiler existed there. Unrelated baseline `crates/cli/src/main.rs` formatting was reverted and is **not** included in this patch.

### Replay

```bash
git clone https://github.com/avala-ai/agent-code.git
cd agent-code
git checkout 82e0edfa7372c256d893d0854f954d9099254f88
git apply --check /path/to/reviewer-subagent-first-slice.patch
git apply /path/to/reviewer-subagent-first-slice.patch
cargo test -p agent-code-lib review:: --lib --locked
cargo test -p agent-code-lib services::coordinator::coordinator_tests --lib --locked
cargo test -p agent-code-lib tools::agent::tests --lib --locked
cargo test -p agent-code --bin agent ui::modern::run::tests --locked
```

## Explicit limitations / next gates

- **No provider-backed independent review was executed.** The route, child command and output parsing were unit-tested. Output of actual interactive child runs may include CLI/progress text rather than a single raw JSON object; this correctly produces a non-structured fallback, **not** proof of end-to-end review JSON delivery. Verify against a real local/mock model before promising structured findings availability.
- The child instructions are currently prefixed to its task prompt rather than installed as a replacement system message; this does not yet satisfy issue #524's exact **base-instructions replacement** requirement. User/project disk agent definitions can still override builtins elsewhere; interactive `/review` intentionally fetches the builtin directly.
- `Plan` mode Bash classifier and tool allowlists are **not an OS-level read-only/network sandbox**. Overlay creation failure is tested fail-closed, but hostile shell redirection, subprocess/OS writes and network egress are **not yet independently proven blocked**.
- Completion results are labelled in the operator's **TUI transcript**, not injected into the parent's model messages as a bounded `user_action`; no automatic corrective S3 loop. No CLI `agent review --json`, API `POST /review`, or full CLI/classic-session parity was claimed.
- Full upstream test matrix, cross-OS CI, clippy, benchmark and maintainer review remain **not run**. The current internal GitHub workflow checks OpenSiro fork lifecycle, **not** native Rust source correctness.

This partial operational improvement is reviewable; it is **not** sufficient to promote to `QUALIFIED` or declare the upstream system's S3* grade changed. No contributor fork or external `avala-ai/agent-code` branch, issue comment, PR or code file was created or modified. External submission is reserved for the human operator.
