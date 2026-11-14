# Batch 40 / Akmatori #79 — durable outbox recovery design falsifiers (protocol v0.9.0)

**Execution:** 2026-11-14 UTC · **Owner:** [Upstream issue #56](https://github.com/opensiro/upstream/issues/56) · **Existing research:** [PR #303](https://github.com/opensiro/upstream/pull/303) · **Target-owned user need:** [Akmatori issue #79](https://github.com/akmatori/akmatori/issues/79).

**Protocol and origin:** prospective Upstream contribution SemVer **v0.9.0 capability-first continuation** of the *same* batch-40 explicit revisit of batch 39's pinned ten repositories. This does not create a new cohort, source reservation, issue or manifest class, nor rewrite frozen batch 39 or the historical v0.8.0 execution. First-party issue #79 supplies a **SOURCE_FIRST** independently useful new user task; this is **not** an Index-first / `ASSESSMENT_DERIVED` intervention.

## Capability hypothesis — unchanged before and after comparison

**Operator:** a team announcing a PR with its testing context in a configured Slack listener channel.

**New task:** optional `on_change=run` requests a read-only pre-merge risk/test/rollback review in the original Slack thread, without a cron poll, direct @mention, an incident or automatic PR merge. Existing `on_change=store` saves the classified `change` event and starts **zero** worker runs; previous bounded [worker→mock-Slack native test](2026-11-14-upgrade40-v090-akmatori79-native-worker-delivery.md) demonstrated **one** request run and **one** mock Slack-thread reply only with an experimental handler seam, a **fake** worker response and **zero** incidents.

**Motivation for this bounded follow-up:** the earlier source-message claim avoided duplicate work but a crash after claiming and before worker send permanently lost the *new* user task. Without a recovery mechanism, a product feature claiming autonomous pre-merge review would be unreliable even if its ordinary happy-path Go tests passed. Therefore this experiment tests the **specific user-task delivery scope**, rather than promoting a generic reliability fix to an independently delivered feature.

## New source-native recovery experiment

The original first-party source checkouts are pinned at:

- Frozen cohort `akmatori/akmatori@be62d926fe6d92dceb5cf12e9a95cb587433cdf1`.
- Separately observed live main `akmatori/akmatori@7afba4fb5919f30233fc859be3626bcfdaedbdb7`.

Artifacts:

- [Five-case Go native research test](repro/2026-11-14-upgrade40-akmatori-durable-outbox-native_test.go) — SHA-256 `51413a798772ad3d105f96aa7b820882eb677fd99ed0090a3c10c1199fc14517`.
- [Machine-readable six execution receipts](evidence/2026-11-14-upgrade40-akmatori-durable-outbox-native.json) — exact commands, stdout/stderr excerpts, source pins, scope limits and statuses.

**Important distinction:** the new `batch40_research_durable_change_outbox` SQLite table, admission transaction, conditional leases, states and claim/ack transitions exist **only in a Go test file copied into disposable pinned Akmatori checkouts**. Akmatori's original `EventService.Record` is not transactionally coupled to an outbox. No new production table/schema, migration, handler API, worker retry or Slack acknowledgment logic is integrated into the third-party repository. This is a falsifier and bounded engineering proof, **not a proposed finished patch**.

The study uses GORM's real SQLite database driver with **on-disk, reopenable databases** (not just in-memory mocks), native Akmatori `database.Event` and `database.AgentRun`, actual `SkillService.PrepareRequestScope` and `BeginRun`, and the original `database.FinishAgentRun` durable completion primitive. Deterministic synthetic timestamps stand in for lease passage; no live LLM, external network, Slack workspace or user review is invoked.

### Five tested native cases

| Test | Observed contract | What it does **not** prove |
| --- | --- | --- |
| `AtomicEventAdmissionAndRollback` | A **prototype** transaction commits an `Event` and outbox intent together or rolls both back; duplicate Slack source key produces 2 Event rows but **1** outbox job; a new DB connection reads the same intent | Original `EventService.Record` does **not** provide this atomic integration |
| `LeaseExpiryRecoversLostDispatch` | Lease owner A reserves but crashes before run; owner B fails before expiry, succeeds after expiry; A cannot mark B's work; a single native request run completes, and `completed` cannot be reclaimed | Real worker execution, crash after worker acceptance, exact-once side effects |
| `ConcurrentLeaseFencing` | Two independent SQLite GORM connections compete on the same pending source key; **one** conditional lease claim wins; `attempts=1` | Separate OS processes / multi-host PostgreSQL semantics |
| `SlackPostAmbiguityFailsClosed` | Simulated Slack success before saving a receipt leaves `posting`; blind replay is rejected and receipt is **not** fabricated | That a lost acknowledgment is recoverable or safely repostable |
| `SubmittedWithoutAckRequiresReconciliation` | The `submitted` state after an uncertain worker send blocks blind replay but can leave an unconfirmed user task | Guaranteed worker acceptance, safe retry or worker-side run-ID dedup |

**Measured bounds:** five cases passed **20 full repetitions on frozen pin** and **20 repetitions on observed-main pin**; additionally **two Go `-race` runs per pin**, all PASS. The full first-party `go test ./internal/handlers -count=1` package passed in the observed-main disposable checkout with the research tests installed. All six individual receipt executions have exit code 0. The original frozen target checkout remains clean.

The first exploratory implementation had a **test-fixture** GORM copying mistake: the duplicated `Event` retained the inserted primary-key `ID` and was rejected as `UNIQUE constraint failed: events.id`. Resetting the copied test record's generated primary key correctly simulates a *second inbound event*. Separately, using `SkillService.FinishRun` in a short-lived fixture scheduled background memory-file regeneration that raced test temporary-directory cleanup; the final proof uses the same original durable `database.FinishAgentRun` persistence primitive directly and does not attribute that scratch-fixture cleanup issue to the target product. Both failures were corrected **before** the separately repeated PASS receipts.

## Design decision: delivery guarantees cannot be claimed from a lease alone

`pending` → `leased(owner,expiry)` → `submitted` → `completed` → `posting` → `posted` is an *experimental decision sketch*, not the approved third-party state model. A lease expires safely only when **no ambiguous externally accepted work** remains. Where a WebSocket send or Slack post may already have succeeded, blindly reclaiming and repeating the external side effect risks duplicate agent work or duplicate Slack messages; refusing every retry risks silently losing the review.

For a source-owner-compatible design, **one exact decision** is still needed on each interface:

1. **Event-to-outbox atomicity:** the original listener's `EventService.Record` must either commit a durable dispatch intent in the **same** transaction with captured per-channel `on_change` permission/policy, or provide a separate replayable event-to-intent reconciler that cannot silently activate old events after policy changes. A test-only transaction does not make the current handler atomic.
2. **Worker side:** stable per-event `run_id`/deduplication key, durable acceptance/completion acknowledgments, a source-gated lease owner and explicit recovery rules. The current `AgentWSHandler.StartIncident` WebSocket send and callback lifecycle do not by themselves prove a crash-safe distributed transaction with the worker.
3. **Slack side:** distinguish `posting` from `posted` only after trusted source-side acknowledgment and a verified re-read/reconciliation strategy for lost receipts. Do **not** assert `chat.postMessage` exactly-once or automatically post twice when receipt history is ambiguous.
4. **Permissions:** preserve default `store`, source provenance, channel `Enabled`/`CanListen`/`CanPost` checks, opt-in operator setting, trusted skill and tool allowlists, no automatic GitHub merge rights and no escalation from `change` into an incident.
5. **Source-native verification:** repeat the exact scripted capability before/after in a disposable *integrated* production-path implementation, including interrupted transaction, worker-dispatch and Slack-post boundaries; independently verify target support, native CI and first-party review rights before any external patch.

A new recovery mechanism has to be assessed **as support for #79's new operator task**, not scored as another new feature solely because it contains retries, leases or a table. Equally, newly observed evidence does **not** prove that existing Akmatori has a product bug: `on_change=run` is not implemented in the target source.

## Admission and research disposition

| Fit gate | Assessment |
| --- | --- |
| `need` | **PASS**, first-party #79 explicit customer/operator capability request; exact maintainer implementation contract not agreed |
| `mechanism` | **PASS for research fixtures**: original event, request and persistent GORM/SQLite mechanisms support a bounded independently testable lease/recovery design |
| `counterfactual` | **PASS only in scripted offline native scope** for pre-send crash recovery and replay suppression; real worker outcome and user-facing review quality remain PENDING |
| `scope` | **PENDING**: original listener–outbox integration, PostgreSQL/source-native migration, worker acceptance/reconciliation, Slack receipt ambiguity and operator permissions |
| Overall | **`OPPORTUNITY_RESEARCH_PENDING / NO_ADMITTED_PATCH`**. No four full PASS, third-party feature delivery, maintainer acceptance, real product benefit, S3/S4 autonomy improvement or Index grade change established |

**Stop/follow-up:** preserve these falsifiers; do not loop further generic SDK/fault-injection probes as evidence of the new capability. The owner decision now required is the **end-to-end delivery/permission contract**, especially behavior after an ambiguous worker/Slack acknowledgment. With that decision, test the smallest integrated change in a disposable source tree and revisit the four gates. Until then, the next research work in the *same* frozen cohort can move to a separately demanded new capability such as [Akmatori #48 VictoriaLogs](https://github.com/akmatori/akmatori/issues/48), without creating a new batch.
