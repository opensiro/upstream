# agentUniverse — opt-in Implementation–Supervision halt (source only)

Status: TECHNICALLY_VALIDATED_SOURCE_ONLY; external publication NOT AUTHORIZED.
No external fork, issue, PR or merge has been created by this pilot.

## Source and screening

- Canonical Index: opensiro/vsm-harness-index main@32f6f7a4bc0ed244e909613ed2bd440adc054b3d
- Included assessment: assessments/ag/agentuniverse.md; S1=A; S2/S3/S3*/S4/S5=—.
- First-party code: agentuniverse-ai/agentUniverse master@925101e96a465a7d750701f6d768c835fe30593a.
- Apache-2.0 license verified **before** work. CONTRIBUTING.md and
  .github/pull-request-template.md inspected; future external submission
  must meet maintainer consultation, tests and docs requirements.
- Scoped duplicate searches across both open and closed issues/PRs:
  no existing halt-on-exhausted-correction implementation found.
  First-party issue #4140 and open PRs #4141/#4142 address parsing of
  supervision verdicts, a **separate but relevant dependency**. Broad
  repository-wide duplicate certification is not claimed.

## Native function

The shipped Implementation–Supervision work pattern repeatedly asks a
supervisor whether a checkpoint requires correction. When the configured
correction budget is already spent, default code continues later checkpoints
and returns the last result.

An optional `halt_on_unresolved_correction=True` setting now:

- stops further checkpoints when supervision rejects work and the budget
  cannot authorize a correction;
- records `halt_checkpoint` and machine-readable
  `UNRESOLVED_SUPERVISION_CORRECTION_LIMIT`;
- withholds the rejected final output from ISAgentTemplate.parse_result;
- works in both synchronous and asynchronous methods;
- retains original behavior when unset (False).

The implementation calls only original ISWorkPattern and ISAgentTemplate
source. The tests use scripted first-party Implementation/Supervision classes
and make **no model/provider requests**.

## Before/after

- BEFORE: new five tests: 3 FAIL / 2 PASS. The two default-compatibility
  tests pass; opt-in halt and user-facing config propagation are absent.
- AFTER: all five new tests PASS. Together with existing IS and peer,
  agent template, InputObject and OutputObject native tests: **25 PASS / 0 FAIL**.
- `git diff --check`, Python compileall and pristine first-party
  `git apply --check`: PASS.
- Runtime environment: separate local Python 3.12 venv with constrained
  langchain 0.1.x and MCP 1.21.2. Old package has Pydantic compatibility
  warnings. Full repository suite NOT CERTIFIED.
- Source patch: `halt-on-unresolved-supervision.patch`, applicable to
  the pinned first-party commit.

```bash
PYTHONPATH=. .venv/bin/python -m pytest -q \
  tests/test_agentuniverse/unit/agent/test_is_supervision_halt.py \
  tests/test_agentuniverse/unit/agent/test_is_work_pattern.py \
  tests/test_agentuniverse/unit/agent/test_is_correction_output.py \
  tests/test_agentuniverse/unit/agent/template/test_supervision_agent_template.py \
  tests/test_agentuniverse/unit/agent/test_peer_work_pattern.py \
  tests/test_agentuniverse/unit/agent/test_input_object.py \
  tests/test_agentuniverse/unit/agent/test_output_object.py
```

## Attribution, fit and limitations

The Index describes IS as a **task-level** feedback/correction loop, not
whole-system S3/S3*. The specific failure-to-halt condition was established
from current first-party code and scripted tests. This is
ASSESSMENT_INFORMED, not a completed ASSESSMENT_DERIVED #56 experiment.

The feature stops on the *reported* verdict; it cannot validate the
accuracy of that verdict. In particular, current first-party #4140/#4141/#4142
must be reviewed independently before claiming reliable real-user
rejection handling. No live LLM evaluation, downstream user effect, new
S3/S3* ownership or maintainer acceptance is established.

Native fit: mechanistic need PASS (continuation observed), architecture
PASS (opt-in sync/async IS path), bounded counterfactual PASS (3-stage run
shortened to 2 on unresolved rejection), maintainer acceptance PENDING.
The 34-case Corrective S5 mandate does not cover external publication of
this new Improvement.
