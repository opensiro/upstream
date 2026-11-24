# Roadmap publication history and loop guard

[Upstream](../README.md) · [Pilot #93](https://github.com/opensiro/upstream/issues/93) · [Implementation issue #109](https://github.com/opensiro/upstream/issues/109)

Before proposing another public Roadmap Issue, use the **read-only** publication-history view to identify prior OpenSiro outward actions and related native issues. This is an **additional preflight**, not publication permission, a second ledger, a replacement for source-native semantic review, or a claim of exhaustive historical coverage.

## Source of truth

- `opensiro-contributions/<fork>@opensiro/meta` stores stable issue case IDs, append-only `.opensiro/events/`, `publication-receipt.md` and dated case evidence. Preserve draft-only states and conflicting historical checkpoints without converting them into publications.
- The original GitHub repository owns Issue, Discussion, PR, author and response facts. Current provider readback supersedes a previously observed state; a bot reply never establishes human-maintainer acceptance.
- `opensiro/upstream` exposes only a **projection**, with source URLs and coverage. The archive projection pins the current `upstream-old` HEAD and reads explicit publication fields in the historical casebook, `registry.yaml`, `data/upstream-lifecycle.json` and `data/pr-maintenance/targets.json`. Provider readback decides authorship and current state. Unmatched archived actions remain distinct from canonical Roadmap cases; replacement PRs by other authors are not credited to OpenSiro. Other historical trees, publishers and unlinked publications may remain unindexed: `historical_inventory_complete=false` is intentional.

## CLI

For a read-only organization inventory, use `python3 scripts/publication_history.py --format json`. For any candidate, use the procedure below. The CLI never posts and the bounded archive remains incomplete.


## Mandatory persisted Roadmap gate

The history scan is deliberately a two-step workflow. Discovery and local draft checks do not make a proposal ready for the owner.

1. Run a scoped candidate discovery with the exact proposed title (for comments, use the existing Issue title/search subject), candidate kind and concrete delta. For an existing Issue comment use candidate kind original_issue_comment and the exact --candidate-destination https://github.com/OWNER/REPO/issues/N. No --case-ref or body is required for discovery. The report provides review_evidence_sha256 and review_context; ROADMAP_NOT_READY_FOR_EXTERNAL_PROPOSAL is expected until the case is persisted. Nonzero exit is not a failure to perform research. Review all material matches, full original evidence and actual maintainer feedback; do not manufacture novelty from keywords. A candidate subject/title change requires another scan.
2. Reconcile the actual original/native evidence in the existing roadmap.md. Keep the historical receipt's original research pin separate from the current publication review source pin; update the canonical decision and Human/AI where the findings change them. In the existing case, maintain exactly one current set of the following fields (preserve older values via Git history/events rather than ambiguous duplicate fields):

```markdown
- Publication review source HEAD: <current original default branch SHA>
- Publication review action: original_issue
- Publication review destination: https://github.com/OWNER/REPO
- Publication review title SHA256: <SHA256 of exact UTF-8 title without trailing newline>
- Publication review history SHA256: <review_evidence_sha256 from discovery>
- Publication review resolution: NEW_DISTINCT_OUTCOME
- Publication review rationale: <source-linked conclusion about prior work, feedback, native alternatives and concrete user-visible delta>
```

For original_issue_comment, use REUSE_EXISTING, the exact existing Issue URL, and hash the search subject (not a new outward title). For fork_issue, destination is the verified fork URL; for original_discussion, destination is the original repository and the native category/rules still require separate first-party verification. NEW_DISTINCT_OUTCOME does not certify actual novelty. The rationale and the substantive evidence/overlap analysis must be current and truthful, not a placeholder or a claim of review based only on the digest. If the same outcome is already covered, stop or use a useful, separately approved comment, not NEW_DISTINCT_OUTCOME. If no useful action is justified, record the conclusion and stop; no gate PASS is needed.
3. Run both case validators, commit the complete case on opensiro/meta, read back that exact commit and re-run both. Then derive the exact native-facing body and persist it in the same case: original-issue-draft.md, original-discussion-draft.md, or maintainer-comment-draft.md (body bytes only, without private approval instructions). A fork Issue is deterministic from the canonical Human issue.md; render its immutable links at the final metadata commit using --render-fork --draft-only, after canonical persistence. Local issue payload checks use --draft-only; the distinct LOCAL_DRAFT_PAYLOAD_PASS_NOT_APPROVAL_READY result is not usable for consent. Reuse a current case/draft without a redundant commit.
4. Run the same live candidate discovery again with the exact current --case-ref and --candidate-body-file. This validates the actual fork parent, ACTIVE/ALLOW state, current fork/source refs before/after readback, both canonical validators against committed files, unique reconciliation fields/digest, and exact committed outbound bytes (or deterministic fork rendering). No mutable local worktree can substitute for that commit. Require roadmap_gate.status = ROADMAP_PERSISTED_VERIFIED for the mechanical barrier and show its immutable roadmap_url, case_ref, source_head, target_transition, proposal_decision and review rationale outside the proposed body. The scoped review digest excludes the metadata HEAD/provenance links of the commit that records the review itself; the exact approval snapshot separately binds those pins, provider evidence, draft and canonical file hashes.
5. For Issues, run validate_public_issue_payload.py in its default approval mode with --case-dir, --repo, --case-ref, --source-head, --title-file, --body-file, and --history-report pointing to this live candidate report. It independently reads back the same committed files and rejects local differences, missing/stale history, source drift and payload drift. Native Markdown templates still require the existing --native-markdown-template-file flag. Discussion/comment paths use the same history persistence barrier and their separate verified channel/rules/target/complete-text review.
6. Before any separately approved POST rerun the live candidate scan with the same --case-ref and --previous-report pointing to the exact approval-time report. Repeat payload and native template/destination checks. Changed evidence, metadata, source, target or bytes invalidates the preview. Keep the current exact consent gate.

```bash
# Discovery (no committed body/pin required; do NOT treat this as approval)
python3 scripts/publication_history.py \\
  --repo opensiro-contributions/browser-harness \\
  --candidate-original browser-use/browser-harness \\
  --candidate-case browser-resource-control-20261117 \\
  --candidate-title "$EXACT_TITLE" --candidate-kind original_issue \\
  --candidate-delta "$CONCRETE_DELTA" --format json > /tmp/roadmap-discovery.json

# After canonical persistence, draft persistence, exact committed readback:
python3 scripts/publication_history.py \\
  --repo opensiro-contributions/browser-harness \\
  --candidate-original browser-use/browser-harness \\
  --candidate-case browser-resource-control-20261117 \\
  --candidate-title "$EXACT_TITLE" --candidate-kind original_issue \\
  --candidate-delta "$CONCRETE_DELTA" --case-ref "$META_SHA" \\
  --candidate-body-file /tmp/exact-original-issue.md --format json > /tmp/approval-history.json

python3 scripts/validate_public_issue_payload.py --kind original \\
  --case-dir /path/to/verified/.opensiro/issues/browser-resource-control-20261117 \\
  --repo browser-use/browser-harness --case-ref "$META_SHA" --source-head "$ORIGINAL_SHA" \\
  --title-file /tmp/exact-title.txt --body-file /tmp/exact-original-issue.md \\
  --history-report /tmp/approval-history.json
```

The example is an interface illustration, not authorization or a new Browser Harness proposal. Read the actual candidate JSON even on nonzero exit. The new persistence barrier is independent of history novelty: POSSIBLE_OVERLAP still requires source-first semantic reconciliation, ALREADY_PUBLISHED/REUSE_EXISTING blocks repeated new Issue publication, and genuine incomplete history/first-party search blocks the persistence-ready candidate. For existing-Issue comments, Discussions and fork Issues the existing history classifier still does not certify native-channel novelty; ROADMAP_PERSISTED_VERIFIED does not change HISTORY_UNVERIFIED into NEW_PROPOSAL or authorize that action. Complete the existing channel-specific review and explicit consent separately. No validator can prove that a prose rationale is honest or that every material source was actually read. Scope limitations remain in the report, not hidden by a digest.

The view uses the existing `roadmap_view.py` verified fork discovery and canonical case IDs; it reads case receipt and append-only `publication` events as proof. A GitHub URL *merely cited in a research file* is **not** evidence OpenSiro published it. Same-case publication in the **same action channel** returns `ALREADY_PUBLISHED` even if an old README said `NOT_PUBLISHED`. A separate fork vs original Issue remains a separately approvable action but returns overlap for review. Exact older OpenSiro-authored titles returned by provider search yield `REUSE_EXISTING`; related original/cross-project references yield `POSSIBLE_OVERLAP`. Insufficient provider, history or search coverage yields `HISTORY_UNVERIFIED`.

GitHub REST GET is used for original/fork Issues, PRs, and bounded Issue comments, while an authenticated **read-only GitHub GraphQL query** is used for Discussion content and comments. A missing token, 403/404, truncated comments, changed outbound SHA, source mismatch or unsupported channel yields `UNVERIFIED`. The CLI searches native original Issues **and PRs**, both by publisher and bounded terms, and reads bounded repository Discussions through authenticated read-only GraphQL when enabled. Missing token or pagination/completeness uncertainty is recorded as `HISTORY_UNVERIFIED`. Native REST Issue/PR search reads up to 1,000 results per query in 100-item pages; every page must have a consistent reported count, complete flag, expected length and distinct, correct-channel identities. A result beyond the provider cap, page error, count drift or duplicate remains unverified; a successful bounded scan is not exhaustive global history. CLI uses the existing GH_TOKEN/GITHUB_TOKEN runtime authentication if configured; exhausted anonymous REST quota is a blocker, not grounds for bypass. Native original search does not cover every alternate audience; new non-original-Issue channels remain conservatively unverified for novelty. Independently review source-native alternatives, actual maintainer feedback and the concrete user-visible delta. Keyword matches and bounded negative searches do not establish equivalence or novelty.

## Approval packet / human review

For each candidate record: exact original and fork, stable case ID, target channel, matched publication URL and type, current readback state/author, title/body fingerprints when recorded, recent comments with bot status, event/receipt provenance, and `coverage`/warnings. Review source-native alternatives and any replies. State **what new user-visible result the proposal would add**, or link existing discussion and stop. Automated keyword comparison across different originals is only an advisory signal, not proof they have identical needs.

The existing [exact external-publication gate](../PROTOCOL.md#external-publication-consent) and [native full-payload gate](../PROTOCOL.md#exact-public-github-issue-payload-gate--fork-and-original) remain mandatory, including verified first-party template, complete owner-visible final title/body, both human attestations where required, fresh source checks, and separate current-conversation approval. This script never grants S5 delegation, publication consent, product adoption, approval to reply, or a new Index grade.

## Known limitations and further acceptance work

The projection covers verified present fork-local case/event/receipt evidence, named archive ledgers and casebook fields, and bounded original Issue/PR/Discussion discovery. It does **not** replay all historical Git trees, discover every external publication under changed authors, exhaustively enumerate unlimited Discussion histories, or infer source-native semantic equivalence. Archived unmatched rows are candidates until provider readback verifies authorship. Therefore the overall historical completeness flag stays **false** even on an error-free selected-fork scan. GitHub REST/GraphQL limitations must be reflected in `coverage`, not silently turned into zero matches.

Further changes to source-native semantic matching, historical/legacy backfill, pagination and channel-specific pre-POST search should be reviewed against [#109](https://github.com/opensiro/upstream/issues/109). Deterministic tests cover same-case repeats, distinct action channels, unrelated evidence links, named archive discovery and deduplication, historical draft/receipt precedence, source links vs publications, bot feedback, Discussion/API failures, and changes in payload/source/feedback across approval and pre-POST snapshots.
