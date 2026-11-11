# Verified external outcomes — evidence gate and observation

**Owner:** `opensiro/upstream` (Upstream Contributions S1). This is the source-backed **candidate observer and independently revalidated accepted merged-change exporter**; Organization owns the public metrics contract. An accepted source merge is not a claim of deployed benefit.
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

It cross-checks source-ledger PR URLs and intervention deduplication
against the current `portfolio_reconcile.py` union, including any
original/replacement chains. **Do not freeze a cohort count in this document**:
the owning scripts validate the current corpus, and their live output reports
the actual number of interventions, PR URLs and excluded non-publications.
New sources require a reviewed cohort/schema migration. The source exclusion
count is separate from the outcome denominator.

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

## Automatic accepted-source export — bounded S1 evidence rule

The `observe` job automatically exports every candidate whose live result is
`VERIFIED` as `ACCEPTED_MERGED_CHANGE_ONLY`, with
`acceptance_basis=DETERMINISTIC_VERIFIED_MERGE` and
`benefit_claim=NOT_MEASURED`. No per-intervention owner consent, GitHub
`APPROVED` review or independent S3* audit is needed for this narrow
deterministic outcome. The selection is made from the **complete, source-digest
checked observation**, then each positive case is **re-evaluated from live
first-party external PR and native CI APIs** before export. An unverified,
unmerged, incomplete, drifted, stale or ambiguous result cannot be accepted.

The previously versioned
[`data/verified-external-outcomes/accepted-v1.json`](../data/verified-external-outcomes/accepted-v1.json)
retains **optional historical decision provenance** for the two originally
owner-accepted Improvement interventions: Agent Fleet
([decision #177](https://github.com/opensiro/upstream/pull/177)) and Citadel
([decision #178](https://github.com/opensiro/upstream/pull/178)). Membership
in this manually maintained file **does not determine automatic acceptance**:
new machine-`VERIFIED` interventions are counted even when absent from it.
Legacy records must still have exact first-party evidence and attributable
merged decision PRs; a stale or counterfeit historical claim fails closed.
Do not add new entries merely to obtain automatic acceptance.

Each historical entry identifies one existing source intervention,
the **complete original/replacement PR chain** and effective PR, exact external
merge SHA/timestamp, immutable native test receipt, and a merged Upstream
decision PR attributable to the authorized owner. Its decision scope is
`ACCEPTED_MERGED_CHANGE_ONLY`, with `benefit_claim=NOT_MEASURED`. This scope
never asserts runtime deployment or productivity. A historical decision URL
must refer to a real first-party Upstream PR merged by the named owner; inserting
a URL into JSON cannot satisfy historical-provenance validation.

To bind the owner's decision to evidence rather than an unrelated PR, the
decision PR's description must contain three exact standalone lines (substitute
source-backed values; the marker lines alone are not acceptance):

```text
Outcome-Acceptance: <intervention_id>
Outcome-Merge: <40-character external merge SHA>
Outcome-Native-Receipt: <immutable GitHub native evidence URL>
```

The historical ledger may link an owner decision only after its merge. This is
additional audit provenance, **not** the route that every new outcome must use.

`scripts/accepted_external_outcomes.py` checks source IDs, replacement
chains and source/cohort digests against the complete current live observation.
For **every `VERIFIED` candidate** it independently re-fetches first-party
disposition, native CI and (where needed) post-publication source compare.
If an optional historical decision exists, its exact provenance is checked
too. Drift, missing receipt, ambiguous status or invalid historical provenance
aborts the export. `PENDING_REVIEW` Corrective/casebook/registry cases remain
outside automatic acceptance and need an explicitly scoped semantic path.

```bash
python3 scripts/accepted_external_outcomes.py --validate-only
python3 -m unittest discover -s tests -p 'test_accepted_external_outcomes.py' -v
# After a successful read-only observe, with GITHUB_TOKEN for live revalidation:
python3 scripts/accepted_external_outcomes.py \
  --observation-json /tmp/upstream-external-outcomes.json \
  --output-json /tmp/upstream-accepted-outcomes.json
```

The existing workflow adds the separately labeled accepted-source JSON into
the **same 90-day artifact**; it does not create another workflow/job or a
GitHub write. Even a nonempty, valid export is
`UPSTREAM_ACCEPTED_SOURCE_ONLY` with `organization_metric_claimed=false`.
The separate [Organization PR #322](https://github.com/opensiro/vsm-oss-organization/pull/322)
is now **merged** (`da377c16375793e6912db56996094e58d8dccfb2`).
The Organization metrics workflow consumes a fresh, first-party revalidated
export from this owning implementation, checks owner source/cohort digests,
enforces distinct identities and immutable native receipts, and fails closed
when evidence is stale or contradictory. The measured quantity is narrowly
**source-verified merged changes**, not deployed improvement. Missing live
evidence remains unclaimed, not zero. Historical growth windows remain
unavailable without independently reproducible baseline exports.

## Remaining evidence and publication work

1. Keep the **live Upstream observation and accepted-source export** healthy.
   PR-check or mock success is not evidence of an actual third-party merge.
2. Resolve ambiguous Corrective/casebook records with attributable owner
   decisions and pinned native receipts; Henterprise replacement counts only
   once, and independently implemented fixes do not become OpenSiro merges.
3. Keep [Organization metrics contract](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/METRICS.md)
   and the separately [generated public-site projection](https://github.com/opensiro/opensiro.com/blob/main/scripts/sync-vsm-oss-metrics.cjs)
   aligned by source-controlled, reviewed changes. Do **not** substitute the
   resolved-PR acceptance rate or historic Product-native fit percentage.
4. Recheck website job/output at the owning site revision before claiming
   public deployment; a merged collector does not itself deploy a page.

Risk-based independent review remains appropriate for ambiguous attribution;
routine exact-identity CI readback does not itself require a fabricated S3*
assessment. Third-party maintainers remain the only owners of external merge.

The dated [2026-11-07 manual first-party readback](OUTCOME_AGENT_READBACK_2026-11-07.md)
is an **agent-authored candidate dossier**, not a successful `observe` run,
an accepted outcome ledger or an Organization metric. Its volatile status
snapshot must be revalidated against the next complete live workflow artifact.
