# Bounded organization-specific CLA template execution

**Authority source:** [Organization S5 #323](https://github.com/opensiro/vsm-oss-organization/issues/323) and [CLA delegation contract](https://github.com/opensiro/vsm-oss-organization/blob/main/contracts/s5/cla-template-delegation.md).
**Implementation owner:** [Upstream #274](https://github.com/opensiro/upstream/issues/274). **Current transport:** read-only, deny-by-default registry, cryptographic intent preflight and local SQLite attempt journal. No working client-identity binding, legally authorized executor, or automatic CLA agreement acceptance is implemented.

## Principle

The owner has authorized a bounded class of AI-assisted CLA actions based on **specific approved templates for specific organizations**. The owner instruction is not approval of any unknown current/future contractual terms. Until a template is independently approved for its exact CLA text and signatory capacity, the existing [standing publication mandate](STANDING_EXTERNAL_PR_PUBLICATION.md) still forbids an invented human legal attestation.

**Source of truth:** current third-party contributor instructions, actual legal counterparty, the exact CLA content, and independently attributable human approval. A GitHub token, fork ownership, or a populated JSON file is not proof of these. DCO sign-offs are different assertions and are out of scope.

## Version-pinned template enrolment

[Registry](../policies/cla-template-registry-v1.json) contains *candidate descriptions*, NOT signed agreements. For each counterparty, independently capture before activation:

- original GitHub organization/repo, legal entity, CLA version/source URL, SHA-256 of the exact accepted agreement text (after a canonical serialization policy is specified), and effective time;
- individual or authorized corporate capacity, identity and rights/employee/employer claims, supported by the actual signatory;
- exact approved literal GitHub operation (one-time bot reply vs submission-as-assent), and whether it applies to a single repo or a larger explicitly specified project set;
- approval of **the exact content and exact action** in independently verifiable evidence, not an agent-authored comment masquerading as a personally signed document;
- validity, revocation and per-action idempotency key, plus fresh authenticated source/bot readback and a target-side result receipt.

Do not store privileged credentials, confidential employment details or personal contract materials in the public registry. Use public non-sensitive receipt pointers and source hashes.

The included `scripts/cla_template_gate.py` is a **static policy preflight**. It can block unenrolled, wrong-repository, wrong-actor, stale-digest or incomplete approvals. Even when all static fields match, it returns `REQUIRES_INDEPENDENT_LIVE_ATTESTATION_CHECK`, **never permission to sign**. A separate implementation must verify genuine signer authorization, current counterparty terms, target-native contributor requirements, transport credentials and external reply, before any write. No code in this PR performs external `agree` comments, CLA acceptance or PR creation.

## Revka first-party terms observation (inactive, 2026-11-13)

The present [Revka CLA v1.0](https://github.com/KumihoIO/Revka/blob/a1acd826502e12a6c2f3d147e488a7d2982c480b/docs/contributing/cla.md) was fetched verbatim through authenticated GitHub read-only access at source `KumihoIO/Revka@a1acd826502e12a6c2f3d147e488a7d2982c480b`. Its **raw UTF-8 file bytes** (4,055 bytes) had SHA-256 `c6f2f0061d44875d6043530ba2ce0b93a77327dca5672a92787f84afb20de623` on 2026-11-13. This is a **source-content observation**, not consent, signed terms, legal advice, or a reusable credential.

Registry fields `observed_source_ref` and `observed_terms_sha256` are **informational only**. They never substitute for the enrolment-only `terms_sha256`, `signer_capacity`, `signer_approval_ref`, literal `exact_action`, expiry or independent live signatory verification. The Revka template remains `PENDING_EXACT_TERMS_APPROVAL`, the enrolment `terms_sha256` remains `null`, and the executor flag remains `false`.

Opening a PR to `KumihoIO/Revka` already constitutes contributor-person assent under section 9 of the observed first-party CLA; it must not be triggered merely by technical readiness or a generic request to continue. Recheck the current original-repository terms, the human's actual individual/corporate capacity, and exact personally approved rights before any external publication. The [fork-local Revka #1](https://github.com/opensiro-contributions/Revka/pull/1) is not a CLA acceptance to the original project.

## Chat-only operator approval is the preferred user interface

The contributor may review a **specific current CLA template and outgoing PR packet in their active chat** and reply `Я утверждаю` / `I approve`. **Do not require them to repost that decision in a GitHub issue, PR comment, or other website as a routine second approval.** The agent owns the subsequent GitHub technical actions and publication/audit records when all independently applicable gates pass.

Keep **decision transport** separate from **trustworthy legal-person attribution**:

1. **Presentation:** the agent shows the original repository and legal counterparty, first-party CLA URL and immutable text digest/version, individual/corporate capacity, required contributor-rights and employer/patent representations, exact fork branch/commit/files, and the precise third-party action that constitutes acceptance (Revka PR creation; Microsoft Fara bot statement). Disclose whether project rules require CI before PR creation and what validation is unrun.
2. **In-chat decision:** a human reply is an `IN_CHAT_INTENT_RECORDED` event scoped to that displayed packet. A generic `continue`, a preference for chat-only approvals, or an agent's reproduction of the user's words does not bind the person to unseen contracts or modified code. Reask only on materially changed terms/scope or insufficient actual legal-rights representation.
3. **Attribution gate:** before treating the decision as legally executable, a trustworthy client/provider must furnish independently verifiable binding of the chat participant to the intended real human signatory and the exact presented packet, with time and replay protection. **This ChatGPT/GitHub integration does not currently expose such attestation to the CLA executor.** GitHub API authentication as `xLagerFeuer` proves which account the tool can act through, **not** who typed the chat reply or their rights. An AI-authored GitHub comment, claimed chat URL, SHA-256 digest or copied transcript must never be accepted as substitute evidence.
4. **Execution:** only after the required signatory and rights checks, enabled exact template, current first-party terms/native tests, external-PR publication mandate and destination readbacks have passed may the agent submit the corresponding original-project PR/comment. Create the public, minimally necessary *operational* receipt automatically; never demand a redundant user-posted GitHub declaration. Keep any underlying chat identity proof private and reference it only through a verified non-sensitive receipt handle.
5. **Fail closed:** if the current interface cannot furnish genuine signatory attribution or cannot verify required legal-rights statements, record `IN_CHAT_INTENT_RECORDED / IDENTITY_BINDING_UNAVAILABLE / NO_CLA_ACTION`. Continue safe testing, packet preparation and other repositories without claiming an external CLA submission or target acceptance.

**Current Revka example (2026-11-13):** the operator chose individual (not OpenSiro corporate) participation and used `утверждаю` in chat concerning [the source-pinned Revka v1.0 text](https://github.com/KumihoIO/Revka/blob/a1acd826502e12a6c2f3d147e488a7d2982c480b/docs/contributing/cla.md) and [fork-local PR #1](https://github.com/opensiro-contributions/Revka/pull/1) at `75c7adfca75fb30075e75674eb1badc2f6b7c90a`. This records **in-chat intent**, not independently verified identity, personally attested rights or accepted CLA. The Revka registry remains disabled and the third-party PR remains unpublished until the remaining gates are actually satisfied. Do **not** re-ask for an ordinary GitHub comment as a UX workaround.

This defines the desired channel and fail-closed transition; it **does not** activate an unavailable client identity-attestation feature or independently certify that chat alone constitutes a legally valid signature. For any third-party agreement that mandates its own specific action, that target-controlled action remains necessary even when all human-facing decisions occur in chat.

## Read-only cryptographic chat receipt verification (implementation stage)

[Source library](../scripts/cla_chat_attestation.py) and [negative/positive tests](../tests/test_cla_chat_attestation.py) implement **only a cryptographic precheck** for a chat-originating, exact-packet approval. This component does not access the chat client, mint an identity claim, store credentials, perform a PR POST, accept a CLA or set `legal_acceptance_executor_enabled`.

**A genuine provider-origin receipt must contain:** a versioned issuer and subject, `APPROVE` decision and affirmative rights assertion, a packet SHA-256 covering source repository/base, legal counterparty, original CLA text hash, branch/head, signer/capacity and exact acceptance action, issuance/expiry (maximum 10 minutes), a single-use nonce, and a detached Ed25519 signature. Signed bytes use canonical JSON and domain separation; a copied chat transcript, arbitrary GitHub comment, unsigned packet or untrusted self-signed issuer is not admissible.

The verification interface requires **three independently controlled inputs** which must not be authored by the agent as evidence: (a) the client/provider's pinned Ed25519 public key, (b) the provider-subject → actual legal signatory binding, and (c) a durable anti-replay ledger. Ed25519 verification uses the optional `cryptography` package and fails closed if unavailable. The test suite uses a visibly fake local test issuer and never provisions a production trust root.

Even when the cryptographic check succeeds, it returns `VERIFIED_RECEIPT_NON_EXECUTABLE`, **not `ALLOW`**. The future executor must still check live original-project CLA text, real contributor rights/employer permissions, exact template enrolment, source/base/fork heads, required first-party CI, issuer revocation and an **atomic** nonce claim before the third-party submission. Only actual target readback can prove the submitted action, and no result from this library may be promoted automatically to acceptance.

[Historical Revka v1.0 source packet](../data/cla-chat-packets/2026-11-13-revka-v1.json) captures a reproducible digest and the prepared fork-local commit **without storing chat messages or pretending that the operator's earlier in-chat decision is a signed receipt**. It is a historical observation and cannot be replayed as current legal authorization.

**Current platform blocker:** there is no independently verifiable provider signature or identity-linked chat receipt from the ChatGPT client in this workflow. Consequently both CLA execution and original Revka PR submission remain blocked. The owner should not need to repeat approval in a GitHub issue as a workaround; exposing a genuine first-party attestation API would be separate platform/integration work.

## Crash-uncertain single-attempt journal (offline-only)

The [atomic nonce and dispatch journal](CLA_ATTEMPT_JOURNAL.md), [source](../scripts/cla_attempt_journal.py) and [tests](../tests/test_cla_attempt_journal.py) provide local **at-most-one-attempt bookkeeping** for a future independently authorized executor. SQLite `BEGIN IMMEDIATE` ensures concurrent reservation of the same issuer/nonce cannot succeed twice; the first dispatch intent is irreversible, and a timeout remains ambiguous pending independently verified target readback. A recorded PR URL is **not** target confirmation or CLA acceptance.

This is deliberately **not** an execution privilege. It cannot provide a valid human identity binding, enroll exact CLA terms, consume a real provider attestation, check live target terms, call the GitHub API or submit a PR. Its records carry only non-executable state; the current Revka template and public external contribution remain blocked by the missing provider-signed identity channel and unfinished required native CI.

## Initial candidate cases (inactive)

- [Revka CLA](https://github.com/KumihoIO/Revka/blob/main/docs/contributing/cla.md): PR submission itself indicates individual CLA assent; must verify current terms and contributor's legal rights before a PR which triggers assent.
- [Microsoft Fara #96](https://github.com/microsoft/fara/pull/96#issuecomment-6810190721): policy-service reply `@microsoft-github-policy-service agree` is a first-person legal declaration; individual/corporate alternatives are not equivalent. The existing PR is not evidence of accepted CLA.
- [VOLY DCO](https://github.com/voly-codes/voly/blob/main/CONTRIBUTING.md): every commit requires contributor-person `Signed-off-by`. Do not route this through a CLA-bot template.

## Failure handling / evidence

Fail closed on changed wording, terms hash mismatch, identity or company mismatch, missing personal authorization, employer/third-party IP ambiguity, absent CI, unknown public parent, revoked mandates, duplicate/uncertain provider responses, or third-party rejection. Return an exact blocked case to the real signatory; continue with other eligible sources. Never fabricate legal consent or claim target acceptance on local success.

When a real acceptance is later possible, record a dated immutable receipt for the *actual original PR/comment and target check*, plus current and pinned source terms/approval refs; separately retain assessment/native test provenance. Mark it as `SUBMITTED` until independently confirmed, never as human review or VSM grade.

Testing: `python3 -m unittest tests.test_cla_template_gate -v`. The gate is read-only and independent from GitHub authentication.
