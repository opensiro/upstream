---
candidate_id: IMPR-AGENT-ZERO-PROJECT-SECRETS-20261021
state: SCREENING
origin_class: ASSESSMENT_INFORMED
target_repo: agent0ai/agent-zero
index_sha: 5393b698bfdfa4ca14d97a79238234eca20694e5
assessment_path: assessments/ag/agent-zero.md
review_ref: b1cbd1f960a1a5c4482b324dcff4742aa67b7a51
source_sha: ff2a5b9c9c4e490ba38dd7c313e779510bb2071a
fit_need: PASS
fit_mechanism: PENDING
fit_value: PENDING
fit_scope: PENDING
---

# IMPR-AGENT-ZERO-PROJECT-SECRETS-20261021 — isolate per-project credentials

**Status:** `SCREENING / ASSESSMENT_INFORMED`; not an Index-derived S2/S5 defect. The [frozen Index assessment](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ag/agent-zero.md) recognizes Agent Zero's model-operated desktop/tools and optional delegated agents, but does not identify cross-project secret exposure. Independent [upstream issue #1955](https://github.com/agent0ai/agent-zero/issues/1955) reports one project's agent accessing another project's `.a0proj/secrets.env` during normal task execution.

At currently inspected `main@ff2a5b9c9c4e490ba38dd7c313e779510bb2071a`, first-party [`helpers/secrets.py`](https://github.com/agent0ai/agent-zero/blob/ff2a5b9c9c4e490ba38dd7c313e779510bb2071a/helpers/secrets.py) still constructs `get_secrets_manager()` inputs from global secrets, `usr/.env` and **only the active project**, consistent with the issue's masking gap. This alone proves **masking scope**, not that arbitrary OS-level file reads are preventable or that the current branch independently reproduces the full access scenario. Issue #1955 supplies its own reported reproducer, not an OpenSiro-run exploit.

**Product benefit hypothesis:** project-scoped credential access so a task running for project B cannot read or use project A's credentials without explicit authorization. Broadening text masking of all project credentials is only defense-in-depth; it is **not** an access-control boundary. A real fix likely needs scoped filesystem/tool execution rights, container/user isolation or equivalent OS protection compatible with intended host bridge and multi-project usage.

## Four native fit gates

| Gate | Verdict | Rationale |
| --- | --- | --- |
| Need | `PASS` | First-party issue #1955 specifies a cross-project secret access symptom and current source confirms incomplete masking registration |
| Mechanism | `PENDING` | Actual project identity, tool sandbox, path access and OS user isolation contract must be established |
| Counterfactual benefit | `PENDING` | No isolated A/B project credentials before/after regression test run |
| Scope | `PENDING` | Current maintainer policy, compatibility of shared host access, credential migration and overlapping security fixes unresolved |

**Baseline:** reported issue + current masking source; independent execution `NOT_RUN`. **After:** `NOT_IMPLEMENTED / INCONCLUSIVE`. **Next gate:** synthetic non-secret fixtures representing projects A and B in a controlled local container with no real credentials; verify one project cannot read sibling secrets while allowed same-project use remains intact. No external issue, PR, fork or grade change made.
