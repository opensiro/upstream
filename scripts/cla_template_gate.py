#!/usr/bin/env python3
"""Read-only, fail-closed CLA template preflight. Never executes a legal acceptance."""
import argparse
import hashlib
import json
import re
from datetime import date, timezone, datetime
from pathlib import Path

REGISTRY = Path(__file__).resolve().parents[1] / "policies" / "cla-template-registry-v1.json"


def assess(data, *, template_id, repository, actor, terms_sha256):
    """Return a decision. No result of this function permits an agreement POST."""
    if data.get("schema_version") != 1 or data.get("default_decision") != "BLOCK":
        return {"state": "BLOCKED", "reason": "INVALID_REGISTRY_CONTRACT"}
    if data.get("policy_status") != "S5_CATEGORY_APPROVED_TEMPLATE_ENROLMENT_REQUIRED":
        return {"state": "BLOCKED", "reason": "AUTHORITY_STATUS_UNVERIFIED"}
    templates = data.get("templates")
    if not isinstance(templates, list):
        return {"state": "BLOCKED", "reason": "INVALID_TEMPLATE_LIST"}
    matches = [item for item in templates if isinstance(item, dict) and item.get("id") == template_id]
    if len(matches) != 1:
        return {"state": "BLOCKED", "reason": "TEMPLATE_MISSING_OR_AMBIGUOUS"}
    template = matches[0]
    if template.get("repository") != repository:
        return {"state": "BLOCKED", "reason": "REPOSITORY_MISMATCH"}
    if template.get("signer_actor") != actor:
        return {"state": "BLOCKED", "reason": "SIGNER_ACTOR_MISMATCH"}
    if template.get("status") != "ENROLLED_EXACT_TERMS":
        return {"state": "BLOCKED", "reason": "EXACT_TERMS_NOT_APPROVED"}
    # A validated CLA is reusable for unchanged signatory/repository/terms.
    # Do not invent an expiration for perpetual/unspecified first-party terms.
    required = ("legal_counterparty", "terms_url", "terms_sha256", "signer_capacity",
                "exact_action", "signer_approval_ref", "mechanism")
    if any(not template.get(field) for field in required):
        return {"state": "BLOCKED", "reason": "MISSING_EXACT_ENROLMENT_FIELD"}
    digest = template["terms_sha256"]
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        return {"state": "BLOCKED", "reason": "INVALID_TERMS_DIGEST"}
    if digest != terms_sha256:
        return {"state": "BLOCKED", "reason": "TERMS_DIGEST_MISMATCH"}
    # Explicit limitations control when present; absent expiry is not a blocker.
    expires = template.get("valid_until")
    if expires is not None:
        if not isinstance(expires, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", expires):
            return {"state": "BLOCKED", "reason": "INVALID_APPROVAL_EXPIRY"}
        try:
            cutoff = date.fromisoformat(expires)
        except ValueError:
            return {"state": "BLOCKED", "reason": "INVALID_APPROVAL_EXPIRY"}
        if cutoff < datetime.now(timezone.utc).date():
            return {"state": "BLOCKED", "reason": "APPROVAL_EXPIRED"}
    if not data.get("legal_acceptance_executor_enabled", False):
        return {"state": "BLOCKED", "reason": "EXECUTOR_NOT_ACTIVATED"}

    # A JSON entry is never proof of a person's consent, their rights or current
    # source terms. This static preflight deliberately stops before legal action.
    return {"state": "BLOCKED", "reason": "INDEPENDENT_LIVE_SIGNATORY_AND_SOURCE_VERIFICATION_REQUIRED"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--template", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--actor", required=True)
    parser.add_argument("--terms-sha256", required=True)
    args = parser.parse_args()
    try:
        data = json.loads(args.registry.read_text(encoding="utf-8"))
        decision = assess(data, template_id=args.template, repository=args.repository,
                          actor=args.actor, terms_sha256=args.terms_sha256)
    except (OSError, ValueError, TypeError) as exc:
        decision = {"state": "BLOCKED", "reason": "REGISTRY_READ_ERROR", "detail": str(exc)}
    print(json.dumps(decision, sort_keys=True))
    return 0 if decision["state"] == "STATIC_ALLOW" else 2


if __name__ == "__main__":
    raise SystemExit(main())
