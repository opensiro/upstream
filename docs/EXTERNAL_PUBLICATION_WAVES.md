# External contribution publication waves

**Owner:** Upstream Contributions, under [Upstream #6](https://github.com/opensiro/upstream/issues/6) and [#56](https://github.com/opensiro/upstream/issues/56). This is an operator grouping rule for existing contribution handoffs, **not** a new source-screening command, automated executor, S5 mandate, external-PR grant or adoption metric.

## Wave contract

When the operator requests external contributions in waves, select **five distinct third-party repositories per wave** from existing source-pinned technical handoffs. Count repositories, not patches or PR URLs. Check against already published external PRs and currently active internal source claims before selection. Preserve the selected identities and their order in a dated reviewable wave report; do not silently substitute a convenient sixth source when a selected case is blocked.

For **each of the five**, independently:

1. Read the current upstream default branch/ref, license text, contribution/security policies, PR template and relevant issues/PRs. Distinguish a historical native test pin from the current source and check for maintainer fixes or duplicate work.
2. Review the actual product-native patch, matched before/after test receipts and any first-party CI gaps. If source has moved, rebase/replay and rerun relevant native tests before claiming current readiness. Do not use live LLM/agent/provider trials as a substitute for deterministic source validation.
3. Apply the target's **own PR form**, requested checks and legal attestations first. Then append the [AI disclosure v2](AI_ASSISTED_PR_DISCLOSURE.md) with the current and historical canonical Index URLs, original `reviewed_at` and `review_ref`. Do not fabricate checks, CLA/DCO approval, human technical review or adoption.
4. Separate `FORK/BRANCH_PREPARED`, `PR_BODY_PREPARED`, `APPROVED_TO_PUBLISH`, `OPEN`, `BLOCKED`, `ALREADY_FIXED` and the eventual external maintainer disposition. The current [prospective human-per-PR gate](CORRECTIVE_PR_PUBLICATION.md) still requires **specific publication approval for each exact title/body**, after final source/template checks. A wave-level request is **not** five individual authorizations; stage-specific fork/branch permissions under #6 also remain effective.
5. Publish a validated, specifically approved PR as **Open · Ready for review**. Use Draft only for an explicitly accepted readiness condition, not to circumvent a mandatory source policy. Never merge into third-party repositories. Register any genuinely created external PR through the applicable reviewable ledger/watchlist change, and continue maintenance after publication.

Return a **five-row report even when zero PRs can be published**. Each row states source ref, license/policy or test gap, exact permission state, source-linked disposition and next allowed action. Blocks stay attached to their original case; resuming them requires the missing evidence/authority. A subsequent wave selects another five distinct candidates without declaring blocked cases rejected or successful.

The technical [`upstream batch` / `upstream upgrade batch`](ASSESSMENT_CANDIDATE_BATCHES.md) five-source screening cohorts remain separate: a screening outcome of `AWAITING_EXTERNAL` is a prepared hypothesis/patch, **not** publication approval. The existing [Upstream Auto](UPSTREAM_AUTO.md) task-reservation prototype does not issue five publication grants or spawn agents.

## Recorded waves

- [2026-11-11 wave 01](../reports/2026-11-11-external-publication-wave-01.md) — five source-first handoffs, no external write.
- [2026-11-11 wave 02](../reports/2026-11-11-external-publication-wave-02.md) — five further handoffs, two publication proposals, no external write.
- [2026-11-11 wave 03](../reports/2026-11-11-external-publication-wave-03.md) — five remaining handoffs reconciled, one publication proposal, no external write.
