# Functional effects — evidence ledger

**Evidence date:** 2026-10-22. **Owner:** `opensiro/upstream`.
This is **not** the eight-intervention PR acceptance dashboard, the Organization-owned product-native fit snapshot, or a VSM S2 regrade.
Source-only matched tests and a green CI run cannot be counted as an improvement deployed to users.

| Pilot | Origin | Before | After | Evidence level | Product benefit | External delivery |
| --- | --- | --- | --- | --- | --- | --- |
| [Zot](https://github.com/opensiro/upstream/issues/56) | `ASSESSMENT_DERIVED_HYPOTHESIS` | Controlled two-worker shared-file schedule: 1/2 intended updates preserved; both reported done, no conflict feedback. | Opt-in file-scope wrapper: 2/2 updates preserved after explicit retry; 1 conflicting admission refused; disjoint declared workers remained concurrent. | `SOURCE_ONLY_MECHANISM` | `NOT_MEASURED` | `NONE` |
| [AgentBox](https://github.com/opensiro/upstream/issues/61) | `ASSESSMENT_DERIVED_HYPOTHESIS` | Native CLI preflight/assignment accepted T-1, T-2 and T-3 as three separate box allocation requests against a stubbed Hub API. | Opt-in planner recommended [T-1,T-2] and [T-3] using explicitly supplied write intent; 20/20 new native Vitest checks passed. | `SOURCE_ONLY_PLANNING` | `NOT_MEASURED` | `NONE` |
| [Kit](https://github.com/opensiro/upstream/pull/70) | `ASSESSMENT_INFORMED` | Original compiled kit sessions failed to start with issue #222 partial TOML (missing subagent.harness). | Compiled patched CLI exited successfully, warned about subagent.harness, and preserved the TOML bytes; original/added Rust tests passed. | `NATIVE_CLI_BEHAVIOR` | `NOT_MEASURED` | `NONE` |
| [Agent Code](https://github.com/opensiro/upstream/pull/69) | `ASSESSMENT_INFORMED` | First-party issue #524 requested an independent review role; no controlled live-model review-quality baseline recorded. | Native reviewer role, process/permission boundaries and JSONL parsing tested; model precision/recall still unmeasured. | `SOURCE_REGRESSION_ONLY` | `NOT_MEASURED` | `NONE` |
| [HarnessDesk](https://github.com/opensiro/upstream/pull/55) | `ASSESSMENT_INFORMED` | First-party issue #1772 reports second-host socket takeover; original gateway source unlinks the socket without host ownership. | V2 gateway-ownership patch passed source-pinned native gateway regressions and full check:push; no deployed end-user result measured. | `SOURCE_REGRESSION_ONLY` | `NOT_MEASURED` | `NONE` |

## Reproducibility and next gate

### Zot — `zot-scoped-admission`

- **Comparability:** Same pinned Zot source and deterministic synthetic runners, but explicit retry changes the schedule and throughput.
- **Next gate:** First-party demand, compatibility with long-lived Zot sessions, and authoritative file-write scope.
- **Receipts:** [1](https://github.com/opensiro/upstream/blob/main/pilots/zot-shared-workspace/BASELINE_RECEIPT_2026-10-20.md), [2](https://github.com/opensiro/upstream/blob/main/pilots/zot-shared-workspace/SCOPED_AFTER_RECEIPT_2026-10-20.md), [3](https://github.com/opensiro/upstream/actions/runs/39476648135)

### AgentBox — `agentbox-manager-advice`

- **Comparability:** Paired task intent at source/planner level; no boxes, real file modifications or user-facing conflict frequency measured.
- **Next gate:** Human-owned issue-first AgentBox Phase 4 design feedback, then real conflicting/disjoint box workloads.
- **Receipts:** [1](https://github.com/opensiro/upstream/pull/72), [2](https://github.com/opensiro/upstream/actions/runs/39683286746), [3](https://github.com/opensiro/upstream/pull/64)

### Kit — `kit-partial-subagent-config`

- **Comparability:** Same pinned Kit source and issue-level CLI fixture; no model session or deployment measured.
- **Next gate:** Internal fallback-policy review and human-owned Kit contribution; never count as Index-derived discovery.
- **Receipts:** [1](https://github.com/opensiro/upstream/pull/70), [2](https://github.com/opensiro/upstream/actions/runs/39658753131), [3](https://github.com/opensiro/upstream/actions/runs/39671040353)

### Agent Code — `agent-code-reviewer`

- **Comparability:** Tests prove source contracts, not a before/after reviewer-quality metric.
- **Next gate:** External publication decision and real-model paired quality study if the effectiveness claim is needed.
- **Receipts:** [1](https://github.com/opensiro/upstream/pull/69), [2](https://github.com/opensiro/upstream/actions/runs/39640741764)

### HarnessDesk — `harnessdesk-socket-ownership`

- **Comparability:** Pinned-source regression tests; production multi-host deployment not observed.
- **Next gate:** Exact-stage contribution authorization, native external review and deployed host observation.
- **Receipts:** [1](https://github.com/opensiro/upstream/pull/55), [2](https://github.com/opensiro/upstream/blob/main/pilots/harnessdesk-1772/ASSESSMENT_LINKAGE_2026-10-20.md)

## Classification boundary

- `ASSESSMENT_DERIVED_HYPOTHESIS` is the **selection origin**, not a completed native improvement.
- `ASSESSMENT_INFORMED` means the first-party report supplied the concrete defect; do not retroactively credit Index with discovery.
- `SOURCE_ONLY_*` and `SOURCE_REGRESSION_ONLY` establish narrow mechanisms/tests, not a deployed change.
- `NATIVE_CLI_BEHAVIOR` can establish a genuine product-code execution difference on a frozen fixture, without establishing live adoption.
- `external_delivery=NONE` concerns the *pilot's third-party PR*, not internal OpenSiro PRs or the separate eight-case portfolio.

Only an independently accepted native need and a matched real workload can justify stronger product impact claims; external delivery is a separate dimension. Follow [the experiment method](ASSESSMENT_TO_IMPROVEMENT.md) and [#56](https://github.com/opensiro/upstream/issues/56).

Regenerate: `python3 scripts/functional_effects.py --write`; verify: `python3 scripts/functional_effects.py --check`.
