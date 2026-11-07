# Verified external outcomes — evidence gate and observation

**Owner:** `opensiro/upstream` (Upstream Contributions S1). This is a
source-backed **candidate/evidence collector**, not an Organization-issued KPI.
The metric contract is owned by
[`vsm-oss-organization/metrics.yaml`](https://github.com/opensiro/vsm-oss-organization/blob/main/metrics.yaml)
and [`docs/METRICS.md`](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/METRICS.md).
`Product-native fit` remains **deprecated**; no fit judgment is generated here.

## What constitutes an outcome

The source-defined gate is: **confirmed first-party external disposition +
attributable contribution identity + source-pinned native evidence**. The gate
prohibits inferring deployed benefit or productivity from a PR merge.

| Observation | Sufficient for automatic evidence verification? |
| --- | --- |
| PR merged at third-party repository | **No**: only one gate |
| Exact merge SHA, merged timestamp, contributor, source fork and maintainer merge actor | Necessary first-party disposition/attribution evidence |
| Successful native CI with exact run ID, owning internal PR and completed result | Necessary pinned test receipt in the current Improvement fast path |
| Closed without merge; maintainer replaced original PR | **No**: interpret and deduplicate after human evidence review |
| Open PR, disappearing PR, mutable `blob/main` receipt | **No** |
| First-party accepted outcome | Does **not** assert deployed user benefit |

The deterministic fast path currently covers two exact, pre-reviewed
**Improvement** records: Citadel #366 and Agent Fleet #43. Its checks include
the external author and fork, final head SHA, merge SHA, merge timestamp,
independent merger and the matching successful OpenSiro native CI run attached
to the recorded internal PR. If the published and landed source heads differ,
the GitHub compare must be complete and show **workflow-only** changes; any
product-code delta requires a fresh native receipt or reviewed attribution.
Neither case is counted until those checks succeed in the live observation.
Any identity/provenance drift produces `PENDING_REVIEW` or fails closed; it
never silently expands the count.

Corrective publications currently have `SUBMITTED` receipts, frequently with
**mutable** `blob/main` test links. A merged Corrective PR therefore needs
reviewed completion and native receipt pinning before promotion. Historical
casebook PRs and the registry require semantic attribution; Henterprise's
original and replacement PR are **one intervention**, not two results.
StarNet's independent third-party implementation is **not** automatically a
merge of the OpenSiro contribution. Blocked Corrective items have no external
PR and are explicitly excluded from the candidate cohort, not labeled failures.

## Inputs and outputs

`scripts/verified_external_outcomes.py` reads, but never modifies:

- `data/corrective-publication/2026-10-23-01.json`;
- `data/improvement-publication/2026-10-24-01.json`;
- frozen `data/upstream-fit-snapshot.json` **for identity only**;
- `registry.yaml`.

It cross-checks that these source ledgers cover the same **25 PR URLs** as the
existing `portfolio_reconcile.py` union, while keeping **24 distinct
interventions** (one Henterprise replacement pair). These counts are present
source-contract checks, not everlasting Organization metrics. New sources
require a reviewed cohort/schema migration. The source exclusion count is
separate from the outcome denominator.

The live output contains a UTC timestamp, source and cohort SHA256 digests,
one traceable record per intervention, PR URL(s), externally observed state,
merge commit SHA, source receipt path, native test receipt if recorded, and
classification with machine-readable reason codes:

- `VERIFIED` — **automatically verified evidence candidate**, not yet the
  Organization's claimed primary metric;
- `PENDING_REVIEW` — semantic attribution, mutable evidence, changes to the
  tested head or incomplete publication disposition;
- `INSUFFICIENT_EVIDENCE` — no externally merged resolution;
- `UNVERIFIABLE` — only an explicitly reviewed unavailable PR source.

Run locally:

```bash
python3 scripts/verified_external_outcomes.py --validate-only
python3 -m unittest discover -s tests -p 'test_verified_external_outcomes.py' -v
# Requires GITHUB_TOKEN for read-only GitHub API calls:
python3 scripts/verified_external_outcomes.py --report --output-json /tmp/upstream-external-outcomes.json
```

The [daily/manual workflow](../.github/workflows/verified-external-outcomes.yml)
produces a readable job summary and 90-day JSON artifact; PR runs execute
offline validation only. No scheduled GitHub commits, issue updates, external
publication, PR merge, retroactive ledger edits or cross-repository writes are
performed. A partial or unexpected source error fails the observation.

## Next gate: publish the actual primary metric

1. Verify a successful **live workflow run and artifact**; do not substitute
   offline mocks or passing CI for a real observation.
2. Review ambiguous human disposition, native receipt and replacement-chain
   evidence in an Upstream-owned PR. Preserve accepted historical provenance.
3. Define an owner-reviewed, versioned **accepted outcome ledger** whose exact
   records can be revalidated from first-party evidence and included without
   double counting; never use a raw merged-PR count as this ledger.
4. Only then extend the Organization generic metrics collector from
   `unclaimed_semantic_evidence` to a value gated on the validated Upstream
   accepted ledger. The public site may display the result **after** that
   contract lands, never by relabeling the PR acceptance percentage.

Risk-based independent review remains appropriate for ambiguous attribution;
routine exact-identity CI readback does not itself require a fabricated S3*
assessment. Third-party maintainers remain the only owners of external merge.
