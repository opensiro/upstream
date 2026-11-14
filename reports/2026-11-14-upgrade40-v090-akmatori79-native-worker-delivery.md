# Batch 40 — Akmatori #79: native WebSocket worker → Slack thread capability and crash-boundary test (v0.9.0)

**Date:** 2026-11-14 UTC · **Parent:** [Upstream issue #56](https://github.com/opensiro/upstream/issues/56), [research PR #303](https://github.com/opensiro/upstream/pull/303) · **Protocol:** current prospective contribution SemVer **0.9.0**, [capability-first procedure](https://github.com/opensiro/upstream/blob/main/docs/CAPABILITY_FIRST_RESEARCH.md).

This is an explicitly authorized continuation of **the same batch 40 explicit revisit of the frozen batch 39 cohort**, not a new batch, issue, reservation, manifest field or rewrite of historical v0.8.0 reports. Source-first user demand originates at [Akmatori issue #79](https://github.com/akmatori/akmatori/issues/79). **Attribution is SOURCE_FIRST / ASSESSMENT_INFORMED (at most), not strict ASSESSMENT_DERIVED.** The first-party issue is not proof of maintainer acceptance of this exact implementation.

## 1. New user capability, not a repair

| v0.9.0 required question | Bounded, source-grounded answer |
| --- | --- |
| **Who needs it?** | Teams announcing a PR release/change in a configured Slack listener channel, with human testing context in their message; Akmatori #79 explicitly asks for optional review-on-change |
| **New task** | A `change` announcement can **initiate a read-only pre-merge review without a cron poll, separate @mention or incident**; the operator receives the review in the **original thread** |
| **Trigger → action → output** | Slack listener `change` classification → one authorized, source-key-idempotent *request* scope and native WebSocket `new_incident` worker frame → completed `AgentRun` → native `finishSlackMessage` sends a thread reply |
| **Original alternative** | Original listener saves `change` as an `Event` and stops with **zero agent run / zero Slack review reply**; human mention/cron can create separate work |
| **Native benefit proxy** | Matched fixed input and fixture response: **0 → 1 request-run and 0 → 1 same-thread answer**, while first receipt has **one event, one classifier call, zero incidents** |
| **Safety/compatibility** | `store` default remains untouched; experiment allows no worker tools (`tool_allowlist: []`), carries an explicit *never merge* read-only task, preserves `event_uuid` and source message key, and tests one redelivery + negative crash interval |
| **VSM relevance** | An operator-governed **S1 task admission**, source-to-run **S2 coordination**, explicit permission gates akin to **S3 control**, evidence/provenance useful to audit; this is a proposed interpretive map, **not proof of S3/S4 autonomy, source causal derivation or Index regrade** |

## 2. Sources, exact provenance and reproducible experiment

**Original frozen cohort source:** `akmatori/akmatori@be62d926fe6d92dceb5cf12e9a95cb587433cdf1`. **Separately observed current source:** `akmatori/akmatori@7afba4fb5919f30233fc859be3626bcfdaedbdb7`. The current commit must not silently replace the original cohort pin.

The earlier [v0.9.0 capability readback](2026-11-14-upgrade40-v090-akmatori79-capability-readback.md) proved only first-party event/agent-run/thread DB handling with an injected result. **This new experiment extends that evidence to the real first-party WebSocket transport and real first-party Slack API post adapter**, but with explicitly fake remote endpoints.

Research artifacts:

- [Source-native Go test](repro/2026-11-14-upgrade40-akmatori-onchange-worker-native_test.go) — SHA-256 `527f88095bb5b3791e5afd6de1318c3df927be7ddb99c497902ff1a08320f973`. Three native checks: worker/thread integration, concurrent DB-source-key claim and the crash-gap counterexample.
- [Experimental two-file, zero-context source seam](repro/2026-11-14-upgrade40-akmatori-onchange-worker-integration-seam.patch) — SHA-256 `58cc400fe5407bc8d22d9154a9437cbfec905ccc4a5281ede54d6453cb86cb19`. Only adds a **research-only hook after the original listener stores a non-alert `change` event**. Its test-only callback provides candidate behavior. **NOT a product patch or an approved permanent handler API.** Applying it uses `git apply --unidiff-zero <path>` on a disposable, exact-pinned source copy; applicability was checked on *both* original pins.
- [Machine-readable executions](evidence/2026-11-14-upgrade40-akmatori-onchange-worker-slack-native.json) — six exact command/output receipts, the source/patch hashes, observed controls, stop gates and failure semantics. The source owner checkout remained clean.

The test creates a real local `AgentWSHandler` WebSocket server and an independently connected fake worker over the `gorilla/websocket` client, and a local `httptest` Slack server handling `chat.postMessage`. It invokes the **real `SlackHandler.handleAlertChannelMessage`**, original one-shot extraction and native `EventService.Record`. The experimental hook calls the **original `SkillService.PrepareRequestScope`, `BeginRun`, `AgentWSHandler.StartIncident`, `ReleaseRun` and `SlackHandler.finishSlackMessage`**. The fake worker returns a **constant scripted review response**. No real AI-generated review, GitHub merge action, Slack workspace traffic or external tool access is involved.

The wire protocol frame type is `new_incident` (the original worker message enum also uses it for a **non-incident request**); in the original database there is **no `Incident` row** for this request. A test-only `batch40_research_change_claims` table, with a primary key `channel_uuid:message_ts`, controls candidate source-message admission. **This schema is not a proposed maintainer-approved migration.**

## 3. Native results (bounded and repeatable)

| Measured fixture property | Original `on_change=store` | Experimental source-triggered `run` |
| --- | ---: | ---: |
| Change event initially stored / classified | 1 / 1 | **1 / 1** |
| Native worker request dispatched | **0** | **1 `new_incident` WebSocket frame** |
| `AgentRun` persisted and finished | **0** | **1 `completed`** |
| Slack thread reply through first-party client | **0** | **1 `chat.postMessage`**, original channel + root timestamp |
| Incident opened | **0** | **0** |
| Tools passed to worker | — | **Explicit empty allowlist `[]`** |
| Duplicate same Slack message delivered | — | **0 additional runs and 0 additional posts** |

**Native evidence:** all three scenarios passed **20 executions** on each pinned source (`go test ./internal/handlers -run '^TestBatch40(NativeChangeWorkerToSlackThread|ClaimAtomicIndependentConnections|NativeAtMostOnceClaimCanStrandUndispatchedChange)$' -count=20`). All three passed `go test -race` **twice on both pins**. The broader **`go test ./internal/handlers -count=1`** passed on the current-main-pin disposable tree including the hook and test file.

**Independent-connection claim test:** two independently opened, file-backed SQLite GORM connections concurrently attempt `ON CONFLICT DO NOTHING` for the same `channel_uuid:message_ts`; one gets the claim. This is **not** a distributed multi-host, multi-process or production PostgreSQL guarantee.

**Critical counterexample (also a PASS test):** persist the source-message claim and simulate a crash before `BeginRun`/worker dispatch; reopen the database and retry. The claim remains, retry admits **zero** jobs, and **zero** `AgentRun` rows exist. The prototype therefore achieves at-most-once **admission** but can irrecoverably drop the **new user task**. This is a discovered **design requirement for the new feature**, *not* evidence that original Akmatori has a defect (it does not implement this behavior yet).

**Do not overstate:** the real Slack workspace did not receive a response; only the original SDK wrote to the mock API. The emitted review body is a fixture, not task-quality evidence. The experimental research hook is intentionally not a persisted `Channel.on_change` setting, API/frontend schema or production source patch. Duplicate Slack delivery still records a second event and could incur another classifier call; the source-key admission only blocks duplicate **run/response**. No measured adoption, time saving, human review quality, production reliability or VSM autonomy uplift.

## 4. Fit / authority disposition

| Gate | Current result |
| --- | --- |
| `need` | **PASS** for target-owned #79 user demand; maintainer's detailed implementation design not settled |
| `mechanism` | **PASS** for bounded first-party event → request scope → WebSocket worker protocol → completed run → mock Slack thread post, with a disposable research seam |
| `counterfactual` | **PASS for scripted native capability transport** (original zero → experimental one); **PENDING actual AI review quality, real workspace operation and independent production-effect confirmation** |
| `scope` | **PENDING** — the reproducible *claim-before-dispatch* crash gap, channel configuration/storage/API, skill allowlist and trusted source permissions, threaded follow-up behavior, delivery retries and upstream maintainer boundary remain |
| Overall | **`OPPORTUNITY_RESEARCH_PENDING / NO_ADMITTED_PATCH`**; no four full-PASS, no external Akmatori PR, no completed assessment-derived autonomy-improvement cycle |

### Next decisive design step

Before any external implementation, obtain a maintainer-compatible **durable delivery contract**: source-key deduplication at ingress, an atomic stateful outbox or durable leased dispatch claim, explicit transition / retry owner and expiry handling, an idempotent worker execution key and an independently checked Slack post/reply policy (including crash-after-post ambiguity). Decide who may enable `run`, which skills and tools are allowed (read-only review cannot auto-merge a PR), how the default `store` stays compatible, and what optional regex should mean. Then demonstrate a deterministic original-vs-new **completed** workflow with injected failures at each boundary and an independent runner. Do **not** promote technical test success to autonomous authority or to human/product benefits.

**Intended classification:** `SOURCE_FIRST MINOR_FEATURE` candidate. Reliability/dedup work is a necessary *supporting constraint*, not an independent claim that a bug fix is a new feature. Frozen batch 39 and prior v0.8.0 research remain immutable.
