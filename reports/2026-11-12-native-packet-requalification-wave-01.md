# Current-source native packet requalification - wave 01 (2026-11-12)

Owner: opensiro/upstream issue 56. This is technical evidence, NOT a fork write, external PR, maintainer adoption, or VSM grade claim. Frozen candidate batches remain unchanged.

| Original repository | Current source HEAD | Exact selected patch SHA256 | Fresh source-native replay | Other remaining checks |
|---|---|---|---|---|
| kstawiski/evidence-gated-scientific-agent | 85b396a824dfad6ec0880cbe07d86d3e24920ae8 | 0974cdefa228cfdf37e1b750144e01c269c8f2dee6d9aa8ea01e86dd79b23646 | BEFORE 15 pass/1 fail; AFTER 16 pass/0 fail | Whole uv pytest non-live gate not yet run; fork-local PR absent |
| microsoft/fara | a675d6d61c41c47ae87bacefeab22caad18e3e84 | fce42386bd6b1cf1ea0fed6c22a206589239cdeeb37f53cfaa48eb027da9002e | BEFORE 2 pass/1 fail; AFTER 3 pass/0 fail | Broader first-party tests and Microsoft CLA/policy review not complete; fork-local PR absent |
| ScaleML/AgentSPEX | db99b7b6802fe15ef2997c82ec1d49e5228128f6 | Not selected | Old patch applied to exact source; pytest collection blocked by missing python-dotenv | First-party environment and feature fit |
| howl-anderson/agentsilex | cd529f2838151fd8a4f0d6b7054a45d829b3f78d | Not selected | Old patch applied to exact source; pytest collection blocked by missing litellm | Evaluation environment and broad baseline |
| agentuniverse-ai/agentUniverse | f69b130bacaa784289ec8dc2a9798d122cd8fe5a | Not selected | Old source 114 commits behind, comparison shows no changes to four proposed patch files | Fresh patch replay, native tests, maintainer consultation |

## Source-native execution receipts

Executed 2026-11-12 via connected dev-alpha-2 SSH gateway on isolated shallow clones of the original GitHub default branches, Python 3.12.3, pytest 7.4.4, and an isolated Pydantic >=2.11 installation. Authenticated GitHub actor: xLagerFeuer.

Evidence Bench: original SHA equals the canonical Index review_ref; reviewed_at 2026-10-17; original Apache-2.0 LICENSE and CONTRIBUTING inspected. Current first-party CONTRIBUTING welcomes focused narrow deterministic policy fixes and proposes the broad non-live test suite. Test-only patch against pristine original yielded 15 passes, 1 failing negative test, because status=error counted successful and admitted a failure URL. Exact production patch yielded 16 passes, 0 failures on tests/test_policy.py. Original and patch SHA and git apply --check / diff --check verified. No model or live retrieval performed.

Fara: original SHA equals the canonical Index review_ref; reviewed_at 2026-10-17; first-party MIT LICENSE inspected, root CONTRIBUTING and common PR templates absent. On pristine original, test-only patch yielded 2 passes and 1 failing mismatch test, because existing checkpoint reused a task with a different task_id. Exact production patch yielded 3 passes and 0 failures on tests/test_run_context_resume_identity.py. Source SHA, exact patch SHA, apply and diff checks verified. No browser, model, or benchmark performed.

Archived patch bytes are identical to source-only OpenSiro draft PRs 120 and 121, independently re-executed in this session, not accepted automatically from those drafts. No unpublished PR-body draft was copied into Upstream. Existing direct public forks for Evidence Bench and Fara matched original main SHA at preflight. Matching-author third-party external PR search found no published proposal for any of the five, which does not establish global semantic nonduplication.

Host filesystem usage reached 99 percent (about 1.9 GB free). No first-party broad CI, source-native fork CI, actual fork commit, external PR POST, third-party merger, deployment, or strict assessment-derived causal completion is claimed.

Next: review this exact technical packet and pass Upstream integrity. On merged main, independently verify effective standing mandates, GitHub actor, source and fork SHAs, license/contributor policy and native completeness before issuing an exact one-use preparation decision. Ineligible cases remain blocked within this fixed five-source wave.
