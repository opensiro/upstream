# Conversation-first contribution proposals (read-only)

This is the **provider-agnostic, local-only proposal surface** for OpenSiro
Upstream. It allows any conversational agent or operator to examine a bounded
batch, describe the actual improvement to each target system and select
candidate IDs **for preview only**.

**Important:** This module performs **no GitHub requests or writes**, does not
create forks, prepare patches, submit external pull requests or store
authorization. It contains no token integration, no reusable approval receipt
and no privileged executor. Neither a selected item nor a digest authorizes
any operation.

The source code is [`scripts/batch_proposals.py`](../scripts/batch_proposals.py).
The proposed write-execution contract remains separate in
[Issue #6](https://github.com/opensiro/upstream/issues/6) and
[Draft PR #7](https://github.com/opensiro/upstream/pull/7).

## One candidate is a concrete system improvement plan

Each candidate explains what part of the *target upstream* changes, the
source-backed problem, a bounded change, its **expected/unverified** benefit,
and the planned validation. Optional VSM relevance can inform discovery,
but it neither proves a capability improvement nor changes a canonical
assessment state.

| Field | Meaning |
| --- | --- |
| `id` | Unique stable candidate ID |
| `source` | Target upstream `OWNER/REPOSITORY` |
| `fork_name` | Planned fork name, not an existing/created fork |
| `stages` | Proposed permission stages, **not authorization** |
| `expected_license` | Recorded SPDX observation; `null` requires a blocker |
| `proposal.system_component` | Concrete upstream component/workflow |
| `proposal.problem` | Observable issue and reason for change |
| `proposal.planned_change` | What exactly should change |
| `proposal.expected_improvement` | Hypothesis, **not a measured result** |
| `proposal.validation` | Regression tests, acceptance checks or other evidence needed |
| `proposal.evidence_url` | HTTPS source/issue URL; syntactic validation does **not** verify the claim |
| `blockers` | Outstanding risks or absent evidence; blocked items are **not executable** |

The supported proposed stages, in dependency order, are
`create_public_fork`, `prepare_contribution`, `submit_external_pr`.
A row may include several stages, but no stage is implemented for execution
by this component. External upstream maintainers retain all rights to accept
or merge an external PR. Forks are not archived by this component.

## Draft manifest shape

Use a **local** file named `upstream-YYYYMMDD-slug.json`, up to 16 KiB.
It contains 1–10 candidates and **does not** contain `approved_by`,
`approval_ref`, `approved_at` or any agent-generated assertion of consent.

**Synthetic syntax illustration only** — `example/project-a` and its issue
URL are placeholders, not verified external evidence; the license is not
attested for this fictional repository.

```json
{
  "schema_version": 1,
  "batch_id": "upstream-20261018-synthetic",
  "revision": 1,
  "status": "proposal_only",
  "candidates": [
    {
      "id": "project-a",
      "source": "example/project-a",
      "fork_name": "project-a",
      "stages": ["create_public_fork", "prepare_contribution"],
      "expected_license": "MIT",
      "proposal": {
        "system_component": "Task handoff controller",
        "problem": "An interrupted handoff may leave the task owner ambiguous",
        "planned_change": "Add explicit handoff outcomes and a regression test",
        "expected_improvement": "Better task owner traceability after interruption",
        "validation": "Test interrupted/rejected transfers in the source project",
        "evidence_url": "https://github.com/example/project-a/issues/1"
      },
      "blockers": []
    }
  ]
}
```

Save that example as `/tmp/upstream-20261018-synthetic.json`. Preview it:

```bash
python3 scripts/batch_proposals.py \
  --manifest /tmp/upstream-20261018-synthetic.json \
  --draft --select project-a --format text
```

Omit `--format text` to receive JSON. Selecting an unknown or duplicate ID
is an error. A blocked entry can appear **selected for preview**, but
`selection_has_blockers: true` remains visible and **never grants
permission**. Use `--draft` deliberately; `--execute` is unsupported.

## Integrity and interpretation

The renderer returns:

- `status: PROPOSAL_PREVIEW`
- `authorization_status: NOT_APPROVED_NO_WRITES`
- `proposal_sha256`: canonical JSON digest of the complete draft;
- `selection_sha256`: canonical digest binding the **set** of selected IDs
  to that draft and revision, independent of selection order.

Reformatting JSON does not alter these hashes. Changing the plan, revision,
candidate list or selected IDs does. They are **unsigned identity keys for
review**, not authenticated human approvals, write permissions, evidence of
upstream consent or verification that cited URLs support the proposed claim.

## Known limits and next scope

This implementation checks local JSON schema, basic source/name shapes,
lengths, duplicate destinations, planned stage order, evidence URL syntax,
and blockers. It **does not access GitHub** to check repository existence,
license compatibility, source evidence, upstream policy or actual outcome.

A later executor may be an authorized conversational agent or a restricted
headless runner. Either will need a separate, genuinely attributable decision,
explicit per-item/stage scope, credentials controlled outside this module,
and its own tests before any writes. Do not turn the older single-fork helper
into an approval bypass, install `UPSTREAM_FORK_TOKEN`, or interpret
demonstration batch #001 as approved.

Local validation on this isolated preview implementation: **32/32 offline
positive/negative cases passed** (including network-disabled invocation,
selection hashes, bad stages and no `--execute`). These tests have **not**
been published as dedicated GitHub batch CI, so this claim must not be
confused with a passing batch-specific required check.
