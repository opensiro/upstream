# CrewDeck: enforce the S2 worker claim invariant at every admission entry point

Status: `ASSESSMENT_DERIVED` / **native source-tested**, OpenSiro-only unpublished packet.
Owning route: [Upstream #56](https://github.com/opensiro/upstream/issues/56),
batch `data/assessment-candidate-batches/2026-11-06-12.json`.

## Index-first origin and current product

- Canonical Index source: [`assessments/cr/crewdeck.md` at Index `5e070733`](https://github.com/opensiro/vsm-harness-index/blob/5e0707331a61345df50a2d3cfec543d448fde963/assessments/cr/crewdeck.md), reviewed 2026-11-05. Its `S2=C` witness is exclusive task/worker admission and completed-prerequisite gating. That is **constructor-owned** S2, not an S2 autonomous agent or a claim that the grade should change.
- Exact first-party baseline: [`mnbresearch/crewdeck@7925ffb`](https://github.com/mnbresearch/crewdeck/commit/7925ffb4c5e922f0081cce9ca59f62190b6e7864), also the observed current default-branch HEAD when screened 2026-11-06.
- Product-native need: [CrewDeck README](https://github.com/mnbresearch/crewdeck/blob/7925ffb4c5e922f0081cce9ca59f62190b6e7864/README.md) explicitly promises **one task per agent** and execution locks. The scheduler's `nextTaskFor()` enforces it, while `claim()` is a public engine operation reachable through the server's `POST /api/tasks/:id/run` route. An operator can bypass the scheduler and claim a second concurrent task for the same agent. That can dispatch two shell/HTTP adapters for the same operational worker.
- Related guard: direct `claim()` also admitted `done` and `review` tasks, starting previously completed or not-yet-approved work contrary to the normal to-do dispatch policy.
- Local project policy: observed MIT `LICENSE` and dependency-free `npm test`; no root `CONTRIBUTING.md` in the screened baseline. Read-only GitHub issue/PR overlap search for `lock`, `claim`, `concurrent`, `dispatch` returned no matching item at screening time; absence of lexical hits is not semantic uniqueness proof. Recheck if publication becomes possible.

## Bounded fix

Patch: [`manual-claim-admission.patch`](manual-claim-admission.patch), SHA-256
`d1176ff1c0b258d96befbee1fca4c6981ffce78e6333e5e01dfabf2f69d2208f`.

It changes only two first-party files:

1. `lib/engine.mjs`: both scheduler and direct claim check in-flight `runs`; direct claim also rejects non-`todo` tasks before executing anything.
2. `tests/engine.test.mjs`: two native deterministic regression tests exercise direct claim overlap, clean sequential progress, completed-task replay and approval-gated replay.

No VSM branding or organizational model is inserted into CrewDeck. It changes a concrete safety condition of CrewDeck's own execution controller.

### Matched native observation

1. On untouched pinned `7925ffb`, with exactly the two new tests, `node --test tests/engine.test.mjs`: **9 PASS / 2 FAIL** (both new tests fail with *Missing expected exception*).
2. On the patched same source: first attempt **10 PASS / 1 FAIL** due to an existing assertion requiring the error message `locked`. The patch preserves that established error precedence.
3. After the bounded adjustment, `npm test`: **11 PASS / 0 FAIL**; `git diff --check` passes.
4. Detached, clean Git worktree at the same `7925ffb`: `git apply --check` with the exact archived patch passes; `git apply` followed by full native `npm test` yields **11 PASS / 0 FAIL** again.

Native Node v24.22.1, npm v11.9.0. No model invocation, adapter execution, agent task, network service, browser, or live provider call was used. This is a script-level correctness result, **not** measured deployment benefit, absence of other races, or an updated VSM score.

## Fit and release boundary

| Gate | Verdict | Independent product-native reason |
| --- | --- | --- |
| Need | PASS | Project promises exclusive worker execution; direct API violates it. |
| Mechanism | PASS | Shared engine `claim()` and native `runs` ledger are the relevant enforcement points. |
| Counterfactual | PASS | Prevents double dispatch and unauthorized replay even if OpenSiro and VSM terminology are absent. |
| Scope | PASS | Two-file, dependency-free change with two source-level negative regressions; default scheduler still works. |

**Authority:** this is an OpenSiro internal prepared patch. The finite 34-case Corrective S5 publication mandate does **not** cover this new Improvement cohort. No new external fork, branch, issue, pull request, maintainer message or merge was performed. An independently attributable authorization and a fresh source/policy/overlap check are required to move to external publication. External acceptance and real-user benefit are `NOT_VERIFIED`.
