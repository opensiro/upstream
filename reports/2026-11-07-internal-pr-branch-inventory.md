# Internal PR and branch inventory — 2026-11-07 UTC (pre-refactor)

**Observed against:** `opensiro/upstream/main@99ac0597ff01568a0e8bde78558e7966fb8ef1c4`. This source-dated read-only inventory was taken **before opening refactor PR #153**. Live counts will change with new PRs/branches; do not treat this as the current repository head.

**Provenance:** GitHub REST `GET /repos/opensiro/upstream/branches?per_page=100`, `GET /repos/opensiro/upstream/pulls?state=open&per_page=100`, and `state=closed&per_page=100&page=1,2`. Each branch head was matched against the PR's exact `head.ref` and `head.sha`; no inferred ownership by naming pattern.

**Result:** 28 total branches = 21 open-PR heads + 6 closed-unmerged retained heads + one protected `main`. **Zero unmatched non-main branches.** `main` was `99ac0597ff01568a0e8bde78558e7966fb8ef1c4`. GitHub reported `main.protected=true`, without disclosing all branch-gate details.

## Open PR branches (21 at capture)

| PR | Exact branch | Branch head SHA | PR mode |
| --- | --- | --- | --- |
| [#152](https://github.com/opensiro/upstream/pull/152) | `docs/closure-attribution-20261107` | `1973657eb2ef2beb01bf0d22595537ddfa35a046` | Review |
| [#123](https://github.com/opensiro/upstream/pull/123) | `research/nanocoder-s2-coalesce-20261024` | `677aa482a5e01c4ff430daebf1912884048ea24a` | Draft |
| [#121](https://github.com/opensiro/upstream/pull/121) | `research/fara-resume-task-id-20261023` | `70563a1b721402694cd6dcc122690e200bcf1717` | Draft |
| [#120](https://github.com/opensiro/upstream/pull/120) | `research/evidence-bench-retrieval-error-20261023` | `0d205f12b92abd1c7ecf55c5b31ff7056354b93a` | Draft |
| [#119](https://github.com/opensiro/upstream/pull/119) | `research/agent-fleet-s2-stale-lease-20261023` | `ac3c154739c196df6b279292bbdb52a4b0100b7e` | Draft |
| [#118](https://github.com/opensiro/upstream/pull/118) | `research/citadel-s2-atomic-claims-20261023` | `40ef72c450b93a0a451b1f69b085e0ac43b1f5d0` | Draft |
| [#117](https://github.com/opensiro/upstream/pull/117) | `pilot/agentuniverse-is-halt-20261023` | `c34a98285bf9dbc5bb3d5126f31f05d6c5877b28` | Draft |
| [#116](https://github.com/opensiro/upstream/pull/116) | `pilot/agentspex-checkpoint-offline-preflight-20261023` | `78f82a4c5b7413fa9daaa0027195ce00e4dcd365` | Draft |
| [#115](https://github.com/opensiro/upstream/pull/115) | `pilot/agentsilex-s3star-recorded-audit-20261023` | `82a2fe5f6ba4ee44be68b3c54b7fac132637b71b` | Draft |
| [#114](https://github.com/opensiro/upstream/pull/114) | `pilot/agentlite-s3-delegation-budget-20261023` | `da424f0b7535ce5cf685d04a844947697ece7b44` | Draft |
| [#113](https://github.com/opensiro/upstream/pull/113) | `pilot/agentharness-s3star-dag-verify-20261023` | `779a3e6e90cd0b703391ea2d0b71906cd34d814c` | Draft |
| [#112](https://github.com/opensiro/upstream/pull/112) | `pilot/agentflow-s4-rollback-20261023` | `c6b679703cac022ad245f5175670e4465b252cf5` | Draft |
| [#111](https://github.com/opensiro/upstream/pull/111) | `opensiro/license-first-candidate-intake-20261023` | `7928c0bc1202ac5f93ad01f61f176afb10f0ec68` | Review |
| [#71](https://github.com/opensiro/upstream/pull/71) | `research/agentbox-s2-optin-plan-20261022` | `771f2fbaaa56046f39d032f79cd0f9d52791b55b` | Draft |
| [#70](https://github.com/opensiro/upstream/pull/70) | `pilot/kit-222-partial-subagent-config-20261021` | `0d8dff12f6eb139fa031f27674b290d351afb34e` | Review |
| [#69](https://github.com/opensiro/upstream/pull/69) | `pilot/agent-code-524-review-subagent-20261021` | `18321fa156d13055961e0cd0930a7cb5cf323923` | Review |
| [#67](https://github.com/opensiro/upstream/pull/67) | `design/improvement-candidates-intake-20261020` | `3f006c47385398b562158f711bd249506c727fd7` | Draft |
| [#55](https://github.com/opensiro/upstream/pull/55) | `ci/harnessdesk-1772-v2-current-full-gate-20261020` | `57dcdb411bf49f72c519f86188bba3c184d5f7a4` | Review |
| [#54](https://github.com/opensiro/upstream/pull/54) | `test/harnessdesk-1772-current-pinned-gates-20261020` | `ee5c02d40e968361eec8ca15505b36f4a7f61aa8` | Review |
| [#21](https://github.com/opensiro/upstream/pull/21) | `docs/cognee-upstream-submission-20261019` | `2908f594d90aa2ec6488ba6fbd7739d41b7e1b15` | Draft |
| [#1](https://github.com/opensiro/upstream/pull/1) | `docs/propose-registry-cc0-prose-ccby-2026-10-16` | `8c3a520dbcb70185db8be05acd44f160081fe817` | Draft |

## Closed without merge, intentionally retained (6)

These refs were not removed in the earlier verified merged-branch cleanup; prior retention is tracked in [#130](https://github.com/opensiro/upstream/issues/130) and [#150](https://github.com/opensiro/upstream/issues/150).

| PR | Exact retained branch | Branch head SHA | Former mode |
| --- | --- | --- | --- |
| [#110](https://github.com/opensiro/upstream/pull/110) | `opensiro/corrective-publication-receipts-20261023` | `9cc577ad1c774b12db76e9375fa2de22c1eefb6e` | Draft |
| [#68](https://github.com/opensiro/upstream/pull/68) | `pilot/agentdescent-453-native-fix-20261021` | `68213ab48139e0f2b158bc6e1de44f2e3f1e78ab` | Draft |
| [#52](https://github.com/opensiro/upstream/pull/52) | `feat/operator-signed-one-use-stage-host-20261020` | `4b15667093bf26e32d965bc6614e176256ddb24e` | Draft |
| [#18](https://github.com/opensiro/upstream/pull/18) | `docs/fork-first-control-plane-test-20261019` | `7f47dc1c66502baeea6a10cc0e10959bbc33ec53` | Draft |
| [#17](https://github.com/opensiro/upstream/pull/17) | `feature/prepare-package-tests-20261019` | `3d9aa59b01a802f10a38cbb457e73c8be7d4d03a` | Review |
| [#7](https://github.com/opensiro/upstream/pull/7) | `docs/chat-batch-approval` | `61397e1edc394abc87e2ba8c11160d579f52ff5d` | Draft |

## Disposition and migration safety

- No unmatched branch was identified for deletion. **No branch, PR, setting or historical git object was changed** by this inventory.
- 108 previously merged-PR branches were deleted in the separate, owner-authorized maintenance route; this observation is not a rerun of that deletion.
- Preserve research Draft PRs and native source receipts until their own exact-scope disposition review. A PR marked Draft, old, conflicted or passing CI is not automatically obsolete or merge-ready.
- The documentation and read-only reconciliation PR #153 creates its **own additional branch** after this capture; reconcile from live GitHub before future PR triage or branch deletion.
- Retained closed-unmerged branches #7/#17/#18/#52/#68/#110 require a **fresh** exact SHA, PR/branch protection and evidence-retention decision before deletion.
- This internal inventory is unrelated to the separately counted 18-target or 25-URL **external** PR portfolio; local repo PRs are not third-party adoption outcomes.
