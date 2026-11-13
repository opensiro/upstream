# Short-form DCO 1.1 sign-off consent (exact-commit scope)

**Status: reusable exact-commit operator procedure with an explicitly historical example; this file is NOT a fresh DCO declaration, legal delegation, or blanket consent.** Owner: Upstream Contributions. Governing technical publication rule: [standing external PR publication](STANDING_EXTERNAL_PR_PUBLICATION.md). This route is **separate** from the [organization-specific CLA template mechanism](CLA_TEMPLATE_DELEGATION.md) and [Organization S5 #323](https://github.com/opensiro/vsm-oss-organization/issues/323).

## Reusable card — every new packet needs its own attestation

Show the contributor the **current** source/repository, license and unaltered DCO 1.1, exact unsigned commit SHAs **and content tree hashes**, verified signer name/email and rights/capacity, proposed branch and expected head, and any explicitly approved mechanical transformations. Do not reuse historical SHAs or a free-floating “Я утверждаю”.

When adding a sign-off changes a functional commit SHA used by a later `fix.md` entry, explain this prospective one-reference update **before asking for permission**, then verify that the final tree differs only by that approved mechanical reference. Any changed code, changed terms or additional unapproved commits require fresh consent.

Keep `PREPARED`, `PERSON_ATTESTED_EXACT_SCOPE`, `SIGNED_HISTORY_READBACK`, `EXTERNAL_PR_PUBLISHED` and `MAINTAINER_DECISION` separate. Technical publication mandates and GitHub credentials never establish the contributor's legal right to sign.

## Chat-first DCO approval interface (no duplicate GitHub user post)

A trusted assistant client may present the exact DCO 1.1 contribution card in the current chat and receive `Я утверждаю` / `I approve` **there**. The signatory does not have to manually repeat that decision as a GitHub comment merely for convenience; if all required verifications pass, the agent performs the scoped GitHub actions and stores minimally necessary provenance.

This is a **channel preference**, not blanket future DCO consent. The actual approval must still be bound to the signatory's independently verified identity, exact unsigned commits/trees, DCO and target license text, authorized sign-off `Name <email>`, any permitted mechanical rewriting, and time. Provider-attested user identity and a genuine attributable exact-scope decision are distinct from a connected GitHub actor, an AI-generated GitHub comment or a text digest of a chat transcript. If this client does not provide the needed independent attribution, record `IN_CHAT_INTENT_RECORDED / IDENTITY_BINDING_UNAVAILABLE` and **do not sign or publish on that basis**.

A third-party project may require a specific DCO trailer or legal acceptance mechanism irrespective of the chat channel; the agent must fulfill it only after the personal-assent and technical gates, never by claiming a chatbot preference waives target requirements. This chat-only UX rule is shared with [CLA template delegation](CLA_TEMPLATE_DELEGATION.md), but DCO and CLA remain separate agreements.

## Historical original approval card — superseded VOLY history

**Counterparty / original repository:** `voly-codes/voly`  
**Working fork / proposal:** [`opensiro-contributions/voly` PR #1](https://github.com/opensiro-contributions/voly/pull/1)  
**Original unsigned commits in order (historical; no longer the live branch):**
- [`311f0b468697d47f9ac5f84312202a4bcb10870c`](https://github.com/opensiro-contributions/voly/commit/311f0b468697d47f9ac5f84312202a4bcb10870c)
- [`b42ec77f71560922af17b5160e0bf87238a60fcd`](https://github.com/opensiro-contributions/voly/commit/b42ec77f71560922af17b5160e0bf87238a60fcd)

**Terms being acknowledged:** [Developer Certificate of Origin, version 1.1](https://developercertificate.org/) (unaltered text); target [CONTRIBUTING.md](https://github.com/voly-codes/voly/blob/main/CONTRIBUTING.md), which requires a sign-off **on each commit**; target [Apache License 2.0](https://github.com/voly-codes/voly/blob/main/LICENSE). These first-party documents must be rechecked at the exact publication base, not accepted from this example alone.

**Signer:** an independently authenticated natural person, with their own explicitly verified `Name <email>` sign-off identity. A GitHub username or existing Git commit author alone does not prove the human's identity or rights.

### Short agreement

> **I confirm the following for each of the two exact commits identified above.**
>
> 1. I have the right to submit the contribution under the original project's applicable Apache-2.0 terms, and I personally certify that the applicable alternative in DCO 1.1 section (a), (b) or (c) is true, together with section (d). I am not asserting rights I do not hold or authority for an employer or other rights holder without authorization.
> 2. I understand that submitting a contribution under Apache-2.0 can involve copyright and patent license grants under that license; this confirmation is not a separate copyright assignment or a new, independent CLA. Applicable original-project terms control.
> 3. I understand that the contribution, sign-off identity and public Git history may be retained and redistributed indefinitely as stated in DCO 1.1.
> 4. I authorize the OpenSiro agent **only** to add my verified `Signed-off-by: Name <email>` trailer to **each of these exact commits**, preserve their source trees/diffs, update the existing fork branch safely, and submit a third-party PR **only if** all technical, legal, target-policy and standing-publication gates independently pass.
> 5. This approval is **not** a blanket approval for future commits, changed code, other repositories, corporate attestations, CLA acceptance, or third-party merges. If the target terms or substantive commit contents change, obtain fresh person-specific assent.

**Short reply mechanism:** after a trusted interface presents this exact card and terms, the signer may reply **“Я утверждаю” / “I approve”**. The interface must bind the reply to this displayed card, verified signer identity, exact original commit SHAs, unmodified DCO version and applicable source policy. A free-floating chat phrase, reusable account-wide setting, bot statement or unauthenticated issue comment **does not** establish acceptance.

## Required machine-enforced execution boundary

1. **Before asking:** read back the source and fork, the two commit objects, diff/trees, target license/contribution rules, any rights exceptions, identity and the live branch head. Provide the signer with the complete exact scope above. If rights are uncertain, stop and request a personal determination; an agent cannot decide a person's legal entitlement.
2. **Consent evidence:** require a trustworthy, attributable current-session decision from that actual human, bound to the exact card (including signer name/email, repository, SHAs, terms/version and acceptance time). Record a minimally necessary durable reference/digest, without inventing identity or disclosing additional private data. **This document and a hash alone are not proof of consent.**
3. **After consent:** reverify unchanged old objects and branch head; rewrite **only commit messages** to append that person's exact trailer to both commits, retaining original authorship and **identical content trees and patch scope**. Any other change, unexpected conflict, or history mismatch is fail-closed. Use safe expected-head/CAS update and read back the new commits; record original-to-signed SHA mapping.
4. **Before external PR:** independently rerun applicable source-native gates and the target's current PR template, license, DCO/CLA and standing publication policy. Verify the fork-local proposal and new head; never call a changed history automatically approved just because a previous one was.
5. **Audit outcome:** distinguish `PROPOSED`, `HUMAN_ATTESTED`, `COMMIT_MESSAGES_SIGNED`, `EXTERNAL_PR_PUBLISHED` and `MAINTAINER_DECISION`. No later state can be inferred from an earlier one. Do not claim deployment or third-party acceptance.

## Completed VOLY example — 2026-11-13

The first unsigned pair above was individually attested and signed, but **superseded** once the source's same-commit documentation and `fix.md` requirements were checked. It cannot authorize changed content.

The corrected pair received a **new exact-scope contributor-person DCO confirmation**: unsigned functional commit `d7728a1c26f6413f20daac757113ac8d49ea3730` and follow-on `fix.md` commit `247f0f1a8b4a8231d65abdc8aca5a95aaf8b6854`. Their final DCO-signed objects are [`840a7344ed6c07396ff661868b8219af02044098`](https://github.com/opensiro-contributions/voly/commit/840a7344ed6c07396ff661868b8219af02044098) and [`649a3fac6b11f0cbc20ea091bed4184cb8b39352`](https://github.com/opensiro-contributions/voly/commit/649a3fac6b11f0cbc20ea091bed4184cb8b39352). The second tree differs from the unsigned candidate **only** by the `fix.md` reference to the newly signed functional SHA.

The exact signed head passed `1,228` first-party Python tests (4 skipped, 1 expected failure, 0 failures), the documentation-link gate and environment-documentation gate. [Original-project VOLY #20](https://github.com/voly-codes/voly/pull/20) was actually published as **Open, Ready for review**; its title/body/head matched [fork-local #1](https://github.com/opensiro-contributions/voly/pull/1). [Upstream #281](https://github.com/opensiro/upstream/pull/281) merged the dated GitHub publication readback and maintenance target. This is **not** evidence of third-party maintainer acceptance, merge, deployed benefit or autonomous legal-person identity verification.

[Revka CLA](https://github.com/KumihoIO/Revka/blob/main/docs/contributing/cla.md) is a different instrument: submission itself signals copyright/patent and contributor-rights consent. VOLY DCO approval is **not** Revka CLA authorization.

This is a historical evidence summary, not a reusable person's signature.

This document is a compact presentation and operational wrapper for the existing DCO and upstream license. It is not a modified DCO text, a replacement for target legal terms, or legal advice.