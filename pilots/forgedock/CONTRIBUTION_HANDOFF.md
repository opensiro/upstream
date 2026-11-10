# ForgeDock — equal-version GitHub divergence silently loses authoritative state

**Stage:** `AWAITING_EXTERNAL`. A local, exact native-script patch is ready for human-owned external consideration. No external fork/PR, GitHub workflow run, installed agent or provider execution was attempted.

- **Frozen source:** `RapierCraftStudios/ForgeDock@f5bfeeedf6baadd94aea1e6769f69abd45080016` (AGPL-3.0-or-later). Index included `S1=A` under SHA `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`. The VSM assessment motivated checking the first-party phase/state recovery seam; the defect comes from direct `bin/engine/reconcile.mjs` source inspection, not a claimed assessment finding.
- **Need — PASS:** `reconcileState(local, remote)` implements a `GitHub wins on divergence` contract and uses version `v` to choose the advanced side. When local/remote are both present with **equal version but different state**, it unconditionally chooses `local`, silently ignoring GitHub's different authoritative phase or terminal outcome.
- **Mechanism — PASS:** for equal version, compare snapshots with Node's built-in structural equality; if different, return `{ state: remote, action: "hydrate" }`, retaining the existing local path only for actually identical states. Keep the separate local-higher (`remirror`) and remote-higher (`hydrate`) rules.
- **Counterfactual — PASS (bounded):** two new genuine first-party `node:test` cases on identical-version phase and terminal conflicts were RED on pinned original (**5 PASS / 2 FAIL**), then both turned green (**7 PASS / 0 FAIL**). Existing fresh/hydrate/remirror/equal tests remained green.
- **Scope — PASS:** `bin/engine/reconcile.mjs` and its existing `bin/tests/engine-reconcile.test.mjs`; direct Node execution only, no `runner.mjs` calls, model completions, coding agents or external GitHub operations.

## Reproducibility

| Script | Outcome |
| --- | --- |
| `node bin/tests/engine-reconcile.test.mjs` on unmodified frozen source with two added contract cases | 5 PASS / 2 FAIL |
| Same script after one-function change | 7 PASS / 0 FAIL |
| `node --check bin/engine/reconcile.mjs`; `git diff --check` | PASS |
| `git apply --reverse --check` with exact handoff patch in modified checkout | PASS |
| Full ForgeDock suite, process-level crash/failover, Claude/other model, GitHub CI | **Not run / not claimed** |

**Exact patch:** [equal-version-remote-divergence.patch](equal-version-remote-divergence.patch), SHA256 `fa48410f79038108f116c8233a9c2ad5fe3dadf5ec535b3267d87af8e6b32264`, byte-identical to tested source diff.

**Limitations:** The test proves only deterministic tie handling in the reconciliation function. It does not demonstrate that a same-version conflict occurs frequently in a deployed pipeline, nor prove end-to-end recovery or external upstream acceptance. Follow ForgeDock's North Star/dossier rules before any external submission. `continue` advances to Pi Loop Studio.

## 2026-10-25 contributor-rights prerequisite

Current [CONTRIBUTING.md](https://github.com/RapierCraftStudios/ForgeDock/blob/main/CONTRIBUTING.md) explicitly requires a personal DCO sign-off on **every commit** in support of its AGPL-3.0/commercial dual-license business model. The finite OpenSiro publication mandate does not itself constitute the GitHub signatory's legal certification or authorize someone else to sign on their behalf. Current [AGENTS.md](https://github.com/RapierCraftStudios/ForgeDock/blob/main/AGENTS.md) also routes through `NORTHSTAR.md` and authoritative shared command workflow.

**Publication state: BLOCKED by mandatory DCO/legal-rights prerequisite.** No external fork, PR, issue, branch push or fresh native test was run in this pass. The historical RED/GREEN is bounded to the pinned version, not current project certification. Move to the next authorized candidate.
