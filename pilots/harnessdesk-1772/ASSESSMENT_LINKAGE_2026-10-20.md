# HarnessDesk #1772 — assessment linkage and evidence-bound result

**Classification (2026-10-20): `ASSESSMENT_INFORMED`**, not a completed `ASSESSMENT_DERIVED` improvement experiment.

**Execution:** `SOURCE_PREPARED / BLOCKED_EXTERNAL_STAGE`.
**Engineering validation:** reviewed V2 patch, targeted tests and pinned full local pre-push gate PASS.
**Product-effect verdict:** `INCONCLUSIVE_NOT_DEPLOYED` (no published branch, upstream PR, accepted merge or deployed product observation).

This note supplements rather than rewrites the time-ordered historical [pilot record](README.md). It does not grant permission to push, does not change the canonical Index assessment or claim upstream acceptance. See [assessment-to-improvement protocol](../../docs/ASSESSMENT_TO_IMPROVEMENT.md) and [Upstream #56](https://github.com/opensiro/upstream/issues/56).

## 1. Canonical assessment origin and its actual finding

- Pinned canonical Index source: [`vsm-harness-index@13dab0d4f2954614f7f99a9fa044ad5b9a154490`](https://github.com/opensiro/vsm-harness-index/commit/13dab0d4f2954614f7f99a9fa044ad5b9a154490), [`assessments/ha/harnessdesk.md`](https://github.com/opensiro/vsm-harness-index/blob/13dab0d4f2954614f7f99a9fa044ad5b9a154490/assessments/ha/harnessdesk.md), reviewed upstream ref `24add77185eebe321b0aa0b578933acf4a8e05d3`, assessment date 2026-10-01, included.
- Assessed VSM: `S1=A`, `S2=A`, `S3=C(P)`, `S3*=A`, `S4=—`, `S5=—`. These are **organizational function/decision-right observations**, not a feature request or ranking.
- The assessment's system-in-focus includes the host, common plugin/tool projection and inter-agent coordination. It records that supported agents rely on available tools and shared coordination mechanisms; protecting the tool gateway therefore matters to the assessed operating boundary.
- **Non-claim:** the assessment never diagnoses a missing cross-process `tools.sock` owner protocol, nor demonstrates that making S3 autonomous would repair the socket failure. We must not invent that causal finding after the fact.

## 2. Independently discovered native defect and concrete fix

- Primary source: first-party [HarnessDesk issue #1772](https://github.com/HarnessDesk/HarnessDesk/issues/1772), describing a second headless host launched on the same `HARNESSDESK_HOME` and port. The duplicate removes/rebinds `run/tools.sock` and then exits, stranding the original host's new agent sessions without tools.
- Implementation surface: [`packages/server/src/tool-gateway.ts`](https://github.com/HarnessDesk/HarnessDesk/blob/81d5e34e0e8e3d7e0945bc680695940b41ab852f/packages/server/src/tool-gateway.ts), `development@81d5e34e0e8e3d7e0945bc680695940b41ab852f` (observed 2026-10-20).
- Bounded improvement: [reviewed V2 patch](tool-gateway-ownership-fix-v2.patch), SHA-256 `12b5c7e55a6f730fb9a2465ca30dd47321690c87c0d887e7b8c9d6990ec186e7`, adds process owner/nonces, socket filesystem identity verification, recovery serialization, exclusive publication and safe shutdown. It changes exactly the existing ToolGateway implementation and adds `packages/server/test/tool-gateway-ownership.test.ts`.
- V1 was superseded after adversarial regressions found unsafe socket deletion; V2 explicitly guards both foreign-listener deletion and the `net.Server.close()` pathname behavior. See [V2 review](IMPLEMENTATION_REVIEW_V2_2026-10-20.md).

## 3. Evidence quality

| Observation | Evidence | Does not establish |
| --- | --- | --- |
| Primary product need | [Upstream #1772](https://github.com/HarnessDesk/HarnessDesk/issues/1772), reproducer and original source | That VSM assessment discovered the specific defect |
| Mechanism and plausible benefit | Exact V2 patch and cross-process/foreign-socket regression scenarios | Higher autonomy grade or changed organizational owner |
| Targeted regression validation | [V2 review](IMPLEMENTATION_REVIEW_V2_2026-10-20.md), real Node build, 17/17 targeted Linux/macOS gateway PASS on dated source pins | Entire product or deployed user-experience effect |
| Full upstream pre-push validation on `81d5e34...` | [GitHub Actions 39467673123](https://github.com/opensiro/upstream/actions/runs/39467673123), `pnpm check:push` job completed SUCCESS | External contributor branch existence, external PR publication or downstream acceptance |
| Actual contribution delivery | [Pilot fork](https://github.com/opensiro-contributions/HarnessDesk) exists, but `opensiro/fix-toolgateway-1772` branch absent at last GET; [owner policy](../../policies/harnessdesk-1772-local-prepare.json) `PROPOSED_NOT_ACTIVE` | GitHub push or accepted upstream contribution |

The stronger downstream effectiveness claim (running HarnessDesk after integration has reliably preserved tools during duplicate-host attempts) **has not been independently observed in an accepted/released product**. The isolated regression tests give narrower reproducible engineering evidence.

## 4. Why not count this as the strong assessment-derived pilot?

The assessment supplied a relevant **subsystem and organizational context**. The specific socket ownership bug, its root cause and solution were established by the external product report and source inspection. The patch is justified even if HarnessDesk were never assessed with VSM.

This is precisely `ASSESSMENT_INFORMED`. The legitimate benefit is **ToolGateway reliability**, not claimed transfer of S2 or S3 decision rights. An arbitrary addition of an S3 manager/reviewer would not repair this issue and must not be justified by the grade `C(P)`.

## 5. Treatment and next experiment

Retain V2, its native-fit primary evidence, tests, full-gate receipt and existing unpublished PR draft. Do not abandon or misrepresent the engineering work; complete it later **only** through the independently authorized fork/PR route. The external PR publication remains human-owned.

Run the next **strong assessment-derived** experiment as a separate [Index-first functional gap selection under Upstream #56](https://github.com/opensiro/upstream/issues/56), with an independently demonstrated product-native gap, *before* baseline and matched *after* test, measurable safety/benefit and truthful outcome. Do **not** preselect HarnessDesk merely because its fork or prepared patch exists. Any future Index reassessment is separately scoped and cannot be inferred from this contribution.
