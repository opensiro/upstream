# Dark Factory: fail closed on unknown or aliased parallel file scopes

> **Current third-party lifecycle (readback 2026-11-12):** **MERGED**: [original ruslantrachuk/dark-factory PR #106](https://github.com/ruslantrachuk/dark-factory/pull/106) on 2026-11-10T16:44:55Z by `ruslantrachuk`. Final source PR head `bbcd33077bb94befe9599f6f62642caac1cfc885` and merge commit `36d788ad7df913d09f91c63be88155323a9f5ae8`. [Five-source GitHub evidence](../../reports/2026-11-12-five-merged-external-pr-lifecycle-readback.md). Any older unpublished or AWAITING_EXTERNAL wording below is a **historical preparation snapshot**, not the current external lifecycle. Strict native-outcome metric acceptance is separate and remains unclaimed.


Status: `ASSESSMENT_DERIVED` / **native helper source-tested**, OpenSiro-only unpublished packet.
Owning route: [Upstream #56](https://github.com/opensiro/upstream/issues/56),
batch `data/assessment-candidate-batches/2026-11-06-12.json`.

## Index-first S2 finding

The included [`dark-factory` assessment at Index `5e070733`](https://github.com/opensiro/vsm-harness-index/blob/5e0707331a61345df50a2d3cfec543d448fde963/assessments/da/dark-factory.md) observed `S2=C` through a concrete anti-interference mechanism: `pairwiseDisjoint` chooses parallel builder waves only when their planned `files[]` sets do not overlap; otherwise it serializes writes. Its reviewed source was `a56142f7`.

The independently checked newer current default branch is [`ruslantrachuk/dark-factory@19d4c47`](https://github.com/ruslantrachuk/dark-factory/commit/19d4c470e50acab9eeaf346152cd43afc2ad4f85), 2026-11-05. The core code still compares raw path strings and treats absent/empty sets as disjoint. The `graph.tasks[].files` schema allows an empty array and the planning prompt retrieves file lists from free-form issue text. Therefore the guard can send *unknown* or equivalent textual file scopes to parallel builders even though disjointness is not established. The existing single integrator cannot undo arbitrary simultaneous same-file edits. This is a narrow first-party S2 safety decision; it is **not** evidence of autonomous model coordination or a reason to change VSM grades.

Native source: [`feature-core.js`](https://github.com/ruslantrachuk/dark-factory/blob/19d4c470e50acab9eeaf346152cd43afc2ad4f85/plugins/dark-factory/workflows/feature-core.js), the `pairwiseDisjoint` function and the parallel/sequential branch. Current first-party policy: MIT `LICENSE`; `CONTRIBUTING.md` requires English, no installed-plugin dependency on root-only files, tests documented and wired into CI. A read-only issue/PR overlap search on collision/file scope terms did not return a same-topic candidate; lexical absence is not proof of uniqueness.

## Technical packet and matched evidence

Patch [`wave-file-scope-guard.patch`](wave-file-scope-guard.patch), SHA-256:
`3a8c505216bd41cf1ccac83c5d0ed6567311865933fd00946977e30c12d5dd3d`.

Four first-party files change:

- `plugins/dark-factory/workflows/feature-core.js` — do not accept a missing/empty file list as proof of disjointness; compare normalized repository-relative lexical paths; reject outside-root/absolute/wildcard scopes for parallel execution.
- `tests/test_feature_core_disjointness.mjs` — five Node `node:test` cases extract and execute **the literal first-party `pairwiseDisjoint` implementation** from its shipped workflow file. They do not reproduce or simulate the agent execution engine.
- `.github/workflows/test.yml` and `CONTRIBUTING.md` — run this native helper suite in CI and document it, following contributor policy.

Matched scripted result against the same first-party source:

| Case | Unmodified `19d4c47` + identical tests | Patched `19d4c47` |
| --- | --- | --- |
| Five native file-scope tests | **2 PASS / 3 FAIL** | **5 PASS / 0 FAIL** |
| Existing `python3 scripts/test_repo.py` | Not rerun at baseline | **36 PASS / 0 FAIL**, original and clean re-applied patch checkout |

Clean detached Git worktree from current source: `git apply --check` passes for the archived exact patch, then `node --test tests/test_feature_core_disjointness.mjs` gives 5 PASS and repo wiring gives 36 PASS again. Node v24.22.1, Python 3.12. No model, builder, simulated dry-run agent episode, provider, network, browser or external service execution. The full first-party CI (Claude plugin validator, venv pytest integration suites, all dry-run scenarios) **was not executed**; record `NOT_VERIFIED`, not PASS.

## Native fit and remaining limits

| Gate | Outcome | Product-native meaning |
| --- | --- | --- |
| Need | PASS | A source guard currently approves parallelism even with zero file-scope evidence. |
| Mechanism | PASS | The guard is called immediately before the actual parallel/sequential branch. |
| Counterfactual | PASS | Serializing unproven overlaps prevents conflicting simultaneous writes independently of VSM language. |
| Scope | PASS | One pure guard and a native zero-agent test, with release CI wiring. |

The normalization is **lexical**, not filesystem-realpath or symlink-aware; no claim of full alias safety, tested end-to-end developer workflows, or measured user benefit. In some legitimate cases the change chooses serial execution conservatively, which may reduce concurrency. A maintainer may need to define a broader file-scope canonicalization contract before accepting it.

**No external publication authorization.** The finite 34-case Corrective mandate excludes this new Improvement batch. No external fork, branch, issue, PR, maintainer contact or merge was made. This is an internal handoff only; publication/acceptance and deployment benefits remain unverified.
