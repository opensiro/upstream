# Fork lifecycle MVP — legacy implementation, not activated

> **The deployed operator proposal preview is
> [conversation-first and provider-agnostic](BATCH_PROPOSALS.md).**
> The future owner-authorized execution policy is still only proposed
> in [draft PR #7](https://github.com/opensiro/upstream/pull/7).
> This file describes the previously merged single-fork MVP for auditability;
> it is **not an activation checklist**. Do not configure per-fork GitHub
> Required reviewers as the user-facing approval mechanism.
>
> **STOP: DO NOT PROVISION `UPSTREAM_FORK_TOKEN`.** The deployed `main`
> is now **preview-only** since
> [merged safety PR #8](https://github.com/opensiro/upstream/pull/8).
> The legacy manual `execute=true` route, privileged job and credential
> reference have been removed from the workflow. The separately authorized
> batch executor in [draft PR #7](https://github.com/opensiro/upstream/pull/7)
> has **not** been implemented or accepted.
> [Issue #6](https://github.com/opensiro/upstream/issues/6)
> tracks the actual activation gates.

## What is already implemented

[Initial PR #5](https://github.com/opensiro/upstream/pull/5) introduced
`scripts/create_fork.py` and a manual GitHub Actions workflow:

- Fixed destination GitHub organization:
  [`opensiro-contributions`](https://github.com/opensiro-contributions).
- Source is a public, enabled, non-archived `OWNER/REPOSITORY`.
- Optional destination name; default branch only by default.
- Read-only source/destination preflight, observed SPDX license reporting.
- The **underlying API helper** can request a fork and verify its direct
  GitHub `parent` relationship, with asynchronous polling and a hard
  stop on collisions or mismatched parent.
- A completed `CREATED_VERIFIED` receipt is not an upstream submission,
  acceptance, or VSM assessment improvement.

This helper and the original workflow were *source-prepared*, not granted
operational authority. No fork is created merely by merging the code.

## Safe source inspection

While the approved-batch executor remains unavailable, use the
[local batch proposal preview](BATCH_PROPOSALS.md) for candidate selection.
For **one actual upstream source**, the manual fork lifecycle workflow,
made preview-only by PR #8, can perform read-only source/destination
inspection, equivalent to:

```bash
python3 scripts/create_fork.py --source OWNER/REPOSITORY
```

Do **not** supply `--execute`, provision an environment secret or
treat a `DRY_RUN` as authorization. The helper API still contains the legacy
creation capability, but the deployed workflow **has no write job**. This
does not establish the future batch-approval authorization boundary.

## Current approval model (future implementation)

1. Any compatible agent or conversational client proposes a finite batch
   with per-system problem, concrete planned change, expected improvement,
   validation, and public evidence.
2. The operator selects exactly the allowed entries and **explicit
   permission stages** within one chat-level batch decision.
3. A separate, protected authorization boundary must verify the selected
   set. A JSON `approved_by` assertion alone does **not** authenticate
   who approved it.
4. Only a tested batch-specific executor may use a least-privilege fork
   credential to carry out **approved `create_public_fork` operations**.
   Contribution preparation, external PR publication and archiving require
   their own explicitly authorized stages; none are implemented here.
5. Record per-item GitHub-verified results and maintain separate upstream
   contribution/outcome and fork maintenance statuses in
   [`registry.yaml`](../registry.yaml).

A GitHub Actions environment may eventually be used as a protected secret
boundary, without an extra GitHub reviewer click for each fork, but it is
**not** a substitute for batch authorization and restricted workflow edits.

## Remaining validation before activation

- [x] Replace the legacy manual write path in **deployed** `main`.
  [PR #8](https://github.com/opensiro/upstream/pull/8) removed its
  `execute` input, privileged job and token reference; verify this remains
  true after any subsequent workflow changes.
- Finish the approved-batch executor and its dedicated positive/negative
  tests; these are not yet part of CI.
- Protect `main` and workflow/manifest modification authority.
- Configure the environment and scope a separate credential only **after**
  independent validation of those technical enforcement controls.
- Preserve exact approval provenance; do not describe agent-authored JSON
  or an issue link as an independently authenticated operator signature.
- Verify the first real owner-authorized batch with receipt links and
  only then update the registry for observed, correctly parented forks.

The [Organization #274](https://github.com/opensiro/vsm-oss-organization/issues/274)
boundary decision is separate. This infrastructure work does not admit
Upstream as a fourth S1 domain or authorize a third-party upstream PR.

References:
- https://docs.github.com/en/rest/repos/forks
- https://github.com/opensiro/upstream/pull/5
- https://github.com/opensiro/upstream/pull/7
