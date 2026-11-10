"""Exact TWO-file external fork preparation core; no installed writer or issuer.

A trusted execution HOST supplies an authenticated GitHub patch port and an
authenticated one-use approval issuer. Arbitrary Python mocks are ONLY tests.
This source does not load PATs, run git push, issue approvals or create PRs.
Unlike connected_stage_adapter.py, this permits one existing package source
file plus one NEW package-local test file, with pre/post content fingerprints.
"""
from copy import deepcopy
import hashlib
from pathlib import PurePosixPath
import re

from batch_proposals import BatchError, preview_draft
from connected_stage_adapter import NotFound, StageBlocked

SHA = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")
BRANCH = re.compile(r"^opensiro/[a-z0-9][a-z0-9._/-]{0,79}$")
PATH = re.compile(r"^packages/[a-zA-Z0-9_-]+/(?:src|test)/[a-zA-Z0-9_./-]+\.tsx?$")
DIFF = re.compile(r"^diff --git a/([^\n]+) b/([^\n]+)$", re.M)
STAGE = "prepare_contribution"
FIELDS = {"working_repo", "source_branch", "source_sha", "base_branch",
          "base_sha", "new_branch", "patch_text", "patch_sha256",
          "changed_paths", "preimage_sha256", "postimage_sha256"}
PROVIDER_METHODS = ("repo", "branch", "file", "patch_capability",
                    "publish_patch_commit", "commit")
HOST_METHODS = ("verify_exact_prepare", "authorize_exact_stage")


def need(condition, reason):
    if not condition:
        raise StageBlocked(reason)


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def good_branch(value):
    return (type(value) is str and BRANCH.fullmatch(value) is not None
            and ".." not in value and "//" not in value
            and not value.endswith(("/", ".", ".lock")))


def _validate(action):
    need(type(action) is dict and
         (set(action) == FIELDS or
          set(action) == FIELDS | {"fork_observed_sha"}),
         "Invalid exact multi-file stage action")
    if "fork_observed_sha" in action:
        need(type(action["fork_observed_sha"]) is str
             and SHA.fullmatch(action["fork_observed_sha"]),
             "Observed fork branch SHA must be pinned")
    for key in ("working_repo", "source_branch", "source_sha", "base_branch",
                "base_sha", "new_branch", "patch_text", "patch_sha256"):
        need(type(action[key]) is str, "Invalid string field " + key)
    need(action["working_repo"].startswith("opensiro-contributions/")
         and action["working_repo"].count("/") == 1,
         "Only contributor organization forks are supported")
    need(action["source_branch"] in ("main", "master", "development")
         and action["base_branch"] in ("main", "master", "development"),
         "Unapproved base branch")
    need(SHA.fullmatch(action["source_sha"]) and SHA.fullmatch(action["base_sha"]),
         "Source and working base must be pinned")
    need(action["source_sha"] == action["base_sha"],
         "The fork base must match reviewed current upstream commit")
    need(good_branch(action["new_branch"]), "Invalid new branch")
    need(type(action["changed_paths"]) is list
         and len(action["changed_paths"]) == 2
         and len(set(action["changed_paths"])) == 2,
         "Exactly two distinct changed paths required")
    src = [p for p in action["changed_paths"] if type(p) is str and
           "/src/" in p]
    tests = [p for p in action["changed_paths"] if type(p) is str and
             "/test/" in p]
    need(len(src) == len(tests) == 1,
         "One source file and one new package test file required")
    for path in action["changed_paths"]:
        need(type(path) is str and PATH.fullmatch(path)
             and path == str(PurePosixPath(path))
             and not any(part in (".", "..") for part in path.split("/"))
             and "//" not in path and ".." not in path
             and len(path) <= 200,
             "Path outside controlled production/test scope")
    need(type(action["preimage_sha256"]) is dict
         and set(action["preimage_sha256"]) == set(src)
         and type(action["postimage_sha256"]) is dict
         and set(action["postimage_sha256"]) == set(action["changed_paths"])
         and all(type(v) is str and DIGEST.fullmatch(v)
                 for v in list(action["preimage_sha256"].values())
                 + list(action["postimage_sha256"].values())),
         "Missing bound pre/postimage SHA256")
    patch = action["patch_text"]
    need(0 < len(patch.encode("utf-8")) <= 131072
         and patch.endswith("\n") and "\r" not in patch
         and "\x00" not in patch and patch.startswith("diff --git "),
         "Invalid or oversized textual patch")
    need(DIGEST.fullmatch(action["patch_sha256"])
         and digest(patch) == action["patch_sha256"],
         "Patch digest mismatch")
    pairs = DIFF.findall(patch)
    need(len(pairs) == 2
         and all(a == b for a, b in pairs)
         and set(a for a, _ in pairs) == set(action["changed_paths"]),
         "Patch diff paths differ from exact file scope")
    need(not any(line.startswith(("rename from ", "rename to ",
                                   "copy from ", "copy to ", "deleted file mode ",
                                   "GIT binary patch", "Binary files "))
                 for line in patch.splitlines()),
         "Patch cannot rename, delete, copy or carry binary objects")
    need(patch.count("new file mode ") == 1
         and "new file mode " in patch.split("diff --git a/" + tests[0])[1]
         and "--- /dev/null" in patch.split("diff --git a/" + tests[0])[1],
         "Patch must introduce precisely one test file")


