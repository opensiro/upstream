# OpenSiro — Corrective Upstream PR Publication (new-session handoff)

Continue the existing external Corrective PR publication lane of [OpenSiro Upstream #56](https://github.com/opensiro/upstream/issues/56), *not* a new assessment batch, new proposal-only simulation or new VSM organizational domain. Work through the 34 verified source-native technical packets **serially** and publish eligible external Draft PRs using the bounded owner-confirmed delegation.

## Mandatory bootstrap

1. Read [VSM-OSS START_HERE](https://github.com/opensiro/vsm-oss-organization/blob/main/START_HERE.md) → `docs/ECOSYSTEM.md` → `docs/AGENT_CONTROL_PLANE.md`.
2. Read the **current main** of [opensiro/upstream](https://github.com/opensiro/upstream), [#6](https://github.com/opensiro/upstream/issues/6), [#56](https://github.com/opensiro/upstream/issues/56), and especially:
   - `docs/CORRECTIVE_PR_PUBLICATION.md` (bounded authority/stop conditions);
   - `data/corrective-publication/2026-10-23-01.json` (finite 34-case queue);
   - `docs/ORGANIZATION_FORK_UPSTREAM_PR.md` (authenticated fork/PR handoff);
   - `docs/ASSESSMENT_TO_IMPROVEMENT.md` (origin/evidence limits).
3. Run `python3 scripts/corrective_publication_queue.py validate` to ensure all existing `SUBMITTED`/`MERGED` Corrective PRs are monitored, then `python3 scripts/corrective_publication_queue.py next` to select the current first `QUEUED` case. **Do not rely on historical first-candidate names:** published submissions may have advanced the queue. The baseline commit and 34 IDs are frozen: do not silently repin or add unreviewed batch-11 candidates.

## Standing publication authority — 2026-10-23

OpenSiro owner `xLagerFeuer` expressly confirmed delegation of **public fork creation, nondefault work-branch push, and external upstream Draft PR submission** for the **34 listed Corrective cases without per-case reconfirmation**. This supersedes earlier manual publication routing only inside this finite set, **subject to authenticated actor/provider permissions and project policies**. External maintainers alone own acceptance and merge. Do not transfer Organization S5 or admit Upstream as a fourth bounded S1 domain (Organization #274 remains separate). Revocation or a contrary explicit owner instruction stops new writes.

## Repeat for each queued case

1. Inspect its **real pinned original** `pilots/<case>/CONTRIBUTION_HANDOFF.md`, patch, relevant tests and frozen Index assessment. Refresh the third-party upstream default/target branch and check license, `CONTRIBUTING`, issue assignment, existing issues/PRs and overlap. If the defect is already fixed, the upstream denies contributions, CLA/DCO cannot be truthfully satisfied, or evidence is insufficient, record the exact blocker/closure and **advance to the next case**.
2. Reproduce the actual first-party RED on relevant current source, apply the minimal production patch plus regression test, then run matched GREEN and available first-party **native deterministic script/CLI tests**. **Never run live LLM-agent sessions, model providers, Browser agent-quality trials, benchmark episodes or simulated model-task experiments.** Report missing toolchains/dependencies without inventing a PASS.
3. Read back the authenticated GitHub identity, org rights and exact source/fork parent. Use only a verified **public** `opensiro-contributions/<repo>` direct fork, one `opensiro/` contribution branch, and nondefault base/head SHAs. Current ChatGPT GitHub connector has PR creation but may not expose fork creation; the configured credential-owning VM/host previously had `gh` + PAT. Use legitimately configured access if actually available. **Never request/copy a token into chat or bypass a denied tool permission.** No made-up branch, fork, successful write or agent.
4. Run the live read-only `scripts/upstream_pr_handoff.py` preflight where possible (branch exists, fork direct-parent, `push=true`, nonempty comparison, no duplicate PR). On a real PASS, publish one **external Draft PR** by a supported authenticated GitHub action. Record exact PR URL and number, authenticated actor, source/base/head SHAs, native test receipt and CI status in the separate publication ledger **and register the same PR in** `data/pr-maintenance/targets.json` **within the same reviewable change**. The hourly maintenance monitor must cover every submitted Corrective PR. Do **not** confuse an internal OpenSiro PR with an external upstream PR. Never merge an external PR or make an unsupported DCO/CLA attestation.
5. On recoverable ordinary errors, repair and retry within the same bounded case. On real permission, policy, author-license, missing operation or protected-branch blocker, mark that case `BLOCKED` with evidence and continue the **next case**. Do not pause for minor questions or wait for a maintainer's asynchronous review. If every case is terminal, summarize genuine submitted/open/merged/closed outcomes. Preserve historical batch manifests and origin classification (`ASSESSMENT_INFORMED`, not retrospectively derived).

## Output and working cadence

Report `DONE / NOW / BLOCKED / NEXT / NEED YOU` concisely, linking **actual** GitHub PRs and tests. `продолжай` resumes this **Corrective publication queue** and moves to the next candidate after a completed/blocked case; it does not silently switch to assessment-batch-11 screening. Continue independently in large bounded iterations, but do not claim writes without GitHub readback or override a genuinely ungranted permission.
