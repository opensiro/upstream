# Automatic fork executor — recovery of the existing REST route

**Status:** DESIGN / READ-ONLY READINESS ONLY. **No fork execution is activated.**
**Owner:** [Upstream #28](https://github.com/opensiro/upstream/issues/28), under [#6](https://github.com/opensiro/upstream/issues/6).  
**Operator surface:** existing [OpenSiro OSS Control Plane](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/AGENT_CONTROL_PLANE.md).

## Decision: do not require a custom ChatGPT MCP plugin

The GitHub **fork API operation and a source-prepared REST client already exist** in this repository. The currently connected ChatGPT GitHub action set lacks a *native create-fork tool*, but that limitation is **not equivalent** to "OpenSiro cannot automate forks".

The owner can choose either independently reviewed execution transport:

1. **Protected Upstream GitHub Actions / GitHub REST executor** (preferred recovery candidate): adapt the existing `scripts/create_fork.py` transport to a **new batch-scoped, fail-closed executor** invoked only after a trustworthy Control Plane approval/authority record. The historical `workflow_dispatch` create job **must not be restored** and an unsigned `approved_by` or an unprotected workflow input is never approval. GitHub App installation credentials *may* be an option if exact creation and source permissions can be verified; the existence of an installed app alone proves neither.
2. **Native connected provider method**: a host-owned `create_public_fork` operation and genuine host `authorize(intent)`, using the existing `scripts/connected_fork_adapter.py`. This is an alternative, **not a prerequisite** for the Actions/REST transport, and it is not currently available in the connected action set.

**Neither transport is activated.** Do not build a second Control Plane, permanent bot, arbitrary-scope write interface or generic scheduled runner. Do not require a personal fork or a new custom MCP plugin as the default workaround.

## Existing reviewed assets and their actual states

| Artifact | Evidence and boundary |
| --- | --- |
| [PR #5](https://github.com/opensiro/upstream/pull/5) | Merged source client and initially manual GitHub Actions design; **never live-activated by that PR**. |
| [`scripts/create_fork.py`](../scripts/create_fork.py) | Standard-library REST `POST /repos/{source}/forks` with fixed `opensiro-contributions`, `organization`, fork name and `default_branch_only`. Dry-run and a legacy token-based execute path remain in source, but **no deployed privileged workflow calls it**. Reusing this HTTP implementation does **not** authorize its legacy `--execute` path. |
| [PR #8](https://github.com/opensiro/upstream/pull/8) | Merged safety rollback. The deployed [`fork-lifecycle.yml`](../.github/workflows/fork-lifecycle.yml) is **preview-only** and has no `execute`, `--execute`, `UPSTREAM_FORK_TOKEN`, privileged job or write token. Preserve that invariant. |
| [PR #7](https://github.com/opensiro/upstream/pull/7) | Closed unmerged draft of earlier conversation-first batch authorization; read-only selection was incorporated separately in [PR #9](https://github.com/opensiro/upstream/pull/9). No approved-batch executor exists. |
| [PRs #30–32](https://github.com/opensiro/upstream/pull/30) | Merged **source-only** `connected_fork_adapter.py`, explicit nondefault branch/SHA verification, post-consent action+manifest revalidation, offline mocked tests. They do not provide an authenticated fork-capable host. |
| [`scripts/batch_proposals.py`](../scripts/batch_proposals.py) | Offline `proposal_only` manifest with stage scopes and digests. The digest is a proposal identifier, **not** a signature or proof of approval. |
| GitHub app installation inventory, checked 2026-10-19 | GitHub connector listed an installation for account `opensiro-contributions` (installation ID `172538419`, repository_selection=`all`). Its repository list returned zero visible repositories. **Neither result proves fork-create rights, app permissions, authentication of an approver, or access to a third-party source.** This is a time-stamped observation, not durable authority. |

## Bounded transaction: assessment-derived contribution → verified working fork

```text
Index assessment @ immutable commit + upstream-native issue/fit
  → Upstream proposal_only candidate, source and stage-scope digests
  → Control Plane displays exact candidate, operation, source and destination
  → real operator authorization (once per exact selected batch/scope)
  → trusted executor verifies attributable identity, grant and permitted stages
  → fresh source/license/policy / fork destination / ref checks
  → create_public_fork only for selected candidate(s), one call each
  → independent GitHub readback and per-item status/partial receipt
  → later separately authorized prepare_contribution
  → complete unpublished external PR package
  → operator owns external PR publication; upstream maintainer owns acceptance
```

For any **deferred Actions executor**, a normal chat reply does not automatically become an authenticated GitHub Actions event. A trusted bridge must create and bind a verifiable short-lived authorization artifact (e.g. host-authenticated one-use decision reference with exact digest), and the runner must check it **independently at execution time**. An issue comment, `workflow_dispatch` input, JSON `approved_by`, model-authored assertion, CI success, or a digest by itself is insufficient. If no such bridge exists, **stop at source preparation** instead of inventing a token/approval.

### Minimum verifier contract before a write

- **Authority:** independently attest actual authenticated actor, legitimate owner of the destination/org operation, intended execution identity, selected candidate IDs, exact `create_public_fork` stage, approved manifest and selection digests, expiry, revocation and replay restrictions. A batch may authorize multiple bounded forks but **not** other stages.
- **Provider and token:** independently verify GitHub API transport, organization creation rights and source-repository forking policy; if using a GitHub App installation token or scoped credentials, prove the actual applicable permissions and source/destination installation coverage first. Organization installation visibility or `repository_selection=all` is not a verified permission claim. Do not require permanent PAT storage in chat.
- **Input limits:** fixed `opensiro-contributions`, public eligible sources, current source/issue/license/policy, no duplicate intervention or unexpected existing destination. Revalidate digests and ref after the decision; detect conflict and changed scope.
- **Branch:** for [HarnessDesk #1772](../pilots/harnessdesk-1772/README.md), integration target is `development`, not default `main`. Bind exact source `development` SHA and `default_branch_only=false` / all-branches copy where the provider supports it. The old REST client's parent-only verification is **insufficient**: verify the fork has `development` at that exact SHA and connected actor push rights, or do not report `CREATED_VERIFIED`.
- **Execution:** single GitHub create attempt per authorized item. A provider HTTP 202 is `PENDING_VERIFICATION` until readback; no unsafe auto-retry after unknown partial results. Record exact refs, branch, observed permissions, operation actor and failure category. Forking does not authorize external PR submission.
- **Isolation:** protected `main`, protected workflow/config/manifest authority, no PR-branch code or untrusted manifest controlling a privileged job, no unbounded repo-write permission, exact least-privilege credentials and auditable redacted receipts.

### Recommended next reviewable work

1. **Read-only capability inventory:** assess GitHub App/organization installation permissions and whether GitHub's forks API may operate against an external source under the chosen credentials. Identify a **supported** transport. If the app cannot fork from third-party sources under its current installation scope, record `BLOCKED_PROVIDER`; do not silently use a broad PAT.
2. **Decide the executor + approval bridge:** prefer a bounded Actions/REST adapter reusing the fork client **if** the executor can independently validate the exact current-session or deferred Control Plane approval; otherwise use native connected `create_public_fork` only if it actually becomes available. No extra human GitHub approval click should be required **if** the selected batch already carries genuine enforced authorization.
3. **Implement under a new separately reviewed PR:** create a **new** restricted batch executor and dedicated positive/negative tests. Keep `fork-lifecycle.yml` preview-only until an independently validated guarded transition is approved. Tests: absent/stale/replayed/cross-scope approval, unauthorized organization, missing method, permission 403, changed manifest/SHA, name collision, wrong parent, no working branch, private fork, missing push, 202 pending and partial responses.
4. **First pilot only when gates are live:** freshly qualify HarnessDesk #1772 against its pinned Index assessment, source `development` ref, contribution rules, CLA/license and overlap, then request the operator's exact selected stage/batch approval. The current blocked proposal is **not** executable. Execute one fork and attach provider readback; only after that separately authorize implementation work.

## Acceptance and stop

- **DONE for this document:** recognizes the pre-existing REST implementation as a valid possible automation transport, without incorrectly treating a native ChatGPT connector write method or custom MCP plugin as mandatory.
- **NOT DONE:** trusted approval-to-runner bridge, fork-creation capability/credentials, live organization rights, source branch verified in a new fork, executed external write or S1 operational closure.
- **Stop:** no workflow privilege expansion, legacy `UPSTREAM_FORK_TOKEN` provisioning, real fork, external PR, new Organization S1 admission, or autonomy grade from this documentation.

Related: [Issue #28](https://github.com/opensiro/upstream/issues/28), [Issue #6](https://github.com/opensiro/upstream/issues/6), [Organization #274](https://github.com/opensiro/vsm-oss-organization/issues/274), [legacy lifecycle audit](FORK_LIFECYCLE.md), [fork stage route](OPENSIRO_CONTRIBUTIONS_FORK_ROUTE.md).
