# AgentBox S2 manager-advisory CI migration — 2026-11-11

**Disposition: FORK_NATIVE_MANAGER_ADVISORY_PARITY_PASS.**
This relocates a frozen optional, **research-only** advisory prototype,
not a product deployment, external PR, or outcome claim.

## Source identity and execution

- Original `madarco/agentbox@605ee75d63319003c188bc532d4e5b2ba36a51d6`,
  also the matching public [`opensiro-contributions/agentbox`](https://github.com/opensiro-contributions/agentbox)
  fork's `main` on this date.
- Evidence-only branch `opensiro/ci-agentbox-manager-advisory-parity-20261111`
  at [`e9b40d947463adace9ea09aa8facc28518620b92`](https://github.com/opensiro-contributions/agentbox/commit/e9b40d947463adace9ea09aa8facc28518620b92).
  The branch adds **only one CI YAML**; fork `main` and upstream product source unchanged.
- Immutable OpenSiro fixture checkout: `opensiro/upstream@c2ae25433a8b709bcdb24a9349a451620f1578c1`,
  containing the same `pilots/agentbox-s2/manager-advisory/module.ts` and
  `module.test.ts` source files as the original Upstream workflow.
- Historical [Upstream run #39683286746](https://github.com/opensiro/upstream/actions/runs/39683286746):
  **SUCCESS**, Ubuntu 24.04. Matching-fork [run #43090937771](https://github.com/opensiro-contributions/agentbox/actions/runs/43090937771):
  **SUCCESS, attempt 1**, actual GitHub-hosted Ubuntu runner.
- Original [`agentbox-s2-manager-advisory.yml`](historical-upstream-manager-advisory.yml)
  archived byte-for-byte; original Git blob SHA: `0b5479c2dc186b80b3ceabce8b36f4ff88d9f0e6`.

## Native parity

The fork workflow differs only in branch-only trigger and explicit
read-only, credential-free checkouts of frozen Upstream fixtures and
source from the correctly parented fork. It keeps Node 22,
pnpm 9.15.0, `pnpm install --frozen-lockfile`, full `pnpm build`,
the manager-advisory native Vitest module tests,
`@madarco/agentbox` TypeScript typecheck and ESLint, and
the assertion that only two untracked additive research files were
injected into a disposable source checkout. **All passed.**
No source file, branch default, third-party PR, or production API changed.

## Independent Draft PR #71

Open [Upstream PR #71](https://github.com/opensiro/upstream/pull/71)
is the distinct `task-overlap-plan` prototype. Its source diff contains
`.github/workflows/agentbox-s2-plan-prototype.yml` and separate
`pilots/agentbox-s2/prototype/**` files, **not** the historical
`manager-advisory` workflow or its module fixtures. Archiving the latter
does not remove or approve #71's separate checks. No merge of #71 was
performed; no source-native product benefit, external adoption, or VSM
autonomy regrade is inferred.
