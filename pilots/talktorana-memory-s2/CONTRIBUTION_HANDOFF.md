# talktorana agent-harness — prevent stale memory rewrite under concurrency

Status: **ASSESSMENT_DERIVED / AWAITING_EXTERNAL / NOT_PUBLISHED**. This is an OpenSiro-local technical packet under [Upstream #56](https://github.com/opensiro/upstream/issues/56) and [batch 13](../../data/assessment-candidate-batches/2026-11-06-13.json), not a third-party PR or proof of deployed improvement.

## Source and native need

- Canonical Index `1e2d2b1c48e3b8d846d6911c98e4b76f1c6f1340`: [`assessments/ag/agent-harness-talktorana.md`](https://github.com/opensiro/vsm-harness-index/blob/1e2d2b1c48e3b8d846d6911c98e4b76f1c6f1340/assessments/ag/agent-harness-talktorana.md). Included `S1=A / S2=C`, reviewed source `4d5e11d16e4e9755c4282634778f112c44e21d12`.
- Independently inspected genuine current first-party source: [`talktorana/agent-harness@7b2f57b70849c33fb38c6188ab12ceff42cd099c`](https://github.com/talktorana/agent-harness/commit/7b2f57b70849c33fb38c6188ab12ceff42cd099c), MIT `LICENSE`. No root contributor guide observed. Read-only public issue/PR searches for memory concurrency/revise/retire returned no exact lexical match; absence of a semantic duplicate is not established.
- The assessed S2 interference mechanism is shared memory read-modify-write under multiple in-process writers. `append()` holds the process-wide `_LOCK` for its read+write; `revise()` and `retire()` read their snapshot **before** acquiring `_LOCK` for the final write. Another task can append in that interval; the mutator then atomically replaces the file with a stale snapshot, silently discarding that new note.

## Four fit gates

| Gate | Result | Evidence |
| --- | --- | --- |
| `need` | PASS | Two deterministic genuine-`MemoryStore` interleavings erase a newly accepted note on untouched source. The repo's own memory module promises no lost in-process writes. |
| `mechanism` | PASS | A stale read outside `_LOCK` in `revise` / `retire` is followed by `_atomic_write`; the S2 memory guard does not span that transaction. |
| `counterfactual` | PASS | Even without AI, a web task and scheduler thread may concurrently record/correct notes. Losing a successful write is independently adverse. |
| `scope` | PASS | One decorator holds the existing reentrant process-wide lock over the complete two mutators; no provider, prompt, database or distributed-lock policy is changed. |

## Reproducible native result

Patch: [`concurrent-revise-retire.patch`](concurrent-revise-retire.patch), SHA-256 `0256bed316e87edae27bf4d19ffe97f74d4810f7d1ab168ae26a622feda42fa8`.

The added `test_memory_mutator_interleaving.py` pauses the real first-party `Path.read_text` after reading the original note, starts a competing real `MemoryStore.append`, and then allows `revise` or `retire` to finish. It does not run an agent, model, provider or external service.

| Exact source | Native deterministic tests |
| --- | --- |
| Clean original `7b2f57b` + added regression | 2 FAIL: `test_revise_preserves_concurrent_append`, `test_retire_preserves_concurrent_append` (new note lost) |
| Patched `7b2f57b` | 7 PASS: both new regressions + all five first-party `test_memory_concurrency` cases; `py_compile` PASS |
| Disposable clean Git worktree at `7b2f57b` + exact archived patch | `git apply --check` PASS, 7/7 native tests PASS, `git diff --check` PASS |

The protected scope remains **one Python process**. The first-party documentation explicitly excludes concurrently writing containers that share a mounted memory path. No multi-process lock, network storage guarantee, full repository test-suite PASS, live agent outcome, downstream user benefit, external acceptance or VSM regrade is claimed.

## Return and authority

Prepared as a reviewable OpenSiro technical handoff. `external_action=NOT_EXECUTED`: no fork, external issue/PR, push or maintainer contact. External publication of this improvement is outside the historical 34-case Corrective mandate and requires a separate attributable owner decision, current source/policy/overlap recheck and applicable execution rights under [#6](https://github.com/opensiro/upstream/issues/6). The next batch row may proceed without waiting for that grant.
