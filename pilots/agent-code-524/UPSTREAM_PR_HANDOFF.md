# Upstream contribution handoff — avala-ai/agent-code #524

**Scope:** executable source-level, offline-validated improvement. This is a *prepared human-owned external PR packet*, not a published fork/branch/PR and not the completed upstream #524 issue. The original [issue #524](https://github.com/avala-ai/agent-code/issues/524) and already merged [first slice #529](https://github.com/avala-ai/agent-code/pull/529) establish the expected staged architecture.

**Current source pin:** `avala-ai/agent-code/main@82e0edfa7372c256d893d0854f954d9099254f88`.
**Patch:** [reviewer-subagent-first-slice.patch](reviewer-subagent-first-slice.patch), SHA256 `58a70a40beafcceef1f76161f869f4fe2366272d8a82ea9fe9b48fcf530235e1`.
**Internal review artifact:** [opensiro/upstream PR #69](https://github.com/opensiro/upstream/pull/69) — **open, ready for internal code/evidence review; not merged**.

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

The patch spans eight Rust/docs files across the core library and modern CLI, including a sensitive permissions boundary. Under the upstream [SHIP.md](https://github.com/avala-ai/agent-code/blob/main/SHIP.md) large/dangerous-change rules, prefer staged human review and avoid treating the green offline run as a security approval. The maintainer may prefer splitting the patch into smaller changes before review. Preserve semantics and evidence; do not mislabel this as complete #524 or change the source pin without retesting.

## Actual before/after receipts and contribution readiness (2026-10-21)

**Source engineering / offline behavior verified:**
- [Complete native offline CI #39640741764](https://github.com/opensiro/upstream/actions/runs/39640741764) — SUCCESS, compiled real source, Rust tests, required permission-overlay rejects, synthetic local HTTP/JSONL integration.
- [Linux/Windows upstream compatibility CI #39640741743](https://github.com/opensiro/upstream/actions/runs/39640741743) — SUCCESS: cross-platform all-target tests and independent exact Clippy baseline diagnostic-location parity. **Unqualified strict Clippy still fails** on six existing source lines in two unchanged upstream files; no new diagnostic locations attributed to this patch.
- [Original-vs-patched executable #39640742103](https://github.com/opensiro/upstream/actions/runs/39640742103) — SUCCESS. Main agent unchanged, child reviewer uses its own dedicated system persona, and both missing/malformed mandatory permission overlay cases change from **ALLOWED** to **REJECTED**. This is a deterministic process-contract improvement, **not** full TUI E2E, security containment, or model review-quality improvement.

**Publication state / read-only preflight:** original public upstream `main` remains `82e0edfa7372c256d893d0854f954d9099254f88`; existing issue [#524](https://github.com/avala-ai/agent-code/issues/524) is open; first partial upstream [#529](https://github.com/avala-ai/agent-code/pull/529) merged. No public `opensiro-contributions/agent-code` or `opensiro/agent-code` repository was found during this checkpoint; **no verified working fork, contribution branch or external PR**. Under the existing [fork-stage route](https://github.com/opensiro/upstream/blob/main/docs/OPENSIRO_CONTRIBUTIONS_FORK_ROUTE.md) and [Upstream #6](https://github.com/opensiro/upstream/issues/6), neither a successful OpenSiro CI nor the operator's generic `continue` creates a stage-specific authorization. No fork/branch write has been performed.

**Next permitted handoff:** internal technical/permissions review of the eight-file patch, followed by an **exactly authorized** fork-and-`prepare_contribution` stage if the operator separately chooses it. The external PR itself is reserved for manual human publication.

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
- [x] Independent [offline validation workflow #39628191036](https://github.com/opensiro/upstream/actions/runs/39628191036) **SUCCESS** on internal PR head `a39412a22357a5647ff9740e0fb832460daf8427`: exact patch SHA/source/apply, Rust formatting, full `agent-code-lib --lib` and `agent-code --bin agent` tests, scoped Clippy, native compiled executable, credential-free startup/overlay smoke, actual local mock-provider HTTP/JSONL subprocess smoke, and evaluator tests **all job steps PASS**. This is offline engineering validation only; no real model API, model-quality E2E, Windows matrix, or unqualified all-targets CI. Subsequent documentation commits do not modify the pinned eight-file source patch.
- [x] Independently completed source-pinned [all-targets compatibility run #39634816635](https://github.com/opensiro/upstream/actions/runs/39634816635) **SUCCESS**: Linux `cargo check --all-targets --locked` + `cargo test --all-targets --locked`; Windows `cargo test --all-targets --locked`; SHA-pinned source/patch replay and strict Clippy baseline-to-patch diagnostic-location comparison. All three jobs PASS.
- [x] Original upstream strict Clippy **is NOT green even without the patch**: six `clippy::unnecessary_cast` error locations in two unaffected files. With the patch it reports exactly the same six unique locations, duplicated across build targets (12 events); **zero new lint locations**. [Fail-closed validator](verify_clippy_baseline.py) plus [8/8 parser/unit tests](test_verify_clippy_baseline.py) record and verify the distinction. Do not call this unqualified strict-Clippy PASS.
- [x] Rechecked complete credential-free process/mock-provider run [#39634816349](https://github.com/opensiro/upstream/actions/runs/39634816349) **SUCCESS** on the same frozen native patch, without LLM API.
- [ ] Upstream maintainer's own external PR CI, baseline strict-lint resolution/acceptance, optional release target matrix and reviewer sign-off remain open; the local OpenSiro workflow does not replace these steps.
- [ ] Verify/create the actual contributor fork under a separate exact-stage operator authorization, then validate its branch, direct parent, source SHA and push rights; current public candidate forks were not found. Publication permission remains separate.
- [ ] Human publication of the external PR and maintainer feedback (not performed by this handoff).

**Research boundary:** independent-review quality benefit and any S3* reassessment remain `NOT_MEASURED` in the separate [optional protocol](evaluation/PROTOCOL.md). A working implementation + offline tests is legitimate source engineering but **not measured superiority to existing review**.
