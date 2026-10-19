"""Pure P1 local-mandate preflight. No GitHub calls, grants, or write capability.

Only a trusted execution host can attest an issued, unrevoked owner decision.
A locally supplied FakeHost (including tests) is NOT evidence of authority.
The result is scope evidence, never an approval or instruction to write.
"""
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import PurePosixPath
import re

REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
BRANCH = re.compile(r"^opensiro/[a-z0-9][a-z0-9._/-]{0,79}$")
GRANT_FIELDS = {
    "schema_version", "kind", "status", "grant_id", "issuer",
    "recipient_execution_id", "working_repositories", "branch_prefix",
    "path_prefixes", "allowed_stage", "valid_from", "valid_until",
}
INTENT_FIELDS = {"stage", "working_repo", "branch", "file_paths",
                 "external_publication"}


class MandateBlocked(Exception):
    """Mandate or host attestation unavailable; never write."""


def _need(ok, reason):
    if not ok:
        raise MandateBlocked(reason)


def digest(value):
    return hashlib.sha256(json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _instant(value):
    _need(type(value) is str and value.endswith("Z"),
          "Grant time must be explicit UTC ISO8601 ending in Z")
    try:
        instant = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        raise MandateBlocked("Invalid grant timestamp") from None
    _need(instant.tzinfo is not None, "Missing UTC time zone")
    return instant


def _path(value):
    _need(type(value) is str and 1 <= len(value) <= 240
          and not value.startswith("/") and not value.endswith("/")
          and not any(c in value for c in ("\\", ":", "\x00")),
          "Invalid repository-relative path")
    components = value.split("/")
    _need(all(part not in ("", ".", "..") for part in components)
          and str(PurePosixPath(value)) == value,
          "Unsafe repository path")
    _need(not value.startswith((".github/", ".git/"))
          and value not in (".git", ".github"),
          "Protected infrastructure path")
    return value


def preview_p1_scope(grant, intent, *, trusted_host=None):
    """Verify exact future scope using host attestations. Never perform writes.

    Trusted host methods: actor_identity(), utcnow(), verify_owner_grant(digest).
    The host MUST independently authenticate the issuer's effective decision,
    its digest/actor/term and live revocation status; a model-provided object is
    not such a host. Provider rights, source policy and drift remain separate.
    """
    _need(trusted_host is not None and all(
        callable(getattr(trusted_host, name, None)) for name in
        ("actor_identity", "utcnow", "verify_owner_grant")
    ), "Trusted execution host not connected")
    _need(type(grant) is dict and set(grant) == GRANT_FIELDS,
          "Unrecognized P1 grant shape")
    _need(grant["schema_version"] == 1
          and grant["kind"] == "UPSTREAM_LOCAL_P1"
          and grant["status"] == "ISSUED",
          "No operative P1 grant claim")
    _need(type(grant["grant_id"]) is str
          and bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{3,99}", grant["grant_id"])),
          "Invalid grant identity")
    _need(type(grant["issuer"]) is str and
          bool(REPO.fullmatch(grant["issuer"])),
          "Issuer is not an explicit repository owner identifier")
    _need(type(grant["recipient_execution_id"]) is str
          and len(grant["recipient_execution_id"].strip()) >= 8,
          "No concrete recipient execution identity")
    repos = grant["working_repositories"]
    _need(type(repos) is list and 1 <= len(repos) <= 5
          and len(set(repos)) == len(repos)
          and all(type(x) is str and REPO.fullmatch(x) for x in repos),
          "No explicit repository allowlist")
    _need(grant["branch_prefix"] == "opensiro/"
          and grant["allowed_stage"] == "prepare_contribution",
          "P1 cannot delegate publication or branch scope expansion")
    prefixes = grant["path_prefixes"]
    _need(type(prefixes) is list and 1 <= len(prefixes) <= 8
          and len(set(prefixes)) == len(prefixes),
          "Invalid allowed path prefixes")
    for prefix in prefixes:
        _need(type(prefix) is str and prefix.endswith("/"),
              "Allowed prefix must name a directory")
        _path(prefix + "witness.txt")

    valid_from, valid_until = _instant(grant["valid_from"]), _instant(grant["valid_until"])
    _need(valid_from < valid_until <= valid_from + timedelta(days=30),
          "Grant interval must be bounded to 30 days")
    _need(type(intent) is dict and set(intent) == INTENT_FIELDS,
          "Invalid exact action intent")
    _need(intent["stage"] == "prepare_contribution"
          and intent["external_publication"] is False,
          "External publication and other stages remain operator-owned")
    _need(type(intent["working_repo"]) is str
          and intent["working_repo"] in repos,
          "Working repository outside explicit grant")
    branch = intent["branch"]
    _need(type(branch) is str and bool(BRANCH.fullmatch(branch))
          and branch.startswith(grant["branch_prefix"])
          and ".." not in branch and "//" not in branch
          and not branch.endswith((".", "/", ".lock")),
          "Unapproved or unsafe branch")
    paths = intent["file_paths"]
    _need(type(paths) is list and 1 <= len(paths) <= 8
          and len(set(paths)) == len(paths), "Invalid file change set")
    for p in paths:
        _path(p)
        _need(any(p.startswith(prefix) for prefix in prefixes),
              "File outside bounded path allowlist")

    # All following facts are host-observed, not fields in the grant JSON.
    try:
        actor = trusted_host.actor_identity()
        now = trusted_host.utcnow()
        witnessed = trusted_host.verify_owner_grant(digest(grant))
    except Exception as exc:
        raise MandateBlocked("Host attestation unavailable: " + type(exc).__name__) from None
    _need(type(actor) is str and actor == grant["recipient_execution_id"],
          "Recipient execution identity mismatch")
    _need(type(now) is datetime and now.tzinfo is not None
          and now.utcoffset() == timedelta(0)
          and valid_from <= now < valid_until,
          "Host time outside grant term")
    _need(type(witnessed) is dict
          and set(witnessed) == {"grant_digest", "issuer", "recipient", "active", "revoked"}
          and witnessed["grant_digest"] == digest(grant)
          and witnessed["issuer"] == grant["issuer"]
          and witnessed["recipient"] == actor
          and witnessed["active"] is True
          and witnessed["revoked"] is False,
          "No current trusted, unrevoked issuer attestation")
    return {
        "status": "SCOPE_PRECHECK_ONLY_NOT_A_WRITE_AUTHORIZATION",
        "grant_digest": digest(grant),
        "intent_digest": digest(intent),
        "working_repo": intent["working_repo"],
        "recipient_execution_id": actor,
    }
