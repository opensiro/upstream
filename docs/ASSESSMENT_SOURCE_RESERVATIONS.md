# Assessment batch source reservations — experimental primitive

**Owner:** [Upstream #144](https://github.com/opensiro/upstream/issues/144). **Status:** proposal / opt-in primitive, **not** the live batch admission gate.

`scripts/assessment_source_reservations.py` demonstrates a Git-native, cross-run
source-reservation operation. The ledger is a single `reservations.json` file on
the dedicated `refs/heads/batch-upstream-reservations` branch in this repository.
It is deliberately *not* a new scheduler, VSM assessor or permission issuer.

## Mechanism

1. Validate the entire five-row candidate manifest against a **local Index checkout
   at the manifest's exact frozen `index_sha`**, including included status, S1=A,
   reviewed source commit and assessment identity. No remote Index attestation is
   claimed from this local-only check.
2. Fetch the **existing** reservation branch. A missing/unreadable ref or an
   unexpected tree fails closed; the script never bootstraps a branch implicitly.
3. Replay append-only `CLAIM` / `RELEASE` events. Sources are compared by
   case-folded `owner/repo` identity. A live claim or duplicate batch ID fails.
   Releases must cite a reviewed Upstream issue/PR and preserve the claimant,
   exact source set and an auditable reason. Recovery is a *separate reviewed
   ledger change*, not a TTL or silent eviction.
4. Default CLI mode previews the claim. The explicit `--write-claim` option
   creates a Git commit **without modifying the checkout** and attempts an
   ordinary, non-forced, fast-forward push to the ledger ref. If two writers
   read the same parent, at most one can publish its different child; the
   other fails with `BLOCKED_CONCURRENT_RESERVATION`. Refetch and revalidate
   after rejection. Never force-push or override the losing writer.

Example **preview only** (requires a previously established reservation branch):

```bash
python3 scripts/assessment_source_reservations.py \
  data/assessment-candidate-batches/2026-11-06-13.json \
  --index-root /path/to/exact-pinned-vsm-harness-index \
  --git-root /path/to/upstream \
  --evidence https://github.com/opensiro/upstream/issues/144
```

Writing a claim requires a separately reviewed adoption decision and repository
permissions, plus `--write-claim`; this document does not instruct operators to
initialize the ledger branch or treat a successful claim as full admission.

## Critical remaining gates before operational use

- **Canonical remote visibility:** compare the exact Index ref to the owning
  canonical remote. The current script proves only its checked-out SHA.
- **Merged and open work:** machine-check all historical merged batch manifests
  and *every* currently active open draft PR immediately before claim, then
  revalidate at review/merge. A CAS claim alone does not discover legacy
  unreserved drafts, a recent main merge or GitHub repository renames.
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

The tests use a local bare Git remote. They exercise two workers with the same
parent, a losing non-fast-forward push, case-alias collisions, append-only
release/recovery semantics, exact Index HEAD mismatch, incomplete cohorts and
unavailable reservation refs. No GitHub or model provider is invoked.
