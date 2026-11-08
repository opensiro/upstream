# Harness² — library path-component admission

**Status:** `ASSESSMENT_INFORMED` / `AWAITING_EXTERNAL`, strictly local source-only technical handoff. No external PR, model agent, trajectory replay or sandbox rollout was executed.

## Exact evidence and candidate provenance

- Canonical Index object: `396a54bb690f8ec7ce966bf9b00b241b30036307`, `assessments/ha/harness2.md`, `included S1=A`, reviewed `2026-10-18`.
- Upstream source: `google-research/harness2@1cfe254e8d25b15f37048c3730134686abe60335` (Apache-2.0), [first-party library.py](https://github.com/google-research/harness2/blob/1cfe254e8d25b15f37048c3730134686abe60335/harness2/core/library.py).
- The library's `slug(task_id)` only replaced `/`, so `"."`, `".."` and `""` remained filesystem special components. `Library.entry_dir()` uses those components below `harnesses/`; `Library.forget()` later recursively removes that returned directory. The domain directory function also accepted `".."`, allowing `Library.dir` to escape its intended run root. This is a **source-defined file-path boundary defect**, not a model benchmark result.

## Real-source script test

```shell
python3 -m unittest discover -s tests -p test_library_path_components_native.py -v
```

At the reviewed revision plus the new test file: **2 PASS / 5 FAIL / 1 additional Windows-separator assertion absent initially**. After the narrow source fix and full eight-case test file: **8 PASS / 0 FAIL**. Controls preserve ordinary task/domain flattening. Only `Library.entry_dir`, `slug` and `domain_dir` were exercised; no directory deletion was invoked and no pre-existing files were modified. These are regular Python unittest fixtures, not LLM-agent simulations.

## Proposed diff

- [`library-path-component-guard.patch`](library-path-component-guard.patch), SHA256 `ff286bbdebb07b1e6da88b91e89b2734fac5af10545ee627d6fef856f577dd09`.
- `slug()` rejects empty and dot path components and flattens Windows separators too. `domain_dir()` rejects dot and dotdot after standard normalization. All other entry names retain their existing representation. `git apply --reverse --check` on locally patched first-party source: PASS.
- No broader first-party model-dependent suite claimed, no provider mocks, no researcher grading or policy-effectiveness claim.

## Next boundary

Check for upstream overlap and issue assignment/maintainer expectations, reproduce with the supported upstream Python test environment and obtain separately authorized human publication. The external right is **not** delegated by this packet. Next frozen candidate may be screened immediately.

**2026-10-24 publication preflight:** upstream `main` remains pinned at `1cfe254e8d25b15f37048c3730134686abe60335`, Apache-2.0 license is present. [Google Research `CONTRIBUTING.md`](https://github.com/google-research/harness2/blob/main/CONTRIBUTING.md) requires a **Google Contributor License Agreement** signed by the contributor or employer. The proposed patch also fixes a filesystem escape/delete boundary, requiring security-conscious maintainer coordination. The bounded OpenSiro 34-case publication mandate does not authorize a new CLA attestation on behalf of `xLagerFeuer`. Do **not** submit a public code PR or sign a CLA without the owner's separate agreement and the relevant security channel decision. **No fork/PR created; ledger remains `QUEUED`.**

**2026-10-25 terminal queue review:** Current upstream CONTRIBUTING.md still requires a contributor/employer-signed Google CLA for all code submissions. No verified CLA status or personal authorization to accept one is present. **Ledger now `BLOCKED`**, superseding yesterday's `QUEUED` preflight status. No fork, external PR or fresh native tests; the prior source patch stays internal.
