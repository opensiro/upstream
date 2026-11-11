# Kram S2 native CI migration — 2026-11-11

**Disposition:** `NATIVE_PARITY_PASS` for the exact pinned Kram S2
edit-file replay. This migrates a historical Upstream Actions execution
surface to the source-matched `opensiro-contributions/kram` working fork.
It is **not** an external PR, first-party adoption, user-benefit measurement,
Index regrade or grant to modify the third-party `codexmark/kram` repository.

## Two independent GitHub run receipts

| Evidence | Immutable identity |
| --- | --- |
| Historical Upstream native run | [39830836737](https://github.com/opensiro/upstream/actions/runs/39830836737) |
| Replacement fork-native run | [43059374414 — success](https://github.com/opensiro-contributions/kram/actions/runs/43059374414) |
| Matching public direct fork | [`opensiro-contributions/kram`](https://github.com/opensiro-contributions/kram), parent `codexmark/kram` |
| Branch / tested workflow commit | [`opensiro/ci-kram-s2-replay-20261111` at `af6bbb28f6dc6ca867df011c8cd4ab6c54cd0676`](https://github.com/opensiro-contributions/kram/blob/af6bbb28f6dc6ca867df011c8cd4ab6c54cd0676/.github/workflows/opensiro-kram-s2-replay.yml) |
| First-party baseline source | `codexmark/kram@5f18406709f432dbdb2d6b09da6f140385516366` — also the fork default-branch SHA at migration time |
| Frozen OpenSiro replay packet | `opensiro/upstream@c88b010894faa7fcf5981195de7e3894796d99f9` |
| Complete patch SHA256 | `c8877dda2405f6d18d5c0693c3620115c8b57907248b4f6c3d42007dec0d030b` |
| Native `s2_replay_test.go` SHA256 | `c3aa4221b0577683da3e7f2a7d8fd78a896eb11c2210e93b946a13adcc931c86` |
| Native `s2_delegate_replay_test.go` SHA256 | `53bd0dac335f4b38cb0c5078b7dba829d192ae1a5750e575f6f86e7cc2360ccf` |
| Historical Upstream workflow Git blob | `1c380c26901350faec3f35bcb4dfe00da4f06146`; its exact YAML is preserved at [historical-upstream-native-replay.yml](historical-upstream-native-replay.yml) |

The replacement runs on GitHub-hosted `ubuntu-24.04` with Go `1.26.6`,
`contents: read`, two SHA-pinned public checkouts and
`persist-credentials: false`. All mutations are confined to the disposable
runner checkout. The fork's `master` and third-party `codexmark/kram` are
unchanged; only a dedicated `opensiro/...` CI branch was created.

## Observed source-native result

The fork runner repeated the **same** two-stage test contract as the old
Upstream workflow: apply only the test files before running the original
code, assert the expected failing mechanism and independent-file control,
apply only the `edit_file.go` production patch, then run the same named Go
tests under the race detector and `bash scripts/verify.sh`.

| Native observation | BEFORE on baseline | AFTER with isolated patch |
| --- | --- | --- |
| Same-path concurrent edits (50 trials) | 0 preserved, 50 lost | 50 preserved, 0 lost |
| Delegated-registry edits (30 trials) | 0 preserved, 30 lost | 30 preserved, 0 lost |
| Competing same-marker edits (50 trials) | 49 double-success claims | 0 double-success claims |
| Disjoint-file control (50 trials) | 50 completed | 50 completed |
| Race-enabled focused native Go tests | Expected failing baseline | All named tests PASS |
| Full native repository verification | Not used as a before/after baseline | `scripts/verify.sh` PASS |

The original source's failing Go exit code is an **expected RED** and was
accepted only after checking exact diagnostic markers. The patched source
passed all named race-enabled tests and the full native gate. See the
[run's step logs](https://github.com/opensiro-contributions/kram/actions/runs/43059374414)
for command-level output. These results are one deterministic native
reproduction, not estimates of live agent behavior or deployed impact.

## Retired Upstream execution surface

- Move the old `kram-s2-native-replay.yml` YAML from `.github/workflows/`
  into this pilot directory as a byte-preserving historical recipe.
- Retain the immutable [original YAML at the pre-migration commit](https://github.com/opensiro/upstream/blob/c88b010894faa7fcf5981195de7e3894796d99f9/.github/workflows/kram-s2-native-replay.yml)
  and the [historical native run](https://github.com/opensiro/upstream/actions/runs/39830836737).
- Keep the functioning fork branch available for branch-specific replay; it
  is **not** added to the fork's `master` or to any third-party publication
  diff. Later pruning of this branch needs a separate evidence-retention
  decision.
- Update Upstream's automated legacy workflow guard, functional-effect
  links and operator map after the reviewed retirement PR merges.

GitHub-hosted run logs may expire under the repository's retention policy.
This receipt keeps the source/test hashes, runner identity, exact commands,
observations and run URL durable even if downloadable logs expire.
Other legacy workflows remain blocked on their own parity receipts under
[Upstream #214](https://github.com/opensiro/upstream/issues/214).

**Scope:** `external_delivery=NONE`; `product_benefit=NOT_MEASURED`.
