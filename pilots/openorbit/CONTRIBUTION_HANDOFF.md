# OpenOrbit — dot-only path parameters change the HTTP endpoint

**Stage:** `AWAITING_EXTERNAL`. Exact local TypeScript script-test patch, no external fork/PR and no live model, Electron session or HTTP request.

- **Frozen source:** `maneja81/OpenOrbit@2c30242310c3f2e8453b1116d657e65634e6973e` (MIT); included `S1=A` Index assessment at `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`: assessed first-party HTTP tool/approval guards motivated source screening; the specific WHATWG URL normalization defect came from direct `electron/main/ai/httpToolRequest.ts` inspection.
- **Need — PASS:** `buildHttpRequest` encodes substituted path parameters using `encodeURIComponent`, but bare `.` and `..` remain dots. A subsequent `new URL(...)` call normalizes these whole path segments and can change the target endpoint path. Slash/question-mark injection was already covered; standalone dot segments were not.
- **Mechanism — PASS:** reject exactly `.` and `..` as path parameter values before constructing the URL. Leave all existing path, query, header and body substitutions unchanged. Does not redefine user approval policy or claim to eliminate all URL-level hazards.
- **Counterfactual — PASS (bounded):** the existing first-party `httpToolRequest.test.ts` suite had **17 PASS / 2 FAIL** after adding two isolated cases (`.` and `..`); after the small patch it reported **19 PASS / 0 FAIL**. No network or agent runtime was involved.
- **Scope — PASS:** first-party request-builder function and its existing Vitest file only.

## Evidence

| Script | Result |
| --- | --- |
| `npx vitest run electron/main/ai/httpToolRequest.test.ts` with added tests before fix | 17 PASS / 2 FAIL |
| Same command after fix | 19 PASS / 0 FAIL |
| `git diff --check`; `git apply --reverse --check` | PASS |
| Full Electron app, model-provider task session, real HTTP dispatch, wider CI | **Not executed / not claimed** |

**Exact tested patch:** [dot-segment-path-parameter-guard.patch](dot-segment-path-parameter-guard.patch), SHA256 `f90c3a02aa8e759f30289a402e5d03657031049f64936095b1acb1ac382b5ae9`. Byte-identical to source diff on pinned checkout. `npm ci --ignore-scripts` installed lockfile dependencies without executing package lifecycle scripts.

**Limits:** This proves request-construction correctness for path placeholders, not exploitability against any particular HTTP service, upstream acceptance, or the quality of agent decisions. Human-owned external publication remains separate. Generic `continue` moves to Reef.
