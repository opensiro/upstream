# DiscoveryRSI — earlier episode records mutate after later scoring

**Stage:** `AWAITING_EXTERNAL`. Internal native patch and evidence only; no external fork, issue, commit, PR, or merge.

- **Source:** `Gen-Verse/DiscoveryRSI@7389e0b58ae50486ab35aa3dcbfa2fa15fea1a91`, pinned from the included `S1=A` Index assessment at `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`, not `ASSESSMENT_DERIVED`. The assessment exposed the candidate-history/replay mechanism; the concrete mutable-object aliasing bug was discovered by direct-source native probes.
- **Need — PASS:** `DiscoveryLoop.run` scores the objects returned by its proposer in place. If a deterministic proposer reuses one `Candidate` across iterations, later scoring silently rewrites previous `Episode.candidates` and `history` entries. Thus the returned first episode's score becomes 2 even though the JSONL replay already stored score 1. Proposer-owned input objects are also unexpectedly annotated in place.
- **Mechanism — PASS:** deep-copy proposed candidates before per-iteration scoring so every episode and replay record refers to an independent snapshot. Does not alter the selection policy, replay serialization, provider adapter, or task prompts.
- **Counterfactual — PASS (bounded):** four real-source Python stdlib `unittest` cases using fixed proposer/critic functions and temporary JSONL file: before **1 PASS / 3 RED**; after **4 PASS / 0 FAIL**. Checks snapshot immutability, replay parity, source-object preservation, and an ordinary fresh-candidate baseline. No LLM agent, inference provider, model mock, or performance evaluation was run.
- **Scope — PASS:** one import and one list construction in `src/discovery_rsi/core.py`, plus one new direct-script test file.

## Native checks and limitations

| Check | Result |
| --- | --- |
| `PYTHONPATH=src python3 -m unittest -v tests/test_replay_snapshot_unittest.py` before | **1 PASS / 3 RED** |
| Same stdlib tests after | **4 PASS / 0 FAIL** |
| `python3 -m compileall -q src/discovery_rsi tests/test_replay_snapshot_unittest.py` | PASS |
| `git diff --check` | PASS |
| `git apply --reverse --check` against tested checkout | PASS |
| Shipped `pytest tests/test_core.py` | **Not run:** pytest is absent here; first-party pytest runner remains a maintainer gate |
| Full original first-party suite, inference adapters, benchmark | **Not run / not claimed** |

**Patch:** [candidate-episode-snapshot.patch](candidate-episode-snapshot.patch), SHA256 `af4c299cf3cf92fc79b2a2417de361fd119c0c362c1dbe6bfc2da8145607b68c`, exactly equal to the tested native Git diff. Reverse-apply check passed. Local external code remains uncommitted and unpushed.

**Adversarial review:** Deep copying potentially large candidate evidence lists adds bounded per-iteration memory/copy overhead. The patch does not prevent a proposer from actively mutating objects passed via the `history` argument, repair truncated JSONL, validate scores, or guarantee durable fsync. It establishes only that reused returned candidates cannot retroactively mutate prior in-memory episode snapshots.

**Continuation:** External publication remains a human action. Generic `continue` skips this `AWAITING_EXTERNAL` row and advances to `orch-resume-checkpoint-idempotency`.
