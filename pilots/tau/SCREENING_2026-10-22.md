# Tau — bounded source screening (batch 03, row 1)

**Disposition:** CLOSED_NO_CHANGE. No accepted source patch or external PR. No provider/model-agent execution.

- Canonical Index assessment: `assessments/ta/tau.md` at Index `396a54bb690f8ec7ce966bf9b00b241b30036307`, source reviewed at `huggingface/tau@9fe6a719ac0bda3696e9fc8413643cfe9786c73c`.
- Current upstream `main` was observed at `ae9a1d94874a229cb783d53277eb374290448850`. `src/tau_agent/session/storage.py` did not change between the reviewed source and that revision.
- Source inspection: single-entry `append` uses a cross-process lock and fsync; `append_batch` uses same-directory temporary file, `os.replace` and directory fsync; `read_all` uses a read lock and strict JSONL validation. The contract promises atomic **batch** append, not arbitrary salvage of an incomplete single-entry append after a process crash.
- Executed real first-party native script tests at the pinned revision using the repository's prescribed `uv` environment: `uv run --offline pytest -q tests/test_session.py tests/test_session_manager.py tests/test_codex_resume.py` → **75 passed, 0 failed**. (The first isolated `tests/test_session.py` check was also 41 passed.) No model/provider runtime was started.
- Bounded issue/PR searches for corrupted JSONL or atomic append found no direct existing matching regression/patch. That negative result is not a guarantee of completeness.
- No red/green counterfactual or source-grounded functional improvement was established, so no code change is justified here.

| Fit gate | Status | Reason |
| --- | --- | --- |
| Need | FAIL | No reproduced defect in inspected session path |
| Mechanism | PASS | Exact file and native first-party tests verified |
| Counterfactual | FAIL | Baseline native tests pass; no RED |
| Scope | PENDING | No evidenced code change |

**Continuation:** Advance to the next batch 03 row without waiting.
