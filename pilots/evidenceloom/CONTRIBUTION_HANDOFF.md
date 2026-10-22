# Evidence Loom — Unicode-spaced percent suffix bypasses numeric review scale guard

**Stage:** `AWAITING_EXTERNAL`. Native source/test patch packet only. No write, issue, PR or merge against the external repository.

- **Frozen source:** `simonguo/evidenceloom@de30bd4262fe0198dcc349e318fb0c1f1f9fc410`, included `S1=A` Index snapshot `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`, not `ASSESSMENT_DERIVED`. The assessment surfaced deterministic evidence and numeric verification scripts; exact Unicode-space behavior was identified from first-party `numeric_spans.py` and independently reproduced.
- **Need — PASS:** `_SCALE.match(suffix.lstrip(" \t"))` skips only ASCII space/tab. Both public `supported_numeric_span()` and private `_SectionSpans.numeric()` therefore report the selected `12` in `12\u202f%`, `12\u00a0%` or `12\u2009%` as a plain supported numeric span, even though `%` is a scale suffix. The code already recognizes these three separators in numeric-grouping boundary protection, so their omission from suffix handling is inconsistent.
- **Mechanism — PASS:** name one internal `_SCALE_GAP` character set with ASCII space/tab plus NBSP, narrow NBSP and thin space, and reuse it at the two scale-check sites. Do not change any token parsing, source evidence provenance, surrounding prose validation, rounding or external API.
- **Counterfactual — PASS (bounded):** six offline first-party-code stdlib tests: **3 RED / 3 PASS before** and **6 PASS / 0 FAIL after**. Three formerly failing Unicode-space percent variants, with control cases for ASCII-separated and immediate percent plus ordinary non-scaled decimal context. Each case checks both independent parser entry points.
- **Scope — PASS:** one Python numeric-span script, one added standard-library direct-source test file, no provider/model, market-data endpoint, UI or graph execution.

## Native checks

| Check | Result |
| --- | --- |
| `python3 -m unittest discover -s tests -p test_numeric_scale_whitespace_unittest.py -v` before | **3 PASS / 3 RED** |
| Same command after | **6 PASS / 0 FAIL** |
| `python3 -m compileall -q` changed Python files | PASS |
| `git diff --check` | PASS |
| `git apply --reverse --check` on patched frozen checkout | PASS |
| Full first-party pytest suite / market-data integration / LLM model trials | **Not run / not claimed** |

**Exact patch:** [unicode-spaced-numeric-scale.patch](unicode-spaced-numeric-scale.patch), SHA256 `185b89c27de2bed91d3f22b9898bd3c37d73cd15a3e71155a1d0afe22546c983`, equal to the tested genuine-source diff. External code remains local, unpushed.

**Limitations:** This checks only known Unicode grouping spaces; it does not establish correctness for every Unicode separator, percent notation, saved source artifact or independent claim. It does not certify surrounding prose. An upstream maintainer would still need full regression and language/UI parity review. External contribution remains human-owned; `continue` advances to Workflow One.
