# Batch 40 — Akmatori #79 capability-first native comparison (Upstream Protocol v0.9.0)

**Executed:** 2026-11-14 UTC. **Owner:** [Upstream #56](https://github.com/opensiro/upstream/issues/56), **existing** [batch-40 research PR #303](https://github.com/opensiro/upstream/pull/303). This is **prospective v0.9.0 capability-first continuation**, **not** rewriting the historical v0.8.0 batch-40 reports or frozen batch-39 artifact. Same ten-source `EXPLICIT_REVISIT` cohort, with Akmatori as the prioritized already-selected source.

**Authority / attribution:** the need is a first-party [Akmatori #79 user request](https://github.com/akmatori/akmatori/issues/79). The origin is **SOURCE_FIRST / GENERAL_UPSTREAM or ASSESSMENT_INFORMED**, not strict `ASSESSMENT_DERIVED`; no Index-first prediction for this product behavior was frozen before inspecting the issue. VSM labels below are an *architectural interpretation*, not independent causal evidence, permission, Index reassessment or proven S3/S4 autonomy.

## Up-front capability contract (v0.9.0)

| Question | Specific answer |
| --- | --- |
| **Operator and new task** | A team announces “please review and merge this PR, tested in staging” in a configured Slack change channel. An opt-in agent should **prepare an independent pre-merge risk / blast-radius / missing-tests / rollback review** without polling or a direct @mention |
| **Trigger → action → observable output** | A single `slack_listener` event classified `change` → **only** when the channel explicitly has `on_change=run` and passes bounds, create an independently scoped **request run**, retain `event_uuid`, point to the original Slack thread → eventual review result in that thread; **no incident**, and **not permission to merge** |
| **Existing alternative** | The original Slack listener correctly records `change` for later retrieval and starts **zero** agent runs. A human can explicitly @mention Akmatori in a separate request flow or a cron integration can poll. Neither is opt-in change-triggered automatic review |
| **User-backed need** | Maintained in first-party [issue #79](https://github.com/akmatori/akmatori/issues/79); no invented production outcome or guaranteed maintainer acceptance |
| **Bounded native value proxy** | On identical synthetic Slack `change` input: baseline **0** request-run rows vs opt-in research adapter **1**. Maintain **1** classified and stored event, **1** classifier call, **0** incidents. The completed **fixture** answer must be retrievable via original `lookupSlackThread` |
| **Negative controls** | Default `store`; `info` class; disabled/non-listening/non-postable channel; no filter match; invalid regex; unapproved skill; serial replay — none may add an unintended request run |
| **VSM map / owner** | S1 is the bounded Slack work trigger and operator-requested user task; S2 preserves event-to-agent scope coordination; S3 includes operator policy / tool-rights gates; S3* would require independently auditable provenance / result. None of these are new VSM-grade admissions or S5 decision transfers |
| **Outstanding decisions** | Maintainer approval of per-channel schema/API/UI, default behavior, exact source-message security and runtime provenance, optional skill availability, transactional `EventUUID` admission and retry semantics, actual worker dispatch and thread reply |

## Source and executed native procedure

- Frozen cohort source: [`akmatori@be62d926fe6d92dceb5cf12e9a95cb587433cdf1`](https://github.com/akmatori/akmatori/tree/be62d926fe6d92dceb5cf12e9a95cb587433cdf1).
- Separately rechecked source: [`akmatori/main@7afba4fb5919f30233fc859be3626bcfdaedbdb7`](https://github.com/akmatori/akmatori/tree/7afba4fb5919f30233fc859be3626bcfdaedbdb7). This is the **observed live main pin**, not silently substituted for the original freeze.
- [Original source-native negative controls](repro/2026-11-14-upgrade40-akmatori-change-listener_test.go) had already established `change → 1 event, 0 runs, 0 incidents` and that naively calling `processMessage` for an already classified listener message creates **a second classification and event, still no run**.
- **New [research-only source-native Go test](repro/2026-11-14-upgrade40-akmatori-onchange-capability_test.go)** is copied into each disposable checkout's `internal/handlers/` test package. It invokes the **actual original `SlackHandler.handleAlertChannelMessage`** using an offline mock Slack HTTP API and controlled one-shot classifier; its new, **test-only** candidate adapter uses original `database.BeginAgentRun`, `database.Event`, `database.FinishAgentRun` and `lookupSlackThread`.
- The adapter is **NOT integrated into Akmatori's original Slack listener, settings, frontend, worker, or channel table**. It does not send a real Slack answer or execute a real LLM reviewer. The fixture finish result is *injected deterministic research output*, not a generated quality assessment. Each checkout preserves original source bytes; no third-party patch or PR was created.
- [Machine-readable native receipt](evidence/2026-11-14-upgrade40-akmatori-onchange-capability-native.json) includes the exact test source SHA-256, both source SHAs, four original Go executions and limitations. **Both pins passed all nine scenarios once with verbose output and again ten times.** On observed current main, the same nine-subcase fixture additionally **PASSed Go `-race`**; the exact command/output is in the machine receipt. This checks only in-process races during these source-native fixtures, not cross-process exactly-once semantics. The first exploratory version accidentally included literal backticks in the regex filter and failed the positive test; the fixture typo was corrected before the repeated passed results. The initial failure did not establish any defect in Akmatori.

### Matched before/after result

| Native observable | Original `store` | Proposed research `run` |
| --- | ---: | ---: |
| First-party Slack listener events stored | **1** | **1** |
| One-shot classifier calls | **1** | **1** |
| AgentRun entries in first-party native DB | **0** | **1** |
| Incidents created | **0** | **0** |
| Original Slack thread lookup resolves request scope | Not applicable (no run) | **PASS** |
| After simulated `FinishAgentRun`, thread lookup returns saved fixture answer | Not applicable | **PASS** |
| Re-enter candidate adapter sequentially with original event UUID | — | **No second run** |

**Nine controlled subcases:** `default_store_compatibility`, `explicit_opt_in_run`, `info_remains_store_only`, `disabled_channel`, `non_listening_channel`, `cannot_reply_to_thread`, `filter_miss`, `invalid_filter_fails_closed`, `unsupported_skill_fails_closed`. Every one was checked on both source pins. A target PR must preserve the original `alert` → incident route separately; this research does **not** claim it tested every alert branch, production channel loader, the real agent worker, user response delivery or cross-process replay.

The positive test passes only a constrained `incident-manager` root skill and does not enable a free-form unreviewed skill name or automatic git merge. The source Channel schema presently lacks `on_change`, and the test-only mode and guard variables are *not production policy implementation*. In particular, the existing `agent_runs.event_uuid` index is not a uniqueness admission policy: **sequential** replay prevention in this adapter is not an atomic or crash-safe inter-process guarantee.

## v0.9.0 admission gate and stop boundary

| Gate | Result | Unresolved for implementation / product benefit |
| --- | --- | --- |
| `need` | **PASS** — independent first-party user task and explicit `on_change` request in #79 | Maintainer has not approved the specific design in this research |
| `mechanism` | **PASS**, bounded source-native research adapter shows event→run→thread provenance can reuse shipped native primitives | Does not prove complete worker dispatch or UI/migration behavior |
| `counterfactual` | **PASS for native DB capability proxy** — original 0 runs → test-only opt-in 1, negative controls | **PENDING** actual before/after agent task/Slack reply and independent runner attestation |
| `scope` | **PENDING** — settings/data migration, channel permission source, skill allowlist, atomic once-only event→run handoff, worker & thread reply | Requires owner design and verified normal CI before any third-party product PR |
| Overall | **`OPPORTUNITY_RESEARCH_PENDING / NO_ADMITTED_PATCH`** | Four full PASS, original maintainer-compatible contract and independent product workflow test are still missing |

**Next smallest decisive test:** obtain/confirm first-party design decisions for the minimal `Channel.on_change` setting (default `store`, explicit `run`, optional skill and URL filter) and connect it to the preclassified `EventUUID → request scope → real agent worker → original Slack thread reply` route in a **disposable** source-native prototype. Compare baseline and candidate with the same deterministic event; assert no added incident, no extra classification, no unauthorized action, no duplicate delivery and correct available review output. Use an independent scripted runner for strict research-validation claims. A reviewable external Akmatori PR is permitted only after the owning Upstream fit and external policy gates pass; do not silently publish from this research.

**Status:** new narrowly evidenced **`MINOR_FEATURE` candidate**, not `BUG_FIX`, not strict assessment-derived, not implementation-delivered, no real production review quality or autonomy gain measured. Historical batch 39 and earlier v0.8.0 batch-40 receipts remain unchanged.
