# Batch 40 / Akmatori #48 — VictoriaLogs as a NEW SRE evidence capability (protocol v0.9.0)

**Execution:** 2026-11-14 UTC · **Owner:** [OpenSiro Upstream #56](https://github.com/opensiro/upstream/issues/56) · **Existing batch-40 research:** [PR #303](https://github.com/opensiro/upstream/pull/303) · **First-party demand:** [Akmatori #48](https://github.com/akmatori/akmatori/issues/48).

**Origin:** `SOURCE_FIRST` independently demanded **`MINOR_FEATURE` candidate**, not strict `ASSESSMENT_DERIVED`. This is another source already in the **same** frozen batch-39/batch-40 cohort, not a new batch, source reservation, issue, manifest entry, VSM regrade or retrospective rewrite. Apply the **prospective** Upstream contribution SemVer **v0.9.0 capability-first** research contract; preserve original v0.8.0 batch execution provenance.

## 1. New operator task and value

| v0.9.0 capability question | Research contract |
| --- | --- |
| **Who needs it?** | SRE operators using VictoriaMetrics metrics and VictoriaLogs journal/nginx/system logs; [first-party issue #48](https://github.com/akmatori/akmatori/issues/48) describes an incident in which the local journal had already rotated and metrics-only triage reached the wrong conclusion |
| **New user task** | Search time-bounded **LogsQL journal entries** during an incident and retrieve actual log messages that explain a service crash loop, *in addition to* PromQL/MetricsQL measurements |
| **Trigger → action → observable result** | SRE asks for a bounded log search over a selected time window → new `victoria_logs.query` operation (proposed) requests `/select/logsql/query` with LogsQL → NDJSON log records with `_time`, `_msg` and contextual fields; no change to metrics endpoints |
| **Original alternative** | Source-native `victoria_metrics.instant_query` returns a standard Prometheus metric response. The original `victoria_metrics.api_request` **rejects** `/select/logsql/query` under its read-only metrics endpoint allowlist; the original source has **no** `victoria_logs` type or registration |
| **Native benefit proxy** | Matched offline triage: first-party original metrics query returns a job-state vector but **cannot** return VictoriaLogs evidence; test-only adapter returns **two** NDJSON systemd journal rows with crash-loop/restart messages and correct host/timestamp |
| **Negative/compatibility controls** | Preserve existing metrics query; fixed `start/end`, max six-hour range, max 200 records, max 128 KiB response, required LogsQL/URL, rejected invalid/malformed/HTTP-failed data, URL path scope, no writes, and three bounded HTTP auth options |
| **VSM connection** | The logs provide additional **S1 operational evidence** and enable S3*/feedback review of triage claims. They do not, by themselves, establish that VSM predicted the user need or that an autonomous S3/S4 organization completed an improvement cycle |

**Contract origin matters:** the concrete VictoriaLogs product task was identified via the original maintainer/user issue, *after source inspection*. A VSM assessment may contextualize system ownership and evidence, but cannot retroactively become the origin of the feature proposal.

## 2. Original sources, official protocol and native test

**Immutable original cohort:** `akmatori/akmatori@be62d926fe6d92dceb5cf12e9a95cb587433cdf1`. **Separately inspected observed main:** `akmatori/akmatori@7afba4fb5919f30233fc859be3626bcfdaedbdb7`. Both preserve the original `mcp-gateway` Go module and first-party `internal/tools/victoriametrics` sources.

Official VictoriaLogs [querying HTTP API](https://docs.victoriametrics.com/victorialogs/querying/) documents `/select/logsql/query`, `start/end`, `limit` and a **JSON-lines stream**, rather than the Prometheus response envelope used by the existing Akmatori Metrics tool. It also documents `/select/logsql/hits`, `field_names`, `field_values` and `stats_query` as separate endpoints. This separation is important: *renaming* the existing VictoriaMetrics client to VictoriaLogs would not implement the requested protocol.

Published research artifacts:

- [Go source-native test and test-only LogsQL HTTP adapter](repro/2026-11-14-upgrade40-akmatori-victorialogs-capability-native_test.go), SHA-256 `4b76adc8f014c278c84de3a047ea9d32fdb0f4b38cdeb7ea84a71fb564567704`.
- [Eight exact native test execution receipts](evidence/2026-11-14-upgrade40-akmatori-victorialogs-capability-native.json), including both source commits, full `victoriametrics` package checks, original-vs-candidate test output, native Go `-race` and the remaining scope gates.

**Original source-native method:** a disposable pinned checkout receives **only** an added `*_test.go` file in the original `mcp-gateway/internal/tools/victoriametrics` Go package. The test invokes the original **`VictoriaMetricsTool.InstantQuery` and `APIRequest`**, with a first-party-style populated credential cache and a local `httptest` HTTP endpoint. It then runs a **test-only** LogsQL client that performs actual HTTP form POST, interprets bounded NDJSON and returns two synthetic systemd log messages from another local endpoint. No production code, gateway registry, user settings, credential resolver, real VictoriaLogs deployment, Slack workspace or third-party PR was changed or exercised.

### Native before / after

| Observable | Current original metrics tool | Research-only LogsQL adapter |
| --- | --- | --- |
| Query | First-party `InstantQuery` for a metric vector | `POST /select/logsql/query`, form-encoded LogsQL |
| Source API response | Prometheus JSON envelope | VictoriaLogs line-delimited JSON |
| Crash-loop journal evidence | **Unavailable:** `APIRequest` rejects LogsQL endpoint | **Available:** two bounded test lines, including `systemd myservice crash loop: exit code 1` |
| Existing Metrics operation | **Retained** | Not modified |
| User triage action | Cannot query this log source via shipped tool | Candidate supports a *new* read-only log retrieval task **only in the research fixture** |

**Negative controls:** invalid/inverted/unbounded timestamps, oversized line limit, missing bearer credential, missing LogsQL query, malicious extra base path, malformed NDJSON, >128-KiB response, more rows than allowed, non-2xx server error. Positive auth fixtures check none, basic auth and explicit `X-Research-Token` header; the primary workflow checks bearer authorization.

**Executed:** three named Go tests (`NewTriageWorkflowAndOriginalBoundary`, `QuerySafetyAndBounds`, `AuthModesAndHTTPFailure`) PASS **20 full repetitions on the frozen source** and **20 on the separately observed source main**, **Go `-race` × 2 per pin**. The full original `mcp-gateway/internal/tools/victoriametrics` test package passes on both pins with the fixture included. All eight published execution records exited 0.

### What remains untested/unimplemented

The test-only adapter does **not** implement the four other first-party requests in issue #48: `hits`, `field_names`, `field_values`, `stats_query`; their response structures and authorization need separate supported contracts. The adapter does not integrate into the gateway registry, connector catalog, source `victoria_logs` settings/auth resolution, tool instance selection, rate limiting, production proxy/egress restrictions, source tool allowlists, output-format normalization, permissions or maintainer-owned API/design. The fixed 6-hour/200-row/128-KiB bounds are *research defaults* for a safe fixture, not approved production settings. There is no real journal/metrics dataset or human adjudication of root cause; all messages are scripted, not production observation.

The native test's controlled metric response and journal lines are a **counterfactual capability discriminator**, not measured SRE productivity, diagnostic accuracy, adoption, production remediation, bug repair or proof of VSM autonomous improvement. The original metrics API correctly refuses a non-metrics endpoint, so **do not call this an original security bug**.

## 3. Native fit and research disposition

| Gate | Current result |
| --- | --- |
| `need` | **PASS** — original first-party user request #48 and concrete journal-based SRE workflow |
| `mechanism` | **PASS for bounded research** — first-party metrics baseline and LogsQL HTTP/NDJSON transport identified and exercised on original Go module |
| `counterfactual` | **PASS for synthetic source-native new user action** — metrics-only cannot surface original journal entries; controlled LogsQL query can; **PENDING** independent real data/provider benefit |
| `scope` | **PENDING** — maintainer contract, all requested functions, settings/auth/permission integration, real VictoriaLogs connection and source-native full before/after product tests |
| Overall | **`OPPORTUNITY_RESEARCH_PENDING / NO_ADMITTED_PATCH`**, `SOURCE_FIRST MINOR_FEATURE` candidate; **no four complete PASS**, no external target PR, deployment, observed product outcome or strict assessment-derived upgrade |

**Next smallest maintainer decision / native falsifier:** confirm the intended `victoria_logs` tool registration and supported query endpoints and credentials, then implement a restricted read-only `query` operation in a *disposable* source checkout using the exact first-party gateway registry and source-auth model, validate on a version-pinned genuine VictoriaLogs API fixture or instance, and test that enabling it adds the log-retrieval task without changing VictoriaMetrics behavior. Respect first-party license, maintainer approval, tool authorization and third-party PR rules before any product patch. Do not expand synthetic probes endlessly while the source-owned scope remains unapproved.
