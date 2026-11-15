# Migration — upstream-old → new Upstream

[← Home](../README.md) · [Architecture](ARCHITECTURE.md) · [SemVer](../VERSIONING.md)

The former [opensiro/upstream](https://github.com/opensiro/upstream-old) repository was renamed **opensiro/upstream-old** on 2026-11-15. A fresh [opensiro/upstream](https://github.com/opensiro/upstream) now hosts **prospective case-first contribution work**.

| Responsibility | Location |
| --- | --- |
| Historical batches, research, issues, PRs, original evidence, automation, source registries | **[upstream-old](https://github.com/opensiro/upstream-old)** |
| New contribution issues and prospective v0.12.0 protocol | **[upstream](https://github.com/opensiro/upstream)** |
| Working target code, native tests, fork-local branches | **[opensiro-contributions](https://github.com/opensiro-contributions)** |
| Existing VSM organizational control, shared selection and KPI contract | **[vsm-oss-organization](https://github.com/opensiro/vsm-oss-organization)** |

**Observed historical checkpoint:** [upstream-old main at `5e641ec9401b40800080791b2e490491522b1734`](https://github.com/opensiro/upstream-old/commit/5e641ec9401b40800080791b2e490491522b1734). This records a frozen *inspection point*, not a claim that the predecessor's still-open issues/PRs stopped moving.

## Links and case ownership

The former name is in use again. Old **issue #56 is [upstream-old #56](https://github.com/opensiro/upstream-old/issues/56)**, not `opensiro/upstream/issues/56`. The same applies to [old PR #303](https://github.com/opensiro/upstream-old/pull/303), its [historic v0.11.0 package](https://github.com/opensiro/upstream-old/blob/main/changes/v0.11.0.md), receipts and workflow references.

**No automatic migration of issues, PRs or frozen cohorts.** To resume an old case in the new workflow, explicitly determine its original owner, pinned source revision, concurrent work and next unsolved decision; create a linked new issue *only when an intentional handoff is needed*, preserving backreferences. Do not silently replace original case evidence with regenerated screenshots or invented new issue IDs.

## SemVer continuity

[upstream-old CHANGELOG](https://github.com/opensiro/upstream-old/blob/main/CHANGELOG.md) owns **0.1.0–0.11.0** and its original Git commits. Early packages through 0.6.0, including 0.5.1, were retrospectively assigned in the predecessor and are not historical contemporaneous Git releases. The new repository starts a **prospective minor v0.12.0** for case-first contributions, retaining the relevant old 0.10.0 exact external consent and 0.11.0 working-fork requirements.

**Protocol succession is not Git ancestry:** this repository has fresh commits; old tags, issue numbering and version packages remain in upstream-old. An unverified `v0.12.0` tag must not be claimed as published merely because `VERSION` exists.

## Integration steps and unfinished boundaries

1. Update Organization links to old issues/PRs/scripts/policies so they point to **upstream-old**; its new-work references should point to **upstream**.
2. Preserve real old issue/PR maintenance and source pinning; moving its README or file layout does not transfer external maintainer obligations.
3. **Outcome collector not migrated yet.** The historical accepted-export generator, evidence ledgers and observation workflows are still in upstream-old. Organization `verified_external_outcomes` must remain **unclaimed** when fresh validation from the declared source cannot run, never silently zero. A production source switch needs a separately tested provenance-/digest-preserving adapter and an atomic update to [metrics.yaml](https://github.com/opensiro/vsm-oss-organization/blob/main/metrics.yaml).
4. Verify individual target forks' actual parent/visibility/branch rights and contributor rules on GitHub. The [opensiro-contributions](https://github.com/opensiro-contributions) organization URL does not certify that every desired fork exists. Do not rewrite original target product READMEs as part of governance synchronization.

This note is **not a receipt for a completed data migration**, a new scheduler, a VSM assessment, or a release of external communication rights.
