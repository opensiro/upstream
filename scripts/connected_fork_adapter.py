"""Source-prepared fork stage for a trusted same-session Control Plane host.

Neither the GitHub port nor a real host authorization callback is shipped here.
This is NOT a standalone or credential-backed write path.
"""
import re

from batch_proposals import BatchError, preview_draft
from connected_stage_adapter import NotFound, StageBlocked


STAGE = "create_public_fork"
DEST_OWNER = "opensiro-contributions"
SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$")
ACTION_FIELDS = {"destination_owner", "fork_name"}


def _need(ok, message):
    if not ok:
        raise StageBlocked(message)


def _validate(action):
    _need(type(action) is dict and set(action) == ACTION_FIELDS,
          "Invalid fork-stage action shape")
    _need(all(type(action[k]) is str for k in ACTION_FIELDS),
          "Fork-stage fields must be strings")
    _need(action["destination_owner"] == DEST_OWNER,
          "Destination owner outside restricted fork namespace")
    name = action["fork_name"]
    _need(bool(SLUG.fullmatch(name)) and not name.endswith(".")
          and name.casefold() not in (".", ".."), "Invalid fork name")


def _preflight(item, action, github):
    destination = action["destination_owner"] + "/" + action["fork_name"]
    # The trusted host port MUST make a real provider capability/permission
    # observation. An untrusted draft, token, or agent boolean is not enough.
    try:
        capability = github.fork_capability(action["destination_owner"])
    except Exception as exc:
        raise StageBlocked("Fork capability check failed: " + type(exc).__name__) from None
    _need(type(capability) is dict
          and capability.get("available") is True
          and capability.get("authorized") is True
          and capability.get("owner") == action["destination_owner"]
          and type(capability.get("actor")) is str
          and bool(capability["actor"]),
          "No verified provider capability/organization authority")
    try:
        source = github.repo(item["source"])
    except Exception as exc:
        raise StageBlocked("Upstream lookup failed: " + type(exc).__name__) from None
    _need(source.get("full_name", "").casefold() == item["source"].casefold(),
          "Upstream identity changed")
    _need(source.get("private") is False
          and source.get("archived") is False
          and source.get("disabled") is not True
          and source.get("forking_allowed") is not False,
          "Upstream is not a forkable active public repository")
    _need((source.get("license") or {}).get("spdx_id")
          == item["expected_license"], "Upstream SPDX observation changed")
    try:
        github.repo(destination)
    except NotFound:
        return capability["actor"], destination
    except Exception as exc:
        raise StageBlocked("Destination lookup failed: " + type(exc).__name__) from None
    # An existing correctly parented fork is useful but not a NEW fork test.
    _need(False, "Destination is already occupied; no new-fork proof")


def execute_one_public_fork(*, manifest, selected_ids, stage_scopes,
                            candidate_id, action, github=None, authorize=None):
    """Try ONE authorized public-fork stage; never advance to patch or PR.

    Trusted github port methods: fork_capability(owner), repo(full_name),
    create_public_fork(source, owner, name, default_branch_only=True).
    Only a genuine provider 404 may raise NotFound; all other errors fail
    closed. authorize(intent) MUST be a host-attributed same-session decision.
    This code cannot by itself authenticate consent or provide GitHub rights.
    """
    _need(github is not None and callable(authorize),
          "Trusted host authorization and connected GitHub port required")
    _need(all(callable(getattr(github, fn, None)) for fn in
              ("repo", "fork_capability", "create_public_fork")),
          "Connected provider fork methods unavailable")
    _validate(action)
    try:
        preview = preview_draft(manifest, selected_ids=selected_ids,
                                stage_scopes=stage_scopes)
    except BatchError as exc:
        raise StageBlocked("Invalid proposal: " + str(exc)) from None
    matches = [item for item in preview["candidates"]
               if item["id"] == candidate_id and item["selected"]]
    _need(len(matches) == 1, "Fork candidate not selected")
    item = matches[0]
    _need(item["selected_stages"] == [STAGE],
          "This adapter requires fork-only stage selection")
    _need(not item["blockers"] and item["expected_license"]
          not in (None, "UNKNOWN", "NOASSERTION")
          and item["proposal"]["evidence_url"],
          "Blocked or insufficiently reviewed proposal")
    _need(action["fork_name"].casefold() == item["fork_name"].casefold(),
          "Fork name does not match proposal")
    _need(item["source"].split("/")[0].casefold() != DEST_OWNER.casefold(),
          "Source must be external to fork destination")
    actor, destination = _preflight(item, action, github)
    intent = {
        "candidate_id": candidate_id, "stage": STAGE,
        "source": item["source"], "destination": destination,
        "default_branch_only": True,
        "proposal_sha256": preview["proposal_sha256"],
        "selection_scope_sha256": preview["selection_scope_sha256"],
        "connected_actor": actor,
    }
    # A mock callback returning True is only an offline unit-test fixture.
    _need(authorize(dict(intent)) is True,
          "No trustworthy exact-stage operator authorization")
    actor_again, destination_again = _preflight(item, action, github)
    _need((actor_again, destination_again) == (actor, destination),
          "Provider identity or fork destination changed after approval")

    try:
        result = github.create_public_fork(item["source"], DEST_OWNER,
                                           action["fork_name"],
                                           default_branch_only=True)
    except Exception as exc:
        return {**intent, "status": "FAILED", "reason": type(exc).__name__,
                "note": "Write may have partially succeeded; do not retry without a new decision"}
    # A GitHub 202 / accepted response alone is not verification.
    if type(result) is not dict or result.get("accepted") is not True:
        return {**intent, "status": "PENDING_VERIFICATION",
                "note": "Provider did not attest acceptance; read-only investigation required"}
    try:
        observed = github.repo(destination)
    except NotFound:
        return {**intent, "status": "PENDING_VERIFICATION",
                "note": "Fork not yet visible; read-only follow-up, no automatic retry"}
    except Exception as exc:
        return {**intent, "status": "PENDING_VERIFICATION",
                "note": "Readback failed: " + type(exc).__name__}
    verified = (observed.get("full_name", "").casefold() == destination.casefold()
                and observed.get("fork") is True
                and (observed.get("parent") or {}).get("full_name", "").casefold()
                == item["source"].casefold()
                and observed.get("private") is False
                and observed.get("archived") is False
                and (observed.get("permissions") or {}).get("push") is True
                and observed.get("html_url") == "https://github.com/" + destination)
    return {**intent, "status": "CREATED_VERIFIED" if verified
            else "VERIFICATION_FAILED",
            "fork_url": observed.get("html_url") if verified else None,
            "note": None if verified else "Unexpected identity, parent, visibility, or push rights"}