# G-Rump — bounded source screening (batch 03, row 5)

**Disposition:** BLOCKED_EVIDENCE. No product code modification, external PR or model-agent execution.

- Canonical Index assessment: `assessments/g-/g-rump.md` at `396a54bb690f8ec7ce966bf9b00b241b30036307`; reviewed source `Aphrodine-wq/G-Rump@876766327171eed40df89ef1d58c8c9a475c8def`. Live `main` still resolves to this SHA as of 2026-10-22.
- Actual source `Sources/GRump/Intelligence/Daemon/AutonomousLoop.swift`: a daemon goal invokes `git checkout -B grump-daemon/<id>` on `viewModel.workingDirectory`, then enters the existing ChatViewModel loop; no prior branch return is visible in `DaemonRunner.run`. This suggests the interactive user's shared checkout can remain on the scratch branch. The observation is source-backed but **has not been reproduced by executing the native Swift product**.
- Index also characterizes the daemon as one serial operating agent with approvals, **not** a separate concurrently independent S1; this screen does not upgrade that VSM classification.
- The environment lacks the native Swift/macOS app toolchain. A shell-only reproduction of `git checkout` would not be an actual first-party scripted regression, so was not misrepresented as one. Bounded GitHub search found no directly overlapping restore fix.

| Fit gate | Status | Reason |
| --- | --- | --- |
| Need | PENDING | Probable branch-return issue, pending native test |
| Mechanism | PASS | Exact first-party daemon branch command |
| Counterfactual | PENDING | No compiled Swift RED/GREEN fixture |
| Scope | PASS | Workdir branch selection and restoration in DaemonRunner |

**Continuation:** Defer only this evidence-blocked row and roll forward automatically to the next complete frozen cohort.
