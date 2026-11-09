# Histh S2 — conservative subagent-batching admission

**Cohort:** [Upstream upgrade batch 21](../../data/assessment-candidate-batches/2026-11-09-21.json). **Owner:** [Upstream #56](https://github.com/opensiro/upstream/issues/56). **Origin:** prospective `ASSESSMENT_DERIVED` at [immutable pre-source checkpoint `95d9306`](https://github.com/opensiro/upstream/commit/95d9306537e0cdf6877942215a53ff679f561b7b). **External action:** `NOT_EXECUTED`.

## Identity and observed S2 boundary

- Included Index: [`assessments/hi/histh.md`](https://github.com/opensiro/vsm-harness-index/blob/46219bf103b0b122d86abc3ca70ae3d8bc820e2c/assessments/hi/histh.md); reviewed target `f2aff641e55c2e6bb8c55a8fb82b67bdf2addd1a`.
- First-party current revision actually checked: [`ayandexyz/Honey-I-Shrunk-the-Harness@1ac18ff`](https://github.com/ayandexyz/Honey-I-Shrunk-the-Harness/tree/1ac18ffb723f107391b82a34bfa9dc06abf0123a), MIT; product also names itself FreeCode.
- S2=C: native scheduling serializes writing child agents and parallelizes read-only agents. A classifer uses the call's `readOnly` input; `executeSubagent` can instead resolve an omitted flag from a local agent definition's `mode`.
- Current root `CONTRIBUTING.md` asks for native tests/lint/typecheck and a separate A/B evaluation for behavior changes. No such live A/B is performed under the operator's no-model-trial boundary.

## Exact native failure

The [planner's `agent` tool](https://github.com/ayandexyz/Honey-I-Shrunk-the-Harness/blob/1ac18ffb723f107391b82a34bfa9dc06abf0123a/apps/core/src/tools/agent.ts) presently treats `readOnly` absent as safely parallel (`coerceBoolean(undefined) !== false`). Yet [agent definitions](https://github.com/ayandexyz/Honey-I-Shrunk-the-Harness/blob/1ac18ffb723f107391b82a34bfa9dc06abf0123a/apps/core/src/agent/definitions/loader.ts) support `mode: build`; `executeSubagent` resolves omitted `readOnly` using that definition. The batch planner has no project-definition context. Two project build-role child calls with omitted `readOnly` can therefore be scheduled in parallel even though their actual tool modes permit mutation.

**Patch:** require `readOnly === true` explicitly to mark an agent call concurrency-safe. Explicit read-only agents remain parallel; ambiguous implicit-mode agents serialize. This deliberately trades some implicit-default concurrency for a safe conservative admission rule. No new runtime, model call, autonomous S2 owner or grade claim.

- [Native regression patch](native-regression.patch) applies only the source-native `batching.test.ts` case; its two implicit build-role calls must not share a parallel batch.
- [Native fix patch](native-fix.patch) updates the first-party classifier and adjusts one older test to explicitly pass `readOnly: true`.
- [Separate runner RED→GREEN receipt](INDEPENDENT_HOST_RECEIPT_2026-11-09.md) is the only technical-benefit claim.

## Delivery and next boundary

**Qualified local technical handoff; `AWAITING_EXTERNAL`.** No fork, external branch, third-party issue, PR, merge, release, or maintainer acceptance is claimed. Upstream #6 still governs external stage authorization. Maintainer review must weigh the conservative default-parallelism tradeoff, supported third-party policy/CI, and the A/B-eval condition; do not substitute live agent/provider testing in this project. A separately authorized external publication would require its own current source recheck and exact grant. The result is a bounded native correctness fix inside S2=C, not `C→A` or observed deployed safety.