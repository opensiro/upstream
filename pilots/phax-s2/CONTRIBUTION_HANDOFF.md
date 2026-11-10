# phax — S2 cross-run path-alias overlap: bounded technical handoff

Status: **ASSESSMENT_DERIVED / AWAITING_EXTERNAL** (2026-11-06). This is an internal reviewable OpenSiro technical packet, **not** an external phax issue, fork, PR, merged fix or delivered benefit.

## Evidence and frozen source

- Canonical Index: [phax assessment at frozen Index commit](https://github.com/opensiro/vsm-harness-index/blob/1e2d2b1c48e3b8d846d6911c98e4b76f1c6f1340/assessments/ph/phax.md), reviewed source ref `3a9457a63ad8e2b6e6cd6ba63ce38366450c1499`; S1=A / S2=C.
- Tested live first-party source: [phax `1eeff6b0792ce90edf0e11b18557613f3aa7dae9`](https://github.com/lbdremy/phax/tree/1eeff6b0792ce90edf0e11b18557613f3aa7dae9), Apache-2.0. Core [`compute.ts`](https://github.com/lbdremy/phax/blob/1eeff6b0792ce90edf0e11b18557613f3aa7dae9/src/domain/planOverlap/compute.ts) intersects raw file strings; [`fromPhaxPlan.ts`](https://github.com/lbdremy/phax/blob/1eeff6b0792ce90edf0e11b18557613f3aa7dae9/src/domain/planOverlap/fromPhaxPlan.ts) passes through plan paths; [schema](https://github.com/lbdremy/phax/blob/1eeff6b0792ce90edf0e11b18557613f3aa7dae9/src/schemas/phaxPlan.ts) accepts string paths. Landed diff paths come from the global file reconciliation.
- Product claim: [phax 1.0 announcement](https://github.com/lbdremy/phax/blob/1eeff6b0792ce90edf0e11b18557613f3aa7dae9/docs/blog/announcing-phax-1.0.md) describes conservative overlap detection and landed-plan reconciliation without false negatives.
- Repository issue/PR keyword search on 2026-11-06 found [historical feature PR #117](https://github.com/lbdremy/phax/pull/117) mentioning overlap, but no identified path-alias correction. Recheck overlap before any external submission.

## Native defect and four fit gates

**Need PASS:** `./src/widget.ts` and `src/widget.ts` denote the same repo-relative file, but the source treats them as separate strings. Two genuine first-party core assertions fail at current untouched head: `computePlanOverlap` reports `cleanPairs=[A,B]` / no edge for plans editing that file, while `computeReadjustmentImpact` marks the plan unaffected after a run modifies that file.

**Mechanism PASS:** this specifically undermines the assessment's S2 cross-run coordination/adjustment mechanism. The relative-path alias is admitted by the plan's string schema and is not normalized in the overlap projection. It is not a generic code-quality or speculative model-behavior observation.

**Counterfactual PASS:** canonicalizing repo-relative path spelling with `node:path.posix.normalize` inside both footprint constructors aligns paths for plan-vs-plan and landed-vs-plan intersection, without changing external file writes or admission/review gates.

**Scope PASS:** no model session, provider, browser, live run, CLI mutating action, or external fork/branch/PR was started. Only genuine pure first-party domain functions with fixed arguments were called under Node 24.

## Minimal patch and checks

- Exact patch: [`normalize-overlap-paths.patch`](normalize-overlap-paths.patch), SHA256 `7281e253723a43b4c926befb0897a0658ef321e58a3b0178871b16afdf7c6607`. It adjusts two footprint constructors and adds two unit tests to the existing `tests/unit/planOverlap/compute.test.ts` suite.
- **Untouched head:** two targeted source-native Node assertions **FAIL** (both missing edges/impact).
- **After:** eight direct fixed-data assertions **PASS**, covering the two regressions plus create/edit, delete-or-rename, markdown severity, clean pairs and regenerated artifacts. A second detached clean checkout pinned at `1eeff6b` passes `git apply --check`, applies the archived patch, passes the same eight assertions, and `git diff --check`.
- **Limit:** local `node_modules` is absent, so Vitest, TypeScript build and full first-party integration tests were **not** run; the added unit tests are unexecuted under Vitest. Exact regression was tested by importing the genuine TS implementation with Node 24's native strip-types and `registerHooks` resolving source `.js` specifiers to `.ts`, not by reimplementing phax. Path normalization is lexical and does not resolve symlinks, OS case-folding or repo-root-specific absolute aliases.

## Return and unexercised external right

This patch is reviewable for a human or separately authorized external stage. The `adjust-plan` application builds session artifacts and a prompt; no live adjustment or human approval was exercised. Consequently the stronger claim that an approval-withheld session leaves the full workflow unchanged was **not** empirically tested.

`external_action=NOT_EXECUTED`; `product_benefit=BOUNDED_NATIVE_CORRECTNESS_ONLY`; `experiment_cycle=INCOMPLETE_NO_EXTERNAL_DELIVERY`. External fork/PR publication and any eventual phax maintainer acceptance require a separate effective grant and actual provider receipts. An OpenSiro internal PR is not that grant.
