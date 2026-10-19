# P1 scope preflight — source-only integration surface

**Status: OFFLINE / NOT CONNECTED / NOT GRANTED.** This is a bounded policy verifier proposed as implementation support for [Upstream #6](https://github.com/opensiro/upstream/issues/6) and [OSM design PR #19](https://github.com/opensiro/upstream/pull/19). It does **not** issue a P1 mandate, create a GitHub branch, stage changes, publish a PR, or prove organizational autonomy. The current exact-item `prepare_contribution` gate remains in effect.

`scripts/osm_p1_scope.py:preview_p1_scope(grant, intent, trusted_host=...)` checks:
- an explicit issued-claim shape, concrete agent execution identity, exact fork/repository allowlist, bounded branch/path and **prepare-only** operation;
- finite UTC grant lifetime of no more than 30 days;
- a **trusted execution host** providing the actual actor, UTC time and independently confirmed current issuer grant digest, identity and revocation status;
- no external PR publication, fork creation, default-branch mutation, unsafe paths or arbitrary repository scope.

An on-disk `status=ISSUED` value is **not** issuance: host attestation is mandatory and never furnished by the proposal author or this Python file. FakeHost-based positive tests prove only the code's conditional logic. `SCOPE_PRECHECK_ONLY_NOT_A_WRITE_AUTHORIZATION` is a non-execution receipt, **not** a write grant or a GitHub preflight. Current P1 is `PROPOSED_NOT_GRANTED`; therefore no real execution is permitted through this code.

This module deliberately does **not** wrap, modify or activate `connected_stage_adapter.py`. A future host integration must separately verify real repository rights, source contribution policy, true branch/path state, exact action bytes/content, branch protection, authenticated issuer/actor, and per-operation revocation before *every* mutation. It must still preserve partial-write and unknown-outcome stop conditions, and the manual external PR publication right.

Review/validate with `python3 -m unittest discover -s tests -p 'test_osm_p1_scope.py' -v`. Acceptance of a source-only mock test cannot be cited as S1=A, an effective delegation, or a completed upstream contribution.

## Proposal-to-preflight integration (offline)

The optional `scripts/osm_p1_pipeline.py:preview_p1_pipeline(...)` composes the actual `batch_proposals.preview_draft` selection, the **non-authorizing** `preview_p1_scope` check, and the existing `connected_stage_adapter._preflight` repository **reads**. It constructs the P1 intent from the exact proposal action, not from separately supplied text, and only accepts one `prepare_contribution` candidate. The result is always `PIPELINE_PREVIEW_ONLY_NO_GITHUB_WRITES` and `can_execute=false`. There is **no execute or write adapter** on this path.

`tests/test_osm_p1_pipeline.py` uses synthetic issue metadata, an explicitly fake issuer-host and fake GitHub reads to cover positive composition and fail-closed deviations (unissued/revoked/mismatched grant, wrong workspace, altered source/license, push denial, base drift, branch/file collision, blocked candidate and external stage). No test result claims a real owner decision, live connector authorization, or actual upstream contribution. Run the full existing test suite through the repository's GitHub CI. Do not use this preview receipt to bypass Upstream #6's exact-stage gate.
