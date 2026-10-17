# Updating OpenSiro's upstream registry

The registry describes contributions **from** OpenSiro **to** external OSS projects.

- Use one `registry.yaml` record per distinct project/contribution. Keep `upstream` and `fork` as actual GitHub repository URLs.
- Keep **contribution outcome** separate from **fork lifecycle**. The former is the upstream status; the latter is an OpenSiro maintenance decision.
- Use `research`, `preparing`, `submitted`, `merged`, `closed`, or `not-accepted` for contribution status.
- Use `active`, `maintained`, or `archived` for maintenance status.
- Record upstream issue/PR links **only after they exist**. Document the evidence for a merge before setting `merged`.
- Update `projects/<slug>/README.md` with scope, research receipts, compatibility and next actions. Do not copy entire external repositories here.
- Before archiving a fork: check unresolved PRs/maintenance obligations, record its final state and archive reason, then archive the public fork intentionally. Do not automate archiving based on a merged PR alone.
- Do not add a gatekeeping VSM assessment or operational S3–S5 mandates to this lightweight portfolio.

## External intervention casebook

The [casebook](cases/README.md) is a read-only portfolio view of interventions recorded under the [Organization upstream-intervention-fit experiment](https://github.com/opensiro/vsm-oss-organization/tree/main/experiments/upstream-intervention-fit). Include both successes and failures, link first-party PR/review/commit evidence, and distinguish a submitted PR from a merged PR and from an independently landed maintainer implementation.

Do **not** create duplicate `registry.yaml` fork-lifecycle records for personal contributor forks just to track an experiment. Do **not** assign or update a product-native fit gate here independently: change the Organization-owned observation with evidence and then refresh this view. The experimental fit label is neither maintainer approval nor a VSM assessment result.
