# Proposed external outcome decision — Agent Fleet native lease contract

**Status: REVIEW REQUESTED — NOT ACCEPTED.** Parent: [Upstream #159](https://github.com/opensiro/upstream/issues/159). Ledger mechanism: [PR #176](https://github.com/opensiro/upstream/pull/176).

Evidence observation: [read-only workflow #42496755046](https://github.com/opensiro/upstream/actions/runs/42496755046), `2026-11-08T15:49:58+00:00`. [Artifact #13624300312](https://github.com/opensiro/upstream/actions/runs/42496755046/artifacts/13624300312) downloaded and checked. Source SHA256 `e32c7c4ee85d94a0b0245cd8ac869b1ed958614942905700a57db51febc51955`; cohort SHA256 `9ec745b1a73ce49ece1bea7b3c3ac844bb9bfe80bfe2dbc74c48a2819d472adf`.

This packet is **agent-prepared review material**, not independent S3* evidence, a reviewer sign-off, deployed user benefit, or an Organization KPI. The source record and live observation remain machine `VERIFIED` **candidates**. Its proposed scope is **merged change only**, with `benefit_claim=NOT_MEASURED`.

Reviewer must check the linked first-party evidence and decide explicitly. Approval of the separately merged decision PR (with exact evidence markers) is required before an `accepted-v1.json` entry can cite that approval. Rejection or missing evidence leaves the entry absent.

## First-party evidence

- External contributor PR: [chankov/agent-fleet #43](https://github.com/chankov/agent-fleet/pull/43); actor `xLagerFeuer`, head fork `opensiro-contributions/agent-fleet`, base `chankov/agent-fleet`.
- Third-party maintainer merge on `2026-10-24T20:47:51Z`, by `chankov`, merge commit `212bbf6e2f26addb24c448070f8c8ac404da376e`.
- Exact published and merged head both `9647f07e88384fd9360c4d98a0d2ba18f63606de`; no post-publication head drift.
- [Exact upstream-native CI run #40093167700](https://github.com/opensiro/upstream/actions/runs/40093167700): completed/success, head `ac3c154739c196df6b279292bbdb52a4b0100b7e`, linked internal [PR #119](https://github.com/opensiro/upstream/pull/119).
- Source publication record: [`data/improvement-publication/2026-10-24-01.json`](https://github.com/opensiro/upstream/blob/db1d7b1453e0c8e2eaf15564d76e65d686642650/data/improvement-publication/2026-10-24-01.json). It records `product_user_benefit=NOT_MEASURED`.
- External merged diff updates the writer-lease implementation plus a race test, worker fixture, test runner and changeset; it does **not** prove deployment, productivity or user benefit.

## Reviewer decision

- [ ] Verify independent upstream-maintainer merger and exact author/fork identity.
- [ ] Verify published and merged head are identical.
- [ ] Verify successful native CI linked to internal PR and matching source record.
- [ ] Accept **only the attributable merged patch outcome**, or document reason to hold/reject.
- [ ] Confirm no runtime deployment, productivity, autonomous S3* sign-off or VSM regrade is claimed.

**Proposed ledger record after a genuine accepted review:** `intervention_id=improvement:agent-fleet-native-lease-contract`, `decision=ACCEPTED_MERGED_CHANGE_ONLY`, `benefit_claim=NOT_MEASURED`, external PR #43, merge SHA above, native CI URL above. No ledger entry should be committed by this packet alone.
