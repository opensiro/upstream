# External PR portfolio observation history

## What is automated

The [daily/manual portfolio reconciliation workflow](../.github/workflows/portfolio-reconciliation.yml)
reads the **existing** reviewed 18-PR maintenance watchlist, frozen historical
casebook identities, and OpenSiro fork registry. It publishes one human-readable
GitHub Actions job summary and **one JSON artifact from the same observation**.
The artifact is named `upstream-portfolio-observation-<run_id>` and retained for
**90 days** under the repository's GitHub Actions artifact policies.

The JSON includes `schema_version`, UTC `observed_at`, `cohort_sha256` and the
exact deduplicated PR URL/group/outcome records. `cohort_sha256` hashes only
the PR identities and their cohort membership, never their live outcomes.
The known 404 remains explicitly unverifiable; source errors stop the run
without publishing a successful partial observation.

## Compare two or more retained runs

Download the `upstream-portfolio-observation-<run_id>` artifacts from their
individual GitHub Actions runs, then extract their JSON files to distinct local
paths. Run:

```bash
python3 scripts/portfolio_history.py first.json second.json
```

The script uses no network or GitHub token. It validates each snapshot,
rejects changed cohorts and duplicate timestamps, sorts chronologically,
and reports both the **official 18-target resolved-only watchlist rate** and
the **broader 25-URL descriptive union** separately. The 25 URLs overlap
in interventions and are **not** an expanded 25-intervention acceptance cohort.

## Limits and next stage

- This workflow's artifacts are a **bounded, expiring history**, not a permanent
  archive. The separate [public site](https://opensiro.com/upstream-portfolio.html)
  now displays the latest successfully materialized observation, and its
  [published JSON](https://opensiro.com/assets/upstream-portfolio-observation.json)
  is committed with source SHA to the site's Git history. That site history
  provides dated revisions but is **not an immutable independent audit log**.
  GitHub may remove workflow artifacts under repository/retention rules.
- A first successful live scheduled/manual `observe` job and downloadable
  artifact must be verified before claiming active historical coverage.
- PR `merged` / `closed_unmerged` states do not establish why a contributor's
  PR closed, deployed functional improvement, or Organization-owned
  `verified_external_outcomes`. No `Product-native fit` scores are generated:
  that experimental metric is **DEPRECATED**.
- Changes to the watched cohort require source review and a new fingerprint;
  comparing across cohort revisions requires an explicit reviewed mapping.
- The workflow has **read-only** `contents` permission; no issue, Git commit,
  cross-repository writes, automatic PR publication or merge rights are added.

The website's own [sync procedure](https://github.com/opensiro/opensiro.com/blob/main/docs/UPSTREAM_PORTFOLIO_SYNC.md)
uses this Upstream repository's collector and explicit live GitHub PR evidence;
it neither changes the original 18-target watchlist nor computes Organization
verified adoption. As of 2026-11-07, the first site source observation and
Pages deployment were verified independently; the **first scheduled Upstream
artifact run remains to be verified**. A passing CI run is not proof of a
live artifact. A longer-term immutable history store remains a separate design.
