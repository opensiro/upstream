# Upstream contribution handoff — avala-ai/agent-code #524

**Scope:** executable source-level, offline-validated improvement. This is a *prepared human-owned external PR packet*, not a published fork/branch/PR and not the completed upstream #524 issue. The original [issue #524](https://github.com/avala-ai/agent-code/issues/524) and already merged [first slice #529](https://github.com/avala-ai/agent-code/pull/529) establish the expected staged architecture.

**Current source pin:** `avala-ai/agent-code/main@82e0edfa7372c256d893d0854f954d9099254f88`.
**Patch:** [reviewer-subagent-first-slice.patch](reviewer-subagent-first-slice.patch), SHA256 `58a70a40beafcceef1f76161f869f4fe2366272d8a82ea9fe9b48fcf530235e1`.
**Internal review artifact:** [opensiro/upstream Draft PR #69](https://github.com/opensiro/upstream/pull/69).

## Suggested external PR (human publishes separately)

**Title:** `feat(review): run /review in a constrained independent reviewer subagent`

**Description:**

> Partial implementation of #524, building on the target/rubric groundwork merged via #529.
>
> This patch routes the modern TUI `/review` to a dedicated child process rather than running inside the authoring conversation. It replaces the normal child system message with a reviewer-only rubric/JSON contract, enforces mandatory fail-closed child permission overlays, parses completed JSONL review output into bounded structured findings, and prevents subagent memory-consolidation side effects. Results appear in the operator TUI/`/tasks`; rejected or malformed outputs are not imported as trusted parent conversation text.
>
> **Verification:** exact-source patch/checksum, Rust format, native library/CLI tests, checked Clippy scope, compiled CLI startup/required-overlay smoke and local synthetic OpenAI-compatible provider/JSONL smoke (when and only when those checks have actually completed; link the corresponding receipt). Tests are offline and require no external LLM API. Synthetic provider output is a **transport integration check, not an evaluation of reviewer accuracy or a production LLM E2E**.
>
> **Non-goals / follow-ups:** no `agent review --json`, no `POST /review`, no model-backed quality claims, no proof of OS-level filesystem/network confinement, and no automatic fix/PR publishing. Please review as a **bounded independent-review execution slice**, not as closure of all #524 acceptance criteria.
>
> **Compatibility / safety:** reuses the current AgentTool/TaskManager, preserves non-review agent output behavior, and fails closed when the child cannot enforce the required permission overlay.

The maintainer may prefer splitting the patch into smaller changes before review. Preserve semantics and evidence; do not mislabel this as complete #524 or change the source pin without retesting.

## Source preparation (for a human-authorized contributor fork)

```bash
# Run only in a clean clone/worktree of the exact public upstream source:
git clone https://github.com/avala-ai/agent-code.git
cd agent-code
git checkout 82e0edfa7372c256d893d0854f954d9099254f88
sha256sum /path/to/reviewer-subagent-first-slice.patch
git apply --check /path/to/reviewer-subagent-first-slice.patch
git apply /path/to/reviewer-subagent-first-slice.patch
git diff --check
cargo fmt --all -- --check
cargo test -p agent-code-lib --lib --locked
cargo test -p agent-code --bin agent --locked
```

The contributor must use their own **explicitly authorized fork/branch** and make a human-owned external publication decision; this handoff does not grant permission to push or open a third-party PR.

## Validation / publication gates

- [x] Upstream is pinned; branch and issue/previous merged slice checked.
- [x] Patch SHA-256 pinned and source-clean replay/native unit test receipt exists in [README](README.md).
- [x] No API key / real LLM endpoint is needed for the current contribution validation scope.
- [ ] A new isolated GitHub Actions [offline validation workflow](../../.github/workflows/agent-code-524-offline.yml) must complete and be inspected; record the exact workflow run and step outcomes here before treating its smoke assertions as passed.
- [ ] Upstream maintainer's complete `cargo check --all-targets`, `cargo test --all-targets`, `cargo clippy --all-targets -- -D warnings` and format CI need independent completion on the contribution branch; scoped lint exception does **not** certify full upstream Clippy. Six baseline `unnecessary_cast` warnings exist in untouched files.
- [ ] External fork/branch evidence plus PR title/body/source digest verified **if publication is authorized**.
- [ ] Human publication of the external PR and maintainer feedback (not performed by this handoff).

**Research boundary:** independent-review quality benefit and any S3* reassessment remain `NOT_MEASURED` in the separate [optional protocol](evaluation/PROTOCOL.md). A working implementation + offline tests is legitimate source engineering but **not measured superiority to existing review**.
