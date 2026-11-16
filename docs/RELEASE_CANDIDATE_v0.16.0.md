# Upstream v0.16.0 — consolidated release candidate

**Status: DRAFT FOR OWNER AGREEMENT; NOT A PUBLISHED RELEASE.** Prepared 2026-11-16. One coordinated GitHub Release is proposed, rather than separate releases for the three already merged intermediate protocol revisions.

| Reference | Verifiable state at preparation |
| --- | --- |
| Last published GitHub Release | [v0.13.0](https://github.com/opensiro/upstream/releases/tag/v0.13.0), tag commit `dd896d43af6aee0100e921ad01be3634d73efb8c` |
| Current consolidated candidate | `VERSION=0.16.0` on `main`; pre-draft baseline `2231b05e0824b967c1822892a2139a74c06e9f5c` |
| Release publication | **Not approved or performed**; no `v0.16.0` tag or Release observed at preparation |
| Final immutable release SHA | **TO BE VERIFIED after owner agreement**, including final release-policy/review changes and passing checks |

## Proposed single release summary

This package consolidates the live, source-backed changes **since the last published v0.13.0 release**. It is not a claim that the intermediate v0.14.0/v0.15.0 GitHub Releases existed.

1. **Capability-first Upgrade and scoped batch modes** — [PR #7](https://github.com/opensiro/upstream/pull/7), [v0.14.0 history](../changes/v0.14.0.md). `upstream upgrade` prioritizes a demonstrable new original-harness task/output, original baseline, source-native falsifier and appropriate S1/S2/S3/S3*/S4/S5 hypotheses; `upstream batch [N]` remains technical/repair screening. A batch is not a quota of patches or PRs.
2. **Popularity-first distribution without GitHub batch bookkeeping** — [PR #9](https://github.com/opensiro/upstream/pull/9), [v0.15.0 history](../changes/v0.15.0.md). Among screenable candidates, prefer original projects with more publicly verified unique contributors, stars as a labeled fallback. One distinct-source research turn before repeats; subsequent 1×–2× rank preference or operator-selected uniform. Research batches produce **chat reports**, not a new issue/PR/frozen cohort per run.
3. **License/formalities first and human decision inbox** — [PR #10](https://github.com/opensiro/upstream/pull/10), [v0.16.0 history](../changes/v0.16.0.md). Verify original source/license text, contributor rules, CLA/DCO and restrictions **before ranking popularity**. Preserve read-only `SCREENABLE_READ_ONLY`, `HUMAN_GATE_PENDING`, `INSUFFICIENT_EVIDENCE` dispositions without auto-clearing legal rights. Introduce the internal [Human gate form](https://github.com/opensiro/upstream/issues/new?template=human-gate.yml) for genuine deduplicated human rights/access decisions, **not** for batch reporting.
4. **Source-dated external PR activity and read-only calendar** — [PR #6](https://github.com/opensiro/upstream/pull/6) and [PR #8](https://github.com/opensiro/upstream/pull/8). One-shot `scripts/activity.py` derives published/merged/closed-unmerged and approved-closure subset from original GitHub PR/review readbacks; distinct per-day visual bands, strict incomplete-snapshot checks and a static report. [Documentation and calendar](ACTIVITY.md). The already released v0.13 aggregator is reused, not reinvented.

## Dated, bounded activity snapshot — *not* a live outcome claim

At **2026-11-16 12:00 UTC**, [the recorded snapshot](ACTIVITY.md) covered **60 verified fork metadata branches**, **61 independent improvement records** and **42 unique linked original-repository PRs**: **11 merged / 24 open / 7 closed without merge**; **0** of the seven had explicit `APPROVED` reviews. The counts are dated, partial and are **not** new verified benefit, completion percentages, adoption or a second KPI. Original GitHub repositories remain authoritative for live PR statuses.

## Unchanged controls and acknowledged limits

- Detailed working history belongs in verified `.opensiro/` on the fork's independent `opensiro/meta` branch; original GitHub owns PR events; Upstream presents derived snapshots.
- The bounded historical migration is reconciled and [issue #2](https://github.com/opensiro/upstream/issues/2) closed, **not** proof that every research-only or unmapped historical source was migrated. The `verified_external_outcomes` producer/Organization cutover and website sync are **not established**.
- `upstream upgrade` phrases are **chat operator routes, not installed CLI subcommands** or an autonomous universal runner.
- Prior v0.8–v0.11 native-first, independent runner and working-fork evidence remains historical; no new cross-project native validation claim is made by this release.
- Fork `DORMANT / PAUSE / STOP`, original license/CLA/DCO, protected branch rules and **exact current-conversation owner consent before any third-party public post** still apply. No new legal delegation, third-party rights, automatic PR publication or autonomous VSM grade.
- The current v0.14/v0.15/v0.16 change packages and their integration commits remain public historical evidence. **Do not rewrite, relabel, delete or backdate them.** One v0.16.0 GitHub Release may summarize them together without pretending earlier Releases existed.

## Owner agreement / publication checklist

- [ ] Owner agrees the **complete scope and final notes**, including legal/consent and outcome caveats; version `v0.16.0` is the proposed consolidated number.
- [ ] Re-read latest `main`, original `v0.13.0` release tag, existing `v0.16.0` tag absence, any concurrent changes and the exact intended immutable integration SHA.
- [ ] Run `python3 scripts/validate_contract.py` and `python3 -m unittest discover -s tests -v` at the **final** integration SHA; verify `VERSION`, `CHANGELOG`, and `changes/v0.16.0.md` agree there.
- [ ] With authorized tooling and confirmed owner release instruction only, create an immutable `v0.16.0` tag pointing at the reviewed final commit, then **one GitHub Release** with these combined notes. Verify tag/ref and Release via first-party readback.
- [ ] Once actually published, update any stale **candidate-specific** status text separately; do not invent a success or tag before the GitHub readback.

## Future release cadence

New normative edits may be proposed and reviewed under an **Unreleased** changelog section **without** changing `VERSION` or creating a separate SemVer package/tag for each small edit. When a coherent bundle is agreed by the owner, the single final release PR chooses the next SemVer number, publishes the consolidated change package, validates it, and only then may a GitHub Release be created. Mere merge into `main` or completion of a chat batch is **not** consent to release.
