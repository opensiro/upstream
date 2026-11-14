# Batch 40 — new source-first functional opportunities in original Akmatori cohort

**Date:** 2026-11-14 UTC. **Owner:** [Upstream #56](https://github.com/opensiro/upstream/issues/56) / [batch-40 PR #303](https://github.com/opensiro/upstream/pull/303). **Protocol:** SemVer v0.8.0. **Selection:** `EXPLICIT_REVISIT` of the **same ten original repositories** from frozen batch-39 ref `8a5ebb36058140e2b84ae4fb1b0751c9b0be7d89`. No new batch, issue, source reservation, canonical Index change, or migration of frozen artifacts.

**Purpose:** choose source-native *functional* improvements with an identifiable real operator/use-case, rather than continue probing hypothetical duplicates or introducing redundant VSM machinery. The findings below originate in **current first-party upstream issues** and are therefore `GENERAL_UPSTREAM / SOURCE_FIRST`, **not retrospectively assessment-derived** from batch 39.

## Higher-priority lead: [Akmatori #79](https://github.com/akmatori/akmatori/issues/79) — opt-in agent run for Slack `change` messages

**User need:** a team posts a change announcement such as “please review and merge PR X, tested on staging” to a Slack listener channel. Akmatori correctly classifies and stores `change` events but does not run a pre-merge review until a human explicitly asks or a cron job polls. The issue explicitly requests a **per-channel `on_change: store | run` (default `store`)** setting, optional designated skill/runbook, optional message filter, thread reply, and **no incident creation**.

**Pinned product sources:** frozen [`akmatori@be62d92`](https://github.com/akmatori/akmatori/tree/be62d926fe6d92dceb5cf12e9a95cb587433cdf1); freshly observed **current default `main@7afba4fb5919f30233fc859be3626bcfdaedbdb7`**, not silently substituted for the freeze. `internal/handlers/slack_processor.go:handleAlertChannelMessage` uses `ExtractAndClassify`, stores the event with original Slack channel and message-ts provenance, and **returns for any non-`alert` kind**. The current `internal/database/models_channels.go:Channel` does **not** have `OnChange`. `internal/handlers/slack_processor.go:processMessage` is the existing *mention/request* agent-run path; it calls `classifyNewMention` for a new thread, so simply calling it after a listener `change` will repeat the classification.

### Executed native falsifier with two original source states

[Native Go research test](repro/2026-11-14-upgrade40-akmatori-change-listener_test.go) uses **real first-party `SlackHandler`**, first-party `EventService` and GORM SQLite event/incident/run tables, mocked Slack HTTP `conversations.history`, and a controlled first-party one-shot classifier that returns `event_kind=change`. It was executed in **disposable source copies**, not merged into either original checkout or current upstream.

| Scenario | Frozen `be62d92` | Live main `7afba4f` |
| --- | --- | --- |
| One Slack listener PR-announcement classified as `change` | **PASS**: 1 event stored, 0 agent runs, 0 incidents | **PASS**: same |
| **Naïve reuse negative control:** call original `processMessage` for that already classified message to try to obtain an agent run | **PASS**: 2 classifier calls, 2 event records with different source kinds, 0 agent runs | **PASS**: same |
| `go test ./internal/handlers -run '^TestBatch40(ListenerChangeAnnouncementStoresOnly\|NaiveMentionReuseAfterChangeCreatesDuplicateEvent)$' -count=10` | **PASS**, 10 repeats | **PASS**, 10 repeats |

See exact [machine receipt](evidence/2026-11-14-upgrade40-akmatori-change-listener-native.json) with original source pins, commands, first-attempt verbose output, test-file SHA-256, and both repeat suites.

**Product-design finding:** The requested behavior is currently **absent**, and the attractive shortcut “call the request/mention handler with the existing change event” **does not implement the feature**. The first-party mention route **reclassifies** the event and may produce a duplicate `slack_mention` record. It therefore needs a **preclassified event → request-scope/run** pathway which preserves original `event_uuid`, carries the source channel/message thread, and avoids a second classifier call or an incident. Merely allowing `change` to flow into the alert handler would be wrong: alerts go through incident creation.

### Safely bounded proposed owner contract (design only; no implementation)

- **Existing operator authority / S1 channel envelope:** explicit per-channel `on_change=run`, default `store`; channel enabled and integration enabled; message source authorization and `CanListen`; `CanPost` required when user expects thread reply; optional bounded filter and explicit allowlisted skill/runbook selection, not unrestricted model-supplied tool power.
- **S2 event/request routing:** persist the source `change` exactly once with Slack external message ID; use the original `event_uuid` when beginning a **non-incident** request scope/run. Do **not** invoke `classifyNewMention` a second time, and do not allow the classifier to self-approve execution.
- **S3 effect constraints:** preserve current skill/tool allowlist and approval requirements for any action (especially “merge this PR”); an autonomous *pre-merge review* is not permission to merge or modify third-party repositories.
- **Replay and recovery:** a restarted listener or duplicate Slack delivery must not create multiple runs for the same immutable source event; define an atomic `event_uuid` → run admission boundary. An in-memory `processedMsgs` dedup alone cannot prove cross-process behavior.
- **Response scope:** reply in original thread with result/provenance; no incident row, no automatic policy or S5 transfer.

These are **candidate acceptance criteria, not newly granted runtime permissions or evidence of a completed implementation**. They must be checked against channel migration/API/forms/worker routing and the maintainer's intended design.

| Gate | Evidence-based disposition | Missing item |
| --- | --- | --- |
| `need` | **PASS** — exact user request [#79](https://github.com/akmatori/akmatori/issues/79) | No missing demand for `change`-triggered review |
| `mechanism` | **PASS** for existing event, request-scope and threaded-run primitives | Safe code refactor/reuse, not a feature implementation yet |
| `counterfactual` | **PASS** for native *current inability* and negative workaround; **PENDING for independent matched before/after feature benefit** | Test `store` default versus `run`, filter hit/miss, skill auth and retry/idempotency with a real worker fixture |
| `scope` | **PENDING** despite specific user envelope | Confirm migration/API/UI ownership, permissions, recovery, maintainers' desired opt-in setting |
| Admission | **NO_ADMITTED_PATCH** | Full four-gate PASS and independent native before/after before external PR |

## Secondary source-first opportunity: [Akmatori #48](https://github.com/akmatori/akmatori/issues/48) — VictoriaLogs tool during SRE investigation

**Reported incident context:** the user says their service crash-loop evidence was retained in VictoriaLogs after the local journal rotated; VictoriaMetrics *metrics-only* investigation led to a wrong conclusion. This is **user-reported need, not an independently re-enacted production incident**.

**Target surface:** the current gateway already ships `victoria_metrics.instant_query`, `range_query`, `label_values`, `series`, and `api_request`, as well as a credential/cache/rate-limit/HTTP transport module in `mcp-gateway/internal/tools/victoriametrics/`. Both the frozen target and current main do **not** register `victoria_logs`. The requested functionality is not a duplicate of PromQL: **LogsQL** querying, time/line bounds, discovery of field names/values, hits and statistics.

**Independent public API authority:** the official [VictoriaLogs HTTP query API](https://docs.victoriametrics.com/victorialogs/querying/) documents the exact requested routes: `/select/logsql/query`, `/select/logsql/hits`, `/select/logsql/field_names`, `/select/logsql/field_values`, and `/select/logsql/stats_query`. Outputs include **newline-separated JSON log rows** for some query operations and summary JSON for aggregate endpoints, so copying the VictoriaMetrics Prometheus-response parser would be unsafe. Time-window, response-body and log-line caps; bearer/basic/custom-header auth; explicit proxy/SSRF boundaries; tenant isolation and secrets redaction need native verification.

**Provisional gates:** `need=PASS` (issue #48), `mechanism=PASS` for the existing modular gateway HTTP/registration pattern and the documented VictoriaLogs routes, `counterfactual=PENDING` for a native first-party mock-service-to-agent fixture with a previously invisible diagnostic log message and strict negative controls, `scope=PENDING` for credential/catalog/UI/API parity and maintainer preference. **No implementation claim**. As a genuine new observation/diagnostic capability, this may be more measurable than endlessly revisiting an already-present SDK hook.

## Priority decision and negative outcomes

**Order of remaining functional proof:** (1) Akmatori #79: explicit operator-triggered review, native listener test reproduced twice and straightforward expected output; (2) Akmatori #48: log acquisition for SRE, exact public LogsQL HTTP contract, needs a live module and bounded data fixtures; (3) older Akmatori #67: semantic cross-incident corroboration still needs validated independent evidence and operator confirmation semantics. The previously researched `go-agent-harness` concurrent-effect controls are legitimate technical findings but have **no matching first-party product issue/contract in its observed issue corpus**, and the SDK's `BeforeTool`/`CustomData` already allows caller-side mitigation. Do **not** promote that hypothetical SDK feature over the two confirmed Akmatori user needs.

**Review status:** `SCREENING_COMPLETE` for historical 60-row source inventory, **`OPPORTUNITY_RESEARCH_PENDING` for actual product opportunity validation**. No four-gate PASS, no independent product improvement measurement, no upstream implementation and no external derivative PR. Preserve source attribution and immutable batch-39 records.
