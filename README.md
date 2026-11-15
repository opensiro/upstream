# OpenSiro Upstream

**Find useful improvements. Keep the working history with the harness. View the portfolio in one place.**

Upstream is the **operational S1 domain** of [OpenSiro VSM OSS](https://github.com/opensiro/vsm-oss-organization). It coordinates source-backed contributions to external AI harnesses without implementing a second VSM organization.

**Protocol:** [v0.13.0](VERSION) · [How work proceeds](PROTOCOL.md) · [Fork metadata](docs/FORK_METADATA.md) · [Architecture](docs/ARCHITECTURE.md) · [History](CHANGELOG.md)

## How it works

1. **Find:** establish an original-source need and decide whether to explore a real improvement.
2. **Improve:** implement and run native tests in a verified [opensiro-contributions](https://github.com/opensiro-contributions) working fork.
3. **Offer:** submit an external PR after the exact required approval; original maintainers decide what to merge.
4. **Observe:** read the original PR status and update the related fork-local record. OpenSiro may keep working, watch, go dormant or archive the project; no compulsory maintenance TTL.

The human view is **what happened, what is happening, what is next, and can I pause it?** Each fork stores detailed records in `.opensiro/` on its **separate `opensiro/meta` branch**, never in product/default/external PR branches.

## Architecture: who owns what?

| Data | Source of truth | What Upstream presents |
| --- | --- | --- |
| Original product behavior and external PR reviews/merge status | Original upstream GitHub repository | Source-linked, dated live PR observation |
| Working product code, native tests and branch commits | [opensiro-contributions](https://github.com/opensiro-contributions) matching fork | Links and status |
| OpenSiro attention, each improvement, decisions and operational transaction history | **`.opensiro/` on fork `opensiro/meta`** | **Lightweight derived aggregate**, not copied logs |
| Pre-fork intake / exceptional cross-fork migration decisions | A minimal Upstream issue | Research or coordination link, without pretending a fork exists |
| Organization-wide selected work, S2–S5 and metrics contract | [VSM OSS Organization](https://github.com/opensiro/vsm-oss-organization) | No duplicate scheduler, VSM control plane or KPI |

[Full architecture](docs/ARCHITECTURE.md) · [Fork-local structure and owner STOP/RESUME](docs/FORK_METADATA.md) · [Migration programme #2](https://github.com/opensiro/upstream/issues/2)

## Human intervention and attention

Fork-level attention: `ACTIVE` / `WATCHING` / `DORMANT` / `ARCHIVED`. These describe **our discretionary effort**, not the external PR. A project may be dormant indefinitely and may be reactivated. A human's `PAUSE` / `STOP` / `RESUME` decision is an attributable fork-local event; the executor must check it **before a new effectful step**. A committed file does not instantly kill an already executing process.

**PR status** is a separate, source-owned observation: `OPEN` (including draft as a qualifier), `MERGED`, `CLOSED_UNMERGED` or `UNKNOWN`. Green tests, a merge or an accepted PR do not alone prove deployed user value. We presently prioritize this simple public PR lifecycle telemetry; no public usefulness score has been established.

## For operators and agents

Start from [Organization START_HERE](https://github.com/opensiro/vsm-oss-organization/blob/main/START_HERE.md) → [ECOSYSTEM](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/ECOSYSTEM.md) → [AGENTS.md](AGENTS.md), the original source and the verified fork meta branch. Use [Organization TODO.md](https://github.com/opensiro/vsm-oss-organization/blob/main/TODO.md) for shared selection; never create a second scheduler. `upstream discover` / `upstream continue <source or contribution>` / `upstream status` are **conversational routes**, not installed commands or an autonomous service.

**External-public consent:** before any outward public third-party issue/comment/review/PR or public fork-local proposal, show the owner the exact target/action/final content and verified diff, and obtain explicit current-conversation consent. The [active protocol gate](PROTOCOL.md#external-publication-consent) preserves the [historical gate](https://github.com/opensiro/upstream-old/blob/main/docs/EXTERNAL_PUBLIC_COMMUNICATION_GATE.md). Neither this internal architecture approval nor passing tests grants external publication/CLA/merge rights.

## Migration and accuracy

Previous batches, issues, original evidence, registries, watcher scripts and protocol through v0.11.0 belong to [opensiro/upstream-old](https://github.com/opensiro/upstream-old). [Migration guide](docs/MIGRATION.md) · [migration programme #2](https://github.com/opensiro/upstream/issues/2).

**Not yet migrated:** real fork-local `.opensiro/` records, validated aggregate/PR observer, historical accepted-export producers and website sync. Current Organization `verified_external_outcomes` is **unclaimed for this new source**, not zero. No migration percentage or live PR inventory is claimed merely because v0.13.0 docs exist. Old and new evidence must not be silently mixed.
