# Short-form DCO 1.1 sign-off consent (exact-commit scope)

**Status: proposed operator wording and execution checks, NOT an accepted DCO declaration or activated legal delegation.** Owner: Upstream Contributions. Governing technical publication rule: [standing external PR publication](STANDING_EXTERNAL_PR_PUBLICATION.md). This route is **separate** from the [organization-specific CLA template mechanism](CLA_TEMPLATE_DELEGATION.md) and [Organization S5 #323](https://github.com/opensiro/vsm-oss-organization/issues/323).

## Approval card — what the human sees

**Counterparty / original repository:** `voly-codes/voly`  
**Working fork / proposal:** [`opensiro-contributions/voly` PR #1](https://github.com/opensiro-contributions/voly/pull/1)  
**Original unsigned commits in order:**
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

**Current VOLY state at proposal drafting (2026-11-13):** fork-local PR #1 is open at `b42ec77f71560922af17b5160e0bf87238a60fcd`; its recorded first-party full-suite receipt is 1,228 passed / 4 skipped / 1 xfailed / 0 failed. That receipt is historical, not a fresh post-signoff check. **No signer acceptance or external VOLY PR is recorded by this document.**

This document is a compact presentation and operational wrapper for the existing DCO and upstream license. It is not a modified DCO text, a replacement for target legal terms, or legal advice.