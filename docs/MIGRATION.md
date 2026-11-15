# Migration — upstream-old → new Upstream

[← Home](../README.md) · [Architecture](ARCHITECTURE.md) · [SemVer](../VERSIONING.md)

The former [opensiro/upstream](https://github.com/opensiro/upstream-old) repository was renamed **opensiro/upstream-old** on 2026-11-15. A fresh [opensiro/upstream](https://github.com/opensiro/upstream) now hosts **v0.13.0 aggregate-only operations and minimal intake**. [Migration programme #2](https://github.com/opensiro/upstream/issues/2) governs parallel history transfer into verified fork-local `.opensiro/` metadata.

| Responsibility | Location |
| --- | --- |
| Historical batches, research, issues, PRs, original evidence, automation, source registries | **[upstream-old](https://github.com/opensiro/upstream-old)** |
| Lean portfolio aggregate, pre-fork intake, migration coordination and prospective v0.13.0 protocol | **[upstream](https://github.com/opensiro/upstream)** |
| Working target code/native tests and OpenSiro `.opensiro/` event history on separate `opensiro/meta` branch | **[opensiro-contributions](https://github.com/opensiro-contributions)** |
| Existing VSM organizational control, shared selection and KPI contract | **[vsm-oss-organization](https://github.com/opensiro/vsm-oss-organization)** |

**Observed historical checkpoint:** [upstream-old main at `5e641ec9401b40800080791b2e490491522b1734`](https://github.com/opensiro/upstream-old/commit/5e641ec9401b40800080791b2e490491522b1734). This records a frozen *inspection point*, not a claim that the predecessor's still-open issues/PRs stopped moving.

## Links and case ownership

The former name is in use again. Old **issue #56 is [upstream-old #56](https://github.com/opensiro/upstream-old/issues/56)**, not `opensiro/upstream/issues/56`. The same applies to [old PR #303](https://github.com/opensiro/upstream-old/pull/303), its [historic v0.11.0 package](https://github.com/opensiro/upstream-old/blob/main/changes/v0.11.0.md), receipts and workflow references.

**No automatic migration of issues, PRs, frozen cohorts or fork metadata.** To resume an old case in the new workflow, explicitly determine its original owner, pinned source revision, concurrent work and next unsolved decision; use a verified fork-local `.opensiro/` contribution and event record when a real matching fork exists, or keep a **minimal** new intake/coordination issue before a fork exists; preserve original backreferences. Do not silently replace original case evidence with regenerated screenshots or invented new issue IDs.

## SemVer continuity

[upstream-old CHANGELOG](https://github.com/opensiro/upstream-old/blob/main/CHANGELOG.md) owns **0.1.0–0.11.0** and its original Git commits. Early packages through 0.6.0, including 0.5.1, were retrospectively assigned in the predecessor and are not historical contemporaneous Git releases. The new repository started at **prospective minor v0.12.0** for case-first contributions; **v0.13.0** changes detailed contribution ownership to fork-local metadata with Upstream aggregate-only reporting, retaining the relevant old 0.10.0 exact external consent and 0.11.0 working-fork requirements.

**Protocol succession is not Git ancestry:** this repository has fresh commits; old tags, issue numbering and version packages remain in upstream-old. An unverified `v0.12.0` tag must not be claimed as published merely because `VERSION` exists.

## Fork-local transfer and parallel migration

The target fork's **`opensiro/meta` branch** alone contains `.opensiro/state.json`, `.opensiro/contributions/<stable-id>.json` and append-only `.opensiro/events/<event-id>.json`; original default/product branches and external PR diffs remain clean. Fork identity must be independently verified before any metadata write. The **one-fork-per-worker shard** permits parallel transfers across different parent projects, with optimistic HEAD checks preventing conflicting writes to the same fork. No mandatory maintenance TTL is imposed; `ACTIVE/WATCHING/DORMANT/ARCHIVED` express our own discretionary attention, not GitHub PR outcomes or contractual support.

[Migration issue #2](https://github.com/opensiro/upstream/issues/2) requires a reviewed and deduplicated historical inventory before reporting any completion percentage. Stages `DISCOVERED/MAPPED/MATERIALIZED/RECONCILED/INDEXED` must be proved at precise source SHA, with separately visible `BLOCKED/UNMAPPED/UNKNOWN`. Do not treat published PR count or historical registry entries as verified fork count. The new repository has no live exporter or migrated per-fork logs yet; do not claim them by adding this doc. See [fork metadata contract](FORK_METADATA.md).

## Integration steps and unfinished boundaries

1. Update Organization links to old issues/PRs/scripts/policies so they point to **upstream-old**; its new-work references should point to **upstream**.
2. Preserve real old issue/PR maintenance and source pinning; moving its README or file layout does not transfer external maintainer obligations.
3. **Outcome collector not migrated yet.** The historical accepted-export generator, evidence ledgers and observation workflows are still in upstream-old. Organization `verified_external_outcomes` must remain **unclaimed** when fresh validation from the declared source cannot run, never silently zero. A production source switch needs a separately tested provenance-/digest-preserving adapter and an atomic update to [metrics.yaml](https://github.com/opensiro/vsm-oss-organization/blob/main/metrics.yaml).
4. Verify individual target forks' actual parent/visibility/branch rights and contributor rules on GitHub. The [opensiro-contributions](https://github.com/opensiro-contributions) organization URL does not certify that every desired fork exists. Do not rewrite original target product READMEs as part of governance synchronization.

This note is **not a receipt for a completed data migration**, a new scheduler, a VSM assessment, or a release of external communication rights.
