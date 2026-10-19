# Organization forks → external upstream pull requests (VM/host)

**Owner:** [Upstream #6](https://github.com/opensiro/upstream/issues/6);
fork credential/creation evidence: [#28](https://github.com/opensiro/upstream/issues/28).
**Status:** external fork creation **ONE_OFF_FORK_VERIFIED** in
`opensiro-contributions`; PR **READ-ONLY HANDOFF IMPLEMENTED**; external
PR publication **HUMAN-OWNED / NOT EXECUTED**. No additional Control Plane
or background agent is installed.

## Actual credential and rights evidence (2026-10-20)

On the existing credential-owning VM/host the `gh` identity is
`xLagerFeuer`. Authenticated read-only checks observed:

- `opensiro` membership `admin/active`;
  `opensiro-contributions` membership `admin/active`;
- classic token's reported scopes `gist`, `read:org`, `repo` (the token
  **itself was not disclosed**);
- `HarnessDesk/HarnessDesk` is publicly readable, but the actor does
  **not** have `push` to that upstream repository;
- a real GitHub CLI `gh repo fork HarnessDesk/HarnessDesk --org
  opensiro-contributions --clone=false` created
  [opensiro-contributions/HarnessDesk](https://github.com/opensiro-contributions/HarnessDesk).
  Authenticated readback confirmed the fork is public, its direct parent,
  `permissions.push=true`, and the nondefault source `development`
  branch was copied at the pinned SHA.

**Interpret strictly:** successful fork creation into
`opensiro-contributions` does not constitute a separate live test of new
fork creation into `opensiro`. Administrative org membership and `repo`
scope make that plausible, subject to organization policy and repo settings.
Likewise, GitHub `repo` scope plus write rights in an own fork make PR
submission plausible, **but no real third-party PR has been submitted**.
The classic token is broad and should not be copied to chat or made globally
available to CI. Use the already configured host identity and a
least-privilege credential for long-running service automation.

## A. Organization fork from an existing VM/host

For one separately selected/authorized public source:

```bash
gh api --method GET user --jq .login
gh api --method GET user/memberships/orgs/opensiro --jq '.role + "/" + .state'
gh api --method GET repos/OWNER/REPO --jq '[.full_name,.private,.archived,.default_branch]|@json'
gh repo fork OWNER/REPO --org opensiro --clone=false
gh api --method GET repos/opensiro/REPO \
  --jq '[.full_name,.fork,.private,.parent.full_name,.permissions.push]|@json'
```

The fork command is a **write**. It is displayed as a future operator-owned
step and must **not** be executed automatically just to check PAT scopes.
On every live call, verify absence/collision, source license/policy, exact
branch and SHA, applicable org creation rights, and a concrete operator
decision. `opensiro` and `opensiro-contributions` are **distinct destinations**.
No unrequested duplicate forks should be created.

For nondefault working branches, omit `--default-branch-only`, then
independently verify the required branch in the fork and matching source
SHA. A successful `gh repo fork` exit alone is not a verified receipt.

## B. Preflight for an upstream pull request

The new [`scripts/upstream_pr_handoff.py`](../scripts/upstream_pr_handoff.py)
uses **authenticated GitHub GET requests only**, with the credential
already legitimately available to `gh` on the VM/host. It requires:

- source, active public fork, exact direct parent and authenticated
  `permissions.push=true` for that fork;
- fixed `opensiro/`-namespaced **existing pushed contribution branch**;
  pinned source `base_sha` and fork `head_sha`;
- nonempty GitHub comparison from selected upstream base to qualified
  organization fork head, no existing open matching pull request;
- bounded, explicitly reviewed PR title and body, and an actor identity.

For example, **only after a real contribution branch has been prepared
and independently validated** (replace both SHAs and branch):

```bash
gh api --method GET repos/HarnessDesk/HarnessDesk/branches/development --jq .commit.sha
gh api --method GET repos/opensiro-contributions/HarnessDesk/branches/opensiro/fix-toolgateway-1772 --jq .commit.sha

python3 scripts/upstream_pr_handoff.py \
  --upstream HarnessDesk/HarnessDesk \
  --fork opensiro-contributions/HarnessDesk \
  --base-branch development \
  --base-sha '<observed-upstream-development-SHA>' \
  --head-branch opensiro/fix-toolgateway-1772 \
  --head-sha '<observed-fork-branch-SHA>' \
  --title 'fix: preserve ToolGateway socket ownership' \
  --body-file /path/to/reviewed-pr-body.md > pr-handoff.json
```

The script returns `PR_READY_FOR_MANUAL_REVIEW_NOT_PUBLISHED` with
the **exact draft** REST request only if all checks pass. If the branch does
not exist, its SHA differs, the fork is mismatched/unwritable, a PR already
exists, or the comparison has no file changes, it **fails closed** with
`PR_BLOCKED_NO_WRITE` and a nonzero exit. Its JSON digest is **not**
an authorization token or a signed permit.

**Why REST rather than `gh pr create --head ORG:branch`?**
The [GitHub CLI manual](https://cli.github.com/manual/gh_pr_create)
says organization owners are not currently supported by its
`--head user:branch` option. The
[REST Create a pull request endpoint](https://docs.github.com/en/rest/pulls/pulls)
accepts `head=organization:branch` for a cross-repository PR, with
`head_repo` required if both repositories share the same organization
owner. The handoff builds the exact path/payload for these scenarios and
defaults to `draft=true`.

## C. Separate human-owned external publication

After the operator explicitly approves **this exact title, body, fork,
branch, target base and observed SHAs**, they can re-run preflight and
publish **manually** from the credential-owning VM/host:

```bash
jq -er '.status == "PR_READY_FOR_MANUAL_REVIEW_NOT_PUBLISHED"' pr-handoff.json
jq -e '.draft_request_body' pr-handoff.json > reviewed-pr-request.json

# WRITE: human-owned, NEVER called by preflight or an unattended workflow
gh api --method POST repos/HarnessDesk/HarnessDesk/pulls \
  --input reviewed-pr-request.json
```

No script in this PR executes the write command. A future automated
publication stage needs an independently authenticated, revocable,
one-use Control Plane stage grant and a protected executor, separate from
existing `create_public_fork` and `prepare_contribution` permission.
Submitting external PRs is **currently a human decision**, and a one-off
fork approval must never be silently reused.

## Test state and remaining blockers

Offline tests use a fake `gh api` port and verify exact GET-only
commands, same/different owner namespace, actor, direct fork parent, pinned
SHAs, nonempty diff and existing-PR exclusion. A real read-only execution
on the credential-owning VM can exercise fail-closed behavior without
creating a branch or PR. Do **not** create meaningless external branches or
empty demonstration PRs solely to turn this into a positive live test.

For the existing HarnessDesk #1772 pilot, the canonical source proposal
still lists `prepare_contribution` and unresolved blockers. Its newly
created fork is only **one cleared infrastructure condition**, not a valid
production fix, tested patch, upstream PR publication or a new S1
admission/autonomy grade.
