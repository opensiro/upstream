# Native CI placement for external harness improvements

**Owner:** `opensiro/upstream`. **Applies to:** `upstream batch`, `upstream upgrade batch`, and other first-party native effect checks. **Authority:** [UPSTREAMING](../UPSTREAMING.md), [assessment → improvement](ASSESSMENT_TO_IMPROVEMENT.md), [Upstream #6](https://github.com/opensiro/upstream/issues/6). This operational placement rule creates no new GitHub permissions.

## Separation of concerns

| Place | Owns | Tests / actions |
| --- | --- | --- |
| `opensiro/upstream` | Index-sourced preregistration, five-row batch records, patch/test handoff, pinned provenance, observed outcomes and links to independent receipts | CI for Upstream metadata, generated views, registry integrity and existing operational observers; **no new harness-specific native CI on `main`** |
| `opensiro-contributions/<target>` | Permissioned working fork and product-native branch/patch | Reuse the target's own tests/CI; add a narrowly scoped branch workflow only when needed for deterministic before/after evidence |
| Distinct deterministic runner / host | Pinned source checkout and matched test execution when a permitted fork is unavailable | Independently executed scripted source-native tests; attributable environment, commands and immutable receipts |
| Third-party original | Upstream maintainer's implementation and contribution acceptance | Its own native CI only when the external owner permits; never assumed writable or available |

`opensiro-contributions` is the normal working-fork location, **not** an automatic stage grant. The general connected fork/branch executor is still gated by [#6](https://github.com/opensiro/upstream/issues/6). Neither this document nor a batch selection authorizes a new fork, branch, external PR, comment or third-party workflow mutation. A source-only independent host test may proceed only under the actual host/tool permissions and without a chatbot directly executing the strict-derived before/after validation.

## Runner selection and evidence

1. Prefer the project's existing native tests/CI in a **currently authorized working fork**; use its pinned source/base and a separate feature branch so the original developer's CI/configuration is not silently changed. When necessary, a temporary project-specific workflow may live only on the working branch. Avoid including test-only orchestration in an external contribution unless a maintainer requests it.
2. Otherwise use a **distinct deterministic host/runner** with a captured execution identity and independently inspectable logs. Pin the exact source SHA and run the actual first-party code path. A test dispatched by the AI to an independent deterministic executor remains separate from an AI-executed validation; local chatbot shell execution does not satisfy the strict-derived gate.
3. If no legitimate independent runner is available, record `BLOCKED_INDEPENDENT_EXECUTION` and continue other eligible batch rows. A `green` Upstream metadata job is never a replacement. Do not launch live LLM agents or provider trials.

Every native before/after receipt stored or linked from `upstream` must identify:

- canonical Index assessment/ref and the frozen pre-code hypothesis checkpoint when `ASSESSMENT_DERIVED` is claimed;
- exact external source repository, baseline commit, tested patch commit or patch SHA256, test SHA256, first-party entry point and expected observation;
- runner owner/identity, run URL or retrievable artifact, environment/dependencies, precise commands, baseline and after outputs (including negative/null results), native regression/control result;
- any retention limit of remote logs plus a durable concise result record, permissions used and unresolved native-fit/publication gates.

A runner PASS validates the bounded scripted mechanism under these conditions only. The assessment-origin classification, demonstrated product effect, published external PR, maintainer acceptance and any VSM regrade remain separate claims.

## Handling existing Upstream workflows

Do **not** delete, disable or rewrite existing harness-specific workflows merely because this rule is adopted. Inventory their existing runs and schedules, retain attributable historical evidence, then migrate active native validation to the corresponding permitted fork/runner in a reviewable change. Avoid per-harness workflow files in new Upstream PRs that would reach `main`.

**Batch 14 / Runloop:** [Draft PR #174](https://github.com/opensiro/upstream/pull/174) already ran [a successful independent pinned before/after pilot](https://github.com/opensiro/upstream/actions/runs/42493920695). That earlier run remains evidence for its exact tested inputs and SHA; it does not permanently authorize or justify adding `assessment-upgrade-b14-runloop-native.yml` to `upstream/main`. Before integrating #174, preserve an attributable receipt, arrange future reproducibility at a genuinely authorized runner, and remove its project-specific workflow from the integration diff. Until then, leave the PR Draft and report the outstanding runner/authorization boundary rather than treating historical PASS as a new permission.
