# Politik — containment false positive on filenames beginning with two dots

**Stage:** AWAITING_EXTERNAL; local native technical packet only, no fork or external PR.

- Canonical assessment: Index assessments/po/politik.md at 396a54bb690f8ec7ce966bf9b00b241b30036307; reviewed and current source cordfuse/politik@c1fa7312c75599d72b187bf20088f51f5dda2247 (live main observed matching 2026-10-22).
- **Provenance: ASSESSMENT_INFORMED, not ASSESSMENT_DERIVED.** Assessment identified the runner's containment/incident response; the particular false-positive path bug was discovered during later inspection and is not a direct preexisting Index hypothesis.
- Need: PASS — the first-party isInside helper wrongly flags an ordinary within-root path such as '..cache/state.json' because it checks string prefix '..' rather than the parent-directory component. checkContainment then wrongly reports a WROTE_OUTSIDE breach and may suspend a governed session.
- Mechanism: PASS — one local src/containment.ts conditional, exact native Node test cases for inside filenames and actual traversal.
- Counterfactual: PASS — first-party test file baseline 16 PASS / 1 RED (new regression), then 17 PASS / 0 FAIL with the two-line check change. The new test itself was executed as source; no LLM or subprocess coding agent.
- Scope: PASS — source file and a matching first-party regression test only.

## Checks

| Check | Result |
| --- | --- |
| Baseline focused test | 16 PASS / 1 RED on the new expected behavior |
| After change focused test | 17 PASS / 0 FAIL |
| TypeScript no-emit check | PASS — npm run build (tsc --noEmit) |
| Full first-party npm test | 37 test files PASS, 1 unrelated run-turn.test.ts FAIL (test's spawned CLI produced empty stdout), not a full-suite PASS |

The failing full-suite test concerns process orchestration and was not fixed or reclassified here. Upstream publication remains a separate human-owned act. Patch: containment-dotdot-prefix.patch, produced from real first-party diff. The external repo's files were not committed or pushed.

**Patch SHA256:** `3a68922871fe7395f2118225d1477f0ec3f4297f3f3daf88b9c4f359037eeb4b`. Exact match against native git diff; reverse-application on tested source confirmed.

**Handoff:** If the external owner grants publication for this exact source and patch, verify upstream has not independently changed the code, apply the patch, rerun the focused native test, then create a human-authorized external PR. Generic continue skips this AWAITING_EXTERNAL row and proceeds to the next candidate.
