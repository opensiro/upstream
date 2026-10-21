# agent-code #524 — constrained fresh-context reviewer subagent, first native slice

**Research / implementation status:** `NATIVE_PATCH_PREPARED / SELECTED_NATIVE_RUST_TESTS_PASS / NOT_UPSTREAM_SUBMITTED` (2026-10-21). This is an internal, reviewable OpenSiro patch handoff, **not** a completed implementation of [avala-ai/agent-code issue #524](https://github.com/avala-ai/agent-code/issues/524).

## Source and selection

- **Canonical Index:** [`opensiro/vsm-harness-index@5393b698bfdfa4ca14d97a79238234eca20694e5`](https://github.com/opensiro/vsm-harness-index/commit/5393b698bfdfa4ca14d97a79238234eca20694e5); [included `assessments/ag/agent-code.md`](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ag/agent-code.md) at assessed `review_ref=2734ab5f18939b20c774b39c4406788383e35255`. It explicitly reports no independently source-observing S3* code-review closure in the assessed product. Do not treat `S3*=—` alone as a defect.
- **Current target:** [`avala-ai/agent-code/main@82e0edfa7372c256d893d0854f954d9099254f88`](https://github.com/avala-ai/agent-code/commit/82e0edfa7372c256d893d0854f954d9099254f88); issue [#524](https://github.com/avala-ai/agent-code/issues/524) explicitly requests a fresh-context independent reviewer with read-only repo inspection and a rubric. `/review` in current code already has target parsing and a rubric via prior work, but returns `CommandResult::Prompt` to the **parent** TUI session.
- **Candidate:** [`IMPR-AGENT-CODE-ISOLATED-REVIEW-20261021`](https://github.com/opensiro/upstream/blob/design/improvement-candidates-intake-20261020/candidates/agent-code-isolated-reviewer-20261021.md), `ASSESSMENT_DERIVED` at **hypothesis discovery** level, not proven product benefit.
- **Native patch:** [`reviewer-subagent-first-slice.patch`](reviewer-subagent-first-slice.patch); SHA256 `fed2a54bee994773929367c13000e1de1caed08826a06450b7f1afd9d15b0754`. This patch is an artifact against the exact target `main` commit, **not** a GitHub write to the target repo.

## Native behavior — built-in reviewer and fail-closed subagent permission overlays

- Add `review` to `AgentRegistry::with_defaults`, with the already-maintained `review::RUBRIC` attached to the child's task prompt; a 20-turn limit; `read_only=true`; and allowlisted `FileRead`, `Grep`, `Glob`, and `Bash`. Explicitly exclude network tools, delegation tools and filesystem writing/editing tools.
- Reuse the existing `AgentTool` subprocess contract: invoking `Agent` with `subagent_type="review"` and an explicit task description invokes a **distinct** `agent --prompt` child process. The parent conversation is **not serialized** into that command and the type requests a `Plan` permission overlay. The existing Bash `Plan` validator rejects classified writes/network requests.
- Advertise this type in the tool description/schema and a single tool-reference page. No separate bot, executor, duplicate runner or new dependency.
- Add two native tests: reviewed definition/rubric/limited tools and constructed child command/scope. The tests never contact an LLM provider.
- **Fail-closed overlay enforcement:** `apply_agent_definition` now returns `Result<(), String>` rather than logging and continuing with parent permissions. Its constrained overlay write or serialization failure aborts command preparation; errors propagate through foreground/background `AgentTool`, per-agent `Coordinator::run_agent`, team runs, and detached background workflows. Unrestricted agents are not forced to create an overlay. The test injects an overlay-write error without changing global environment and confirms a descriptive failure instead of accepting inherited permissions.

## Child CLI overlay enforcement (2026-10-21)

The updated patch also changes `crates/cli/src/main.rs` (now **four native files**): when `AGENT_CODE_REQUIRE_PERMISSIONS_OVERLAY=1` or a child explicitly supplies a required overlay, it must not proceed without the file or silently continue after invalid TOML, missing/invalid `[permissions]` or a host policy that refuses overlays. The shared launcher sets the marker only after creating a valid overlay and propagates it to both `AgentTool` and `Coordinator` children. The main interactive CLI retains its historical warning behavior for manually supplied invalid overlays. First-party parser unit tests **2/2 PASS**; compiled binary was tested on five isolated, synthetic negative cases; **5/5 refused before model access (exit status 1)**.

## Explicitly NOT done or proved

This **does not** convert the slash `/review` from `CommandResult::Prompt` to a child run; it does not replace the child's true system message (the current shared coordinator prefixes the reviewer instructions to the child prompt), parse structured JSON findings, render review cards, return structured results into the parent UI, or expose `agent review --json` / `POST /review`. Those are later distinct acceptance criteria of #524.

**Remaining security boundaries:** the tested overlay-write error no longer falls back to inherited permissions in the launcher. Project disk agent definitions named `review` are now ignored (tested) so they cannot override the built-in profile; `Plan` mode Bash constraints are classifier-based, not an OS sandbox; actual attempts to write via subprocess, shell redirection and network egress have **not** been independently tested. The child must still call its configured model provider, so tool-level network restrictions cannot mean total network isolation. Do **not** call the reviewer fully sandboxed or fail-closed across all configuration/OS escape paths.

No live provider review quality measurements, false-green rate, or before/after correctness metric are claimed. This is a **product-native partial implementation** selected from the Index-origin S3* hypothesis, with **actual independent review benefit still pending**. No VSM grade, candidate qualification, external fork, target code/issue/PR, S1 admission or external stage grant is changed.

## Exact-patch validation checkpoint: fail-closed child process

On the source-pinned `main@82e0edfa7372c256d893d0854f954d9099254f88`, the SHA256 `fed2a54bee994773929367c13000e1de1caed08826a06450b7f1afd9d15b0754` patch was applied into **a second clean worktree**. `git apply --check`, `git diff --check` and `cargo fmt --all -- --check` all passed on that clean worktree.

After compiling `agent-code` (Rust 1.97, local Zig C/archive/linker adapters), ran the **real `target/debug/agent` executable** with an isolated, empty HOME, no provider keys, `AGENT_CODE_SUBAGENT=1`, `AGENT_CODE_REQUIRE_PERMISSIONS_OVERLAY=1` and a synthetic task. Each of five intentionally broken overlays aborted with exit code **1** and the expected specific error:

| Executed error case | Exit / observed result |
| --- | --- |
| Required overlay marker but no `--permissions-overlay` argument | 1 / missing required flag |
| Required overlay file does not exist | 1 / failed to read |
| Malformed TOML file | 1 / invalid TOML |
| TOML file without `[permissions]` | 1 / missing section |
| `[permissions]` has invalid value type | 1 / invalid section |

**Runtime negative-path total: 5/5 PASS**; no model call or network access was required. CLI overlay parser's two new Rust unit tests also passed (**2/2**). The earlier coordinator, AgentTool and review filters passed **37/37**, **15/15** and **14/14**, respectively, during development of the typed reviewer and launcher hardening. A later attempt to repeat the complete filters on one shared checkout was interrupted when **parallel changes to the same checkout** began modifying `/review` and waiting on Cargo locks; **do not count that incomplete rerun as final exact-patch CI**.

**Still required for complete acceptance:** independently reproduce a successful child review with a configured local/test provider, assert filesystem/network restrictions under negative adversarial cases, handle structured results and route `/review` to the child rather than the ambient conversation, run the full upstream check/test/clippy/CI matrix. A real OS-level sandbox and loaded provider must be considered separately. This is a tested **fail-closed configuration boundary**, not proof of zero escape vectors or measurable code-review quality.

## Verification contract and replay

The original `AgentRegistry::with_defaults` has **no** registered `review` role. The patch adds definition tests, a deterministic injected overlay-write failure regression and validates construction of a separate subprocess with an explicit prompt, review rubric and `--permission-mode plan`.

```bash
git clone https://github.com/avala-ai/agent-code.git
cd agent-code
git checkout 82e0edfa7372c256d893d0854f954d9099254f88
git apply --check /path/to/reviewer-subagent-first-slice.patch
git apply /path/to/reviewer-subagent-first-slice.patch
cargo fmt --all -- --check
cargo test -p agent-code-lib builtin_review_subagent_is_constrained_and_has_a_rubric --lib
cargo test -p agent-code-lib review_subagent_is_a_fresh_process_with_a_read_only_tool_boundary --lib
cargo test -p agent-code-lib a_missing_permissions_overlay_fails_closed --lib
```

**Native Rust validation at exact source HEAD, with the candidate patch applied:**

- Rust toolchain `1.97.0` with a local Zig C/linker/archive wrapper (stock VM lacks `cc`/`ar`). No model API keys required.
- `cargo test -p agent-code-lib review:: --locked --lib` → **14/14 PASS** (existing review target/rubric tests).
- `cargo test -p agent-code-lib services::coordinator::coordinator_tests --locked --lib` → **37/37 PASS**, including the new definition/profile test.
- `cargo test -p agent-code-lib tools::agent::tests --locked --lib` → **15/15 PASS**, including the new child-process command test.
- **66/66 selected tests PASS** across the three nonoverlapping module filters; `cargo fmt --all -- --check` and `git diff --check` PASS; exact patch `git apply --check` and formatting on a second pristine worktree PASS.
- The new `a_missing_permissions_overlay_fails_closed` regression passed **1/1** on the final implementation, and `an_unrestricted_subagent_needs_no_overlay` passed within the coordinator test group. The previous code had an explicit log-and-continue fallback, so the critical behavior difference is inspectable. The baseline original `AgentRegistry::with_defaults` did **not** register a `review` type. After the patch, the new test confirms registration, rubric inclusion, plan permission-mode, explicit bounded tool profiles and separate subprocess command construction. This is a *configuration-and-execution-path test*, **not an executed live LLM review**.

**Not run:** `cargo check --all-targets`, full `cargo test --all-targets`, `cargo clippy --all-targets -- -D warnings`, cross-platform CI, a live model-run and actual no-write/no-network sandbox adversarial tests. Full acceptance of issue #524 remains unmet. An isolated Rust 1.97 toolchain was bootstrapped because this VM initially had no `cargo`, `rustc`, system `cc` or `ar`. First unmodified build failed on missing `cc`; a Zig C/linker wrapper was added, then initial retry failed on missing `ar`, then a Zig archive wrapper was added. These are **environment setup failures**, not assertions about the target implementation. Selected native Rust tests completed successfully. Full CI, adversarial runtime sandboxing and model-backed comparative review remain outside this result.

**Independent patch replay:** the exact updated diff was applied on a separate pristine checkout of original `82e0edfa7372c256d893d0854f954d9099254f88`. `git apply --check`, `git diff --check` and `cargo fmt --all -- --check` succeeded there. The SHA256 above refers to this updated fail-closed revision, not the older first-slice patch.

**Authority:** internal OpenSiro draft only, external maintainer PR publication remains human-owned.
