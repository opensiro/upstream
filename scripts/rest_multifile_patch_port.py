"""GitHub REST Git-Data port for one exactly-scoped two-file patch commit.

Source-only: a real trusted VM/host must inject (1) an authenticated REST
transport, (2) a provider-derived actor/capability attestor, and (3) a
sandboxed local git-apply materializer. No PAT, network session, approval,
CLI entrypoint, retry, or host authorizer is provided by this library.

Git blob/tree and commit objects may be written before the final ref POST.
Only POST git/refs makes the new branch externally visible, atomically.
"""
import base64
import binascii
import re
from urllib.parse import quote

from connected_stage_adapter import NotFound, StageBlocked
from rest_fork_port import _repo, _branch

SHA = re.compile(r"^[0-9a-f]{40}$")
SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$")
DEST = "opensiro-contributions"


def need(condition, reason):
    if not condition:
        raise StageBlocked(reason)


class GitHubRESTMultifilePatchPort:
    """Trusted-host injected source-side REST Git Data provider.

    api(method, path, body=None) returns (actual HTTP status, JSON).
    materializer(repo, base_sha, patch_text, exact_paths) must locally
    git-apply --check + apply the patch to a CLEAN exact base checkout,
    verify the changed path set, forbid symlinks, and return
      {"base_sha": SHA, "changed_paths": [paths],
       "source_file_modes": {path: "100644", ...},
       "files": {path: resulting UTF-8 text, ...}}
    where the current production blob is regular 100644 and the new test
    blob is also 100644. The host must independently validate this result
    against the local worktree and never use a string supplied by an issue
    as a materialization attestation.
    capability_attestor(owner) must derive effective actor/permissions
    from the authenticated host and provider, not any proposal boolean.
    """

    def __init__(self, *, api=None, materializer=None,
                 capability_attestor=None):
        need(callable(api) and callable(materializer)
             and callable(capability_attestor),
             "Protected REST transport, git materializer and attestor required")
        self._api = api
        self._materialize = materializer
        self._attest = capability_attestor

    def _request(self, method, path, body=None, *, expected=(200,), absent=False):
        response = self._api(method, path, body)
        need(type(response) is tuple and len(response) == 2
             and type(response[0]) is int and type(response[1]) is dict,
             "Unexpected GitHub API response shape")
        status, value = response
        if status == 404 and absent:
            raise NotFound()
        need(status in expected, "GitHub provider rejected " + method +
             " request (status " + str(status) + ")")
        return value

    def repo(self, name):
        name = _repo(name)
        return self._request("GET", "repos/" + name)

    def branch(self, name, branch):
        name = _repo(name)
        branch = _branch(branch)
        data = self._request(
            "GET", "repos/" + name + "/branches/" + quote(branch, safe=""),
            absent=True)
        commit = data.get("commit")
        need(type(commit) is dict and type(commit.get("sha")) is str
             and SHA.fullmatch(commit["sha"]), "Malformed branch SHA")
        return {"sha": commit["sha"]}

    def file(self, name, path, branch):
        name = _repo(name)
        branch = _branch(branch)
        need(type(path) is str and 0 < len(path) <= 240
             and all(part not in ("", ".", "..") for part in path.split("/"))
             and "\\" not in path and "\x00" not in path,
             "Invalid source file path")
        data = self._request("GET",
                             "repos/" + name + "/contents/" + quote(path, safe="/") +
                             "?ref=" + quote(branch, safe=""), absent=True)
        need(data.get("type") == "file" and data.get("encoding") == "base64"
             and type(data.get("content")) is str,
             "File is not a GitHub base64-encoded regular blob")
        try:
            data_bytes = base64.b64decode("".join(data["content"].split()),
                                         validate=True)
            need(len(data_bytes) <= 131072, "Provider file exceeds bound")
            content = data_bytes.decode("utf-8")
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise StageBlocked("Malformed UTF-8 base64 file") from None
        return {"content": content}

    def patch_capability(self, owner):
        need(owner == DEST, "Outside permitted contribution organization")
        proof = self._attest(owner)
        need(type(proof) is dict
             and set(proof) == {"owner", "actor", "available", "authorized"}
             and proof["owner"] == owner
             and type(proof["actor"]) is str and SLUG.fullmatch(proof["actor"])
             and proof["available"] is True
             and proof["authorized"] is True,
             "Authenticated provider patch right not confirmed")
        return dict(proof)

    def commit(self, name, sha):
        name = _repo(name)
        need(type(sha) is str and SHA.fullmatch(sha),
             "Invalid commit hash")
        data = self._request("GET", "repos/" + name + "/commits/" + sha)
        parents = data.get("parents")
        files = data.get("files")
        need(type(parents) is list and len(parents) == 1
             and type(files) is list and len(files) < 300
             and all(type(p) is dict and type(p.get("sha")) is str
                     for p in parents)
             and all(type(f) is dict and type(f.get("filename")) is str
                     for f in files), "Commit review missing/truncated")
        return {"parents": [p["sha"] for p in parents],
                "changed_paths": [f["filename"] for f in files]}

    def publish_patch_commit(self, name, base_sha, new_branch,
                             patch_text, changed_paths, expected_postimages):
        """Return SHA if ref POST succeeded; no overwrites or retries.

        A trusted host must have already consumed exact stage authority.
        The caller must verify remote branch, parent, paths and contents.
        """
        name = _repo(name)
        new_branch = _branch(new_branch)
        need(name.split("/")[0] == DEST and new_branch.startswith("opensiro/"),
             "Invalid destination repository or contribution branch")
        need(type(base_sha) is str and SHA.fullmatch(base_sha),
             "Invalid base SHA")
        need(type(patch_text) is str and 0 < len(patch_text.encode()) <= 131072
             and type(changed_paths) is list and len(changed_paths) == 2
             and len(set(changed_paths)) == 2
             and type(expected_postimages) is dict
             and set(expected_postimages) == set(changed_paths),
             "Patch publication scope invalid")
        # The port is called only after source-stage preflight and one-use
        # host approval. Still fail closed if the target unexpectedly exists.
        try:
            self.branch(name, new_branch)
        except NotFound:
            pass
        else:
            raise StageBlocked("Contribution branch collision before Git Data write")

        material = self._materialize(name, base_sha, patch_text,
                                     list(changed_paths))
        need(type(material) is dict
             and set(material) == {
                 "base_sha", "changed_paths", "source_file_modes", "files"}
             and material["base_sha"] == base_sha
             and type(material["changed_paths"]) is list
             and sorted(material["changed_paths"]) == sorted(changed_paths)
             and type(material["source_file_modes"]) is dict
             and set(material["source_file_modes"]) == set(changed_paths)
             and all(v == "100644"
                     for v in material["source_file_modes"].values())
             and type(material["files"]) is dict
             and set(material["files"]) == set(changed_paths),
             "Local exact git-apply attestation unavailable")
        from connected_multifile_stage import digest
        for path in changed_paths:
            value = material["files"][path]
            need(type(value) is str and
                 digest(value) == expected_postimages[path],
                 "Materialized patch postimage mismatch")

        parent = self._request("GET",
                               "repos/" + name + "/git/commits/" + base_sha)
        parent_tree = (parent.get("tree") or {}).get("sha")
        need(type(parent_tree) is str and SHA.fullmatch(parent_tree),
             "Expected base commit/tree unavailable")
        tree = self._request(
            "POST", "repos/" + name + "/git/trees",
            {"base_tree": parent_tree,
             "tree": [{"path": p, "mode": "100644", "type": "blob",
                       "content": material["files"][p]} for p in changed_paths]},
            expected=(201,))
        tree_sha = tree.get("sha")
        need(type(tree_sha) is str and SHA.fullmatch(tree_sha),
             "Git tree POST did not provide a verified SHA")
        new_commit = self._request(
            "POST", "repos/" + name + "/git/commits",
            {"message": "fix: protect tool gateway socket ownership",
             "tree": tree_sha, "parents": [base_sha]},
            expected=(201,))
        new_sha = new_commit.get("sha")
        need(type(new_sha) is str and SHA.fullmatch(new_sha),
             "Git commit POST did not return exact SHA")
        # GitHub POST /git/refs is non-overwriting: an existing branch
        # returns 422. Never fall back to PATCH/UPDATE or force.
        ref = self._request(
            "POST", "repos/" + name + "/git/refs",
            {"ref": "refs/heads/" + new_branch, "sha": new_sha},
            expected=(201,))
        need(ref.get("ref") == "refs/heads/" + new_branch
             and (ref.get("object") or {}).get("sha") == new_sha,
             "Branch creation result mismatched exact commit")
        return {"commit_sha": new_sha}
