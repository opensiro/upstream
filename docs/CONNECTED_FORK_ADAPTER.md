# Connected fork-stage adapter (source-prepared; not live)

**Status: SOURCE-PREPARED / OFFLINE MOCK-TESTED / NO TRUSTED HOST OR CONNECTED FORK OPERATION.**

[Issue #6](https://github.com/opensiro/upstream/issues/6) owns the activation gate.
Use [the existing Organization Control Plane](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/AGENT_CONTROL_PLANE.md) for presenting operator decisions; this module does not add another Control Plane, hosted bot, cron job, OAuth flow or PAT. The fork-first pilot contract is [FIRST_LIVE_FORK_TEST.md](FIRST_LIVE_FORK_TEST.md).

## Implementation

[`scripts/connected_fork_adapter.py`](../scripts/connected_fork_adapter.py) exports:

```python
execute_one_public_fork(
    manifest=manifest_file,
    selected_ids=["candidate-id"],
    stage_scopes={"candidate-id": ["create_public_fork"]},
    candidate_id="candidate-id",
    action={"destination_owner": "opensiro-contributions", "fork_name": "repo-name",
            "working_branch": "development", "working_branch_sha": "<exact-source-sha>",
            "default_branch_only": False},
    github=trusted_connected_port,
    authorize=trusted_current_session_authorization,
)
```

The adapter is **not** an executable command and supplies neither `github` nor `authorize`. An agent-authored `approved_by`, `lambda _: True`, a digest, this document, mock tests or a connected token is **not** real authorization.

The strict implementation deliberately accepts **only one `create_public_fork` stage** in the selected scope. It cannot implement or implicitly authorize `prepare_contribution`, `submit_external_pr`, fork archiving, deletion, registry mutations or organizational admission. It fixes the destination namespace to `opensiro-contributions`. The exact action explicitly binds `working_branch`, pinned `working_branch_sha` and `default_branch_only` as a boolean. For a nondefault contribution branch (e.g. HarnessDesk `development`), only a separately approved all-branch fork (`default_branch_only=False`) can qualify. The provider must actually support that option; an unsupported option is `BLOCKED_CAPABILITY`, not permission to fall back to default-only. A live operator decision must bind the specific source, destination, proposed revision/stage scope, identity and stage.

## Required trusted host interfaces (not provided by this repository)

- `github.fork_capability(destination_owner)` returns a **live provider-derived**, trusted mapping: `available=True`, `authorized=True`, `owner` and connected `actor`. An agent-authored permission boolean is not a real gate; host-side enforcement remains mandatory.
- `github.repo(full_name)` returns GitHub repository metadata, or raises `NotFound` for a real provider **404 only**.
- `github.branch(full_name, branch)` returns current immutable SHA from the **real provider** for both the source working branch and the new fork. The source SHA must match the exact intent both **before and after** operator authorization. After fork creation, the matching branch and SHA must be read back; a new default-only `main` fork is never proof that `development` was copied. Translate 401/403, timeouts, rate limits and other errors differently; never treat them as nonexistence.
- `github.create_public_fork(source, owner, name, default_branch_only=<exact-authorized-bool>)` is the **actual provider operation**; returns a normalized `{"accepted": true}` only upon provider acknowledgement. No such operation is currently exposed by the connected GitHub tools used in this project.
- `authorize(intent)` is the trusted authenticated, attributable **current-session human decision**, not a locally fabricated callback. It must reject wrong/stale/expired/revoked/unselected stage or changed scope.

These are host-port requirements, **not** proof that the current client implements them. Never use the legacy standalone token-bearing `create_fork.py --execute` as a substitute.

## Guardrails and receipts

1. Re-read the source/proposal, SPDX observation, selected stage, fixed destination, provider capability/actor and absent target. An existing matching fork is useful for other work but cannot count as a **new-fork** witness. Current contributor and legal policy still require independent human review: an SPDX string alone is insufficient.
2. Ask for exact same-session operator consent via the trusted host. **Freeze the reviewed action**, then reread the proposal-only manifest and selected stage/scope after consent; any changed digest or mutable action field blocks the write. Independently repeat provider source-branch, identity and destination preflight **after** the decision and before the only write. These consistency tests do not themselves authenticate host consent.
3. Invoke the native create-fork operation only once. A provider acceptance result alone yields no success claim; read back the exact full name, upstream parent, public status, actor push permission and canonical public URL.
4. Return `CREATED_VERIFIED` only when fork and **pinned working branch SHA** readback pass. Return `PENDING_VERIFICATION` for an unobservable/asynchronous response; `VERIFICATION_FAILED` for observable mismatch; `FAILED` for provider write error (remote side effects may still have occurred). **No automatic write retry, rollback, claim of merge or promotion to the next stage.**
5. `StageBlocked` is the no-write outcome for unavailable capability, unselected stages, blocked proposals, conflicting destination, mismatched policy/license, missing exact consent or drift. Do not update `registry.yaml` until a real, independently verified fork exists.

## Tests and limits

`python3 -m unittest discover -s tests -p 'test_*.py' -q` includes [mock positive/negative fork-stage checks](../tests/test_connected_fork_adapter.py): blocked/no-capability/no-consent/invalid scopes, permission/policy/name drift, existing/wrong fork, asynchronous or incorrect results, and the absence of implicit prepare/submit authorization.

**Mock success is not a live fork.** A passing local fake-provider test never authenticates a GitHub account, org-create permission or actual source branch contents. A default-only fork of a repository that requires a distinct development branch must not be promoted to ready. The connected provider does not currently have a fork-creation method, and the real trusted host authorization port has not been wired. Live operation remains **BLOCKED_CAPABILITY / BLOCKED_AUTHORIZATION** until both are independently demonstrated, a real candidate is checked and the exact operator decision is provided.

## Current source integration

This adapter is based on Draft PR #18, rebased conceptually on the current protected `main` after the assessment-driven S1 and HarnessDesk pilot work. The new source-only branch-aware preparation is tracked in [Upstream #28](https://github.com/opensiro/upstream/issues/28); **the production GitHub connector fork method and trustworthy user authorization boundary are still absent**. This document does not unblock the existing intentionally blocked [HarnessDesk candidate](../pilots/harnessdesk-1772/README.md).
