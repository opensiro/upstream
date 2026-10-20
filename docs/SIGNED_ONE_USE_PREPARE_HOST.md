# Operator-signed prepare grant: implementation boundary (inactive)

**Status: source-only, NOT INSTALLED / NO OPERATOR SIGNATURE / NO EXTERNAL FORK WRITE.** Owner: [Upstream #6](https://github.com/opensiro/upstream/issues/6). This is an optional verification component for the existing two-file stage contract; not a new Control Plane, plugin, hosted bot, or source of authority.

## What is actually implemented

[`SignedOneUsePrepareHost`](../scripts/signed_one_use_prepare_host.py) implements exactly the existing `verify_exact_prepare(intent)` / `authorize_exact_stage(grant, intent)` host interface. It never signs or issues a grant and cannot create a GitHub ref by itself. It consumes an **externally issued** signed JSON envelope containing the canonical exact-intent SHA-256, issuer and subject actor (`xLagerFeuer` in this pilot), action-specific audience (`opensiro/upstream:prepare_contribution`), a random 128-bit grant ID, an explicitly enrolled public-key fingerprint, and issued/expiry timestamps with a strict **15-minute maximum**.

Verification uses `/usr/bin/openssl` on a root-owned non-group/world-writable Linux system binary and root-owned parent directories, with a restricted subprocess environment and disabled environment-sourced OpenSSL config. It checks the signature, caller-supplied intent digest, bound actor and scope, time window and revocation by signed file removal/replacement. The opaque in-memory object is not itself the signed permission. Immediately before authorization the envelope is verified again; an atomic SQLite transaction records the grant ID as consumed, even if the subsequent GitHub writer fails. A consumed grant must never automatically be retried.

The single-file adapter is unchanged. The two-file stage separately rechecks authenticated GitHub refs and file preimages **after** one-use host authorization, and validates the eventual atomic patch-write readback. A successful signed-host test with a `FakePort` is **not** a real GitHub mutation or a human approval.

## Mandatory independent trust boundary — not present on the current VM

An execution agent with arbitrary shell access as `robot`, GitHub PAT/CLI write credentials and write access to the verifier code or its configuration **cannot constitute its own independent authorization authority**. File mode 0600, a known public-key digest or SQLite transaction does **not** establish resistance to that same OS principal changing files, reverting the ledger or calling GitHub directly. Consequently, **do not activate this code with signer, trusted-key metadata, grant folder and replay ledger all under `robot`'s control**.

For activation, a distinct trusted host/OS principal or comparable protected host service must independently own **all** of the following, outside the executor's write privileges:

1. Operator public-key enrollment, pinned fingerprint and expected actor. No agent-proposed or repo-provided key may self-enroll. The operator keeps the private signing key off the VM and never places it in GitHub, a chat, an agent tool argument or shared filesystem.
2. The canonical exact action shown to the operator, its independently authenticated consent/signature channel, signed-envelope delivery and effective revocation before consumption. The holder must sign *only* the bounded `prepare_contribution` intent, including both source/fork SHAs, the new branch, paths, patch hash, pre/postimages, selected proposal and scope hashes.
3. Protected replay ledger with effective rollback prevention, one-use claim and expiry checks. This implementation's SQLite storage is a **local mechanism**, not a remote or cross-privilege security guarantee.
4. Authenticated GitHub transport and a policy-enforced writer limited to the approved contributor fork, scoped Git Data commit/tree/new-ref calls, no force push or external `POST /pulls`. Recheck actor, issue/source/fork refs, hashes and provider capability immediately before write.
5. Evidence receipts after attempted writes, including unknown/partial outcomes and no automatic retry. External PR publication remains separately human-owned.

The current `zhdanov` execution principal does **not** satisfy these protections. There is no enrolled owner key, effective signed stage grant, protected issuer or live runner. The source code and its tests **must never be invoked with a generated test fixture or a permissive fake as a real grant**.

## Test scope

`python3 -m unittest discover -s tests -v` covers signed-grant negative cases (wrong issuer/key/actor/intent, altered signature, expiry, missing/replaced envelope, replay), fixed OpenSSL invocation against hostile `PATH`/`OPENSSL_CONF`, and a two-file core integration using an ephemeral **test-only key** plus a simulated atomic GitHub port. These results establish source behavior, **not** external authorization, live operator attribution, or fork preparation.

Until a trusted issuer and host boundary are separately reviewed and demonstrably effective, the only legitimate result of a live exact stage is `BLOCKED_NO_WRITE`. The existing dated [HarnessDesk shared-commit handoff](../pilots/harnessdesk-1772/PREPARE_SHARED_CURRENT_20261020.md) remains non-authorizing.
