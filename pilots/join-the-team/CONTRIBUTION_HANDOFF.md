# join-the-team — operating-model bootstrap escapes target via symlinks

**Stage:** `AWAITING_EXTERNAL`. Native source patch and repeatable tests only; no external fork, commit, issue or PR was created.

- **Source:** `jpantsjoha/ai-native-developer-experience@e93069b92735ba096abf662f2b9d95a0ebfd36f9`, matching the inspected upstream `main` on 2026-10-22.
- **Canonical assessment:** `assessments/ai/ai-native-developer-experience-join-the-team.md`, included `S1=A` at frozen Index `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`, **not** `ASSESSMENT_DERIVED`: the assessment identifies a native bootstrap/validation component; the specific symlink-boundary issue was found in the source afterwards, not predicted by the assessment.
- **Need — PASS:** the initializer promises non-destructive installation inside a requested target but `Path.exists()` returns false for a dangling output symlink. Its subsequent `write_bytes()` follows that link and creates a file outside the target. An ancestor `docs` symlink likewise redirects new planning files outside the target.
- **Mechanism — PASS:** reject a symlink at any destination and any canonicalised output path outside the resolved target during the existing all-artifact preflight. Existing preservation/idempotency flow remains in place.
- **Counterfactual — PASS:** two newly written first-party deterministic `unittest` cases both fail on baseline (script exits 0 and writes outside target); after the patch, both pass (script exits 2 with no external writes). Both use disposable temporary directories.
- **Scope — PASS:** only `skills/operating-model-bootstrap/scripts/bootstrap_operating_model.py` and the corresponding `tests/test_operating_model.py` change.

## Native receipts

| Check | Verified result |
| --- | --- |
| Baseline focused first-party file + two new tests | 11 PASS, **2 RED** (both symlink boundary checks) |
| After patch focused file | 13 PASS, 0 FAIL |
| Entire first-party `python3 -m unittest discover -s tests -p 'test_*.py' -q` | **131 PASS**, 0 FAIL, 40.512 seconds |
| `make typecheck` | PASS — Python standard-library compilation |
| `make spec-conformance` | PASS — Agent Plugins 1.0.0, 0 findings |
| Plugin validator | PASS — 0 findings |
| Operating-model template validator | PASS — 0 warnings |
| `make lint` / `make check` | Not run: `markdownlint-cli2` is not installed; do not claim the aggregate gate passed |

Patch: [`bootstrap-symlink-boundary.patch`](bootstrap-symlink-boundary.patch). Its SHA256 is `1d71b8cde8a61f1d0a6c06911ac9ce457db71be042b9822b2d93f4d2d144efb0`, identical to the native Git diff over the two tested files. The patch is uncommitted and unpushed in the external checkout.

**Adversarial limitation:** This narrow fix guards canonicalised paths at preflight time; it does not claim to close a concurrent symlink-substitution (TOCTOU) race between the check and `write_bytes()`. Hardening against concurrent adversaries would require a separate design and native test plan.

**External handoff:** A human owner may later verify this exact patch against fresh upstream `main`, check for maintainer overlap and repository rules, rerun native tests and explicitly authorise publication. Generic `continue` **skips** this `AWAITING_EXTERNAL` row and advances to `maref-run-state-boundary`.

## 2026-10-25 current-fit and contributor-policy stop

The current upstream `main` remains `e93069b92735ba096abf662f2b9d95a0ebfd36f9`, exactly the source revision used for the original native patch. The preflight still checks `Path.exists()` for destinations without a symlink/canonical-target admission guard. There is no newly published fix PR for this exact defect in the bounded search. The old source-tested native receipts above are preserved; **the tests were not re-run in this 2026-10-25 pass**.

Current [AGENTS.md](https://github.com/jpantsjoha/ai-native-developer-experience/blob/main/AGENTS.md) requires reviewing the status/roadmap, checking for active delivery lanes, coordinating with the active owner and using the delivery-orchestrator work contract. Its [delivery-orchestrator](https://github.com/jpantsjoha/ai-native-developer-experience/blob/main/skills/delivery-orchestrator/SKILL.md) requires a tracked issue before starting code. The previous adoption lane [#32](https://github.com/jpantsjoha/ai-native-developer-experience/issues/32) / [#33](https://github.com/jpantsjoha/ai-native-developer-experience/pull/33) was closed and merged, and no open issue for the symlink escape or corresponding open PR was found. The finite OpenSiro Corrective publication grant covers forks/branches/PRs, not an independent third-party issue or owner-coordination write.

**Publication: BLOCKED by the upstream intake/coordination policy.** No fork, branch push, external issue or PR was created on this pass. Continue with the next frozen candidate; do not treat this policy gate as failure of the previously tested source patch.
