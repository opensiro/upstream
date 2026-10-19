"""Host-only GitHub REST fork provider port; no credentials or live dispatch.

The authenticated request transport and provider-verified capability proof
MUST be supplied by a trusted host. This module does not authenticate a user,
install a GitHub App, get tokens, issue approvals or expose a CLI entrypoint.
No caller-authored boolean is proof of organization creation permission.
"""
import re
from urllib.parse import quote

from connected_stage_adapter import NotFound, StageBlocked

DEST = "opensiro-contributions"
SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$")
BRANCH = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,119}$")


def _slug(x):
    if type(x) is not str or not SLUG.fullmatch(x) or x.endswith("."):
        raise StageBlocked("Invalid GitHub repository path")
    return x


def _repo(value):
    if type(value) is not str or value.count("/") != 1:
        raise StageBlocked("Expected exact OWNER/REPO")
    return "/".join(_slug(x) for x in value.split("/"))


def _branch(value):
    if (type(value) is not str or not BRANCH.fullmatch(value)
            or value.endswith(("/", ".", ".lock"))
            or ".." in value or "//" in value or "@{" in value):
        raise StageBlocked("Invalid working branch")
    return value


def _result(response, operation):
    if (type(response) is not tuple or len(response) != 2
            or type(response[0]) is not int):
        raise StageBlocked("Invalid trusted REST response for " + operation)
    return response


class GitHubRESTForkPort:
    """One-purpose adapter, constructed only inside a trusted execution host.

    api(method, path, body=...) must make authenticated GitHub API calls and
    return (HTTP status, decoded JSON). Never log or pass auth tokens here.
    capability_attestor(owner) must derive actor, privileges and permissions
    from the authenticated HOST/provider, never from a submitted manifest.
    """

    def __init__(self, *, api=None, capability_attestor=None):
        if not callable(api) or not callable(capability_attestor):
            raise StageBlocked("Trusted authenticated API and capability attestor required")
        self._api = api
        self._attest = capability_attestor

    def fork_capability(self, owner):
        if owner != DEST:
            raise StageBlocked("Fork destination outside authorized namespace")
        # Trust only a host implementation that actually attests live rights.
        # A fake callable in Python is permitted in offline tests, not proof.
        proof = self._attest(owner)
        if type(proof) is not dict or set(proof) != {
                "available", "authorized", "owner", "actor"}:
            raise StageBlocked("Unverifiable fork capability proof")
        if (proof["available"] is not True or proof["authorized"] is not True
                or proof["owner"] != DEST
                or type(proof["actor"]) is not str or not proof["actor"]):
            raise StageBlocked("No actual provider fork permission proof")
        return dict(proof)

    def _read(self, url):
        status, payload = _result(self._api("GET", url), "GET")
        if status == 404:
            raise NotFound()
        if status in (401, 403):
            raise PermissionError("GitHub authorization denied")
        if status != 200 or type(payload) is not dict:
            raise StageBlocked("GitHub repository/branch read failed")
        return payload

    def repo(self, full_name):
        full_name = _repo(full_name)
        return self._read("/repos/" + full_name)

    def branch(self, full_name, name):
        full_name = _repo(full_name)
        branch = _branch(name)
        payload = self._read("/repos/" + full_name + "/branches/" +
                             quote(branch, safe=""))
        sha = (payload.get("commit") or {}).get("sha")
        if type(sha) is not str or not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise StageBlocked("Unverified GitHub branch SHA")
        return {"sha": sha}

    def create_public_fork(self, source, owner, name, *, default_branch_only):
        source = _repo(source)
        name = _slug(name)
        if owner != DEST or source.split("/")[0].casefold() == DEST:
            raise StageBlocked("Wrong fork namespace or source owner")
        if type(default_branch_only) is not bool:
            raise StageBlocked("Fork copy strategy must be boolean")
        # Exactly one provider call. The caller must never retry on unknown
        # network/error/202 states; externally visible verification is separate.
        status, payload = _result(self._api(
            "POST", "/repos/" + source + "/forks",
            body={"organization": DEST, "name": name,
                  "default_branch_only": default_branch_only}), "POST")
        if status in (401, 403):
            raise PermissionError("GitHub fork creation permission denied")
        if status in (409, 422):
            raise StageBlocked("GitHub fork collision, policy or validation error")
        if status != 202 or type(payload) is not dict:
            raise StageBlocked("GitHub fork create did not return accepted HTTP 202")
        # Provider 202 is acknowledged, NOT independently verified.
        returned_owner = (payload.get("owner") or {}).get("login")
        returned_name = payload.get("name")
        if (type(returned_owner) is not str
                or returned_owner.casefold() != DEST.casefold()
                or type(returned_name) is not str
                or returned_name.casefold() != name.casefold()):
            raise StageBlocked("Unexpected fork creation response identity")
        return {"accepted": True}
