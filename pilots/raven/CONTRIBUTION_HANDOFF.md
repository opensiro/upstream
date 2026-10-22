# Raven — stopped-turn step boundary (technical packet, not upstream PR)

**Batch:** [2026-10-22-01](../../data/assessment-candidate-batches/2026-10-22-01.json), row 4/5.
**Disposition:** local native RED/GREEN demonstrated; external publication **NOT EXECUTED**, awaiting the separate owner publication right. This packet is not an accepted Raven contribution.

## Assessment-first provenance and fit

- Frozen [Index assessment](https://github.com/opensiro/vsm-harness-index/blob/f2ea54a19770b21f88d70113fe8c60c72802e19e/assessments/ra/raven.md) reviewed EverMind-AI/Raven at e6c0344cb7ce00db25d554e4bb671ec1909a8f9f and a native read-before-edit ledger. The assessment **did not** diagnose the later web-stream boundary defect.
- New native checkout: EverMind-AI/Raven at 4315993300e538ec954c79565cbc8585006c8053. Need is from first-party [issue #1061](https://github.com/EverMind-AI/Raven/issues/1061), open at screening. **Origin ASSESSMENT_INFORMED, never ASSESSMENT_DERIVED.**
- **need PASS:** issue supplies a product-native, user-visible inter-turn mixing case.
- **mechanism PASS:** native runtime reset on Stop, late delta opens a step, the following opener leaves it active.
- **counterfactual PASS:** both new native fixtures RED before production source fix and GREEN afterward, using identical fixed frame sequences.
- **scope PASS:** two new-turn entry handlers and existing first-party web-session Vitest harness; no provider/model calls, changed permissions or public API.
- No exact overlapping fix PR found in the bounded GitHub search as of 2026-10-22. Recheck immediately before any external publication.

## Change and verified native behavior

- [Exact tested patch](stopped-turn-step-boundary.patch), SHA256 **3e5bc3194c82b66a62441c9eabc523dcdefd5f8e54f0b62ed07844b8ff3cd400**; matches the live source git diff byte-for-byte and passed reverse-apply verification against the working checkout.
- Production change: in ui-web/src/state/session/stages.ts call the already-shipped reset(rt) at both message.start and turn.started entry paths.
- In ui-web/src/state/session/runtime.cancel.test.ts collect real native pipeline step text with the existing fake transcript sink and add two fixed-frame tests; input starts with A: a1, stops A, receives A's late a-tail, starts B and receives b1.
- **Before:** first-party baseline cancel suite **12/12 PASS**; added regressions **2 RED** with actual steps [a1, a-tailb1] instead of [a1, a-tail, b1], other 12 remain PASS.
- **After:** focused four-file suite **60/60 PASS**. Exact command: npm test -- src/state/session/runtime.cancel.test.ts src/state/session/pipeline.events.test.ts src/state/session/runtime.streams.test.ts src/state/session/runtime.clock.test.ts
- npm run type-check **PASS**. npm run lint exit 0 with 4 existing warnings in unrelated React pages, 0 errors.
- Full npm test on the expanded sparse source: **251 files PASS; 4,215 tests PASS; 2 FAIL**. The remaining script-gate Vitest tests (check-css and check-class-namespace) receive empty child-process stdout; both underlying native scripts print OK when executed directly. Do **not** claim full-suite PASS or a proven root cause for these two runner discrepancies. Earlier missing root source subdirectories were restored before the final run.

The measured change separates the next turn's step from the old late step. It does **not** establish rejection of all stale frames: the orphan late A step may still be rendered. Nor does it establish real-model or Browser quality; no LLM agents ran.

## Return and remaining authority

This is a local technical packet, not a published fork or Raven PR. External publication remains human-owned in Upstream #56; revisit on a distinct attributable grant, fresh maintainer response or targeted command. Before publishing, refresh main/PR overlap, recheck the two unrelated Vitest CLI-gate discrepancies in normal CI, and follow Raven's AGENTS.md rules (including its commit, branch and review gates). Generic continue skips this **AWAITING_EXTERNAL** row and selects the next eligible candidate.
