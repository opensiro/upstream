# Continuous source → OpenSiro Contributions workspace pipeline

**Owner:** Upstream [#56](https://github.com/opensiro/upstream/issues/56),
fork executor [#28](https://github.com/opensiro/upstream/issues/28) under
[#6](https://github.com/opensiro/upstream/issues/6). **Policy decision:**
technical changes should reach the matching `opensiro-contributions` working
fork in the same contribution cycle; an external upstream PR requires an
**explicit human approval for that PR**. No automatic external PR publication.

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
   existing third-party PRs and fork state first.
4. **Fork preparation, conditionally executable:** a **trusted, actor-bound
   execution host** verifies exact source, license, branch, SHA, parent,
   visibility, destination permissions, and its one-use create/prepare-stage
   grant. Reuse the verified existing fork or create the exact missing public
   fork; put the validated change on an `opensiro/...` working branch and run
   allowed native CI. Read back the commit and record its attributable SHA.
   The next technical change must update that working branch under a fresh
   bound stage decision and drift checks; no detached private side queue.
5. **Human release decision:** show the exact changed files, test receipt,
   fork branch, license/contributor conditions, target base and draft external
   PR body to a human. Only after a **specific human approval** may the
   trusted publisher create that external PR. No implied approval from a
   batch command, internal PR, prior approvals, or the finite 34-case mandate.
   The external maintainer alone decides acceptance or merge.

The step-4 write executor is **not live-connected** in the current ChatGPT
GitHub connector. The preparatory adapters in `scripts/` and offline tests
do not constitute host authentication or stage authority. Until #6/#28 are
resolved, `WAITING_FOR_TRUSTED_EXECUTOR` is a real blocked state: the inventory
and technical handoff are continuously updated in Upstream, while fork
creation, branch sync, and third-party PRs remain unexecuted. Do not
silently substitute a PAT, direct CLI write, unprotected Actions workflow,
or an arbitrary `approved_by` field for the missing host boundary.

## Command and CI contract

```bash
python3 scripts/contribution_workspaces.py status
python3 scripts/contribution_workspaces.py list --source talktorana/agent-harness
python3 scripts/contribution_workspaces.py sync
python3 scripts/contribution_workspaces.py check
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
