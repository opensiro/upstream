# Architecture — one improvement, three ownership layers

[← Home](../README.md) · [Protocol](../PROTOCOL.md) · [Evidence](EVIDENCE.md)

Upstream is **one operational S1 domain inside OpenSiro VSM OSS**, not a second copy of VSM. [Organization ECOSYSTEM.md](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/ECOSYSTEM.md) owns cross-repository boundaries, [Profile](https://github.com/opensiro/vsm-harness-profile) owns VSM meanings, [Skills](https://github.com/opensiro/vsm-harness-skills) owns the assessment procedure and [Index](https://github.com/opensiro/vsm-harness-index) owns canonical assessments.

```text
opensiro/upstream                         → one long-lived improvement issue
  user need + source/Index provenance + next decision
          │
          ▼
opensiro-contributions/<matching fork>    → working code, original native CI
  branch + tests + source-pinned diff
          │
          ▼
original external repository              → real maintainer authority
  external PR + feedback + merge/closure
          │
          ▼
opensiro/upstream                         → verified outcome in SAME issue
  independent PR readback + test limitations
          │
          ▼
vsm-oss-organization                      → approved metric aggregation and
  shared current-work selection              organization-wide control
```

A chat session can span one or several technical steps without creating a batch. An idea can end at research when source-native value fails; code or external PR is not mandatory for honest closure.

## Where facts live

| Data | [Upstream](https://github.com/opensiro/upstream) | [opensiro-contributions](https://github.com/opensiro-contributions) | [VSM OSS](https://github.com/opensiro/vsm-oss-organization) |
| --- | --- | --- | --- |
| Task and state | **One owning GitHub issue** | Link to issue | Current selection only — [TODO.md](https://github.com/opensiro/vsm-oss-organization/blob/main/TODO.md) |
| VSM hypothesis / original product need | **Dated claim, pinned source links** | Reference | Canonical assessment remains in Index |
| Code and native tests | Receipt/URL | **Working fork branch and native CI** | None |
| Working branch | Verified branch and SHA link | **Canonical source** | None |
| External PR | URL, verified readback and maintainer disposition | Source diff/branch | No parallel ledger |
| Outcomes and metrics | **Per-case facts and validated accepted-outcome producer** | Reproducible technical evidence | [Contracted aggregation](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/METRICS.md) |

## Reuse existing VSM control, do not duplicate it

- **S1 Upstream:** local product opportunity research, source-native qualification, authorized engineering and feedback; [S1 domain contract](https://github.com/opensiro/vsm-oss-organization/blob/main/contracts/s1/domain-contracts.md#upstream-contributions-domain).
- **S2 coordination / S3 current control / S3* audit:** belong under actual [Organization control contracts](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/CONTROL_PLANE.md); case status, CI, reviews or GitHub labels alone are not evidence those functions operated.
- **S4 / S5 and parent authority:** [Organization roadmap](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/ROADMAP.md) and [S5 parent contract](https://github.com/opensiro/vsm-oss-organization/blob/main/contracts/s5/parent-authority.md); the existence of a route does not prove autonomous execution.
- **Global scheduling:** selected issues only in existing [Organization TODO.md](https://github.com/opensiro/vsm-oss-organization/blob/main/TODO.md). No second Upstream task board.
- **Autonomous session reporting:** reuse Organization [DONE / NOW / BLOCKED / NEXT / NEED YOU](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/AUTONOMOUS_WORK_REPORTING.md).

The [opensiro-contributions](https://github.com/opensiro-contributions) organization hosts original-target-specific forks, not a second case registry. Each fork retains the original project's source, README and CI; do **not** rewrite third-party product READMEs to insert OpenSiro governance.

## Outcome / metric boundary

The existing primary Upstream Organization KPI is **`verified_external_outcomes`**: independently verified accepted merged changes. PR counts, green tests, active cases and derived batch counts are not productivity KPIs. A merged change alone does not establish deployed benefit or causal VSM impact.

**Cutover is incomplete:** the old scripts, ledgers and accepted-source exporter still reside in [upstream-old](https://github.com/opensiro/upstream-old). The new repo **does not yet produce a live accepted outcomes export**. The existing [Organization metrics contract](https://github.com/opensiro/vsm-oss-organization/blob/main/metrics.yaml) must not silently read nonexistent new paths or interpret unavailable evidence as zero. Historical old outputs should be linked as historical; a new verified export/source-contract switch requires its own tests and review. [Details](EVIDENCE.md) · [Migration](MIGRATION.md).
