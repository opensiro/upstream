# Bounded external Improvement publication — 2026-10-24

**Status:** two external PRs originally published as Draft; **both changed to Ready for review on owner follow-up instruction (2026-10-24)**, verified from GitHub. This is *not* a change to the canonical Index, an Organization S1 admission, an accepted upstream merge, or evidence of live model productivity.

**Owner decision:** [VSM-OSS #287](https://github.com/opensiro/vsm-oss-organization/issues/287), `IMPROVEMENT-PUBLISH-2026-10-24-01`, following the 2026-10-24 operator instruction to formalize a **two-case S5-limited mandate**. The linked issue is executor-authored on the operator's active public GitHub account; it is not asserted to be an independently human-typed GitHub attestation. Owner authority comes from the actual parent-declaration contract, not simply GitHub permissions. The experiment owner remains [Upstream #56](https://github.com/opensiro/upstream/issues/56).

## Exact finite two-case publication

| Source | Internal native-tested patch | External PR (now Ready for review) | State |
| --- | --- | --- | --- |
| Citadel / S2 atomic scope claims | [OpenSiro #118](https://github.com/opensiro/upstream/pull/118), [strict six-cell CI PASS](https://github.com/opensiro/upstream/actions/runs/40039135313) | [SethGammon/Citadel #366](https://github.com/SethGammon/Citadel/pull/366) | `SUBMITTED_READY_FOR_REVIEW` |
| Agent Fleet / S2 stale writer lease | [OpenSiro #119](https://github.com/opensiro/upstream/pull/119), [native + portability + pack CI PASS](https://github.com/opensiro/upstream/actions/runs/40093167700) | [chankov/agent-fleet #43](https://github.com/chankov/agent-fleet/pull/43) | `SUBMITTED_READY_FOR_REVIEW` |

The [separate machine-readable ledger](../data/improvement-publication/2026-10-24-01.json) holds exact source base SHA, authenticated actor, public direct-fork parent, verified fork/head SHA, patch SHA-256, five-file diff, actual external URL and current publication disposition. Both forks are public under `opensiro-contributions`; no default/protected branch writes or external merges were performed.

Both PRs were initially Draft under the narrow publication mandate. A later explicit owner instruction to mark these same two as ready was executed without changing the source, candidate set, or merge rights. The ledger preserves the historical `initial_publication=SUBMITTED_DRAFT` for audit.

Each actual external PR has a first-party native RED→GREEN reproducer; the source-pinned internal CI evidence was obtained **without LLM-agent or provider quality tests**. Neither maintainer feedback nor deployed-system improvement is claimed merely because PRs were opened. Strict pilot [#56](https://github.com/opensiro/upstream/issues/56) remains **INCOMPLETE** pending authentic upstream feedback and applicable review disposition.

## Binding limits and return

Only these two exact source and patch identities were covered by the parent instruction. The finite 34-case Corrective publication mandate and its [frozen ledger](../data/corrective-publication/2026-10-23-01.json) are **unchanged**, not expanded or consumed. No permission for other batch-11 cases, future batches, third-party merges, legal attestations, issue policy waivers, force pushes, S3 or S5 redefinition, VSM grade changes, or publication of unverified code.

Stop follow-up writes if the operator revokes the grant, a maintainer forbids further updates, or contributor/branch/legal policy changes. Future interactions with the same PR are bounded to compatible review and CI fixes within the existing exact product scope, not new independent changes. Observe external review and update the ledger only with actual third-party GitHub readback.

## Deterministic consistency gate

`python3 -m unittest discover -s tests -p 'test_improvement_publication.py' -q` checks finite scope, two actual PR identities, unique source and SHA, current Ready-for-review/nonmerged state (with historical Draft origin), authentic fork parent, and exclusion of the original 34-case queue. This does not validate GitHub state in real time; read it back before updating external-status fields.
