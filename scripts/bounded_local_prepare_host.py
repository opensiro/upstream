"""Bounded local fork preparation mandate (inactive unless owner applies policy).

Simplified, trust-based alternative to signed exact grants. Only an explicit
owner-applied ACTIVE policy read from Upstream/main may enable this host.
The writer remains the existing two-file stage and new-ref-only REST port.
This is NOT protection against an executor abusing its existing raw PAT.
"""
import base64
import binascii
import hashlib
import json
import re
import time

from connected_stage_adapter import StageBlocked

SOURCE = "HarnessDesk/HarnessDesk"
FORK = "opensiro-contributions/HarnessDesk"
POLICY_REPO = "opensiro/upstream"
POLICY_PATH = "policies/harnessdesk-1772-local-prepare.json"
ACTOR = "xLagerFeuer"
STAGE = "prepare_contribution"
ISSUE = "harnessdesk-1772"
BRANCH = "opensiro/fix-toolgateway-1772"
PATHS = ["packages/server/src/tool-gateway.ts",
         "packages/server/test/tool-gateway-ownership.test.ts"]
HEX64 = re.compile(r"^[0-9a-f]{64}$")

def need(ok, reason):
    if not ok:
        raise StageBlocked(reason)

def canonical(value):
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, OverflowError):
        raise StageBlocked("Noncanonical mandate/intent") from None

def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


class CurrentMainMandateReader:
    """Read latest policy from PUBLIC current main via authenticated GET only.

    transport = existing GitHubCLIJSONTransport. A same-credential attacker
    could still bypass this Python code: never describe it as a security
    boundary against unrestricted PAT/SSH.
    """
    def __init__(self, transport):
        need(callable(transport), "Authenticated read transport missing")
        self.transport = transport

    def _get(self, path):
        status, body = self.transport("GET", "repos/" + POLICY_REPO + "/" + path)
        need(status == 200 and type(body) is dict,
             "Current main mandate fetch unavailable")
        return body

    def __call__(self):
        prior = self._get("branches/main")
        head = (prior.get("commit") or {}).get("sha")
        need(type(head) is str and re.fullmatch(r"[0-9a-f]{40}", head),
             "Cannot pin owning main branch")
        # Bind policy contents to the observed main commit; if main advances,
        # the next decision must start from a freshly observed policy.
        obj = self._get("contents/" + POLICY_PATH + "?ref=" + head)
        need(obj.get("type") == "file" and obj.get("encoding") == "base64"
             and type(obj.get("content")) is str,
             "Mandate is not an ordinary GitHub file")
        try:
            data = base64.b64decode("".join(obj["content"].split()),
                                    validate=True)
            need(len(data) <= 8192, "Mandate exceeds bounded size")
            policy = json.loads(data.decode("utf-8"))
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise StageBlocked("Invalid current owner policy document") from None
        need(type(policy) is dict, "Mandate policy must be a JSON object")
        later = self._get("branches/main")
        need((later.get("commit") or {}).get("sha") == head,
             "Mandate main branch drifted during read")
        return policy


class _BoundedGrant:
    __slots__ = ("intent_digest", "policy_digest", "used")

    def __init__(self, intent_digest, policy_digest):
        self.intent_digest = intent_digest
        self.policy_digest = policy_digest
        self.used = False


class BoundedLocalPrepareHost:
    """No per-action user prompt within a previously ACTIVE bounded mandate.

    Test readers may be injected; the real runner MUST use
    CurrentMainMandateReader(GitHubCLIJSONTransport()) and never derive
    activation from a draft file, CLI flag, issue/PR text or this module.
    """
    def __init__(self, *, mandate_reader, clock=None):
        need(callable(mandate_reader), "Current main mandate reader unavailable")
        self._reader = mandate_reader
        self._clock = time.time if clock is None else clock
        need(callable(self._clock), "Trusted clock missing")
        self._grant = None

    def _accepted(self, intent):
        policy = self._reader()
        need(type(policy) is dict and set(policy) ==
             {"schema_version", "mandate_id", "status", "issuer_actor",
              "actor", "execution_host", "source", "working_repo",
              "candidate_id", "stage", "source_branch", "base_branch",
              "new_branch", "changed_paths", "valid_from", "valid_until",
              "owner_decision_url", "publication_owner"},
             "Missing or unexpected mandate fields")
        need(type(policy["schema_version"]) is int
             and policy["schema_version"] == 1
             and policy["mandate_id"] == "harnessdesk-1772-local-p1"
             and policy["status"] == "ACTIVE"
             and policy["issuer_actor"] == ACTOR
             and policy["actor"] == ACTOR
             and policy["execution_host"] == "zhdanov:robot"
             and policy["source"] == SOURCE
             and policy["working_repo"] == FORK
             and policy["candidate_id"] == ISSUE
             and policy["stage"] == STAGE
             and policy["source_branch"] == "development"
             and policy["base_branch"] == "development"
             and policy["new_branch"] == BRANCH
             and policy["changed_paths"] == PATHS
             and policy["publication_owner"] == "human_operator"
             and type(policy["owner_decision_url"]) is str
             and policy["owner_decision_url"].startswith(
                 "https://github.com/opensiro/upstream/issues/6#issuecomment-")
             and len(policy["owner_decision_url"]) <= 180,
             "No effective owner-selected narrow preparation mandate")
        start, end = policy["valid_from"], policy["valid_until"]
        now = self._clock()
        need(type(start) is int and type(end) is int
             and type(now) in (int, float) and start > 0
             and end > start and end - start <= 30 * 86400
             and start <= now < end,
             "Standing preparation mandate expired or outside finite term")
        need(type(intent) is dict
             and intent.get("stage") == STAGE
             and intent.get("candidate_id") == ISSUE
             and intent.get("source") == SOURCE
             and intent.get("actor") == ACTOR
             and intent.get("working_repo") == FORK
             and intent.get("source_branch") == "development"
             and intent.get("base_branch") == "development"
             and intent.get("new_branch") == BRANCH
             and intent.get("changed_paths") == PATHS
             and type(intent.get("source_sha")) is str
             and re.fullmatch(r"[0-9a-f]{40}", intent["source_sha"])
             and intent.get("base_sha") == intent["source_sha"]
             and type(intent.get("fork_observed_sha")) is str
             and re.fullmatch(r"[0-9a-f]{40}", intent["fork_observed_sha"])
             and all(type(intent.get(key)) is str
                     and HEX64.fullmatch(intent[key])
                     for key in ("proposal_sha256", "selection_scope_sha256",
                                 "patch_sha256"))
             and type(intent.get("preimage_sha256")) is dict
             and list(intent["preimage_sha256"]) == PATHS[:1]
             and type(intent.get("postimage_sha256")) is dict
             and list(intent["postimage_sha256"]) == PATHS
             and all(type(v) is str and HEX64.fullmatch(v)
                     for v in list(intent["preimage_sha256"].values())
                     + list(intent["postimage_sha256"].values())),
             "Action exceeds selected local pilot mandate")
        return digest(policy)

    def verify_exact_prepare(self, intent):
        need(self._grant is None, "Host already owns an unconsumed stage")
        policy_digest = self._accepted(intent)
        grant = _BoundedGrant(digest(intent), policy_digest)
        self._grant = grant
        return grant

    def authorize_exact_stage(self, grant, intent):
        need(type(grant) is _BoundedGrant and grant is self._grant
             and grant.used is False and grant.intent_digest == digest(intent),
             "Wrong, reused or altered standing mandate action")
        need(grant.policy_digest == self._accepted(intent),
             "Standing mandate changed, revoked or moved")
        grant.used = True
        self._grant = None
        return True
