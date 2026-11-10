# KnowWork — assessment-derived S2 improvement handoff

**Status:** `AWAITING_EXTERNAL` — implementation/test artifacts prepared internally; **no external PR, external fork mutation, or maintainer publication has been authorized by this batch**.

- Source: `knowflow-ai/KnowWork` Apache-2.0, [pinned baseline `033b492`](https://github.com/knowflow-ai/KnowWork/tree/033b49240ec49c7b8d3b43f1783b9b4d89425b5e). The canonical [Index assessment](https://github.com/opensiro/vsm-harness-index/blob/da98a140b1c6541f639c1dc4094bf2aeaacdb08d/assessments/kn/knowwork.md) records S2=C.
- Origin: `ASSESSMENT_DERIVED`, bounded cross-process sandbox **start** race after [independent hypothesis checkpoint](https://github.com/opensiro/upstream/commit/5ddeba928a62829d1951f3380d728920ff63ec01). The target already handled name/create-409 conflicts; this is a distinct path.
- Native regression: [`native-regression.patch`](native-regression.patch) (SHA256 `30702f011b0487580fc9fd58e2253f5afacaabaf1d82344eef97765a13139192`), two variants (existing-created, newly-created).
- Candidate fix: [`native-fix.patch`](native-fix.patch) (SHA256 `fcc24402da2b1dc7219fbed9098b3a893d54728620a6bc069f5a56f3bf6b60ca`) confirming same-ID running state after a peer wins start; no unrelated architecture changes.
- Evidence: [first-party deterministic independent RED/GREEN receipt](INDEPENDENT_HOST_RECEIPT_2026-11-10.md); 2/2 RED before, 2/2 GREEN after, 34/34 relevant lifecycle checks PASS.

**Prospective maintainer-facing PR:** apply both patches atop the pinned source, rerun tests on the target's current revision, verify any newly introduced lifecycle behavior, and publish only after a separately authorized external contribution decision. For a published external PR, include the currently required OpenSiro disclosure v2, assessment link and date, explicit AI autonomy/error limitations, and the precise nature of the user's present manual monitoring. Do not imply that current manual gate is permanent or that the patch is proven on real Docker.

**Stop conditions:** if the target has already independently addressed the start race, if current source API semantics changed, if the license changed, or if genuine start failures are swallowed, re-screen before publication. The native fixture deliberately models an interleaving; a real deployment should be validated by the maintainer as appropriate.
