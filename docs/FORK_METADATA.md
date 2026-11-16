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

**Branch boundary.** Add `.opensiro/` only on the dedicated `opensiro/meta` branch, **never** on the original project's default branch, product/feature branch or an external third-party PR diff. First verify `fork=true`, actual `parent.full_name`, default branch, meta branch HEAD, rights and relevant contributor policy. Do not rewrite the original README or its CI. Do not force-push the meta branch or merge it into a product branch. If the source already uses `.opensiro/` or a branch collision exists, stop and resolve explicitly before writing.

## Materialize on demand during an authorized Upgrade

A verified matching fork can exist **without** `opensiro/meta`; the [full-cycle Upgrade protocol](../PROTOCOL.md#upgrade-metadata-materialization--missing-opensirometa) now treats this as a **provisioning step**, not an automatic reason to abandon an otherwise qualified opportunity. A chat-only `batch N` does not initialize metadata.

1. Confirm original `OWNER/REPO`, source SHA, the `opensiro-contributions` fork's `fork=true` and exact `parent.full_name`, and first-party license/contributor rights. Verify actual fork-write authority and any prior human `PAUSE/STOP` decision. A missing metadata ref is *not* proof of `ALLOW`; a 403/429/unknown ref is **not** a confirmed missing branch.
2. If the metadata ref is definitely absent and creation is authorized, create **only** `refs/heads/opensiro/meta` from a pinned existing fork default HEAD (never rewrite the default branch). Commit `.opensiro/state.json` and one `.opensiro/contributions/<stable-id>.json` describing the real source-pinned intervention, and an append-only event only where a genuine attributable checkpoint/decision exists. Initialize `PAUSE/DORMANT` unless `ALLOW/ACTIVE` is supported by a real current owner grant; never infer permissions or fabricate events. A PAUSE bootstrap does not grant RESUME.
3. If metadata already exists or another actor concurrently creates it, **read and reconcile** with its actual HEAD and existing stable IDs; never force-push, reset controls or replace another intervention's evidence. Separate original/replacement PR URLs may belong to one contribution.
4. Independently read back the new ref plus `state.json` and contribution at the exact meta commit, then check the fork-specific [read-only aggregate](../scripts/aggregate.py) and any already published original PR's live status. A failed scan or missing record remains `UNKNOWN`, not zero/success. The branch/record must exist and be verified before reporting a full-cycle Upgrade as approval-ready.

Keep all of this `.opensiro/` data **off** default/product/external PR branches. A previously published PR with missing metadata is handled by source-linked **reconciliation**, never by opening a duplicate PR or attributing the metadata creation date as the original implementation date. This procedure does not override third-party publication consent or fork PAUSE/STOP.

## Minimal proposed v1 contract

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
  "schema_version": 1,
  "id": "legacy-assessment-2026-11-09-16-dougong",
  "original_repository": "original-owner/harness",
  "legacy_sources": ["https://github.com/opensiro/upstream-old/issues/56"],
  "title": "Concrete user-visible improvement",
  "work_state": "RESEARCH",
  "next_action": "Verify the real source-native need",
  "source_revision": null,
  "native_evidence": [],
  "work_branches": [],
  "external_prs": [],
  "last_event_id": "2026-11-15T170000Z--event-001"
}
```

`id` is stable and namespace-safe across frozen batches, historical registry and original/replacement PRs. Do not make one contribution per PR, or one per work session. A contribution can have zero, one or many external PR URLs, including replacements; original and replacement remain one intervention. `work_state` is OpenSiro workflow (e.g. `RESEARCH`, `BUILD`, `READY`, `DELIVERED`, `MAINTENANCE`, `CLOSED_NO_CHANGE`, `CLOSED`, `BLOCKED`), **not** automatic adoption or usefulness. Keep original Index/assessment pins, provenance and precise technical evidence as links to their actual owning sources. The illustrative identifier and source URL above do not attest that those records have migrated.

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
