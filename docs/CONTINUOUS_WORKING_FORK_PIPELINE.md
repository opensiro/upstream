# Continuous source → OpenSiro Contributions workspace pipeline

**Owner:** Upstream [#56](https://github.com/opensiro/upstream/issues/56),
fork executor [#28](https://github.com/opensiro/upstream/issues/28) under
[#6](https://github.com/opensiro/upstream/issues/6). **Policy decision:**
technical changes should reach the matching `opensiro-contributions` working
fork in the same contribution cycle. The owner's [standing publication decision](STANDING_EXTERNAL_PR_PUBLICATION.md)
now authorizes qualified external PR publication **without repeated per-PR human approval**.

## One source inventory, additive to the original 100

The [100-source priority snapshot](../data/fork-priorities/2026-11-08.json)
is preserved unchanged. [`scripts/contribution_workspaces.py`](../scripts/contribution_workspaces.py)
builds the current working inventory from that snapshot **plus every integrated
frozen `data/assessment-candidate-batches/*.json` case**, earlier standalone
[native pilots](../data/contribution-workspaces/pilot-sources.json), and
the historical [casebook/registry PR lifecycle sources](../data/upstream-lifecycle.json).
A source that was worked on but excluded from the initial 100 remains included;
negative screens and blocked hypotheses are tracked, without inventing a
defect or patch. Historical external PR sources are tracked for continuity,
not treated as new unpublished work.

The current generated [workspace registry](../data/contribution-workspaces/registry.json)
is an **intent and provenance index**, not proof of 183 actual GitHub forks.
For a one-time, human-supervised bootstrap and later collaboration from
different GitHub plugins, see the [read-only bootstrap proposal and contributor
protocol](FORK_BOOTSTRAP_AND_COLLABORATION.md) and its
[`fork-bootstrap-proposal.json`](../data/contribution-workspaces/fork-bootstrap-proposal.json).
Historical mapping is not live verification. The names of different source
repositories can collide: e.g. four distinct `*/agent-harness` sources.
For these the proposed fork name is deliberately empty until the correct
parent and an unoccupied destination have been verified. Never attach a patch
to a same-named fork without checking `parent.full_name` and push rights.

### Provider readback checkpoint (2026-11-09)

The [separate dated observation](../data/contribution-workspaces/fork-readbacks/2026-11-09.json)
records authenticated **read-only** GitHub REST GET results for the 16 already
mapped public organization forks. All 16 reported the expected
`parent.full_name`, public fork status and an actual branch SHA; among the
same-named source/fork branches, **9 matched** and **7 differed**. This
observation does **not** establish which side is ahead, whether another
working branch contains a contribution, whether source-native tests pass,
or that a new fork/patch write is authorized. It is a dated receipt only:
every write stage must independently refresh source/fork/permissions and
exact branch SHA. The generated registry links this receipt without
changing its historical-mapping fork state.

Later independently observed public forks can be added in a new dated
`fork-readbacks/YYYY-MM-DD.json` record, including forks for the sources
outside the original 100 and correctly parented forks with non-default names
that resolve collisions. This never rewrites the frozen priority pool: a new
dated mapping remains `DATED_MAPPING_REQUIRES_LIVE_READBACK`, requires a
fresh provider preflight before writes, and does not attest that a branch
contains a tested contribution.

## Single-cycle state and authority

1. **Intake:** reserve one source identity (`owner/repo`); resolve it against
   the generated inventory before selecting a new batch. Preserve the pinned
   Index and reviewed source refs, prior batches, and open competing work.
2. **Screen:** record the four native-fit gates and any prospective VSM
   hypothesis. If no independently supported improvement exists, close the
   screen; retain the source record without creating a fake change.
3. **Technical change:** keep the native patch, its tests and independent
   execution receipt in Upstream. At `AWAITING_EXTERNAL`, emit a workspace
   preparation intent pointing to the same source and patch. Reconcile
   existing third-party PRs and fork state first. Upstream's patch is an
   attributable evidence packet, **not the live candidate PR diff**; avoid
   repetitive internal PRs containing only a copy of a future PR body.
4. **Autonomous fork preparation, conditionally executable:** an eligible
   five-repository wave is covered by the revocable, time-bounded
   [standing preparation mandate](STANDING_PREPARATION_AUTONOMY.md).
   The **trusted, actor-bound execution host** verifies exact source,
   license, branch, SHA, parent, visibility, destination permissions and
   fresh current-main policy, then internally issues a one-use stage decision
   **without requesting new human approval**. Reuse the verified existing
   fork or create the exact missing public
   fork; put the validated change on an `opensiro/...` working branch and run
   allowed native CI. Read back the commit and record its attributable SHA.
   The next technical change must update that working branch under fresh
   automatic bound stage checks; no detached private side queue.
   The candidate diff lives on this **source-matched contributor fork**, not
   in an `opensiro/upstream` documentation or PR-body staging branch.
5. **Fork-local proposal and standing release gate:** create a PR inside the
   matching `opensiro-contributions/<target>` fork, from the validated
   `opensiro/...` head to the fork's source-matched default branch. Its
   exact title/body come from the checked code diff, latest target PR template,
   contributor requirements and disclosure v3. Verify that fork-local PR URL,
   unchanged head/base SHAs, final text and test receipt in the fork-local proposal.
   Under the [independent standing publication mandate](STANDING_EXTERNAL_PR_PUBLICATION.md),
   an authorized publisher may open a qualifying third-party PR **without another owner prompt**
   after verifying the exact proposal, current policies and native checks; re-read both GitHub PRs afterward.
   Neither a fork-local PR nor a batch command by itself grants publication rights.
   The external maintainer alone decides acceptance or merge.

The owner's **preparation decision is now standing**, not a repeated
human prompt. This does **not** mean every writer is live-connected: the
ChatGPT GitHub connector lacks general fork creation; the two-file CLI
stage is narrow, and existing-branch updates require safe compare-and-swap
support. A valid connected host must actually check current-main policy
and authenticated provider state. Otherwise `WAITING_FOR_TRUSTED_EXECUTOR`
is a **technical** block, **not a request for the owner to authorize
preparation again**. Do not substitute a PAT, raw CLI write, unprotected
Actions workflow, or arbitrary `approved_by` field for host enforcement.

### Dated external PR publication readbacks

When an externally authorized PR has actually been published, record
its authenticated GitHub PR identity, actor, fork and head SHA in a separately
reviewed dated readback. The [2026-11-10 publication readback](../data/external-pr-publication-readbacks/2026-11-10.json)
is the first such additive source. Register its verified PR URL in the
[explicit maintenance watchlist](../data/pr-maintenance/targets.json) in the
same change. The Verified external outcomes candidate observer includes these
publication identities to reconcile its portfolio exactly, but treats them
as **publication-only** evidence, never automatic verified adoption. This
does not mutate the historical finite Corrective or Improvement ledgers.

## Fork-local PR proposal contract

The source-specific **unpublished publication proposal** lives as a normal
Pull Request in the correctly parented public `opensiro-contributions/<target>`
fork. The fork's `opensiro/...` working branch contains **only the product code,
tests and approved source-native files**; its pull request is against the
fork's own source-matched default branch, not against the third-party original.
This is a reviewable preparation record, not a third-party submission or
a grant to merge the fork's default branch.

- Verify current target license, contributor/security policies, template,
  target default SHA, fork parent/visibility/push rights, branch/head SHA and
  non-overlapping PRs. Obtain the applicable fork/branch/proposal write authority;
  do not infer it from the existence of a fork or earlier approval.
- Reuse/update the **one fork-local PR per technical topic**. Its title/body
  reflect the target's actual PR format plus disclosure v3; link the pinned
  Index assessment, current assessment and test evidence. Do not invent
  first-party checks, author attestations, independent human review or adoption.
- Do **not** commit `PR_PROPOSAL.md`, `.opensiro/pr-body.md` or similar
  publication-only files into the branch that will be submitted externally.
  Do **not** create an Upstream docs-only PR or report to store the draft
  title/body. Existing dated Upstream proposals remain historical read-only
  records; they are never copied without current fork/source verification.
- Bind the standing-publication eligibility check to the fork-local PR URL, unchanged
  head/base SHA and **exact** title/body readback. A changed diff, target
  template or material PR prose requires refreshed validation, **not another routine owner prompt**.
  An ordinary wave command is not itself the standing grant.
- On authorized external publication, create the third-party PR from that
  exact fork branch as **Open · Ready for review** unless a real source-native
  readiness condition justifies Draft. Require a fresh GitHub readback and
  matching code/head, title and body. Record **both** PR URLs and the
  source/head SHA in the dated Upstream readback; add only the external PR
  to the maintenance watchlist and adoption observers.
- After publication, the third-party PR owns maintainer interaction and the
  live published description. The fork-local PR remains a durable
  preparation/revision trail; it may be closed **without merge** after its
  publication link is recorded, but must never be merged automatically into
  the fork default branch. External PRs are never merged by OpenSiro.

`upstream` owns selection, assessment-linked hypotheses, pinned independent
RED/GREEN receipts, stage/publication decisions, fork/external PR **links**,
external lifecycle readbacks and portfolio metrics. It does **not** own the
live contribution diff, fork-native CI or editable target PR proposal.
[Native CI placement](NATIVE_CI_EXECUTION.md) and
[publication waves](EXTERNAL_PUBLICATION_WAVES.md) apply unchanged.

## Command and CI contract

```bash
python3 scripts/contribution_workspaces.py status
python3 scripts/contribution_workspaces.py list --source talktorana/agent-harness
python3 scripts/contribution_workspaces.py sync
python3 scripts/contribution_workspaces.py check
python3 scripts/fork_bootstrap_manifest.py status
python3 scripts/fork_bootstrap_manifest.py check
```

- Run `sync` **in the same internal change** that adds/changes a batch
  manifest or material handoff reference. Do not alter historical frozen
  statuses to imply that a separate external action occurred.
- The registry also fingerprints each locally linked pilot packet's **current**
  file content. For batch handoffs with an explicit patch SHA256, it compares
  the observed bytes against the frozen claim. For other local handoffs it
  exposes one unreviewed patch candidate, several ambiguous patch candidates,
  or no local packet. Changes to the pilot's source-native evidence invalidate
  `check` until `sync` refreshes the same internal PR. A discovered patch is
  **not an approved patch selection** or a tested remote working branch.
- Standalone native pilots outside the assessment batches receive the same
  content fingerprint. Original pilot paths remain frozen under
  [the historical baseline](../pilots/HISTORICAL_BASELINE.json), while new
  experiments can be added to the catalog.
- The unfiltered repository-integrity workflow runs `check` on all PRs and
  pushes to `main`; an out-of-date workspace registry fails CI. The registry
  is therefore continuously coupled to committed Upstream technical records,
  standalone pilot mappings, and retained historical PR identity changes.
- Retain future independently read-back fork/ref observations as dated,
  separately reviewed records under `data/contribution-workspaces/fork-readbacks/`.
  A successful privileged fork or patch operation also needs its **separate**
  trusted execution-stage receipt; read-only parent/branch observations cannot
  stand in for one. Do not turn the generated registry into a self-attesting
  provider receipt.
- A generated workspace entry does **not** authorize any write. Distinguish
  `registered`, `fork verified`, `technical branch synced`, `external PR
  approved`, `external PR submitted`, and `maintainer accepted` in downstream
  reporting. Existing PR metrics must never count a prepared branch as a PR.

### Coverage at introduction (2026-11-09)

| Surface | Sources |
| --- | ---: |
| Original priority pool | 100 |
| Frozen assessment batches 01–22 | 125 records |
| Overlap between priority 100 and batches | 55 |
| Batch sources added outside priority 100 | 70 |
| Other native pilot sources added | 5 |
| Historical casebook/registry sources added | 8 |
| **Working inventory** | **183 distinct sources** |
| Historical fork mappings in the priority pool | 16 (not live reverified) |

The inventory includes 50 `AWAITING_EXTERNAL` technical handoffs, five
historical cases needing license review and ten unresolved source identities
with name collisions; these categories are **not additive**. No claim is made
that the 167 other working forks exist or that their patches have been pushed.
