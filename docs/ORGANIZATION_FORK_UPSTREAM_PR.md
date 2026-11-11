# Organization forks → external upstream pull requests (VM/host)

**Owner:** [Upstream #6](https://github.com/opensiro/upstream/issues/6);
fork credential/creation evidence: [#28](https://github.com/opensiro/upstream/issues/28).
**Status:** external fork creation **ONE_OFF_FORK_VERIFIED** in
`opensiro-contributions`; PR **READ-ONLY HANDOFF IMPLEMENTED**; external
PR publication **NOT EXECUTED** as of this historical handoff. Since
2026-10-23, exactly 34 frozen Corrective cases had a separate
[owner-approved finite publication mandate](CORRECTIVE_PR_PUBLICATION.md),
subsequently amended to prefer Ready for review. The 2026-11-09 per-PR approval
rule was superseded on 2026-11-11 by the [standing publication mandate](STANDING_EXTERNAL_PR_PUBLICATION.md).
No additional Control
Plane or background agent is installed.

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

### Fork-local proposal ownership

After a verified, authorized `opensiro/...` contribution branch is ready,
record its prospective external PR title/body in a normal Pull Request from
that branch to the **matching contributor fork's default branch**. That
fork-local PR is the canonical proposal; it is not an external publication
or a merge request to accept into fork `main`. It retains the current
source-native template and [current disclosure v3](AI_ASSISTED_PR_DISCLOSURE.md).
Publish only the exact human-approved title/body and checked head to the
third-party repository after the normal permission gate. See
[fork-local proposal contract](CONTINUOUS_WORKING_FORK_PIPELINE.md#fork-local-pr-proposal-contract).

### Source-native PR form and contributor requirements

The **target upstream repository owns the shape of its PR**. Before drafting,
requesting owner approval, or submitting *any* external PR (including a Draft
PR and an already-authorized finite-cohort case):

1. **Read current primary sources at the actual target base/ref.** Inspect
   `.github/PULL_REQUEST_TEMPLATE.md`, `.github/pull_request_template.md`,
   `PULL_REQUEST_TEMPLATE.md`, `pull_request_template.md`,
   `docs/PULL_REQUEST_TEMPLATE.md` and relevant
   `.github/PULL_REQUEST_TEMPLATE/` variants, including filename, path
   and content SHA. Check `CONTRIBUTING.md`, contribution/PR guidelines,
   `CODEOWNERS` when applicable, and documented CLA/DCO, tests, security and
   issue-linking requirements. A missing root template alone does **not** prove
   the repository has no template; inspect its tree or equivalent inventory.
2. **Select the original appropriate template.** If several templates apply,
   use the one matching the proposed bug/fix/feature; if selection is
   ambiguous, stop for clarification rather than inventing a universal form.
   If no applicable template exists after inspection, use a concise
   product-native summary, change, evidence and limitations without claiming
   that the repository provided a template.
3. **Preserve the target's requested structure and intent.** Keep applicable
   headings, order, required sections, fields and checkboxes, and answer what
   each field actually asks. Remove instructional HTML comments or optional
   sections only as the original template permits. Do **not** substitute an
   OpenSiro-owned `Summary / Verification` form for a target's `Done /
   Decisions / Open questions / Upgrade` form, for example. Do not mark
   unexecuted tests or unmet checks as completed. Make technical claims
   source-native; OpenSiro provenance can be linked without displacing the
   maintainer's requested content.
4. **Resolve source policy conflicts before publication.** Check the
   contributor's required commands, DCO sign-off, CLA status, documentation,
   licensing, test coverage and external-change scope. If a mandatory target
   requirement cannot be met (including one that conflicts with OpenSiro's
   no-live-model-trial boundary), disclose the conflict and hold the PR for
   an attributable owner decision; never silently skip the requirement or
   manufacture a passing receipt.
5. **Disclose agent-led work without displacing the original template.**
   Append the [OpenSiro AI-assisted PR disclosure](AI_ASSISTED_PR_DISCLOSURE.md)
   verbatim after the target's required sections. The current v2 text states
   that publication is temporarily human-approved while the owner monitors
   pipeline errors; it makes no claim of human technical review. Do not
   describe the present publication as fully autonomous. A future fully
   autonomous mode requires its own effective authorization and disclosure.
6. **Bind the reviewed request to the readback.** Record the exact target
   base SHA, applicable template path and SHA (or verified `NONE`), source
   policy path/ref, draft title/body and known outstanding checks in the
   handoff. Run the normal branch/diff/duplicate-PR preflight again before
   submission. The human's exact-title/body approval applies **after** the
   source-native form has been completed; editing the body afterward requires
   renewed review of the changed request. A template/policy mismatch is
   `PR_BLOCKED_NO_WRITE`, not permission to post a generic draft.

This is a mandatory review/pre-publication rule, **not** a claim that the
existing `upstream_pr_handoff.py` automatically parses or enforces external
repository templates. Its authenticated GET-only checks still enforce the
separate identity/branch/diff boundary; the maintainer must check the
source-native content and evidence before acting on its output.

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

The script returns `PR_PREFLIGHT_READY_NOT_PUBLISHED` with
the **exact draft** REST request only if all checks pass. If the branch does
not exist, its SHA differs, the fork is mismatched/unwritable, a PR already
exists, or the comparison has no file changes, it **fails closed** with
`PR_BLOCKED_NO_WRITE` and a nonzero exit. Its JSON digest is **not**
an authorization token or a signed permit.

The `--body-file` is a **local, transient preflight input** assembled from
the verified contributor-fork diff and current target template. It need not,
and ordinarily should not, be committed as `reports/*-pr-body.md` or
packaged in a documentation-only `opensiro/upstream` PR. Only a real
external publication readback becomes a reviewed PR lifecycle record here.

**Why REST rather than `gh pr create --head ORG:branch`?**
The [GitHub CLI manual](https://cli.github.com/manual/gh_pr_create)
says organization owners are not currently supported by its
`--head user:branch` option. The
[REST Create a pull request endpoint](https://docs.github.com/en/rest/pulls/pulls)
accepts `head=organization:branch` for a cross-repository PR, with
`head_repo` required if both repositories share the same organization
owner. The handoff builds the exact path/payload for these scenarios and
defaults to **Ready for review (`draft=false`)** for a validated, authorized,
source-native-valid contribution. Use `--draft --draft-reason 'specific pending
review condition'` only when source policy permits a concrete outstanding
readiness condition; this is not a way to bypass a mandatory source-policy,
license, CLA/DCO or publication gate. The `draft_request_body` JSON key is
retained for backward compatibility, even when its `draft` value is `false`.

## C. External publication: standing owner decision and case-local checks

For **every new external PR**, the [current standing owner decision](STANDING_EXTERNAL_PR_PUBLICATION.md) replaces individual approval. After independently revalidating **this exact title, body, fork, branch, target base, native tests, contributor policy and observed SHAs**, an authorized publisher can use the credential-owning VM/host:

```bash
jq -er '.status == "PR_PREFLIGHT_READY_NOT_PUBLISHED"' pr-handoff.json
jq -e '.draft_request_body' pr-handoff.json > reviewed-pr-request.json

# WRITE: requires the effective standing publication grant and source-native checks; never called by preflight
gh api --method POST repos/HarnessDesk/HarnessDesk/pulls \
  --input reviewed-pr-request.json
```

No script in this historical handoff executes the write command. For **only**
the 34 cases enumerated in the [finite Corrective queue](../data/corrective-publication/2026-10-23-01.json),
the 2026-10-23 owner decision was the historical publication authorization: the
authorized contribution actor could create the public `opensiro-contributions` fork, push a bounded working
branch and open an external PR without a new per-case vote **under that
historical mandate**. The current general standing grant is separate. For new, fully validated PRs,
prefer Ready for review (`draft: false`); Draft needs a concrete pending
readiness reason. This remains subject to fresh preflight and provider
identity/readback checks. It is **not** a
credential, API capability, bypass of a permission denial, DCO/CLA signature,
right to merge or authorization to contact maintainers outside PR creation.
Future general automation still requires its separate activation; a one-off
fork approval must never be silently reused for unrelated cases.

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
