# OpenSiro — upstream contributions

This repository is the public **portfolio and lifecycle registry** for OpenSiro's contributions to third-party open-source projects.

It is **not** a monorepo of forks, a mirror of upstream code, a claim of upstream endorsement, or a new organizational control plane. Each working fork remains a separate GitHub repository.

## Public impact dashboard

**[Open the Upstream Dashboard →](DASHBOARD.md)** — readable on GitHub. It shows the eight experimental upstream interventions, separately verified external PR states, historical product-native fit (**60% of completed fit reviews** in the pinned experiment), primary evidence and distinct verification dates. For a filterable browser view see [`docs/index.html`](docs/index.html) (HTML file; GitHub Pages publishing is not enabled by these files).

These are **dated observations, not live acceptance rates or productivity scores**. The [Organization-owned snapshot](https://github.com/opensiro/vsm-oss-organization/blob/main/experiments/upstream-intervention-fit/snapshot.json) is authoritative for fit and attribution; [`data/upstream-lifecycle.json`](data/upstream-lifecycle.json) is this repository's independently checked public PR-state receipt. Neither makes a new S1 domain or modifies Control Plane authority.

### Keeping the portfolio current

The [read-only status procedure](docs/UPSTREAM_STATUS_FRESHNESS.md) checks both the eight-case experimental portfolio and separately submitted `registry.yaml` upstream PRs. It renders `DASHBOARD.md`, `docs/index.html` and the casebook from one local receipt. A daily GitHub Actions job reports drift without using write permissions or automatically changing fit classifications.

### External PR maintenance (adjacent operating pilot)

[Upstream PR Maintenance](docs/PR_MAINTENANCE.md) tracks the external PR review queue, new or edited maintainer feedback and failing CI in the [read-only GitHub-sensing / OpenSiro-inbox #125](https://github.com/opensiro/upstream/issues/125) route. The hourly [workflow](.github/workflows/pr-maintenance.yml) is merged on `main` and [initial activation was verified](https://github.com/opensiro/upstream/issues/125#issuecomment-6385585447). Its current default-branch checkpoint covers **13** targets; reviewable [PR #129](https://github.com/opensiro/upstream/pull/129) adds five external Ready-for-review Corrective PRs for a proposed **18-target** watchlist. That extension is not active until integration and checkpoint migration are verified. Native-only repair and external PR integration still require separate applicable contributor authority. This does **not** admit Upstream as a fourth Organization S1 domain (see [Organization #274](https://github.com/opensiro/vsm-oss-organization/issues/274)).

### Operational-readiness review (2026-10-25)

The [source-backed Upstream readiness review](reports/2026-10-25-upstream-operational-readiness.md) separates the finite Corrective result (**13 SUBMITTED / 21 BLOCKED / 0 QUEUED on unmerged PR #129**) from default-branch deployment, external PR maintenance, the strict functional experiment [#56](https://github.com/opensiro/upstream/issues/56), and Organization S1 admission. This dated observation is not a new authorization, external PR acceptance rate or assessment result. A fresh chat must inspect the exact PR branch while it remains unmerged.

## Current work

| External project | OpenSiro fork | Contribution | Upstream status | Fork lifecycle |
| --- | --- | --- | --- | --- |
| [Cognee Community](https://github.com/topoteretes/cognee-community) | [opensiro/cognee-community](https://github.com/opensiro/cognee-community) | [Canonical OpenSiro VSM assessment source](projects/cognee/README.md) | [PR #434 — submitted](https://github.com/topoteretes/cognee-community/pull/434) | **Active** |

Machine-readable current state: [`registry.yaml`](registry.yaml). Research and testing evidence is linked in project profiles.

## Assessment-shaped external intervention cases

A separate [product-native fit casebook](cases/README.md) documents **eight** publicly evidenced interventions into other OSS harnesses that originated from or were shaped by OpenSiro assessment/research. It includes accepted, still-open, and unsuccessful work. Most are in **personal contributor forks**, not OpenSiro-owned forks, so their fork-maintenance state is **not** inferred or added to `registry.yaml`.

The [Organization experimental ledger](https://github.com/opensiro/vsm-oss-organization/tree/main/experiments/upstream-intervention-fit) remains the source of truth for the four fit gates, participant attribution and deduplication. The casebook is a linked portfolio view, **not** an upstream endorsement, an acceptance rate or a VSM grade claim.

## Assessment-derived product improvement (separate test)

The [functional effect ledger](docs/FUNCTIONAL_EFFECTS.md) records source-native
before/after observations and their limits separately from external PR lifecycle
and Organization fit. It is deliberately explicit about **unmeasured real-user
benefit**; regenerate its Markdown from
`data/functional-effects.json` using `scripts/functional_effects.py`.

**Test rule:** assessment-derived upstream pilots use **deterministic native script/CLI tests only**. Pinned product-code baselines, matched after-tests and regressions are sufficient for a bounded technical effect; **live LLM agents, model calls and Browser agent-quality tests are out of scope**. Deployed end-user benefit, external PR acceptance and VSM grade changes remain separate unproven claims. See the [binding validation policy](docs/ASSESSMENT_TO_IMPROVEMENT.md#mandatory-validation-boundary--native-scripted-tests-only).

The [Kram S2 replay](pilots/kram-s2/README.md) is the current strongest
Index-first native-tool result: a pinned real Go `edit_file` source path
reproduced concurrent lost updates and a local scoped patch eliminated those
losses in repeated fixture runs. The supplied `delegate_task` replay still
uses a synthetic child-task selector; it does **not** establish provider-driven
agent productivity, user benefit, upstream adoption or an S2 grade change.

The [assessment-to-improvement protocol](docs/ASSESSMENT_TO_IMPROVEMENT.md)
distinguishes **assessment-derived** functional interventions, **assessment-informed**
engineering fixes and generic upstream contributions. The stronger test starts
from an actual Index function finding, confirms independent product-native
value and measures behavior **before and after** the change; neither a higher
VSM grade nor a merged PR is its success criterion. [Upstream #56](https://github.com/opensiro/upstream/issues/56)
tracks the next Index-first pilot. The already prepared
[HarnessDesk #1772](pilots/harnessdesk-1772/ASSESSMENT_LINKAGE_2026-10-20.md)
socket reliability fix is classified as **assessment-informed**, not a
completed assessment-derived improvement experiment.

## Two independent status dimensions

**Contribution outcome** tracks the result *at upstream*: `research`, `preparing`, `submitted`, `merged`, `closed`, or `not-accepted`. Only a verified upstream merge is marked `merged`.

**Fork lifecycle** tracks the OpenSiro repository itself: `active`, `maintained`, or `archived`. An archived fork does **not** imply that its upstream contribution was accepted.

Typical sequence: **Fork → Research → Implement → Submit → Upstream outcome → Maintain or archive**. Projects can stay `maintained` indefinitely.

## Archiving policy

Before archiving an inactive fork, verify that its planned PRs are resolved or intentionally closed, no known maintenance obligations remain, and this registry contains its final outcome and upstream links. Archive the **public GitHub fork**, retaining its history; do not silently delete it. A need for continued maintenance is reason to keep it active. A fork may be unarchived if maintenance resumes.

The archived state is an explicit decision, **not an automatic action triggered by merged PRs**.

## Assessment-driven S1 function test

The Organization Control Plane command `test S1 function: upstream contributions`
uses the [assessment-driven S1 test contract](docs/ASSESSMENT_DRIVEN_S1_TEST.md).
It **starts with a pinned canonical Index assessment of an AI harness**, then
independently checks whether that finding motivates a real upstream-native
change. A familiar fork, unrelated GitHub issue or lower VSM grade is
insufficient. The result may legitimately be `NO_ELIGIBLE_ASSESSMENT_CANDIDATE`
without creating any fork or PR.

This assessment-to-contribution test is **distinct** from generic OSS discovery,
this repository's existing portfolio and normal contributor-selected upstream
issues. It neither admits a fourth Organization S1 domain nor activates
P1/connected writes or external PR publication.

For a **single read-only assessment-linked proposal and test-file plan**,
[`scripts/assessment_driven_handoff.py`](scripts/assessment_driven_handoff.py)
composes the local [Index-object origin preflight](scripts/assessment_origin_preflight.py)
with the existing [exact prepare-stage handoff](docs/CONTROL_PLANE_HANDOFF.md).
It returns one non-authorizing packet, never a fork, push or external PR. A
local git checkout and proposal fields do **not** prove live canonical Index
origin, external native fit, or authenticated operator authorization.

## Conversation-first contribution proposals (read-only)

[Batch proposal preview](docs/BATCH_PROPOSALS.md) is a **provider-agnostic,
local-only** way to review up to ten possible contributions before an owner
approves anything. Every candidate states the target system's problem,
planned change, **expected (unverified) benefit**, validation and evidence.
It can display the operator's **proposed selection** in JSON or plain text.

```bash
python3 scripts/batch_proposals.py --manifest /path/to/upstream-YYYYMMDD-name.json --draft --select candidate-a,candidate-c --scope 'candidate-a=create_public_fork' --format text
```

The optional `--scope` can **reduce** the stages proposed for each
selected candidate; it cannot add a new action. Without it, a selected
candidate retains all proposed stages for preview. The result includes
`selection_scope_sha256` binding the exact per-candidate stage subset.

This command never contacts GitHub, creates forks, publishes external PRs
or records an approval. Selection and SHA-256 identifiers are **not**
authorization. See [the proposal schema and limitations](docs/BATCH_PROPOSALS.md).

## OSM autonomy-transfer design (prospective)

[OSM delegation design](docs/OSM_DELEGATION_DESIGN.md) maps the proposed progression from agent-owned local preparation to a complete **unpublished** contribution package, while external PR publication remains a separate human right. It is a design for **future attributable delegation**, not an effective mandate, a new S1 domain, or a bypass of the current exact-stage execution gate. [Organization #274](https://github.com/opensiro/vsm-oss-organization/issues/274) still owns the reserved boundary decision.

## Control Plane preparation handoff (read-only)

The existing [OpenSiro OSS Control Plane](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/AGENT_CONTROL_PLANE.md)
can present an [exact prepare-stage handoff](docs/CONTROL_PLANE_HANDOFF.md)
for one selected external contribution. The local
[`control_plane_handoff.py`](scripts/control_plane_handoff.py) validates
one candidate and one proposed `prepare_contribution` action, binding its
selected stage, working fork, pinned base revision, branch, test file and
content digest. It returns `ACTION_PREPARED_NOT_AUTHORIZED` and performs
**no GitHub calls or writes**. A distinct current-session operator decision
and working trusted GitHub port are still required for actual changes.

## Working fork destination: opensiro-contributions (currently blocked)

For Index-assessment-derived contributions, the intended working-fork
namespace is `opensiro-contributions`, **not an ad hoc personal fork**.
See the [provider/authority/branch-aware fork handoff](docs/OPENSIRO_CONTRIBUTIONS_FORK_ROUTE.md)
and tracked [Upstream #28](https://github.com/opensiro/upstream/issues/28).
The existing Control Plane is the only operator entry. The
[source-prepared fork-stage adapter](docs/CONNECTED_FORK_ADAPTER.md) and
[first live pilot contract](docs/FIRST_LIVE_FORK_TEST.md) require a pinned
working branch/SHA and independently verified new-fork readback. They **do not
expose a connected native create-fork operation or effective exact-stage
authorization**. Do not describe old Draft PR #18, unit-test fake providers
or preview-only workflows as fork creation. A candidate requiring a nondefault
branch must prove that exact ref exists in the resulting authorized fork
before preparation.

## Automatic fork execution: existing REST route, currently gated

OpenSiro already has a source-prepared [REST fork client](scripts/create_fork.py)
from [PR #5](https://github.com/opensiro/upstream/pull/5). Its
write-capable workflow was intentionally disabled by
[PR #8](https://github.com/opensiro/upstream/pull/8) pending a trustworthy
approval boundary. A **new custom MCP plugin is not a prerequisite**:
either a protected batch-only Actions/REST executor or a native connected
fork action could satisfy the [upstream execution contract](docs/AUTOMATIC_FORK_EXECUTOR_RECOVERY.md)
once its **actual provider rights and separately authenticated exact-scope
Control Plane authorization** are verified. The
[GitHub CLI execution-host route](docs/CLI_FORK_HOST.md) allows reuse of
an existing **credential-owning VM/host** without naming or depending on
an orchestration application; a reported existing PAT still needs an
execution-user identity and effective permission check. Neither write
route is currently active.
Do not restore the legacy manual `--execute` path or treat a batch
preview as consent. See [Upstream #28](https://github.com/opensiro/upstream/issues/28).

## Organization fork → upstream PR (bounded publication mandate)

The existing credential-owning VM/host has **live verified** one-off fork
creation in `opensiro-contributions` (Issue [#28](https://github.com/opensiro/upstream/issues/28)).
A separate [organization-fork PR handoff](docs/ORGANIZATION_FORK_UPSTREAM_PR.md)
uses **authenticated GETs only** to bind an upstream base and pushed fork
branch to reviewed SHA/diff evidence. It prepares a REST draft payload,
**not** an external PR. The owner has now separately authorized a **finite
34-case Corrective publication cohort** on 2026-10-23: see the
[bounded mandate](docs/CORRECTIVE_PR_PUBLICATION.md),
[validated queue](data/corrective-publication/2026-10-23-01.json) and
[new-session handoff](docs/NEXT_SESSION_CORRECTIVE_PR_PROMPT.md).
For these exact cases only, public fork/working-branch creation and external
**Draft PR** publication no longer require case-by-case operator approval;
fresh source/policy checks, authenticated actual write rights and GitHub
receipts remain mandatory. All other external submissions retain their
separate human publication decision. No external PR is implied by this record.

## Exact two-file contribution preparation (source only)

A [bounded two-file preparation stage](docs/CONNECTED_MULTIFILE_STAGE.md)
now supports the **proposed** production-source-plus-new-regression patch
shape needed for HarnessDesk #1772, while preserving the original
single-test-file adapter unchanged. It binds entire patch bytes, pinned
identical upstream/fork bases, pre/post file contents and one
authenticated, revocable exact stage grant from the **real VM/host**.
A [source-prepared REST Git Data port](docs/REST_MULTIFILE_PATCH_PORT.md)
provides the atomic tree/commit/new-ref algorithm; the [CLI host transport and clean Git patch materializer](docs/CLI_HOST_MULTIFILE_RUNTIME.md) also exist as source. **No trusted provider attestor, effective grant issuer or deployed host binding is connected**; offline pass is not authority to push a fork branch.
External publication outside the exact Corrective mandate remains separately
human-owned. Its bounded exception does not activate the general prospective
fork/patch executor or authorize upstream merges.

## Fork lifecycle automation

The manually dispatched [fork lifecycle workflow](.github/workflows/fork-lifecycle.yml)
is **preview-only on `main`** after [PR #8](https://github.com/opensiro/upstream/pull/8).
It no longer offers an `execute` input, privileged create job or credential
reference. The [public fork preflight](docs/FORK_PUBLIC_PREFLIGHT.md) now checks
live source/working-branch SHA, declared license and destination public
visibility using **anonymous GET requests only**; a green public preflight
is never fork authority. The old [fork lifecycle handoff](docs/FORK_LIFECYCLE.md) is historical
and **not** a deployment checklist.

[Activation issue #6](https://github.com/opensiro/upstream/issues/6)
tracks future execution. The [non-executable authorization and stage contract](docs/BATCH_EXECUTION_BOUNDARY.md)
specifies how a same-session connected agent or separately verified
headless runner could accept **one exact operator decision** without
conflating chat selection with GitHub permissions. The old
[Draft PR #7](https://github.com/opensiro/upstream/pull/7) is superseded
by the merged preview and is **not merge-ready**.

A narrowly limited [connected-stage preparation adapter](docs/CONNECTED_STAGE_ADAPTER.md)
now supplies **source-prepared, mock-tested** one-file test preparation in an
existing writable fork, gated by a trusted session authorization callback.
It is **not connected to a live host** and **not an approved contribution**;
no fork or external PR execution is enabled. It remains under Issue #6.

**Do not provision `UPSTREAM_FORK_TOKEN` or execute demonstration batch #001.**
Neither proposal preview nor fork planning grants external PR publication,
archiving or a new VSM OSS organizational boundary.

## Contributions

For a new project, add a record to `registry.yaml` and a short `projects/<slug>/README.md`. See [CONTRIBUTING.md](CONTRIBUTING.md).

This registry is maintained independently from Cognee's own repositories. Draft work in OpenSiro forks must not be represented as an upstream PR or merge.
