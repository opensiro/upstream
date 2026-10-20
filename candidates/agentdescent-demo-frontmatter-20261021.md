---
candidate_id: IMPR-AGENTDESCENT-DEMO-SKILL-20261021
state: SCREENING
origin_class: ASSESSMENT_INFORMED
target_repo: Birfy/agentdescent
index_sha: 5393b698bfdfa4ca14d97a79238234eca20694e5
assessment_path: assessments/ag/agentdescent.md
review_ref: d1cfa8f6eb570d927826278c70aa23b86d3c5264
source_sha: d1cfa8f6eb570d927826278c70aa23b86d3c5264
fit_need: PASS
fit_mechanism: PENDING
fit_value: PENDING
fit_scope: PENDING
---

# IMPR-AGENTDESCENT-DEMO-SKILL-20261021 — generated demo skill must be host-loadable

**Status:** `SCREENING / ASSESSMENT_INFORMED`. [AgentDescent Index assessment](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ag/agentdescent.md) credits S4=A because an agent can autonomously propose and select persistent prompt/skill improvements across evaluated task distributions. It does **not** diagnose the particular sample SKILL.md structure or its host-loading incompatibility.

[First-party issue #453](https://github.com/Birfy/agentdescent/issues/453) reports that `agentdescent demo` creates `csv-total/SKILL.md` lacking frontmatter. Validation then disables its structural gate and, when copied to OpenCode/Claude Code/Codex, the example is not discovered as an actual skill. Current [`agentdescent/demo.py`](https://github.com/Birfy/agentdescent/blob/d1cfa8f6eb570d927826278c70aa23b86d3c5264/agentdescent/demo.py) defines `_SKILL_MD` beginning with Markdown title rather than required frontmatter and writes it to `SKILL.md`, confirming the issue's source premise.

**Native change hypothesis:** emit minimal valid `name` and task-triggered `description` frontmatter for the demo skill, keeping the existing intentionally wrong rule, offline reflector and replay/expected outcome unchanged. Prove the generated output passes first-party validation and an actual supported host lists the skill. Do not use only a string-prefix assertion as evidence of actual host interoperability.

## Four native fit gates

| Gate | Verdict | Evidence |
| --- | --- | --- |
| Need | `PASS` | Specific native issue #453 and observed current `_SKILL_MD` generator |
| Mechanism | `PENDING` | Exact frontmatter, validator contract and doc compatibility not yet implemented/tested |
| Counterfactual benefit | `PENDING` | No matched native demo + OpenCode/Claude/Codex host-loading before/after |
| Scope | `PENDING` | Check maintainer's competing PR and ensure demo educational semantics, fixtures and tests stay intact |

**Baseline:** issue-reported host behavior, source-consistent; independent host test `NOT_RUN`. **After:** `NOT_IMPLEMENTED`. **Next gate:** add isolated deterministic test `demo → validate_skill_tree`, then a small fix and real host discovery smoke, preserving the original offline evaluation. **Not** a verified S4 grade change or contribution. No third-party files/issue/PR written.
