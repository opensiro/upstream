# Batch 40 — native concurrent tool-effect identity and crash boundaries

**Date:** 2026-11-14 UTC. **Owner:** [Upstream #56](https://github.com/opensiro/upstream/issues/56), [batch-40 PR #303](https://github.com/opensiro/upstream/pull/303). **Protocol:** SemVer v0.8.0. **Selection:** explicit revisit of the frozen ten-source batch-39 set; no new source-disjoint selection, new batch, Index assessment, or owner change. **Classification:** source-first `GENERAL_UPSTREAM / ASSESSMENT_INFORMED` technical findings, **not** proven `ASSESSMENT_DERIVED` VSM benefit.

**Pinned original:** [`shalyhinpavel/go-agent-harness@63a2a153`](https://github.com/shalyhinpavel/go-agent-harness/tree/63a2a15315c3a52964bcbc8b15d48f97f49f5a21); original checkout remained clean. Relevant shipped APIs: [`agent/types.go`](https://github.com/shalyhinpavel/go-agent-harness/blob/63a2a15315c3a52964bcbc8b15d48f97f49f5a21/agent/types.go) has `Hooks.BeforeTool`, `ChatRequest.CustomData` and `HookContext.CustomData`. `CustomData` is explicitly an embedding-program supplied context rather than data obtained from the wire. Earlier batch-40 [Go session-retry test](repro/2026-11-14-upgrade40-go-agent-store-retry_test.go) and [existing hook mitigation](repro/2026-11-14-upgrade40-go-agent-file-ledger_test.go) already proved that a failed post-effect session append can lose a tool result and that a consumer-owned durable effect ledger may suppress *sequential* replay.

## New first-party engine executions (source-native, no upstream modifications)

The [new reproducible Go test](repro/2026-11-14-upgrade40-go-agent-concurrent-identity_test.go) uses two **real first-party `AgentEngine` instances** with separate sessions, the original `NewToolRegistry` / `Hooks.BeforeTool` / `ChatRequest` methods, deterministic `llm.MockProvider` and synthetic local filesystem effects. It is a **research-only file in a disposable checkout**. The [machine execution receipt](evidence/2026-11-14-upgrade40-go-agent-concurrent-idempotency.json) contains original pin, fixture SHA-256 and exact output. The four root tests (five distinct result scenarios) passed once verbosely and then passed in **20 consecutive reruns** at Go 1.27.4.

| Source-native scenario | Observed synthetic side effects | Interpretation |
| --- | ---: | --- |
| **Concurrent ordinary check-and-allow**: both hooks read a missing completed-effect file before either runs the effect; both executions write the marker afterward | **2** | A non-atomic `BeforeTool` check cannot make two separate engines mutually exclusive, even when model tool-call IDs are the same |
| **Atomic application claim** with `os.OpenFile(O_CREATE\|O_EXCL)` before execution | **1** | An application-side claim can exclude one concurrent executor within this no-crash fixture. This capability is already compatible with the SDK |
| **Crash window**: simulate pre-existing claim persisted but actual effect never happened | **0** | An exclusive claim alone creates a risk of **permanently suppressing a needed retry**. It is not exactly-once execution |
| **LLM tool-call ID drift**: after effect executes and session outcome append fails, user retries the same business operation with a different model-issued `ToolCall.ID` | **2** | Treating a model-generated call ID as the *cross-attempt business transaction key* is unjustified and unsafe |
| **Stable caller business identity**: same replay, but the embedding program supplies stable `business_id` via `ChatRequest.CustomData`, and the shipped `BeforeTool` checks a separate completed-effect ledger using `HookContext.CustomData` | **1** | The SDK **already supplies** the necessary context/hook to enforce a **consumer-owned sequential duplicate suppression** policy in this fixture |

The first test synchronizes both reads using a barrier; the effect writes a completion marker after passing the non-atomic check. This is not merely a missing-file stub: both first-party engine calls actually execute and record the simulated effect after the check.

The successful `O_EXCL` and stable-key controls are deliberately **not claimed as a complete transaction protocol**. `O_EXCL` provides a reservation in this filesystem fixture, not an atomic external payment, rollback, recovery, recorded final outcome or uncertainty resolution. If a process dies between claim and effect, the claim can exist with **zero** completed operations. Likewise, a stable key prevents replay only when the consumer actually supplies, stores and binds it to one business operation; the model's `ToolCall.ID` alone is not such an end-to-end promise.

## Admission ledger and ownership boundaries

**What this establishes:** a reproducible concurrence/control boundary, another failure mode for model-ID-only replay protection, and a strong negative control showing that an application can use **existing** `BeforeTool` and caller-owned `CustomData` to reduce duplicates. The implementation's app/server owner must choose semantics based on actual external effects. A generic SDK cannot infer which two tool calls mean the same transaction.

**What it does NOT establish:** an outstanding consumer-reported defect, a reproducible real-world duplicate payment, a missing SDK primitive, a replacement for a transactional external API, a VSM attribution to S1/S3*, or an admitted feature. Searches for the terms `idempotency`, `retry tool`, `duplicate tool` and `crash session` in the upstream GitHub issue corpus returned no matching issue in this inspection; absence of search results is not proof no users need the feature.

| Gate | State | Required next evidence |
| --- | --- | --- |
| `need` | **PENDING** | Concrete target embedding/maintainer use case requiring retriable non-idempotent tool effects; the current repo's generic SDK does not promise exactly-once |
| `mechanism` | **PASS** (existing hook and caller data, synthetic mechanisms) | No additional SDK core change admitted; candidate application-level transaction/outbox adapter boundary needs ownership |
| `counterfactual` | **PASS only for controlled technical fixtures; PENDING for product benefit** | Compare actual caller-owned effect ledger vs baseline with realistic cross-process retries, concurrent claims, ambiguous result and injected failures |
| `scope` | **PENDING** | Define authenticated caller business key, atomic action+record boundary, idempotent external endpoint, `pending/completed/failed/unknown` reconciliation, retention and remediation of ambiguous outcomes |

### Functional design to test, not to publish as a patch

A useful future integration contract would be: **S1 request provenance/identity** from an authenticated caller; **S3 operational safeguard** in the existing hook/transaction adapter; **external effect owner** controlling its own transaction and reconciliation; **operator-controlled escalation** for `unknown` outcomes. These are an engineering decomposition of a hypothesis, **not new VSM semantics** or upgraded Index function scores.

Next decisive test: identify an actual user-managed tool integration and execute simultaneous **separate-process** retries against a genuinely idempotent operation endpoint (or a local transactional stand-in with commit/ack failure injection), including a forced **crash between reserve and effect**. Compare duplicate count, lost count and indeterminate outcomes with the same business keys and replay schedule. Only admission-gate evidence and independent native before/after justify a product PR. No external PR, no third-party patch, and no source modifications were made.

**Status:** `SCREENING_COMPLETE / OPPORTUNITY_RESEARCH_PENDING / NO_ADMITTED_PATCH`. Previous batch 39 freeze, candidate ownership and upstream protocol v0.8.0 are unchanged.


## Further native control: two tool calls inside one model turn

In the previous concurrent test, two separate engine instances raced. The *original SDK itself* also intentionally uses [`executeToolsParallel` in `agent/loop.go`](https://github.com/shalyhinpavel/go-agent-harness/blob/63a2a15315c3a52964bcbc8b15d48f97f49f5a21/agent/loop.go), with `MaxParallelTools` controlling fan-out. The [additional source-native test](repro/2026-11-14-upgrade40-go-agent-same-turn-parallel_test.go) issues **two different model ToolCall IDs for one caller-owned business operation within a single MockTurn**, passing a shared authenticated `business_id` through the original `ChatRequest.CustomData` / `HookContext.CustomData` path.

| Same-turn scenario | Synthetic effects |
| --- | ---: |
| `MaxParallelTools=8`, two hooks concurrently observe absent completed-effect marker, then both tools execute | **2** |
| `MaxParallelTools=1`, identical completed-effect hook, each call serially sees the preceding completion | **1** |
| `MaxParallelTools=8`, consumer-owned `O_EXCL` reservation within `BeforeTool` | **1** |

All three original SDK paths **PASS** the [native receipt](evidence/2026-11-14-upgrade40-go-agent-same-turn-parallel-race.json): one verbose trial, **50 repeat trials**, and **3 trials under Go `-race`** (no race detected). Two processes/hosts are not covered by `MaxParallelTools=1` on one engine. Conversely, `MaxParallelTools=1` is already supported and **serializes all tools, including unrelated read-only operations**, so setting it globally incurs avoidable performance/parallelism tradeoffs. The `O_EXCL` claim remains an *application-owned* best-effort at-most-once reservation and does not establish crash-safe exactly-once execution.

**Clarification of product admission:** this is a meaningful *behavioral* boundary with reproducible controls, **not** proof of a missing SDK bug or that any maintainer wants native transactional semantics. The valid design space is an embedding-owned effect key and idempotent external effect API. `need=PENDING; mechanism=PASS; counterfactual=PASS for synthetic mechanism only, PENDING for product uplift; scope=PENDING`. **NO_ADMITTED_PATCH** remains unchanged.
