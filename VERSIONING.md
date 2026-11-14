# Upstream contribution protocol — SemVer

This repository versions **one contribution protocol**, independently of VSM Profile versions, Skills assessment Methodology versions, Index commits, individual third-party package versions, `schema_version` fields, and legal-policy/mandate IDs. The only current protocol version is the root [`VERSION`](VERSION), with human-readable grouped changes in [`CHANGELOG.md`](CHANGELOG.md) and [`changes/`](changes/).

## What is versioned

The **effective Upstream contribution procedure**: assessment-first/assessment-informed selection, evidence gates and falsifiers, source-native checks and runner independence, preparation and contributor-fork placement, target PR forms and disclosure, technical publication gates, review/readback and lifecycle requirements.

A version **describes** these rules; it does not extend the active S5 mandate, accept a CLA/DCO, define VSM S1–S5 semantics, regrade the Index, or transfer a third-party maintainer's rights. For executable authority, always consult the current owning policy and user decision.

## SemVer bump contract (experimental 0.x line)

- **MINOR** (`0.y.0`): add, remove, strengthen or relax a required contribution stage, native-evidence gate, publication condition, admission/selection mode or supported operator workflow. During `0.x`, a minor may be incompatible with prior operator assumptions; the changelog must state the practical effect.
- **PATCH** (`0.y.z`): fix an implementation/documentation inconsistency **without introducing a new independently intended obligation**, or correct an invented blocker to restore the existing approved process (for example `0.5.1` direct-chat CLA-as-PR correction).
- **MAJOR**: reserve `1.0.0` for an explicitly declared stable external contribution-protocol contract. After 1.x, incompatible changes require a major bump under ordinary SemVer.
- Routine new assessed sources, batch outcomes, external PRs, watcher receipts, test counts, dashboard regeneration or editorial spelling **do not** by themselves bump the protocol.

A PR that changes normative rules must update `VERSION` and `CHANGELOG.md` and add **one** matching `changes/vX.Y.Z.md` package. It may group several independently reviewed protocol changes into one version. A code-only fix that does not change behavior may be grouped with the next real release; don't fabricate a release per commit. Always preserve the previous packages.

## One-time historical reconstruction (2026-11-14)

No Upstream SemVer tag or VERSION file existed before this reconstruction. The snapshots for `0.1.0` to `0.6.0` are **retrospective change packages** anchored to actual original `main` commits, not releases that were issued on those historical dates. The initial formal version is `0.7.0`: its `VERSION` file starts on the integration commit, while the package cites its last pre-versioning protocol change, [PR #298](https://github.com/opensiro/upstream/pull/298). Historical tags, if created, point at the **original checkpoint commits** and only establish a now-readable comparison line; their creation date is not backdated.

For historical work, a package tells which rules had reached the main branch at its checkpoint. **Do not rewrite** immutable batch manifests or claims about which procedure was applied at the time. An old `need` result may later be independently invalidated (as with KnowWork #4) without its old execution becoming `0.7.0` evidence.

## Releasing and tracing

1. Inspect current `main` and relevant source/authority PRs; group the changes and classify the SemVer bump.
2. Update `VERSION`, `CHANGELOG.md`, and the numbered change package together. Run the repository suite and the version consistency test.
3. Merge only after CI and normal review. Create one immutable lightweight `vX.Y.Z` Git tag at the **actual merged version commit**; do not move an existing version tag.
4. For historical reconstruction only, optional lightweight `vX.Y.Z` tags may instead pin the clearly disclosed retrospective historical checkpoints. Do not represent their tag creation as a historic release. If a tag cannot be created safely, keep the documented checkpoint SHA and do not imply it exists.
5. When troubleshooting a contribution, cite its actual execution/publication Git SHA and relevant current evidence alongside the nearest applicable **existing** protocol checkpoint. A historical snapshot label is not a substitute for proving what a runner or agent actually read.

No automatic tagging workflow, separate per-rule versioning system, schema migration or authority expansion is introduced by this policy.
