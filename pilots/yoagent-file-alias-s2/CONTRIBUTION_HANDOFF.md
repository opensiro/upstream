# yoagent S2 — hard-link aliases must share the file mutex

**Batch:** [Upstream upgrade 24](../../data/assessment-candidate-batches/2026-11-10-24.json) / [#56](https://github.com/opensiro/upstream/issues/56). **Prepared state:** `ASSESSMENT_DERIVED / AWAITING_EXTERNAL`. **External action:** `NOT_EXECUTED`.

## Prospective source of the hypothesis

The [included canonical Index assessment](https://github.com/opensiro/vsm-harness-index/blob/8cd38ff31b5b75c6f603624bbbed5072822c5aec/assessments/yo/yoagent.md) rated `yologdev/yoagent@f1495e7` S2=C for coordination of file-tool access. At [pre-source checkpoint b4fcedc](https://github.com/opensiro/upstream/commit/b4fcedc797cb8094897c56764cf85ab33e980472), we predicted that two names for one file could bypass a path-indexed coordination mutex. The prediction specified a Unix hard-link falsifier before fresh source or issue inspection.

Actual [file tools](https://github.com/yologdev/yoagent/blob/f1495e7f5746445a269ec6a9d14fa8ac346b359d/src/tools/file.rs) acquire a process-global weak-referenced mutex keyed by resolved `PathBuf`. [PathSandbox](https://github.com/yologdev/yoagent/blob/f1495e7f5746445a269ec6a9d14fa8ac346b359d/src/tools/sandbox.rs) canonicalizes symlinks but cannot collapse distinct hard-link names; those paths address one underlying Unix inode. The prespecified source-native test failed at exactly that mutex boundary.

## Narrow product-native technical return

- [Native regression patch](native-regression.patch): on Unix create two hard-link aliases and a distinct file; hold the first guard, require the alias to **wait**, allow the distinct file through, then require the alias to proceed after release.
- [Production patch](native-fix.patch): key existing Unix regular files by `(device,inode)`, with fallback to the previous resolved pathname for nonexistent/nonregular/non-Unix cases. Preserve original cancellation behavior and weak-map cleanup.
- [Independent host receipt](INDEPENDENT_HOST_RECEIPT_2026-11-10.md): exact product SHA, patch SHA-256s, external Docker Rust runner IDs, reproduced **RED 1 failing regression → GREEN 2/2 related tests**, expanded **592/592** `cargo test --lib` and `cargo fmt -- --check` PASS.

| Native fit gate | Decision | Scope of proof |
| --- | --- | --- |
| `need` | **PASS** | Real-source pinned regression acquired two distinct path guards for one Unix inode before fix. |
| `mechanism` | **PASS** | File guard key now identifies existing regular file inode, not alias pathname. |
| `counterfactual` | **PASS** | Matched test fails before/passes after; unrelated file proceeds; existing cancellation test and 592 library tests pass. |
| `scope` | **PASS** | Minimal MIT-license Unix-specific source/test patch, fallbacks preserved and no provider/agent/external action. |

## Limitations and handoff boundary

The test covers **one process** and existing regular files; no guarantee for other processes, competing unlink/recreate/replace races, Windows or nonregular files. Rust 1.86 minimum support was *not* verified because current dependencies required Rust 1.91.1 in this runner; the local lockfile was resolved without `--locked`. Source-native maintainer compatibility, broader integration tests and the current default-branch state must be rechecked before proposing the change.

This is a measured **mutex correctness fix**, not demonstrated real-world workflow improvement, external adoption, or automatic Index S2 grade change. Publication to `yologdev/yoagent` is **not** authorized by an ordinary Upstream batch; obtain the distinct current [external publication gate](https://github.com/opensiro/upstream/issues/6), recheck MIT and [CONTRIBUTING](https://github.com/yologdev/yoagent/blob/f1495e7f5746445a269ec6a9d14fa8ac346b359d/CONTRIBUTING.md), and only then open a third-party PR.
