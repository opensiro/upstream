# Fork public preflight — live source evidence without privileged access

**Status:** READ-ONLY CAPABILITY, NOT A FORK APPROVAL OR CREATION EXECUTOR.  
**Owner:** [Upstream #28](https://github.com/opensiro/upstream/issues/28), parent [#6](https://github.com/opensiro/upstream/issues/6).

[`scripts/fork_public_preflight.py`](../scripts/fork_public_preflight.py)
performs a real, anonymous **GET-only** GitHub API observation before a
proposed fork. The existing
[`fork-lifecycle.yml`](../.github/workflows/fork-lifecycle.yml)
remains a manual **preview-only** workflow (`contents:read`, checkout
from `main`, no secret, no privileged job, no POST, no `--execute`).

## Example

```bash
python3 scripts/fork_public_preflight.py \
  --source HarnessDesk/HarnessDesk \
  --fork-name HarnessDesk \
  --working-branch development \
  --all-branches \
  --expected-license MIT \
  --expected-sha '<40-character-current-development-commit>'
```

The expected SHA must come from a **current external source observation**,
not a durable project assumption. Use a real 40-character lowercase SHA,
not the placeholder above. If it is omitted, the script will report the
current observed SHA but return a blocked/unpinned status; it will never
quietly convert an observation into approval. A missing expected SPDX also
blocks completeness.

The tool checks, and emits machine-readable evidence for:

- exact public source identity, public/non-archived/non-disabled status and
  explicit `forking_allowed` denial when present;
- observed SPDX string vs separately provided expected value;
- exact selected source branch and 40-hex SHA vs supplied SHA, including
  nondefault branch/copy-mode compatibility;
- whether `opensiro-contributions/<name>` is publicly visible and already
  occupies the destination;
- distinction between a public GET 404 and 401/403/429: permission failures
  are **not** interpreted as absence;
- fixed `NOT_APPROVED_NO_WRITES` and
  `NOT_TESTED_NO_CREDENTIALS` authority/permission fields.

Passing public observations yields only
`PUBLIC_PREFLIGHT_OK_NOT_AUTHORIZED` — **NOT** `CREATED_VERIFIED`,
not verified organization creation rights, not a trusted ChatGPT/Control
Plane permission, and not a new-fork receipt. An anonymous public 404 is
not proof that a private/colliding destination does not exist. License
observations are not a substitute for contribution-policy and CLA review.

Missing/changed SHA, unsuitable source/branch, mismatched SPDX, publicly
occupied destination or API failure is a **blocked or unknown** status.
The **public preflight CLI** intentionally lacks any `--execute` command,
credential, POST or fallback privilege escalation. A separate,
[credential-owning VM/host CLI route](CLI_FORK_HOST.md) may use a PAT already
provisioned on that host, but has not been authorized or activated by this
public preflight.

## Provider/authentication boundary

For a real fork, the currently merged source chain still needs an
authenticated, least-privilege protected REST execution host and a trusted
exact-batch operator authorization mechanism. [REST fork port](REST_FORK_PORT.md)
and [batch host gate](BATCH_FORK_HOST_GATE.md) are source-level,
offline-tested components, not an activated runner. GitHub's
[Create a fork API](https://docs.github.com/en/rest/repos/forks) documents
the source-and-destination installation coverage needed for GitHub Apps.

The canonical candidate
[`pilots/harnessdesk-1772/`](../pilots/harnessdesk-1772/)
is still `prepare_contribution`-only with explicit blockers;
a clean public preflight does **not** add a `create_public_fork` stage or
override its existing source/proposal constraints.

The operator retains publication of any third-party PR; this preflight
has no ability to publish, archive, change the registry or admit another
bounded Organization S1 function.
