# OpenSiro Upstream

**Find useful improvements. Keep the working history with the harness. View the portfolio in one place.**

## I'm human

- **I don't understand any of this:** [Show me the visual map](https://opensiro.com/vsm.html) — a direct, illustrated introduction to the VSM approach.
- **Web overview:** [opensiro.com](https://opensiro.com)
- **How do I contribute?** [Contribute to OpenSiro with AI](https://github.com/opensiro/vsm-oss-organization/blob/main/CONTRIBUTE_WITH_AI.md)
- **Contribution protocol:** [How Upstream works](PROTOCOL.md)
- **Published versions:** [GitHub Releases](https://github.com/opensiro/upstream/releases)

You can follow a real improvement from source-backed investigation to an external PR and its observed status without learning the internal OpenSiro control structure. The contribution guide provides a copy-paste route for working with an AI agent.

## I'm AI

Treat this README as the public handoff surface, then continue with the current shared [`START_HERE.md`](https://github.com/opensiro/vsm-oss-organization/blob/main/START_HERE.md). For already tracked work use shared [`TODO.md`](https://github.com/opensiro/vsm-oss-organization/blob/main/TODO.md); for new, unclassified, cross-repository or authority-sensitive work use [`CONTRIBUTOR_START.md`](https://github.com/opensiro/vsm-oss-organization/blob/main/CONTRIBUTOR_START.md).

If the bootstrap resolves Upstream work here, [`AGENTS.md`](AGENTS.md), [`PROTOCOL.md`](PROTOCOL.md), and [`docs/FORK_METADATA.md`](docs/FORK_METADATA.md) govern local contribution workflow. Verified fork-local `.opensiro/` records, original third-party sources, and external PR facts remain authoritative in their respective owners. External-publication consent is required for each specific third-party action; this README grants no additional permission.

Upstream is the **operational S1 domain** of [OpenSiro VSM OSS](https://github.com/opensiro/vsm-oss-organization). It coordinates source-backed contributions to external AI harnesses without implementing a second VSM organization.

**Protocol:** [v0.14.0](VERSION) · [How work proceeds](PROTOCOL.md) · [Fork metadata](docs/FORK_METADATA.md) · [Architecture](docs/ARCHITECTURE.md) · [History](CHANGELOG.md) · [Releases](https://github.com/opensiro/upstream/releases)

## Releases

[GitHub Releases](https://github.com/opensiro/upstream/releases) publish tagged snapshots of the **Upstream contribution protocol**, not releases of third-party harnesses. The current protocol is [v0.14.0](VERSION); see its [change package](changes/v0.14.0.md), [changelog](CHANGELOG.md), and [versioning rules](VERSIONING.md). A release does **not** certify completion of historical migration, deployed value, external PR acceptance, or VSM autonomy.

The new repository started its own history with v0.12.0. The predecessor's v0.1.0–v0.11.0 history stays with [upstream-old](https://github.com/opensiro/upstream-old/blob/main/CHANGELOG.md); no tags or GitHub Releases are implied for that old history.

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

## External PR activity (dated snapshot)

![External PR activity calendar](docs/activity.svg)

As of **2026-11-16 12:00 UTC**, the **42 distinct original-repository PRs** linked from 61 migrated improvement records: **11 merged**, **24 open**, **7 closed without merge**, of which **0** have an explicit GitHub `APPROVED` review. These categories are **source-observed PR lifecycle facts**, not independent-improvement counts or deployed-benefit claims.

[Full dated statistics, coverage and on-demand refresh instructions](docs/ACTIVITY.md). The calendar reflects original PR events, not metadata backfill commits; the SVG is a static, manually refreshable view, **not a live counter**.

## Capability-first upstream upgrade

`upstream upgrade` is a **conversation route for discovering a genuinely new harness capability** — a user/operator trigger, action/decision and observable output, not merely a repair with a VSM label. Use existing `.opensiro/` history, the read-only aggregate, current original GitHub issues/PRs and independently testable native counterfactuals before proposing implementation.

| Route | Meaning |
| --- | --- |
| `upstream upgrade` | Deeply investigate **one** promising new-capability question; no new batch |
| `upstream upgrade OWNER/REPO` or `upstream upgrade <contribution-id>` | Inspect/continue a specific original harness or stable contribution record |
| `upstream upgrade batch 10` | **Ten distinct original harnesses**, S1/S2/S3/S3*/S4/S5 source-backed dispositions each, focused native tests only where needed; **not** ten PRs, fixes or a new frozen cohort |
| `upstream batch [N]` | Separate technical/repair screening mode; it is not an alias for `upgrade` |

All modes are **operator phrases, not executable CLI commands**. Functional opportunity, VSM/Index chronology, need/mechanism/counterfactual/scope, original-work alternative and native benefit must be distinguished. `DORMANT / PAUSE` allows no automatic engineering restart, and outward public third-party communication still requires exact current-conversation owner approval. [v0.14.0 upgrade procedure](PROTOCOL.md#capability-first-upstream-upgrade-new-work-not-historical-batching).

## Read-only portfolio aggregation

A **one-shot, read-only** standard-library Python tool now derives a source-linked view from verified `opensiro-contributions/*` forks' `opensiro/meta` branches. It reads `.opensiro/state.json`, `.opensiro/contributions/*.json`, and the **original external repositories' live PR APIs**. Nothing is written back to forks, original PRs or Upstream; no scheduled sync, background service, extra ledger or mandatory maintenance TTL.

```bash
# Read two already verified pilot forks
python3 scripts/aggregate.py --format markdown \\
  --repo opensiro-contributions/Citadel \\
  --repo opensiro-contributions/agent-fleet

# Entire accessible public organization (can require authenticated API quota)
GH_TOKEN=... python3 scripts/aggregate.py --format json > snapshot.json

# On-demand state changes between two independently captured observations
python3 scripts/aggregate.py --format markdown --compare snapshot.json

# Alternative read-only views
python3 scripts/aggregate.py --format csv
python3 scripts/aggregate.py --only-active --format markdown
python3 scripts/aggregate.py --no-prs --format json
```

`--format` is `json`, `markdown` or `csv`. `--repo` may be repeated to limit API reads; `--only-active` filters out WATCHING/DORMANT/ARCHIVED, **not** the current GitHub status of their PRs. The CLI reads an optional `GH_TOKEN` or `GITHUB_TOKEN` environment variable (never embeds it in output). A first-party external PR with `state=closed` and non-null `merged_at` is `MERGED`; closed without `merged_at` is `CLOSED_UNMERGED`; open (including draft) is `OPEN`; lookup failures and unverified links are `UNKNOWN`. The JSON output includes an observation timestamp and exact fork meta HEAD/blob SHAs. `--compare` reports known PR-status transitions relative to an earlier saved JSON report; it does not create an ongoing change log.

**Coverage caveat:** this is a **partial, metadata-backed portfolio projection**, not a reconstruction of the entire `upstream-old` portfolio. A source project without `opensiro/meta` is counted as missing metadata, **not** as having no contributions; historical inventory completion and deployed usefulness are not claimed. GitHub API failures remain explicit warnings, and incomplete scans exit nonzero. A merged PR alone is not a verified benefit or the Organization's `verified_external_outcomes` KPI.

## For operators and agents

Start from [Organization START_HERE](https://github.com/opensiro/vsm-oss-organization/blob/main/START_HERE.md) → [ECOSYSTEM](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/ECOSYSTEM.md) → [AGENTS.md](AGENTS.md), the original source and the verified fork meta branch. Use [Organization TODO.md](https://github.com/opensiro/vsm-oss-organization/blob/main/TODO.md) for shared selection; never create a second scheduler. `upstream discover` / `upstream continue <source or contribution>` / `upstream status` are **conversational routes**, not installed commands or an autonomous service.

**External-public consent:** before any outward public third-party issue/comment/review/PR or public fork-local proposal, show the owner the exact target/action/final content and verified diff, and obtain explicit current-conversation consent. The [active protocol gate](PROTOCOL.md#external-publication-consent) preserves the [historical gate](https://github.com/opensiro/upstream-old/blob/main/docs/EXTERNAL_PUBLIC_COMMUNICATION_GATE.md). Neither this internal architecture approval nor passing tests grants external publication/CLA/merge rights.

## Migration and accuracy

Previous batches, issues, original evidence, registries, watcher scripts and protocol through v0.11.0 belong to [opensiro/upstream-old](https://github.com/opensiro/upstream-old). [Migration guide](docs/MIGRATION.md) · [migration programme #2](https://github.com/opensiro/upstream/issues/2).

**Migration status (2026-11-16):** the bounded one-time historical backfill is [closed with a source-linked reconciliation](https://github.com/opensiro/upstream/issues/2): 60 verified fork-local metadata destinations, 61 distinct contribution records, and explicit security/unmapped/skipped exceptions. This does **not** assert exhaustive migration of research-only history. The live outcome exporter and website sync are **not migrated**. Current Organization `verified_external_outcomes` is **unclaimed for this new source**, not zero. No migration percentage or live PR inventory is claimed merely because v0.13.0 docs exist. Old and new evidence must not be silently mixed.
