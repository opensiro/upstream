"""Read-only proposal → local P1 scope → GitHub preflight composition.

This deliberately lacks create_branch/create_file and any execution entry point.
It requires both a trusted grant host and connected read-only provider surface.
Its success result is never authority to mutate a repository.
"""
import hashlib

from batch_proposals import BatchError, preview_draft
from connected_stage_adapter import STAGE, StageBlocked, _preflight, _validate_action
from osm_p1_scope import MandateBlocked, preview_p1_scope


class PipelineBlocked(Exception):
    """Fail closed, preserving the governing missing condition."""


def preview_p1_pipeline(*, manifest, candidate_id, action, grant,
                        trusted_host=None, github=None):
    """Inspect a single pre-existing fork without GitHub mutations.

    The returned receipt is an *offline/mockable inspection*, not executable
    authorization. A compatible trusted host must independently attest the
    actual owner/agent, effective grant and revocation. Even with valid
    attestations, the current connected adapter's separate exact-item write
    authorization gate remains unchanged; this function cannot invoke it.
    """
    if trusted_host is None or github is None:
        raise PipelineBlocked("Both trusted grant host and connected GitHub reads are required")
    try:
        _validate_action(action)
        selection = preview_draft(
            manifest, selected_ids=[candidate_id],
            stage_scopes={candidate_id: [STAGE]},
        )
        items = [x for x in selection["candidates"]
                 if x["id"] == candidate_id and x["selected"]]
        if len(items) != 1:
            raise PipelineBlocked("Candidate unavailable in the selected proposal")
        item = items[0]
        if (item["blockers"] or item["selected_stages"] != [STAGE]
                or not item["expected_license"]
                or not item["proposal"]["evidence_url"]):
            raise PipelineBlocked("Candidate is blocked, unreviewed or outside prepare stage")
        if action["working_repo"].split("/")[1].casefold() != item["fork_name"].casefold():
            raise PipelineBlocked("Working fork does not match selected upstream proposal")

        intent = {
            "stage": STAGE,
            "working_repo": action["working_repo"],
            "branch": action["new_branch"],
            "file_paths": [action["file_path"]],
            "external_publication": False,
        }
        scope = preview_p1_scope(grant, intent, trusted_host=trusted_host)
        _preflight(item, action, github)  # provider reads only; no mutation

    except (BatchError, StageBlocked, MandateBlocked) as exc:
        raise PipelineBlocked(str(exc)) from None

    return {
        "status": "PIPELINE_PREVIEW_ONLY_NO_GITHUB_WRITES",
        "candidate_id": candidate_id,
        "stage": STAGE,
        "source": item["source"],
        "working_repo": action["working_repo"],
        "base_sha": action["base_sha"],
        "branch": action["new_branch"],
        "file_path": action["file_path"],
        "content_sha256": hashlib.sha256(action["content"].encode("utf-8")).hexdigest(),
        "proposal_sha256": selection["proposal_sha256"],
        "selection_scope_sha256": selection["selection_scope_sha256"],
        "p1_scope_precheck": scope["status"],
        "grant_digest": scope["grant_digest"],
        "can_execute": False,
    }
