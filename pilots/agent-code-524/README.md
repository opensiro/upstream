# agent-code #524 — constrained fresh-context reviewer subagent, first native slice

**Research / implementation status:** `NATIVE_PATCH_PREPARED / RUST_TESTS_PENDING / NOT_UPSTREAM_SUBMITTED` (2026-10-21). This is an internal, reviewable OpenSiro patch handoff, **not** a completed implementation of [avala-ai/agent-code issue #524](https://github.com/avala-ai/agent-code/issues/524).

## Source and selection

- **Canonical Index:** [`opensiro/vsm-harness-index@5393b698bfdfa4ca14d97a79238234eca20694e5`](https://github.com/opensiro/vsm-harness-index/commit/5393b698bfdfa4ca14d97a79238234eca20694e5); [included `assessments/ag/agent-code.md`](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ag/agent-code.md) at assessed `review_ref=2734ab5f18939b20c774b39c4406788383e35255`. It explicitly reports no independently source-observing S3* code-review closure in the assessed product. Do not treat `S3*=—` alone as a defect.
- **Current target:** [`avala-ai/agent-code/main@82e0edfa7372c256d893d0854f954d9099254f88`](https://github.com/avala-ai/agent-code/commit/82e0edfa7372c256d893d0854f954d9099254f88); issue [#524](https://github.com/avala-ai/agent-code/issues/524) explicitly requests a fresh-context independent reviewer with read-only repo inspection and a rubric. `/review` in current code already has target parsing and a rubric via prior work, but returns `CommandResult::Prompt` to the **parent** TUI session.
- **Candidate:** [`IMPR-AGENT-CODE-ISOLATED-REVIEW-20261021`](https://github.com/opensiro/upstream/blob/design/improvement-candidates-intake-20261020/candidates/agent-code-isolated-reviewer-20261021.md), `ASSESSMENT_DERIVED` at **hypothesis discovery** level, not proven product benefit.
- **Native patch:** [`reviewer-subagent-first-slice.patch`](reviewer-subagent-first-slice.patch); SHA256 `0dfd319e31548af89b751af703f391ba46d57e4dc3846b91fe7b88a3e56d569d`. This patch is an artifact against the exact target `main` commit, **not** a GitHub write to the target repo.

## First narrow behavioral slice — built-in review subagent usable via existing Agent tool

- Add `review` to `AgentRegistry::with_defaults`, with the already-maintained `review::RUBRIC` attached to the child's task prompt; a 20-turn limit; `read_only=true`; and allowlisted `FileRead`, `Grep`, `Glob`, and `Bash`. Explicitly exclude network tools, delegation tools and filesystem writing/editing tools.
- Reuse the existing `AgentTool` subprocess contract: invoking `Agent` with `subagent_type="review"` and an explicit task description invokes a **distinct** `agent --prompt` child process. The parent conversation is **not serialized** into that command and the type requests a `Plan` permission overlay. The existing Bash `Plan` validator rejects classified writes/network requests.
- Advertise this type in the tool description/schema and a single tool-reference page. No separate bot, executor, duplicate runner or new dependency.
- Add two native tests: reviewed definition/rubric/limited tools and constructed child command/scope. The tests never contact an LLM provider.

## Explicitly NOT done or proved

This **does not** convert the slash `/review` from `CommandResult::Prompt` to a child run; it does not replace the child's true system message (the current shared coordinator prefixes the reviewer instructions to the child prompt), parse structured JSON findings, render review cards, return structured results into the parent UI, or expose `agent review --json` / `POST /review`. Those are later distinct acceptance criteria of #524.

**Hardening caveat:** the current shared `apply_agent_definition` helper logs and may fall back to inherited permissions on permissions-overlay file-write errors; user/project disk agent definitions can override built-in types. Therefore an allowed-tools unit assertion alone **cannot** be treated as a fail-closed safety guarantee for arbitrary runtime configurations. The first slice needs a separate fail-closed permissions-overlay + actual no-write/no-network negative test before being promoted or described as a fully confined reviewer. The reviewer will also necessarily use the user's configured model endpoint; the tool-level network restriction is not equivalent to an OS-level egress sandbox.

No live provider review quality measurements, false-green rate, or before/after correctness metric are claimed. This is a **product-native partial implementation** selected from the Index-origin S3* hypothesis, with **actual independent review benefit still pending**. No VSM grade, candidate qualification, external fork, target code/issue/PR, S1 admission or external stage grant is changed.

## Verification contract and replay

The original `AgentRegistry::with_defaults` has **no** registered `review` role. The patch adds definition tests and validates construction of a separate subprocess with an explicit prompt, review rubric and `--permission-mode plan`.

```bash
git clone https://github.com/avala-ai/agent-code.git
cd agent-code
git checkout 82e0edfa7372c256d893d0854f954d9099254f88
git apply --check /path/to/reviewer-subagent-first-slice.patch
git apply /path/to/reviewer-subagent-first-slice.patch
cargo fmt --all -- --check
cargo test -p agent-code-lib builtin_review_subagent_is_constrained_and_has_a_rubric --lib
cargo test -p agent-code-lib review_subagent_is_a_fresh_process_with_a_read_only_tool_boundary --lib
```

**Local exact native Rust test result:** pending. An isolated Rust 1.97 toolchain was bootstrapped because this VM initially had no `cargo`, `rustc`, system `cc` or `ar`. First unmodified build failed on missing `cc`; a Zig C/linker wrapper was added, then initial retry failed on missing `ar`, then a Zig archive wrapper was added. These are **environment setup failures**, not assertions about the target implementation. Record a PASS only after Rust compiler and test runner exit successfully, and separately note CI/full matrix gaps.

**Authority:** internal OpenSiro draft only, external maintainer PR publication remains human-owned.