def _observed_file(github, repo, path, branch):
    record = github.file(repo, path, branch)
    need(type(record) is dict and type(record.get("content")) is str,
         "Cannot independently read bound file content")
    return record["content"]


def _preflight(item, action, github):
    source_name = item["source"]
    work_name = action["working_repo"]
    source = github.repo(source_name)
    fork = github.repo(work_name)
    need(type(source) is dict and source.get("full_name", "").casefold() ==
         source_name.casefold()
         and source.get("private") is False
         and source.get("archived") is False
         and (source.get("license") or {}).get("spdx_id") == item["expected_license"],
         "Source identity, visibility or license changed")
    need(type(fork) is dict and fork.get("full_name", "").casefold() ==
         work_name.casefold()
         and fork.get("private") is False and fork.get("archived") is False
         and fork.get("fork") is True
         and (fork.get("parent") or {}).get("full_name", "").casefold() ==
         source_name.casefold()
         and (fork.get("permissions") or {}).get("push") is True
         and work_name.split("/")[1].casefold() == item["fork_name"].casefold(),
         "Fork parent, visibility, name or writer permission mismatch")
    rights = github.patch_capability("opensiro-contributions")
    need(type(rights) is dict and set(rights) ==
         {"owner", "actor", "available", "authorized"}
         and rights["owner"] == "opensiro-contributions"
         and type(rights["actor"]) is str and rights["actor"]
         and rights["available"] is True and rights["authorized"] is True,
         "No host/provider-attested patch writing capability")
    source_base = github.branch(source_name, action["source_branch"])
    work_base = github.branch(work_name, action["base_branch"])
    need(type(source_base) is dict
         and source_base.get("sha") == action["source_sha"],
         "Upstream source branch changed")
    if "fork_observed_sha" not in action:
        need(type(work_base) is dict
             and work_base.get("sha") == action["base_sha"],
             "Source or working fork base SHA drift")
    else:
        # A fork may already contain the source commit object without
        # moving its development branch. Prove exact object and ancestry.
        observed = action["fork_observed_sha"]
        need(type(work_base) is dict
             and work_base.get("sha") == observed,
             "Observed fork branch moved after review")
        need(callable(getattr(github, "shared_commit", None))
             and callable(getattr(github, "compare_commits", None)),
             "No authenticated shared-commit ancestry evidence port")
        object_receipt = github.shared_commit(work_name, action["base_sha"])
        need(type(object_receipt) is dict
             and object_receipt.get("sha") == action["base_sha"]
             and type(object_receipt.get("tree_sha")) is str
             and SHA.fullmatch(object_receipt["tree_sha"]),
             "Exact upstream base commit object not available in fork")
        relation = github.compare_commits(
            work_name, observed, action["base_sha"])
        need(type(relation) is dict
             and relation.get("status") in ("ahead", "identical")
             and type(relation.get("ahead_by")) is int
             and relation["ahead_by"] >= 0
             and relation.get("behind_by") == 0
             and relation.get("base_commit_sha") == observed
             and relation.get("merge_base_sha") == observed,
             "Fork branch not an ancestor of reviewed shared source commit")
    try:
        github.branch(work_name, action["new_branch"])
    except NotFound:
        pass
    else:
        raise StageBlocked("Contribution branch already exists")
    prod = next(p for p in action["changed_paths"] if "/src/" in p)
    test = next(p for p in action["changed_paths"] if "/test/" in p)
    need(digest(_observed_file(github, source_name, prod,
                               action["source_branch"])) ==
         action["preimage_sha256"][prod],
         "Source preimage SHA mismatch")
    # Shared-object mode reads the target fork by exact source SHA,
    # never by its intentionally unchanged old development branch.
    target_ref = (action["base_sha"] if "fork_observed_sha" in action
                  else action["base_branch"])
    need(digest(_observed_file(github, work_name, prod, target_ref)) ==
         action["preimage_sha256"][prod],
         "Exact fork commit preimage differs from reviewed source")
    try:
        github.file(work_name, test, target_ref)
    except NotFound:
        pass
    else:
        raise StageBlocked("Expected new test file already exists")
    return rights["actor"]


