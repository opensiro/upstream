# Standing external PR publication mandate

**Owner:** Upstream Contributions S1 under [#6](https://github.com/opensiro/upstream/issues/6). **Attributable parent/owner decision:** [xLagerFeuer, 2026-11-11](https://github.com/opensiro/upstream/issues/6#issuecomment-6801859676). **Machine-readable policy:** [`standing-external-publication-p1.json`](../policies/standing-external-publication-p1.json).

The owner has **delegated the routine decision to submit subsequent third-party pull requests**. This prospective, continuing and revocable mandate **supersedes the 2026-11-09 exact-per-PR conversational approval requirement**. It is not limited to the historical finite Corrective cohort. An agent must **not ask the owner to approve each qualifying proposal or every five-source wave again**.

## Scope and checks

The authorized stage is `submit_external_pr` only for a validated, source-native contribution from an `opensiro/...` branch in an authentic **public, direct** `opensiro-contributions/<target>` fork into its matching original third-party repository. The matching fork-local PR remains the single authoritative unpublished title/body proposal. Publication defaults to **Open · Ready for review**; Draft requires a real target-permitted readiness limitation and truthful disclosure.

Before **every** publication, independently verify:

1. Live source and fork default/head SHAs, exact branch diff, parent identity, actor permissions, absence of duplicate or already-fixed work, and no unintended files or secrets.
2. Current first-party license, `CONTRIBUTING`, issue/PR, security, assignment, CLA/DCO, branch and PR-template rules. Never invent or implicitly accept a contributor-person legal attestation.
3. Appropriate deterministic native RED/GREEN and first-party checks. Distinguish checks actually passed from missing or skipped checks; if the target requires a check **before PR publication**, block rather than pretending the PR is ready.
4. Current target PR form and [AI disclosure v3](AI_ASSISTED_PR_DISCLOSURE.md), including both current and immutable Index assessment links, `reviewed_at` and `review_ref`. Do not claim human code review, fully autonomous research results or upstream acceptance.
5. The real POST/creation result and fresh provider readback of the resulting PR, matching fork head, base, title, body and state; then register the PR in an attributable dated publication receipt and the explicit maintenance watchlist.

The mandate transfers the **publication decision**, not third-party repository merge rights, default-branch write rights, legal attestations, unrelated comments/issues, secrets management or the power to waive source-native requirements. External maintainers alone decide whether to accept and merge. The owner can revoke or narrow this mandate by an attributable decision and matching policy update; on contradictory or unavailable live policy, stop the publication and report the actual blocker.

## Implementation and evidence boundary

Read the **current default-branch policy** and owner decision before any publication, and use an authenticated tool/host for the exact verified GitHub action. This policy file and this document alone are **not** evidence of a working autonomous executor, successful PR POST, verified product improvement, or a VSM autonomy grade. An available publisher must check the exact candidate and record the external result. If the needed executor or mandatory technical evidence is unavailable, continue preparing other cases without requesting another general permission.

The earlier `standing-preparation-p1.json` remains a separate **time-bounded fork/patch grant**; it must not be broadened or used as the authorization for `submit_external_pr`. [Publication wave contract](EXTERNAL_PUBLICATION_WAVES.md), [working-fork pipeline](CONTINUOUS_WORKING_FORK_PIPELINE.md), and [Upstream #56](https://github.com/opensiro/upstream/issues/56) remain the operating route.
