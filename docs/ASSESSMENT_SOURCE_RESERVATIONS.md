# Assessment batch source reservations — experimental primitive

**Owner:** [Upstream #144](https://github.com/opensiro/upstream/issues/144). **Status:** proposal / opt-in primitive, **not** the live batch admission gate.

`scripts/assessment_source_reservations.py` demonstrates a Git-native, cross-run
source-reservation operation. The ledger is a single `reservations.json` file on
the dedicated `refs/heads/batch-upstream-reservations` branch in this repository.
It is deliberately *not* a new scheduler, VSM assessor or permission issuer.

## Mechanism

1. Validate the entire five-row candidate manifest against a **local Index checkout
   at the manifest's exact frozen `index_sha`**, including included status, S1=A,
   reviewed source commit and assessment identity. The standalone reservation
   **preview** only checks that local frozen object.
2. For an explicit **write**, perform a **GET-only live collision preflight**:
   read canonical `upstream/main`'s Git tree and every merged frozen batch
   manifest, enumerate **all** open PRs and their changed batch manifests,
   then repeat main/open-PR head inventory to detect changes during the read.
   First attest that the exact frozen Index SHA is reachable from the current
   `opensiro/vsm-harness-index/main` by GitHub's commit comparison endpoint;
   repeat its main SHA after the scan. A duplicate normalized source,
   unreachable Index SHA, truncated API page/tree, malformed response,
   inaccessible PR head or rate-limit failure blocks the write. A caller may
   identify its own PR only when it holds exactly one matching manifest.
3. Fetch the **existing** reservation branch. A missing/unreadable ref or an
   unexpected tree fails closed; the script never bootstraps a branch implicitly.
4. Replay append-only `CLAIM` / `RELEASE` events. Sources are compared by
   case-folded `owner/repo` identity. A live claim or duplicate batch ID fails.
   Releases must cite a reviewed Upstream issue/PR and preserve the claimant,
   exact source set and an auditable reason. Recovery is a *separate reviewed
   ledger change*, not a TTL or silent eviction.
5. Default CLI mode previews the claim. The explicit `--write-claim` option
   creates a Git commit **without modifying the checkout** and attempts an
   ordinary, non-forced, fast-forward push to the ledger ref. If two writers
   read the same parent, at most one can publish its different child; the
   other fails with `BLOCKED_CONCURRENT_RESERVATION`. Refetch and revalidate
   after rejection. Never force-push or override the losing writer.
   Actual concurrent Git clients may receive `incorrect old value provided`
   when both push children of the same ref head. This explicit Git CAS error
   is classified as `BLOCKED_CONCURRENT_RESERVATION`, not as a generic Git
   permission failure. A local bare-remote fixture verifies one winning push
   and one attributable collision; it is **not** a live GitHub two-agent test
   or activation of the dormant reservation branch.

Example **preview only** (requires a previously established reservation branch):

```bash
python3 scripts/assessment_source_reservations.py \
  data/assessment-candidate-batches/2026-11-06-13.json \
  --index-root /path/to/exact-pinned-vsm-harness-index \
  --git-root /path/to/upstream \
  --evidence https://github.com/opensiro/upstream/issues/144
```

Independent **read-only remote preflight** (does not require the reservation
branch or make any write):

```bash
python3 scripts/assessment_batch_conflict_preflight.py \
  data/assessment-candidate-batches/2026-11-06-13.json \
  --index-root /path/to/exact-pinned-vsm-harness-index
```

The preflight reads public GitHub data anonymously or uses an ordinary
`GITHUB_TOKEN` when present; errors fail closed. Its receipt reports the
canonical Index main SHA, ancestral pin, count of upstream main manifests,
open PRs, active PR manifests and exact conflicts.
`CLEAR_PREVIEW_ONLY` is **not** a reservation or an admission.

## Default: human-owned merge decision, no reservation activation

The repository owner may keep ordinary `batch upstream` work **manual at merge**:

1. Agents independently prepare source-linked, reviewable five-row proposals.
   They may use the GET-only preflight without a reservation branch.
2. Immediately before an owner decision, re-run the preflight against current
   Index and Upstream GitHub state. A collision or incomplete visibility means
   **do not merge that proposal** without reconciling the competing source.
3. The owner decides which PR, if any, to merge. A green preflight or green CI
   is evidence for the review, **not** authority for an automatic merge or
   third-party publication.

This path does **not** require the CAS reservation branch or a new required CI
setting. It protects the accepted `main` state through human review, but it
**does not prevent duplicated work before review** or make two simultaneous
manual decisions atomic. If that cost becomes material, the opt-in CAS branch
can be separately reviewed and enabled for early source admission.

Writing a claim requires a separately reviewed adoption decision and repository
permissions, plus `--write-claim`; this document does not instruct operators to
initialize the ledger branch or treat a successful claim as full admission.

## Critical remaining gates before operational use

- **Cross-ref atomicity:** the read-only preflight now scans merged batch
  manifests and all visible open draft PRs, but GitHub's main and PR heads
  can change **after** that scan, while only reservation commits are serialized
  by CAS. Revalidate at review/merge and ensure admitted work uses the gate.
  A GitHub repository rename/alias is not resolved by case folding alone.
- **Required CI/admission:** provide a reviewable check verifying source
  disjointness, provenance, per-row gates, and the authoritative reservation
  ledger. Existing `validate/status/next` remain read-only and unchanged.
- **Recovery:** introduce an owner-reviewed release/abandoned-draft procedure
  with evidence and a release writer. `replay()` already checks release events,
  but this prototype does not expose release mutation via CLI.
- **Branch policy:** establish the dedicated branch intentionally; prohibit
  history rewrites and define who may append claims/releases. Ensure protected
  branch rules permit only the approved admission mechanism.

No `SUBMITTED` state, third-party action, grant or autonomy/S5 finding follows
from a claim. Until all gates above are implemented, `CLAIMED_CAS` is only a
reservation event; its receipt explicitly reports `admission_attested: false`.

## Offline validation

`python3 -m unittest tests/test_assessment_source_reservations.py -v`

`python3 -m unittest tests/test_assessment_batch_conflict_preflight.py -v`

The tests use a local bare Git remote. They exercise two workers with the same
parent, a losing non-fast-forward push, case-alias collisions, append-only
release/recovery semantics, exact Index HEAD mismatch, incomplete cohorts and
unavailable reservation refs. No GitHub or model provider is invoked.

The preflight fixtures also cover complete merged/open-source scans, casefold
collisions, exact-own-PR matching, missing Index pins, truncated GitHub trees,
API visibility failures, a canonical Index ancestry mismatch, and changing
Index/Upstream main SHAs.
