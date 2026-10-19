# GitHub REST fork transport — source-only host port

**Status:** `SOURCE_PREPARED / NO LIVE HOST / NO CREDENTIALS / NO PUBLIC FORK CREATED`.  
**Owner:** [Upstream #28](https://github.com/opensiro/upstream/issues/28), parent [#6](https://github.com/opensiro/upstream/issues/6).

[`scripts/rest_fork_port.py`](../scripts/rest_fork_port.py) is a constrained
GitHub REST implementation of the `github` methods expected by
[`scripts/batch_fork_executor.py`](../scripts/batch_fork_executor.py)
and `connected_fork_adapter.py`.

It deliberately **does not read tokens** or supply a real `authorize` host.
Its constructor accepts two dependency-injected **trusted host** callables:

- `api(method, path, body=...)` — the authenticating HTTP client, returning
  `(HTTP status, JSON)`. It must own GitHub identity and credentials and
  never expose them in a PR, issue, manifest or log.
- `capability_attestor("opensiro-contributions")` — a *provider-derived*
  verified actor + actual destination/source creation rights mapping, not
  a hard-coded `available=True` or untrusted user setting. Python cannot
  verify the caller's trust boundary; the deployed host must enforce it.

The port supports only `repo(full_name)`, `branch(full_name, name)`,
`fork_capability(owner)` and `create_public_fork(source, owner, name,
default_branch_only=boolean)`. It fixes destination `opensiro-contributions`,
uses GitHub REST `POST /repos/{owner}/{repo}/forks` and returns
`accepted=True` only for HTTP 202 with the expected response owner/name.
Readback of the new fork parent, public status, push rights and **required
working branch at pinned SHA** belongs to the existing connected adapter.
A 202 response on its own **is not verified creation**.

401/403 errors are denied permissions, **never** treated as an absent
destination. Genuine GET 404 yields `NotFound`. Collision/validation
errors and malformed responses fail closed; a stage that has attempted a
POST must **not** automatically retry, even if that POST raised.

## External GitHub API requirement (verified 2026-10-20)

[GitHub's Create a fork REST reference](https://docs.github.com/en/rest/repos/forks)
currently states two alternative permission sets for fine-grained
tokens: `Contents:read` + `Repository creation:write`, or
`Contents:read` + `Administration:write`. For GitHub Apps,
the app must be installed on the **destination account with all repository
access**, and on the **source account with source repository access**.
See also [GitHub's 2026-10-13 permission update](https://github.blog/changelog/2026-10-13-github-app-improvements-for-least-privilege-and-management/).

Current linked GitHub installation inventory shows an app installation for
`opensiro-contributions` with `repository_selection=all`, **but does not
prove effective `repository_creation:write` or read access to an
external source installation**. No installation for `HarnessDesk` was
observed in the accessible inventory, so the GitHub App route **has not
demonstrated the source-side requirement** for the HarnessDesk pilot.
Do not claim that an installed destination app suffices.

No native `create_public_fork` action is exposed by the existing ChatGPT
GitHub integration. A separately protected Actions/REST executor remains
possible, but the authenticated *operator batch authorization → runner*
bridge, credential isolation and replay/revocation enforcement remain
unimplemented. Do not restore the legacy manual
[`fork-lifecycle.yml`](../.github/workflows/fork-lifecycle.yml)
`--execute` path or provision `UPSTREAM_FORK_TOKEN`.

## Offline tests

[`tests/test_rest_fork_port.py`](../tests/test_rest_fork_port.py)
checks GET 200/404/403 differentiation, correct REST POST parameters,
owner restrictions, default-only versus nondefault-branch behavior,
malformed SHA/ref rejection, single POST on error, false identity, 202
acknowledgement and fake-host batch integration. No network, credentials
or real fork are involved.

## Production activation stop

Until the **effective** trusted host and narrow credentials are verified,
this source module is inert. The [HarnessDesk proposal](../pilots/harnessdesk-1772/)
remains blocked and does **not** authorize fork creation. A first real
run must refresh Index source, external issue/policy/license,
`development` SHA, destination absence, operator-selected stage/digests,
then one authenticated POST followed by independent actual readback.
External upstream PR publication remains human-owned.
