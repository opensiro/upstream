# Proposed external PR: kstawiski/evidence-gated-scientific-agent

**State:** internal exact-title/body proposal; not yet approved or published. Do not publish without independently replaying the source-pinned code/test patch into a permitted working branch, completing the source-native checks that apply and obtaining an individual approval of the final title and body. This heading and note are not part of the PR body.

**Proposed title:** `fix: exclude failed retrievals from evidence admission`

## Proposed PR body (copy only after all gates above)

## Summary

- Treat retrieval results with failure-like `status` values (including `error`, `failure`, `timeout` and `canceled`) as failed even if the tool response has no separate `error` field.
- Prevent those responses from increasing `successful_calls` or adding an apparent source URL to the scientific evidence record.
- Add a negative failed-retrieval fixture and a positive successful-retrieval control to the existing policy tests.

## Why

A failed retrieval can contain a URL in its error message. That URL is **not evidence** that the referenced content was fetched, so it must not pass the evidence-admission guard.

## Validation

- Historical independent first-party source CI at `main@85b396a824dfad6ec0880cbe07d86d3e24920ae8`: failing negative case before the fix, then **16/16 policy tests PASS** after the patch. [Internal OpenSiro CI](https://github.com/opensiro/upstream/actions/runs/40026575626).
- The upstream SHA was unchanged at publication preflight, but the full source-required `uv run pytest -m "not live"` and adjacent lint/integration were **not certified passing by this preflight**. No live model/MCP, real retrieval or science benchmark outcome is claimed.
- [Exact reviewed patch at archived internal head](https://github.com/opensiro/upstream/blob/0d205f12b92abd1c7ecf55c5b31ff7056354b93a/pilots/evidence-bench/retrieval-error-admission.patch).

<!-- opensiro-ai-assessment-disclosure:v2 -->
## AI-assisted contribution disclosure

**VSM assessment:** [Current record](https://github.com/opensiro/vsm-harness-index/blob/main/assessments/ev/evidence-bench.md) · [Snapshot used for this PR](https://github.com/opensiro/vsm-harness-index/blob/396a54bb690f8ec7ce966bf9b00b241b30036307/assessments/ev/evidence-bench.md)

**Assessment date:** 2026-10-17 (`reviewed_at`) · **Assessed source revision:** `85b396a824dfad6ec0880cbe07d86d3e24920ae8`

This PR was prepared by the [OpenSiro Upstream Contributions](https://github.com/opensiro/upstream) AI-agent workflow, informed by the VSM assessment linked above. Technical analysis, code changes and reported checks were agent-driven; no independent human code review is claimed. For now, a human approves publication while monitoring the pipeline for errors. That approval is **not** a technical correctness guarantee. Fully autonomous publication is a future goal, **not** the status of this PR. AI-generated changes may be incomplete or incorrect; please review the diff and evidence independently.

The assessment describes the assessed source revision on the stated date; it is not a guarantee about this PR or later upstream code. Maintainers and their agents can compare the current record with the snapshot and reassess if the source or evidence has changed.
