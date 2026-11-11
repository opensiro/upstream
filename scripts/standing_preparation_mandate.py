"""Finite owner-directed preparation autonomy; no external PR authorization.

Use only in a trusted connected host with provider-derived actor/host identity.
The host reads policy and generated registry from the SAME current Upstream
main commit before each decision. Per-operation opaque grants are automatic
under that standing mandate; no per-operation human prompt is needed.

This is deliberately not a raw credential sandbox: the authenticated GitHub
port and its exact source/license/fork/branch checks still gate every write.
"""
import base64
import binascii
import hashlib
import json
import re
import time

from connected_stage_adapter import StageBlocked

POLICY_REPO = "opensiro/upstream"
POLICY_PATH = "policies/standing-preparation-p1.json"
REGISTRY_PATH = "data/contribution-workspaces/registry.json"
DECISION_URL = "https://github.com/opensiro/upstream/issues/6#issuecomment-6799137559"
ACTOR = "xLagerFeuer"
HOST = "dev-alpha-2"
DESTINATION = "opensiro-contributions"
STAGES = ["create_public_fork", "prepare_contribution"]
SHA = re.compile(r"^[0-9a-f]{40}$")
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
BRANCH = re.compile(r"^opensiro/[a-z0-9][a-z0-9._/-]{0,79}$")
FIELDS = {
    "schema_version", "mandate_id", "status", "issuer_actor", "actor",
    "execution_host", "owner_decision_url", "valid_from", "valid_until",
    "source_registry", "destination_owner", "max_distinct_sources_per_wave",
    "allowed_stages", "branch_prefix", "required_packet_state",
    "publication_owner", "external_pr_publication",
}


def need(ok, reason):
    if not ok:
        raise StageBlocked(reason)


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=True,
                                     separators=(",", ":"), allow_nan=False)
                          .encode()).hexdigest()


class CurrentMainStandingPreparationReader:
    """GET-only policy/registry reader, pinned to one observed public main SHA."""
    def __init__(self, transport):
        need(callable(transport), "Authenticated GET transport unavailable")
        self.transport = transport

    def _get(self, path):
        status, body = self.transport("GET", "repos/" + POLICY_REPO + "/" + path)
        need(status == 200 and type(body) is dict,
             "Cannot read authoritative current Upstream main")
        return body

    def _json(self, path, sha):
        obj = self._get("contents/" + path + "?ref=" + sha)
        need(obj.get("type") == "file" and obj.get("encoding") == "base64"
             and type(obj.get("content")) is str,
             "Policy or registry is not a GitHub file")
        try:
            data = base64.b64decode("".join(obj["content"].split()), validate=True)
            need(len(data) <= 1_500_000, "Policy or registry exceeds safe bound")
            value = json.loads(data.decode("utf-8"))
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise StageBlocked("Invalid authoritative JSON") from None
        need(type(value) is dict, "Authoritative document must be an object")
        return value

    def __call__(self):
        first = (self._get("branches/main").get("commit") or {}).get("sha")
        need(type(first) is str and SHA.fullmatch(first), "Unpinned main")
        policy = self._json(POLICY_PATH, first)
        registry = self._json(REGISTRY_PATH, first)
        final = (self._get("branches/main").get("commit") or {}).get("sha")
        need(first == final, "Mandate or registry drifted during read")
        return {"head_sha": first, "policy": policy, "registry": registry}


class _Grant:
    __slots__ = ("intent_digest", "snapshot_digest", "used")

    def __init__(self, intent_digest, snapshot_digest):
        self.intent_digest = intent_digest
        self.snapshot_digest = snapshot_digest
        self.used = False


