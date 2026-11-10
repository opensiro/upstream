# Caveman Code — bounded source screening (batch 03, row 4)

**Disposition:** BLOCKED_EVIDENCE. A concrete assessed isolation risk exists; no accepted patch or external PR. No LLM/subagent was launched.

- Canonical Index: `assessments/ca/caveman-code.md` at `396a54bb690f8ec7ce966bf9b00b241b30036307`; source `JuliusBrussee/caveman-code@3a21be115c32aa27288c8ed6d860d9aa1b65d2c5`. Live `main` matches exactly as of 2026-10-22.
- In `packages/coding-agent/src/core/tools/task.ts`, `maybeCreateWorktree` returns the shared `parentCwd` when requested `isolation: worktree` cannot find a git root **or** `createWorktree` throws. This intentionally coded fallback is a genuine mechanism risk, but the appropriate error behavior and any demonstrated write collision need native reproduction rather than inference.
- The repository's `AGENTS.md` requires per-package native Vitest with mock subprocesses, prohibits starting the application/build commands, and bars unauthorized external commits/PRs. Installed lockfile dependencies without lifecycle scripts (`npm ci --ignore-scripts`). The prescribed focused first-party test invocation from `packages/coding-agent` — `npx tsx ../../node_modules/vitest/dist/cli.js --run test/task-tool.test.ts` — **collected zero tests** because package `@juliusbrussee/caveman-agent` resolves to an unavailable built entry. This is a **test setup blocker**, not a failed product regression; no fake PASS is recorded.
- Source instructions prohibit `npm run build`, so do not bypass the blocker with that command. No source files of the external repo were edited or committed. A native harness capable of importing workspace packages is needed before RED/GREEN and permission to change behavior can be asserted.
- Bounded GitHub issue/PR searches found no direct matching worktree-fallback fix.

| Fit gate | Status | Reason |
| --- | --- | --- |
| Need | PENDING | Concrete risk, missing native evidence of observable wrong effect |
| Mechanism | PASS | Exact fallback source path identified |
| Counterfactual | PENDING | Native suite could not collect tests |
| Scope | PASS | Bounded worktree creation/fallback function |

**Continuation:** Preserve this receipt, skip the blocked row, proceed to the next frozen candidate. Do not run a model agent as a test substitute.
