# Improvement candidate backlog (research-only DRAFT)

This directory is a proposed **Upstream-owned research intake**, separate from [`registry.yaml`](../registry.yaml) (real forks/contributions), [`cases/`](../cases/README.md) (observed portfolio), and the existing [`batch_proposals.py`](../docs/BATCH_PROPOSALS.md) (selected proposal-only GitHub stages).

**No candidate card is authorization to create a fork, change an external project or submit an upstream issue/PR.** See the [design and status contract](../docs/IMPROVEMENT_CANDIDATES_PIPELINE_DRAFT.md) and [Upstream #56](https://github.com/opensiro/upstream/issues/56). Dates/SHAs reflect source snapshots inspected 2026-10-20–21, **not live future state**. Actual issue/PR/source status must be refreshed before execution.

## Index-wide source of improvement hypotheses

New assessment-derived work begins with the **full included Index queue**, not keyword-filtered S2-only shortlists. Run [the read-only all-six-function sweep](../sweeps/README.md) at a trusted frozen Index HEAD and record separate S1 / S2 / S3 / S3* / S4 / S5 function decisions **for each included system**. Every system yields **zero to many** hypotheses; missing reviews are *not* zero-candidate outcomes. Current [coverage baseline and outstanding count](../reports/2026-10-21-full-index-function-sweep-bootstrap.md) is source-pinned, not an assumption about all future Index commits.

This `candidates/` directory represents only concrete hypotheses **after** such analysis; it must not be filled with one card per system just to make its size match the Index. Hypothesis discovery/coverage and independent target-native demand/fit are separate stages. An `ASSESSMENT_INFORMED` candidate can coexist in the pool but never gets upgraded to `ASSESSMENT_DERIVED` merely because its target was included in the full sweep.

## Offline candidate integrity check (proposed)

Run the **read-only local structural inspector** on this directory:

```bash
python3 scripts/inspect_improvement_candidates.py --root candidates --format text
python3 -m unittest discover -s tests -p 'test_inspect_improvement_candidates.py' -v
```

Cards use a small, strictly parsed YAML-like **scalar frontmatter** for identity, original Index pin, current target source pin, candidate state and four native-fit gate declarations. Duplicate IDs, malformed pins, missing supporting prose, unsupported status values and `QUALIFIED/SELECTED` claims with incomplete gates fail closed. A dedicated credential-free [CI workflow](../.github/workflows/improvement-candidates.yml) runs these checks.

**Critical:** This inspector checks only local syntax and internal consistency. The displayed `declared_fit_complete` boolean is a *card author's declaration*, **not** independent verification. It never reads live Index/target repositories or accepts/fabricates authorization, and its output always says `candidate_transition_authorized=false` and `NOT_APPROVED_NO_GITHUB_WRITES`. A real transition to the existing proposal preview still requires separate source/fit verification and operator decision. No input flag can trigger proposal generation or GitHub writes.

## Linkage to the existing proposal-only path

The [read-only candidate-to-proposal linker](../scripts/improvement_candidate_linkage.py) checks an **already** qualified/selected assessment-linked candidate against an **already authored** `batch_proposals.py` manifest item and local pinned Index assessment object. It rejects blocked cards/proposals, different target repositories, changed assessment refs and dishonest `QUALIFIED` flags with incomplete native-fit declarations. It never creates a candidate, draft or permission; see the [detailed design and example](../docs/IMPROVEMENT_CANDIDATES_PIPELINE_DRAFT.md#offline-candidate-to-existing-proposal-linkage-prototype-still-not-promotion). No current card is qualified or selected, so only **synthetic isolated test fixtures** cover a positive linkage; real product fit and canonical live source checks remain external human/agent duties.

## Initial candidates (not a ranked or approved queue)

| Candidate | Provenance of specific hypothesis | Research state | Next gate |
| --- | --- | --- | --- |
| [AgentBox: prevent overlapping independent box dispatch](agentbox-overlap-manager-20261020.md) | Index assessment directly names **manual** cross-box conflict coordination | `BLOCKED_EVIDENCE` | First-party manager design / intended path scopes |
| [AgentBox: dependency readiness semantics](agentbox-dependency-readiness-20261020.md) | Precise observation surfaced in subsequent source inspection; **assessment-informed**, not a separate Index diagnosis | `PARKED` | Does `dependsOn` constrain worker dispatch or merely task allocation? |
| [Zot: shared-root write preservation](zot-shared-write-20261020.md) | Index assessment directly identifies shared writable RepoRoot and absent inter-worker arbiter | `PARKED` | Show demand for *built-in* behavior over manual worktrees |
| [Kit: partial subagent config startup failure](kit-subagent-config-20261021.md) | First-party open [issue #222](https://github.com/speakeasy-api/kit/issues/222), **assessment-informed** rather than derived S2 finding | `SCREENING` | Reproduce current-main startup failure and determine narrow safe fallback |
| [A-Evolve: evolved harness executable hook hardening](a-evolve-harness-exec-20261021.md) | Index S4 workspace-evolution path informed the review; exact code-execution problem came from [issue #28](https://github.com/A-EVO-Lab/a-evolve/issues/28), **not** diagnosed in Index | `SCREENING` | Current-source isolated canary test, trust contract, and bounded containment design |

| [Agency Swarm: unexpected tracing egress](agency-swarm-tracing-endpoint-20261021.md) | Native [issue #828](https://github.com/VRSEN/agency-swarm/issues/828), **assessment-informed**, not missing S2/S5 evidence | `SCREENING` | Check endpoint override/explicit tracing opt-in with mocked HTTP egress |
| [agent-code: fresh-context isolated reviewer](agent-code-isolated-reviewer-20261021.md) | **Assessment-derived S3* research hypothesis** and independent [upstream issue #524](https://github.com/avala-ai/agent-code/issues/524); rubric and review targets are **already shipped** | `SCREENING` | Confirm remaining subagent isolation gap and prove bounded review usefulness |
| [agent-code: concurrent background task output IDs](agent-code-background-output-20261021.md) | Independent [upstream issue #515](https://github.com/avala-ai/agent-code/issues/515), **assessment-informed** | `SCREENING` | Multi-process live output collision test and namespace/adoption migration |
| [Agent Harness Core: backoff gateway restart](agent-harness-core-backoff-restart-20261021.md) | Native [issue #22](https://github.com/phenomenoner/agent-harness-core/issues/22), **assessment-informed** | `SCREENING` | Reproduce Windows restart with one backoff child, preserve fail-closed owner identity |
| [Agent Orchestrator: reviewer no-write contract](ao-reviewer-readonly-20261021.md) | Independent [upstream #6962](https://github.com/OrchestratorInc/agent-orchestrator/issues/6962); **assessment-informed**, with historical alias now redirected to the owning repo | `SCREENING` | Validate true read-only shell sandbox and submit contract against current maintainer policy |

| [Agent-S: typed text is not terminal control](agent-s-cli-action-20261021.md) | Native [#235](https://github.com/simular-ai/Agent-S/issues/235), **assessment-informed** | `SCREENING` | Check reporter's incoming fix, add exact action-status regression |
| [Agent Squad: bound streaming after disconnect](agent-squad-stream-20261021.md) | Native [#662](https://github.com/2FastLabs/agent-squad/issues/662) and overlapping #661, **assessment-informed** | `SCREENING` | Mock provider stream, abort propagation, retained memory cap |
| [Agent Zero: cross-project credential isolation](agent-zero-project-secrets-20261021.md) | Native [#1955](https://github.com/agent0ai/agent-zero/issues/1955), **assessment-informed** | `SCREENING` | Synthetic isolated project A/B credentials and true access boundary |
| [AgentDescent: host-loadable demo skill](agentdescent-demo-frontmatter-20261021.md) | Native [#453](https://github.com/Birfy/agentdescent/issues/453), **assessment-informed** | `SCREENING` | Generated SKILL.md valid frontmatter and actual host discovery smoke |The Kit candidate is an independently useful **assessment-informed** alternative, **not** a strict assessment-derived test win; an existing external issue does not become an OpenSiro contribution by appearing here.

See the [Batch 003 ten-system full-function screen](../reports/2026-10-21-index-sweep-batch-003.md) and the [bounded 2026-10-21 Index-first screen](../reports/2026-10-21-improvement-candidates-index-screen.md) for independently checked non-selections and the Kit-specific classification rationale. This is not a new exhaustive Index assessment or promotion of Issue #222 into a completed product improvement.

**Not every screened harness becomes a candidate.** Claw Code, KairoCode, AtomCode and Dendrophis were documented as negative or unqualified alternative screens in [AgentBox source-screen receipt](../pilots/agentbox-s2/NATIVE_FIT_DECISION_AND_ALT_SCREEN_2026-10-20.md); they are **not** approved backlog entries or discarded assessments. This is a bounded example set.

## Minimum card template

Copy for a substantively new, independently screenable **one-change hypothesis**; keep the exact snapshot and reference original owner issues as sources rather than converting card prose into new authority.

```markdown
# candidate_id — short improvement title
Status: DISCOVERED | SCREENING | BLOCKED_EVIDENCE | QUALIFIED | SELECTED | PARKED | REJECTED
Origin: ASSESSMENT_DERIVED | ASSESSMENT_INFORMED | GENERAL_UPSTREAM | INSUFFICIENT
Owner issue: link (if exists)
Target: OWNER/REPO; current source SHA (observed YYYY-MM-DD)
Index: immutable Index SHA/path + assessed review_ref + exact finding (if applicable)
Selection-order evidence: evidence or UNKNOWN

## Native behavior, problem, and independent demand
Observed vs hypothesized; first-party sources and exact limits.

## One bounded intervention and falsifier
Expected native benefit, legitimate null/negative outcome, design alternatives.

## Four native-fit gates
Need: PASS / PENDING / FAIL — evidence
Mechanism: PASS / PENDING / FAIL — evidence
Counterfactual benefit: PASS / PENDING / FAIL — evidence
Scope: PASS / PENDING / FAIL — evidence

## Test/effect vs contribution
Baseline: NOT_RUN / MEASURED; source and receipt
After: NOT_TESTED / ...; quantitative result and regressions, or absent
Downstream: existing proposal/fork/PR refs only if real

## Next gate and decision owner
One concrete next validation, what blocks it, and where its decision is owned.
```

To prevent stale duplicates, retain one stable candidate ID for the hypothesis and link evidence/issue comments rather than rewriting prior receipts. Fork lifecycle continues in `registry.yaml` only after a fork exists.
