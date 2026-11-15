# Upstream contribution-protocol changelog

**Current protocol:** [v0.13.0](VERSION) · [Versioning](VERSIONING.md) · [Migration](docs/MIGRATION.md).

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
