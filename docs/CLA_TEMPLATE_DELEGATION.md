# Bounded organization-specific CLA template execution

**Authority source:** [Organization S5 #323](https://github.com/opensiro/vsm-oss-organization/issues/323) and [CLA delegation contract](https://github.com/opensiro/vsm-oss-organization/blob/main/contracts/s5/cla-template-delegation.md).
**Implementation owner:** [Upstream #274](https://github.com/opensiro/upstream/issues/274). **Unattended template transport:** read-only, deny-by-default registry, cryptographic intent preflight and local SQLite attempt journal. No working client-identity binding or automatic CLA agreement acceptance is implemented. A separate human-directed PR-as-assent route is described below.

## Principle

The owner has authorized a bounded class of AI-assisted CLA actions based on **specific approved templates for specific organizations**. The owner instruction is not approval of any unknown current/future contractual terms. Until a template is independently approved for its exact CLA text and signatory capacity, the existing [standing publication mandate](STANDING_EXTERNAL_PR_PUBLICATION.md) still forbids an invented human legal attestation **for unattended automation**. A target-defined PR-as-assent action with an explicit current-session human instruction is a distinct path, without any invented separate legal-signature requirement.

**Source of truth:** current third-party contributor instructions, actual legal counterparty, the exact CLA content, and independently attributable human approval. A GitHub token, fork ownership, or a populated JSON file is not proof of these. DCO sign-offs are different assertions and are out of scope.

## Version-pinned template enrolment

[Registry](../policies/cla-template-registry-v1.json) contains *candidate descriptions*, NOT signed agreements. For each counterparty, independently capture before activation:

- original GitHub organization/repo, legal entity, CLA version/source URL, SHA-256 of the exact accepted agreement text (after a canonical serialization policy is specified), and effective time;
- individual or authorized corporate capacity, identity and rights/employee/employer claims, supported by the actual signatory;
- exact approved literal GitHub operation (one-time bot reply vs submission-as-assent), and whether it applies to a single repo or a larger explicitly specified project set;
- approval of **the exact content and exact action** in independently verifiable evidence, not an agent-authored comment masquerading as a personally signed document;
- validity (including no expiry where the original terms impose none), revocation and **separate per-action** idempotency key, plus fresh authenticated source/bot readback and a target-side result receipt.

Do not store privileged credentials, confidential employment details or personal contract materials in the public registry. Use public non-sensitive receipt pointers and source hashes.

The included `scripts/cla_template_gate.py` is a **static policy preflight**. It can block unenrolled, wrong-repository, wrong-actor, stale-digest or incomplete approvals. Even when all static fields match, it returns `REQUIRES_INDEPENDENT_LIVE_ATTESTATION_CHECK`, **never permission to sign**. A separate implementation must verify genuine signer authorization, current counterparty terms, target-native contributor requirements, transport credentials and external reply, before any write. No code in this PR performs external `agree` comments, CLA acceptance or PR creation.

## Revka first-party terms observation (inactive, 2026-11-13)

The present [Revka CLA v1.0](https://github.com/KumihoIO/Revka/blob/a1acd826502e12a6c2f3d147e488a7d2982c480b/docs/contributing/cla.md) was fetched verbatim through authenticated GitHub read-only access at source `KumihoIO/Revka@a1acd826502e12a6c2f3d147e488a7d2982c480b`. Its **raw UTF-8 file bytes** (4,055 bytes) had SHA-256 `c6f2f0061d44875d6043530ba2ce0b93a77327dca5672a92787f84afb20de623` on 2026-11-13. This is a **source-content observation**, not consent, signed terms, legal advice, or a reusable credential.

Registry fields `observed_source_ref` and `observed_terms_sha256` are **informational only**. They never substitute for the enrolment-only `terms_sha256`, `signer_capacity`, `signer_approval_ref`, literal `exact_action`, expiry or independent live signatory verification. The Revka template remains `PENDING_EXACT_TERMS_APPROVAL`, the enrolment `terms_sha256` remains `null`, and the executor flag remains `false`.

Opening a PR to `KumihoIO/Revka` already constitutes contributor-person assent under section 9 of the observed first-party CLA; it must not be triggered merely by technical readiness or a generic request to continue. Recheck the current original-repository terms, the human's actual individual/corporate capacity, and exact personally approved rights before any external publication. The [fork-local Revka #1](https://github.com/opensiro-contributions/Revka/pull/1) is not a CLA acceptance to the original project.

## One acceptance, reusable for unchanged repository CLA terms

**Policy:** a valid first-party CLA acceptance is a **repository-scoped, terms-versioned standing consent**, not a per-PR or per-commit approval. Store the accepted combination of `signer`, `individual/corporate capacity`, `original repository`, `legal counterparty`, and exact first-party `terms_sha256` with its authentic first acceptance evidence. So long as these inputs remain unchanged and the consent has not expired or been revoked, **reuse it automatically** for subsequent PRs. A new branch, patch, commit SHA or PR number does not reset the CLA. Do not create an artificial 10-minute, single-use or per-PR expiration for this durable approval.

**Approval lifetime vs operation lifetime:** the short-lived signed chat receipt in [`cla_chat_attestation.py`](../scripts/cla_chat_attestation.py) verifies an initial exact approval event, and the [SQLite attempt journal](CLA_ATTEMPT_JOURNAL.md) guards an individual GitHub dispatch against duplicate sends. Neither determines the duration of the already accepted CLA. Their nonces must not be reused, but the *underlying valid CLA* may be. Subsequent PRs still need normal source-native testing, rights to the new contribution, current target CLA and license checks and the standing publication mandate; **not** a new CLA decision for unchanged terms.

**Reconfirm only on a material change:** CLA text or counterparty, original repository outside scope, individual/corporate signatory change, actual contractual expiration/revocation, or an explicit third-party requirement for a new declaration. If rights to *new code* cannot be substantiated, block that PR independently without pretending a new CLA signature would solve it. DCO `Signed-off-by` remains per-commit.

**Revka:** its [CLA v1.0](https://github.com/KumihoIO/Revka/blob/main/docs/contributing/cla.md) does not specify a fixed expiry or per-PR renewal. On the *first* properly authorized original Revka PR/patch submission, first-party section 9 provides the acceptance mechanism; a verified acceptance can then be reused for later contributions from the same individual while the terms and rights conditions remain applicable. This does not mark our fork-local Revka #1 as accepted or override the current missing trusted first-acceptance evidence.

## Simple direct-chat route for a PR that itself accepts a CLA

The preferred path for individual contributions to an original project whose first-party CLA treats PR creation as acceptance is:

1. In the current active conversation, the human explicitly approves the identified repository, CLA version/text and individual capacity, then requests the specific original-project PR. This is an operational S5 directive in chat, **not** a cryptographically proven identity signature, not broad permission to impersonate the owner and not authorization for another agreement.
2. The agent checks the live original project's exact CLA text, user-approved scope, GitHub authenticated publishing actor, contributor rights/employer statements, unchanged fork head and diff, first-party pre-PR validation, PR template and disclosure. If anything material conflicts, **do not POST**; explain only the actual failed gate. No second GitHub comment or new in-chat approval for unchanged exact terms.
3. The agent submits the actual source-native PR to the original repository using its authenticated account. The original first-party acceptance mechanism—not an agent-made evidence file—governs assent. Read back its original URL, actor, base, head, diff and state; record a non-sensitive operational receipt. Do not assert that this proves independent real-person identity, legal validity or maintainer acceptance.
4. Once original-project first acceptance is confirmed, reuse it for later PRs by that individual under the same CLA text, capacity and repo. Per-PR code rights and CI still apply; DCO remains separate.

**No invented provider-signature prerequisite.** The Ed25519 chat receipt verifier and atomic attempt journal are optional infrastructure for an unattended legal-action executor. The missing ChatGPT provider attestation blocks that unattended route, **not** a PR-as-assent action directly ordered by the human in the current chat where the target requires no separate signature. This interactive route does not activate the automated CLA registry or allow bot agreement comments from an inferred human identity.

**Revka v1.0:** section 9 says no separate individual signature is required and opening the original PR indicates assent. The operator has given the individual approval and explicit publication instruction for KumihoIO/Revka; an authenticated original PR may proceed only when exact first-party rights/validation/readback checks pass. No source submission or accepted CLA is claimed until it actually occurs.

## Chat-only operator approval is the preferred user interface

The contributor may review a **specific current CLA template and outgoing PR packet in their active chat** and reply `Я утверждаю` / `I approve`. **Do not require them to repost that decision in a GitHub issue, PR comment, or other website as a routine second approval.** The agent owns the subsequent GitHub technical actions and publication/audit records when all independently applicable gates pass.

Keep **decision transport** separate from **trustworthy legal-person attribution**:

1. **First-acceptance presentation:** the agent shows the original repository and legal counterparty, first-party CLA URL and immutable text digest/version, individual/corporate capacity, required contributor-rights and employer/patent representations, exact fork branch/commit/files, and the precise third-party action that constitutes acceptance (Revka PR creation; Microsoft Fara bot statement). Disclose whether project rules require CI before PR creation and what validation is unrun.
2. **In-chat decision:** a human reply is an `IN_CHAT_INTENT_RECORDED` event scoped to that displayed packet. A generic `continue`, a preference for chat-only approvals, or an agent's reproduction of the user's words does not bind the person to unseen contracts or modified code. Reask only on materially changed terms/scope or insufficient actual legal-rights representation.
3. **Independent attribution for unattended execution:** before a stored template can initiate a new legal statement without the current human present, a trustworthy client/provider must furnish independently verifiable binding of the chat participant to the intended real human signatory and the exact presented packet, with time and replay protection. **This ChatGPT/GitHub integration does not currently expose such attestation to the CLA executor.** GitHub API authentication as `xLagerFeuer` proves which account the tool can act through, **not** who typed the chat reply or their rights. An AI-authored GitHub comment, claimed chat URL, SHA-256 digest or copied transcript must never be accepted as substitute evidence.
4. **Unattended template execution:** only after the required signatory and rights checks, enabled exact template, current first-party terms/native tests, external-PR publication mandate and destination readbacks have passed may the unattended agent submit a legal agreement action. Direct current-chat PR-as-assent submission uses the separate route above and never authorizes standalone CLA-bot comments. Create the public, minimally necessary *operational* receipt automatically; never demand a redundant user-posted GitHub declaration. Keep any underlying chat identity proof private and reference it only through a verified non-sensitive receipt handle.
5. **Fail closed:** if the current interface cannot furnish genuine signatory attribution or cannot verify required legal-rights statements, record `IN_CHAT_INTENT_RECORDED / IDENTITY_BINDING_UNAVAILABLE / NO_CLA_ACTION`. Continue safe testing, packet preparation and other repositories without claiming an external CLA submission or target acceptance.

**Current Revka example (2026-11-13):** the operator chose individual (not OpenSiro corporate) participation and used `утверждаю` in chat concerning [the source-pinned Revka v1.0 text](https://github.com/KumihoIO/Revka/blob/a1acd826502e12a6c2f3d147e488a7d2982c480b/docs/contributing/cla.md) and [fork-local PR #1](https://github.com/opensiro-contributions/Revka/pull/1) at `75c7adfca75fb30075e75674eb1badc2f6b7c90a`. This records **in-chat intent**, not independently verified identity, personally attested rights or accepted CLA. The Revka unattended registry remains disabled; its original-project PR has not yet been submitted and still depends on current target-native and rights checks, but no invented provider signature is needed for a **live direct-chat command**. Do **not** re-ask for an ordinary GitHub comment as a UX workaround.

This defines the desired channel and fail-closed transition; it **does not** activate an unavailable client identity-attestation feature or independently certify that chat alone constitutes a legally valid signature. For any third-party agreement that mandates its own specific action, that target-controlled action remains necessary even when all human-facing decisions occur in chat.

## Read-only cryptographic chat receipt verification (implementation stage)

[Source library](../scripts/cla_chat_attestation.py) and [negative/positive tests](../tests/test_cla_chat_attestation.py) implement **only a cryptographic precheck** for a chat-originating, exact-packet approval. This component does not access the chat client, mint an identity claim, store credentials, perform a PR POST, accept a CLA or set `legal_acceptance_executor_enabled`.

**A genuine provider-origin receipt must contain:** a versioned issuer and subject, `APPROVE` decision and affirmative rights assertion, a packet SHA-256 covering the exact **first-acceptance action** (source repository/base, legal counterparty, original CLA text hash, branch/head, signer/capacity), issuance/expiry (maximum 10 minutes), a single-use nonce, and a detached Ed25519 signature. Signed bytes use canonical JSON and domain separation; a copied chat transcript, arbitrary GitHub comment, unsigned packet or untrusted self-signed issuer is not admissible.

The verification interface requires **three independently controlled inputs** which must not be authored by the agent as evidence: (a) the client/provider's pinned Ed25519 public key, (b) the provider-subject → actual legal signatory binding, and (c) a durable anti-replay ledger. Ed25519 verification uses the optional `cryptography` package and fails closed if unavailable. The test suite uses a visibly fake local test issuer and never provisions a production trust root.

Even when the cryptographic check succeeds, it returns `VERIFIED_RECEIPT_NON_EXECUTABLE`, **not `ALLOW`**. The future executor must still check live original-project CLA text, real contributor rights/employer permissions, exact template enrolment, source/base/fork heads, required first-party CI, issuer revocation and an **atomic** nonce claim before the third-party submission. Only actual target readback can prove the submitted action, and no result from this library may be promoted automatically to acceptance.

[Historical Revka v1.0 source packet](../data/cla-chat-packets/2026-11-13-revka-v1.json) captures a reproducible digest and the prepared fork-local commit **without storing chat messages or pretending that the operator's earlier in-chat decision is a signed receipt**. It is a historical observation and cannot be replayed as current legal authorization.

**Current unattended-platform blocker:** there is no independently verifiable provider signature or identity-linked chat receipt from the ChatGPT client in this workflow. Consequently **unattended template CLA execution** remains blocked. **This does not by itself block a human-directed original Revka PR under its submission-as-assent clause.** The owner should not need to repeat approval in a GitHub issue as a workaround; exposing a genuine first-party attestation API would be separate platform/integration work.

## Crash-uncertain single-attempt journal (offline-only)

The [atomic nonce and dispatch journal](CLA_ATTEMPT_JOURNAL.md), [source](../scripts/cla_attempt_journal.py) and [tests](../tests/test_cla_attempt_journal.py) provide local **at-most-one-attempt bookkeeping** for a future independently authorized executor. SQLite `BEGIN IMMEDIATE` ensures concurrent reservation of the same issuer/nonce cannot succeed twice; the first dispatch intent is irreversible, and a timeout remains ambiguous pending independently verified target readback. A recorded PR URL is **not** target confirmation or CLA acceptance.

This is deliberately **not** an execution privilege. It cannot provide a valid human identity binding, enroll exact CLA terms, consume a real provider attestation, check live target terms, call the GitHub API or submit a PR. Its records carry only non-executable state. Each nonce controls a single submission attempt, **not the lifetime or reuse of an already valid CLA**; the current unattended Revka template remains blocked by the missing provider-signed identity channel. The human-directed original PR route does not inherit that requirement; its actual source-native checks remain necessary.

## Initial candidate cases (inactive)

- [Revka CLA](https://github.com/KumihoIO/Revka/blob/main/docs/contributing/cla.md): PR submission itself indicates individual CLA assent; must verify current terms and contributor's legal rights before a PR which triggers assent.
- [Microsoft Fara #96](https://github.com/microsoft/fara/pull/96#issuecomment-6810190721): policy-service reply `@microsoft-github-policy-service agree` is a first-person legal declaration; individual/corporate alternatives are not equivalent. The existing PR is not evidence of accepted CLA.
- [VOLY DCO](https://github.com/voly-codes/voly/blob/main/CONTRIBUTING.md): every commit requires contributor-person `Signed-off-by`. Do not route this through a CLA-bot template.

## Failure handling / evidence

Fail closed on changed wording, terms hash mismatch, identity or company mismatch, missing personal authorization, employer/third-party IP ambiguity, absent CI, unknown public parent, revoked mandates, duplicate/uncertain provider responses, or third-party rejection. Return an exact blocked case to the real signatory; continue with other eligible sources. Never fabricate legal consent or claim target acceptance on local success.

When a real acceptance is later possible, record a dated immutable receipt for the *actual original PR/comment and target check*, plus current and pinned source terms/approval refs; separately retain assessment/native test provenance. Mark it as `SUBMITTED` until independently confirmed, never as human review or VSM grade.

Testing: `python3 -m unittest tests.test_cla_template_gate -v`. The gate is read-only and independent from GitHub authentication.
