# GitHub REST Git Data two-file patch port — source prepared, inactive

**Owner:** [Upstream #6](https://github.com/opensiro/upstream/issues/6)
and [#28](https://github.com/opensiro/upstream/issues/28).
**Status:** REST provider implementation with offline-only tests.
**NOT** an installed authenticated VM executor or an actual fork write.

## Architecture

[`scripts/rest_multifile_patch_port.py`](../scripts/rest_multifile_patch_port.py)
implements the GitHub provider interface required by
[`connected_multifile_stage.py`](../scripts/connected_multifile_stage.py)
without embedding PATs, GitHub CLI authentication, an automatic approval
issuer, or a standalone `--execute` entry point.

The **existing credential-owning VM/host** must inject all three components:

1. **`api(method,path,body)`**: authenticated GitHub REST transport,
   returning exact HTTP status and parsed JSON. The actor must be the
   real principal that will write Git objects. A 403 must never be
   reported as a 404.
2. **`capability_attestor(owner)`**: reads authentic provider actor and
   rights to edit the specific destination; returns an attested
   `{owner,actor,available,authorized}` dictionary. A proposal's
   `authorized: true` is not a valid attestation. The stage also
   verifies target fork `permissions.push=true`.
3. **`materializer(repo,base_sha,patch,paths)`**: in an isolated,
   clean checkout of the **exact** pinned base, perform
   `git apply --check` and `git apply`, inspect actual staged
   paths, reject symlink/submodule/mode changes, and compute UTF-8
   postimages and source file modes. It must return precisely
   `{base_sha,changed_paths,source_file_modes,files}`; each new regular
   file is `100644`. The port checks these bytes against all
   expected postimage SHA256 values **before** any REST POST. A fake
   materializer is valid only for offline tests.

All three are **host capabilities**, not fields inside the pilot packet
or artifacts that can authorize themselves. The actual
`host.verify_exact_prepare()` and `host.authorize_exact_stage()`
methods must independently establish an operator decision, one-use
enforcement, expiry/revocation and action binding before invoking any
mutating provider method.

## Atomic public-branch creation

After host authorization and the stage's twice-run preflight:

1. `GET /repos/{fork}/branches/{branch}` — existing branch **blocks**;
   only verified 404 means absence.
2. Materialize the exact patch locally and validate only the **two**
   allowed paths and SHA-256 postimages, without network writes.
3. `GET /repos/{fork}/git/commits/{base_sha}` to recover the exact
   base tree. A missing or malformed tree blocks.
4. `POST /repos/{fork}/git/trees` creates a tree from that base with
   only the two exact UTF-8 `100644` blobs.
5. `POST /repos/{fork}/git/commits` creates one commit with parent
   exactly `base_sha`.
6. `POST /repos/{fork}/git/refs` creates the **new** `refs/heads/opensiro/*`
   reference. This is the **only externally visible branch update**,
   and GitHub rejects existing refs instead of overwriting them. No
   `PATCH /git/refs`, force, delete or automatic retry exists here.

Intermediate tree/commit objects may be orphaned if the final ref POST
fails; that is **not** a successful contribution. The stage returns
`UNKNOWN_AFTER_WRITE` on an exception or
`PENDING_VERIFICATION` if the post-write GET cannot independently
confirm exact new branch/parent/two file paths and both remote contents.
It is forbidden to retry automatically after an ambiguous result.

## Scope and remaining blockers

The [HarnessDesk V2 handoff](../pilots/harnessdesk-1772/PREPARE_V2_HANDOFF.md)
remains `ACTION_PREPARED_NOT_AUTHORIZED`; its fork's
`development` SHA was behind external source at last authenticated read.
This port does **not** synchronize that fork, clear manifest blockers,
create an issuer, or transfer local-only credentials to this runtime.

The only automatic remote write implemented in the provider **requires**
an authenticated host grant and a successful current-base preflight. Until
a real host transport/materializer/capability attestor **and** trusted
grant issuer are installed and verified, no PR or other production code
is permitted to call the write path. Never infer live rights from mock
unit tests, token presence or a prior one-off fork operation.

External upstream PR submission is **still a separate human-owned
publication action**, not part of this provider.

## Tests

[`tests/test_rest_multifile_patch_port.py`](../tests/test_rest_multifile_patch_port.py)
covers both read and write REST shape, order (tree → commit → ref),
no overwrite, provider status handling, 403-vs-404, invalid file encoding,
wrong postimages/modes, malformed commit/tree, empty/missing attestor and
zero retry. These are fake, offline provider tests.
