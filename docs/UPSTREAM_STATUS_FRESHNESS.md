# Upstream portfolio status: sources, freshness and Control Plane routing

## Problem and decision

PRs #933/#934 merged after the Organization's 2026-10-12 experiment snapshot and a 2026-10-17 portfolio review. The original `DASHBOARD.md` and HTML still called them open. An outdated assistant context or dashboard must **never** substitute for verification at the owner of the fact.

This repository owns public **upstream PR lifecycle observations**, not the Organization's experimental product-native fit assessments, general VSM grades or system-boundary decisions. A merged PR does not prove an S2 improvement or change an `A/C/P` ownership state.

| Question | Owner / source | Refresh rule |
| --- | --- | --- |
| Was an external PR merged, open or closed? | External GitHub PR; read-only receipt in `data/upstream-lifecycle.json` | Live GET comparison daily; fail on drift |
| How many *distinct interventions* were merged? | This repository's pinned intervention cohort and verified PR chains | Derived from receipts, never count PR URLs blindly |
| Does a contribution satisfy the four product-native fit gates? | `vsm-oss-organization/experiments/upstream-intervention-fit` | Human-reviewed experiment update; never infer from PR merge |
| Which OpenSiro-owned forks and submissions exist? | `registry.yaml`, backed by external PR links | Verify submitted registry PRs with the same read-only live check; update reviewed registry entry when an event occurs |
| What are the canonical general VSM assessments? | `vsm-harness-index` | Follow Index methodology and evidence independently |
| Is Upstream an admitted Organization S1 domain? | `vsm-oss-organization` S5 boundary decision ([#274](https://github.com/opensiro/vsm-oss-organization/issues/274)) | **Not admitted**; status observation does not admit it |

## Operator procedure

From `opensiro/upstream`:

```bash
# 1. Compare external public GitHub PR states to the saved receipt; no writes.
python3 scripts/upstream_status.py --check-live

# 2. Only if PR state drift is confirmed, refresh ALL receipts atomically.
python3 scripts/upstream_status.py --refresh

# 3. Render the dashboard, HTML and casebook from the pinned experiment
#    plus this verified lifecycle receipt.
python3 scripts/upstream_status.py --render

# 4. Check deterministic presentation and tests.
python3 scripts/upstream_status.py --check-generated
python3 -m unittest discover -s tests -p 'test_upstream_status.py'
```

`GITHUB_TOKEN` is optional for public data and used only for GitHub **GET** requests if set. API timeout, rate-limit, missing URL or unexpected state is an error, **never silently `open` or a synthetic success**. The refresh collects all primary and replacement PRs before writing the local JSON. It does not touch third-party repositories, publish a contribution or change a fit gate.

The daily workflow `.github/workflows/upstream-status-freshness.yml` has only `contents: read` and runs `--check-generated`, offline unit tests and `--check-live`. This also verifies `registry.yaml` entries with an actual `upstream_pr`, currently Cognee #434; a null PR is correctly excluded. An external lifecycle change deliberately makes the check fail with old/new state and the refresh instructions; a contributor then creates a normal reviewable PR for this OpenSiro-owned repository. It does **not** auto-commit, open PRs, grant S1 autonomy or edit Organization experimental evidence.

If the Organization's experimental **fit classifications or cohort** change, update the authoritative Organization ledger and deliberately repin `data/upstream-fit-snapshot.json` in a separately reviewed change; then run `--refresh`/`--render`. The local SHA-256 binding prevents an unnoticed fit snapshot change from reusing stale lifecycle receipts. It does not purport to automatically detect unseen remote changes to Organization fit.

## Attribution and historical evidence

- Henterprise source-contributor PR #1 closed and a maintainer-authored replacement #3 merged; the receipt includes **both** but the cohort counts **one** intervention, with contributor and merger roles distinct in the Organization ledger.
- StarNet #56 remains an open contributor PR in the receipt; equivalent implementation by a maintainer is independent and does not count as this contributor's merged PR.
- The dated case narratives keep their original historical review timestamps. The casebook's generated **PR lifecycle column** is sourced from the same verified receipt as both dashboards. Static narrative claims about a historic CI gate are not current PR states.
- Cognee #434 is a separately submitted OpenSiro-owned fork contribution, tracked in `registry.yaml` and verified in `registry_records`. It is excluded from the eight-case fit-experiment denominator.

## Control Plane handoff / no context loss

For a fresh chat, agent or Control Plane invocation:

1. Read `vsm-oss-organization/START_HERE.md` and `docs/ECOSYSTEM.md` for scope/routing.
2. Follow `opensiro/upstream` current default branch; read this contract, `registry.yaml`, `DASHBOARD.md` and `data/upstream-lifecycle.json`.
3. Report **both** `observed_at` (PR lifecycle) and `as_of` (fit), plus pending drift-check status. If fresh data matters, run `--check-live`. Never elevate saved counts into a timeless claim.
4. For a candidate improvement, link its pinned canonical Index assessment and before/after test receipts under [assessment-to-improvement](ASSESSMENT_TO_IMPROVEMENT.md); an external merged PR alone is not evidence of improved S2.
5. Before a cross-repository S1 governance or autonomy conclusion, consult Organization's owning contract. Upstream remains an adjacent portfolio/test, not a fourth admitted domain.

This is **a local evidence/freshness mechanism**, not an operative transfer of execution or publication authority.
