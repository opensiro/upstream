---
candidate_id: IMPR-AGENTDESCENT-DEMO-SKILL-20261021
state: REJECTED
origin_class: ASSESSMENT_INFORMED
target_repo: Birfy/agentdescent
index_sha: 5393b698bfdfa4ca14d97a79238234eca20694e5
assessment_path: assessments/ag/agentdescent.md
review_ref: d1cfa8f6eb570d927826278c70aa23b86d3c5264
source_sha: d1cfa8f6eb570d927826278c70aa23b86d3c5264
fit_need: PASS
fit_mechanism: PASS
fit_value: PENDING
fit_scope: PENDING
---

# IMPR-AGENTDESCENT-DEMO-SKILL-20261021 — generated demo skill must be host-loadable

**Status:** `REJECTED / SUPERSEDED_BY_UPSTREAM_MERGE` for a new OpenSiro intervention; historical origin `ASSESSMENT_INFORMED`. [AgentDescent Index assessment](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ag/agentdescent.md) credits S4=A because an agent can autonomously propose and select persistent prompt/skill improvements across evaluated task distributions. It does **not** diagnose the particular sample SKILL.md structure or its host-loading incompatibility.

[First-party issue #453](https://github.com/Birfy/agentdescent/issues/453) reports that `agentdescent demo` creates `csv-total/SKILL.md` lacking frontmatter. Validation then disables its structural gate and, when copied to OpenCode/Claude Code/Codex, the example is not discovered as an actual skill. Current [`agentdescent/demo.py`](https://github.com/Birfy/agentdescent/blob/d1cfa8f6eb570d927826278c70aa23b86d3c5264/agentdescent/demo.py) defines `_SKILL_MD` beginning with Markdown title rather than required frontmatter and writes it to `SKILL.md`, confirming the issue's source premise.

**Native change hypothesis:** emit minimal valid `name` and task-triggered `description` frontmatter for the demo skill, keeping the existing intentionally wrong rule, offline reflector and replay/expected outcome unchanged. Prove the generated output passes first-party validation and an actual supported host lists the skill. Do not use only a string-prefix assertion as evidence of actual host interoperability.

## Four native fit gates

| Gate | Verdict | Evidence |
| --- | --- | --- |
| Need | `PASS` | Specific native issue #453 and observed current `_SKILL_MD` generator |
| Mechanism | `PASS` | [Internal native patch PR #68](https://github.com/opensiro/upstream/pull/68) reproduces red-to-green using the first-party `validate_skill_tree`, `plan`, and replay against the exact original source SHA |
| Counterfactual benefit | `PENDING` | First-party gate changed from `['no-frontmatter']` to `[]` and 219/219 scoped native tests passed on clean patch replay; real OpenCode/Claude/Codex host discovery and full CI remain unverified |
| Scope | `PENDING` | No competing PR found in bounded search; tests preserve demo semantics, but full native CI and external host validation are outstanding; external publication is human-controlled |

**Implementation checkpoint (2026-10-21):** [Internal OpenSiro Draft PR #68](https://github.com/opensiro/upstream/pull/68) contains a [three-file native patch and exact red/green receipt](https://github.com/opensiro/upstream/blob/pilot/agentdescent-453-native-fix-20261021/pilots/agentdescent-453/README.md). On exact current upstream `main@d1cfa8f`, the original demo returns `['no-frontmatter']` under the project's validator; the new regression test fails. After applying the patch to an **independent clean checkout**, the same validator returns `[]`, demo `plan` does not disable the structural skill gate, and **219/219 scoped native tests PASS** (98.37 seconds). `git apply --check` and focused **114/114 tests PASS** as well. Patch SHA-256: `2910c29c7236dc8c351920510068e236b54114e1c5a1d043700c7b5777e5265b`.

**Remaining blockers:** real host discovery `NOT_RUN`, complete upstream `pytest -q` `NOT_COMPLETE` (interrupted at ~5%), upstream CI `NOT_RUN`, upstream maintainer review `NOT_STARTED`. The evidence supports a local native **format/gate behavior improvement**, not an externally adopted or released product improvement. Candidate stays `SCREENING` with `fit_value` and `fit_scope` `PENDING`, no `QUALIFIED` or `SELECTED` promotion. This remains `ASSESSMENT_INFORMED`, **not** a diagnosis of missing S4 from Index. No third-party code, issue, PR, fork or Index grade was written.

## Fresh upstream deduplication — 2026-10-21

**No further OpenSiro implementation or external PR is warranted.** First-party [Birfy/agentdescent PR #459](https://github.com/Birfy/agentdescent/pull/459), titled `fix(demo): the csv-total demo skill is a valid Agent Skill`, **merged on 2026-10-21 at 06:37:42 UTC**; [issue #453](https://github.com/Birfy/agentdescent/issues/453) is now closed. Target `main` advanced to `e38098339f04dcccf5483af2d54fb2bac43cf85d` at inspection. This supersedes internal [OpenSiro Draft PR #68](https://github.com/opensiro/upstream/pull/68) as an external submission proposal. Its frozen earlier red/green receipt remains historical **OpenSiro source engineering only**; it is not proof we authored the already merged upstream change. No shared source, credit, external PR or maintainer acceptance should be invented. Candidate research decision: `REJECTED` **because product change already landed**, not due to negative functional value.
