# Roadmap publication history and loop guard

[Upstream](../README.md) · [Pilot #93](https://github.com/opensiro/upstream/issues/93) · [Implementation issue #109](https://github.com/opensiro/upstream/issues/109)

Before proposing another public Roadmap Issue, use the **read-only** publication-history view to identify prior OpenSiro outward actions and related native issues. This is an **additional preflight**, not publication permission, a second ledger, a replacement for source-native semantic review, or a claim of exhaustive historical coverage.

## Source of truth

- `opensiro-contributions/<fork>@opensiro/meta` stores stable issue case IDs, append-only `.opensiro/events/`, `publication-receipt.md` and dated case evidence. Preserve draft-only states and conflicting historical checkpoints without converting them into publications.
- The original GitHub repository owns Issue, Discussion, PR, author and response facts. Current provider readback supersedes a previously observed state; a bot reply never establishes human-maintainer acceptance.
- `opensiro/upstream` exposes only a **projection**, with source URLs and coverage. The archive projection pins the current `upstream-old` HEAD and reads explicit publication fields in the historical casebook, `registry.yaml`, `data/upstream-lifecycle.json` and `data/pr-maintenance/targets.json`. Provider readback decides authorship and current state. Unmatched archived actions remain distinct from canonical Roadmap cases; replacement PRs by other authors are not credited to OpenSiro. Other historical trees, publishers and unlinked publications may remain unindexed: `historical_inventory_complete=false` is intentional.

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
  --candidate-kind original_issue \
  --candidate-body-file /tmp/exact-original-issue.md --format json > /tmp/approval-history.json

# A second outward audience from one case is different from a duplicate:
# this still demands a new exact approval and cross-channel overlap review.
python3 scripts/publication_history.py \
  --repo opensiro-contributions/opencode \
  --candidate-original anomalyco/opencode \
  --candidate-case opencode-session-collision-20261119 \
  --candidate-title 'New original issue title' \
  --candidate-kind original_issue \
  --candidate-delta 'Describe a genuinely new user-visible capability vs the published Issue.' \
  --candidate-body-file /tmp/exact-original-issue.md
```

Use the same preflight again immediately **before an already separately approved POST**, with the same title/body and `--previous-report /tmp/approval-history.json`. The candidate snapshot binds the original current default-branch HEAD, exact UTF-8 title/body hashes, case/metadata pins, archive scope, publication states/hashes, feedback hashes, and native search results; per-observation timestamps do not change the snapshot. `CHANGED_OR_UNVERIFIED` requires renewed review. A matching snapshot is not permission to send. `--no-archive` is diagnostic only and cannot yield a CLI `NEW_PROPOSAL` candidate. No code here calls GitHub create/update endpoints or sends public messages. Nonzero exit means **blocked or unverified**, not permission to bypass; exit 0 with `NEW_PROPOSAL` is only a **bounded negative search**, never approval.

The view uses the existing `roadmap_view.py` verified fork discovery and canonical case IDs; it reads case receipt and append-only `publication` events as proof. A GitHub URL *merely cited in a research file* is **not** evidence OpenSiro published it. Same-case publication in the **same action channel** returns `ALREADY_PUBLISHED` even if an old README said `NOT_PUBLISHED`. A separate fork vs original Issue remains a separately approvable action but returns overlap for review. Exact older OpenSiro-authored titles returned by provider search yield `REUSE_EXISTING`; related original/cross-project references yield `POSSIBLE_OVERLAP`. Insufficient provider, history or search coverage yields `HISTORY_UNVERIFIED`.

GitHub REST GET is used for original/fork Issues, PRs, and bounded Issue comments, while an authenticated **read-only GitHub GraphQL query** is used for Discussion content and comments. A missing token, 403/404, truncated comments, changed outbound SHA, source mismatch or unsupported channel yields `UNVERIFIED`. The CLI searches native original Issues **and PRs**, both by publisher and bounded terms, and reads bounded repository Discussions through authenticated read-only GraphQL when enabled. Missing token or pagination/completeness uncertainty is recorded as `HISTORY_UNVERIFIED`. Native original search does not cover every alternate audience; new non-original-Issue channels remain conservatively unverified for novelty. Independently review source-native alternatives, actual maintainer feedback and the concrete user-visible delta. Keyword matches and bounded negative searches do not establish equivalence or novelty.

## Approval packet / human review

For each candidate record: exact original and fork, stable case ID, target channel, matched publication URL and type, current readback state/author, title/body fingerprints when recorded, recent comments with bot status, event/receipt provenance, and `coverage`/warnings. Review source-native alternatives and any replies. State **what new user-visible result the proposal would add**, or link existing discussion and stop. Automated keyword comparison across different originals is only an advisory signal, not proof they have identical needs.

The existing [exact external-publication gate](../PROTOCOL.md#external-publication-consent) and [native full-payload gate](../PROTOCOL.md#exact-public-github-issue-payload-gate--fork-and-original) remain mandatory, including verified first-party template, complete owner-visible final title/body, both human attestations where required, fresh source checks, and separate current-conversation approval. This script never grants S5 delegation, publication consent, product adoption, approval to reply, or a new Index grade.

## Known limitations and further acceptance work

The projection covers verified present fork-local case/event/receipt evidence, named archive ledgers and casebook fields, and bounded original Issue/PR/Discussion discovery. It does **not** replay all historical Git trees, discover every external publication under changed authors, exhaustively enumerate unlimited Discussion histories, or infer source-native semantic equivalence. Archived unmatched rows are candidates until provider readback verifies authorship. Therefore the overall historical completeness flag stays **false** even on an error-free selected-fork scan. GitHub REST/GraphQL limitations must be reflected in `coverage`, not silently turned into zero matches.

Further changes to source-native semantic matching, historical/legacy backfill, pagination and channel-specific pre-POST search should be reviewed against [#109](https://github.com/opensiro/upstream/issues/109). Deterministic tests cover same-case repeats, distinct action channels, unrelated evidence links, named archive discovery and deduplication, historical draft/receipt precedence, source links vs publications, bot feedback, Discussion/API failures, and changes in payload/source/feedback across approval and pre-POST snapshots.
