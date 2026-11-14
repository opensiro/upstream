# Upstream contribution protocol — SemVer change packages

**Current version:** [`0.7.0`](VERSION) · [Versioning policy](VERSIONING.md)

This history covers **protocol-relevant** changes, not every merged PR, new screening row, generated view, external PR or fix. Each package links the actual historical main-branch checkpoint and the PRs that changed how contributions are selected, validated, prepared, authorized or published.

**Historical integrity:** Versions `0.1.0` through `0.6.0`, including `0.5.1`, were **assigned retrospectively on 2026-11-14**. Their dated Git commits are real snapshots, **not evidence that releases or SemVer tags existed on those dates**. The first newly recorded version is `0.7.0` at the versioning integration commit; its last pre-versioning protocol checkpoint is PR #298. Retrospective tags, if published, identify historical snapshots without rewriting them. No frozen pilot or batch provenance is backfilled.

## [0.7.0](changes/v0.7.0.md) — Post-source probes and falsified-dependency safeguards

Historical checkpoint: [`781781a436`](https://github.com/opensiro/upstream/commit/781781a4364d553305b468e74e8a0e725c511c05) · 2026-11-13 through 2026-11-14

- Require an observable **post-source scoped probe** for each of the six upgrade functions. Pre-source `NO_SUPPORTED_HYPOTHESIS` is provisional; `CLOSED_NO_CHANGE` needs native evidence, while blockers name their next falsifiable check ([#297](https://github.com/opensiro/upstream/pull/297)).
- Separate optional ranked issue/PR leads and discovery feasibility from source-native four-PASS need/fit admission and independent before/after validation; retain source rights and publication gates ([#297](https://github.com/opensiro/upstream/pull/297)).
- When a proposed defect depends on third-party SDK/driver/HTTP status or exception behavior, **verify the actual supported dependency method, version and observed result before accepting `need=PASS`**. A fake-only RED→GREEN cannot establish a reachable product defect ([#298](https://github.com/opensiro/upstream/pull/298)).
- Correct the archival interpretation of [KnowWork #4](https://github.com/knowflow-ai/KnowWork/pull/4): real `docker-py 7.2.0` `APIClient.start()` returns normally for HTTP 304; the injected `APIError(304)` hypothesis is `need=FAIL`. Preserve frozen evidence and do not re-publish that unsupported change ([#298](https://github.com/opensiro/upstream/pull/298)).

## [0.6.0](changes/v0.6.0.md) — Six-function multifunction upgrade coverage

Historical checkpoint: [`faf9356967`](https://github.com/opensiro/upstream/commit/faf935696781a80f211a4c14911b84a7f6aa888f) · 2026-11-13 (after 0.5.1 checkpoint)

- Remove the accidental S1=A / S2=C-only discovery restriction for **schema-v2** upgrade cohorts; include all canonical Index `status: included` sources regardless of ownership state and do not fabricate `function: S2` ([#292](https://github.com/opensiro/upstream/pull/292)).
- Keep explicit legacy `--schema-version 1` only for historic A/C → S2 discovery; do not modify frozen legacy manifests or VSM assessment output ([#292](https://github.com/opensiro/upstream/pull/292)).
- Require **S1, S2, S3, S3*, S4 and S5** to be inspected for every included upgrade source: an immutable six-function pre-source matrix and six function-level dispositions in the post-source summary. Thus ten sources mean **60** function reviews, not ten single-function guesses ([#295](https://github.com/opensiro/upstream/pull/295)).
- Use the first ten-source schema-v2 batch as a dated screening exercise, not proof that any particular feature or fix passed native gates ([#293](https://github.com/opensiro/upstream/pull/293)).

## [0.5.1](changes/v0.5.1.md) — Direct-chat PR-as-assent CLA correction

Historical checkpoint: [`877c6aefef`](https://github.com/opensiro/upstream/commit/877c6aefefc73f2a5c9535e1ad46fd0489ab0691) · 2026-11-13 (after 0.5.0 checkpoint)

- Correct an **invented ChatGPT-provider signature prerequisite** for the limited case where the original first-party individual CLA makes an original-project PR itself the acceptance event, with a direct instruction by the human in the current chat ([#290](https://github.com/opensiro/upstream/pull/290)).
- Preserve the live checks of exact first-party terms, individual capacity, contributor-rights representations, authenticated GitHub actor, source-native tests, fork provenance, template and external PR readback ([#290](https://github.com/opensiro/upstream/pull/290)).
- Continue fail-closed unattended CLA template execution and prohibition on standalone bot `agree` actions; do **not** claim independently cryptographic real-person identity certification ([#290](https://github.com/opensiro/upstream/pull/290)).

## [0.5.0](changes/v0.5.0.md) — Feature-first screening, exact-native adaptation and guarded CLA work

Historical checkpoint: [`fa43ae7ec3`](https://github.com/opensiro/upstream/commit/fa43ae7ec3de3f545d46976e5e3bab7477a513a3) · 2026-11-11 through 2026-11-13

- Expand bounded source-native patch adapters to source/test pairs in an operator-mcp Python module while preserving exact patch hashes, path guards and fork provenance ([#255](https://github.com/opensiro/upstream/pull/255), [#256](https://github.com/opensiro/upstream/pull/256)).
- Implement deterministic read-only Index cohort discovery and reject overlapping frozen assessment batches in required CI ([#270](https://github.com/opensiro/upstream/pull/270), [#271](https://github.com/opensiro/upstream/pull/271)).
- Prioritize **minor/major native product capabilities** during `upstream upgrade batch`, retaining genuine bug-fix fallback when no qualified new capability is supported ([#277](https://github.com/opensiro/upstream/pull/277)).
- Add an assessment-hypothesis **quality readback** that distinguishes prospective origin, native `need`, runner verification, negative screens, source evidence and maintainer outcomes without inventing a success KPI ([#283](https://github.com/opensiro/upstream/pull/283)).
- Document individual CLA/DCO chat approval boundaries and a deny-by-default, **non-executing** legal template registry; add optional signed-intent verifier and durable single-attempt network-operation journal without treating a GitHub credential or bot text as legal consent ([#275](https://github.com/opensiro/upstream/pull/275), [#285](https://github.com/opensiro/upstream/pull/285), [#286](https://github.com/opensiro/upstream/pull/286), [#287](https://github.com/opensiro/upstream/pull/287)).
- Fix immutable CLA reuse: a valid, unchanged source-defined agreement is not forced to expire with a per-PR nonce or short-lived authorization receipt ([#288](https://github.com/opensiro/upstream/pull/288)).

## [0.4.0](changes/v0.4.0.md) — Five-source preparation and standing publication mandates

Historical checkpoint: [`fa806c1286`](https://github.com/opensiro/upstream/commit/fa806c12862abea1cf03d63f1849dc9e4bdf67cd) · 2026-11-10 through 2026-11-11

- Enforce **matching contributor-fork ownership of new external native CI** while retaining Upstream-owned observation and governance workflows ([#215](https://github.com/opensiro/upstream/pull/215)).
- Delegate routine, bounded five-repository fork/patch **preparation** under a revocable, host- and actor-scoped mandate, without per-source reapproval; preserve one-use technical checks and block unauthorized writes ([#216](https://github.com/opensiro/upstream/pull/216), [#230](https://github.com/opensiro/upstream/pull/230)).
- Keep PR proposals on actual working forks and require exact source / fork head, base, diff, provenance and post-POST source readbacks before recording an external publication ([#217](https://github.com/opensiro/upstream/pull/217)).
- Replace per-PR human **publication** prompts with a distinct, standing, revocable mandate for fully qualified contributions; do **not** transfer external merge, CLA/DCO attestations or permission to skip native gates ([#223](https://github.com/opensiro/upstream/pull/223)).
- Correct stale generated workspace routing so it checks the effective standing publication policy instead of falsely requiring a second manual owner approval ([#248](https://github.com/opensiro/upstream/pull/248)).

## [0.3.0](changes/v0.3.0.md) — Fork-local source-of-truth, target PR requirements and AI disclosure

Historical checkpoint: [`0ff30e4820`](https://github.com/opensiro/upstream/commit/0ff30e4820a82661a3df7252bc55b51f642e5e9c) · 2026-11-08 through 2026-11-10

- Connect a frozen source pool and historical native pilots to a collision-aware contributor-fork workspace registry; document supervised fork creation without asserting an unattended executor ([#191](https://github.com/opensiro/upstream/pull/191), [#193](https://github.com/opensiro/upstream/pull/193), [#194](https://github.com/opensiro/upstream/pull/194), [#195](https://github.com/opensiro/upstream/pull/195), [#196](https://github.com/opensiro/upstream/pull/196)).
- Make source license and contributor-policy evidence a **first-class intake preflight**, rather than assuming a technically plausible patch is publishable ([#111](https://github.com/opensiro/upstream/pull/111)).
- Require the **original repository's current PR template**, contributor instructions and DCO/CLA gates; default a qualified PR to **Open · Ready for review**, with Draft only for a documented target-permitted reason ([#200](https://github.com/opensiro/upstream/pull/200), [#201](https://github.com/opensiro/upstream/pull/201)).
- Require an AI-assisted contribution disclosure with canonical and immutable assessment anchors, reviewed date/source revision, actual tests and honest provenance ([#203](https://github.com/opensiro/upstream/pull/203)).
- Make the matching `opensiro-contributions/<target>` fork the canonical home of source-native branch, tests and the **one unpublished fork-local PR proposal**; Upstream holds only evidence, decisions and externally observed receipts ([#210](https://github.com/opensiro/upstream/pull/210)).

## [0.2.0](changes/v0.2.0.md) — Index-first intake, strict-derived evidence, and runner boundaries

Historical checkpoint: [`dd990d48e8`](https://github.com/opensiro/upstream/commit/dd990d48e8ab390a64020a300f08e25c1b85c620) · 2026-10-26 through 2026-11-08

- Make **assessment-first, source-disjoint five-source batches** an explicit Upstream route, with honest `AWAITING_EXTERNAL`, `BLOCKED_EVIDENCE` and `CLOSED_NO_CHANGE` dispositions; distinguish Upstream screening from Index publication ([#143](https://github.com/opensiro/upstream/pull/143)).
- Separate `upstream batch` (may be assessment-informed) from **`upstream upgrade batch`** (prospective assessment-derived hypotheses). Freeze the Index finding and falsifiable prediction **before inspecting current upstream issues/source**; prevent hindsight relabeling ([#171](https://github.com/opensiro/upstream/pull/171), [#173](https://github.com/opensiro/upstream/pull/173)).
- Require an independent deterministic runner / first-party before-and-after receipt to claim a strict derived benefit; place new external harness native CI in authorized contributor forks or separate runners rather than Upstream control-plane Actions ([#171](https://github.com/opensiro/upstream/pull/171), [#175](https://github.com/opensiro/upstream/pull/175)).
- Introduce read-only batch/collision preflight, opt-in Git compare-and-swap source reservations and bounded Upstream Auto parallel task claims without inventing execution or PR rights ([#151](https://github.com/opensiro/upstream/pull/151), [#162](https://github.com/opensiro/upstream/pull/162), [#165](https://github.com/opensiro/upstream/pull/165)).
- Add stable repository-wide offline integrity CI independently of target-specific pilot workflows ([#148](https://github.com/opensiro/upstream/pull/148)).

## [0.1.0](changes/v0.1.0.md) — Corrective publication and first-party PR maintenance

Historical checkpoint: [`e0fe0f240e`](https://github.com/opensiro/upstream/commit/e0fe0f240e26a4125177c172b9eb08aff19e59df) · 2026-10-23 through 2026-10-26

- Introduce a **finite, explicitly authorized** publication lane for 34 already-evidenced Corrective cases; publishing a contributor PR is separate from claiming an original-project merge ([#109](https://github.com/opensiro/upstream/pull/109)).
- Add hourly external-PR readbacks: maintainer review and comments, edited feedback, merge conflicts, check conclusions, deduplicated observations and a tracked target set ([#126](https://github.com/opensiro/upstream/pull/126), [#127](https://github.com/opensiro/upstream/pull/127), [#133](https://github.com/opensiro/upstream/pull/133)).
- Reconcile published external PRs against the source-pinned corrective queue and maintenance coverage, without retroactively granting publication to new cases ([#128](https://github.com/opensiro/upstream/pull/128)).

## What does not cause a protocol version bump

Routine new candidate/Index batches, proposal count changes, live PR status observations, CI runs, regenerated dashboards and immutable historic corrections that do **not** change the operative contribution procedure have their own Git SHA and evidence lineage. They are **not** separate SemVer releases.

For the one-time reconstruction policy and future bump rules, see [VERSIONING.md](VERSIONING.md).
