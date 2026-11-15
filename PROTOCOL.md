# Upstream contribution protocol — v0.12.0

[Home](README.md) · [Architecture](docs/ARCHITECTURE.md) · [Evidence](docs/EVIDENCE.md) · [Migration](docs/MIGRATION.md)

**One concrete opportunity, one durable issue; many sessions as needed.** This is an operating protocol for the existing [Upstream Contributions S1](https://github.com/opensiro/vsm-oss-organization/blob/main/contracts/s1/domain-contracts.md#upstream-contributions-domain), not a separate VSM organization, scheduler or autonomous runtime.

## The unit of work

A contribution case identifies one independently useful new user/operator action (or independently confirmed repair) in one original upstream source. It is owned by **one Upstream GitHub issue**. A repository can have distinct opportunities, but repeating a source probe, revisiting a past batch or changing SemVer does **not** create another case. A 40-minute chat is a work interval, not a completion criterion.

Each case keeps these answers readable: **what user task improves; what source evidence supports it; which exact fork/commit/test demonstrates it; and what action/decision happens next**. It may remain research-only or end as evidence-backed no-change.

## Research and qualification

1. Verify original repository, exact source revision, legal and contributor boundaries, existing behavior, competing PRs and existing Upstream cases (including [upstream-old](https://github.com/opensiro/upstream-old)).
2. First ask **who needs what NEW task/output and why** (or what existing behavior is demonstrably broken). Propose a bounded benefit proxy, original alternative and negative/compatibility control. A broken retry or compatibility fix is a repair, not automatically a feature.
3. Record chronology honestly: **ASSESSMENT_DERIVED** needs a dated, pinned Index-first prediction **before** fresh original-source investigation; **ASSESSMENT_INFORMED** is a supported but non-causal Index link; **GENERAL_UPSTREAM** is an ordinary source-first opportunity; **INSUFFICIENT** means the attribution is not established. A VSM ownership grade never proves product need.
4. Check native fit: **need, mechanism, counterfactual and scope** must each be supported before accepting a derivative implementation. Pending evidence stays pending; never make mock-only failures count as observed product defects. Relevant S1–S5 functions may inform the reasoning, but six independent tests per case are not an output quota.

## Implement and validate

Check the actual original repository, fork parent, license, branch SHA, writer rights and overlapping PRs **before expanding into target code**. Use a bounded disposable experiment only to answer a specific missing question. Real implementation and target native CI belong in the correctly parented **[opensiro-contributions/<target>](https://github.com/opensiro-contributions)** fork, not in this repository.

For a new feature, compare source-pinned original behavior to an actually new user action/output; for a repair, reproduce a reachable original failure. Run independent, original-project native before/after tests and a negative/compatibility control as appropriate. Link exact source/working SHA, commands, results and limitations from the same Upstream issue. When no trusted authenticated executor exists, report the exact blocker, not a fake branch or CI receipt.

## Deliver, observe, close

Use the target project's contributor requirements, PR template, licensing, CLA/DCO terms, exact verified diff and appropriate AI disclosure. External maintainer decisions remain external. Return review feedback and working-branch revisions to the **same case**; do not start another batch or issue just because a reviewer requested changes.

Record actual first-party disposition: prepared, proposed, merged, closed-unmerged, waiting, unverifiable, unsupported or source-proven no change. Distinguish native test success, external PR merge, deployment, adoption and measured user benefit. An external PR count or green CI alone is not an outcome metric.

At meaningful transitions, use the existing [Organization reporting contract](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/AUTONOMOUS_WORK_REPORTING.md): **DONE / NOW / BLOCKED / NEXT / NEED YOU**. Update the owning issue. The sole shared selection scheduler is [Organization TODO.md](https://github.com/opensiro/vsm-oss-organization/blob/main/TODO.md); no Upstream clone, extra agent scheduler, S2–S5 or VSM grading machinery is created.

## External-publication consent

The active restriction recorded in [upstream-old](https://github.com/opensiro/upstream-old/blob/main/docs/EXTERNAL_PUBLIC_COMMUNICATION_GATE.md) remains in effect: **before every third-party public issue/comment/reply/PR/review/design question or public fork-local proposal**, show the owner the exact external destination, specific action, complete final text and verified branch/diff when applicable, then obtain **explicit current-conversation approval for that action**. Materially different text, target or diff needs fresh approval. General `continue` instructions, prior broad mandates and passing tests are not permission.

Internal OpenSiro documentation/issue/PR work, read-only research and already independently authorized working branch preparation have separate rights. All external actions additionally require effective target/license/CLA/DCO/provider permissions. On missing approval or rights, record the blocker and **do not post publicly**.

## Historic protocol continuity

The prior contribution protocol reached **v0.11.0** in [upstream-old](https://github.com/opensiro/upstream-old). v0.12.0 changes the durable work unit from a frozen batch/revisit to a contribution issue, while retaining capability-first research, source-native evidence, early fork verification and exact external-consent requirements. It neither moves the old Git history nor upgrades frozen claims retroactively. [Migration](docs/MIGRATION.md).
