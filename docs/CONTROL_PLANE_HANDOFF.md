# Control Plane → Upstream: exact prepare-stage handoff

**Current status: read-only preparation implemented; execution NOT activated.**

The existing [OpenSiro OSS Control Plane](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/AGENT_CONTROL_PLANE.md)
is the human-facing conversation. This repository is the *owner* of the
contribution proposal, technical handoff and stage implementation.

This is **not a separate bot, scheduler or UI**. It creates neither a fourth
admitted S1 domain nor an Upstream-hosted runtime. Organization [#274](https://github.com/opensiro/vsm-oss-organization/issues/274)
remains a separate S5 boundary decision.

The [OSM autonomy-transfer design](OSM_DELEGATION_DESIGN.md) proposes **future standing local decision rights** and human-owned external PR publication. It is not an authorization source: this handoff's current exact-stage consent, host/connector, source preflight and no-write fail-closed contract remain operative until a distinct authorized grant and implementation replace them.

## Assessment-driven S1 test versus generic preparation

For `test S1 function: upstream contributions`, the Control Plane must first
follow the [assessment-driven test contract](ASSESSMENT_DRIVEN_S1_TEST.md):
**pinned Index harness assessment → concrete finding → independently verified
upstream-native need/fit → scoped proposal**. No prior Cognee fork or unrelated
GitHub issue may bypass that intake. Preserve Index provenance separately from
`proposal.evidence_url`. A rejected finding or no suitable assessment-derived
candidate closes the discovery test without selecting another target.

The generic `contribute to other harnesses` and explicitly targeted
`prepare upstream contribution <source/issue>` routes remain available
independently; neither counts as an assessment-driven S1 test by itself. This
handoff still requires exact operator decision and trusted connected rights
before every real write. It does **not** enforce the Index-evidence test gate
in Python or grant any rights by merely providing a document link.

## End-to-end operator flow (bounded)

1. **Discover** via `contribute to other harnesses`. Refresh the external
   source repository, concrete maintainer signal, default-branch source,
   contribution policy and overlapping PRs. An Index gap is not enough.
2. **Propose** an Upstream `proposal_only` draft with a real evidence link.
   Display candidate IDs, blockers and possible stages using
   [`batch_proposals.py`](../scripts/batch_proposals.py).
3. **Prepare** an exact read-only packet for **one candidate and the
   `prepare_contribution` stage only** via
   [`control_plane_handoff.py`](../scripts/control_plane_handoff.py).
   The packet says `ACTION_PREPARED_NOT_AUTHORIZED`, binds the proposed
   revision/selection digests and the exact working repository, source branch
   SHA, new branch, root `tests/` or package-local `packages/.../test(s)/` path and test-content SHA-256.
4. **Operator decision:** the conversation presents the precise packet and
   asks for a separate explicit **approve or decline** decision on that exact
   action. A generic `continue`, `подтверждаю`, draft JSON field, hash,
   GitHub issue comment or tool token is **not** action-specific consent.
   The packet itself cannot identify the human or authenticate a chat.
5. **Only with verified current-session authorization and connected rights:**
   a trusted host supplies both `authorize(intent)` and the authenticated
   GitHub provider port to
   [`connected_stage_adapter.py`](../scripts/connected_stage_adapter.py).
   Recheck exact draft, source, fork ancestry, push rights, contribution
   policy/licensing, branch SHA, absence of branch/test file and stage scope
   before *each* write. If a host cannot establish the operator's exact
   decision, do not substitute a source-code `authorize=lambda _: True`.
6. **Return:** `CREATED_VERIFIED`, `PENDING_VERIFICATION`, `PARTIAL`,
   `FAILED` or `BLOCKED` plus actual GitHub refs and remaining work.
   Never turn a test-file commit into an external PR, external upstream merge,
   autonomy grade, new S1 domain, or observed product improvement.
   `create_public_fork` and `submit_external_pr` are **not implemented**
   in this adapter.

## Preview command (no GitHub calls)

Given a **local** Upstream proposal-only manifest `upstream-YYYYMMDD-slug.json`
and an already prepared UTF-8 test file:

```bash
python3 scripts/control_plane_handoff.py \
  --manifest /path/to/upstream-YYYYMMDD-slug.json \
  --candidate candidate-id \
  --working-repo contributor/fork-name \
  --base-branch main \
  --base-sha 0123456789012345678901234567890123456789 \
  --new-branch opensiro/candidate-id-tests \
  --file-path tests/test_candidate.py \
  --content-file /path/to/test_candidate.py
```

This validates *local* consistency; it does **not** verify real fork
ownership, license compatibility, source policy, actual repository existence,
authentic human consent or the right to push.

Output is a single JSON `UPSTREAM_PREPARATION_HANDOFF` packet. It contains a
SHA-256 digest and byte length, **not** the test-file bytes, access tokens or
approval evidence. The host must re-read the proposed exact bytes and validate
their digest before any stage execution; otherwise stop.

## Mandatory stop conditions

A selected blocked candidate, revised proposal, changed content digest,
stale source branch, missing exact operator decision, unverified external
policy, absent fork, mismatched parent, disallowed branch/path, denied push
permission, unavailable connector operation, readback mismatch or any partial
write must remain **blocked/unknown/partial** as appropriate. Do not
interpret successful mock tests, CI, unsigned hashes, or a connected GitHub
session as user authorization.

**Minimal next pilot:** choose one real source and *already existing* writable
fork; prepare one test file and show its exact packet in the conversation.
Until the user authorizes that exact action and the host can enforce the
rights, **make no external writes**.

The test fixture is intentionally synthetic and is not a permission to write.
