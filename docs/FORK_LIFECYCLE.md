# Fork lifecycle MVP — prepared, not activated

OpenSiro stores contribution facts in [registry.yaml](../registry.yaml).
New working forks may live in the separate GitHub organization
[opensiro-contributions](https://github.com/opensiro-contributions).
Each is a *real GitHub fork*; this repository is not a code monorepo.

This workflow is deliberately **not an S1 authority grant**.
[Organization #274](https://github.com/opensiro/vsm-oss-organization/issues/274)
is still a proposed organizational boundary change. No VSM autonomy
grade, independent publication right or archived-fork policy is implied.

## Owner setup (mandatory for write mode)

1. Review and merge the implementation PR; the workflow should run only from
   the default branch. First use **execute=false**, which makes no changes.
2. Create an Actions environment named **fork-creation** in
   opensiro/upstream. Configure **required reviewers** and disallow
   self-approval if available. Simply mentioning an environment in YAML
   does *not* configure protection; verify the settings in the GitHub UI.
3. Create a fine-grained PAT owned by an authorized organization member,
   scoped to **opensiro-contributions**, with **Contents: read** and
   **Repository creation: write**. Confirm organizational restrictions
   and public-repository-creation policy. Do not grant repository
   deletion, transfer or broader administration permissions.
4. Store that PAT as the **fork-creation environment secret** named
   **UPSTREAM_FORK_TOKEN**. Never put a token in a repo secret,
   registry, issue, PR comment, or chat. Keep it absent until approval
   protection is configured. Rotation and revocation remain the owner's tasks.
5. Protect main and workflow changes. Use workflow execution policies
   to restrict actors who can dispatch privileged runs if available.
   A workflow_dispatch input such as execute=true is **not** sufficient
   authorization on its own.

## Usage

Actions -> **Fork lifecycle (manual)** -> Run workflow (branch: main):

- **source:** public GitHub repository as OWNER/REPOSITORY.
- **fork_name:** optional, defaults to the original repository's name.
- **all_branches:** false by default, reducing unnecessary history/refs.
- **execute:** false by default. True requests actual creation; when
  protected, the create job waits for environment approval.

The read-only preview validates the source, checks any existing destination
and reports declared SPDX license (or UNKNOWN). It does not conclude
license compatibility or maintainer willingness to accept a PR.

Create mode uses GitHub's official POST /repos/{owner}/{repo}/forks endpoint,
with the fixed destination organization. It verifies that the returned
name and owner match the requested target, then checks the direct upstream
parent of the resulting public fork. It handles asynchronous creation:
CREATED_VERIFIED only after verification; PENDING_VERIFICATION otherwise.
An existing repository with the correct direct parent is idempotently
EXISTS_VERIFIED. A name collision or wrong parent is a hard stop.

**No registry entry is automatically created.** After verifying the fork,
a maintainer updates registry.yaml and projects/<slug>/README.md with
the fork URL, contribution context, provenance and active/maintained state.
A created fork is not a submitted PR, acceptance, or upstream merge.

## Validation / exclusions

Run offline tests: python3 -m unittest discover -s tests -v

The workflow has no schedule, no PR trigger, no third-party forker action
and no automatic fork archiving. Only actions/checkout is used, pinned
to its exact v4.2.2 commit. It does not check out third-party source code
or write to external upstream repositories.

Archiving must be designed separately with isolated administration rights,
unresolved-PR/maintenance checks, an explicit archive decision and an
audit receipt. A merge must **never** automatically cause an archive.

References:
- https://docs.github.com/en/rest/repos/forks
- https://github.blog/changelog/2026-10-13-github-app-improvements-for-least-privilege-and-management/
