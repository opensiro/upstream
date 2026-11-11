# Documentation map

The root [README.md](../README.md) is the public handoff. [AGENTS.md](../AGENTS.md) routes agent work. [UPSTREAMING.md](../UPSTREAMING.md) is the **local ownership and lifecycle contract**. This directory contains detailed operating procedures, evidence models and historically bounded designs.

## Current operator navigation

| Task | Owner document |
| --- | --- |
| Which GitHub Action to use, what to keep, what to retire | [ACTIONS.md](ACTIONS.md) · [native CI placement](NATIVE_CI_EXECUTION.md) · [migration issue #214](https://github.com/opensiro/upstream/issues/214) |
| Tests, automation, scheduled sensing, generated views | [OPERATIONS.md](OPERATIONS.md) |
| Five-source upstream screening | [ASSESSMENT_CANDIDATE_BATCHES.md](ASSESSMENT_CANDIDATE_BATCHES.md) |
| Five-repository external publication waves | [EXTERNAL_PUBLICATION_WAVES.md](EXTERNAL_PUBLICATION_WAVES.md) · [working-fork-first pipeline](CONTINUOUS_WORKING_FORK_PIPELINE.md) |
| Upstream Auto (on-demand task balancing and opt-in CAS claims) | [UPSTREAM_AUTO.md](UPSTREAM_AUTO.md) · [owner issue #161](https://github.com/opensiro/upstream/issues/161) |
| Assessment → testable external improvement | [ASSESSMENT_TO_IMPROVEMENT.md](ASSESSMENT_TO_IMPROVEMENT.md) |
| Native effect evidence, not adoption | [FUNCTIONAL_EFFECTS.md](FUNCTIONAL_EFFECTS.md) |
| External PR maintenance and triage | [PR_MAINTENANCE.md](PR_MAINTENANCE.md) · [PR_MAINTENANCE_TRIAGE.md](PR_MAINTENANCE_TRIAGE.md) |
| Official resolved-PR acceptance | [RESOLVED_PR_ACCEPTANCE.md](RESOLVED_PR_ACCEPTANCE.md) |
| Dated external PR observations and bounded history | [PORTFOLIO_HISTORY.md](PORTFOLIO_HISTORY.md) |
| Verified external outcomes — candidate observation vs accepted-source export | [VERIFIED_EXTERNAL_OUTCOMES.md](VERIFIED_EXTERNAL_OUTCOMES.md) |
| External PR state freshness | [UPSTREAM_STATUS_FRESHNESS.md](UPSTREAM_STATUS_FRESHNESS.md) |
| Guarded status-drift patch and manual Draft PR | [OPERATIONS.md](OPERATIONS.md#external-observation-read-only) |
| Cross-lane status model | [HARNESS_STATUS_MODEL.md](HARNESS_STATUS_MODEL.md) |
| Corrective publication authority | [CORRECTIVE_PR_PUBLICATION.md](CORRECTIVE_PR_PUBLICATION.md) |
| Control Plane → local prepare | [CONTROL_PLANE_HANDOFF.md](CONTROL_PLANE_HANDOFF.md) |
| Standing autonomous fork/patch preparation (no per-action owner prompt) | [STANDING_PREPARATION_AUTONOMY.md](STANDING_PREPARATION_AUTONOMY.md) · [current policy](../policies/standing-preparation-p1.json) · [execution gate #6](https://github.com/opensiro/upstream/issues/6) |
| Source-native PR proposal and disclosure in its working fork | [UPSTREAMING.md](../UPSTREAMING.md#contribution-lifecycle) · [AI disclosure](AI_ASSISTED_PR_DISCLOSURE.md) |
| Supervised org-fork bootstrap and cross-plugin internal contributions | [FORK_BOOTSTRAP_AND_COLLABORATION.md](FORK_BOOTSTRAP_AND_COLLABORATION.md) · [read-only proposal](../data/contribution-workspaces/fork-bootstrap-proposal.json) |
| Source collision preflight and optional reservation | [ASSESSMENT_SOURCE_RESERVATIONS.md](ASSESSMENT_SOURCE_RESERVATIONS.md) |

## Detailed designs and gated execution

- **Proposal and selection:** [BATCH_PROPOSALS.md](BATCH_PROPOSALS.md), [ASSESSMENT_DRIVEN_S1_TEST.md](ASSESSMENT_DRIVEN_S1_TEST.md) and [BATCH_EXECUTION_BOUNDARY.md](BATCH_EXECUTION_BOUNDARY.md).
- **Fork creation and stage adapters:** [AUTOMATIC_FORK_EXECUTOR_RECOVERY.md](AUTOMATIC_FORK_EXECUTOR_RECOVERY.md), [BATCH_FORK_HOST_GATE.md](BATCH_FORK_HOST_GATE.md), [CONNECTED_FORK_ADAPTER.md](CONNECTED_FORK_ADAPTER.md), [CONNECTED_STAGE_ADAPTER.md](CONNECTED_STAGE_ADAPTER.md), [CONNECTED_MULTIFILE_STAGE.md](CONNECTED_MULTIFILE_STAGE.md).
- **Host/provider transports:** [CLI_FORK_HOST.md](CLI_FORK_HOST.md), [CLI_HOST_MULTIFILE_RUNTIME.md](CLI_HOST_MULTIFILE_RUNTIME.md), [REST_FORK_PORT.md](REST_FORK_PORT.md), [REST_MULTIFILE_PATCH_PORT.md](REST_MULTIFILE_PATCH_PORT.md), [ORGANIZATION_FORK_UPSTREAM_PR.md](ORGANIZATION_FORK_UPSTREAM_PR.md), [OPENSIRO_CONTRIBUTIONS_FORK_ROUTE.md](OPENSIRO_CONTRIBUTIONS_FORK_ROUTE.md).
- **Authority and bounded pilots:** [OSM_DELEGATION_DESIGN.md](OSM_DELEGATION_DESIGN.md), [P1_SCOPE_PREFLIGHT.md](P1_SCOPE_PREFLIGHT.md), [BOUNDED_LOCAL_PREPARE_MANDATE.md](BOUNDED_LOCAL_PREPARE_MANDATE.md), [FORK_PUBLIC_PREFLIGHT.md](FORK_PUBLIC_PREFLIGHT.md), [FORK_LIFECYCLE.md](FORK_LIFECYCLE.md), [FUNCTIONAL_EFFECTS.md](FUNCTIONAL_EFFECTS.md).

Many adapter documents are deliberately **source-prepared, mock-tested or historical**. The narrow standing preparation mandate is issued, but an active policy file alone does not prove provider-authenticated execution or authorize external PR publication. Read its exact gate and owning issue.

## Historical handoffs and dated receipts

- [Historical publication wave 01](../reports/2026-11-11-external-publication-wave-01.md), [FIRST_LIVE_FORK_TEST.md](FIRST_LIVE_FORK_TEST.md), [NEXT_SESSION_CORRECTIVE_PR_PROMPT.md](NEXT_SESSION_CORRECTIVE_PR_PROMPT.md), [IMPROVEMENT_PR_PUBLICATION_2026-10-24.md](IMPROVEMENT_PR_PUBLICATION_2026-10-24.md).
- [Reports](../reports/README.md), [casebook](../cases/README.md), [technical pilots](../pilots/README.md).

For current S1 admission and S5 authority, the [Organization repository](https://github.com/opensiro/vsm-oss-organization) is authoritative; an older document's historical admission status must not override it.
