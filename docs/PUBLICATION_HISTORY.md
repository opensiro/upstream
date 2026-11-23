# Roadmap publication history and loop guard

[Upstream](../README.md) · [Pilot #93](https://github.com/opensiro/upstream/issues/93) · [Implementation issue #109](https://github.com/opensiro/upstream/issues/109)

Before proposing another public Roadmap Issue, use the **read-only** publication-history view to identify prior OpenSiro outward actions and related native issues. This is an **additional preflight**, not publication permission, a second ledger, a replacement for source-native semantic review, or a claim of exhaustive historical coverage.

## Source of truth

- `opensiro-contributions/<fork>@opensiro/meta` stores stable issue case IDs, append-only `.opensiro/events/`, `publication-receipt.md` and dated case evidence. Preserve draft-only states and conflicting historical checkpoints without converting them into publications.
- The original GitHub repository owns Issue, Discussion, PR, author and response facts. Current provider readback supersedes a previously observed state; a bot reply never establishes human-maintainer acceptance.
- `opensiro/upstream` exposes only a **projection**, with source URLs and coverage. Older publications in `upstream-old`, outside current forks, or under another publisher may be unindexed: `historical_inventory_complete=false` is intentional.

## CLI

```bash
# Full accessible organization inventory, read-only
python3 scripts/publication_history.py --format json

# Bounded case/source check BEFORE requesting exact owner approval
python3 scripts/publication_history.py \
  --repo opensiro-contributions/browser-harness \
  --candidate-original browser-use/browser-harness \
  --candidate-case browser-resource-control-20261117 \
  --candidate-title 'Proposal: opt-in task-level browser resource admission for Browser Harness — Opensiro VSM architecture review' \
  --candidate-kind original_issue --format json

# A second outward audience from one case is different from a duplicate:
# this still demands a new exact approval and cross-channel overlap review.
python3 scripts/publication_history.py \
  --repo opensiro-contributions/opencode \
  --candidate-original anomalyco/opencode \
  --candidate-case opencode-session-collision-20261119 \
  --candidate-title 'New original issue title' \
  --candidate-kind original_issue \
  --candidate-delta 'Describe a genuinely new user-visible capability vs the published Issue.'
```

Use the same preflight again immediately **before an already separately approved POST**. No code here calls GitHub create/update endpoints or sends public messages. Nonzero exit means **blocked or unverified**, not permission to bypass; exit 0 with `NEW_PROPOSAL` is only a **bounded negative search**, never approval.

The view uses the existing `roadmap_view.py` verified fork discovery and canonical case IDs; it reads case receipt and append-only `publication` events as proof. A GitHub URL *merely cited in a research file* is **not** evidence OpenSiro published it. Same-case publication in the **same action channel** returns `ALREADY_PUBLISHED` even if an old README said `NOT_PUBLISHED`. A separate fork vs original Issue remains a separately approvable action but returns overlap for review. Exact older OpenSiro-authored titles returned by provider search yield `REUSE_EXISTING`; related original/cross-project references yield `POSSIBLE_OVERLAP`. Insufficient provider, history or search coverage yields `HISTORY_UNVERIFIED`.

GitHub REST GET is used for original/fork Issues, PRs, and bounded Issue comments, while an authenticated **read-only GitHub GraphQL query** is used for Discussion content and comments. A missing token, 403/404, truncated comments, changed outbound SHA, source mismatch or unsupported channel yields `UNVERIFIED`. Original first-party search is currently **Issue-only**; a candidate targeting a new Discussion, PR or fork Issue cannot be classified `NEW_PROPOSAL` on that Issue-only search. In all cases perform the native Discussions/PRs/code/maintainer search independently; do not treat string/keyword overlap as a full semantic assessment.

## Approval packet / human review

For each candidate record: exact original and fork, stable case ID, target channel, matched publication URL and type, current readback state/author, title/body fingerprints when recorded, recent comments with bot status, event/receipt provenance, and `coverage`/warnings. Review source-native alternatives and any replies. State **what new user-visible result the proposal would add**, or link existing discussion and stop. Automated keyword comparison across different originals is only an advisory signal, not proof they have identical needs.

The existing [exact external-publication gate](../PROTOCOL.md#external-publication-consent) and [native full-payload gate](../PROTOCOL.md#exact-public-github-issue-payload-gate--fork-and-original) remain mandatory, including verified first-party template, complete owner-visible final title/body, both human attestations where required, fresh source checks, and separate current-conversation approval. This script never grants S5 delegation, publication consent, product adoption, approval to reply, or a new Index grade.

## Known limitations and further acceptance work

The first version covers verified present fork-local case/event/receipt evidence and bounded original Issue author/content searches. It does **not** replay historical Git trees, backfill all `upstream-old` cases, discover every external publication under changed authors, or run exhaustive repository-wide semantic or Discussion searches. Therefore the overall historical completeness flag stays **false** even on an error-free selected-fork scan. GitHub REST/GraphQL limitations must be reflected in `coverage`, not silently turned into zero matches.

Further changes to source-native semantic matching, historical/legacy backfill, pagination and channel-specific pre-POST search should be reviewed against [#109](https://github.com/opensiro/upstream/issues/109). Deterministic tests cover same-case repeats, different audiences, historical draft/receipt precedence, source links vs publications, bot feedback, Discussion/API failures, and changed payload hashes.
