# Read-only candidate intake preflight

**Owner:** `opensiro/upstream` / experiment [#56](https://github.com/opensiro/upstream/issues/56). **Organizational route:** [VSM-OSS #285](https://github.com/opensiro/vsm-oss-organization/issues/285). This does not create a new S1 domain, permit publication, or change any VSM classification.

Use **before preparing a derivative patch, creating a fork or opening an external PR**. Run against the actual third-party upstream repository and pin its reported branch SHA:

```sh
python3 scripts/candidate_intake_preflight.py --source OWNER/REPO --topic 'bounded candidate description'
```

The script makes only unauthenticated, repository-scoped GitHub REST `GET` requests. It does not run an agent, model, Browser test, GitHub write, clone, download a credential, or grant copyright permission. Its deterministic unit tests use a fake GET responder.

## Evidence and interpretation

1. Check the public repository identity, default/selected branch and exact source SHA.
2. Enumerate root `LICENSE`/`LICENCE`/`COPYING`/`UNLICENSE` files. Read the **actual content** (not only the often-missing GitHub SPDX metadata) and emit the file path and SHA-256. Multiple license candidates require explicit scope review. Notices, vendored-code licenses, patent/trademark limits and proposed patch compatibility **still require human/source review**.
3. Only if a root license file was verified, read available root `CONTRIBUTING.md`, `AGENTS.md`, `CLAUDE.md` and emit bounded flags for DCO/CLA, issue, branch, testing/CI, before-Draft and before-merge mentions. These are textual hints, not an automatically cleared gate; check relevant `.github` files and first-party policies manually where present.
4. If `--topic` is supplied, inspect the first page of issues and open PRs for title overlaps; filter PR entries out of the issue result. This **cannot prove absence of a duplicate**. A full first page returns `PAGINATION_REQUIRED`, and title-only matching can miss synonyms, changed titles and closed PRs.

| Machine status | Meaning | Next action |
| --- | --- | --- |
| `LICENSE_REVIEW_REQUIRED` (exit 0) | Public source/ref and **nonempty root license text** verified | Human/operator must still establish applicable grant and compatibility before derivative work; then check notices, full contributor policy, overlap and exact Draft/merge timing |
| `LICENSE_BLOCKED` (exit 2) | No root license file observed | Do not make a derivative; investigate other license locations or obtain rights. **Not** a legal judgment that all use is forbidden |
| `INSUFFICIENT_EVIDENCE` (exit 2) | API denied/rate-limited, malformed, missing required content, SHA unverifiable, etc. | Preserve source error, retry/inspect first-party evidence without treating it as license absence |

**Never convert `LICENSE_REVIEW_REQUIRED` to `LICENSE_ELIGIBLE` automatically.** Human/legal provenance and context determine eligibility, and an SPDX label or apparent OSS license does not override repository-specific policy. No machine status verifies DCO/CLA attestation, external issue assignment, contributor identity, organization fork-write permission, permitted branch naming, CI gate timing or a right to merge.

The broader [candidate screening process](ASSESSMENT_CANDIDATE_BATCHES.md) owns the triaged `LICENSE_ELIGIBLE` / `LICENSE_BLOCKED` / `LICENSE_UNRESOLVED` verdict; [Corrective publication](CORRECTIVE_PR_PUBLICATION.md) rechecks it on current third-party sources at the publication stage. The already frozen 34-case queue remains unchanged, and running this preflight alone is **not** a publication attempt.

## Negative-test contract

The tests must prove that a metadata-only SPDX label cannot bypass absent root license text; 403/429/404 and malformed content never become eligibility; a 100-item page is not exhaustive; invalid repo/branch/topic input never reaches the network; CLI has no `--execute` or mutation mode. Run:

```sh
python3 -m unittest discover -s tests -p 'test_candidate_intake_preflight.py' -v
python3 -m unittest discover -s tests -p 'test_fork_public_preflight.py' -v
python3 scripts/corrective_publication_queue.py validate
```

This is **phase 1, read-only preflight**. Authenticated issue/workflow gates and publication permission checks must be implemented and verified separately under the [organizational change protocol](https://github.com/opensiro/vsm-oss-organization/pull/286) before any new write automation is enabled.
