# CodeAct S2 — prevent duplicate kernel creation for a new conversation

**Cohort:** [Upstream upgrade batch 22](../../data/assessment-candidate-batches/2026-11-09-22.json) under [#56](https://github.com/opensiro/upstream/issues/56). **Origin:** `ASSESSMENT_DERIVED` (pre-source [checkpoint `441d7675`](https://github.com/opensiro/upstream/commit/441d7675fa42499db6d528f9dbef0bf718a9a503)). **Delivery:** prepared internal source-native packet, `AWAITING_EXTERNAL`; no external action executed.

## Index-first rationale and independent source check

- [Included CodeAct assessment](https://github.com/opensiro/vsm-harness-index/blob/46219bf103b0b122d86abc3ca70ae3d8bc820e2c/assessments/co/codeact.md) S2=C credits first-party *per-conversation Jupyter kernel isolation* against cross-session mutable-state interference, with deterministic `conv_id_to_kernel` binding. Assessed source: `d607f56c9cfe9e8632ebaf65dcaf2b4b7fe1c6f8`.
- At screening, first-party default branch [`xingyaoww/code-act@d607f56c`](https://github.com/xingyaoww/code-act/tree/d607f56c9cfe9e8632ebaf65dcaf2b4b7fe1c6f8) still used the same source, rather than a later reviewed rewrite. Root license is MIT. A query of first-party issues/PRs for a kernel concurrency fix returned no relevant match; this is **not** proof that none exists outside the queried terms.
- The preregistered question targeted *two simultaneous first requests for one previously unseen conversation*. In the actual [`ExecuteHandler.post`](https://github.com/xingyaoww/code-act/blob/d607f56c9cfe9e8632ebaf65dcaf2b4b7fe1c6f8/scripts/chat/code_execution/api.py), `if convid not in conv_id_to_kernel` precedes the asynchronous `await kernel.initialize()`, whereas assignment to the dictionary happens afterward. Two HTTP handlers can thus both allocate a gateway before either stores the binding.

## Native-fit decision

| Gate | Result | Evidence |
| --- | --- | --- |
| `need` | **PASS** | Independent first-party Tornado HTTP test demonstrates two gateways for one `convid` on the unmodified source. |
| `mechanism` | **PASS** | The original in-memory registry has no in-flight per-conversation creation task; an `asyncio` keyed in-flight task removes the duplicate allocation window. |
| `counterfactual` | **PASS** | Before 1/2 native tests passed, after 2/2; different-conversation concurrency remains 1/1 PASS. Narrowed to deterministic resource-ownership correctness, not deployed success. |
| `scope` | **PASS** | Two-file MIT-licensed source/test patch, no model/provider/Browser execution, no public fork/PR, no global serialization of unrelated conversations. |

## Patch and runner

- [Regression-only patch](native-regression.patch): actual Tornado HTTP concurrent POSTs, fake external Jupyter backend; same-conversation single allocation plus different-conversation parallelism control.
- [Production patch](native-fix.patch): use one in-flight `asyncio` task keyed by conversation before awaiting kernel initialization; co-waiters share it, distinct conversation IDs proceed independently; failures close the begun gateway.
- [Independent source-native receipt](INDEPENDENT_HOST_RECEIPT_2026-11-09.md): matched **RED 1/2 → GREEN 2/2**, exact source and patch hashes, host monitoring session, Python/Tornado environment and output caveats. [Reproducible host script](run-native.sh) invokes tests without a live model or gateway.

## Reviewed patch selection for preparation (2026-11-11)

The two existing, first-party-tested patch artifacts are now explicitly selected for the generated working-fork registry, with no new code changes:

- Production: `native-fix.patch`, SHA-256 `11afa4ea02e7c1107a8e1e77ca7333951dfa627e251c3057b6fb854633c99430`.
- Tornado regression: `native-regression.patch`, SHA-256 `9265f2da99a4edba0d690bb152d894157f51ede0a94978b716c3be2adc78adf6`.

The exact target remains `xingyaoww/code-act main@d607f56c9cfe9e8632ebaf65dcaf2b4b7fe1c6f8`, and the direct public fork `opensiro-contributions/code-act` currently has a source-identical default branch. This selection unlocks a *candidate-specific* preparation preflight under the standing mandate; it does not itself push a branch or publish a PR. Rerun source-native checks on the actual fork head and recheck the source after any drift.

## Remaining decision boundary

This is an internal engineering result, **not a contribution to `xingyaoww/code-act` yet**. No third-party fork, branch, PR, merger, deployment or maintainer feedback is claimed. Upstream #6 must authorize actual external stages independently. Before external publication, recheck the target's then-current source, contribution rules and maintainer interest; a standalone upstream maintainer may prefer a different allocation policy. Full integration tests with real Docker/Jupyter remain unrun and are not equivalent to the deterministic mocked-backend correctness evidence. There is **no automatic Index grade increase** or new S2 ownership in this change.
