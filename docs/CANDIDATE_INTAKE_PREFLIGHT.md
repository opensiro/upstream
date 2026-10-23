# Read-only candidate intake preflight

**Owner:** `opensiro/upstream` / experiment [#56](https://github.com/opensiro/upstream/issues/56). **Organizational route:** [VSM-OSS #285](https://github.com/opensiro/vsm-oss-organization/issues/285). This does not create a new S1 domain, permit publication, or change any VSM classification.

Use **before preparing a derivative patch, creating a fork or opening an external PR**. Run against the actual third-party upstream repository and pin its reported branch SHA:

```sh
python3 scripts/candidate_intake_preflight.py --source OWNER/REPO --topic 'bounded candidate description'
```

The script makes only unauthenticated, repository-scoped GitHub REST `GET` requests. It does not run an agent, model, Browser test, GitHub write, clone, download a credential, or grant copyright permission. Its deterministic unit tests use a fake GET responder.

## Evidence and interpretation

1. Check the public repository identity, default/selected branch and exact source SHA.
2. Enumerate root `LICENSE`/`LICENCE`/`COPYING`/`UNLICENSE` files, including named `LICENSE-MIT`, `LICENSE-APACHE`, and comparable common SPDX-family filename variants. Read the **actual content of every matched root license file** (not only the often-missing GitHub SPDX metadata) and emit each path and SHA-256 under `license.files`. If any matched file is missing, malformed, or empty, fail closed. Multiple license candidates require explicit scope review. Notices, vendored-code licenses, patent/trademark limits and proposed patch compatibility **still require human/source review**.
3. Only after verifying root license text, inspect eligible root policies plus `.github/` and `docs/` policy files and `.github/{ISSUE_TEMPLATE,PULL_REQUEST_TEMPLATE}/` text/YAML templates. Pin **all** file reads to the exact observed source commit SHA. Emit content digests and `{path,line,code,stage,excerpt}` evidence. Stage-specific `gates` summarize evidence and unresolved obligations; `NOT_CLEARED` never grants permission to implement, publish, mark ready or merge. This is a bounded enumeration, not proof that no policy exists elsewhere (including linked websites and repository discussions).
4. If `--topic` is supplied, traverse both **open and closed** issues and PRs using `state=all`, up to **30 pages of 100 records per endpoint** (checking the next page after an exactly full page). Search both titles and bodies for normalized topic-token overlaps (including partial similarities); filter PR entries from issue results. `INVENTORY_INCOMPLETE` explicitly records when the bounded limit is hit; a denied page fails closed as `INSUFFICIENT_EVIDENCE`. A complete inventory only establishes bounded lexical overlap, not the absence of semantic duplicates or a fix already merged under a different title.

## Stage boundaries and machine reasons

| Stage | Static evidence now gathered | Still required before actual stage transition |
| --- | --- | --- |
| `BEFORE_IMPLEMENTATION` | Source SHA, root license digest, issue/PR inventory, contributor issue/branch hints | Human or first-party-supported license compatibility decision, source-native defect and duplication check, any required issue assignment |
| `BEFORE_DRAFT` | Contributor DCO/CLA and Draft timing text | Genuine actor/authority/fork/branch verification, native RED→GREEN, diff/secret inspection, attestations and any explicit pre-Draft policy |
| `BEFORE_READY` | Ready-for-review and CI/test mentions | Required CI/reviews and author declaration at the applicable time; Draft may remain pending if policy permits |
| `BEFORE_MERGE` | Merge timing hints | Upstream maintainer, branch protection and review/CI gates; this mandate does not authorize merge |

Every gate contains `status` and `reasons`; clear reason codes include `ROOT_LICENSE_NOT_FOUND`, `SOURCE_EVIDENCE_UNVERIFIED`, `LICENSE_COMPATIBILITY_REVIEW_REQUIRED`, `POTENTIAL_DUPLICATE_REVIEW_REQUIRED` and `DUPLICATE_INVENTORY_INCOMPLETE`. Hints do not determine whether the upstream actually *requires* DCO, CLA, issue assignment or branch syntax. Resolve these using the first-party context and the correct stage; no machine text-match can certify consent.

| Machine status | Meaning | Next action |
| --- | --- | --- |
| `LICENSE_REVIEW_REQUIRED` (exit 0) | Public source/ref and **nonempty root license text** verified; bounded policy/overlap evidence gathered | Human/operator must still establish applicable grant and compatibility **before derivative work**; then evaluate the stage-specific gates |
| `LICENSE_BLOCKED` (exit 2) | No root license file observed | Do not make a derivative; investigate other license locations or obtain rights. **Not** a legal judgment that all use is forbidden |
| `INSUFFICIENT_EVIDENCE` (exit 2) | API denied/rate-limited, malformed, missing required content, SHA unverifiable, etc. | Preserve source error, retry/inspect first-party evidence without treating it as license absence |

**Never convert `LICENSE_REVIEW_REQUIRED` to `LICENSE_ELIGIBLE` automatically.** Human/legal provenance and context determine eligibility, and an SPDX label or apparent OSS license does not override repository-specific policy. No machine status verifies DCO/CLA attestation, external issue assignment, contributor identity, organization fork-write permission, permitted branch naming, CI gate timing or a right to merge.

The broader [candidate screening process](ASSESSMENT_CANDIDATE_BATCHES.md) owns the triaged `LICENSE_ELIGIBLE` / `LICENSE_BLOCKED` / `LICENSE_UNRESOLVED` verdict; [Corrective publication](CORRECTIVE_PR_PUBLICATION.md) rechecks it on current third-party sources at the publication stage. The already frozen 34-case queue remains unchanged, and running this preflight alone is **not** a publication attempt.

## Negative-test contract

The tests must prove that a metadata-only SPDX label cannot bypass absent root license text; 403/429/404 and malformed content never become eligibility; exact-SHA policy evidence, nested `.github/` discovery and line numbers work; fully paginated open/closed issues and PRs are checked and page-budget exhaustion is reported; invalid repo/branch/topic input never reaches the network; CLI has no `--execute` or mutation mode. Run:

```sh
python3 -m unittest discover -s tests -p 'test_candidate_intake_preflight.py' -v
python3 -m unittest discover -s tests -p 'test_fork_public_preflight.py' -v
python3 scripts/corrective_publication_queue.py validate
```

This is **phase 1, read-only preflight**. Authenticated issue/workflow gates and publication permission checks must be implemented and verified separately under the [organizational change protocol](https://github.com/opensiro/vsm-oss-organization/pull/286) before any new write automation is enabled.
