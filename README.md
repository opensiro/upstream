# OpenSiro Upstream

**Useful improvements to open-source AI harnesses, from evidence to external contribution.**

Upstream is the **operational S1 domain** of [OpenSiro VSM OSS](https://github.com/opensiro/vsm-oss-organization). It investigates improvements, tracks one durable contribution case per issue, links real code and native tests in [opensiro-contributions](https://github.com/opensiro-contributions), and reports verified outcomes. It does **not** implement a second VSM organization.

**Protocol:** [v0.12.0](VERSION) · [How work proceeds](PROTOCOL.md) · [Architecture](docs/ARCHITECTURE.md) · [History](CHANGELOG.md)

## One improvement, one issue

A 40-minute conversation is a **work session**, not a batch. One issue may span many chats, tests and review cycles. A batch is an optional way to execute searches in parallel, **not** a lasting work object; we do not reopen historical batches because a new protocol version appears.

| Step | Owner | Result |
| --- | --- | --- |
| 1. Find and qualify a genuinely useful opportunity | **[opensiro/upstream](https://github.com/opensiro/upstream/issues)** | One issue with the original-source need, evidence, optional VSM hypothesis and next decision |
| 2. Implement and validate in the target project | **[opensiro-contributions](https://github.com/opensiro-contributions)** | Correctly parented working fork, branch, native tests and SHA-linked receipts |
| 3. Propose and respond to maintainer feedback | **Original third-party repository** | External PR and first-party maintainer decision, only after specific external-publication approval |
| 4. Observe and close honestly | **[opensiro/upstream](https://github.com/opensiro/upstream)** | Same issue with verified PR disposition, evidence, actual benefit limits or reason for no change |

A case may close without a patch when source evidence shows duplication, disproves the need or exposes a legitimate blocker. An external merged PR does not automatically demonstrate deployed user benefit.

## Architecture: who owns what?

| Information | [Upstream](https://github.com/opensiro/upstream) | [opensiro-contributions](https://github.com/opensiro-contributions) | [VSM OSS](https://github.com/opensiro/vsm-oss-organization) |
| --- | --- | --- | --- |
| Task and state | **Owning issue** | Link | Current-work selection in [TODO.md](https://github.com/opensiro/vsm-oss-organization/blob/main/TODO.md) |
| VSM hypothesis and need | **Case and evidence links** | Reference | No duplicate canonical Index assessment |
| Code and native tests | Links and results | **Real source branch/tests** | No product code |
| Working branch | Verified link/SHA | **Original work** | No mirror |
| External PR | Link, observation, outcome | Source diff / branch | No second PR ledger |
| Outcomes and metrics | **Case evidence and accepted outcome source** | Reproducible technical proof | **Metric aggregation under [METRICS.md](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/METRICS.md)** |

[Read the complete architecture →](docs/ARCHITECTURE.md)

## For visitors

- [Current opportunities and contribution issues](https://github.com/opensiro/upstream/issues)
- [Propose one improvement](https://github.com/opensiro/upstream/issues/new/choose)
- [Contribution workspaces](https://github.com/opensiro-contributions) — the target-specific working forks
- [What counts as evidence?](docs/EVIDENCE.md)
- [Previous Upstream: opensiro/upstream-old](https://github.com/opensiro/upstream-old) — historical issues, PRs, batches, reports, workflows and **protocol through v0.11.0**; [migration guide](docs/MIGRATION.md)

**Metric continuity:** the existing verified-outcome scripts and historical records have **not** been migrated to this new repository. Until a validated source switch, do not label historical outputs as fresh Upstream metrics or treat missing current exporter data as zero.

## For agents and maintainers

Start from [Organization START_HERE](https://github.com/opensiro/vsm-oss-organization/blob/main/START_HERE.md) → [ECOSYSTEM](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/ECOSYSTEM.md) → [AGENTS.md](AGENTS.md) → the **exact issue**. [Contributing guide](CONTRIBUTING.md).

Conversational commands (not an installed CLI or background daemon): `upstream discover` · `upstream continue <issue URL>` · `upstream status`. The existing Organization [TODO.md](https://github.com/opensiro/vsm-oss-organization/blob/main/TODO.md) selects shared work; Upstream does **not** create a duplicate scheduler.

**External-public consent:** before any public third-party issue, comment, review, PR or public fork-local proposal, present the **exact destination, action, final content and diff** and obtain explicit approval in the current conversation, in addition to native/legal/provider gates. See [protocol](PROTOCOL.md#external-publication-consent) and [historical effective gate](https://github.com/opensiro/upstream-old/blob/main/docs/EXTERNAL_PUBLIC_COMMUNICATION_GATE.md). Generic authorization to continue is not specific external-publication consent.

The Profile, Skills and Index remain the owners of VSM semantics, assessment methodology and canonical results; Organization handles S2–S5 authority where established. No independent Upstream VSM control plane, autonomy grade or additional KPI is claimed.
