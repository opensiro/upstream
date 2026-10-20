# Index six-function improvement sweep — Batch 003 (ten systems)

**Date:** 2026-10-21. **Owning route:** [Upstream #56](https://github.com/opensiro/upstream/issues/56) / [Draft PR #67](https://github.com/opensiro/upstream/pull/67). **Frozen Index:** [main@5393b698bfdfa4ca14d97a79238234eca20694e5](https://github.com/opensiro/vsm-harness-index/tree/5393b698bfdfa4ca14d97a79238234eca20694e5). Input is exactly the next **ten previously unscreened included** assessments after [Batch 002](2026-10-21-index-sweep-batch-002.md), in deterministic path order.

The review read each system's **S1 / S2 / S3 / S3* / S4 / S5** function descriptions at its original Index assessed source pin; each has an independent six-function [receipt](../sweeps/README.md). Target public default HEAD and current open issue signals were queried before opening native-candidate records. This is **bounded hypothesis discovery**, not a complete independent audit of the target's current source, a native executable baseline test, or a VSM reassessment.

## System-by-system decisions

| Index included system / per-function receipt | Current target SHA (short) | Native screen / hypotheses |
| --- | --- | --- |
| [Agency OS](../sweeps/agency-os.json) — `A/C/?/?/?/?` | `010d216b` | Atomic conditional claim prevents duplicate task execution (positive S2). [Open issue #26](https://github.com/swarm-ai-research/agency-os/issues/26) concerns missing CI runner, not a proved operator-S3/S4/S5 defect; **0 native candidates**. The `?` labels stay unchanged. |
| [Agency Swarm](../sweeps/agency-swarm.json) — `A/—/—/—/—/—` | `a86d657e` | **1 independently sourced candidate:** [unexpected trace endpoint egress](../candidates/agency-swarm-tracing-endpoint-20261021.md), grounded in [upstream #828](https://github.com/VRSEN/agency-swarm/issues/828). It is **ASSESSMENT_INFORMED**; model endpoint-vs-trace integration is not an Index S2 or S5 diagnosis. |
| [agent-code](../sweeps/agent-code.json) — `A/—/—/—/—/—` | `82e0edfa` | **2 independent candidates.** [Isolated reviewer](../candidates/agent-code-isolated-reviewer-20261021.md) is **ASSESSMENT_DERIVED at hypothesis level**: the Index explicitly finds no independent complementary audit and [upstream #524](https://github.com/avala-ai/agent-code/issues/524) asks for one. **Important partial implementation:** current code already has `/review` targets and rubric from #529; the only remaining plausible gap is fresh-context, constrained, read-only subagent execution and returned findings. [Background output collision](../candidates/agent-code-background-output-20261021.md) is **ASSESSMENT_INFORMED**: issue [#515](https://github.com/avala-ai/agent-code/issues/515) identifies process-global `<task-id>.out` collisions; current source confirms each TaskManager starts its counter at 1 and paths are shared. |
| [Agent Context Lab](../sweeps/agent-context-lab.json) — `A/—/—/—/—/—` | `372ecc51` | Single coding-task runner has independent evidence checklist on completion, but it is a local task gate, not a separate whole-system audit. No specific upstream product request observed: **0 candidates**. |
| [Agent Fleet](../sweeps/agent-fleet-chankov.json) — `A/C/A/A/P/—` | `1d846daf` | Existing writer lease, model hub's S3 coordination, read-only reviewer and human-parent approved compound learning provide substantial **positive** functionality; **0 additional candidates** from this bounded screen. |
| [Agent Harness Core](../sweeps/agent-harness-core.json) — `A/C/A/—/—/—` | `1e247e06` | **1 separately issue-backed candidate:** [direct-owner backoff/restart deadlock](../candidates/agent-harness-core-backoff-restart-20261021.md) documented in [upstream #22](https://github.com/phenomenoner/agent-harness-core/issues/22), with source vocabulary `backoff` vs `restart-backoff`. **ASSESSMENT_INFORMED**, not diagnosed S2/S3 failure. |
| [Agent Harness (0xenzyme)](../sweeps/agent-harness.json) — `A/?/A/?/—/—` | `386132c9` | Optional worker isolation and reviewer independence are unresolved at the original boundary, but no proven current first-party native defect or request to address; **0 candidates**. |
| [Agent Laboratory](../sweeps/agent-laboratory.json) — `A/—/—/?/A(P)/—` | `d9017d90` | Reviewer-to-correction closure is uncertain; [issue #103](https://github.com/SamuelSchmidgall/AgentLaboratory/issues/103) reports missing manuscript sections but without an evidenced link to reviewer code or a reproducer; **0 justified candidates** from this bound. |
| [agent-loop](../sweeps/agent-loop.json) — `A/—/—/—/—/—` | `49525dc1` | One telemetry-task loop, numeric self-verification and no open native issue in bounded check; **0 candidates**. |
| [Agent Orchestrator (mohamedwaleed)](../sweeps/agent-orchestrator-mohamedwaleed.json) — `A/C/P/—/—/—` | `5445af14` | Task-wave, worktree separation and human merge gate already exist. [Issue #16](https://github.com/mohamedwaleed/agent-orchestrator/issues/16) confirms conflict detection already implemented, leaving follow-ups on redo/attach and status sync; **no duplicate proposal**. |

No missing VSM grade was treated as automatic product improvement. Some `REVIEWED_ZERO` statuses explicitly mean **the bounded screen did not establish a specific fix**, not the system is defect-free or all possible features have been tested.

## Source and attribution

Review receipts retain the **assessed** `review_ref`, distinct from the **current upstream HEAD**. The algorithm checks that every linked candidate has matching canonical assessment path, immutable reviewed SHA, target source identity and Index SHA. The targets above were inspected for current public branch and open issue surfaces. For agent-code the [review command](https://github.com/avala-ai/agent-code/blob/82e0edfa7372c256d893d0854f954d9099254f88/crates/cli/src/commands/mod.rs) and [task lifecycle](https://github.com/avala-ai/agent-code/blob/82e0edfa7372c256d893d0854f954d9099254f88/crates/lib/src/services/background.rs) were source-checked; the already-shipped rubric is **not** reintroduced as an unimplemented feature.

**The sole new strict assessment-derived research hypothesis** is **agent-code independent review**, because the actual frozen Index explicitly identifies missing independent source-observing claim audit. This is an *origin-class research assertion*, not proof of actual audit value, maintainer acceptance or autonomous S3*. Issue #524's existing request establishes independent product-native need, but its existing partial implementation must be respected. Other newly screened candidates were found via their specific upstream issues and are assessment-informed only.

## Cumulative evidence and next work

At frozen Index `5393b698`:
- **19 / 615** included systems have source-pinned six-function research receipts (1 original AgentBox + 5 Batch 001 + 3 Batch 002 + 10 Batch 003).
- **114 / 3,690** function slots have explicit `REVIEWED_ZERO` or `HYPOTHESES_RECORDED` research declarations.
- **596 systems, 3,576 function slots** remain unreviewed. The next deterministic assessment is `assessments/ag/agent-orchestrator-stefan1294.md`.
- The local research candidate backlog contains **9** separate cards; none is `QUALIFIED` or `SELECTED`. New in Batch 003: 4, of which **1 assessment-derived hypothesis** and **3 assessment-informed**. These are not interventions, experimental improvements or upstream PRs.

**Required next gate for agent-code reviewer:** verify remaining isolated execution gap against current subagent/task code and overlapping PRs; then run native before/after or a policy-faithful deterministic contract test before claiming substantive product benefit. Only after all four fit gates become evidence-backed PASS may a candidate be selected for a distinct `proposal_only` handoff.

No full native live tests, target repository modification, PR publication, Index grade change, S1 admission or exact-stage write authorization occurred as part of the sweep.
