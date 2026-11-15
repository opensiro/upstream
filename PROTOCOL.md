# Upstream contribution protocol — v0.13.0

[Home](README.md) · [Fork-local records](docs/FORK_METADATA.md) · [Architecture](docs/ARCHITECTURE.md) · [Historical migration #2](https://github.com/opensiro/upstream/issues/2)

**One harness may have many independent improvements. The detailed operational state belongs to its verified working fork, not a pile of permanent Upstream issues.** No fixed maintenance TTL is imposed. Upstream is an existing S1 domain of OpenSiro VSM OSS, not a second organizational control plane.

## Ownership and work unit

Before a real fork exists, Upstream may own one **minimal intake issue** containing a real source identity, open decision and evidence links; source-proven negative findings need no invented fork or patch. Once a correct [opensiro-contributions](https://github.com/opensiro-contributions) fork is verified, use `.opensiro/` on its independent `opensiro/meta` branch as the **canonical local state and attributed decision/event history** for all that harness's contributions. One `contributions/<stable-id>.json` = one independently scoped useful improvement/repair, not an issue, chat session, old batch, external PR or mandatory new issue. An Upstream issue may remain as a link/operator task, never an authoritative duplicate mutable ledger.

Read [docs/FORK_METADATA.md](docs/FORK_METADATA.md) for the initial JSON contract and authority/branch rules. The original GitHub repository alone owns the actual external PR's open/merge/closure/reviews. Upstream only shows source-linked dated projections.

## Research and qualification

1. Verify original repository identity and exact source revision, license, contributor rules, existing behavior, competing PRs, and prior source links including [upstream-old](https://github.com/opensiro/upstream-old).
2. Ask **who needs what NEW task/output and why**, or which existing behavior is demonstrably broken. Propose a bounded benefit proxy and original alternative. A retry fix remains a repair unless a new feature is independently supported.
3. Respect provenance order: `ASSESSMENT_DERIVED` requires an earlier dated and pinned Index-first prediction; `ASSESSMENT_INFORMED`, `GENERAL_UPSTREAM` and `INSUFFICIENT` must not be misrepresented as causal VSM improvements.
4. Check native **need, mechanism, counterfactual and scope**. Unsupported claims remain pending. No mandatory six-function S1–S5 scan or per-session batch.

## Implement and validate

Inspect original source, actual fork `parent.full_name`, default branch, license/CLA/DCO, branch SHA, contributor rights and overlapping PRs before source changes. The fork has **separate work branches for product code and `opensiro/meta` for OpenSiro-only evidence and events**; never include `.opensiro/` in the original project's PR diff. Don't edit upstream README or CI for OpenSiro metadata. The metadata branch itself must be protected against lost updates through optimistic HEAD checks and one-writer-per-fork coordination.

Demonstrate feature behavior in the original native stack with source-pinned baseline/after evidence and appropriate negative/compatibility control; for a repair, reproduce a real reachable original failure. Record exact fork/source SHA, test commands, result and limitations as links; large raw logs stay in their original technical owner, never copied to Upstream. If a fork cannot be verified, preserve a minimal blocker at intake; do not pretend a branch or passing CI exists.

## Deliver, observe, choose attention

Use the original PR template, policy and AI disclosure. Before outreach follow [External-publication consent](#external-publication-consent). A specific original/replacement PR chain maps to the **same contribution ID**. Source-owned external status is one of `OPEN`, `MERGED`, `CLOSED_UNMERGED`, `UNKNOWN`, with separate draft/review/CI qualifiers. Never interpret closed-unmerged as disproved usefulness or merged as measured deployed benefit.

Maintain the independent fork **attention** setting `ACTIVE`, `WATCHING`, `DORMANT`, `ARCHIVED`. These are elective, reversible choices about whether to perform engineering or scheduled observation; not a maintenance commitment or TTL. State/decision changes and human `PAUSE`, `STOP`, `RESUME` are attributed **significant** events in the fork metadata. A cooperating executor must re-read owner control and effective authority before every new effectful step. Writing STOP does not cancel already-running processes.

At meaningful transitions report existing Organization **DONE / NOW / BLOCKED / NEXT / NEED YOU**. The owner controls cross-repository selection from [Organization TODO.md](https://github.com/opensiro/vsm-oss-organization/blob/main/TODO.md). Upstream is a **rebuildable aggregate** from fork metadata at verified SHA and current first-party external PR reads, not another event store, task scheduler or second VSM. When no data or live readback is available, report **UNKNOWN**, not success/zero.

## External-publication consent

The [historical effective restriction](https://github.com/opensiro/upstream-old/blob/main/docs/EXTERNAL_PUBLIC_COMMUNICATION_GATE.md) still applies: **before every public third-party issue/comment/reply/PR/review/design question or public fork-local proposal**, present exact destination, specific action, final public text and verified code diff as applicable and obtain explicit current-conversation consent. Significant content or destination changes need renewed consent. General permission to continue, internal documentation approval, a metadata event or passing tests is not consent.

Internal OpenSiro research/doc/issues/PRs and independently authorized working branch preparation follow their own grants. Third-party external actions also require legal/CLA/DCO/provider permissions and actual executor rights. Record missing permission as blocked; do not post.

## Migration and metrics

The predecessor protocol through v0.11.0 and frozen original historical sources live in [upstream-old](https://github.com/opensiro/upstream-old). v0.12.0 case-first Upstream issues remain valid historical coordination records; **v0.13.0 moves detailed ownership to fork-local metadata**, and [migration #2](https://github.com/opensiro/upstream/issues/2) covers reviewed per-fork parallel extraction and status progress. Do not rewrite historical evidence or assume a fork exists.

The current Organization `verified_external_outcomes` accepted-merge export remains **unclaimed** for the new source until separate verified semantic/collector cutover. PR state is descriptive public telemetry, not a proof of independent usefulness. Protocol SemVer is not a deployment or autonomy grade.
