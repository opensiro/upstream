# Zot shared-workspace baseline — executed receipt

**Case:** [Upstream #56](https://github.com/opensiro/upstream/issues/56) / source-only [PR #58](https://github.com/opensiro/upstream/pull/58). **Date:** 2026-10-20.

**Source provenance:** selected through pinned canonical [Index `main@5393b698bfdfa4ca14d97a79238234eca20694e5`](https://github.com/opensiro/vsm-harness-index/commit/5393b698bfdfa4ca14d97a79238234eca20694e5), [Zot assessment](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/zo/zot.md), then fresh public [Zot `main@c62d1c549d52cd33390968ffa50667cb79609152`](https://github.com/patriceckhart/zot/commit/c62d1c549d52cd33390968ffa50667cb79609152).

**Execution:** [GitHub Actions run #39474300697](https://github.com/opensiro/upstream/actions/runs/39474300697/job/118806157803) **SUCCESS**. Ubuntu GitHub-hosted ephemeral runner, Go 1.25.0. `permissions: contents: read`; `persist-credentials: false` in both GitHub checkouts. Test source copied to a disposable Zot checkout, without any GitHub write to the upstream, fork or OpenSiro product. Source pinned before test.

Command (unmodified Zot package plus temporary injected research test):

```bash
go test ./packages/agent/swarm -run '^TestAssessmentSharedWorkspaceLostUpdateBaseline$' -count=1 -v -timeout=2m
```

Exact observed log excerpt:

```text
=== RUN   TestAssessmentSharedWorkspaceLostUpdateBaseline
synthetic baseline: workers_reported_done=2, worker_updates_intended=2, final_updates_preserved=1, lost_updates=1, native_conflict_feedback=not_observed
--- PASS: TestAssessmentSharedWorkspaceLostUpdateBaseline (0.00s)
ok github.com/patriceckhart/zot/packages/agent/swarm 0.006s
```

| Observable | Baseline observation |
| --- | --- |
| First-party `Swarm` workers | 2 independent synthetic RunnerFunc workers |
| Shared source initial state | `original\n` |
| Worker preimages | Both read the same original file before either writes |
| Intended unique updates | 2 |
| Preserved updates after ordered conflicting writes | 1 |
| Silently overwritten update | 1 |
| Zot worker status after both return nil | Both `done` |
| Conflict/error returned to worker by Zot swarm | None observed in this controlled case |

**Interpretation:** This is a real, source-pinned execution of Zot's `Swarm` and status lifecycle using fake model workers. It proves a possible **silent lost update** under an intentionally adversarial shared-file schedule in the explicitly documented shared-`RepoRoot` operating mode. The test itself is written to **PASS when the risk is reproduced**, not to require Zot to reject it. It does **not** establish that Zot users commonly experience collisions, that this intentionally selected mode is a software defect, or that any intervention's product value is confirmed.

**Native-fit disposition remains `PENDING`.** Maintainer wants a lightweight, shared-directory mode; `CONTRIBUTING.md` requests design feedback before a multi-package/public-API feature. Proposed next experimental target, *conditional on that feedback*: under an opt-in safe mechanism, run the same controlled schedule and demonstrate either preservation of both updates or an explicit, attributable rejection of one conflicting update, without serializing unrelated workers or damaging cancellation/restart. No such `after` experiment or external PR has been executed.

**Outcome:** `BASELINE_HAZARD_REPRODUCED`; product improvement verdict `INCONCLUSIVE`; origin stage `ASSESSMENT_DERIVED_HYPOTHESIS_NOT_ADMITTED` (not a product-effect success, no new Index grade). The screening [four native-fit gates](SCREENING_2026-10-20.md) remain authoritative.
