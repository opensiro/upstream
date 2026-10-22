# Included Index full-function sweep — Batch 001 (five systems)

**Date:** 2026-10-21. **Owning research contract:** [Upstream #56](https://github.com/opensiro/upstream/issues/56). **Internal implementation:** [Draft PR #67](https://github.com/opensiro/upstream/pull/67). **Input:** publicly verified Index `main@5393b698bfdfa4ca14d97a79238234eca20694e5`, each assessment's immutable `review_ref`.

**Scope:** the **first five included and previously unreviewed Index assessments in deterministic path order**. The [all-included function sweep](../scripts/sweep_index_assessments.py) verified that all five current Index objects have valid identity and six function sections. Each [`sweeps/<id>.json`](../sweeps/README.md) contains **six independently described decisions**. This is a bounded **assessment-evidence hypothesis review**, *not* fresh per-system full product source audits, native tests, new canonical VSM assessments or an exhaustive list of upstream defects.

## Batch decisions

| Included Index assessment @ assessed commit | S1 / S2 / S3 / S3* / S4 / S5 | Function-screen result | Native current-state check |
| --- | --- | --- | --- |
| [A-Evolve](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/a-/a-evolve.md) `18ba996d` | `A / — / — / C / A / —` | [6/6 receipt](../sweeps/a-evolve.json): S4 **one candidate**, five function slots `REVIEWED_ZERO` | Target current `main@18ba996dac9843f2759b2cdf8a94022f58fbfeb9`; [issue #28](https://github.com/A-EVO-Lab/a-evolve/issues/28) and two source paths corroborate syntactic validation vs dynamic module execution. [Candidate card](../candidates/a-evolve-harness-exec-20261021.md): `ASSESSMENT_INFORMED / SCREENING`, not claimed Index-derived |
| [Abhed](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ab/abhed.md) `151b8ddc` | `A / A / — / A / — / —` | [6/6 receipt](../sweeps/abhed.json): zero new candidates | Target current `main@7953dc61c50cf6802f5605aef34a33840cb5d56e`; shipped worktree interference attenuation and reviewer subsystems are explicitly accounted for. Open [PTY flake issue #123](https://github.com/zybuu-ai/abhed/issues/123) is a repository/CI concern, not supported as an Index-derived operational S3 mechanism |
| [acc](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ac/acc.md) `47dba4bd` | `A / — / — / — / — / —` | [6/6 receipt](../sweeps/acc.json): zero new candidates | Target current `main@96aefec321e2d71ebfd68e3e05fe1d10a3236c57`; no open issue was found in bounded issue check; a permission judge is not an independent correctness auditor and generic child invocation is not evidenced sibling interference |
| [Active Graph](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ac/active-graph.md) `50d84059` | `A / — / — / — / — / —` | [6/6 receipt](../sweeps/active-graph.json): zero duplicate candidates | Target current `main@50d8405923b79e4e823a73a3045bb969436a872c`; actual [projection stale-state issue #82](https://github.com/yoheinakajima/activegraph/issues/82) has governing maintainer treatment in [open Draft PR #86](https://github.com/yoheinakajima/activegraph/pull/86). No extra contribution needed from this bounded screen |
| [ActWeave](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ac/actweave.md) `ea0451ac` | `A / — / — / — / — / —` | [6/6 receipt](../sweeps/actweave.json): zero new candidates | Target current `main@ea0451acc090977c14c1c8d9d0b4d2bee5df4238`; bounded issue check found no open product request. Native management-plane tooling and audit logs do not establish a specifically needed replacement S3/S3* capability |

## Origin accuracy and negative results

For A-Evolve, the Index documents model-directed evolution of persistent workspace capability (S4); it **does not** diagnose the particular issue of `harness.py` module-level execution. During independent target-native checking, pre-existing [upstream #28](https://github.com/A-EVO-Lab/a-evolve/issues/28) reports a reproduction; current first-party [candidate validator](https://github.com/A-EVO-Lab/a-evolve/blob/18ba996dac9843f2759b2cdf8a94022f58fbfeb9/agent_evolve/algorithms/meta_harness/engine.py) still checks syntax with `compile()`, and current first-party [harness loader](https://github.com/A-EVO-Lab/a-evolve/blob/18ba996dac9843f2759b2cdf8a94022f58fbfeb9/agent_evolve/protocol/base_agent.py) invokes `exec_module()`. This yields **one `ASSESSMENT_INFORMED` hypothesis**, not a completed native experiment, security exploit claim or assessment-derived S4 finding.

A separate `REVIEWED_ZERO` for a function means this **bounded reading did not justify a concrete independent product change**. It does not prove that upstream code is defect-free, that every known issue was inspected, or that a positive VSM grade exempts a system from future improvements. In particular, do not treat Active Graph's pre-existing PR as our own contribution or automatically count its resolution.

## Coverage result (source-pinned, not a rolling fact)

| Coverage measure | Before Batch 001 | After Batch 001 |
| --- | ---: | ---: |
| Included assessments at pinned Index | 615 | 615 |
| Declared six-function reviewed systems | 1 | **6** |
| Function decisions with substantive receipts | 6 / 3,690 | **36 / 3,690** |
| Included systems left in deterministic queue | 614 | **609** |
| Unreviewed function slots | 3,684 | **3,654** |
| New hypothesis cards from this batch | 0 | **1 (A-Evolve, SCREENING)** |

Next ordered included system: [Aesop](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ae/aesop.md). Do **not** skip to systems with favorable keyword scores.

## Evidence / testing boundaries

- The [coverage script](../scripts/sweep_index_assessments.py) reads current locally pinned Index Git objects, validates identity, sections, function-specific receipts and candidate linkage; it does not actually independently verify native mechanisms or permission rights.
- Research receipts are human/agent **declared** six-function screening, not independently calibrated VSM reassessments. Native-fit follow-up requires current upstream reproduction, maintainer/development constraints and before/after measurements.
- The A-Evolve impact is a conditional local trust-boundary concern; the existing reporter's reproduction is not evidence of a user-generated exploit via model prompt.
- The contributor-fork registry, external repository code and upstream GitHub issue/PR publication are unchanged. No S1 admission, Index grade edit, stage grant, native before/after or authorized external write follows from screening coverage.
