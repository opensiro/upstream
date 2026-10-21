# Agent-code #524 — consolidated independent reviewer and child permission contract

**Internal OpenSiro handoff · Draft PR #69 · 2026-10-21.**

**Canonical upstream source:** [`avala-ai/agent-code/main@82e0edfa7372c256d893d0854f954d9099254f88`](https://github.com/avala-ai/agent-code/commit/82e0edfa7372c256d893d0854f954d9099254f88), existing [issue #524](https://github.com/avala-ai/agent-code/issues/524). **Index lineage:** [`vsm-harness-index/main@5393b698bfdfa4ca14d97a79238234eca20694e5`](https://github.com/opensiro/vsm-harness-index/commit/5393b698bfdfa4ca14d97a79238234eca20694e5), `assessments/ag/agent-code.md`, `review_ref=2734ab5f18939b20c774b39c4406788383e35255`. The Index records no independent S3* review and issue #524 independently describes the product need.

**Source artifact:** [consolidated eight-file native patch](reviewer-subagent-first-slice.patch), SHA-256 `58a70a40beafcceef1f76161f869f4fe2366272d8a82ea9fe9b48fcf530235e1` (57,663 bytes). The source patch was created from the exact pinned target plus the previously reviewed mandatory-child-overlay protection, combined with the later isolated review and result gate. It **applies successfully on an independent pristine checkout**; `git diff --check` PASS.

## Contribution and validation boundary (current scope)

**Delivery type:** **source-level, offline-validated upstream contribution**. This pilot delivers a reviewable patch to the real `agent-code` files, native Rust tests and local scripted checks. It does **not** claim a live LLM end-to-end (E2E) test or experimentally improved review quality. **No paid LLM API key, model subscription or ChatGPT Browser session is required** to finish the current engineering verification and prepare an external upstream PR for human publication.

**Required engineering evidence for this handoff:**
1. Reapply the exact patch to the pinned upstream source; inspect the diff and verify formatting.
2. Run relevant native Rust unit/regression tests (including reviewer routing, prompt/memory isolation, structured JSONL parsing and fail-closed permission failure paths).
3. Run credential-free local scripts against the rebuilt executable. The [offline process smoke](offline_cli_smoke.py) checks executable startup and required overlays; the [mock-provider smoke](mock_provider_smoke.py) can test the actual streaming/request transport against a **local synthetic HTTP endpoint**, without any real provider or inference. Distinguish scripts that have been committed from scripts whose execution has been recorded.
4. Record native lint/build/CI results honestly, including missing full-workspace/all-targets or cross-platform coverage and the six pre-existing strict-Clippy warnings. Do not replace the upstream maintainer's required CI gates with OpenSiro-only tests.

**Explicitly out of scope for the current contribution gate:** real model calls, paid API access, live ChatGPT-browser-driven inference, provider-backed baseline-versus-isolated review comparisons, human-labeled precision/recall benchmarks and claims of S3* capability improvement. A local mock provider is a **scripted integration/transport test**, not real-model E2E. Tool-level read-only configuration is also **not** proof of an operating-system sandbox.

**Acceptance language:** `SOURCE_IMPLEMENTED / OFFLINE_TESTED` can be used only for paths whose recorded checks passed. Do **not** use `E2E_VALIDATED`, `REVIEW_QUALITY_IMPROVED`, `BENEFIT_SUPPORTED`, `QUALIFIED`, or an Index grade change. The original [assessment-to-improvement experiment #56](https://github.com/opensiro/upstream/issues/56) may remain `SCREENING / BENEFIT_NOT_MEASURED`; the absence of live-model tests does **not** prevent a separately reviewed source contribution, but it **does** prevent declaring the stronger assessment-to-measured-product-benefit hypothesis proven.

**Future research (optional, independently scoped):** [paired quality evaluation protocol](evaluation/PROTOCOL.md). The planned 12 cases / 72 runs are a research design, **not** required preconditions for the current file-level upstream PR, not an ongoing background job, and not performed. Maintainers can request additional validation after reviewing the code.

## Changes

- `/review` preserves current target resolution/rubric but produces a distinct `ReviewTask`, **not** a parent-session model prompt. Modern TUI launches a typed `review` child process via existing `AgentTool`/`TaskManager`; the builtin definition cannot be overridden by project disk profiles.
- Constrained overlay creation **fails closed** in both foreground/background parent launch paths. A child marked as requiring an overlay **refuses to run** if the argument is missing or the file cannot be read, parsed or enforced. The non-subagent interactive compatibility policy remains separate.
- Typed `ReviewOutput` JSON has bounded priority/confidence/location validation. The TUI only displays bounded, labelled, *unverified model findings* on successful parse; it never treats raw task stdout as trusted new parent instructions.
- The child `review` role now **replaces** the default system message with a dedicated reviewer system prompt, including the rubric, JSON output contract and strictly scoped documentation of read-only tools. The general coding-agent persona, response style, user memory and additional directories are not injected as reviewer system instructions. The reviewer task remains a separate user message; both the AgentTool and coordinator reviewer child paths tag their role so the child selects this system message. An explicit pure role-routing test checks replacement and main-agent isolation.
- Completion propagation is gated to task IDs started by this TUI and their initial conversation epoch. Late output after a resume or session switch is discarded; malformed/oversized/non-JSON raw output remains available through `/tasks`.
- **Reviewer memory isolation:** the child-side CLI avoids main-agent background memory consolidation for `AgentKind::Subagent`, even when the extract-memories setting is enabled. This prevents an unrelated memory-maintenance model call and reuse of ambient user memory during the fresh-context reviewer task. Main-agent consolidation remains enabled when configured. Three new unit cases cover main-enabled, subagent-enabled and main-disabled behavior.

## Independent GitHub Actions offline verification (completed)

The exact unchanged native source patch above was replayed from the immutable upstream commit in **[OpenSiro offline-native Actions #39628191036](https://github.com/opensiro/upstream/actions/runs/39628191036)** (internal PR head `a39412a22357a5647ff9740e0fb832460daf8427`). The `offline-native` job finished **SUCCESS**. Every job step passed: patch SHA-256 and source SHA verification, clean `git apply`/diff, Rust formatting, full central `agent-code-lib --lib` and `agent-code --bin agent` native test targets, scoped two-target Clippy with documented pre-existing lint exception, compiled patched executable, startup/mandatory-overlay smoke, **actual local mock-provider HTTP/JSONL process smoke**, and evaluation-scorer unit tests.

This independently reproduces scripted executable behavior **without paid credentials or a real model**. The local HTTP mock supplies synthetic JSON; it does **not** measure model accuracy, user outcomes, true network sandbox containment, or all-targets Windows/upstream CI. This newer actual mock-run receipt supersedes the earlier 'mock script committed but not executed' checkpoint. See the [human-owned external PR handoff](UPSTREAM_PR_HANDOFF.md) for remaining source contribution gates. Subsequent documentation changes do not alter the tested eight-file patch.

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

**Rust Clippy validation on the exact current patch:** `cargo clippy -p agent-code-lib -p agent-code --lib --bin agent --locked -- -D warnings` was **BLOCKED** by six pre-existing `clippy::unnecessary_cast` findings in `crates/lib/src/amr/selectors.rs` and `crates/lib/src/tools/bash_parse.rs`; neither file is touched by this patch. A second run with *only that baseline lint* excluded, `cargo clippy -p agent-code-lib -p agent-code --lib --bin agent --locked -- -D warnings -A clippy::unnecessary_cast`, completed **PASS (exit 0)** for both targets. This is a scoped quality check, **not** a clean unqualified `-D warnings` result, and no unrelated baseline cleanup was silently mixed into the review patch.

**Process-level offline smoke (separate from all unit counts):** Rebuilt the exact eight-file patched `agent` CLI binary with `cargo build -p agent-code --bin agent --locked` (**PASS**) and ran the committed [`offline_cli_smoke.py`](offline_cli_smoke.py) on that binary (**PASS, exit 0**). It uses an isolated temporary `HOME` / `XDG_CONFIG_HOME` / workspace, a fake loopback-only model URL, and a nonsecret dummy key. Results: main-agent diagnostic system prompt present; child reviewer **replaces** that prompt with its distinct review-only system instructions and JSON rubric; no main coding-agent persona in child; valid Plan overlay accepted; missing required overlay **rejected**; malformed required overlay **rejected**. No provider/model request was exercised, so this is an independent *process-startup invariant* result, **not** model review effectiveness or actual OS read-only confinement.

```bash
python3 pilots/agent-code-524/offline_cli_smoke.py --binary path/to/the/patched/agent
```

**Measured change (deterministic policy, not a provider-backed outcome):** prior source passed the general `features.extract_memories` condition to the child lifecycle; after patch the same Boolean gate requires `AgentKind::Main`. Subagents therefore cannot trigger that specific memory consolidation path when configured, and the main agent's behavior is preserved. The test is an isolated role-policy assertion; neither a live memory leak nor an LLM review-quality improvement has been demonstrated.

**Scope caveat:** JSONL handling is still tested on synthetic event streams derived from first-party `JsonStreamSink`. Actual review output with a configured model remains to be checked. Source-pinned Linux/Windows all-targets check/tests and strict-Clippy *baseline parity* are now independently checked in Actions; **unqualified strict Clippy still fails** on untouched upstream diagnostics, and actual external upstream PR CI and provider-backed review-quality comparisons remain absent. The active Index `main` may advance; this experiment intentionally retains the frozen assessment pin for provenance and does not regrade it.

## Original upstream all-targets compatibility and baseline lint attribution — PASS (bounded)

**Frozen source + unchanged reviewer patch:** [Actions run #39634816635](https://github.com/opensiro/upstream/actions/runs/39634816635) completed **SUCCESS**. It independently ran `cargo check --all-targets --locked` and `cargo test --all-targets --locked` on Linux, `cargo test --all-targets --locked` on Windows, and an explicit strict-Clippy before/after parity check on clean and patched source. All three jobs PASS. [Offline actual binary/mock-provider workflow #39634816349](https://github.com/opensiro/upstream/actions/runs/39634816349) also finished SUCCESS. Both workflows required **no LLM API** and preserve the exact upstream source/patch digests.

**Unqualified `cargo clippy --all-targets --locked -- -D warnings` is NOT green:** against the *unpatched* upstream source, the strict command returned six distinct `clippy::unnecessary_cast` errors; against patched source it returned the **same six distinct code/file/line locations**, emitted twice across build targets (12 error events), and no new diagnostic locations. The fail-closed [baseline comparator](verify_clippy_baseline.py) attested the two separate source states, and its [8 synthetic tests](test_verify_clippy_baseline.py) PASS. This is source-lint **parity**, not a silent waiver or a claim of strict-Clippy success. Upstream maintainers may require a separate baseline cleanup or explicitly accept the existing lint limitation; neither has occurred.

**Result boundary:** `SOURCE_IMPLEMENTED / OFFLINE_TESTED / LINUX_WINDOWS_ALL_TARGETS_TESTED / CLIPPY_BASELINE_PARITY` for the frozen patch. No real-model E2E, no measured improvement in reviewer precision/recall, no full release matrix and no external upstream PR/CI or maintainer sign-off. The [prepared human-owned PR handoff](UPSTREAM_PR_HANDOFF.md) remains a proposal.

## Remaining acceptance boundaries

- No real model-backed independent review, blinded same-task comparison, or measured software-quality improvement. `ASSESSMENT_DERIVED` remains a **research selection category**; candidate stays `SCREENING`.
- Reviewer instructions now replace the general coding-agent base system message; the user turn contains only the task. The child produces JSONL and the route reconstructs the last completed turn, but real model-generated JSON may still be invalid; that degrades safely to `/tasks` rather than inventing findings.
- A Plan-mode Bash classifier and tool-level permissions are not an OS-level sandbox. No hostile filesystem/subprocess/network egress test has demonstrated complete containment.
- Results are operator-visible in the TUI, but not injected as a bounded model-visible parent action that would close an automatic S3 correction loop.
- Full **two-target unit tests and Linux/Windows all-targets tests are complete** at the frozen patch; unqualified strict Clippy still fails on the same existing upstream baseline diagnostics. Release build matrix, real model/provider tests, external PR CI and maintainer acceptance remain incomplete. The internal GitHub workflow validates the OpenSiro handoff, not third-party upstream acceptance.

**Authority:** only internal OpenSiro Draft PR #69 is written. No third-party code, contribution fork, external issue/PR, VSM grade, organization S1 admission or delegated permission changed. The human operator retains publication authority.

## Optional future paired-quality study — instrument prepared, no product outcome

A [preregistered paired-review protocol](evaluation/PROTOCOL.md) and [read-only deterministic scorer](evaluation/score.py) are retained **only for optional future research, not as gates for the present source-level contribution**. The protocol distinguishes the shipped parent-session `/review` from the patched isolated reviewer on matched held-out bug and clean-control changes, including blinded findings adjudication, token/latency overhead, failed-run accounting and the rubric-vs-isolation confound. Real model-backed observations have **not** been collected, and no claim of improved review precision/recall is made.

The scorer refuses unpaired observations, mismatched source/model/scenario, missing adjudication and incomplete datasets; mock records explicitly produce `NON_LIVE_NOT_PRODUCT_BENEFIT`. It reports TP/FP/FN, clean-control false alarms, failure/invalid-output counts and paired resource deltas, but **never autonomously concludes product benefit**.

**Validator receipt:** [`evaluation/test_score.py`](evaluation/test_score.py), executed from the exact PR commit `51469b76d7d894d64a1bb5ebb97fa0e03bb73531` via public SHA-pinned raw source on a registered VM, **11/11 unittest cases PASS**. This is a lightweight local scorer-test receipt, not live LLM efficacy validation or a rerun of the Rust patch.
