"""Read-only live GitHub principal/fork-rights attestor for the CLI host.

This verifies provider observations. It is NOT an approval issuer and never
creates an action-specific stage permit. Only the protected VM/host may bind
these observations to a separately authenticated one-use operator grant.
"""
import re
from connected_stage_adapter import StageBlocked

ACTOR = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]{0,38}$")
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
OWNER = "opensiro-contributions"


def _need(value, reason):
    if not value:
        raise StageBlocked(reason)


class GitHubCLIProviderAttestor:
    """Read-only, credential-context-bound provider capability evidence.

    The expected source and fork are injected by the trusted host, not the
    candidate's untrusted manifest. The callable returned by this class
    fulfills the REST port's capability_attestor(owner) interface.
    """

    def __init__(self, *, transport, expected_fork, expected_source,
                 expected_actor=None):
        _need(callable(transport), "Authenticated read transport required")
        _need(type(expected_fork) is str and REPO.fullmatch(expected_fork)
              and expected_fork.split("/")[0] == OWNER,
              "Fork is outside controlled destination organization")
        _need(type(expected_source) is str and REPO.fullmatch(expected_source)
              and expected_source != expected_fork,
              "Explicit distinct public source required")
        _need(expected_actor is None or
              (type(expected_actor) is str and ACTOR.fullmatch(expected_actor)),
              "Invalid actor constraint")
        self._transport = transport
        self._fork = expected_fork
        self._source = expected_source
        self._expected_actor = expected_actor

    def _get(self, path):
        response = self._transport("GET", path)
        _need(type(response) is tuple and len(response) == 2
              and type(response[0]) is int
              and type(response[1]) is dict
              and response[0] == 200,
              "Authenticated GitHub identity/rights GET failed")
        return response[1]

    def __call__(self, owner):
        _need(owner == OWNER, "Actor attestation outside allowed owner")
        user = self._get("user")
        actor = user.get("login")
        _need(type(actor) is str and ACTOR.fullmatch(actor)
              and (self._expected_actor is None
                   or actor == self._expected_actor),
              "GitHub identity missing or not the expected operator")
        membership = self._get("user/memberships/orgs/" + OWNER)
        _need(membership.get("state") == "active"
              and membership.get("role") in ("admin", "member"),
              "GitHub actor lacks active destination organization membership")
        fork = self._get("repos/" + self._fork)
        _need(fork.get("full_name") == self._fork
              and fork.get("private") is False
              and fork.get("archived") is False
              and fork.get("fork") is True
              and type(fork.get("parent")) is dict
              and fork["parent"].get("full_name") == self._source
              and type(fork.get("permissions")) is dict
              and fork["permissions"].get("push") is True,
              "GitHub principal cannot write to verified direct public fork")
        return {"owner": OWNER, "actor": actor,
                "available": True, "authorized": True}
