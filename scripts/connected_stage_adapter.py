"""One-file, same-session contribution stage adapter; no token or approval storage.

The caller MUST supply a trusted current-session authorization callback and
an authenticated GitHub connector port. Neither is provided by this module.
This module never turns a draft selection or digest into authorization.
"""
import hashlib
from pathlib import PurePosixPath
import re

from batch_proposals import BatchError, preview_draft


BRANCH = re.compile(r"^opensiro/[a-z0-9][a-z0-9._/-]{0,79}$")
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA = re.compile(r"^[0-9a-f]{40}$")
STAGE = "prepare_contribution"
FIELDS = {"working_repo", "base_branch", "base_sha", "new_branch", "file_path", "content"}


class NotFound(Exception):
    """Provider-specific 404 translated by the trusted connector adapter."""


class StageBlocked(Exception):
    """Preflight failed; do not issue a GitHub write."""


def _need(condition, reason):
    if not condition:
        raise StageBlocked(reason)


def _validate_action(action):
    _need(type(action) is dict and set(action) == FIELDS, "Invalid exact action shape")
    for field in FIELDS:
        _need(type(action[field]) is str, "Action field must be a string: " + field)
    _need(bool(REPO.fullmatch(action["working_repo"])), "Invalid working repository")
    _need(bool(SHA.fullmatch(action["base_sha"])), "Invalid expected base SHA")
    _need(bool(BRANCH.fullmatch(action["new_branch"]))
          and ".." not in action["new_branch"]
          and "//" not in action["new_branch"]
          and not action["new_branch"].endswith(("/", ".", ".lock")),
          "Invalid new branch")
    _need(action["base_branch"] in ("main", "master", "development")
          or bool(BRANCH.fullmatch(action["base_branch"])), "Invalid base branch")
    path = action["file_path"]
    parts = PurePosixPath(path).parts
    in_root_tests = len(parts) >= 2 and parts[0] == "tests"
    # Some upstream monorepos (including HarnessDesk) use package-local
    # singular test/ instead of tests/. Keep both forms inside packages/.
    in_package_tests = (len(parts) >= 4 and parts[0] == "packages"
                        and any(part in ("test", "tests") for part in parts[2:-1]))
    _need(path == str(PurePosixPath(path))
          and (in_root_tests or in_package_tests)
          and all(part not in (".", "..") for part in parts)
          and not any(ch in path for ch in ("\\", ":", "\x00"))
          and len(path) <= 240,
          "First adapter permits one new root tests/ or package-local test(s)/ file only")
    content = action["content"].encode("utf-8")
    _need(1 <= len(content) <= 49152, "Invalid file size")
    _need(action["working_repo"].split("/")[0].casefold() != "opensiro-contributions"
          or action["working_repo"].count("/") == 1, "Invalid destination")


def _missing(fn, *args):
    try:
        return fn(*args), False
    except NotFound:
        return None, True


def _preflight(item, action, github):
    # All reads use the connected account. A 403 must never be treated as a 404.
    source = github.repo(item["source"])
    work = github.repo(action["working_repo"])
    _need(source.get("full_name", "").casefold() == item["source"].casefold(),
          "Source identity mismatch")
    _need(not source.get("private", True) and not source.get("archived", True),
          "Source is not an active public repository")
    _need((source.get("license") or {}).get("spdx_id") == item["expected_license"],
          "Source license observation changed")
    _need(action["working_repo"].split("/")[1].casefold() == item["fork_name"].casefold(),
          "Working fork name differs from selected proposal")
    _need(work.get("full_name", "").casefold() == action["working_repo"].casefold()
          and not work.get("private", True) and not work.get("archived", True),
          "Working repository is not the expected active public repository")
    _need(work.get("fork") is True
          and (work.get("parent") or {}).get("full_name", "").casefold()
          == item["source"].casefold(), "Working repository is not a matching fork")
    _need((work.get("permissions") or {}).get("push") is True,
          "Connected identity has no push permission")
    base = github.branch(action["working_repo"], action["base_branch"])
    _need(base.get("sha") == action["base_sha"], "Base moved since review")
    _, exists = _missing(github.branch, action["working_repo"], action["new_branch"])
    _need(exists, "Target branch already exists")
    _, absent = _missing(github.file, action["working_repo"],
                         action["file_path"], action["base_branch"])
    _need(absent, "Proposed tests file already exists")


def execute_one_test_file(*, manifest, selected_ids, stage_scopes,
                          candidate_id, action, github=None, authorize=None):
    """Apply exactly one new tests/ file after a trusted in-session decision.

    authorize(intent) must be implemented by the trusted conversation host,
    not by the proposal author or a JSON/issue field. This Python file does
    NOT provide a working host authorization integration.
    github implements repo, branch, file, create_branch and create_file.
    """
    if github is None or authorize is None:
        raise StageBlocked("Trusted connector and host authorization are required")
    _validate_action(action)
    try:
        preview = preview_draft(manifest, selected_ids=selected_ids,
                                stage_scopes=stage_scopes)
    except BatchError as exc:
        raise StageBlocked("Invalid source proposal/scope: " + str(exc)) from None
    matches = [item for item in preview["candidates"]
               if item["id"] == candidate_id and item["selected"]]
    _need(len(matches) == 1, "Candidate not selected")
    item = matches[0]
    _need(STAGE in item["selected_stages"], "Stage not selected")
    _need(not item["blockers"] and item["expected_license"] is not None
          and item["proposal"]["evidence_url"], "Candidate is blocked or unreviewed")
    _preflight(item, action, github)

    intent = {
        "candidate_id": candidate_id, "stage": STAGE,
        "source": item["source"],
        "proposal_sha256": preview["proposal_sha256"],
        "selection_scope_sha256": preview["selection_scope_sha256"],
        "working_repo": action["working_repo"],
        "base_branch": action["base_branch"],
        "base_sha": action["base_sha"],
        "new_branch": action["new_branch"],
        "file_path": action["file_path"],
        "content_sha256": hashlib.sha256(action["content"].encode()).hexdigest(),
    }
    # Return False for unavailable, denied, stale, or unverifiable decisions.
    # A local mock returning True is not proof of an actual human decision.
    _need(authorize(dict(intent)) is True, "Operator did not authorize exact action")
    _preflight(item, action, github)  # remote state may have changed during review

    try:
        github.create_branch(action["working_repo"], action["new_branch"],
                             action["base_sha"])
    except Exception as exc:
        return {**intent, "status": "FAILED", "write": "create_branch",
                "reason": type(exc).__name__}
    try:
        result = github.create_file(action["working_repo"], action["file_path"],
                                    action["content"], action["new_branch"])
    except Exception as exc:
        return {**intent, "status": "PARTIAL", "branch_created": True,
                "file_created": False, "reason": type(exc).__name__}
    # This extra read is a real verification, unlike treating an API reply
    # as proof. Never claim atomic rollback across the two writes.
    try:
        saved = github.file(action["working_repo"], action["file_path"],
                            action["new_branch"])
        branch = github.branch(action["working_repo"], action["new_branch"])
        verified = (saved.get("content") == action["content"]
                    and branch.get("sha") == result.get("commit_sha"))
    except Exception:
        verified = False
    return {**intent, "status": "CREATED_VERIFIED" if verified else "PENDING_VERIFICATION",
            "branch_created": True, "file_created": True,
            "commit_sha": result.get("commit_sha")}
