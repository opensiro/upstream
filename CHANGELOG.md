# Upstream contribution-protocol changelog

**Current protocol:** [v0.16.0](VERSION) · [Versioning](VERSIONING.md) · [Migration](docs/MIGRATION.md).

**Release status:** a protocol version merged to `main` is **not** automatically a published GitHub Release. Check [published Releases](https://github.com/opensiro/upstream/releases). At the 2026-11-16 review, v0.13.0 was the latest published release, and the [v0.16.0 consolidated candidate](docs/RELEASE_CANDIDATE_v0.16.0.md) awaits final owner approval. Individual v0.14–v0.16 history entries below remain valid intermediate main snapshots, not claims of three separate GitHub Releases.

## Unreleased

**Single-harness Upgrade scope and fork-local PR review (unreleased):** The default `upstream upgrade` now **selects exactly one original harness** (or uses the explicitly named source) and stays there for all qualification attempts; it does not fall back to another repository after a failed hypothesis, missing meta branch or human CLA gate. A truthful source-local no-change/blocker is valid. End-to-end qualified work must prepare a human-visible **review PR in the matching `opensiro-contributions` fork**, with original-template PR title/body, exact code diff, native tests and current assessment-linked AI disclosure; the external PR is a separate later approval. Public fork-local proposal creation itself still needs exact current-conversation consent; without that, a read-only compare plus complete draft is the permitted handoff. The former historical v3 disclosure text claiming no per-PR approval is **not** copied into new publications. A concrete example needing a separately approved description correction is `browser-use/browser-harness#1034`. Batch screening remains chat-scoped, and no new SemVer/package/release or universal autonomous runner is claimed.

Compatible operating-rule changes accumulate here under review without an automatic SemVer bump for every PR. A coherent owner-approved bundle receives one final version/change package and one verified release, following [VERSIONING.md](VERSIONING.md).

## [0.16.0](changes/v0.16.0.md) — License/formalities-first admission, deferred human availability decisions

**Prospective MINOR, 2026-11-16.** Before contributor-popularity ranking, run the existing read-only source-pinned license, CLA/DCO and contributor-formality preflight. Distinguish screenable **read-only** research from unresolved rights/access and insufficient evidence, without auto-granting a license or claiming that GitHub access is cleared. New separate internal **Human gate — license, formalities & availability** issue form records only genuine deduplicated human decisions; chat batches still create no issues/PRs by default. [Protocol](PROTOCOL.md#license-and-formalities-first--human-gate-category).

## [0.15.0](changes/v0.15.0.md) — Popularity-first selection and chat-only batch reporting

**Prospective MINOR, 2026-11-16.** Default selections favor original harnesses with more unique GitHub contributors (stars only as a labeled fallback). Initial research coverage is breadth-first, then additional opportunities can receive a modest linear 1×–2× popularity preference or remain uniformly distributed on operator request; no contribution/PR quota. `upstream batch N` and `upstream upgrade batch N` produce **chat reports** without new per-batch issues, PRs, frozen manifests or schedulers. Reuse historical v0.8/v0.9 capability-first native testing, v0.11 fork handoff and independent CI receipts, respecting owner controls and exact external publication consent. [Protocol](PROTOCOL.md#default-popularity-priority--no-contribution-quota).

## [0.14.0](changes/v0.14.0.md) — Capability-first upstream upgrade

**Prospective MINOR, 2026-11-16.** `upstream upgrade` now selects demonstrable new harness user/operator capabilities, not frozen batches or bug-fix quotas. `upstream upgrade batch N` explicitly covers N distinct original repositories with S1/S2/S3/S3*/S4/S5 source-backed dispositions; native investigations concentrate on credible functional needs instead of six forced product experiments. `upstream batch [N]` remains a distinct technical/repair route. Historical Index-first chronology, live original PR readbacks, fork-local `PAUSE`/`STOP`, external communication consent and source-native benefit controls remain in force. [Procedure](PROTOCOL.md#capability-first-upstream-upgrade-new-work-not-historical-batching).

## [0.13.0](changes/v0.13.0.md) — Fork-local metadata and aggregate-only Upstream

**Prospective MINOR, 2026-11-15.** Approved source-of-truth switch: detailed per-harness attention, contribution records and attributable events live in `.opensiro/` on a verified target fork's separate `opensiro/meta` branch. Upstream aggregates rather than mirroring logs or requiring one issue per contribution. No mandatory maintenance TTL, and external PR status still comes from the original GitHub source. [Fork metadata](docs/FORK_METADATA.md) · [parallel legacy migration #2](https://github.com/opensiro/upstream/issues/2). Normative docs only; physical migration, validator and live observer remain unfinished.

## [0.12.0](changes/v0.12.0.md) — One improvement, one durable case

**Prospective MINOR, 2026-11-15.** A case-first operating workflow replaces frozen batch/revisit sequences as the normal unit of work. Research, implementation, external delivery and verified-outcome reporting remain source-linked and persistent across sessions. Working code belongs in the target-specific [opensiro-contributions](https://github.com/opensiro-contributions) fork; Organization [TODO.md](https://github.com/opensiro/vsm-oss-organization/blob/main/TODO.md) and S1–S5 authority remain in existing VSM OSS control. Source-native evidence, early working-fork verification and exact external-publication approval are retained. No new KPI or executor is created.

## History before the repository split

The predecessor [upstream-old CHANGELOG](https://github.com/opensiro/upstream-old/blob/main/CHANGELOG.md) is the source of truth for **0.1.0–0.11.0**, its actual commits, change packages and their historical interpretation:

- [v0.11.0 — working-fork handoff](https://github.com/opensiro/upstream-old/blob/main/changes/v0.11.0.md)
- [v0.10.0 — explicit exact external-publication approval](https://github.com/opensiro/upstream-old/blob/main/changes/v0.10.0.md)
- [v0.9.0 — capability-first research](https://github.com/opensiro/upstream-old/blob/main/changes/v0.9.0.md)

Early v0.1.0–v0.6.0 packages were historically reconstructed, not contemporaneous releases. The new repository does not claim the old Git graph or any old tag was transferred.
