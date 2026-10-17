# StarNet — live station status for the lead

- **Upstream:** [androoAGI/starnet](https://github.com/androoAGI/starnet)
- **Contributor fork:** [xLagerFeuer/starnet](https://github.com/xLagerFeuer/starnet)
- **Upstream issue:** [#55](https://github.com/androoAGI/starnet/issues/55)
- **Original contributor PR:** [#56](https://github.com/androoAGI/starnet/pull/56), still **open** and not merged at the 2026-10-17 check.
- **First-party upstream implementation:** [`dc9633b`](https://github.com/androoAGI/starnet/commit/dc9633bb05434e236509583cd1b226140f8d3f67), authored by upstream maintainer @androoAGI on 2026-10-07, explicitly stating **idea by @xLagerFeuer**.
- **Product-native fit:** **pass** (experimental ledger 2026-10-12).

## Real upstream need and solution

StarNet had an authoritative page-side `station.status` snapshot but did not expose it as a normal lead-facing model tool. This made it harder for the lead to report which sessions were busy or waiting for approval without guessing from its own context. Its [existing orchestration plan](https://github.com/androoAGI/starnet/blob/fbddbf992f8e7082196f07c3024781fcf1c276fc/docs/VOICE_ORCHESTRATION_PLAN.md) called for the same read-only verb.

The upstream maintainer's implementation reuses `VoiceLive.statusSnapshot()`, the station bridge and lead/orchestrator capability allowlist, returns REFUSED when a page cannot answer, and adds tests. It additionally declares the tool deferred. On the current upstream `feat/harness-backend` branch, the implementation is present.

## Critical distinction

This is an **upstream-adopted idea**, **not** a merged contributor PR and not proof that the maintainer merged @xLagerFeuer's source commits. Keep the original PR history and its current lifecycle distinct from the maintainer's own commit; do not reapply an already-implemented duplicate change.

**Gate result (ledger):** all four fit gates pass, independently of the OpenSiro grade. [Canonical experimental observation](https://github.com/opensiro/vsm-oss-organization/blob/main/experiments/upstream-intervention-fit/observations.json).
