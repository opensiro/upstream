# AgentBox S2 — optional manager planning proof of mechanism

**Operator route:** proceed with a bounded engineering prototype without waiting for an explicit upstream rejection; *do not* construe silence as accepted product design.

**Source pinned:** [madarco/agentbox@605ee75d63319003c188bc532d4e5b2ba36a51d6](https://github.com/madarco/agentbox/tree/605ee75d63319003c188bc532d4e5b2ba36a51d6). Index-first S2 hypothesis: the [accepted assessment](https://github.com/opensiro/vsm-harness-index/blob/main/assessments/ag/agentbox.md) identifies manual inter-box file conflict avoidance. Native Phase 4 brief in AgentBox is explicitly planned.

## What exists here

- [Pure TypeScript advisory helper](task-overlap-plan.ts) aligned to actual AgentBox `HubApiTask` fields, including `projectId`, `dependsOn`, `boxId` and `status`.
- [Seven native Vitest tests](task-overlap-plan.test.ts): explicit overlapping path grouping, disjoint task parallel suggestions, unknown scopes, traversal/absolute/glob ambiguity, unfinished dependencies, existing competing assignments, project ID scoping and duplicate task identity.
- [Reproducible Actions](../../../.github/workflows/agentbox-s2-plan-prototype.yml): injects **only two new files** into source-pinned AgentBox checkout, installs locked pnpm dependencies, runs native AgentBox build, native Vitest and CLI typecheck, confirms unchanged tracked upstream files. Source is not pushed to the target project's branch or fork.

**Contract:** explicit project-relative write intent, not path guesses from natural-language descriptions. Known file/tree overlaps are proposed for same-box grouping. Unknown/unsafe scopes -> `needsReview`; tasks with unfinished dependencies -> `deferred`; tasks already assigned to a box -> `needsReview` rather than silent reassignment. No interception, no background service, no global lock, no filesystem write, no permissions expansion. Advice always returns `dispatchAuthorized: false`: source checks cannot prove actual writes or freshness, so human/manager must re-read state and make the final dispatch decision.

## Methodology / boundaries

Previously completed [baseline #64](https://github.com/opensiro/upstream/pull/64) measured CLI task assignment of synthetically colliding *descriptions* using a mock hub; [baseline #65](https://github.com/opensiro/upstream/pull/65) tested native task-store metadata under unfinished dependencies. **Neither is evidence of real file conflicts, or of a regression violating AgentBox's contract.** This prototype tests a narrower optional manager recommendation function; even native green tests are not a real-box before/after impact study.

**Research classification:** `ASSESSMENT_DERIVED_HYPOTHESIS / PROTOTYPE_UNDER_TEST`; need `PASS_ROADMAP`, mechanism `PENDING_NATIVE_TEST`, value `NOT_MEASURED`, scope `PENDING_FIRST_PARTY`. Do not regrade VSM or claim S2 autonomy.

**Upstream requirement:** [AgentBox CONTRIBUTING.md](https://github.com/madarco/agentbox/blob/main/CONTRIBUTING.md) explicitly says to open an issue *before* changes larger than a bug fix. [Human-owned issue draft](../AGENTBOX_DESIGN_INQUIRY_DRAFT.md) already exists. A ready-to-review internal proof does **not** waive that requirement, grant a contributor fork permission or publish an external PR. If maintainer rejects the mechanism, record a negative fit result and retire the prototype without making an upstream PR.

**Next:** complete actual native tests and correct errors if needed. Then decide whether the reviewable, optional manager helper is desirable as a first-party feature, and preregister true parallel-box before/after if integration is approved.
