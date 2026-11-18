# Fork-local OpenSiro metadata — v0.13.0

[← Upstream](../README.md) · [Protocol](../PROTOCOL.md) · [Architecture](ARCHITECTURE.md) · [Historical migration #2](https://github.com/opensiro/upstream/issues/2)

## Human model

**One external harness = one verified working fork. One fork may contain many independent contributions.**
OpenSiro may work on it continuously, observe it without engineering, leave it dormant indefinitely, or archive it. There is **no compulsory maintenance TTL**, implied SLA or promise to sustain the third-party project. PR state (a fact owned by GitHub) and OpenSiro attention (our discretionary choice) are separate.

```text
opensiro-contributions/<target fork>   [verified parent: original owner/repo]
  └─ refs/heads/opensiro/meta          [OpenSiro-only metadata branch]
       └─ .opensiro/
            ├─ state.json             [one fork identity, attention and owner control]
            ├─ issues/                [case-level research, specs and issue drafts]
            │   └─ <case-id>/           [README, roadmap, acceptance contract]
            ├─ contributions/
            │   ├─ <stable-id>.json   [one improvement; links to code/tests/PRs]
            │   └─ ...
            └─ events/
                ├─ <unique-event-id>.json [append-only, attributable decision/checkpoint]
                └─ ...

opensiro/upstream
  └─ aggregate view, migration programme, exceptional intake before a fork exists
       └─ links + latest source SHA + first-party PR readback (NOT duplicate logs)
```

### Issue-local case worktree and two-Issue publication route

For a verified working fork, authoritative **case-specific research and plan artifacts** belong at `.opensiro/issues/<stable-case-id>/` on the **separate `opensiro/meta` worktree**. Use `README.md` for the identity, pinned refs, actual fork Issue number/URL (only when it exists), native overlap and next action; store `roadmap.md`, `constructor-acceptance.md`, draft external Issue and review receipts as needed. A plan is **not** an independently implemented improvement: never create `.opensiro/contributions/` solely for a case. `.opensiro/state.json` controls and append-only `events/` remain intact.

A *public GitHub Issue* in the working fork is a separate discussion/index object, not synonymous with a file in `.opensiro/issues/`, a fork-local PR, or an original issue. Search for duplicate fork Issues and obtain **exact current-conversation publication approval** of the target, action and full public title/body before opening it. If no such approval exists, metadata-authorized case documents may remain without a GitHub Issue. Keep the internal Issue open until there is an actual independent closure reason.

For an external original Issue, first check for an already-open equivalent original Issue/PR and **link rather than duplicate**. A fresh original Issue requires a **second independent exact publication approval**; write a maintainer-native self-contained proposal and then first-party-read back its actual URL. This is not native cross-owner Issue transfer; do not claim copied comments, numbering, reactions or ownership. Link publication in the fork's issue-local record; cross-reference from the fork Issue when separately permitted. Original GitHub owns its own state.

Upstream stores only the shared protocol, templates, validators and source-linked aggregate—not named-fork roadmap/contract documents once the writable matching fork is verified. Historical committed versions are retained in Git history as provenance. Never put case files on the fork product/default branch or original PR diff, and fail closed for PAUSE/STOP or unknown metadata rights.

**Branch boundary.** Add `.opensiro/` only on the dedicated `opensiro/meta` branch, **never** on the original project's default branch, product/feature branch or an external third-party PR diff. First verify `fork=true`, actual `parent.full_name`, default branch, meta branch HEAD, rights and relevant contributor policy. Do not rewrite the original README or its CI. Do not force-push the meta branch or merge it into a product branch. If the source already uses `.opensiro/` or a branch collision exists, stop and resolve explicitly before writing.

## Materialize on demand during an authorized Upgrade

A verified matching fork can exist **without** `opensiro/meta`; the [full-cycle Upgrade protocol](../PROTOCOL.md#upgrade-metadata-materialization--missing-opensirometa) now treats this as a **provisioning step**, not an automatic reason to abandon an otherwise qualified opportunity. A chat-only `batch N` does not initialize metadata.

1. Confirm original `OWNER/REPO`, source SHA, the `opensiro-contributions` fork's `fork=true` and exact `parent.full_name`, and first-party license/contributor rights. Verify actual fork-write authority and any prior human `PAUSE/STOP` decision. A missing metadata ref is *not* proof of `ALLOW`; a 403/429/unknown ref is **not** a confirmed missing branch.
2. If the metadata ref is definitely absent and creation is authorized, create **only** `refs/heads/opensiro/meta` from a pinned existing fork default HEAD (never rewrite the default branch). Commit `.opensiro/state.json` and one `.opensiro/contributions/<stable-id>.json` describing the real source-pinned intervention, and an append-only event only where a genuine attributable checkpoint/decision exists. Initialize `PAUSE/DORMANT` unless `ALLOW/ACTIVE` is supported by a real current owner grant; never infer permissions or fabricate events. A PAUSE bootstrap does not grant RESUME.
3. If metadata already exists or another actor concurrently creates it, **read and reconcile** with its actual HEAD and existing stable IDs; never force-push, reset controls or replace another intervention's evidence. Separate original/replacement PR URLs may belong to one contribution.
4. Independently read back the new ref plus `state.json` and contribution at the exact meta commit, then check the fork-specific [read-only aggregate](../scripts/aggregate.py) and any already published original PR's live status. A failed scan or missing record remains `UNKNOWN`, not zero/success. The branch/record must exist and be verified before reporting a full-cycle Upgrade as approval-ready.

Keep all of this `.opensiro/` data **off** default/product/external PR branches. A previously published PR with missing metadata is handled by source-linked **reconciliation**, never by opening a duplicate PR or attributing the metadata creation date as the original implementation date. This procedure does not override third-party publication consent or fork PAUSE/STOP.

## Fork-local record contract (state/events v1; new contributions v2)

Three JSON objects below specify the planned fork-local storage contract; they are **examples, not receipts for files already written**. A strict validator and live exporter remain tracked implementation work in [migration #2](https://github.com/opensiro/upstream/issues/2). Do not claim that non-existent metadata is live.

### `.opensiro/state.json` — fork and attention

```json
{
  "schema_version": 1,
  "original_repository": "original-owner/harness",
  "working_fork": "opensiro-contributions/harness",
  "attention": "WATCHING",
  "owner_control": "PAUSE",
  "last_event_id": "2026-11-15T170000Z--event-001",
  "updated_at": "2026-11-15T17:00:00Z"
}
```

**Attention** is an OpenSiro choice: `ACTIVE` (engineering permitted inside other authority limits), `WATCHING` (observe relevant external PRs; no implied code work), `DORMANT` (no scheduled observation/engineering) or `ARCHIVED` (historical record retained; explicit reactivation required). Transitions are reversible and must have attributed events. These are **not PR states**, VSM autonomy grades, source project statuses or GitHub labels. A maintainer's external PR may remain open in any attention mode.

**Owner control**: `ALLOW`, `PAUSE`, or `STOP`. `STOP` prevents **new** locally orchestrated work until an explicit attributable owner `RESUME` event; `PAUSE` temporarily prevents new effectful actions. An observer may report status but cannot override owner control. The executor must re-read the current meta branch, owner control, decision rights and applicable publication gate before a new effectful step. A GitHub metadata edit cannot forcibly interrupt a currently running shell process or previously sent external request. For emergency cancellation, use the actual runner/permission controls.

### `.opensiro/contributions/<stable-id>.json` — one improvement

```json
{
  "schema_version": 2,
  "id": "legacy-assessment-2026-11-09-16-dougong",
  "original_repository": "original-owner/harness",
  "legacy_sources": ["https://github.com/opensiro/upstream-old/issues/56"],
  "title": "Concrete user-visible improvement",
  "contribution_type": "GENERAL_UPSTREAM",
  "classification_rationale": "This source-native issue documents the need; no earlier Index-first prediction is established.",
  "classification_evidence": ["https://github.com/original-owner/harness/issues/1"],
  "work_state": "RESEARCH",
  "next_action": "Verify the real source-native need",
  "source_revision": null,
  "native_evidence": [],
  "work_branches": [],
  "external_prs": [],
  "last_event_id": "2026-11-15T170000Z--event-001"
}
```


#### Mandatory contribution origin (new records, schema v2)

Every newly created or materially reclassified `.opensiro/contributions/<id>.json` MUST set `schema_version: 2`, `contribution_type`, `classification_rationale` and `classification_evidence`; run `python3 scripts/contribution_classification.py <file>` from the current Upstream repository BEFORE committing to `opensiro/meta`. The classification is about **how the improvement was discovered**, not whether it is a feature, repair, merged PR or deployed benefit. Use exactly one of the protocol's existing categories:

| Type | Evidence gate |
| --- | --- |
| `ASSESSMENT_DERIVED` | An earlier, dated **immutable Index assessment pin** plus an independently dated, pinned pre-implementation hypothesis/prediction receipt; chronological causal claim must be supported. Often called “VSM-derived” informally, but that is **not a second canonical enum**. |
| `ASSESSMENT_INFORMED` | An exact pinned Index assessment, assessed source SHA and review date, used as context; no claim of an independent prior prediction. |
| `GENERAL_UPSTREAM` | Original-repository issue/PR and concrete source-native need; an assessment may be linked as context but causal derivation is **not** asserted. |
| `INSUFFICIENT` | Explicit explanation of unavailable provenance; no invented Index-first chronology or automatic upgrade to a stronger type. |

For assessment-related types include `assessment_pin: {"url": "<immutable Index blob URL>", "reviewed_at": "YYYY-MM-DD", "assessed_source_revision": "<40-hex SHA>"}`; `ASSESSMENT_DERIVED` additionally requires a pinned `prior_prediction_url`, `prior_prediction_date` and `implementation_started_at` (prediction strictly earlier). The validator checks structure; **an operator must still review first-party chronology and meaning**. Do not claim that passing structural validation independently proves causation.

**Legacy compatibility:** the historical imported `schema_version: 1` records may lack classification. Aggregators **must show** `UNCLASSIFIED_LEGACY` and a count; this label is a read-only reporting sentinel, **not an allowed choice for new writes**. Do not silently assign `ASSESSMENT_DERIVED` or `GENERAL_UPSTREAM` to unreviewed legacy evidence. Reclassification requires actual source review, a schema v2 update and an append-only correction event. Existing v1 records must not prevent unrelated read-only aggregation or dashboard updates. No retroactive claim that all historical records were classified.

`id` is stable and namespace-safe across frozen batches, historical registry and original/replacement PRs. Do not make one contribution per PR, or one per work session. A contribution can have zero, one or many external PR URLs, including replacements; original and replacement remain one intervention. `work_state` is OpenSiro workflow (e.g. `RESEARCH`, `BUILD`, `READY`, `DELIVERED`, `MAINTENANCE`, `CLOSED_NO_CHANGE`, `CLOSED`, `BLOCKED`), **not** automatic adoption or usefulness. Keep original Index/assessment pins, provenance and precise technical evidence as links to their actual owning sources. The illustrative identifier and source URL above do not attest that those records have migrated.

**Optional source issue watch:** an existing contribution may add the validated `issue_watch` descriptor, anchored to an original issue and an original comment with a source-backed cursor. See [Issue watching](ISSUE_WATCHING.md). Watch observations and decision signals remain separate from `external_prs` and all outcome counts. A new confirmed change adds an attributed append-only event and advances the watch baseline using non-force CAS only when fork owner control permits; no watch automatically posts an external PR.

### `.opensiro/events/<unique-event-id>.json` — immutable transaction

```json
{
  "schema_version": 1,
  "id": "2026-11-15T170000Z--event-001",
  "recorded_at": "2026-11-15T17:00:00Z",
  "actor": "human-or-agent-identity",
  "kind": "DECISION",
  "contribution_id": "legacy-assessment-2026-11-09-16-dougong",
  "decision": "PAUSE",
  "evidence_urls": [],
  "next_action": "Wait for owner RESUME"
}
```

Events capture **significant** state changes, research conclusions, native test receipts, external PR readback, owner intervention and recovery, not every shell command or repetitive hourly poll. Unique filenames, immutable content, stable IDs, actor, timestamp, source links and non-overwriting commits enable audit and independent continuation. Previous events must not be edited or deleted; a mistake is corrected by a new event referencing the original. Never fabricate unavailable history. Never store secrets, private messages, unbounded logs, third-party unlicensed content or model chain-of-thought.

### Stable case filenames

Current case files use `issue.md`, `constructor-sufficiency.md`, `roadmap.md` and `README.md` without a `-v2` or `-vN` suffix. Update links and remove stale current names when owner control permits the scoped write; record revisions with Git and attributed events, not duplicated version files. Historical comparison artifacts and contribution `schema_version: 2` are unchanged.

### Required readback for explicitly retained research cases

A named roadmap marked by the operator for recording (`зафиксируй`, `в .opensiro`, `persist`) is **not complete as a persisted case** unless the matching fork identity and exact `opensiro/meta` commit have been read back, the case README links to a Human document and a distinct AI/developer contract with reciprocal links, and the source-pinned `roadmap.md` receipt has passed the Upstream structural validator. Check license, effective fork/meta creation rights, current owner PAUSE/STOP and collisions first. A missing fork may be provisioned **only under effective separate authorization**; initialize restrictive owner control unless a genuine owner ALLOW exists. Otherwise retain the research answer but mark `PERSISTENCE_BLOCKED` or `NOT_PERSISTED` and do not claim that a downloadable package or invented fork URL satisfies the request. A plan-only case never creates a `contributions/` record; external/public GitHub Issues, comments and PRs have independent exact consent gates.

## Plan-only capability roadmaps are not new contribution records

[Architecture-first `upstream roadmap OWNER/REPO`](CAPABILITY_ROADMAP.md) may link an accepted historical assessment, original issues/PRs and existing independent fork-local contributions. A **research-only architecture plan** or external issue draft is *not* itself a qualifying improvement and does **not** require a new `.opensiro/contributions/<stable-id>.json` record. If its durable storage is requested and current fork meta rights allow, persist it as `.opensiro/issues/<case-id>/` on the matched fork, not in Upstream. Do not add a new roadmap-state enum, ledger, or owner-control override. If actual native code is later authorized and independently qualified, reuse the existing schema-v2 **one improvement / one record** procedure on `opensiro/meta` and current source-linked provenance. No plan may silently promote `INSUFFICIENT` to `ASSESSMENT_DERIVED` or claim an external PR has merged based on the plan.

## One human-visible case, two independent facts

| Question | Truth owner | Example |
| --- | --- | --- |
| Do we currently want to work on or watch this harness? | `state.json` in verified fork meta branch | `WATCHING` |
| What did OpenSiro decide or change? | Append-only `.opensiro/events/` | Owner `PAUSE`, native tests confirmed |
| Which improvement and next step? | `.opensiro/contributions/<id>.json` | `MAINTENANCE`, check review |
| Is the external PR open/merged/closed? | **Original GitHub repository**, observed live | `OPEN` at known readback UTC |
| What is the overall portfolio status? | **Derived Upstream view**, not another writable record | Counts by observed PR state and freshness |
| Who selects current organization-wide work? | Existing [Organization TODO.md](https://github.com/opensiro/vsm-oss-organization/blob/main/TODO.md) | Links to tasks/owners |

## Before a verified fork exists

Keep a **minimal research/intake issue** or dated pointer in Upstream with original source identity, critical decision and exact old evidence links; never invent `.opensiro/`, a fork or tests. A source-proven no-change may end without creating a fork. When a working fork becomes verified and metadata is materialized, its fork-local record owns the detailed operational history; the Upstream issue may remain a lightweight link/control entry, but must **not** be a duplicate mutable ledger.

## Aggregation and migration

The prospective Upstream observer reads fork `opensiro/meta` at an exact commit SHA and reads exact third-party PR URLs from first-party GitHub. It emits a **rebuildable, source-dated projection** (fork, attention, contribution IDs, external PR status, freshness, next action); source links and checkpoint SHA are sufficient for drill-down. Failed API requests, missing forks, malformed metadata, stale snapshots or unknown PRs yield **UNKNOWN / UNAVAILABLE** and do not silently become zeros or success.

Migration [#2](https://github.com/opensiro/upstream/issues/2) defines reviewed inventory, per-fork worker sharding, deduplication, staged completion counters and original immutable provenance. Parallel workers can modify **different forks**; only one writer at a time may update a single fork's metadata branch, with head-SHA lease/check and conflict recovery. A migration worker's claim expiry is concurrency control, **not maintenance TTL**.

### Boundaries

- `opensiro/upstream-old` keeps frozen original issues, evidence and historical source revisions; it is not rewritten or automatically promoted.
- `opensiro/vsm-oss-organization` keeps S2–S5, global task selection and metrics authority; fork metadata creates no independent VSM or delegated right.
- Exact third-party public issue/comment/PR/review and public fork-local proposals still require the [current per-action approval gate](../PROTOCOL.md#external-publication-consent).
- Current Organization `verified_external_outcomes` definition remains **unclaimed for the new source** until an explicitly reviewed evidence/semantics update. PR statuses are descriptive telemetry, not verified product value.
