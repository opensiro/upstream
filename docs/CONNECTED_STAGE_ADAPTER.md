# Connected stage adapter — narrow preparation pilot (source-prepared)

**Status: SOURCE-PREPARED / MOCK-TESTED; NOT HOST-CONNECTED; NOT OPERATOR-AUTHORIZED.**
[Issue #6](https://github.com/opensiro/upstream/issues/6) remains open.
This Python module is a small dependency-injected bridge for a **same-session
connected GitHub agent**, not a CLI runner, approval store, scheduled job,
GitHub App installation or bypass for the read-only batch preview.

## What is implemented

`scripts/connected_stage_adapter.py` exposes
`execute_one_test_file(manifest, selected_ids, stage_scopes, candidate_id,
action, github, authorize)`.

Only **one narrow portion of `prepare_contribution`** is implemented:
create a new `opensiro/...` branch from a pinned base SHA in an **existing
public fork** that already belongs to the operator's connected writable
repositories, then create **one new test file** under root `tests/` or package-local `packages/.../tests/` or
`packages/.../test/` (for upstream projects that keep tests with each package).
It will not modify an existing file, create a fork, submit an external PR,
archive, change registry state or push arbitrary changes.

Before the first GitHub write, it:

1. Loads the strict `proposal_only` draft through the existing validator,
   verifies the specific selected ID, stage subset and unblocked candidate.
   Both selection digests remain unsigned identifiers, not authorization.
2. Compares exact source and SPDX observation with live repository metadata.
   Re-reads the existing working repository and requires `fork=true`,
   `parent.full_name` matching the candidate's upstream, `permissions.push=true`,
   public/non-archived source and working fork, pinned base branch SHA,
   absence of the proposed new branch and of the proposed new test file.
   These observations do not replace a human license/CLA/contribution-policy check.
3. Calls `authorize(intent)` with the **exact action** and digest of the
   proposed content. **This callback must be supplied by a trusted live
   conversation host that actually attributed a current operator decision.**
   A caller-supplied `lambda _: True` is *not* an authenticated decision.
   No `approved_by` JSON, public GitHub comment, hash or API credential suffices.
4. Performs the same live preflight again immediately before mutation.
   Then uses only the passed authenticated port's `create_branch` and
   `create_file`; it reads back the file and branch to verify their state.

The `github` port must provide these operations, mapped by a **trusted
host-side wrapper** to provider actions (normalizing raw GitHub responses):
`repo(full_name)`, `branch(repo, branch)`, `file(repo, path, ref)`,
`create_branch(repo, new_branch, expected_sha)`, and
`create_file(repo, path, text, branch)`. Only true file/branch absence may
raise the local `NotFound`; **403, auth failure and timeout are not 404**.
For committed changes `create_file` must return `commit_sha`, while
`branch` must expose `sha` and `file` must expose decoded UTF-8 `content`.
The wrapper is **not shipped** by this repository; GitHub connector APIs
are host features, not Python imports.

The `action` mapping has **exactly** these fields:
`working_repo`, `base_branch`, `base_sha`, `new_branch`,
`file_path`, `content`. The new branch begins `opensiro/`, and the
new file is within `tests/`, with a 48 KiB limit.

## Outcomes and limits

- `CREATED_VERIFIED`: new branch/file responses were independently
  checked against the exact proposed content and commit SHA.
- `PENDING_VERIFICATION`: an API create call returned success, but readback
  did not establish the expected state. Requires human review before retry.
- `PARTIAL`: branch was created but file creation failed. Do **not** reuse
  the same approval to retry or delete the branch automatically.
- `FAILED`: branch creation failed; do not assume no remote side effects.
- `StageBlocked`: missing connector/authorization; blocked or unauthorized
  stage, stale SHA, permission, license, identity or branch/path collision.
  **No writes attempted.**

Remote checks are best effort, not transactional or cryptographic.
The mock `authorize` and `FakeGithub` in unit tests **do not evidence a real
operator decision, a deployed connector, or a real contribution**. They
validate the local stage boundary and failure semantics only.

## Activation gate remains closed

No live pilot is authorized by merging these source files. Before using this
for one real external project, an operator must explicitly select the
**candidate, exact `prepare_contribution` action, working fork, branch,
target new file and content**, and a trusted current-session host must
provide the actual authorization and GitHub port. Confirm upstream's
contribution policy/licensing, confirm the existing fork belongs to the
connected writer and inspect the actual bytes/tests beforehand.

This adapter does **not** implement `create_public_fork` (that provider
operation is currently unavailable in the connected GitHub tools) or
`submit_external_pr`. Neither stage may be silently substituted with a PAT,
manual workflow dispatch, third-party website or the old helper. No S1
organizational admission or autonomy grade follows.

Run local tests:

```bash
python3 -m unittest discover -s tests -v
```

CI is wired to both this module and its contract tests, using
`permissions: contents: read` and no write secrets.
