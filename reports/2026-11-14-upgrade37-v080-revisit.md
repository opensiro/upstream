# Upstream upgrade batch 37 revisit under contribution protocol v0.8.0

**Date** 2026-11-14 UTC

**Owner** [Upstream #56](https://github.com/opensiro/upstream/issues/56)

**Protocol** [v0.8.0 at the integrated revision](https://github.com/opensiro/upstream/blob/38f515a1ce567dd6fd1210162df0f5d69b891a57/docs/ASSESSMENT_CANDIDATE_BATCHES.md#post-batch-39-opportunity-depth-and-closure-contribution-protocol-v080)

## Scope and result

The operator explicitly requested a revisit of the ten sources in [batch 37](../data/assessment-candidate-batches/2026-11-13-37.json). [PR #293](https://github.com/opensiro/upstream/pull/293) froze five no-change and five evidence-blocked outcomes. This report follows those same source identities under #56 and adds no cohort manifest or source reservation. The historical [hypotheses](../data/assessment-candidate-batches/2026-11-13-37-HYPOTHESES.md), [summary](../data/assessment-candidate-batches/2026-11-13-37-SUMMARY.md) and [pre-source commit](https://github.com/opensiro/upstream/commit/911456fc4acca4df5b9f38eac1395e97c3355aec) remain the evidence for the original chronology. The current-source findings and separately discovered issue-led opportunities below do not retroactively qualify as `ASSESSMENT_DERIVED`.

The ten repositories have distinct source probes for every pinned Index function (`SCREENING_COMPLETE`). Seven repositories returned 230 passing tests across selected original suites, in addition to one executed two-case Agent Autoloop baseline fixture with controls. The original proposals have six evidence-backed closure dispositions and four `OPPORTUNITY_RESEARCH_PENDING` dispositions. New, separately attributed demand is strongest for agent-autoloop receipt recovery and HelixHarness host support. No row cleared all four implementation gates. There was no target patch, publication, matched after measurement or regrade.

The frozen Index `3896a2de54399beb137f9e9959bb2587ebf4fc4a` is reachable from the observed `ce58f2172bcccbf96fc0248db8886a8847ae4f24` public main. The frozen manifest validates against a detached checkout of the original Index SHA; the controller returns `NO_ACTIONABLE_CANDIDATE`. The offline disjointness check found 38 manifests and 230 distinct sources. A read-only check of 16 open Upstream and 10 open Index PR file lists found no new manifest collision or same-Index-path edit for these ten. The original target licenses were checked first at the current source heads. Target policies cited below apply to any follow-up.

| Original target | Frozen Index assessment | Original public HEAD inspected | Root license |
| --- | --- | --- | --- |
| BinceQu/RoboHarness | [assessment](https://github.com/opensiro/vsm-harness-index/blob/3896a2de54399beb137f9e9959bb2587ebf4fc4a/assessments/ro/roboharness.md) | [`69b81164`](https://github.com/BinceQu/RoboHarness/commit/69b811646beaf6409194fc505ee70fb45e12da44) | MIT |
| deepseek-ai/dsh-superagent-prototype | [assessment](https://github.com/opensiro/vsm-harness-index/blob/3896a2de54399beb137f9e9959bb2587ebf4fc4a/assessments/ds/dsh-superagent.md) | [`8c32a9dc`](https://github.com/deepseek-ai/dsh-superagent-prototype/commit/8c32a9dc5d72c033816c6a8110b37f40cf94fba4) | MIT |
| didi/helixharness | [assessment](https://github.com/opensiro/vsm-harness-index/blob/3896a2de54399beb137f9e9959bb2587ebf4fc4a/assessments/he/helixharness.md) | [`beff98e9`](https://github.com/didi/helixharness/commit/beff98e953557a45e036586432ac1102aa0f7b21) | Apache-2.0 |
| KKKKhazix/agent-autoloop | [assessment](https://github.com/opensiro/vsm-harness-index/blob/3896a2de54399beb137f9e9959bb2587ebf4fc4a/assessments/ag/agent-autoloop.md) | [`d3a44cac`](https://github.com/KKKKhazix/agent-autoloop/commit/d3a44cac4460f4e0417c3d407baa853de7aa25ff) | MIT |
| LineLuLan/line-harness | [assessment](https://github.com/opensiro/vsm-harness-index/blob/3896a2de54399beb137f9e9959bb2587ebf4fc4a/assessments/li/line-harness.md) | [`63c98c60`](https://github.com/LineLuLan/line-harness/commit/63c98c60b18cfe603381890e104a043627b35ccf) | MIT |
| adamentwistle/orchi-build | [assessment](https://github.com/opensiro/vsm-harness-index/blob/3896a2de54399beb137f9e9959bb2587ebf4fc4a/assessments/or/orchi.md) | [`db5a720a`](https://github.com/adamentwistle/orchi-build/commit/db5a720ad7cccfd579e26b7ced7a1bbdcf586306) | MIT (see NOTICE.md) |
| Andy1890/ruhui-agent | [assessment](https://github.com/opensiro/vsm-harness-index/blob/3896a2de54399beb137f9e9959bb2587ebf4fc4a/assessments/ru/ruhui-agent.md) | [`4bbff9f3`](https://github.com/Andy1890/ruhui-agent/commit/4bbff9f3094f5024edb7e25ba36b4c31d55df7d6) | MIT |
| aws-samples/sample-hyperscale-agent-meta-harness | [assessment](https://github.com/opensiro/vsm-harness-index/blob/3896a2de54399beb137f9e9959bb2587ebf4fc4a/assessments/hy/hyperscale-agent-meta-harness.md) | [`9051f03a`](https://github.com/aws-samples/sample-hyperscale-agent-meta-harness/commit/9051f03acde6dda3d589c86584e7b4e110e3cedc) | MIT-0 |
| cuijiejie/open-agent-harness | [assessment](https://github.com/opensiro/vsm-harness-index/blob/3896a2de54399beb137f9e9959bb2587ebf4fc4a/assessments/cu/cuijiejie-open-agent-harness.md) | [`24b01700`](https://github.com/cuijiejie/open-agent-harness/commit/24b0170028ae7683867d2b8d5ce1589d8ace12eb) | Apache-2.0 |
| DaDozlov/harness-agent | [assessment](https://github.com/opensiro/vsm-harness-index/blob/3896a2de54399beb137f9e9959bb2587ebf4fc4a/assessments/he/heaw.md) | [`dfff7b2b`](https://github.com/DaDozlov/harness-agent/commit/dfff7b2bfbd6fb08cb754461124ac8dab2053622) | MIT |

## Original feature opportunities

Gate order is **need / mechanism / counterfactual / scope**. A failed gate means the specific checked proposal did not establish a distinct improvement. Pending means the evidence cannot decide it. A report, optional prerequisite or release snapshot is not a native before/after receipt.

| Target and original question | v0.8.0 disposition | Gates | Falsifier, result or smallest next step |
| --- | --- | --- | --- |
| RoboHarness · receipt diagnostic | `OPPORTUNITY_DECIDED` · equivalent behavior | FAIL / PASS / FAIL / PASS | 9 native observation tests passed. Delivery retry, integrity failure and isolated sessions are already covered. No specific missing operator input/output was identified. |
| dsh-superagent · capacity impact preview | `OPPORTUNITY_RESEARCH_PENDING` | PENDING / PASS / PENDING / PASS | The existing panel passes 13 tests and 10 selected slot tests corroborate the launch cap, startup reservations and one extra slot for human follow-ups. Showing current load and estimating the next eligible tickets are distinct workflows. The operator would need to specify a real capacity change and the expected behavior for one running, one queued and one human follow-up ticket. Hold any ticket-order/ETA claim until that horizon and expected output exist. |
| HelixHarness · extra Base/Candidate comparison | `OPPORTUNITY_DECIDED` · equivalent behavior | FAIL / PASS / FAIL / PASS | Current Run detail already compares pinned Base/Candidate versions, scores and case diagnostics. 14 workflow-contract tests passed. The project declined a separate cross-product benchmark in [#12](https://github.com/didi/helixharness/issues/12#issuecomment-6569271853). Additional cross-product comparison is outside this proposal. |
| Agent Autoloop · per-subject dispatch explanation | `OPPORTUNITY_DECIDED` · equivalent behavior | FAIL / PASS / FAIL / PASS | Merged [#293](https://github.com/KKKKhazix/agent-autoloop/pull/293) keeps full failure detail in `why`, and [#294](https://github.com/KKKKhazix/agent-autoloop/pull/294) exposes recent delivery failure in status/doctor. The proposed generic view lacks a remaining user scenario. The new receipt opportunity below is separate. |
| Line Harness · review coverage matrix | `OPPORTUNITY_DECIDED` · bounded no change | FAIL / PASS / FAIL / PASS | Reviewer already receives criteria plus actual diff, and Line Hub reports finding counts by review layer. 26 existing collector/replay/triage tests passed on fixtures. A finer criteria-to-finding report has no supported downstream consumer in the inspected path. |
| Orchi · pre-fanout collision preview | `OPPORTUNITY_RESEARCH_PENDING` | PENDING / PENDING / PENDING / PENDING | The skill uses free-text task briefs and serializes ambiguous scope. 36 existing skill/Bugbot tests pass; they do not exercise a machine-readable fanout planner. The maintainer would need to choose a scope representation. Two explicitly overlapping packages and two disjoint packages could then test whether a preview adds a useful operator decision. |
| RuHui Agent · offline capability explanation | `OPPORTUNITY_RESEARCH_PENDING` | PENDING / PASS / PENDING / PENDING | The supported doctor path resolves workspace config and reports version/workspace/mode/sandbox. The smallest check is whether a read-only tool inventory gives a real user a decision they cannot make from doctor plus tool documentation. The release-supported Node binary did not start on the separate runner (missing libatomic), so this remains source-only. Policy/loop changes also require an ADR or requirement update and any later contribution requires personal DCO. |
| Hyperscale Agent Meta Harness · rerun discrepancy triage | `OPPORTUNITY_DECIDED` · equivalent behavior | FAIL / PASS / FAIL / PASS | Current report differentiates command failure, timeout, not-run and missing-service cases and carries evidence for the delivered checkout. Source-only conclusion for this specific classification. A future matched report-pair comparison would need a concrete operator report pair. |
| Open Agent Harness · pre-denial explanation | `OPPORTUNITY_RESEARCH_PENDING` | PENDING / PASS / PENDING / PENDING | The current-user endpoint already reports effective roles and tools; tool assembly and permission hints are separate. No user-backed case requiring another explanation was found. A next check should compare the existing UI and endpoint for an ordinary current-user session and one explicitly unavailable benign tool. CONTRIBUTING.md requires an issue before a behavioral change. |
| HEAW · grouped browser verification failures | `OPPORTUNITY_DECIDED` · equivalent behavior | FAIL / PASS / FAIL / PASS | Built-in tester already groups observed issues, evidence and final verdict; before-stop returns failed checks to the agent. Sixteen existing plan/check and session report tests passed. This source conclusion covers the proposed reporting contract. It does not establish browser or model behavior. |

## Separately discovered source-first opportunities

The public issue/PR sweep was performed during this revisit on 2026-11-14. Six repositories returned empty recent issue/PR lists and HEAW returned dependency PRs. That limited public evidence does not exhaust demand. The strongest user reports below have distinct mechanisms and owners.

1. **Agent Autoloop #299 — retain independent receipt actions (S1 with downstream S2/S3 effects).** The reporter describes lost actions and delayed follow-up. The original worker boundary reproduced loss of a valid notice when a separate timer-cancellation entry carried an incompatible field. An entirely valid control retained both items. A normal first-party worker repair may recover a malformed receipt; its own tests establish that an unsuccessful repair preserves the business outcome and can discard the structured receipt. The probe excludes a live workspace and confirms the parser behavior rather than the reported production delays. A narrow candidate would retain a valid independent item and explain the rejected item while preserving schema, end-state validation, action ordering, idempotency and the existing strict hub wire contract. **Need PASS / mechanism PASS / counterfactual PENDING / scope PENDING.** This is a source-first, assessment-informed candidate for a minor capability. The maintainer owns whether partial acceptance belongs in the worker and what cross-item dependencies remain atomic. The contributor guide explicitly routes reproducible defects to issue reporting and points to maintainers for fixes, so #299 is the existing handoff. Their [published contributor guide](https://github.com/KKKKhazix/agent-autoloop/blob/d3a44cac4460f4e0417c3d407baa853de7aa25ff/CONTRIBUTING.md) routes protocol/core changes through concrete compatibility discussion. The next deciding test would compare an independent valid notice plus malformed later item against a fully valid pair, a wholly invalid outcome and a case where partial application could change the intent. [Original issue #299](https://github.com/KKKKhazix/agent-autoloop/issues/299)
2. **Agent Autoloop #297 — completion when worker output is unrelated (S1).** `readMessage` returned `done` for a nonempty line with no receipt and `failed` for empty input. The parser cannot judge whether arbitrary text fulfills the event, and the current contract explicitly allows receipt-less runs. PR #300 improves first-line wording, which does not enforce either completion proof or retry semantics. Treat as a separate source-first fallback and wait for a compatibility decision on an opt-in explicit outcome for event-driven rules. The matched scenario needs both an actual useful receipt-less run and an unrelated result, plus a repeated-side-effect control. [Issue #297](https://github.com/KKKKhazix/agent-autoloop/issues/297) · [PR #300](https://github.com/KKKKhazix/agent-autoloop/pull/300)
3. **HelixHarness #11 — Cursor host support (S1/S2).** A maintainer confirms future support. The host registry currently ships Codex and Claude Code, while PRs #14/#16 propose other host kits. Fifteen existing host-registry tests passed, which supports the current seam, not Cursor compatibility. Native scope/counterfactual remain pending until the maintainer names the intended host, supported release, project adapter and acceptance workflow (command projection, hook ownership, Propose/Apply/Archive, and compatibility controls for both existing hosts). **Need PASS / mechanism PENDING / counterfactual PENDING / scope PENDING.** [Issue #11](https://github.com/didi/helixharness/issues/11#issuecomment-6520384074)
4. **HelixHarness #4 and #3.** Greenfield init has a concrete gap and an existing implementation/test PR #7; route evidence there rather than starting a competing patch. The multi-repo Workspace half of #3 already exists (34 native Workspace/registry tests passed); the remaining single-install multi-host skill projection is a specific but undefined portability request. The next decision is a two-host projection acceptance case against the existing host templates. [Issue #4](https://github.com/didi/helixharness/issues/4) · [PR #7](https://github.com/didi/helixharness/pull/7) · [Issue #3 follow-up](https://github.com/didi/helixharness/issues/3#issuecomment-6568361211)

## Six-function evidence per original source

The state column is the historical Index state, including its original assessment recursion. Observations refer to the pinned current target source above. A configured guard, test suite, log, or individual forecast does not itself establish an organizational function at that recursion.

### BinceQu/RoboHarness

| Function | Index state | Current primary evidence and disposition |
| --- | --- | --- |
| S1 | A | [harness/v2/R1_pro/tools/util/observation_hook.py](https://github.com/BinceQu/RoboHarness/blob/69b811646beaf6409194fc505ee70fb45e12da44/harness/v2/R1_pro/tools/util/observation_hook.py) — Receipt diagnostic already correlates captures and detects repeated observations. Native delivery/progress checks exercise delayed delivery, failed integrity validation and isolation. |
| S2 | — | [harness/v2/R1_pro/tools/util/controller.py](https://github.com/BinceQu/RoboHarness/blob/69b811646beaf6409194fc505ee70fb45e12da44/harness/v2/R1_pro/tools/util/controller.py) — Controller organizes movement within one robot episode. No separate coordination feature was justified for independently owned tasks. |
| S3 | — | [harness/v2/R1_pro/tools/util/budget.py](https://github.com/BinceQu/RoboHarness/blob/69b811646beaf6409194fc505ee70fb45e12da44/harness/v2/R1_pro/tools/util/budget.py) — Budget normalization distinguishes missing and available counters. The bounded episode has a budget surface without a demonstrated fleet-level capacity workflow. |
| S3* | — | [scripts/report_validation.py](https://github.com/BinceQu/RoboHarness/blob/69b811646beaf6409194fc505ee70fb45e12da44/scripts/report_validation.py) — Validation compares completed per-instance means with the reference and checks live run evidence. No separately demonstrated need for another in-episode audit return. |
| S4 | — | [eval/behavior/README.md](https://github.com/BinceQu/RoboHarness/blob/69b811646beaf6409194fc505ee70fb45e12da44/eval/behavior/README.md) — New simulator cases and embodiments enter configured evaluation. Their presence does not create a native adaptation decision about future harness capability. |
| S5 | — | [run.sh](https://github.com/BinceQu/RoboHarness/blob/69b811646beaf6409194fc505ee70fb45e12da44/run.sh) — Launcher selects configuration by task/variant under the operator's choices. No user demand was found for an in-runtime policy decision mechanism. |

### deepseek-ai/dsh-superagent-prototype

| Function | Index state | Current primary evidence and disposition |
| --- | --- | --- |
| S1 | A | [src/core/tickets.ts](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/8c32a9dc5d72c033816c6a8110b37f40cf94fba4/src/core/tickets.ts) — Ticket state retains the bounded work item and recorded disposition. No first-party demand appears for a different work-item hand-in. |
| S2 | A | [tests/followups.spec.ts](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/8c32a9dc5d72c033816c6a8110b37f40cf94fba4/tests/followups.spec.ts) — Native follow-up tests target handback and reassignment across tickets. This covers coordination distinct from the worker-capacity question. |
| S3 | P | [src/app/views/overview.ts](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/8c32a9dc5d72c033816c6a8110b37f40cf94fba4/src/app/views/overview.ts) — Current panel already includes running, queued, idle and maxWorkers. WorkerSlots in src/executor/dsh.ts enforces the current cap. A ticket-level hypothetical projection has no supported ordering/time horizon. |
| S3* | — | [src/app/assessment.ts](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/8c32a9dc5d72c033816c6a8110b37f40cf94fba4/src/app/assessment.ts) — MasterAssessor decides source admission. That is a different subject from independent examination of a worker's resulting diff. No in-bundle audit workflow demand found. |
| S4 | — | [src/app/views/overview.ts](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/8c32a9dc5d72c033816c6a8110b37f40cf94fba4/src/app/views/overview.ts) — Recent trigger/judgment statistics are current operational feedback. No first-party consumer of a future adaptation proposal was found. |
| S5 | P | [src/policy.ts](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/8c32a9dc5d72c033816c6a8110b37f40cf94fba4/src/policy.ts) — settingsPolicy and policyEffects translate operator scope and produce effects of changed settings on tickets. The standing admission policy already has a native control. |

### didi/helixharness

| Function | Index state | Current primary evidence and disposition |
| --- | --- | --- |
| S1 | A | [helixharness/scripts/workflow_router.py](https://github.com/didi/helixharness/blob/beff98e953557a45e036586432ac1102aa0f7b21/helixharness/scripts/workflow_router.py) — The current command router supports the feature lifecycle. Greenfield init has an explicit acceptance contract in #4 and existing implementation PR #7. |
| S2 | A | [helixharness/scripts/tests/test_workspace.py](https://github.com/didi/helixharness/blob/beff98e953557a45e036586432ac1102aa0f7b21/helixharness/scripts/tests/test_workspace.py) — Per-repository dependency and ownership within a Workspace are exercised by original tests. #3's remaining multi-host skill projection request is separate. |
| S3 | P | [helixharness-platform/bench/workload_policy.py](https://github.com/didi/helixharness/blob/beff98e953557a45e036586432ac1102aa0f7b21/helixharness-platform/bench/workload_policy.py) — Benchmark workload policy already scopes platform run resources. No evidence supports changing the operator allocation policy for the original comparison question. |
| S3* | A | [helixharness/skills/code-review/SKILL.md](https://github.com/didi/helixharness/blob/beff98e953557a45e036586432ac1102aa0f7b21/helixharness/skills/code-review/SKILL.md) — Review directs separate standards and spec checks with explicit findings. Another review report is unsupported by current demand. |
| S4 | C | [helixharness-platform/web_ui/templates/bench/run_detail.html](https://github.com/didi/helixharness/blob/beff98e953557a45e036586432ac1102aa0f7b21/helixharness-platform/web_ui/templates/bench/run_detail.html) — Existing Base/Candidate version comparisons include per-case scores, aggregate scores, confidence context and retry information. Generic comparison duplicate. |
| S5 | P | [helixharness/reference/version-policy.json](https://github.com/didi/helixharness/blob/beff98e953557a45e036586432ac1102aa0f7b21/helixharness/reference/version-policy.json) — Version boundaries are explicit, and CONTRIBUTING.md routes major public changes through an issue. #11's Cursor support has direction but no accepted host behavior documented. |

### KKKKhazix/agent-autoloop

| Function | Index state | Current primary evidence and disposition |
| --- | --- | --- |
| S1 | A | [worker/contract.ts](https://github.com/KKKKhazix/agent-autoloop/blob/d3a44cac4460f4e0417c3d407baa853de7aa25ff/worker/contract.ts) — Mixed receipt with a valid notice and invalid later action loses both at resultFrom. A nonempty receipt-less line also classifies as done. Demand independently recorded in #299/#297. |
| S2 | C | [kernel/decide.ts](https://github.com/KKKKhazix/agent-autoloop/blob/d3a44cac4460f4e0417c3d407baa853de7aa25ff/kernel/decide.ts) — Rule/lane deciding already coordinates current work. Fresh #293/#294 show status summaries and full why detail, with a distinct downstream risk when receipt events are dropped. |
| S3 | P | [tests/status-json.test.ts](https://github.com/KKKKhazix/agent-autoloop/blob/d3a44cac4460f4e0417c3d407baa853de7aa25ff/tests/status-json.test.ts) — Status has native machine-readable output. Merged #294 exposes recent channel delivery failures in status/doctor. Original additional dispatch explanation lacks a distinct supported consumer. |
| S3* | A | [plugins/delivery/review.ts](https://github.com/KKKKhazix/agent-autoloop/blob/d3a44cac4460f4e0417c3d407baa853de7aa25ff/plugins/delivery/review.ts) — Separate PR review surface has its own path. Receipt parsing or rendering does not establish the quality of the work that produced it. |
| S4 | — | [protocol/validate.ts](https://github.com/KKKKhazix/agent-autoloop/blob/d3a44cac4460f4e0417c3d407baa853de7aa25ff/protocol/validate.ts) — later is a future run instruction with its own validation, not a future redesign of the hub. Loss of a valid action is a receipt/workflow concern. |
| S5 | — | [kernel/rules.ts](https://github.com/KKKKhazix/agent-autoloop/blob/d3a44cac4460f4e0417c3d407baa853de7aa25ff/kernel/rules.ts) — User-supplied rules specify capabilities and scope at execution. Keep validation and operator decisions intact when considering receipt recovery. |

### LineLuLan/line-harness

| Function | Index state | Current primary evidence and disposition |
| --- | --- | --- |
| S1 | A | [claude/bin/codex-do.ps1](https://github.com/LineLuLan/line-harness/blob/63c98c60b18cfe603381890e104a043627b35ccf/claude/bin/codex-do.ps1) — The worker entry captures a coding run and its hand-in. The Hub's metrics can describe the activity without changing task execution. |
| S2 | A | [claude/hooks/codex-job-watcher.ps1](https://github.com/LineLuLan/line-harness/blob/63c98c60b18cfe603381890e104a043627b35ccf/claude/hooks/codex-job-watcher.ps1) — Watcher returns active worker job state to supervision; the existing wrapper's dispatch/watch boundaries differ from a review coverage matrix. |
| S3 | A | [hub/README.md](https://github.com/LineLuLan/line-harness/blob/63c98c60b18cfe603381890e104a043627b35ccf/hub/README.md) — The Hub already exposes usage, review rounds, run health and lost runs; its read-only SQLite projection does not become an operator intervention surface. |
| S3* | A | [claude/bin/codex-review.ps1](https://github.com/LineLuLan/line-harness/blob/63c98c60b18cfe603381890e104a043627b35ccf/claude/bin/codex-review.ps1) — Reviewer receives actual diff and acceptance criteria, while Hub displays counts stratified by review layer. Criteria-by-criterion structured provenance has no concrete user or maintainer case. |
| S4 | — | [claude/bin/mcp-weekly-update.ps1](https://github.com/LineLuLan/line-harness/blob/63c98c60b18cfe603381890e104a043627b35ccf/claude/bin/mcp-weekly-update.ps1) — Weekly package maintenance is a fixed update routine. No qualifying prospective adaptation evidence associated with the original proposal. |
| S5 | — | [claude/hooks/git-push-guard.ps1](https://github.com/LineLuLan/line-harness/blob/63c98c60b18cfe603381890e104a043627b35ccf/claude/hooks/git-push-guard.ps1) — Installed guard constrains the worker under an existing user policy, without an in-harness decision process for rewriting that policy. |

### adamentwistle/orchi-build

| Function | Index state | Current primary evidence and disposition |
| --- | --- | --- |
| S1 | A | [skills/ticket-session/SKILL.md](https://github.com/adamentwistle/orchi-build/blob/db5a720ad7cccfd579e26b7ced7a1bbdcf586306/skills/ticket-session/SKILL.md) — Ticket workflow records a bounded job, hands it to a worker and returns results. No extra product need was found at hand-in. |
| S2 | A | [skills/fanout/SKILL.md](https://github.com/adamentwistle/orchi-build/blob/db5a720ad7cccfd579e26b7ced7a1bbdcf586306/skills/fanout/SKILL.md) — Planning marks tasks parallel only for disjoint files or packages, otherwise serial. The explicit boundary of a possible preview is ambiguous package ownership, not missing overlap guidance. |
| S3 | A | [bin/usage-watch](https://github.com/adamentwistle/orchi-build/blob/db5a720ad7cccfd579e26b7ced7a1bbdcf586306/bin/usage-watch) — Usage observation protects current capacity via the guard. It has a different consumer and acceptance condition from a plan-preview feature. |
| S3* | A | [docs/adr/0001-pull-request-review.md](https://github.com/adamentwistle/orchi-build/blob/db5a720ad7cccfd579e26b7ced7a1bbdcf586306/docs/adr/0001-pull-request-review.md) — Review policy chooses a separately invoked review path over worker self-report; it requires PR evidence. No reason to treat a worktree scope forecast as an audit. |
| S4 | — | [skills/roadmap-planning/SKILL.md](https://github.com/adamentwistle/orchi-build/blob/db5a720ad7cccfd579e26b7ced7a1bbdcf586306/skills/roadmap-planning/SKILL.md) — Roadmap planning produces a task/drill-down order from existing operator priorities. No independent demand surfaced for an Orchi strategy loop. |
| S5 | P | [docs/adr/0003-ticket-writes.md](https://github.com/adamentwistle/orchi-build/blob/db5a720ad7cccfd579e26b7ced7a1bbdcf586306/docs/adr/0003-ticket-writes.md) — Write authority and owner-specified source constraints apply independently of fanout scheduling. A preview has no established change to the mandate. |

### Andy1890/ruhui-agent

| Function | Index state | Current primary evidence and disposition |
| --- | --- | --- |
| S1 | A | [packages/sdk/agent-node.mjs](https://github.com/Andy1890/ruhui-agent/blob/4bbff9f3094f5024edb7e25ba36b4c31d55df7d6/packages/sdk/agent-node.mjs) — doctor loads the actual workspace and mode, but renders version/workspace/mode/sandbox. An offline tool inventory is a distinct narrow workflow whose consumer is still unverified. |
| S2 | — | [packages/core/src/loop.ts](https://github.com/Andy1890/ruhui-agent/blob/4bbff9f3094f5024edb7e25ba36b4c31d55df7d6/packages/core/src/loop.ts) — Loop handles one agent's tool/use progression and result shape. A planned tool sequence does not imply multiple independently owned work cells. |
| S3 | — | [packages/core/src/budget.ts](https://github.com/Andy1890/ruhui-agent/blob/4bbff9f3094f5024edb7e25ba36b4c31d55df7d6/packages/core/src/budget.ts) — Budget helpers are run-local. No evidence of a deployment-wide queue or operating-control consumer for a new preview. |
| S3* | — | [packages/core/test/rollout.test.mjs](https://github.com/Andy1890/ruhui-agent/blob/4bbff9f3094f5024edb7e25ba36b4c31d55df7d6/packages/core/test/rollout.test.mjs) — Rollout tests cover persistence structure. That does not establish a separate assessor of the task's result or demand for adding one. |
| S4 | — | [packages/providers/src/openai.ts](https://github.com/Andy1890/ruhui-agent/blob/4bbff9f3094f5024edb7e25ba36b4c31d55df7d6/packages/providers/src/openai.ts) — Provider profile supplies capability metadata used by native requests. There is no evidenced prospective provider-selection loop at this boundary. |
| S5 | — | [packages/tools/src/policy.ts](https://github.com/Andy1890/ruhui-agent/blob/4bbff9f3094f5024edb7e25ba36b4c31d55df7d6/packages/tools/src/policy.ts) — Policy distinguishes permitted tool behavior and honors the user boundary. Changes involving policy follow the ADR and DCO in CONTRIBUTING.md. |

### aws-samples/sample-hyperscale-agent-meta-harness

| Function | Index state | Current primary evidence and disposition |
| --- | --- | --- |
| S1 | A | [crates/delivery/src/packager.rs](https://github.com/aws-samples/sample-hyperscale-agent-meta-harness/blob/9051f03acde6dda3d589c86584e7b4e110e3cedc/crates/delivery/src/packager.rs) — Delivery packages the actual source and evidence from a run. Another discrepancy flag cannot change the meaning of ordinary delivery. |
| S2 | — | [crates/dispatcher/src/lib.rs](https://github.com/aws-samples/sample-hyperscale-agent-meta-harness/blob/9051f03acde6dda3d589c86584e7b4e110e3cedc/crates/dispatcher/src/lib.rs) — Dispatcher starts work in separate runs. The review found no demand for a new inter-run coordination surface to support the audit idea. |
| S3 | P | [crates/control-api/src/resume.rs](https://github.com/aws-samples/sample-hyperscale-agent-meta-harness/blob/9051f03acde6dda3d589c86584e7b4e110e3cedc/crates/control-api/src/resume.rs) — Resume has an operator-triggered native path. It is separate from an evidentiary test report and does not require a new report category. |
| S3* | C | [crates/harness-protocol/tests/test_report_not_run.rs](https://github.com/aws-samples/sample-hyperscale-agent-meta-harness/blob/9051f03acde6dda3d589c86584e7b4e110e3cedc/crates/harness-protocol/tests/test_report_not_run.rs) — The original report distinguishes not-run from ordinary results. Current crates/harness-protocol/src/test_report.rs also represents timeout and missing services. |
| S4 | — | [engine/catalog/models.json](https://github.com/aws-samples/sample-hyperscale-agent-meta-harness/blob/9051f03acde6dda3d589c86584e7b4e110e3cedc/engine/catalog/models.json) — Engine/model catalog supplies shipped choices. It does not supply a supported native process for deciding future engine additions using audit results. |
| S5 | — | [crates/delivery/src/repo_names.rs](https://github.com/aws-samples/sample-hyperscale-agent-meta-harness/blob/9051f03acde6dda3d589c86584e7b4e110e3cedc/crates/delivery/src/repo_names.rs) — Delivery target defaults/allowlists constrain delivery policy. No current requirement for an autonomous revision of top-level targets. |

### cuijiejie/open-agent-harness

| Function | Index state | Current primary evidence and disposition |
| --- | --- | --- |
| S1 | A | [src/agent/main_agent.py](https://github.com/cuijiejie/open-agent-harness/blob/24b0170028ae7683867d2b8d5ce1589d8ace12eb/src/agent/main_agent.py) — Shipped agent composes tools and middleware for individual work. Previewing agent decisions is outside the narrow current-user permissions request. |
| S2 | — | [src/agent/subagents/__init__.py](https://github.com/cuijiejie/open-agent-harness/blob/24b0170028ae7683867d2b8d5ce1589d8ace12eb/src/agent/subagents/__init__.py) — Subagent definitions structure one task. No first-party claim that a shared workflow routinely needs a separate coordination plane to explain tool availability. |
| S3 | P | [src/web/routers/rbac.py](https://github.com/cuijiejie/open-agent-harness/blob/24b0170028ae7683867d2b8d5ce1589d8ace12eb/src/web/routers/rbac.py) — Current user sees effective roles/tools, with admin or wildcard behavior. The exact frontend task-blocker/denial scenario required for a new explanation has not been shown. |
| S3* | — | [src/web/routers/audit.py](https://github.com/cuijiejie/open-agent-harness/blob/24b0170028ae7683867d2b8d5ce1589d8ace12eb/src/web/routers/audit.py) — Existing audit route exposes operational logs. No verified independent action-quality audit workflow or incremental demand. |
| S4 | — | [src/agent/memory/user_prefs.py](https://github.com/cuijiejie/open-agent-harness/blob/24b0170028ae7683867d2b8d5ce1589d8ace12eb/src/agent/memory/user_prefs.py) — User preferences inform individual execution. They give no evidence for a capability adaptation decision for the whole service. |
| S5 | — | [src/infra/RbacService.py](https://github.com/cuijiejie/open-agent-harness/blob/24b0170028ae7683867d2b8d5ce1589d8ace12eb/src/infra/RbacService.py) — Roles govern current access; the project requires an issue before changing behavior. There is no demand to change authorization semantics for the proposed explanation. |

### DaDozlov/harness-agent

| Function | Index state | Current primary evidence and disposition |
| --- | --- | --- |
| S1 | A | [src/core/plan.ts](https://github.com/DaDozlov/harness-agent/blob/dfff7b2bfbd6fb08cb754461124ac8dab2053622/src/core/plan.ts) — Plan tracks progress through steps. CLI resume and project test hooks already carry work forward without a new browser-specific work handoff. |
| S2 | A | [src/agents/subagents.ts](https://github.com/DaDozlov/harness-agent/blob/dfff7b2bfbd6fb08cb754461124ac8dab2053622/src/agents/subagents.ts) — Delegate supports parallel work with shared remaining budget and bounded child behavior. Browser review grouping is not a coordination need. |
| S3 | — | [src/observability/session-report.ts](https://github.com/DaDozlov/harness-agent/blob/dfff7b2bfbd6fb08cb754461124ac8dab2053622/src/observability/session-report.ts) — Session report projects budgets, stop reasons and before-stop outcomes. It can already explain a blocked run at the operator surface. |
| S3* | C | [src/skills/built-in.ts](https://github.com/DaDozlov/harness-agent/blob/dfff7b2bfbd6fb08cb754461124ac8dab2053622/src/skills/built-in.ts) — Tester output already includes broken user actions, console/network observations, evidence and a final verdict. src/core/hooks.ts returns failed-check feedback for continuation. |
| S4 | — | [src/evals/compare.ts](https://github.com/DaDozlov/harness-agent/blob/dfff7b2bfbd6fb08cb754461124ac8dab2053622/src/evals/compare.ts) — Explicit local evaluation comparisons and /retro exist. No first-party evidence moves these into a standing adaptability decision or supplies demand for the proposed grouped browser report. |
| S5 | — | [src/config/schema.ts](https://github.com/DaDozlov/harness-agent/blob/dfff7b2bfbd6fb08cb754461124ac8dab2053622/src/config/schema.ts) — Project config validates approval/workspace and model settings fixed by its operator. Public config changes are issue-first under CONTRIBUTING.md. |

## Executed baseline receipts

Read-only deterministic setup and execution used a separate server CLI runner with fresh target clones pinned above. Invocations below are relative to each target's path. These are original-source checks and controls. There was no target derivative, live model, live robot simulator or browser episode.

| Source | Runtime and exact command | Observed result |
| --- | --- | --- |
| RoboHarness | Python 3.12.3, pytest 8.4.2 and Pillow 11.3.0; from `harness/v2/R1_pro`, `PYTHONPATH="$PWD" python -m pytest -q .dev/tests/test_observation_delivery.py .dev/tests/test_observation_progress.py` | 9 passed. Initial attempts lacked Pillow/PYTHONPATH; final invocation collected and ran both files. |
| dsh-superagent | Node v24.13.0, pnpm 11.7.0 frozen lockfile; `node node_modules/vitest/vitest.mjs run tests/panel-overview.spec.tsx` and `node node_modules/vitest/vitest.mjs run tests/runtime-concurrency.spec.ts -t slot` | 13 passed, then 10 selected passed and 46 unselected skipped. Baseline confirms existing slot behavior, not forecasting. |
| HelixHarness | Python 3.12.3; from `helixharness/`, `PYTHONPATH=scripts python3 -m unittest discover -s scripts/tests -p test_workspace.py -q`; same command for `test_workspace_init_registry.py` and `test_host_runtime_registry.py`; from `helixharness-platform/`, `python -m pytest -q bench/tests/test_framework_eval_workflow_contracts.py` using pytest 8.4.2 / PyYAML 6.0.2 | 31 + 3 + 15 + 14 passed. Host registry and evaluation contracts only. |
| Agent Autoloop | Node v24.13.0; `node --disable-warning=ExperimentalWarning --test tests/contract.test.ts tests/worker.test.ts`; `node --input-type=module` with fixture below | 57 existing tests passed. Fixture reproduced #299's validation loss and confirmed #297's parser behavior. |
| Line Harness | Node v24.22.1; from `hub/`, `node --test tests/collector.test.js tests/replay.test.js tests/triage.test.js` | 26 passed using synthetic first-party fixtures. No real operator logs or PowerShell checker execution. |
| Orchi | Python 3.12.3, pytest 8.4.2; `python -m pytest -q bin/tests/test_skills.py bin/tests/test_bugbot_wait.py` | 36 passed. No deterministic fanout overlap preview path executed. |
| RuHui Agent | Attempted Node v26.13.0 `node packages/cli/ruhui.mjs doctor` | The Node binary could not start because the separate runner lacks `libatomic.so.1`; `apt-cache show libatomic1` found no package in its configured cache. Use the project's supported Node setup for the next CLI baseline. Source inspection establishes doctor's declared output surface. |
| Open Agent Harness | Pinned source archive; `python3 -m unittest test.unit.test_rbac_gate -q` on the separate runner | 12 collected, 6 errors and 1 skip in the unprovisioned environment. Tool-registry imports require `langchain_core`. Use the project's declared dependencies and synthetic fixtures for a follow-up, before attempting a UI-level check. No runtime claim supported here. |
| Hyperscale Agent Meta Harness | Source inspection of `crates/harness-protocol/src/test_report.rs` and native tests at the pinned SHA | `command -v cargo` returned no executable on the separate runner. The target pins Rust 1.98.1. The next bounded check if a distinct report pair surfaces is `cargo test -p harness-protocol --test test_report --test test_report_not_run --locked`. |
| HEAW | Node v24.22.1, locked dependencies via `npm ci --ignore-scripts --no-audit --no-fund`; `node scripts/vitest.mjs run test/core/plan-and-checks.test.ts test/observability/session-report.test.ts` | 16 passed, including repeated check failure and session summaries. No browser episode or measured browser-side effect. |

### Agent Autoloop baseline fixture

From the pinned checkout, pass this fixture to `node --input-type=module`. It calls the original pure worker functions with local synthetic text and exercises the separate notice/timer case and the two terminal-message classifications.

```js
import assert from 'node:assert/strict';
import { readMessage, resultFrom } from './worker/contract.ts';

const notice = { title: 'Local fixture', text: 'A baseline observation was recorded' };
const valid = { notice: [notice], later: [{ key: 'follow-up', cancel: true }] };
const mixed = { ...valid, later: [{ key: 'follow-up', cancel: true, at: '2026-11-15T10:00:00Z' }] };
const fence = String.fromCharCode(96).repeat(3);
const run = (receipt) => resultFrom(
  readMessage('Recorded local observation\n' + fence + 'agent-autoloop\n' + JSON.stringify(receipt) + '\n' + fence),
  {},
);

const control = run(valid);
const baseline = run(mixed);
assert.deepEqual(control.result.notice, [notice]);
assert.equal(control.result.later.length, 1);
assert.equal(control.problem, undefined);
assert.equal(baseline.result.notice, undefined);
assert.equal(baseline.result.later, undefined);
assert.ok(baseline.problem?.includes('later'));
assert.equal(readMessage('Local notes for tomorrow').outcome, 'done');
assert.equal(readMessage('   ').outcome, 'failed');
```
