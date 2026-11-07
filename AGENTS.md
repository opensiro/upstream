# Agent entry point — OpenSiro Upstream Contributions

This file routes agents. It does not confer authority, define VSM semantics, or substitute for a fresh GitHub readback.

1. Read the current public [OpenSiro START_HERE.md](https://github.com/opensiro/vsm-oss-organization/blob/main/START_HERE.md), then its [ecosystem owner map](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/ECOSYSTEM.md).
2. Read [README.md](README.md), the local [UPSTREAMING.md](UPSTREAMING.md) contract, [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/OPERATIONS.md](docs/OPERATIONS.md).
3. For open-ended existing work follow the shared [Organization TODO.md](https://github.com/opensiro/vsm-oss-organization/blob/main/TODO.md); for new or cross-repository work follow [CONTRIBUTOR_START.md](https://github.com/opensiro/vsm-oss-organization/blob/main/CONTRIBUTOR_START.md).
4. Read the **exact owning issue and PR**, their current heads and any frozen source refs before acting. An open PR title or older chat is not authoritative for current state.
5. Use a reviewable PR for meaningful local changes. Treat external forks, PRs and comments, protected-branch integration, branch deletion, publication-grant activation and license selection as separate actions with their own authority.

## Evidence and non-conflation

- The [Index](https://github.com/opensiro/vsm-harness-index) owns accepted VSM assessments, [Skills](https://github.com/opensiro/vsm-harness-skills) owns methodology, [Profile](https://github.com/opensiro/vsm-harness-profile) owns semantics, and [Organization](https://github.com/opensiro/vsm-oss-organization) owns the S1/S5 domain boundary and experimental fit.
- Upstream owns its local contribution records, native test receipts, public external-PR lifecycle observations and generated views. Keep external PR identity, distinct intervention identity, product-native effect, cohort-relative fit and fork-lifecycle state separate.
- Pin external product code for native tests. Do not run live model/browser agent quality trials as if they were required evidence for assessment-derived product improvement.
- A `closed` external PR is not by itself a rejection. The actor who performed closure requires GitHub issue-event evidence; the **reason** needs separate primary evidence. A maintainer-written replacement is not a contributor PR merge.
- Never silently widen the 18-target acceptance cohort, change the Organization fit ledger, or count both original and replacement PRs as separate interventions.
- `DASHBOARD.md`, `HARNESS_STATUS.md`, `docs/index.html` and generated casebook regions are materializations; use their scripts and validate rather than hand-editing.

## Common local verification

```bash
python3 -m unittest discover -s tests -v
python3 scripts/upstream_status.py --check-generated
python3 scripts/harness_status.py --check
python3 scripts/portfolio_reconcile.py --validate-only
```

For live checks, privileges, repository branches and retained closed PRs, follow [docs/OPERATIONS.md](docs/OPERATIONS.md) and the exact owning issue. A successful offline mock is not authorization for a network write.