def prepare_exact_two_file_patch(*, manifest, selected_ids, stage_scopes,
                                 candidate_id, action, github=None, host=None):
    """Use trusted host-provided one-use decision + atomic patch publisher port.

    publish_patch_commit must atomically create exactly one new branch with
    one commit based on base_sha, and fail if branch collides. It must verify
    applied exact paths and postimage contents BEFORE any remote write.
    A call error is AMBIGUOUS, not safe to retry automatically.
    """
    need(github is not None and host is not None,
         "Real GitHub provider and trusted host authorization required")
    need(all(callable(getattr(github, n, None)) for n in PROVIDER_METHODS)
         and all(callable(getattr(host, n, None)) for n in HOST_METHODS),
         "Missing authenticated GitHub or host methods")
    frozen = deepcopy(action)
    _validate(frozen)
    need(action == frozen, "Action mutation before admission")
    try:
        preview = preview_draft(manifest, selected_ids=selected_ids,
                                stage_scopes=stage_scopes)
    except BatchError as exc:
        raise StageBlocked("Invalid selected source proposal: " + str(exc)) from None
    matches = [x for x in preview["candidates"]
               if x["id"] == candidate_id and x["selected"]]
    need(len(matches) == 1, "Candidate not selected")
    item = matches[0]
    need(item["selected_stages"] == [STAGE]
         and not item["blockers"]
         and item["expected_license"] is not None
         and item["proposal"]["evidence_url"],
         "Stage not exact, candidate blocked or evidence absent")
    actor = _preflight(item, frozen, github)
    intent = {
        "stage": STAGE, "candidate_id": candidate_id, "source": item["source"],
        "proposal_sha256": preview["proposal_sha256"],
        "selection_scope_sha256": preview["selection_scope_sha256"],
        "actor": actor, "working_repo": frozen["working_repo"],
        "source_branch": frozen["source_branch"],
        "source_sha": frozen["source_sha"], "base_branch": frozen["base_branch"],
        "base_sha": frozen["base_sha"], "new_branch": frozen["new_branch"],
        **({"fork_observed_sha": frozen["fork_observed_sha"]}
           if "fork_observed_sha" in frozen else {}),
        "patch_sha256": frozen["patch_sha256"],
        "changed_paths": deepcopy(frozen["changed_paths"]),
        "preimage_sha256": deepcopy(frozen["preimage_sha256"]),
        "postimage_sha256": deepcopy(frozen["postimage_sha256"]),
    }
    grant = host.verify_exact_prepare(deepcopy(intent))
    need(grant is not None and type(grant) not in (str, bool, dict, int, float),
         "Host did not issue an opaque authenticated grant")
    need(action == frozen, "Action changed during host grant")
    refreshed = preview_draft(manifest, selected_ids=selected_ids,
                              stage_scopes=stage_scopes)
    need(refreshed["proposal_sha256"] == preview["proposal_sha256"]
         and refreshed["selection_scope_sha256"] == preview["selection_scope_sha256"],
         "Proposal or selection scope changed during grant")
    need(host.authorize_exact_stage(grant, deepcopy(intent)) is True,
         "Host denied exact one-use prepare stage")
    need(action == frozen, "Action changed during stage decision")
    need(_preflight(item, frozen, github) == actor,
         "Provider actor or source state changed after authorization")
    try:
        result = github.publish_patch_commit(
            frozen["working_repo"], frozen["base_sha"], frozen["new_branch"],
            frozen["patch_text"], deepcopy(frozen["changed_paths"]),
            deepcopy(frozen["postimage_sha256"]))
    except Exception as exc:
        return {**intent, "status": "UNKNOWN_AFTER_WRITE",
                "reason": type(exc).__name__, "auto_retry": False}
    commit_sha = result.get("commit_sha") if type(result) is dict else None
    if type(commit_sha) is not str or not SHA.fullmatch(commit_sha):
        return {**intent, "status": "PENDING_VERIFICATION",
                "auto_retry": False}
    try:
        remote_branch = github.branch(frozen["working_repo"], frozen["new_branch"])
        commit = github.commit(frozen["working_repo"], commit_sha)
        verified = (
            remote_branch.get("sha") == commit_sha
            and type(commit) is dict
            and commit.get("parents") == [frozen["base_sha"]]
            and sorted(commit.get("changed_paths", [])) ==
            sorted(frozen["changed_paths"])
            and all(digest(_observed_file(
                github, frozen["working_repo"], path, frozen["new_branch"])) ==
                frozen["postimage_sha256"][path]
                for path in frozen["changed_paths"])
        )
    except Exception:
        verified = False
    return {**intent, "status": "PREPARED_VERIFIED" if verified
            else "PENDING_VERIFICATION", "commit_sha": commit_sha,
            "auto_retry": False}
