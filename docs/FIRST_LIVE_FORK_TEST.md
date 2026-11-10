# First live fork test — Index-origin Upstream S1

**Status:** SOURCE-PREPARED, **not connected / not authorized**.  
**Owner:** [Upstream #28](https://github.com/opensiro/upstream/issues/28), [Upstream #6](https://github.com/opensiro/upstream/issues/6).  
**Operator interface:** [existing Organization Control Plane](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/AGENT_CONTROL_PLANE.md).

## Purpose

Demonstrate an actual provider-created **new public fork in
`opensiro-contributions`** of a source-qualified, assessment-derived harness
candidate. A verified fork and a prepared change are **separate stages**;
neither an existing fork nor a preview/mock is evidence of a new fork.

## Source-first pilot

The [HarnessDesk #1772 case](../pilots/harnessdesk-1772/README.md) is
assessment-linked and has a concrete native tool-gateway defect. Refresh its
Index SHA, upstream source/policy, current issue/PR overlap and license **before
any decision**. The committed proposal remains intentionally BLOCKED.

HarnessDesk's working integration branch is **`development`**, while its
default branch is **`main`**. Creating only default `main` is insufficient.
The bounded [fork adapter](CONNECTED_FORK_ADAPTER.md) takes an *exact* action:

```python
{
    "destination_owner": "opensiro-contributions",
    "fork_name": "HarnessDesk",
    "working_branch": "development",
    "working_branch_sha": "<verified source development SHA>",
    "default_branch_only": False,
}
```

This packet is an **example action shape, not an approval**. A trusted
provider must actually expose and honor an all-branches create-fork method.
The source `development` SHA is checked before and after the attributable
current-session operator decision.

## Stages and evidence

1. **Discovery:** pin canonical Index assessment and independently prove
   upstream-native need/fit. Fail closed if no suitable unblocked candidate.
2. **Provider preflight:** authenticate connected actor, organization
   `opensiro-contributions` creation permission, exact upstream source,
   license/fork policy, absent name and pinned `development` SHA. Missing
   native fork method ⇒ `BLOCKED_CAPABILITY`, not a personal-fork request.
3. **Human decision:** present exact candidate/manifest digest, source,
   destination, selected stage, target branch/SHA and copy strategy.
   Authentication/attribution is host-owned; `lambda _: True` is a test fake.
4. **One fork call:** only after exact-stage approval and re-preflight.
   An asynchronous API 202 is not verified creation.
5. **Readback:** verify fork identity, upstream parent, public visibility,
   connected actor push permission **and `development` at the exact
   approved SHA**. Missing branch ⇒ `PENDING_VERIFICATION`; wrong SHA ⇒
   `VERIFICATION_FAILED`. Never silently use `main` or retry writes.
6. **Separate prepare:** authorization for a branch, test/patch and later
   external PR are distinct. Human still owns external PR publication and
   external maintainers own acceptance.

## Current blockers

- The ChatGPT-linked GitHub connector exposes no native create-fork action.
- A trusted provider-bound, attributable current-session `authorize(intent)`
  is not wired into a live fork executor.
- The HarnessDesk proposal has unresolved blockers and no verified writable
  new fork; full upstream tests/production fix were not exercised.

Thus current scope is **source preparation and offline unit tests**, with
no external mutation. Do not deploy a PAT, legacy fork command, bot,
GitHub Actions privileged fork job or second Control Plane to fake a pass.
Formal Organization fourth-S1-domain [#274](https://github.com/opensiro/vsm-oss-organization/issues/274)
is a separate S5 decision, still unmade.
