# Spartan — first Soul archive entry silently skipped on backfill

**Stage:** `SUBMITTED_READY_FOR_REVIEW` on 2026-10-24. [Upstream PR #1](https://github.com/CorticalComputer/Spartan/pull/1), authored by `xLagerFeuer` through the public `opensiro-contributions/Spartan` fork. The original regression experiment below was executed offline.

- **External publication readback:** base `8f7b36a2326c0157a82040f8e04b474f4899c3da`, head `fe55061799561107d3eeffa330cafa0b954e2f4f`, exactly two changed files; OPEN / Ready for review, no upstream merge claimed.

- **Frozen source:** `CorticalComputer/Spartan@8f7b36a2326c0157a82040f8e04b474f4899c3da` (Apache-2.0), included `S1=A` Index `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`; the Index covers persistent Soul/LTM backfill, but the specific delimiter problem was found by inspecting first-party `ltm.py::_parse_existing_soul_file`.
- **Need — PASS:** For a normal Markdown Soul archive beginning directly with YAML frontmatter `---`, the backfill splitter retained that opening marker yet unconditionally prepended a *second* marker. The parser then read empty frontmatter and silently discarded the first entry. Later entries survived, masking partial loss.
- **Mechanism — PASS:** Prepend the opening marker only when it was consumed by the entry-boundary split. Preserve the source's existing length and entry metadata checks.
- **Counterfactual — PASS (bounded):** Four deterministic `unittest` cases against the actual imported first-party function cover one and two normal top-of-file entries, the existing writer's leading-blank delimiter, and short-body exclusion. Before: **2 PASS / 2 FAIL** (lost first entry). After: **4 PASS / 0 FAIL**.
- **Scope — PASS:** only `ltm.py` and `test_native_soul_archive_unittest.py`. Files are temporary local fixtures. No LLM, model mock, persistent machine Soul file, LanceDB, embedding service, GUI, external provider or agent loop.

## Verification

| Command | Evidence |
| --- | --- |
| `python3 -m unittest -q test_native_soul_archive_unittest.py` on pinned original | 2 PASS / 2 FAIL |
| Same command after | 4 PASS / 0 FAIL |
| `python3 -m py_compile ltm.py test_native_soul_archive_unittest.py`; `git diff --check` | PASS |
| `git apply --reverse --check` against modified checkout | PASS |

**Exact tested patch:** [soul-first-entry-backfill.patch](soul-first-entry-backfill.patch), SHA256 `a73d260a5a6cbcd49077f7aa2e1586d567c3d26586fa7c877750bc5d4a3d4b66`. Both patch and test are real code; no simulated LLM-agent outcome is claimed.

**Limits:** This shows one backfill parser input-shape regression only. It does not establish that actual production Soul archives always begin with top-of-file frontmatter, nor assert end-to-end persistence durability or model improvement. External maintainer review and merge stay with the human owner; the next candidate is Cyber AI Team.
