# Henrik Agent Harness — same-CS claim race guard

**Status:** local assessment-informed technical packet; `AWAITING_EXTERNAL`. **No external fork, commit, issue or PR was created.** Human retains the external publication right; check upstream issue assignment and contribution policy before proposing a PR.

## Reproducible source and boundary

- Frozen Index: `opensiro/vsm-harness-index@396a54bb690f8ec7ce966bf9b00b241b30036307`, `assessments/he/henrik-agent-harness.md`, `included S1=A`, reviewed `2026-10-18`.
- Actual upstream: `henrik-me/agent-harness@9168fa451b69c5d53b961ab5c805b3067597ade4` (MIT), `lib/claim.mjs`, `applyClaimPlan()`.
- Procedure: `opensiro/upstream` [#56](https://github.com/opensiro/upstream/issues/56), tenth batch first row. Origin is **ASSESSMENT_INFORMED**: S1 shows a task-claim/admission surface but does not identify this particular defect.
- Source: [first-party claim function](https://github.com/henrik-me/agent-harness/blob/9168fa451b69c5d53b961ab5c805b3067597ade4/lib/claim.mjs#L563-L606). The unchanged routine re-reads WORKBOARD and rejects the current orchestrator gaining a *different* Active CS. It does **not** reject a different orchestrator registering the *same* CS between initial planning and apply; the later idempotent row insertion then leaves the competitor's row but the local rename is still performed. This contradicts the function's own race-check comment.

## Native test proof

No GitHub access, git operations, agent instantiation, model calls, model mocks, task simulation, or provider services were exercised. One real first-party Node function was invoked with fixed in-memory WORKBOARD/runner data.

| Command, at pinned source plus test | Before | After narrow fix |
| --- | --- | --- |
| `node tests/claim-same-cs-race.test.mjs` | 2 PASS / 2 FAIL (same-CS ownership races accepted) | **4 PASS / 0 FAIL** |
| `node tests/lib-claim.test.mjs` | Original suite unchanged | **48 PASS / 0 FAIL** |
| `git apply --reverse --check` | n/a | **PASS** against modified source |

Broader `node --test` was **not** attested: the clean clone lacks package dependencies (`ERR_MODULE_NOT_FOUND` for `js-yaml`), so other test files fail during imports. Do not misreport this as upstream regression or full-suite PASS. The relevant first-party claim test module is dependency-free.

## Change and scope

- Ready-to-apply diff: [`claim-same-cs-race-guard.patch`](claim-same-cs-race-guard.patch).
- SHA256: `e71cb0ae8473064541d953ee5cfce681cd683d701344331ae22f2dbeb1013186`.
- Adds a pre-mutation `freshRows` check: a different owner already holding the requested CS causes `apply-time race` failure. Different orchestrators claiming different CSs remain allowed; repeat apply by the original owner stays idempotent.
- Touches only `lib/claim.mjs` and a new `tests/claim-same-cs-race.test.mjs` in the patch; does not alter any human acceptance, approval, GitHub, model or agent capability.

## Remaining owner decision

Check upstream's current issue/PR overlap and request any required issue assignment; reproduce in a fully dependency-installed CI environment. Only a separately authorized owner should fork, push or open a public upstream PR. Pending external delivery does **not** block the next batch candidate.