class StandingPreparationHost:
    """Trusted-host interface for existing connected fork and patch adapters.

    The wave is an exact five-repository selection, not a free-form blanket
    authorization to mutate any GitHub repository. A separate trusted runner
    must bind host_identity to its actual execution device, and must attest
    GitHub actor/permissions from the provider rather than from user input.
    """
    def __init__(self, *, reader, wave_sources, host_identity, clock=None):
        need(callable(reader), "Authoritative main reader unavailable")
        need(type(wave_sources) is list and len(wave_sources) == 5
             and all(type(s) is str and REPO.fullmatch(s) for s in wave_sources)
             and len(set(s.casefold() for s in wave_sources)) == 5,
             "One wave must identify five distinct real repositories")
        need(host_identity == HOST, "Wrong execution host")
        self.reader = reader
        self.wave = tuple(s.casefold() for s in wave_sources)
        self.clock = time.time if clock is None else clock
        self._grant = None
        self._fork_consumed = set()

    def _snapshot(self, intent):
        snapshot = self.reader()
        need(type(snapshot) is dict and set(snapshot) ==
             {"head_sha", "policy", "registry"}
             and type(snapshot["head_sha"]) is str
             and SHA.fullmatch(snapshot["head_sha"]),
             "Missing pinned owner-repository snapshot")
        p = snapshot["policy"]
        need(type(p) is dict and set(p) == FIELDS,
             "Missing or unexpected standing mandate fields")
        need(type(p["schema_version"]) is int
             and p["schema_version"] == 1
             and p["mandate_id"] == "upstream-preparation-p1-20261111"
             and p["status"] == "ACTIVE"
             and p["issuer_actor"] == ACTOR and p["actor"] == ACTOR
             and p["execution_host"] == HOST
             and p["owner_decision_url"] == DECISION_URL
             and p["source_registry"] == REGISTRY_PATH
             and p["destination_owner"] == DESTINATION
             and type(p["max_distinct_sources_per_wave"]) is int
             and p["max_distinct_sources_per_wave"] == 5
             and p["allowed_stages"] == STAGES
             and p["branch_prefix"] == "opensiro/"
             and p["required_packet_state"] == "EXPLICIT_PATCH_HASH_MATCHED"
             and p["publication_owner"] == "separate_standing_policy"
             and p["external_pr_publication"] == "SEE_STANDING_EXTERNAL_PUBLICATION_P1",
             "No effective owner-selected standing preparation mandate")
        now, start, end = self.clock(), p["valid_from"], p["valid_until"]
        need(type(now) in (int, float) and type(start) is int and type(end) is int
             and end > start and end - start <= 30 * 86400
             and start <= now < end,
             "Preparation mandate expired or not yet active")
        registry = snapshot["registry"]
        need(type(registry) is dict and registry.get("schema_version") == 1
             and type(registry.get("sources")) is list,
             "No authoritative working-source registry")
        sources = {s["source"].casefold(): s for s in registry["sources"]
                   if type(s) is dict and type(s.get("source")) is str}
        need(all(s in sources for s in self.wave), "Wave source not in registry")
        # A blocked member stays in the five-source wave, but must not prevent
        # a distinct eligible member from receiving its own exact one-use grant.
        # Ineligible members themselves still fail closed before any write.
        need(type(intent) is dict
             and intent.get("stage") in STAGES
             and type(intent.get("source")) is str
             and intent["source"].casefold() in self.wave
             and ((intent.get("actor") == ACTOR)
                  if intent["stage"] == "prepare_contribution"
                  else (intent.get("connected_actor") == ACTOR)),
             "Action outside authenticated preparation scope")
        row = sources[intent["source"].casefold()]
        need(row.get("license_review") is False
             and row.get("latest_stage") == "AWAITING_EXTERNAL"
             and type(row.get("proposed_fork")) is str
             and row["proposed_fork"].casefold().startswith(
                 DESTINATION.casefold() + "/")
             and any(type(h) is dict
                     and h.get("stage") == "AWAITING_EXTERNAL"
                     and type(h.get("technical_packet")) is dict
                     and h["technical_packet"].get("state") ==
                     "EXPLICIT_PATCH_HASH_MATCHED"
                     for h in row.get("handoffs", [])),
             "Requested source lacks eligible, reviewed, source-linked packet")
        fork = row["proposed_fork"].casefold()
        if intent["stage"] == "prepare_contribution":
            branch = intent.get("new_branch")
            need(type(branch) is str and BRANCH.fullmatch(branch)
                 and ".." not in branch and "//" not in branch
                 and intent.get("working_repo", "").casefold() == fork,
                 "Patch destination or branch outside authorized fork")
        else:
            need(intent.get("destination", "").casefold() == fork
                 and intent.get("default_branch_only") is False
                 and type(intent.get("working_branch_sha")) is str
                 and SHA.fullmatch(intent["working_branch_sha"]),
                 "Fork destination or branch copy mode is unauthorized")
        return digest(snapshot)

    def verify_exact_prepare(self, intent):
        need(self._grant is None, "An internal stage decision is still pending")
        need(intent.get("stage") == "prepare_contribution",
             "This grant only prepares contribution branches")
        grant = _Grant(digest(intent), self._snapshot(intent))
        self._grant = grant
        return grant

    def authorize_exact_stage(self, grant, intent):
        need(type(grant) is _Grant and grant is self._grant and not grant.used
             and grant.intent_digest == digest(intent),
             "Wrong or replayed internal preparation decision")
        need(grant.snapshot_digest == self._snapshot(intent),
             "Standing preparation scope changed during decision")
        grant.used = True
        self._grant = None
        return True

    def authorize_fork(self, intent):
        """Host-authored callback for connected_fork_adapter's one-use stage."""
        need(intent.get("stage") == "create_public_fork",
             "Standing preparation does not authorize PR publication")
        fingerprint = digest(intent)
        need(fingerprint not in self._fork_consumed,
             "Fork authorization already consumed")
        self._snapshot(intent)
        self._fork_consumed.add(fingerprint)
        return True
