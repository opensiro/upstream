# CLA single-attempt journal — local safety primitive, not legal authority

**Issue:** [Upstream #274](https://github.com/opensiro/upstream/issues/274). **Status:** offline SQLite safety primitive for a hypothetical, separately authorized executor; NOT a working acceptance agent. **Previous prerequisite:** [chat-origin cryptographic receipt verifier](../scripts/cla_chat_attestation.py) introduced by #286.

## Why this exists

A successful request to GitHub can be followed by a network timeout. Automatically resending a CLA-bearing request can duplicate a legally significant action or create ambiguous evidence. A single-use consent nonce should therefore not be reprocessed just because the local agent loses the response.

[Source](../scripts/cla_attempt_journal.py) uses SQLite and `BEGIN IMMEDIATE` plus a unique, domain-separated SHA-256 of the provider issuer/nonce. It allows only these **local record states**, none of which is authorization:

| State | Meaning |
| --- | --- |
| `RESERVED_NO_POST` | The nonce was durably reserved; no third-party action attempted |
| `DISPATCH_BEGAN_UNCONFIRMED` | A single dispatch token was consumed; the external result is **unknown** |
| `READBACK_REPORTED_UNVERIFIED` | A GitHub PR URL claim was recorded; this module did **not** independently verify it |

A second reserve using the same nonce, a changed target, changed packet hash or changed fork SHA, a second dispatch attempt, or an out-of-order readback is rejected. Even a correct URL never becomes `CLA_ACCEPTED`, `VERIFIED`, `ALLOW`, or `LEGAL_CONSENT` here. The raw nonce is not stored.

## Required caller boundaries

1. A separate **trusted** client integration must supply an independently issuer-signed human approval for a *specific* source-pinned packet, verified against an independently provisioned Ed25519 issuer key and signatory identity mapping. This project cannot obtain such a signature from the current ChatGPT chat interface; model output and GitHub OAuth are not substitutes.
2. S5 template enrolment must be active for the exact third-party CLA, individual/corporate capacity and approved action; the current [CLA registry](../policies/cla-template-registry-v1.json) is **disabled** and remains unchanged.
3. The future executor must recheck live original terms and hash, exact original/fork head, current target rules, contributor rights, native CI/PR template, duplicates and its standing publication mandate **before** attempting a legal action.
4. The executor must use **durable storage under the exclusive control of the appropriate trust boundary**, not a GitHub branch, disposable ChatGPT container or in-memory DB. It must atomically claim the one-time nonce and mark `DISPATCH_BEGAN_UNCONFIRMED` **before the first possible external send**.
5. Once dispatch intent is recorded, any crash, timeout, connectivity error or 5xx outcome remains **ambiguous** and must be reconciled through fresh target-side readback **without automatically sending the same operation again**. No exactly-once distributed transaction between SQLite and GitHub is claimed.
6. Successful original-project POST/readback must independently verify the correct original repository, PR number/head/base/body/actor and CLA-specific acceptance outcome. `record_readback()` only saves a submitted URL claim and cannot establish those facts.
7. No user must be required to manually reproduce a signed decision in a GitHub issue as a routine UX workaround. A missing trusted identity channel is a **platform integration blocker**, not permission to fabricate a signature or weaken the gate.

The journal API is intentionally independent of any GitHub SDK, secret, consent creation, legal-post execution or provider attestation provisioning. Integrating it into a real executor requires a separately reviewed, externally authenticated transport and independent provider-side signer-binding evidence.

## Validation

- `python3 -m unittest tests.test_cla_attempt_journal -v` covers 19 offline cases, including 24-thread contention tests for reservations and dispatch, replay across fresh SQLite connections, changed target/head, crash-conservative dispatch persistence, malformed inputs and unverified readback states.
- Existing [chat-receipt signature tests](../tests/test_cla_chat_attestation.py) test a **local fake issuer**, not a production identity authority. This ledger must not be connected to them in a manner that pretends the test key is trusted.
- No real CLA was accepted, no external PR was posted, and no live nonce database was created by the source implementation.

**Revka case:** [fork-local PR #1](https://github.com/opensiro-contributions/Revka/pull/1), exact commit `75c7adfca75fb30075e75674eb1badc2f6b7c90a`. The contributor stated individual approval in chat; the current client does **not** provide independently verifiable legal-person identity proof. Third-party Revka submission is still blocked, and original-project Rust native CI remains incomplete.
