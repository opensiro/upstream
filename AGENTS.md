# Agent entry point — OpenSiro Upstream Contributions

This file routes agents. It does not confer authority, define VSM semantics, or substitute for a fresh GitHub readback.

1. Read the current public [OpenSiro START_HERE.md](https://github.com/opensiro/vsm-oss-organization/blob/main/START_HERE.md), then its [ecosystem owner map](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/ECOSYSTEM.md).
2. Read [README.md](README.md), the local [UPSTREAMING.md](UPSTREAMING.md) contract, [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/OPERATIONS.md](docs/OPERATIONS.md).
3. For open-ended existing work follow the shared [Organization TODO.md](https://github.com/opensiro/vsm-oss-organization/blob/main/TODO.md); for new or cross-repository work follow [CONTRIBUTOR_START.md](https://github.com/opensiro/vsm-oss-organization/blob/main/CONTRIBUTOR_START.md).
4. Read the **exact owning issue and PR**, their current heads and any frozen source refs before acting. An open PR title or older chat is not authoritative for current state.
5. Use a reviewable PR for meaningful local changes. Treat external forks, PRs and comments, protected-branch integration, branch deletion, publication-grant activation and license selection as separate actions with their own authority.
6. Before preparing an **external** PR title/body, follow the target repository's current [source-native PR template and contributor requirements](docs/ORGANIZATION_FORK_UPSTREAM_PR.md#source-native-pr-form-and-contributor-requirements). An OpenSiro generic description does not replace the target's form.
7. For an approved, validated external PR, default to **Open · Ready for review** (`draft: false`). Draft requires an explicitly documented unresolved readiness condition; an internal OpenSiro PR may follow its own separate gate. Neither state authorizes external merge.
8. For external publication, follow the [working-fork-first pipeline](docs/CONTINUOUS_WORKING_FORK_PIPELINE.md) and [five-repository wave contract](docs/EXTERNAL_PUBLICATION_WAVES.md): authorized source code, regression tests and the candidate PR diff belong on an `opensiro/...` branch of the correctly parented `opensiro-contributions/<target>` fork. Keep source-pinned technical evidence and lifecycle records in Upstream. **Do not open an internal Upstream PR whose only deliverable is a copy of a future third-party PR title/body.** Compose the final description from the checked fork diff and target's current template. **Preparation and external PR publication have separate standing mandates; neither requires repeated per-PR conversational approval** ([preparation](docs/STANDING_PREPARATION_AUTONOMY.md), [publication](docs/STANDING_EXTERNAL_PR_PUBLICATION.md)). All source-native checks, authentic provider rights and revocation controls remain mandatory. A disconnected host, ineligible source, expired mandate or unavailable provider capability remains a technical blocker.

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
python3 scripts/verified_external_outcomes.py --validate-only
```

For live checks, privileges, repository branches and retained closed PRs, follow [docs/OPERATIONS.md](docs/OPERATIONS.md) and the exact owning issue. A successful offline mock is not authorization for a network write.
