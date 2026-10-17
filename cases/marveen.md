# Marveen — owner-gated external skill adaptation

- **Upstream:** [Szotasz/marveen](https://github.com/Szotasz/marveen)
- **Contributor fork:** [xLagerFeuer/marveen](https://github.com/xLagerFeuer/marveen)
- **Original upstream PR:** [#1516](https://github.com/Szotasz/marveen/pull/1516)
- **Observed outcome:** merged on 2026-09-30. **Product-native fit:** **pass** in the 2026-10-12 experimental ledger.

## Why it is independently useful

Marveen's Dream Engine encounters external skill opportunities. Directly adopting untrusted external README/repository content into globally active skills introduces a persistent prompt-injection risk. The upstream maintainer [explicitly rejected autonomous Level 3 adoption](https://github.com/Szotasz/marveen/pull/1516#issuecomment-5827208384) and supported the narrower design.

The accepted patch uses Marveen's **existing progressive-autonomy mechanism**: Level 1 reports, Level 2 proposes a local skill adaptation without modifying skill files, missing settings fail closed to Level 1, and there is no autonomous Level 3. This is a source-specific safety/UX benefit even if no VSM assessment exists.

## Public evidence and limitations

- [Original changes and maintainer review](https://github.com/Szotasz/marveen/pull/1516).
- [Maintainer confirms the merge](https://github.com/Szotasz/marveen/pull/1516#issuecomment-5906554788).
- No claim that the patch independently proves an autonomous S4 loop or a new canonical VSM grade.

**Gate result (ledger):** upstream need pass; native mechanism pass; counterfactual value pass; scope compatibility pass. This is the [Organization experimental interpretation](https://github.com/opensiro/vsm-oss-organization/blob/main/experiments/upstream-intervention-fit/observations.json), not an upstream certification.
