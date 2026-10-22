# SIFRA — timed-out code-mode continuation retains host-tool access

**Stage:** `AWAITING_EXTERNAL`. This is a tested, source-only patch packet. No external fork, issue, PR, DBOS workflow, provider or LLM agent was executed.

- **Frozen source:** `atharva1407-sys/SIFRA-Agent-Orchestration-Multi-Agent-Runtime@6856b054ba67e4dc4ef499a46732eeed80b5ac68`, included `S1=A` Index `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`. The assessment identifies SIFRA's first-party TypeScript code-mode, tool and permission boundaries; the specific timeout issue was identified by directly inspecting `sifra/sandbox.ts::runInSandbox`. This is adjacent to the originally frozen approval-replay screening question, not a demonstrated failure of the refund/DBOS flow.
- **Need — PASS:** `Promise.race` rejected a code-mode run at its async deadline, yet the uncancelled continuation could still invoke a host tool later using the original `tools` object. The returned timeout therefore did not revoke tool access.
- **Mechanism — PASS:** Pass a per-invocation frozen API wrapper into the genuine `node:vm` context, guard every host-tool invocation against an active flag, and revoke it in `finally` when the run settles. This blocks *new* late tool invocations; it does **not** cancel already-running tool calls or make `node:vm` a security isolation boundary.
- **Counterfactual — PASS (bounded):** the three-case native Node script reproduces the late side effect against unchanged pinned source (**2 PASS / 1 FAIL**) and verifies its absence after the patch (**3 PASS / 0 FAIL**). Both controls remain green: normal permitted access before the deadline and a timeout result for an overlong async task.
- **Scope — PASS:** first-party `sifra/sandbox.ts` plus `scripts/native-sandbox-timeout.test.mjs`. No database, model, sandbox-provider product, DBOS runtime, cloud side effect or external publisher.

## Verification

| Script | Result |
| --- | --- |
| `node --experimental-strip-types scripts/native-sandbox-timeout.test.mjs` before | 2 PASS / 1 FAIL |
| Same command after | 3 PASS / 0 FAIL |
| `git apply --reverse --check` against modified pinned checkout | PASS |
| Native model/agent/provider runs or upstream CI | **Not run / not claimed** |

**Exact tested patch:** [timeout-revokes-tool-access.patch](timeout-revokes-tool-access.patch), SHA256 `7dc78e02362794c7b2a96280d5ce1420090367d792bb122e5d118fc6d7a99f37`. The patch byte-for-byte matches the pinned source checkout diff; it includes the regression test.

**Limits:** This proves tool-call revocation after timeout for a controlled async continuation. It does not prove containment against malicious JavaScript, prevent in-flight external actions or establish SIFRA runtime approval effectiveness. External upstream publication remains human-owned. Generic `continue` rolls over to the next full frozen candidate cohort.
