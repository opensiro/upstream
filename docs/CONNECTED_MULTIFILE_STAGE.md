# Exact two-file prepare stage — host-only source contract

**Status:** source implementation + offline tests; **NOT ACTIVATED**.
Owner: [Upstream #6](https://github.com/opensiro/upstream/issues/6),
[#28](https://github.com/opensiro/upstream/issues/28).
This is a **new, narrower two-file port**. It does not expand the older
[`connected_stage_adapter.py`](../scripts/connected_stage_adapter.py),
which still only creates one new test file.

## What this implementation does

[`scripts/connected_multifile_stage.py`](../scripts/connected_multifile_stage.py)
defines `prepare_exact_two_file_patch(...)` for **one production source file
that already exists** and **one new package-local test file**. It accepts a
bounded exact text patch, source and working fork identities, pinned
`source_sha == base_sha`, proposed new `opensiro/*` contribution branch,
preimage SHA-256 of the existing production file, postimage SHA-256 of
both files, and a SHA-256 of **the entire patch bytes**.

All of the following are required before the host may authorize:
- The proposal passes `preview_draft` and selects **only**
  `prepare_contribution`; any unresolved proposal blocker prevents writes.
- Current authenticated provider observation confirms active, public
  licensed source and direct public fork under `opensiro-contributions`,
  matching source/fork name, authenticated `push=true`, and host-attested
  exact GitHub actor/capability.
- Source and fork bases are **at the identical reviewed SHA**. This is
  intentional: a stale fork must first be reconciled **outside** this
  stage. Any moving-base drift, existing contribution branch, preimage
  modification or existing test file blocks.
- The patch includes exactly these two paths, adds the test, has no
  binary/rename/copy/delete, and matches its pinned digest.
- The trusted host first returns a **nonprimitive opaque authenticated
  `verify_exact_prepare(intent)` grant**, binds the actual actor,
  proposal/scope hashes, both branch SHAs and complete pre/post fingerprints,
  then approves the **one-use stage** via
  `authorize_exact_stage(grant, intent)`.
- The module performs a second complete provider preflight **after**
  the decision. It never manufactures authority from a packet, approval
  text, PAT presence, issue, comment or `continue`.

After authorization, a **trusted host-injected** provider must implement
`publish_patch_commit(repo, base_sha, branch, patch_text,
exact_paths, expected_postimage_sha256)`. Its contract requires a
single **atomic externally visible branch+commit update**, only if the branch
was absent, with exact paths and local postimage verified **before the
remote ref write**. Never force-overwrite, reuse a changed target, or retry
an ambiguous write. The module independently re-GETs branch SHA, direct
commit parent, changed file list and contents of both final paths before
returning `PREPARED_VERIFIED`.

An error from the write port yields `UNKNOWN_AFTER_WRITE`,
`auto_retry=false`; a failed/missing/mismatched remote readback yields
`PENDING_VERIFICATION`, also not a success or an automatic retry.

## What it does NOT do

The module is **not a live host executor**: it neither supplies
`verify_exact_prepare` nor an authenticated GitHub patch-writing port.
A Python test fake can simulate any decision, so unit tests are **not**
proof of a real authorization, token or fork write.

Do not expose a CLI `--execute`, install an unattended Actions POST,
pass a token through the arguments, or call this module with
`lambda _: True` as an issuer. An actual VM/host implementation must
enforce identity, one-use/expiry/revocation and credential isolation in
its own trusted boundary. The actual GitHub actor for the API transport
must be the actor to which the grant was issued.

The existing [HarnessDesk V2 packet](../pilots/harnessdesk-1772/prepare-v2-handoff.json)
is **`ACTION_PREPARED_NOT_AUTHORIZED`**. That packet is a dated evidence
snapshot and **must not be rewritten as an approval**. The existing fork
`development` is behind the source and must be reconciled by an
independently authorized operation. The external upstream PR still
requires a separate human publication decision and is not in scope.

## Offline test coverage

[`tests/test_connected_multifile_stage.py`](../tests/test_connected_multifile_stage.py)
tests one simulated atomic commit and negative cases: missing/fake grants,
unselected/blocked proposal, stale branch, wrong parent/license/push rights,
path traversal/extra file/bad checksum, unexpected preimage, denial/drift
before writing, non-atomic/ambiguous failures and remote readback mismatches.
The real [V2 patch](../pilots/harnessdesk-1772/tool-gateway-ownership-fix-v2.patch)
has also been passed through the exact two-path parser. This is only a
**contract and mock verification**, not a real fork write or external PR.
