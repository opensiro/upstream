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

## Enforced placement for new workflows (2026-11-11)

**All new harness-specific native GitHub Actions belong in the correctly
parented `opensiro-contributions/<target>` working fork**, on an authorized
`opensiro/...` branch when a temporary evidence runner is needed. Prefer the
source project's existing native workflows first; do not introduce a duplicate
workflow merely to obtain a green badge. Where a fork cannot run the test, use
a separately controlled deterministic runner with an attributable receipt.

`opensiro/upstream/.github/workflows` may contain only Upstream-owned
repository-integrity, provenance/registry, fork lifecycle and external-PR
observation workflows. The distinction is **what is being validated**:
running Upstream's own evidence/metadata checks is allowed; executing a target
harness's native regression in a new Upstream workflow is not. This includes
manually dispatched and path-filtered pilot workflows; making them optional
does not change their ownership.

The [unit-test guard](../tests/test_native_ci_placement.py) recognizes seven
existing Upstream control workflows and freezes the 13 remaining historical
project-specific workflows as **retirement-only exceptions**. New workflow
filenames fail unfiltered repository-integrity CI until their genuine
Upstream-control ownership is explicitly reviewed. The historical list may
shrink as each pilot is migrated, but must not expand. See
[Upstream #214](https://github.com/opensiro/upstream/issues/214) for the
six-source inventory, native-CI readbacks and migration checklist.

Migration is not a blind move: historical Upstream runs and logs remain valid
evidence for their pinned inputs. A corresponding first-party workflow in the
fork is **not automatically equivalent** to a past RED/GREEN pilot. Preserve the
run links and source/test hashes, demonstrate equivalent coverage or a
replacement deterministic runner, then remove the superseded Upstream
workflow in a reviewable PR. Do not copy internal Upstream `pilots/` fixtures
into a third-party publication diff or install unrelated CI into the
original project's `main`.

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

**Batch 14 / Runloop:** [PR #174](https://github.com/opensiro/upstream/pull/174)
has since merged **without** adding `assessment-upgrade-b14-runloop-native.yml`
to `upstream/main`. Its [successful independent pinned before/after run](https://github.com/opensiro/upstream/actions/runs/42493920695)
remains evidence only for the exact tested inputs and SHA. The obsolete
branch-only workflow registration was disabled after the merge; the run
remains available. Any **future** Runloop-native regression must use a
legitimately authorized source-matched fork or distinct deterministic runner
and preserve a new attributable receipt. The historical PASS is not a
standing permission or a reusable current-main CI gate.
