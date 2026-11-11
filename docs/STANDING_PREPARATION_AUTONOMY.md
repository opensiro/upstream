# Standing autonomous preparation mandate

**Owner:** Upstream [#6](https://github.com/opensiro/upstream/issues/6) ·
**Owner-directed instruction:** [2026-11-11 issue record](https://github.com/opensiro/upstream/issues/6#issuecomment-6799137559) ·
**Policy:** [standing-preparation-p1.json](../policies/standing-preparation-p1.json).

The owner delegates routine `create_public_fork` and `prepare_contribution`
decisions to Upstream Contributions S1 **without per-repository or per-action
conversational approval**. This policy **does not itself** delegate
`submit_external_pr`, which now has a [separate standing publication mandate](STANDING_EXTERNAL_PR_PUBLICATION.md). Each wave consists of five distinct external source
repositories, not five future PR titles. Agents may select eligible handoffs,
implement source-native code and regression tests, create/reuse matching public
direct forks **only in `opensiro-contributions`**, prepare dedicated
`opensiro/...` working branches, run native CI and assemble unpublished
PR packages autonomously.

## Per-stage checks, not per-stage human approvals

1. The connected execution host reads the owner policy and generated source
   registry from the **same pinned current `opensiro/upstream/main` commit**.
   It verifies `ACTIVE`, actor, execution host, owner decision link, expiry
   and revocation, and binds the selected five-source wave. Editing a local
   JSON, an agent message or an arbitrary `approved_by` does not activate it.
2. Every **member selected for an actual fork/patch write** must independently have
   an eligible, source-pinned `AWAITING_EXTERNAL` handoff, a matched patch hash,
   reviewed licensing and a unique destination. A blocked member remains in
   the reported five-source wave but does not block a separate eligible member.
   The blocked member still cannot receive an execution decision. Ambiguous
   patches, same-name fork collisions and license conflicts remain stopped
   until evidence resolves them.
3. Before each fork or patch **write**, the provider-authenticated actor
   and permissions, current source/license/policy, public direct-parent fork,
   pinned source/base/branch SHA, patch and prior work are rechecked.
   New branch creation must not overwrite an existing ref. Updating an
   existing branch requires a safe compare-and-swap operation. A partial
   unknown result requires read-only recovery before any retry.
4. The host automatically issues **opaque one-use execution decisions**
   beneath the standing mandate. These bind individual operations but
   **do not ask the user again**. The available `dev-alpha-2` path may
   handle fork creation if its actual authenticated GitHub identity and
   destination permissions check out. Other supported GitHub writes may
   use the connected GitHub integration.
5. Keep technical evidence, source pins and lifecycle receipts in
   `opensiro/upstream`, but keep the code and target PR diff in the matching
   `opensiro-contributions` fork. Do not open internal Upstream PRs solely
   to park future third-party PR prose.

The corresponding [host helper](../scripts/standing_preparation_mandate.py)
supplies an automatic callback to the already-existing fork adapter and a
two-step opaque grant to the exact two-file patch adapter. Its current-main
policy reader, negative tests and actor/scope validation are **not proof**
of a live fork or patch. The exact two-file patch adapter cannot yet update
existing branches or write arbitrary multi-file corrections. The standing
decision is effective as policy; each operation remains executable only
when actual host credentials, provider methods, native tests and safe-write
mechanisms are available. An unavailable capability is a
`WAITING_FOR_TRUSTED_EXECUTOR` **technical block**, never a need for
another human preparation approval.

This is a finite, revocable owner-governance contract, **not a sandbox
against misuse of a host's unrestricted PAT**. Do not confuse a mock
callback, a passing unit test, a source registry entry or an existing
fork with a provider-attested real execution.

## Decisions still reserved

- **Every external PR:** exact final title/body, tested fork diff, current
  source-native PR form and AI disclosure still require independent verification,
  but **no longer a separate human approval** under the current [publication policy](STANDING_EXTERNAL_PR_PUBLICATION.md).
  Qualified, validated external PRs default to Open/Ready, not Draft.
- **Legal attestations:** CLA, DCO and other contributor-person statements
  require the actual authorized person's attestation; agents may not invent
  one.
- **External maintainers:** alone control review and merger into their code.
- **Other writes:** no protected/default-branch edits, force pushes,
  deletions, unsolicited maintainer contact or policy/permission expansion.
  Revocation or expiry on current main immediately denies later preparation.

The separate publication mandate never supplies an extra fork-write permission,
and this preparation mandate never authorizes an external PR POST.
