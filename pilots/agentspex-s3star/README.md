# AgentSPEX — offline YAML checkpoint preflight (source-only)

Status: TECHNICALLY_VALIDATED_SOURCE_ONLY / AWAITING_EXTERNAL_PUBLICATION_AUTHORITY.
External AgentSPEX PR, fork, or issue: NONE. This internal PR is not an
upstream contribution and no product rollout is claimed.

## Origin and source

- Canonical Index main: 32f6f7a4bc0ed244e909613ed2bd440adc054b3d
- Assessment: assessments/ag/agentspex.md (included, S1=A, S3*=—).
- First-party code: ScaleML/AgentSPEX main@db99b7b6802fe15ef2997c82ec1d49e5228128f6
- License: Apache-2.0, verified before technical work.
- Contributor policy: no CONTRIBUTING.md or .github issue/PR template present in this snapshot.
- Duplicate search: all 22 first-party issue-channel records including 20 PRs,
  no overlapping offline checkpoint inspection implementation (the only
  stand-alone issues are #1 and #2).
- Source patch: checkpoint-inspection.patch, applicable to the pristine commit.

## Bounded feature

Add the opt-in `agentspex inspect-checkpoint PATH` command, returning
machine-readable JSON and exit code 2 on unsafe/missing state. The command
checks checkpoint type/schema version, optional task/step count, duplicate
completed IDs, malformed JSON and optionally missing top-level step-output
files. It opens no model connection, box or MCP service and changes no
checkpoint files. Legacy `agentspex run --resume` behavior is unchanged.

### Native baseline vs changed source

- Before: the preflight API and CLI command do not exist. Running the new
  test file against original source fails at module import
  (`ModuleNotFoundError: harness.checkpoints.inspection`).
- Existing baseline runtime: src/harness/agent.py warns on invalid checkpoint
  kind/version but proceeds with loaded state; no first-party inspection CLI.
- After: 12 new deterministic inspector cases PASS, including an actual
  `python -m harness.ephemeral.cli inspect-checkpoint` subprocess test
  for valid JSON exit 0 and mismatched kind exit 2.
- Total selected native tests: 183 PASS / 0 FAIL (checkpoint inspection,
  checkpoint manager, workspace manifest, trace replay, tracing, conditions).
- Validation: Python compileall PASS; git diff --check PASS;
  `git apply --check` against a detached pristine original worktree PASS.
- Warning: project's `pytest` config refers to asyncio_mode but the selected
  environment does not install pytest-asyncio. No live provider, LLM-agent or
  Browser tests were run. Full repository suite NOT CERTIFIED.

Run only deterministic tests:

```bash
PYTHONPATH=src .venv/bin/pytest -q \
  tests/tool_tests/test_checkpoint_inspection.py \
  tests/tool_tests/test_checkpoint_manager.py \
  tests/tool_tests/test_workspace_manifest.py \
  tests/tool_tests/test_trace_replay.py \
  tests/tool_tests/test_tracing.py \
  tests/tool_tests/test_conditions.py
```

### Evidence and boundaries

This is a useful *hypothesized* offline pre-resume check around a subsystem
identified by the Index. The exact unverified checkpoint-preflight need was
found by reading first-party source, not diagnosed by the canonical VSM
assessment; classify as ASSESSMENT_INFORMED, **not a completed
ASSESSMENT_DERIVED #56 chain**. It does not create an independent S3* auditor
or authenticate checkpoint outputs. The checked before/after effect is
presence of a deterministic preflight, not reduced real incident rate or
acceptance by ScaleML maintainers.

Native-fit: need PENDING (no maintainer demand), mechanism PASS, bounded
counterfactual detection PASS, implementation scope PASS. The strict-derived
#56 outcome remains unproven.

No S5 permission extends the 34-case Corrective publication cohort to this
new Improvement case. External publication and maintainers' review remain
separate stages.
