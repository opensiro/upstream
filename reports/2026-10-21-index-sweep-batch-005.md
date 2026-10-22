# Deterministic Index six-function improvement screen — Batch 005 (five systems)

**Date:** 2026-10-21. **Owning experiment:** [Upstream #56](https://github.com/opensiro/upstream/issues/56), [Draft PR #67](https://github.com/opensiro/upstream/pull/67). **Frozen current canonical Index:** `main@5393b698bfdfa4ca14d97a79238234eca20694e5`; next five included assessments after [Batch 004](2026-10-21-index-sweep-batch-004.md) in deterministic path order.

All five have six distinct S1/S2/S3/S3*/S4/S5 research decisions in [`sweeps/`](../sweeps/README.md). Each description follows the exact original assessed `review_ref`. Fresh target public HEAD, first-party issue search and selected current native code surfaces were checked. **Not** comprehensive target implementation review or real binary/GUI/native before/after testing.

| System, assessed function states | Current evidence | Product improvement decision |
| --- | --- | --- |
| [Agent-S](../sweeps/agent-s.json): `A/—/—/—/—/—` | Current `simular-ai/Agent-S/main@15776a8dc659658b1963816ea006f7af1978e595`, [open #235](https://github.com/simular-ai/Agent-S/issues/235), current [`gui_agents/s3/cli_app.py`](https://github.com/simular-ai/Agent-S/blob/15776a8dc659658b1963816ea006f7af1978e595/gui_agents/s3/cli_app.py) | [One `ASSESSMENT_INFORMED / SCREENING` candidate](../candidates/agent-s-cli-action-20261021.md). The shipped S3 GUI task loop treats keywords inside normal `agent.type(...)` text as terminal control. Reporter has said a fix is in preparation; avoid duplicating an incoming native PR. |
| [Agent Squad](../sweeps/agent-squad.json): `A/—/—/—/—/—` | Current `2FastLabs/agent-squad/main@729d5f52869c8280f599a9fa5cf27fc1df445602`, related [issues #662](https://github.com/2FastLabs/agent-squad/issues/662) / [#661](https://github.com/2FastLabs/agent-squad/issues/661) and present `typescript/src/orchestrator.ts` / `typescript/src/utils/helpers.ts` code | [One `ASSESSMENT_INFORMED / SCREENING` candidate](../candidates/agent-squad-stream-20261021.md) for cancellation/bounded in-memory streaming. Related issues are deliberately **deduplicated into one** research hypothesis. Not a missing S3 executive. |
| [Agent Zero](../sweeps/agent-zero.json): `A/—/—/—/—/—` | Current `agent0ai/agent-zero/main@ff2a5b9c9c4e490ba38dd7c313e779510bb2071a`; [issue #1955](https://github.com/agent0ai/agent-zero/issues/1955) and [`helpers/secrets.py`](https://github.com/agent0ai/agent-zero/blob/ff2a5b9c9c4e490ba38dd7c313e779510bb2071a/helpers/secrets.py) | [One `ASSESSMENT_INFORMED / SCREENING` candidate](../candidates/agent-zero-project-secrets-20261021.md) for project-scoped credential access. Current masking only registers global and active-project secrets; that is **not** by itself proof of full filesystem isolation or an independently rerun exploit. Use synthetic test values only. |
| [agent0](../sweeps/agent0.json): `A/—/—/—/—/—` | Current `xudafeng/agent0/main@3eb4d8b31fa1c0b3ba785c0c773e33bc13f30f65`; bounded upstream issue review | **Zero new supported candidates.** Mission/runtime, tool-result feedback and idempotent side-effect ledger are actual S1 functions; their existence doesn't justify an S3/S4/S5 feature request. |
| [AgentDescent](../sweeps/agentdescent.json): `A/—/—/—/A/—` | Current `Birfy/agentdescent/main@d1cfa8f6eb570d927826278c70aa23b86d3c5264`, [open issue #453](https://github.com/Birfy/agentdescent/issues/453), current [`agentdescent/demo.py`](https://github.com/Birfy/agentdescent/blob/d1cfa8f6eb570d927826278c70aa23b86d3c5264/agentdescent/demo.py) | [One `ASSESSMENT_INFORMED / SCREENING` candidate](../candidates/agentdescent-demo-frontmatter-20261021.md): generated demo `SKILL.md` omits required name/description frontmatter, disabling native structural validation and host skill loading. Does not imply the Index diagnosed a missing S4 mechanism. |

**No fresh native reproduction, before/after or intervention outcome was measured** for these cards; reported symptoms come from first-party issues and pinned source checks. All remain research hypotheses pending four independent native-fit gates. The potentially security-sensitive Agent Zero and Agent Squad reproductions must be local/isolated, not public-service stress or actual credentials.

## Cumulative transparent coverage (pinned Index)

| Source-backed research coverage | Initial | After Batch 005 |
| --- | ---: | ---: |
| Included assessments | 615 | 615 |
| Six-function research receipts | 1 | **29** |
| Individual function decisions | 6 | **174 / 3,690** |
| Systems still awaiting individual review | 614 | **586** |
| Function slots still awaiting review | 3,684 | **3,516** |
| Research candidate cards | 3 | **14**, none `QUALIFIED` or `SELECTED` |

Next deterministic system: `assessments/ag/agentflow.md`. All 615 are in the all-included queue; **only 29 have been individually research-screened**, and review records are still evidence declarations rather than independent native tests. Do not add artificial zero-result receipts or claim those 586 systems are completed.

**Provenance rule:** the only new strict `ASSESSMENT_DERIVED` research hypothesis in these five batches remains the agent-code source-independent reviewer; the four new Batch 005 cards are independently issue-sourced, not reverse-engineered Index findings. No candidate automatically becomes a contribution proposal, code patch, external GitHub PR, S1 delegation or Index VSM grade edit.
