# Fara — enforce task identity when resuming a checkpoint

**Status:** assessment-linked functional improvement, internal OpenSiro patch only, no third-party PR or model/browser test.

- From frozen [Index-first candidate batch 11](https://github.com/opensiro/upstream/blob/main/data/assessment-candidate-batches/2026-10-23-11.json), row `fara-native-checkpoint-integrity`; canonical [Fara assessment](https://github.com/opensiro/vsm-harness-index/blob/main/assessments/fa/fara.md). Current first-party source [microsoft/fara@a675d6d61c41c47ae87bacefeab22caad18e3e84](https://github.com/microsoft/fara/commit/a675d6d61c41c47ae87bacefeab22caad18e3e84), original `main` as checked 2026-10-23.
- MIT LICENSE verified; no root `CONTRIBUTING.md` or `.github/` discovered at screening; this is not a claim about all possible downstream policies or rights.
- [Patch](resume-task-identity.patch), SHA-256 `fce42386bd6b1cf1ea0fed6c22a206589239cdeeb37f53cfaa48eb027da9002e`.

## Native source finding

Original `RunContext.create(environment, task, output_dir)` automatically resumed any directory containing `task.json`, ignoring the **requested task identity**. Two differently identified tasks sharing a directory could silently return the prior task and contaminate subsequently persisted results.

Scripted Python 3.12 fixture constructs first-party `Task` objects with different IDs, no model, browser, network or Playwright. The fixture imports original Fara core modules directly without importing Fara package-level agent/provider code.

| Behavior | Unpatched | Patched |
| --- | --- | --- |
| Attempt to resume existing run with different `task_id` | silently reuses other Task (**FAIL**) | raises descriptive ValueError before mutation (**PASS**) |
| Resume same task and restore user-defined checkpoint state | PASS | PASS |
| New directory creates requested task | PASS | PASS |

**Before:** 1 FAIL / 2 PASS in the new tests. **After:** 3 PASS / 0 FAIL. Exact test-only source injection and patched after-test reproduced against a clean pinned first-party checkout. Scope is task-ID safety, not byte-for-byte input-config equality, full checkpoint integrity, agent efficacy or browser reliability. No VSM autonomy grade change or real-user impact measured.

Reviewable native replay workflow: [fara-native-resume.yml](../../.github/workflows/fara-native-resume.yml). External publication remains ungranted for Improvement cases under current finite 34 Corrective S5 authorization.
