# Bounded organization-specific CLA template execution

**Authority source:** [Organization S5 #323](https://github.com/opensiro/vsm-oss-organization/issues/323) and [CLA delegation contract](https://github.com/opensiro/vsm-oss-organization/blob/main/contracts/s5/cla-template-delegation.md).
**Implementation owner:** [Upstream #274](https://github.com/opensiro/upstream/issues/274). **Current transport:** read-only, deny-by-default registry and static preflight only. No automatic legal agreement acceptance is implemented by this document.

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

## Initial candidate cases (inactive)

- [Revka CLA](https://github.com/KumihoIO/Revka/blob/main/docs/contributing/cla.md): PR submission itself indicates individual CLA assent; must verify current terms and contributor's legal rights before a PR which triggers assent.
- [Microsoft Fara #96](https://github.com/microsoft/fara/pull/96#issuecomment-6810190721): policy-service reply `@microsoft-github-policy-service agree` is a first-person legal declaration; individual/corporate alternatives are not equivalent. The existing PR is not evidence of accepted CLA.
- [VOLY DCO](https://github.com/voly-codes/voly/blob/main/CONTRIBUTING.md): every commit requires contributor-person `Signed-off-by`. Do not route this through a CLA-bot template.

## Failure handling / evidence

Fail closed on changed wording, terms hash mismatch, identity or company mismatch, missing personal authorization, employer/third-party IP ambiguity, absent CI, unknown public parent, revoked mandates, duplicate/uncertain provider responses, or third-party rejection. Return an exact blocked case to the real signatory; continue with other eligible sources. Never fabricate legal consent or claim target acceptance on local success.

When a real acceptance is later possible, record a dated immutable receipt for the *actual original PR/comment and target check*, plus current and pinned source terms/approval refs; separately retain assessment/native test provenance. Mark it as `SUBMITTED` until independently confirmed, never as human review or VSM grade.

Testing: `python3 -m unittest tests.test_cla_template_gate -v`. The gate is read-only and independent from GitHub authentication.
