#!/usr/bin/env python3
"""Bounded HarnessDesk preparation: read-only check or ACTIVE-mandate stage.

This is a thin entry for existing components, not a scheduler or new bot.
Never creates external upstream pull requests or updates development refs.
The checked-in mandate is PROPOSED_NOT_ACTIVE: --prepare fails closed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from batch_proposals import preview_draft
from bounded_local_prepare_host import (
    BoundedLocalPrepareHost, CurrentMainMandateReader)
from cli_host_multifile_runtime import (
    GitHubCLIJSONTransport, CleanPublicGitPatchMaterializer)
from cli_host_patch_attestor import GitHubCLIProviderAttestor
from connected_multifile_stage import (
    _preflight, _validate, prepare_exact_two_file_patch)
from connected_stage_adapter import StageBlocked
from rest_multifile_patch_port import GitHubRESTMultifilePatchPort

PILOT = ROOT / "pilots" / "harnessdesk-1772"
CANDIDATE = "harnessdesk-1772"
MANIFEST = PILOT / "upstream-20261020-harnessdesk-1772.json"
PACKET = PILOT / "prepare-v2-20261020-81d5e34-shared.json"
PATCH = PILOT / "tool-gateway-ownership-fix-v2.patch"

def action_from_pilot():
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    need = lambda yes: yes or (_ for _ in ()).throw(
        StageBlocked("Invalid historical V2 pilot evidence"))
    need(packet["status"] == "ACTION_PREPARED_NOT_AUTHORIZED"
         and packet["candidate_id"] == CANDIDATE
         and packet["stage"] == "prepare_contribution"
         and packet["upstream"] == "HarnessDesk/HarnessDesk"
         and packet["fork"] == "opensiro-contributions/HarnessDesk"
         and packet["source_branch"] == packet["fork_base_branch"] == "development")
    patch = PATCH.read_text(encoding="utf-8")
    need(hashlib.sha256(patch.encode("utf-8")).hexdigest() == packet["patch_sha256"])
    action = {
        "working_repo": packet["fork"],
        "source_branch": packet["source_branch"],
        "source_sha": packet["source_sha"],
        "base_branch": packet["fork_base_branch"],
        "base_sha": packet["source_sha"],
        "new_branch": packet["proposed_new_branch"],
        "fork_observed_sha": packet["fork_base_sha"],
        "patch_text": patch,
        "patch_sha256": packet["patch_sha256"],
        "changed_paths": packet["changed_paths"],
        "preimage_sha256": packet["preimage_sha256"],
        "postimage_sha256": packet["postimage_sha256"],
    }
    _validate(action)
    return action

def prepare(*, execute=False, transport=None):
    api = GitHubCLIJSONTransport() if transport is None else transport
    reader = CurrentMainMandateReader(api)
    attestor = GitHubCLIProviderAttestor(
        transport=api, expected_fork="opensiro-contributions/HarnessDesk",
        expected_source="HarnessDesk/HarnessDesk",
        expected_actor="xLagerFeuer")
    port = GitHubRESTMultifilePatchPort(
        api=api, materializer=CleanPublicGitPatchMaterializer(),
        capability_attestor=attestor)
    action = action_from_pilot()
    preview = preview_draft(
        MANIFEST, selected_ids=[CANDIDATE],
        stage_scopes={CANDIDATE: ["prepare_contribution"]})
    selected = [item for item in preview["candidates"]
                if item["id"] == CANDIDATE and item["selected"]]
    if len(selected) != 1 or selected[0]["blockers"]:
        raise StageBlocked("Selected candidate absent or blocked")
    actor = _preflight(selected[0], action, port)
    if not execute:
        try:
            policy = reader()
            policy_status = policy.get("status", "INVALID")
        except StageBlocked:
            policy_status = "UNAVAILABLE"
        return {"status": "READ_ONLY_PREFLIGHT_PASS", "actor": actor,
                "source_sha": action["source_sha"],
                "fork_observed_sha": action["fork_observed_sha"],
                "new_branch": action["new_branch"],
                "mandate_status": policy_status,
                "external_pr_created": False}
    # Never activate from local manifest or --prepare itself: the policy is
    # re-read from the observed/current OWNER REPO main before any stage.
    if reader().get("status") != "ACTIVE":
        raise StageBlocked("NO_ACTIVE_OWNER_APPLIED_LOCAL_MANDATE")
    host = BoundedLocalPrepareHost(mandate_reader=reader)
    return prepare_exact_two_file_patch(
        manifest=MANIFEST, selected_ids=[CANDIDATE],
        stage_scopes={CANDIDATE: ["prepare_contribution"]},
        candidate_id=CANDIDATE, action=action,
        github=port, host=host)

def main():
    cli = argparse.ArgumentParser(description=__doc__)
    group = cli.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="GET-only remote preflight")
    group.add_argument("--prepare", action="store_true", help="write only under ACTIVE owner-applied mandate")
    args = cli.parse_args()
    try:
        result = prepare(execute=args.prepare)
    except StageBlocked as exc:
        print(json.dumps({"status": "BLOCKED_NO_WRITE", "reason": str(exc)}))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
