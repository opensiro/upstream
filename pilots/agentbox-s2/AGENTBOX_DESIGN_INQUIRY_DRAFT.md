# AgentBox — proposed upstream Phase 4 design inquiry (unpublished)

**This is a draft for a HUMAN to publish, not a posted issue, an external PR, permission grant, or chosen architecture.** The intended target is [madarco/agentbox](https://github.com/madarco/agentbox). Its [CONTRIBUTING](https://github.com/madarco/agentbox/blob/main/CONTRIBUTING.md) requires an issue for more-than-bugfix features and a signed contributor license agreement for eventual merges. Recheck current first-party state/duplicates before publishing.

## Proposed title

Phase 4 manager brief: optional file-overlap-aware task grouping before starting boxes?

## Proposed body

I noticed that your `docs/workspaces-tasks-manager-plan.md` says task allocation and keeping separate boxes from fighting over the same files are manual today, while the manager brief (Phase 4) remains planned. I wanted to check which small part of that Phase 4 behavior would be useful to implement without expanding AgentBox's architecture unnecessarily.

From current `main`, the task records expose `dependsOn`, `boxId/boxJobId`, `projectId` and status, but no verified intended-write paths. The CLI's assignment preflight checks task IDs/workspace identity, not whether two tasks are likely to edit the same code. So a safe first step might be an **opt-in, manager-owned planning brief** that collects explicit file-intent scopes before allocating independent boxes and returns a readable collision/unknown-scope warning rather than silently assuming two tasks are independent.

Would this fit the intended Phase 4 direction? In particular:

1. Should the initial implementation be an **agent instruction/manager brief using existing `agentbox tasks` and message surfaces**, or is a persistent task-level intended-file-scope field/API acceptable?
2. For two tasks aiming to change `src/payments/**`, should the preferred response be grouping them into **one box**, a dependency/serialization proposal or asking the user, rather than global path locking?
3. Where should a supervisor return a rejected/stale plan and ask the workers to re-scope? And should missing/ambiguous path intent always block automatic *parallel* assignment?
4. How should the design preserve normal independent `docs/**` work, explicit human choices, multi-host manager records, task reassignment and rollback?

I have not made a third-party fork, implementation PR, or issue for this proposal. I would be glad to prepare a minimal, source-pinned acceptance test and then a bounded change **once the desired interface is clear**.

Context: [pinned current-source analysis and proposed scenarios](https://github.com/opensiro/upstream/blob/main/pilots/agentbox-s2/SCREENING_AND_NATIVE_FIT_2026-10-20.md).

## Publication boundary

- This must be reviewed and submitted deliberately by the authorized operator; no external communication has been made.
- Do not present a VSM grade as a bug report or claim that the function is wholly absent in every downstream deployment.
- Do not promise built-in file locks/sandboxing: neither exist in the proposed manager-brief route, and task titles are not authoritative file-scope claims.
- If maintainers decline the feature, record a negative native-fit result under [OpenSiro #61](https://github.com/opensiro/upstream/issues/61) and select another candidate. No artificial PR is needed.
