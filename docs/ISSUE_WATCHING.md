# Source-linked external issue decision watches

[Upstream](../README.md) · [Fork metadata](FORK_METADATA.md) · [issue #22](https://github.com/opensiro/upstream/issues/22)

An external issue watch is **one optional field on an existing stable contribution record** in the verified `opensiro-contributions/<fork>@opensiro/meta` branch. The original issue, its labels, comments and closed state are GitHub source facts. The fork-local cursor is the ONLY durable alert/dedup state. It is not an external PR, an acceptance claim, a general assessment, or permission to publish anything.

## Contract

`.opensiro/contributions/<stable-id>.json` may include `issue_watch` without changing the contribution `work_state` or whole-fork `attention`. Existing legacy schema v1 records and schema v2 classified records remain supported.

```json
{
  "schema_version": 1,
  "issue_url": "https://github.com/openclaw/openclaw/issues/147509",
  "anchor_comment_url": "https://github.com/openclaw/openclaw/issues/147509#issuecomment-6919296247",
  "expected_decisions": [
    "Does the maintainer admit a fallback-specific thinking default?",
    "May a new implementation PR be submitted?"
  ],
  "relevant_labels": [
    "clawsweeper:no-new-fix-pr",
    "clawsweeper:needs-maintainer-review",
    "clawsweeper:needs-product-decision"
  ],
  "baseline": {
    "state": "open",
    "labels": ["<verified sorted unique original labels>"],
    "last_comment_id": 6919296247,
    "observed_at": "<first-party UTC readback timestamp>"
  },
  "last_alert_fingerprint": null
}
```

**Registration rule:** read the original issue and the exact anchor comment from first-party GitHub, and **only then** write the truthful baseline. Do not set a cursor from chat memory, nor represent the initial registration as a new maintainer decision. The metadata write must preserve fork attention, owner control, other contribution records and earlier immutable events. Check original source identity, exact fork parent and branch head first.

`scripts/issue_watch.py` validates the exact issue and anchored comment, full bounded comment pagination, source-author role, relevant labels, and source state. Outcomes:

- `UNCHANGED` — no verified material change, including non-relevant bot and label activity.
- `NEW_ACTIVITY_NEEDS_REVIEW` — new human comment, selected label change or issue state transition; **not** automatic approval.
- `DECISION_CONFIRMED` — a new explicit yes/no phrase from a GitHub OWNER/MEMBER/COLLABORATOR. Treat the quoted comment as a signal for **human verification**, never an external-publication authorization.
- `UNKNOWN` — unavailable/partial/invalid API readback; no success/zero/outcome claim, no cursor update.

Significant observations produce explicit original issue/comment permalinks. `--apply --allow-fork-write` records a unique immutable attribution event, advances the baseline and stable contribution `next_action/last_event_id` and fork `state.last_event_id`, and updates `opensiro/meta` only with a **non-force fast-forward** from the just-read source commit. A competing metadata update causes a Git 422/non-fast-forward and must be re-read, not overwritten or retried with force. An `ALLOW` owner control and `ACTIVE/WATCHING` attention are required for the optional metadata write; PAUSE/STOP/DORMANT/ARCHIVED can still be observed read-only. No events are written on `UNCHANGED` or `UNKNOWN`.

## On-demand execution

```bash
# Read-only preview for one existing fork-local watch
python3 scripts/issue_watch.py \
  --fork opensiro-contributions/openclaw \
  --contribution openclaw-fallback-model-thinking-defaults

# Bounded multi-fork scan from the existing read-only Upstream aggregator
python3 scripts/aggregate.py --no-prs --format json > portfolio.json
python3 scripts/issue_watch_batch.py --portfolio portfolio.json --output watch-results.json

# Explicit owner-authorized fork-meta commit only, never a third-party request:
GH_TOKEN="<fork-scoped-token>" python3 scripts/issue_watch.py \
  --fork opensiro-contributions/openclaw \
  --contribution openclaw-fallback-model-thinking-defaults \
  --apply --allow-fork-write --output watch-results.json
```

The `--apply` switch does not grant new permissions; it requires an independently supplied token with appropriate `opensiro-contributions` fork contents access, validated fork-local owner rights and current approval. It is *never* a new PR/post/comment/review feature. Read-only scans may show `preview_only`; this is **not** a delivered, deduplicated notification.

## Optional GitHub Actions cadence

[`observe-issues.yml`](../.github/workflows/observe-issues.yml) offers `workflow_dispatch` for read-only preview. A six-hour schedule is **dormant by default**, gated by repository Actions variable `UPSTREAM_ISSUE_WATCH_ENABLED=true`. When enabled, to persist and deduplicate actual alerts across executions, supply secret `OPENSIRO_FORK_WATCH_TOKEN` scoped **only** to verified target forks' repository contents (plus public issue read access). Upstream's normal `GITHUB_TOKEN` is scoped to Upstream and must not be silently treated as cross-organization fork-write authorization.

A scheduled or manually requested write refuses missing switch/secret, partial portfolio coverage and unavailable source facts. The workflow writes source-linked observation receipts to Actions logs, run summary and 30-day artifacts, and prints a notice **only after** a verified fork-local event commit. Readers may inspect/watch these results; GitHub Actions summary is not a direct ChatGPT push notification or a promise of delivery to a person.

**No auto-PR:** an issue/comment/label/closure or product opinion never authorizes creating an external PR, editing an existing PR, posting an issue comment or changing the original project. Any outward publication retains exact current-conversation approval, source CLA/DCO and maintained project policies. `issue_watch` is separate from the PR counter and `verified_external_outcomes`.

## First registration

The existing [OpenClaw fork-local contribution](https://github.com/opensiro-contributions/openclaw/blob/opensiro/meta/.opensiro/contributions/openclaw-fallback-model-thinking-defaults.json) retains `BUILD` and whole-fork `ACTIVE`; its original [issue #147509](https://github.com/openclaw/openclaw/issues/147509) and [authorized request comment](https://github.com/openclaw/openclaw/issues/147509#issuecomment-6919296247) are the sole tracked sources. The [fork-local review PR #1](https://github.com/opensiro-contributions/openclaw/pull/1) is NOT an external original-repo PR. This watched intervention is classified `GENERAL_UPSTREAM`, with Index provenance merely contextual.
