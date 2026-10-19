"""Batch-scoped fork-stage orchestration for a TRUSTED host (source only).

No credentials, GitHub connector, approval issuer or executable CLI shipped.
An untrusted caller can fake Python ports, so a deployment MUST enforce host
identity/approval and bound GitHub credentials OUTSIDE this library. This file
is not an activated runner and is never called by GitHub Actions.
"""
from copy import deepcopy

from batch_proposals import BatchError, preview_draft
from connected_fork_adapter import (_preflight, _validate,
                                    execute_one_public_fork, StageBlocked)

STAGE = "create_public_fork"
MAX_BATCH = 10
PORT_METHODS = ("repo", "branch", "fork_capability", "create_public_fork")
HOST_METHODS = ("verify_exact_batch", "authorize_exact_stage")


def _need(condition, reason):
    if not condition:
        raise StageBlocked(reason)


def _preview(manifest, selected_ids, stage_scopes):
    try:
        return preview_draft(manifest, selected_ids=selected_ids,
                             stage_scopes=stage_scopes)
    except BatchError as exc:
        raise StageBlocked("Invalid selected batch: " + str(exc)) from None


def execute_one_verified_fork_batch(*, manifest, selected_ids, stage_scopes,
                                    actions, github=None, host=None):
    """Execute at most 10 explicitly selected fork stages through TRUSTED ports.

    This module cannot authenticate Python caller identity or the true human.
    The connected host must attest the operator's exact batch selection in
    verify_exact_batch(intent) and enforce a one-use bound grant in
    authorize_exact_stage(grant, batch_intent, per_item_intent).
    Passing mock objects is legal only in tests, never proof of permission.
    """
    _need(github is not None and host is not None,
          "Trusted provider and independently authenticated host are required")
    _need(all(callable(getattr(github, n, None)) for n in PORT_METHODS),
          "Connected fork-capable GitHub port unavailable")
    _need(all(callable(getattr(host, n, None)) for n in HOST_METHODS),
          "Trusted batch/stage authorization methods unavailable")
    _need(type(selected_ids) is list and 1 <= len(selected_ids) <= MAX_BATCH,
          "Select one to ten exact candidate IDs")
    _need(type(stage_scopes) is dict and type(actions) is dict
          and set(stage_scopes) == set(selected_ids)
          and set(actions) == set(selected_ids),
          "Every selected candidate requires exactly one action and stage scope")

    selected = list(selected_ids)
    scopes = deepcopy(stage_scopes)
    frozen_actions = deepcopy(actions)
    preview = _preview(manifest, selected, scopes)
    _need(not preview["selection_has_blockers"],
          "Selected batch has unresolved proposal blockers")
    rows = {c["id"]: c for c in preview["candidates"] if c["selected"]}
    _need(len(rows) == len(selected), "Candidate selection mismatch")
    destinations = set()
    actors = set()
    entries = []

    for candidate_id in selected:
        item = rows[candidate_id]
        action = frozen_actions[candidate_id]
        _validate(action)
        _need(item["selected_stages"] == [STAGE],
              "Only explicit fork-only stages are admitted in this executor")
        _need(item["expected_license"] not in (None, "UNKNOWN", "NOASSERTION")
              and item["proposal"]["evidence_url"],
              "Unreviewed source/license/evidence is not executable")
        _need(action["fork_name"].casefold() == item["fork_name"].casefold(),
              "Destination fork name does not match the proposal")
        destination = action["destination_owner"] + "/" + action["fork_name"]
        _need(destination.casefold() not in destinations,
              "Duplicate destination inside authorized batch")
        destinations.add(destination.casefold())
        actor, observed_dest = _preflight(item, action, github)
        _need(observed_dest == destination, "Unexpected destination")
        actors.add(actor)
        child_preview = _preview(
            manifest, [candidate_id], {candidate_id: [STAGE]})
        _need(child_preview["proposal_sha256"] == preview["proposal_sha256"],
              "Per-stage proposal changed during batch preflight")
        entries.append({
            "candidate_id": candidate_id,
            "stage": STAGE, "source": item["source"],
            "destination": destination, "action": deepcopy(action),
            "stage_scope_sha256": child_preview["selection_scope_sha256"],
        })
    _need(len(actors) == 1, "Batch cannot mix GitHub execution actors")

    batch_intent = {
        "batch_id": preview["batch_id"],
        "revision": preview["revision"],
        "proposal_sha256": preview["proposal_sha256"],
        "selection_scope_sha256": preview["selection_scope_sha256"],
        "connected_actor": next(iter(actors)),
        "selected_stages": deepcopy(entries),
    }
    # The host must authenticate real operator decision and bind the exact
    # intent to an expiring, revocable, replay-protected execution grant.
    # A mock object in unit tests is NOT an effective approval.
    grant = host.verify_exact_batch(deepcopy(batch_intent))
    _need(grant is not None and type(grant) not in (bool, str, dict, int),
          "No trustworthy host-issued batch grant")

    _need(selected_ids == selected and stage_scopes == scopes
          and actions == frozen_actions,
          "Selected batch or fork actions mutated during authorization")
    again = _preview(manifest, selected, scopes)
    _need(again["proposal_sha256"] == preview["proposal_sha256"]
          and again["selection_scope_sha256"] == preview["selection_scope_sha256"],
          "Proposal or stage scopes changed during authorization")
    # Any blocked/stale or partial item stops all later selected writes.
    receipts = []
    for entry in entries:
        candidate_id = entry["candidate_id"]
        action = entry["action"]
        def authorize_stage(stage_intent):
            _need(stage_intent.get("source") == entry["source"]
                  and stage_intent.get("destination") == entry["destination"]
                  and stage_intent.get("stage") == STAGE
                  and stage_intent.get("candidate_id") == candidate_id
                  and stage_intent.get("connected_actor") == batch_intent["connected_actor"]
                  and stage_intent.get("proposal_sha256") == batch_intent["proposal_sha256"]
                  and stage_intent.get("selection_scope_sha256") == entry["stage_scope_sha256"]
                  and stage_intent.get("working_branch") == action["working_branch"]
                  and stage_intent.get("working_branch_sha") == action["working_branch_sha"]
                  and stage_intent.get("default_branch_only") is action["default_branch_only"],
                  "Per-item stage intent is outside the approved batch")
            return host.authorize_exact_stage(grant, deepcopy(batch_intent),
                                              deepcopy(stage_intent)) is True
        try:
            result = execute_one_public_fork(
                manifest=manifest, selected_ids=[candidate_id],
                stage_scopes={candidate_id: [STAGE]},
                candidate_id=candidate_id, action=deepcopy(action),
                github=github, authorize=authorize_stage,
            )
        except StageBlocked as exc:
            receipts.append({"candidate_id": candidate_id, "status": "BLOCKED",
                             "reason": str(exc)})
            break
        receipt = {"candidate_id": candidate_id, **result}
        receipts.append(receipt)
        if receipt["status"] != "CREATED_VERIFIED":
            # Partial success is not a reason to advance or retry.
            break

    return {
        "status": "BATCH_VERIFIED" if (len(receipts) == len(entries) and
                all(r["status"] == "CREATED_VERIFIED" for r in receipts))
                else "BATCH_STOPPED",
        "batch_id": batch_intent["batch_id"],
        "proposal_sha256": batch_intent["proposal_sha256"],
        "selection_scope_sha256": batch_intent["selection_scope_sha256"],
        "selected_count": len(entries),
        "processed_count": len(receipts),
        "receipts": receipts,
        "note": "Offline-tested orchestration, not a trusted host integration",
    }
